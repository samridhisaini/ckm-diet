from sqlalchemy import Column, String, Float, Integer, Text, ForeignKey
from ckm_api.database import Base


class Patient(Base):
    """Static baseline demographics — one row per patient."""
    __tablename__ = "patients"

    pid                  = Column(String, primary_key=True, index=True)
    zone                 = Column(String)
    uphc                 = Column(String)
    arm                  = Column(String)
    age                  = Column(Integer)
    gender               = Column(String)
    marital_status       = Column(String)
    education_years      = Column(Integer)
    occupation           = Column(String)
    income_monthly       = Column(Integer)
    family_members       = Column(Integer)
    height_cm            = Column(Float)
    diabetes_duration_yr = Column(Integer)
    hypertension         = Column(String)
    heart_attack         = Column(String)
    stroke               = Column(String)
    neuropathy           = Column(String)
    retinopathy          = Column(String)
    ckd                  = Column(String)
    med_adherence        = Column(String)
    drug_source          = Column(String)
    baseline_fruit_days  = Column(Integer)
    baseline_veg_days    = Column(Integer)


class Visit(Base):
    """One row per patient per visit — clinical + diet + QoL data."""
    __tablename__ = "visits"

    id                   = Column(Integer, primary_key=True, autoincrement=True)
    pid                  = Column(String, index=True)
    visit_label          = Column(String)
    visit_date           = Column(String)
    attended             = Column(String)
    reason_not_came      = Column(String)

    weight_kg            = Column(Float)
    bmi                  = Column(Float)
    bmi_category         = Column(String)
    waist_cm             = Column(Float)

    sys_bp               = Column(Float)
    dia_bp               = Column(Float)
    htn_controlled       = Column(String)

    hb_a1c               = Column(Float)

    total_cholesterol    = Column(Float)
    triglycerides        = Column(Float)
    ldl                  = Column(Float)
    hdl                  = Column(Float)
    vldl                 = Column(Float)
    egfr                 = Column(Float)
    homa_ir              = Column(Float)
    homa_ir_category     = Column(String)
    serum_creatinine     = Column(Float)
    fasting_glucose      = Column(Float)
    fasting_insulin      = Column(Float)

    n_oral_antidiabetics = Column(Integer)
    n_antidiabetics_cat  = Column(String)
    drug_1               = Column(String)
    dose_1               = Column(Float)
    drug_2               = Column(String)
    dose_2               = Column(Float)
    statin               = Column(String)
    med_changes          = Column(String)

    cur_smoke            = Column(String)
    cons_alcohol         = Column(String)
    vig_activity         = Column(String)
    mod_activity         = Column(String)
    walking              = Column(String)
    walk_days_per_week   = Column(Float)
    walk_min_per_day     = Column(Float)
    hours_sleep          = Column(Float)
    sleep_disturbed      = Column(String)

    diet_eggs_protein    = Column(Float)
    diet_fruits          = Column(Float)
    diet_vegetables      = Column(Float)
    diet_moringa         = Column(Float)
    diet_nuts_seeds      = Column(Float)
    diet_extra_meals     = Column(Float)
    diet_soft_drinks     = Column(Float)
    diet_junk_foods      = Column(Float)

    eq5d_mobility        = Column(String)
    eq5d_self_care       = Column(String)
    eq5d_usual_activity  = Column(String)
    eq5d_pain            = Column(String)
    eq5d_anxiety         = Column(String)
    eq5d_health_vas      = Column(Float)
    mental_health_score  = Column(Float)
    gad7_score           = Column(Integer)
    phq9_score           = Column(Integer)


class Recommendation(Base):
    """One row per LLM diet advice call — stores structured advice fields."""
    __tablename__ = "recommendations"

    id               = Column(Integer, primary_key=True, autoincrement=True)
    pid              = Column(String, index=True)
    model_used       = Column(String)            # e.g. gemini-2.5-flash
    generated_at     = Column(String)            # ISO 8601 UTC timestamp
    assessment       = Column(Text)              # current_diet_assessment
    priority_changes = Column(Text)              # JSON list
    breakfast        = Column(Text)
    lunch            = Column(Text)
    dinner           = Column(Text)
    foods_to_avoid   = Column(Text)              # JSON list
    clinical_note    = Column(Text)
    raw_response     = Column(Text)              # full JSON for audit


class Feedback(Base):
    """Nutritionist ratings per recommendation field — one row per field per submission."""
    __tablename__ = "feedback"

    id                = Column(Integer, primary_key=True, autoincrement=True)
    recommendation_id = Column(Integer, ForeignKey("recommendations.id"), index=True)
    pid               = Column(String, index=True)
    field_name        = Column(String)   # breakfast | lunch | dinner | avoid_0 | clinical_note | etc.
    rating            = Column(String)   # good | bad
    notes             = Column(Text)
    nutritionist      = Column(String)
    submitted_at      = Column(String)   # ISO 8601 UTC timestamp
