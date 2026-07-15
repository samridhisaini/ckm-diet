import json
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from ckm_api import models

VISIT_ORDER = ["Baseline", "3rd month", "6th month", "9th month", "12th month"]


# ─── Patient / Visit queries ───────────────────────────────────────────────────

def get_all_patients(db: Session):
    return db.query(models.Patient).all()


def get_patient(db: Session, pid: str):
    return db.query(models.Patient).filter(models.Patient.pid == pid).first()


def get_visits(db: Session, pid: str):
    visits = db.query(models.Visit).filter(models.Visit.pid == pid).all()
    order_map = {v: i for i, v in enumerate(VISIT_ORDER)}
    return sorted(visits, key=lambda v: order_map.get(v.visit_label, 99))


def get_latest_visit(db: Session, pid: str):
    visits = get_visits(db, pid)
    attended = [v for v in visits if v.attended != "No" and v.visit_label != "Baseline"]
    if attended:
        return attended[-1]
    return visits[-1] if visits else None


def get_patient_with_visits(db: Session, pid: str):
    patient = get_patient(db, pid)
    if not patient:
        return None, []
    visits = get_visits(db, pid)
    return patient, visits


def build_patient_json(patient: models.Patient, visits: list) -> dict:
    """Build the full patient data dict used by the LLM and summary endpoint."""

    def _visit_dict(v: models.Visit) -> dict:
        return {
            "visit":              v.visit_label,
            "date":               v.visit_date,
            "attended":           v.attended,
            "weight_kg":          v.weight_kg,
            "bmi":                round(v.bmi, 2) if v.bmi else None,
            "bmi_category":       v.bmi_category,
            "waist_cm":           v.waist_cm,
            "sys_bp":             v.sys_bp,
            "dia_bp":             v.dia_bp,
            "hb_a1c_pct":         v.hb_a1c,
            "total_cholesterol":  v.total_cholesterol,
            "triglycerides":      v.triglycerides,
            "ldl":                v.ldl,
            "hdl":                v.hdl,
            "egfr":               v.egfr,
            "homa_ir":            v.homa_ir,
            "homa_ir_category":   v.homa_ir_category,
            "serum_creatinine":   v.serum_creatinine,
            "n_oral_antidiabetics": v.n_oral_antidiabetics,
            "drugs":              [d for d in [v.drug_1, v.drug_2] if d],
            "statin":             v.statin,
            "lifestyle": {
                "smokes":            v.cur_smoke,
                "alcohol":           v.cons_alcohol,
                "vigorous_activity": v.vig_activity,
                "moderate_activity": v.mod_activity,
                "walking":           v.walking,
                "walk_days_week":    v.walk_days_per_week,
                "sleep_hours":       v.hours_sleep,
            },
            "diet_days_per_week": {
                "eggs_protein":  v.diet_eggs_protein,
                "fruits":        v.diet_fruits,
                "vegetables":    v.diet_vegetables,
                "moringa":       v.diet_moringa,
                "nuts_seeds":    v.diet_nuts_seeds,
                "extra_meals":   v.diet_extra_meals,
                "soft_drinks":   v.diet_soft_drinks,
                "junk_foods":    v.diet_junk_foods,
            },
            "quality_of_life": {
                "eq5d_mobility":      v.eq5d_mobility,
                "eq5d_pain":          v.eq5d_pain,
                "eq5d_anxiety":       v.eq5d_anxiety,
                "health_vas_0_100":   v.eq5d_health_vas,
                "mental_health_0_10": v.mental_health_score,
                "gad7_score_0_21":    v.gad7_score,
                "phq9_score_0_27":    v.phq9_score,
            },
        }

    sorted_visits = sorted(
        visits,
        key=lambda v: VISIT_ORDER.index(v.visit_label) if v.visit_label in VISIT_ORDER else 99
    )

    return {
        "patient": {
            "pid":                  patient.pid,
            "zone":                 patient.zone,
            "uphc":                 patient.uphc,
            "intervention_arm":     patient.arm,
            "age":                  patient.age,
            "gender":               patient.gender,
            "education_years":      patient.education_years,
            "occupation":           patient.occupation,
            "monthly_income_inr":   patient.income_monthly,
            "family_members":       patient.family_members,
            "height_cm":            patient.height_cm,
            "diabetes_duration_yr": patient.diabetes_duration_yr,
            "comorbidities": {
                "hypertension": patient.hypertension,
                "heart_attack": patient.heart_attack,
                "stroke":       patient.stroke,
                "neuropathy":   patient.neuropathy,
                "retinopathy":  patient.retinopathy,
                "ckd":          patient.ckd,
            },
        },
        "visits": [_visit_dict(v) for v in sorted_visits],
    }


# ─── Recommendation storage ────────────────────────────────────────────────────

def save_recommendation(db: Session, pid: str, model: str, advice: dict) -> models.Recommendation:
    rec = models.Recommendation(
        pid=pid,
        model_used=model,
        generated_at=datetime.now(timezone.utc).isoformat(),
        assessment=advice.get("current_diet_assessment"),
        priority_changes=json.dumps(advice.get("priority_changes", [])),
        breakfast=advice.get("breakfast"),
        lunch=advice.get("lunch"),
        dinner=advice.get("dinner"),
        foods_to_avoid=json.dumps(advice.get("foods_to_avoid", [])),
        clinical_note=advice.get("clinical_note"),
        raw_response=json.dumps(advice),
    )
    db.add(rec)
    db.commit()
    db.refresh(rec)
    return rec


def get_recommendations(db: Session, pid: str) -> list:
    return (
        db.query(models.Recommendation)
        .filter(models.Recommendation.pid == pid)
        .order_by(models.Recommendation.generated_at.desc())
        .all()
    )


def get_recommendation_by_id(db: Session, rec_id: int) -> models.Recommendation:
    return db.query(models.Recommendation).filter(models.Recommendation.id == rec_id).first()


# ─── Feedback storage ──────────────────────────────────────────────────────────

def save_feedback_batch(
    db: Session,
    recommendation_id: int,
    pid: str,
    items: dict,
    nutritionist: str,
) -> None:
    """
    items: { field_name: (rating, notes), ... }
    Upserts — updates existing rating for same rec+field, inserts new ones.
    """
    timestamp = datetime.now(timezone.utc).isoformat()

    for field_name, (rating, notes) in items.items():
        existing = (
            db.query(models.Feedback)
            .filter(
                models.Feedback.recommendation_id == recommendation_id,
                models.Feedback.field_name == field_name,
            )
            .first()
        )
        if existing:
            existing.rating = rating
            existing.notes = notes
            existing.nutritionist = nutritionist
            existing.submitted_at = timestamp
        else:
            db.add(models.Feedback(
                recommendation_id=recommendation_id,
                pid=pid,
                field_name=field_name,
                rating=rating,
                notes=notes,
                nutritionist=nutritionist,
                submitted_at=timestamp,
            ))

    db.commit()


def get_feedback_for_recommendation(db: Session, rec_id: int) -> list:
    return (
        db.query(models.Feedback)
        .filter(models.Feedback.recommendation_id == rec_id)
        .all()
    )


def get_all_feedback(db: Session) -> list:
    return (
        db.query(models.Feedback)
        .order_by(models.Feedback.submitted_at.desc())
        .all()
    )


def update_recommendation(db: Session, rec_id: int, fields: dict) -> models.Recommendation:
    """Overwrite specific text fields on an existing recommendation row."""
    rec = get_recommendation_by_id(db, rec_id)
    if not rec:
        raise ValueError(f"Recommendation ID {rec_id} not found")
    for key, value in fields.items():
        setattr(rec, key, value)
    db.commit()
    db.refresh(rec)
    return rec
