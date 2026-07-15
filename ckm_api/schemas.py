from pydantic import BaseModel
from typing import Optional, List


class VisitOut(BaseModel):
    visit_label:          str
    visit_date:           Optional[str]
    attended:             Optional[str]
    reason_not_came:      Optional[str]
    weight_kg:            Optional[float]
    bmi:                  Optional[float]
    bmi_category:         Optional[str]
    waist_cm:             Optional[float]
    sys_bp:               Optional[float]
    dia_bp:               Optional[float]
    hb_a1c:               Optional[float]
    total_cholesterol:    Optional[float]
    triglycerides:        Optional[float]
    ldl:                  Optional[float]
    hdl:                  Optional[float]
    egfr:                 Optional[float]
    homa_ir:              Optional[float]
    homa_ir_category:     Optional[str]
    serum_creatinine:     Optional[float]
    n_oral_antidiabetics: Optional[int]
    n_antidiabetics_cat:  Optional[str]
    drug_1:               Optional[str]
    drug_2:               Optional[str]
    statin:               Optional[str]
    cur_smoke:            Optional[str]
    cons_alcohol:         Optional[str]
    vig_activity:         Optional[str]
    mod_activity:         Optional[str]
    walking:              Optional[str]
    walk_days_per_week:   Optional[float]
    hours_sleep:          Optional[float]
    diet_eggs_protein:    Optional[float]
    diet_fruits:          Optional[float]
    diet_vegetables:      Optional[float]
    diet_moringa:         Optional[float]
    diet_nuts_seeds:      Optional[float]
    diet_extra_meals:     Optional[float]
    diet_soft_drinks:     Optional[float]
    diet_junk_foods:      Optional[float]
    eq5d_mobility:        Optional[str]
    eq5d_pain:            Optional[str]
    eq5d_anxiety:         Optional[str]
    eq5d_health_vas:      Optional[float]
    mental_health_score:  Optional[float]
    gad7_score:           Optional[int]
    phq9_score:           Optional[int]

    class Config:
        from_attributes = True


class PatientOut(BaseModel):
    pid:                  str
    zone:                 Optional[str]
    uphc:                 Optional[str]
    arm:                  str
    age:                  Optional[int]
    gender:               Optional[str]
    marital_status:       Optional[str]
    education_years:      Optional[int]
    occupation:           Optional[str]
    income_monthly:       Optional[int]
    family_members:       Optional[int]
    height_cm:            Optional[float]
    diabetes_duration_yr: Optional[int]
    hypertension:         Optional[str]
    heart_attack:         Optional[str]
    neuropathy:           Optional[str]
    retinopathy:          Optional[str]
    ckd:                  Optional[str]
    visits:               List[VisitOut] = []

    class Config:
        from_attributes = True


class DietAdviceOut(BaseModel):
    pid:                     str
    patient_name_label:      str
    clinical_snapshot:       dict
    current_diet_assessment: str
    priority_changes:        List[str]
    recommended_foods:       List[str]
    foods_to_reduce:         List[str]
    meal_pattern_advice:     str
    arm_specific_guidance:   str
    targets_next_visit:      str
    important_note:          str
