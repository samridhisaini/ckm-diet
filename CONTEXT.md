# CKM / LCD Study — Complete Data & Analysis Context

> **Last updated:** 2026-06-19  
> **Working directory:** `/Users/samridhisaini/Tanuh/CKM_data_analysis/`  
> **Python environment:** `venv/` (activate before running any script)

---

## 1. Study Background

**Full name:** Lifestyle Change for Diabetes (LCD) Follow-Up Programme  
**Location:** Chennai, Tamil Nadu, India  
**Setting:** Urban Primary Health Centres (UPHCs) under the Greater Chennai Corporation  
**Design:** Prospective longitudinal cohort with two intervention arms  
**Duration:** 12 months per patient (5 scheduled visits)  
**Purpose:** To evaluate the effect of a low-carbohydrate dietary intervention versus usual diet on glycaemic control and related metabolic, psychological, and quality-of-life outcomes in patients with Type 2 Diabetes Mellitus (T2DM).

---

## 2. Intervention Arms

| Arm Code | Label | Description |
|---|---|---|
| `Low carbohydrate diet` | Low-Carb (LCD) | Dietary counselling to reduce carbohydrate intake |
| `Usual diet` | Usual Care (UC) | Standard dietary advice as per UPHC protocol |

---

## 3. Dataset File

| Property | Value |
|---|---|
| Filename | `sample_to_iisc.csv` |
| Rows | 25 (5 patients × 5 visits each) |
| Columns | 157 |
| Structure | **Long format** — one row per patient per visit |
| Code reference (follow-up) | `LCD Followup ODK Codes.xlsx` |
| Code reference (baseline) | `LCD Baseline form ODK Codes.xlsx` |

> **Important:** The dataset is longitudinal. The 25 rows are NOT 25 separate patients — they are **5 patients**, each observed at **5 time points**.

---

## 4. Visit Schedule

| Visit Label | Approx. Time | Notes |
|---|---|---|
| `Baseline` | Month 0 | Full data collection: labs, anthropometrics, questionnaires |
| `3rd month` | Month 3 | Anthropometrics, HbA1c, medication review |
| `6th month` | Month 6 | Anthropometrics, HbA1c, medication review |
| `9th month` | Month 9 | Anthropometrics, HbA1c, medication review |
| `12th month` | Month 12 | Full data collection (same as Baseline) |

**Actual visit dates per patient:**

| Patient | Baseline | 3rd Month | 6th Month | 9th Month | 12th Month |
|---|---|---|---|---|---|
| P1 (1-3-3) | 11-Dec-2024 | 05-Mar-2025 | 18-Jun-2025 | 26-Sep-2025 | 09-Jan-2026 |
| P2 (2-7-11) | 10-Dec-2024 | 04-Mar-2025 | 17-Jun-2025 | 19-Sep-2025 | 08-Jan-2026 |
| P3 (3-10-13) | 11-Nov-2024 | 11-Feb-2025 | 21-May-2025 | 22-Aug-2025 | 22-Dec-2025 |
| P4 (4-14-17) | 21-Jan-2025 | 04-Apr-2025 | 14-Jul-2025 | 30-Oct-2025 | 28-Jan-2026 |
| P5 (4-16-11) | 29-Jan-2025 | 21-Apr-2025 | 18-Jul-2025 | 10-Nov-2025 | 05-Feb-2026 |

---

## 5. Patient Registry (Baseline Characteristics)

| Label | PID | Zone | UPHC | Arm | Age | Gender | Marital | Education | Occupation | Income/mo | Family | Housing |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **P1** | 1-3-3 | Zone IV: Tondiarpet | R.K. Nagar UPHC | Low-Carb | 54 | Male | Married | 7 yrs | Self-employed | ₹20,000 | 4 members | Pucca |
| **P2** | 2-7-11 | Zone VI: Thiruvika Nagar | Thanthai Periyar UPHC | Low-Carb | 48 | Male | Married | 12 yrs | Sales/Clerical | ₹9,000 | 3 members | Pucca |
| **P3** | 3-10-13 | Zone XI: Valasaravakkam | Maduravoyal UPHC | Usual | 51 | Female | Married | 14 yrs | Skilled labourer | ₹40,000 | 3 members | Pucca |
| **P4** | 4-14-17 | Zone XIII: Adyar | SRKV UPHC | Usual | 65 | Female | Widowed | 3 yrs | Homemaker | ₹1,000 | 1 member | Pucca |
| **P5** | 4-16-11 | Zone XIII: Adyar | Voluntary Health Services UPHC | Usual | 56 | Female | Married | 14 yrs | Professional | ₹90,000 | 4 members | Pucca |

| Label | Height (cm) | Baseline BMI | BMI Category | DM Duration | Hypertension | Heart Attack | Neuropathy | Retinopathy | CKD |
|---|---|---|---|---|---|---|---|---|---|
| P1 | 173 | 28.87 | Obese (≥25.0) | 4 yrs | Yes | No | No | No | No |
| P2 | 167 | 23.13 | Overweight (23.0–24.9) | 4 yrs | No | No | No | No | No |
| P3 | 140.5 | 35.46 | Obese (≥25.0) | 1 yr | Yes | Yes | No | No | No |
| P4 | 158.6 | 23.85 | Overweight (23.0–24.9) | 10 yrs | Yes | No | Yes | Yes | No |
| P5 | 157 | 20.69 | Normal (18.5–22.9) | 5 yrs | No | No | No | No | No |

---

## 6. Follow-up Attendance

`Yes` = physically attended the UPHC visit; `No` = missed the visit.

| Patient | 3rd Month | 6th Month | 9th Month | 12th Month | Missed Visits | Reasons for Missing |
|---|---|---|---|---|---|---|
| P1 | Yes | Yes | Yes | Yes | 0 | — |
| P2 | **No** | Yes | **No** | Yes | 2 | Lack of time; No response for calls |
| P3 | **No** | Yes | Yes | Yes | 1 | Work shifted to another location |
| P4 | Yes | Yes | Yes | Yes | 0 | — |
| P5 | Yes | Yes | Yes | Yes | 0 | — |

> When a patient missed a visit, clinical data for that row is entirely NA. Baseline attendance is not tracked (all patients enrolled at Baseline).

---

## 7. Complete Column Reference (157 columns)

### 7.1 Identifiers & Admin
| Column | Description | Type |
|---|---|---|
| `pid` | Patient ID (format: zone-uphc-ind_id) | string |
| `zone` | Zone name | string |
| `uphc` | UPHC name | string |
| `ind_id` | Individual ID within UPHC | integer |
| `arm` | Intervention arm | string |
| `followup` | Visit label | string |
| `enroll_date` | Date of visit (DD-MM-YYYY) | string |

### 7.2 Anthropometrics
| Column | Description | Unit | Collected |
|---|---|---|---|
| `weight` | Body weight | kg | All visits |
| `bmi` | Body mass index (computed) | kg/m² | All visits |
| `bmi_cat` | WHO Asia-Pacific BMI category | string | All visits |
| `waist` | Waist circumference | cm | All visits |
| `height_bl` | Height (baseline only, carried forward) | cm | Baseline |

### 7.3 Blood Pressure
| Column | Description | Unit | Collected |
|---|---|---|---|
| `sys_bp` | Systolic blood pressure | mmHg | All visits |
| `dia_bp` | Diastolic blood pressure | mmHg | All visits |
| `htn_bp` | HTN control status (Yes/No) | categorical | All visits |

### 7.4 Comorbidities (Yes/No — baseline values carried in all rows)
| Column | Condition |
|---|---|
| `hrt_attck` | History of heart attack |
| `stroke` | History of stroke |
| `hypertension` | Diagnosed hypertension |
| `ckd` | Chronic kidney disease |
| `dia_neuro` | Diabetic neuropathy |
| `dia_retino` | Diabetic retinopathy |
| `ulcer` | Diabetic foot ulcer |
| `other_med_con` | Other medical conditions |
| `specify` | Free-text for other condition |

### 7.5 Laboratory / Metabolic Markers
| Column | Description | Unit | Collected |
|---|---|---|---|
| `hb_a1c` | Glycated haemoglobin | % | All visits |
| `tot_chol` | Total cholesterol | mg/dL | Baseline & 12th month only |
| `trig` | Triglycerides | mg/dL | Baseline & 12th month only |
| `low_lipo` | LDL cholesterol | mg/dL | Baseline & 12th month only |
| `ver_lipo` | VLDL cholesterol | mg/dL | Baseline & 12th month only |
| `hig_lipo` | HDL cholesterol | mg/dL | Baseline & 12th month only |
| `egfr` | Estimated glomerular filtration rate | mL/min/1.73m² | Baseline & 12th month only |
| `ser_creat` | Serum creatinine | mg/dL | Baseline & 12th month only |
| `homa_ir` | HOMA-IR insulin resistance score | score | Baseline & 12th month only |
| `homa_ir_cat` | HOMA-IR category (Normal/Abnormal) | categorical | Baseline & 12th month only |
| `fast_gluc` | Fasting glucose | mg/dL | Baseline (selected visits) |
| `pst_fast_gluc` | Post-fasting glucose | mg/dL | Baseline |
| `fast_insulin` | Fasting insulin | µU/mL | Baseline (selected visits) |
| `rbs` | Random blood sugar | mg/dL | Baseline |

### 7.6 Smoking / Tobacco / Alcohol
| Column | Description |
|---|---|
| `cur_smoke` | Currently smokes cigarettes/beedis (Yes/No) |
| `smoke_daily` | Smokes daily (Yes/No) |
| `sm_hw_many_daily` | Number of cigarettes/beedis per day |
| `sm_hw_many_week` | Number of cigarettes/beedis per week |
| `cur_smokeless` | Currently uses smokeless tobacco (Yes/No) |
| `sm_less_daily` | Uses smokeless tobacco daily (Yes/No) |
| `sm_less_hw_many_daily` | Smokeless tobacco units per day |
| `sm_less_hw_many_week` | Smokeless tobacco units per week |
| `cons_alcohol` | Consumes alcohol (Yes/No) |
| `hw_mny_occasion` | Drinking occasions per week |
| `hw_mny_std_drink` | Standard drinks per occasion |

### 7.7 Physical Activity (WHO GPAQ-style)
| Column | Description |
|---|---|
| `vig_phy_activity` | Does vigorous physical activity (Yes/No) |
| `days_vig_activity` | Days/week of vigorous activity |
| `time_vig_activity` | Minutes/day of vigorous activity |
| `mod_phy_activity` | Does moderate physical activity (Yes/No) |
| `days_mod_activity` | Days/week of moderate activity |
| `time_mod_activity` | Minutes/day of moderate activity |
| `walk` | Walks for transport/leisure (Yes/No) |
| `days_walk` | Days/week of walking |
| `time_walk` | Minutes/day of walking |

### 7.8 Sleep
| Column | Description |
|---|---|
| `hours_sleep` | Hours of sleep per night |
| `sleep_distrub` | Sleep disturbance (Yes/No) |

### 7.9 EQ-5D Quality of Life (Collected ONLY at Baseline and 12th Month)
| Column | Domain | Response scale |
|---|---|---|
| `mobility` | Mobility | No problems / Slight / Moderate / Severe / Extreme |
| `self_care` | Self-care | No problems / Slight / Moderate / Severe / Extreme |
| `usual_activity` | Usual activities | No problems / Slight / Moderate / Severe / Extreme |
| `pain` | Pain/discomfort | No pain / Slight / Moderate / Severe / Extreme |
| `anxiety` | Anxiety/depression | Not anxious / Slight / Moderate / Severe / Extreme |
| `men_hlth` | Mental health score (clinician-rated) | 0–10 scale |
| `health_range` | EQ-5D VAS (self-rated overall health) | 0–100 scale |

### 7.10 Medication Adherence (Morisky 4-Item Scale)
| Column | Question | Response |
|---|---|---|
| `ever_forget` | Do you ever forget to take your medicine? | Yes/No |
| `careless_at_times` | Are you careless at times about taking medicine? | Yes/No |
| `stop_taking_med` | Do you stop taking when you feel better? | Yes/No |
| `feel_worse_med` | Do you stop taking when you feel worse? | Yes/No |

> **Scoring:** Each "Yes" = 1 poor-adherence point. All "No" = good adherence.

### 7.11 Medications (Up to 5 drugs tracked)
| Column pattern | Description |
|---|---|
| `no_drugs` | Total number of diabetes drugs |
| `drug_1` … `drug_5` | Drug name (T.Metformin, T.Glibenclamide, T.Glimipride, etc.) |
| `drug_others_1` … `drug_others_5` | Free-text if "Other" selected |
| `dose_1` … `dose_5` | Dose in mg |
| `times_1` … `times_5` | Times per day |
| `no_tab_1` … `no_tab_5` | Number of tablets per dose |
| `duration_1` … `duration_5` | Duration of current prescription (months) |
| `statin` | Prescribed a statin (Yes/No) |
| `n_oral_antidiabetics` | Count of oral antidiabetic drugs (derived) |
| `n_oral_antidiabetics_cat` | Category: 0 drugs / 1 drug / ≥2 drugs |
| `insulin_use` | On insulin (Yes/No) |
| `med_changes` | Medication changes since last visit (Yes/No) |

### 7.12 Diet Frequency (days/week, 0–7)
| Column | Food group |
|---|---|
| `eggs_protein` | Eggs and protein foods |
| `more_fruits` | Fruits |
| `more_vegetables` | Vegetables |
| `moringa_squashes` | Moringa / squashes |
| `nuts_seeds` | Nuts and seeds |
| `more_meal` | Extra meals / snacks |
| `soft_drinks` | Soft drinks / sugary beverages |
| `junk_foods` | Junk / fried foods |

### 7.13 GAD-7 (Anxiety — Collected ONLY at Baseline and 12th Month)
7 items, each scored: Not at all (0) / Several days (1) / More than half the days (2) / Nearly every day (3). Max score = 21.

| Column | GAD-7 Question |
|---|---|
| `nervous` | Feeling nervous, anxious or on edge |
| `control_worry` | Not being able to stop or control worrying |
| `worry_things` | Worrying too much about different things |
| `trouble` | Trouble relaxing |
| `restless` | Being so restless that it's hard to sit still |
| `irritable` | Becoming easily annoyed or irritable |
| `afraid` | Feeling afraid as if something awful might happen |

**Score interpretation:** 0–4 Minimal, 5–9 Mild, 10–14 Moderate, 15–21 Severe anxiety.

### 7.14 PHQ-9 (Depression — Collected ONLY at Baseline and 12th Month)
9 items, same 0–3 scale. Max score = 27.

| Column | PHQ-9 Question |
|---|---|
| `little_int` | Little interest or pleasure in doing things |
| `feeling_down` | Feeling down, depressed, or hopeless |
| `asleep` | Trouble falling or staying asleep, or sleeping too much |
| `little_energy` | Feeling tired or having little energy |
| `poor_appetite` | Poor appetite or overeating |
| `feel_bad` | Feeling bad about yourself |
| `trouble_concentrate` | Trouble concentrating on things |
| `speak_slowly` | Moving or speaking so slowly / being fidgety |
| `hurt_yourself` | Thoughts of hurting yourself |

**Score interpretation:** 0–4 None, 5–9 Mild, 10–14 Moderate, 15–19 Moderately severe, 20–27 Severe depression.

### 7.15 Baseline-Only Variables (Carried Forward in All Rows)
| Column | Description |
|---|---|
| `age_bl` | Age at baseline (years) |
| `gender_bl` | Gender |
| `mar_stat_bl` | Marital status |
| `education_bl` | Years of formal education |
| `occupation_bl` | Occupation category |
| `pincode_bl` | Residential pincode |
| `month_income_bl` | Monthly household income (₹) |
| `tot_fam_mem_bl` | Total family members |
| `house_type_bl` | House type (Pucca/Kutcha) |
| `height_bl` | Height (cm) |
| `diab_dur_bl` | Duration of diabetes (years) |
| `eat_fruit_bl` | Eats fruits (Yes/No) |
| `days_eat_fruit_bl` | Days/week fruits eaten |
| `no_servings_fruit_bl` | Servings of fruit per day |
| `days_eat_veg_bl` | Days/week vegetables eaten |
| `no_servings_veg_bl` | Servings of vegetables per day |
| `med_take_bl` | Takes medications (Regular/Missed few) |
| `res_not_take_med_bl` | Reason for not taking medication |
| `where_rec_drugs_bl` | Where drugs were received |
| `hw_long_drug_issued_bl` | How long drugs issued for (months) |
| `pres_review_bl` | Prescription reviewed (Yes/No / Strip not available) |
| `last_visit_health_fac_bl` | Months since last health facility visit |
| `type_hlth_fac_visited_bl` | Type of facility (PHC / Private clinic) |

### 7.16 Follow-up Admin
| Column | Description |
|---|---|
| `part_came_followup` | Patient physically attended this visit (Yes/No) |
| `reason_not_came` | Reason for missing (Lack of time / Others) |
| `reason_others` | Free-text reason |
| `reason_missing` | Consolidated reason for missing data |

---

## 8. Key Data Values

### 8.1 HbA1c (%) — All Visits
| Patient | Arm | Baseline | 3rd Mo | 6th Mo | 9th Mo | 12th Mo | Change (BL→12M) |
|---|---|---|---|---|---|---|---|
| P1 | Low-Carb | 9.4 | 9.9 | 9.8 | 10.2 | 8.5 | **−0.9** |
| P2 | Low-Carb | 7.6 | — | 10.4 | — | 10.3 | **+2.7** |
| P3 | Usual | 11.2 | — | 7.7 | 7.4 | 6.3 | **−4.9** |
| P4 | Usual | 8.1 | 7.9 | 7.9 | 7.4 | 8.3 | **+0.2** |
| P5 | Usual | 7.7 | 7.5 | 8.1 | 8.0 | 9.2 | **+1.5** |

> P2 missed 3rd and 9th month visits — those HbA1c values are missing by design, not data error.

### 8.2 Weight (kg) — All Visits
| Patient | Arm | Baseline | 3rd Mo | 6th Mo | 9th Mo | 12th Mo | Change |
|---|---|---|---|---|---|---|---|
| P1 | Low-Carb | 86.4 | 87.3 | 81.2 | 86.8 | 86.5 | **+0.1** |
| P2 | Low-Carb | 64.5 | — | 63.1 | — | 60.2 | **−4.3** |
| P3 | Usual | 70.0 | — | 70.2 | 70.7 | 70.4 | **+0.4** |
| P4 | Usual | 60.0 | 61.0 | 60.5 | 60.9 | 59.8 | **−0.2** |
| P5 | Usual | 51.0 | 50.8 | 50.0 | 51.8 | 49.8 | **−1.2** |

### 8.3 BMI (kg/m²) — All Visits
| Patient | Baseline | 3rd Mo | 6th Mo | 9th Mo | 12th Mo |
|---|---|---|---|---|---|
| P1 | 28.87 | 29.17 | 27.13 | 29.00 | 28.90 |
| P2 | 23.13 | — | 22.63 | — | 21.59 |
| P3 | 35.46 | — | 35.56 | 35.82 | 35.66 |
| P4 | 23.85 | 24.25 | 24.05 | 24.21 | 23.77 |
| P5 | 20.69 | 20.61 | 20.28 | 21.02 | 20.20 |

### 8.4 Waist Circumference (cm)
| Patient | Baseline | 3rd Mo | 6th Mo | 9th Mo | 12th Mo |
|---|---|---|---|---|---|
| P1 | 105 | 101 | 104 | 102 | 103 |
| P2 | 82 | — | 92 | — | 89 |
| P3 | 90 | — | 92 | 99 | 98 |
| P4 | 91 | 86 | 92 | 91 | 93 |
| P5 | 85 | 85 | 90 | 90 | 89 |

### 8.5 Blood Pressure (mmHg)
| Patient | Arm | SBP BL | SBP 12M | DBP BL | DBP 12M |
|---|---|---|---|---|---|
| P1 | Low-Carb | 140 | 134 | 80 | 83 |
| P2 | Low-Carb | 121 | 133 | 93 | 87 |
| P3 | Usual | 153 | 134 | 110 | 84 |
| P4 | Usual | 113 | 135 | 60 | 64 |
| P5 | Usual | 123 | 101 | 75 | 65 |

### 8.6 Lipid Profile & Metabolic Markers (Baseline → 12th Month)
| Patient | Total Chol | Trig | LDL | HDL | VLDL | eGFR | HOMA-IR | Serum Creat |
|---|---|---|---|---|---|---|---|---|
| **P1 BL** | 184.6 | 119.2 | 125.0 | 35.8 | 23.8 | 105.2 | 5.8 | 0.8 |
| **P1 12M** | 168.0 | 72.0 | 118.1 | 35.5 | 14.4 | 109.5 | 2.3 | 0.7 |
| **P2 BL** | 250.3 | 797.7 | 58.9 | 31.9 | 159.5 | 105.4 | 12.7 | 0.9 |
| **P2 12M** | 267.0 | 191.0 | 179.7 | 49.1 | 38.2 | 109.2 | 1.0 | 0.8 |
| **P3 BL** | 164.1 | 117.4 | 104.1 | 36.5 | 23.5 | 108.6 | 4.6 | 0.6 |
| **P3 12M** | 102.0 | 56.0 | 56.4 | 34.4 | 11.2 | 113.5 | 1.9 | 0.5 |
| **P4 BL** | 249.7 | 208.2 | 162.7 | 45.4 | 41.6 | 95.9 | 5.1 | 0.7 |
| **P4 12M** | 161.0 | 116.0 | 83.5 | 54.3 | 23.2 | 99.5 | 1.5 | 0.6 |
| **P5 BL** | 219.3 | 77.4 | 50.1 | 153.7 | 15.5 | 116.1 | 1.3 | 0.4 |
| **P5 12M** | 196.0 | 87.0 | 108.9 | 69.7 | 17.4 | 110.0 | 0.5 | 0.5 |

> P2 had severely elevated triglycerides at baseline (797.7 mg/dL — well above the hypertriglyceridaemia threshold of 200 mg/dL). This dropped dramatically to 191 mg/dL by 12th month.  
> P5 had unusually high HDL at baseline (153.7 mg/dL), which fell to 69.7 at 12th month — still in a healthy range.

### 8.7 Oral Antidiabetic Drug Count (per visit)
| Patient | Arm | Baseline | 3rd Mo | 6th Mo | 9th Mo | 12th Mo |
|---|---|---|---|---|---|---|
| P1 | Low-Carb | 2 | 1 | 0 | 1 | 0 |
| P2 | Low-Carb | 2 | 0 | 0 | 0 | 0 |
| P3 | Usual | 2 | 0 | 1 | 0 | 0 |
| P4 | Usual | 2 | 1 | 0 | 0 | 0 |
| P5 | Usual | 2 | 0 | 0 | 0 | 0 |

> All 5 patients were on 2 oral antidiabetic drugs at baseline. Drug counts reduced substantially over the year in most patients. Insulin was not used by any patient.

### 8.8 Baseline Drugs Prescribed
| Patient | Drug 1 | Drug 2 | Statin |
|---|---|---|---|
| P1 | T.Metformin 500mg | T.Glibenclamide | No |
| P2 | T.Metformin 500mg | T.Glimipride 1mg | **Yes** |
| P3 | T.Metformin 500mg | T.Glimipride 1mg | No |
| P4 | T.Metformin 500mg | T.Glimipride 1mg | No |
| P5 | T.Metformin 500mg | T.Glimipride 1mg | No |

### 8.9 Baseline Lifestyle
| Patient | Smokes | Smokeless Tobacco | Alcohol | Vigorous PA | Moderate PA | Walks | Sleep (hrs) |
|---|---|---|---|---|---|---|---|
| P1 | **Yes** | No | No | No | Yes | No | 5 |
| P2 | No | No | **Yes** | No | Yes | No | 6 |
| P3 | No | No | No | No | Yes | No | 8 |
| P4 | No | No | No | No | Yes | Yes (3d/wk, 30min) | 4 |
| P5 | No | No | No | No | Yes | No | 5 |

### 8.10 Baseline Diet Frequency (days/week, 0–7)
| Patient | Eggs/Protein | Fruits | Vegetables | Moringa | Nuts | Extra Meals | Soft Drinks | Junk Foods |
|---|---|---|---|---|---|---|---|---|
| P1 | 4 | 1 | 4 | 0 | 1 | 0 | **7** | **7** |
| P2 | 4 | 0 | 3 | 1 | 0 | 0 | **7** | 2 |
| P3 | 3 | 1 | 3 | 3 | 1 | **7** | **7** | 5 |
| P4 | 5 | 0 | 1 | 0 | 0 | 0 | **7** | 0 |
| P5 | 4 | 2 | **7** | 1 | 3 | 0 | **7** | **7** |

> All 5 patients consumed soft drinks every single day (7/7) at baseline.

### 8.11 Baseline Comorbidities
| Patient | Heart Attack | Stroke | HTN | CKD | Neuropathy | Retinopathy | Ulcer |
|---|---|---|---|---|---|---|---|
| P1 | No | No | **Yes** | No | No | No | No |
| P2 | No | No | No | No | No | No | No |
| P3 | **Yes** | No | **Yes** | No | No | No | No |
| P4 | No | No | **Yes** | No | **Yes** | **Yes** | No |
| P5 | No | No | No | No | No | No | No |

### 8.12 Baseline Medication Adherence (Morisky 4-Item)
| Patient | Forgets | Careless | Stops when better | Stops when worse | Adherence Profile |
|---|---|---|---|---|---|
| P1 | Yes | Yes | Yes | No | Poor (3/4 issues) |
| P2 | No | No | No | No | **Good** |
| P3 | No | No | No | No | **Good** |
| P4 | No | No | Yes | No | Moderate (1/4 issue) |
| P5 | Yes | Yes | No | No | Moderate (2/4 issues) |

### 8.13 EQ-5D Quality of Life (Baseline → 12th Month)
| Patient | Mobility | Self-Care | Usual Activity | Pain | Anxiety | Mental Health | VAS |
|---|---|---|---|---|---|---|---|
| **P1 BL** | No prob. | No prob. | No prob. | No pain | Not anxious | 2 | 55 |
| **P1 12M** | No prob. | No prob. | No prob. | No pain | Not anxious | 2 | 70 ↑ |
| **P2 BL** | No prob. | No prob. | No prob. | No pain | Not anxious | 7 | 70 |
| **P2 12M** | No prob. | No prob. | No prob. | No pain | Not anxious | 0 | 80 ↑ |
| **P3 BL** | No prob. | Slight | Slight | Slight | Slight | 2 | 80 |
| **P3 12M** | No prob. | No prob. | No prob. | No pain | Not anxious | 0 | 60 ↓ |
| **P4 BL** | No prob. | No prob. | No prob. | Slight | Slight | 6 | 80 |
| **P4 12M** | No prob. | No prob. | No prob. | No pain | Not anxious | 0 | 70 ↓ |
| **P5 BL** | Moderate | Slight | Slight | Slight | Slight | 10 | 65 |
| **P5 12M** | Slight | Slight | Slight | Slight | Not anxious | 5 | 85 ↑ |

> EQ-5D and mental health questionnaires were collected **only at Baseline and 12th month** — no data exists for intermediate visits.

### 8.14 GAD-7 Scores (Baseline → 12th Month)
Scoring: Not at all=0, Several days=1, More than half the days=2, Nearly every day=3

| Patient | BL Score | 12M Score | Change |
|---|---|---|---|
| P1 | 4 (Several days on 4/7 items) | 0 | **−4** |
| P2 | 2 (Several days on 2/7 items) | 1 | **−1** |
| P3 | 0 | 1 | +1 |
| P4 | 0 | 0 | 0 |
| P5 | 3 (Several days on 3/7 items) | 0 | **−3** |

### 8.15 PHQ-9 Scores (Baseline → 12th Month)
| Patient | BL Score | 12M Score | Notable items at Baseline |
|---|---|---|---|
| P1 | 4 | 0 | Feeling down (>half days), trouble sleeping, speak slowly (several days) |
| P2 | 0 | 0 | — |
| P3 | 0 | 0 | — |
| P4 | 1 | 2 | Little energy (several days at BL; >half days at 12M) |
| P5 | 2 | 1 | Trouble sleeping, little energy (several days at BL) |

---

## 9. Data Collection Rules

| Variable Group | Baseline | 3rd Month | 6th Month | 9th Month | 12th Month |
|---|---|---|---|---|---|
| Anthropometrics (weight, BMI, waist) | ✓ | ✓ | ✓ | ✓ | ✓ |
| Blood pressure | ✓ | ✓ | ✓ | ✓ | ✓ |
| HbA1c | ✓ | ✓ | ✓ | ✓ | ✓ |
| Lipid panel, eGFR, HOMA-IR | ✓ | — | — | — | ✓ |
| EQ-5D, GAD-7, PHQ-9 | ✓ | — | — | — | ✓ |
| Diet, smoking, alcohol, PA | ✓ | ✓ (partial) | ✓ (partial) | ✓ (partial) | ✓ |
| Medication details | ✓ | ✓ | ✓ | ✓ | ✓ |
| Demographics (age, gender, etc.) | ✓ | Carried forward | Carried forward | Carried forward | Carried forward |

---

## 10. Data Processing in visualize_sample.py

All processing is in `/Users/samridhisaini/Tanuh/CKM_data_analysis/visualize_sample.py`.

### 10.1 Derived Scores

**GAD-7 score** (`gad7` column, added to df):
- Maps: Not at all=0, Several days=1, More than half the days=2, Nearly every day=3
- Sums all 7 items → range 0–21

**PHQ-9 score** (`phq9` column, added to df):
- Same mapping × 9 items → range 0–27

**EQ-5D sum** (`eq5d_sum` column, added to df):
- Mobility/Self-care/Usual activity: No problems=1 … Extreme=5
- Pain: No pain=1 … Extreme pain=5
- Anxiety: Not anxious=1 … Extreme=5
- Sum of all 5 domains → range 5–25

### 10.2 Pivot Helper

```python
def pivot(col):
    pt = df.pivot_table(index='pid', columns='followup', values=col, aggfunc='first')
    return pt.reindex(columns=[v for v in VISIT_ORDER if v in pt.columns])
```
Returns a wide-format table: rows = patients, columns = visits in chronological order.

### 10.3 Key Constants

```python
VISIT_ORDER = ['Baseline', '3rd month', '6th month', '9th month', '12th month']
PIDS        = ['1-3-3', '2-7-11', '3-10-13', '4-14-17', '4-16-11']
PID_LABEL   = {'1-3-3':'P1', '2-7-11':'P2', '3-10-13':'P3', '4-14-17':'P4', '4-16-11':'P5'}
ARM_COLOR   = {'Low carbohydrate diet': '#2196F3', 'Usual diet': '#FF5722'}
VISIT_COLORS= {'Baseline':'#78909C', '3rd month':'#42A5F5', '6th month':'#AB47BC',
               '9th month':'#FFA726', '12th month':'#43A047'}
```

### 10.4 Helper Functions

| Function | Purpose |
|---|---|
| `pid_arm(pid)` | Returns the arm string for a patient |
| `arm_color(pid)` | Returns hex colour for blue (LCD) or orange (Usual) arm |
| `line_trend(ax, pt, ylabel, title)` | Plots multi-line time series with value annotations and end-of-line patient labels (P1–P5 in boxed callouts) |
| `bar_compare(ax, bl_dict, end_dict, ylabel, title)` | Two-bar grouped chart (Baseline vs 12th month) with patient arm labels |
| `bar_all_visits(ax, col, ylabel, title)` | Five-bar grouped chart (all visits) per patient, colour-coded by visit |
| `eq_score(val, col)` | Converts EQ-5D text response to integer score (1–5) |
| `score_gad(row)` | Computes GAD-7 total score for a row |
| `score_phq(row)` | Computes PHQ-9 total score for a row |

---

## 11. Generated Plots

All plots saved to `plots/` at 150 DPI.

| File | Title | What it shows |
|---|---|---|
| `fig1_demographics.png` | Patient Demographics at Baseline | Table of all baseline characteristics for P1–P5 |
| `fig2_clinical_trends.png` | Clinical Outcome Trends Across Follow-Up Visits | 4-panel line chart: HbA1c, Weight, Systolic BP, Diastolic BP over 5 visits. Each line labelled with P1–P5 at right end. |
| `fig3_metabolic_all_visits.png` | Metabolic Markers Across All Visits | 6-panel grouped bar chart: Total Cholesterol, Triglycerides, LDL, HDL, eGFR, HOMA-IR. One group per patient (P1–P5), one bar per visit. Bars present only where data exists (Baseline and 12th month for these markers). |
| `fig4_attendance.png` | Follow-up Attendance | Green/Red heatmap: rows = patients, columns = follow-up visits. Shows who attended/missed each visit. |
| `fig5_drug_count_heatmap.png` | Number of Oral Antidiabetic Drugs per Visit | Heatmap: rows = patients, columns = visits. Cell value = drug count. |
| `fig6_mental_health.png` | Mental Health Scores: Baseline vs 12th Month | 3-panel bar: GAD-7, PHQ-9, EQ-5D VAS (health_range). |
| `fig7_diet_baseline.png` | Dietary Intake Frequency at Baseline | Grouped bar chart: 8 food groups × 5 patients, values in days/week (0–7). |
| `fig8_activity_sleep.png` | Physical Activity & Sleep Across Visits | 2-panel line chart: Walking days/week and Sleep hours/night over 5 visits. |
| `fig9_eq5d_all_visits.png` | EQ-5D Domains Across All Visits | 5-panel heatmap (one per visit). Baseline and 12th month show coloured severity grids (rows=patients, cols=5 EQ-5D domains). 3rd/6th/9th month panels show "Not collected at this visit" in grey. |
| `fig10_bmi_waist.png` | BMI and Waist Circumference Over Time | 2-panel line chart: BMI (with WHO Asia-Pacific reference lines at 18.5, 23.0, 25.0) and Waist circumference. Patient labels (P1–P5) at end of each line. |
| `fig11_arm_comparison_change.png` | Arm Comparison: Change from Baseline to 12th Month | 2-panel bar chart: ΔHbA1c and ΔWeight per patient, colour-coded by arm. Bars above zero = increase; below zero = decrease. |

---

## 12. Key Observations from the Data

> These are observations from the data only — no statistical inferences due to small sample size (n=5).

1. **HbA1c:** P3 (Usual diet) showed the largest improvement (−4.9%). P2 (Low-Carb) worsened the most (+2.7%), but had 2 missed visits. Trends vary substantially within both arms.

2. **Triglycerides:** P2 had severely elevated baseline triglycerides (797.7 mg/dL) — a clinically critical finding — which reduced to 191 mg/dL at 12 months.

3. **HOMA-IR:** All patients improved (reduced) HOMA-IR from baseline to 12th month, suggesting reduced insulin resistance across both arms.

4. **eGFR:** All patients had eGFR >90 (normal kidney function) throughout; no deterioration observed.

5. **Oral Antidiabetics:** All patients started on 2 drugs. By 12th month, most had 0 drugs recorded — possibly reflecting that drugs were not captured at final visit or actual de-prescribing.

6. **Soft drinks:** All 5 patients consumed soft drinks 7 days/week at baseline — a uniform high-risk dietary behaviour.

7. **Attendance:** P1, P4, P5 had perfect attendance (0 missed visits). P2 missed 2 visits (3rd and 9th month). P3 missed 1 visit (3rd month).

8. **Mental health:** GAD-7 and PHQ-9 scores were low at baseline and generally improved or stayed low at 12 months. P5 had the highest baseline QoL problems (Moderate mobility issues, EQ-5D domains with Slight problems across all 5 dimensions).

9. **Medication adherence:** P1 had the worst adherence profile (3/4 Morisky items positive). P2 and P3 had perfect adherence at baseline.

10. **P2 HDL anomaly:** P5 had an unusually high baseline HDL of 153.7 mg/dL, which normalised to 69.7 by 12 months. This extreme baseline value may warrant verification.

---

## 13. File & Folder Structure

```
CKM_data_analysis/
├── sample_to_iisc.csv          # Main dataset (25 rows × 157 cols)
├── LCD Followup ODK Codes.xlsx # ODK codebook for follow-up form
├── LCD Baseline form ODK Codes.xlsx  # ODK codebook for baseline form
├── visualize_sample.py         # Full visualization script (run this to regenerate plots)
├── analysis.py                 # (Opened in IDE — earlier analysis work)
├── CONTEXT.md                  # This file
├── venv/                       # Python virtual environment
└── plots/
    ├── fig1_demographics.png
    ├── fig2_clinical_trends.png
    ├── fig3_metabolic_all_visits.png
    ├── fig4_attendance.png
    ├── fig5_drug_count_heatmap.png
    ├── fig6_mental_health.png
    ├── fig7_diet_baseline.png
    ├── fig8_activity_sleep.png
    ├── fig9_eq5d_all_visits.png
    ├── fig10_bmi_waist.png
    └── fig11_arm_comparison_change.png
```

---

## 14. How to Regenerate All Plots

```bash
cd /Users/samridhisaini/Tanuh/CKM_data_analysis
source venv/bin/activate
python3 visualize_sample.py
```

All 11 figures are saved to `plots/` and overwrite any existing files.

---

*End of context document*
