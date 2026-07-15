"""
Load sample_to_iisc.csv into ckm.db (SQLite).
Run from project root:  python -m ckm_api.seed
"""
import pandas as pd
import numpy as np
from ckm_api.database import engine, SessionLocal, Base
from ckm_api import models

VISIT_ORDER = ["Baseline", "3rd month", "6th month", "9th month", "12th month"]

GAD_COLS = ["nervous", "control_worry", "worry_things", "trouble",
            "restless", "irritable", "afraid"]
PHQ_COLS = ["little_int", "feeling_down", "asleep", "little_energy",
            "poor_appetite", "feel_bad", "trouble_concentrate",
            "speak_slowly", "hurt_yourself"]
FREQ_MAP  = {"Not at all": 0, "Several days": 1,
             "More than half the days": 2, "Nearly every day": 3}


def _score_gad(row):
    return sum(FREQ_MAP.get(str(row.get(c, "Not at all")), 0) for c in GAD_COLS)


def _score_phq(row):
    return sum(FREQ_MAP.get(str(row.get(c, "Not at all")), 0) for c in PHQ_COLS)


def _val(row, col):
    v = row.get(col)
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return None
    if str(v).strip().upper() in ("NA", "NAN", "NONE", ""):
        return None
    return v


def _float(row, col):
    v = _val(row, col)
    try:
        return float(v) if v is not None else None
    except (ValueError, TypeError):
        return None


def _int(row, col):
    v = _float(row, col)
    return int(v) if v is not None else None


def _str(row, col):
    v = _val(row, col)
    return str(v) if v is not None else None


def seed():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    df = pd.read_csv("sample_to_iisc.csv")
    df = df.where(pd.notnull(df), None)

    db = SessionLocal()

    # ── Patients (from Baseline rows) ──────────────────────────────────────
    bl = df[df["followup"] == "Baseline"]
    for _, r in bl.iterrows():
        row = r.to_dict()
        p = models.Patient(
            pid                  = str(row["pid"]),
            zone                 = _str(row, "zone"),
            uphc                 = _str(row, "uphc"),
            arm                  = _str(row, "arm"),
            age                  = _int(row, "age_bl"),
            gender               = _str(row, "gender_bl"),
            marital_status       = _str(row, "mar_stat_bl"),
            education_years      = _int(row, "education_bl"),
            occupation           = _str(row, "occupation_bl"),
            income_monthly       = _int(row, "month_income_bl"),
            family_members       = _int(row, "tot_fam_mem_bl"),
            height_cm            = _float(row, "height_bl"),
            diabetes_duration_yr = _int(row, "diab_dur_bl"),
            hypertension         = _str(row, "hypertension"),
            heart_attack         = _str(row, "hrt_attck"),
            stroke               = _str(row, "stroke"),
            neuropathy           = _str(row, "dia_neuro"),
            retinopathy          = _str(row, "dia_retino"),
            ckd                  = _str(row, "ckd"),
            med_adherence        = _str(row, "med_take_bl"),
            drug_source          = _str(row, "type_hlth_fac_visited_bl"),
            baseline_fruit_days  = _int(row, "days_eat_fruit_bl"),
            baseline_veg_days    = _int(row, "days_eat_veg_bl"),
        )
        db.merge(p)

    # ── Visits (all rows) ───────────────────────────────────────────────────
    for _, r in df.iterrows():
        row = r.to_dict()

        # GAD-7 / PHQ-9 only computed when data exists (Baseline & 12th month)
        has_questionnaire = any(
            row.get(c) not in (None, "NA", "nan") for c in GAD_COLS
        )
        gad7 = _score_gad(row) if has_questionnaire else None
        phq9 = _score_phq(row) if has_questionnaire else None

        v = models.Visit(
            pid                  = str(row["pid"]),
            visit_label          = str(row["followup"]),
            visit_date           = _str(row, "enroll_date"),
            attended             = _str(row, "part_came_followup"),
            reason_not_came      = _str(row, "reason_not_came"),
            weight_kg            = _float(row, "weight"),
            bmi                  = _float(row, "bmi"),
            bmi_category         = _str(row, "bmi_cat"),
            waist_cm             = _float(row, "waist"),
            sys_bp               = _float(row, "sys_bp"),
            dia_bp               = _float(row, "dia_bp"),
            htn_controlled       = _str(row, "htn_bp"),
            hb_a1c               = _float(row, "hb_a1c"),
            total_cholesterol    = _float(row, "tot_chol"),
            triglycerides        = _float(row, "trig"),
            ldl                  = _float(row, "low_lipo"),
            hdl                  = _float(row, "hig_lipo"),
            vldl                 = _float(row, "ver_lipo"),
            egfr                 = _float(row, "egfr"),
            homa_ir              = _float(row, "homa_ir"),
            homa_ir_category     = _str(row, "homa_ir_cat"),
            serum_creatinine     = _float(row, "ser_creat"),
            fasting_glucose      = _float(row, "fast_gluc"),
            fasting_insulin      = _float(row, "fast_insulin"),
            n_oral_antidiabetics = _int(row, "n_oral_antidiabetics"),
            n_antidiabetics_cat  = _str(row, "n_oral_antidiabetics_cat"),
            drug_1               = _str(row, "drug_1"),
            dose_1               = _float(row, "dose_1"),
            drug_2               = _str(row, "drug_2"),
            dose_2               = _float(row, "dose_2"),
            statin               = _str(row, "statin"),
            med_changes          = _str(row, "med_changes"),
            cur_smoke            = _str(row, "cur_smoke"),
            cons_alcohol         = _str(row, "cons_alcohol"),
            vig_activity         = _str(row, "vig_phy_activity"),
            mod_activity         = _str(row, "mod_phy_activity"),
            walking              = _str(row, "walk"),
            walk_days_per_week   = _float(row, "days_walk"),
            walk_min_per_day     = _float(row, "time_walk"),
            hours_sleep          = _float(row, "hours_sleep"),
            sleep_disturbed      = _str(row, "sleep_distrub"),
            diet_eggs_protein    = _float(row, "eggs_protein"),
            diet_fruits          = _float(row, "more_fruits"),
            diet_vegetables      = _float(row, "more_vegetables"),
            diet_moringa         = _float(row, "moringa_squashes"),
            diet_nuts_seeds      = _float(row, "nuts_seeds"),
            diet_extra_meals     = _float(row, "more_meal"),
            diet_soft_drinks     = _float(row, "soft_drinks"),
            diet_junk_foods      = _float(row, "junk_foods"),
            eq5d_mobility        = _str(row, "mobility"),
            eq5d_self_care       = _str(row, "self_care"),
            eq5d_usual_activity  = _str(row, "usual_activity"),
            eq5d_pain            = _str(row, "pain"),
            eq5d_anxiety         = _str(row, "anxiety"),
            eq5d_health_vas      = _float(row, "health_range"),
            mental_health_score  = _float(row, "men_hlth"),
            gad7_score           = gad7,
            phq9_score           = phq9,
        )
        db.add(v)

    db.commit()
    db.close()

    # Quick check
    db2 = SessionLocal()
    n_patients = db2.query(models.Patient).count()
    n_visits   = db2.query(models.Visit).count()
    db2.close()
    print(f"Seeded {n_patients} patients and {n_visits} visits into ckm.db")


if __name__ == "__main__":
    seed()
