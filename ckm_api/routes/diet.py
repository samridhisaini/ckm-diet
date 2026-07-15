from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ckm_api.database import get_db
from ckm_api import crud
from ckm_api.llm.dietician import get_diet_advice, AVAILABLE_MODELS, DEFAULT_MODEL

router = APIRouter()


@router.post("/{pid}/advice", summary="Get personalised LLM diet advice for a patient")
def diet_advice(
    pid: str,
    model: str = Query(default=DEFAULT_MODEL, description=f"Model to use. Options: {AVAILABLE_MODELS}"),
    db: Session = Depends(get_db),
):
    patient, visits = crud.get_patient_with_visits(db, pid)
    if not patient:
        raise HTTPException(status_code=404, detail=f"Patient '{pid}' not found")
    if not visits:
        raise HTTPException(status_code=404, detail="No visit data found for this patient")

    patient_json = crud.build_patient_json(patient, visits)

    try:
        advice = get_diet_advice(patient_json, model=model)
    except EnvironmentError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=502, detail=str(e))

    # Persist recommendation to DB
    rec = crud.save_recommendation(db, pid, model, advice)

    return {
        "recommendation_id": rec.id,
        "pid":               pid,
        "model_used":        model,
        "generated_at":      rec.generated_at,
        "arm":               patient.arm,
        "age":               patient.age,
        "gender":            patient.gender,
        "clinical_snapshot": {
            "latest_hba1c":      next(
                (v.hb_a1c for v in reversed(visits) if v.hb_a1c is not None), None
            ),
            "baseline_hba1c":    visits[0].hb_a1c if visits else None,
            "latest_bmi":        next(
                (round(v.bmi, 2) for v in reversed(visits) if v.bmi is not None), None
            ),
            "hypertension":      patient.hypertension,
            "diabetes_duration": patient.diabetes_duration_yr,
        },
        "diet_advice": advice,
    }
