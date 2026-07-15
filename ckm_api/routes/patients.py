from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ckm_api.database import get_db
from ckm_api import crud, schemas

router = APIRouter()


@router.get("/", summary="List all patients")
def list_patients(db: Session = Depends(get_db)):
    patients = crud.get_all_patients(db)
    return [
        {
            "pid":  p.pid,
            "arm":  p.arm,
            "age":  p.age,
            "gender": p.gender,
            "uphc": p.uphc,
            "diabetes_duration_yr": p.diabetes_duration_yr,
        }
        for p in patients
    ]


@router.get("/{pid}", summary="Full patient record with all visits")
def get_patient(pid: str, db: Session = Depends(get_db)):
    patient, visits = crud.get_patient_with_visits(db, pid)
    if not patient:
        raise HTTPException(status_code=404, detail=f"Patient '{pid}' not found")
    return crud.build_patient_json(patient, visits)


@router.get("/{pid}/latest", summary="Latest attended visit data only")
def get_latest(pid: str, db: Session = Depends(get_db)):
    patient = crud.get_patient(db, pid)
    if not patient:
        raise HTTPException(status_code=404, detail=f"Patient '{pid}' not found")
    latest = crud.get_latest_visit(db, pid)
    if not latest:
        raise HTTPException(status_code=404, detail="No visits found")
    return {
        "pid":         pid,
        "arm":         patient.arm,
        "latest_visit": latest.visit_label,
        "date":        latest.visit_date,
        "hb_a1c":      latest.hb_a1c,
        "weight_kg":   latest.weight_kg,
        "bmi":         latest.bmi,
        "sys_bp":      latest.sys_bp,
        "dia_bp":      latest.dia_bp,
        "n_oral_antidiabetics": latest.n_oral_antidiabetics,
        "diet": {
            "soft_drinks_days_week": latest.diet_soft_drinks,
            "junk_foods_days_week":  latest.diet_junk_foods,
            "vegetables_days_week":  latest.diet_vegetables,
            "fruits_days_week":      latest.diet_fruits,
        },
    }


@router.get("/{pid}/summary", summary="Structured patient summary JSON (input to LLM)")
def get_summary(pid: str, db: Session = Depends(get_db)):
    patient, visits = crud.get_patient_with_visits(db, pid)
    if not patient:
        raise HTTPException(status_code=404, detail=f"Patient '{pid}' not found")
    return crud.build_patient_json(patient, visits)


@router.get("/{pid}/trends", summary="Clinical trends across all visits")
def get_trends(pid: str, db: Session = Depends(get_db)):
    patient = crud.get_patient(db, pid)
    if not patient:
        raise HTTPException(status_code=404, detail=f"Patient '{pid}' not found")
    visits = crud.get_visits(db, pid)
    return {
        "pid": pid,
        "arm": patient.arm,
        "trends": [
            {
                "visit":     v.visit_label,
                "date":      v.visit_date,
                "hb_a1c":    v.hb_a1c,
                "weight_kg": v.weight_kg,
                "bmi":       round(v.bmi, 2) if v.bmi else None,
                "sys_bp":    v.sys_bp,
                "dia_bp":    v.dia_bp,
                "waist_cm":  v.waist_cm,
            }
            for v in visits if v.attended != "No"
        ],
    }
