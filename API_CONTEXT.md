# CKM Dietician API — Complete Context

> **Last updated:** 2026-06-23  
> **Working directory:** `/Users/samridhisaini/Tanuh/CKM_data_analysis/`  
> **Python environment:** `venv/` (always activate before running anything)

---

## What This Is

A REST API built with **FastAPI** that:
1. Stores the CKM/LCD patient dataset in a local **SQLite database** (`ckm.db`)
2. Exposes clean JSON endpoints to fetch patient data by ID, visit, or trend
3. Calls the **Claude LLM (claude-sonnet-4-6)** to act as a personal dietician — taking a patient's full clinical + dietary data and returning structured, culturally appropriate diet advice

The pipeline flow is:

```
CSV file
   ↓  (seed.py — one-time)
SQLite DB (ckm.db)
   ↓  (FastAPI routes)
REST Endpoints  ──→  GET patient data (JSON)
                ──→  POST diet advice
                           ↓
                      Claude API
                           ↓
                    Structured JSON advice
                    (priority changes, food list,
                     arm-specific guidance, targets)
```

---

## File Structure

```
CKM_data_analysis/
├── ckm_api/
│   ├── __init__.py
│   ├── main.py          ← FastAPI app, includes all routes
│   ├── database.py      ← SQLAlchemy engine + session setup (SQLite)
│   ├── models.py        ← ORM table definitions (Patient, Visit)
│   ├── schemas.py       ← Pydantic response shapes
│   ├── crud.py          ← DB query functions + patient JSON builder
│   ├── seed.py          ← Loads CSV → SQLite (run once)
│   ├── routes/
│   │   ├── patients.py  ← All patient data endpoints
│   │   └── diet.py      ← Diet advice endpoint (calls LLM)
│   └── llm/
│       ├── dietician.py ← Anthropic API call + JSON parsing
│       └── prompts.py   ← System prompt + user message builder
├── ckm.db               ← SQLite database (auto-created by seed.py)
├── .env                 ← ANTHROPIC_API_KEY goes here
├── sample_to_iisc.csv   ← Source data
└── API_CONTEXT.md       ← This file
```

---

## Database Schema

### Table: `patients` (5 rows — one per patient)

| Column | Type | Description |
|---|---|---|
| `pid` | TEXT (PK) | Patient ID e.g. "1-3-3" |
| `zone` | TEXT | Chennai zone name |
| `uphc` | TEXT | UPHC facility name |
| `arm` | TEXT | "Low carbohydrate diet" or "Usual diet" |
| `age` | INT | Age at baseline |
| `gender` | TEXT | Male / Female |
| `marital_status` | TEXT | Married / Widowed |
| `education_years` | INT | Years of formal education |
| `occupation` | TEXT | Self-employed / Professional / etc. |
| `income_monthly` | INT | Monthly household income (₹) |
| `family_members` | INT | Number of family members |
| `height_cm` | REAL | Height in cm |
| `diabetes_duration_yr` | INT | Years since DM diagnosis |
| `hypertension` | TEXT | Yes / No |
| `heart_attack` | TEXT | Yes / No |
| `stroke` | TEXT | Yes / No |
| `neuropathy` | TEXT | Yes / No |
| `retinopathy` | TEXT | Yes / No |
| `ckd` | TEXT | Yes / No |
| `med_adherence` | TEXT | Regular / Missed few |
| `drug_source` | TEXT | PHC / Private clinic |
| `baseline_fruit_days` | INT | Days/week eating fruit at baseline |
| `baseline_veg_days` | INT | Days/week eating vegetables at baseline |

### Table: `visits` (25 rows — 5 patients × 5 visits)

**Key columns:**

| Column | Type | Collected When |
|---|---|---|
| `pid` | TEXT | All visits |
| `visit_label` | TEXT | All visits (Baseline / 3rd month / …) |
| `visit_date` | TEXT | All visits |
| `attended` | TEXT | Follow-up visits only (Yes/No) |
| `weight_kg`, `bmi`, `waist_cm` | REAL | All visits |
| `sys_bp`, `dia_bp` | REAL | All visits |
| `hb_a1c` | REAL | All visits |
| `total_cholesterol`, `triglycerides`, `ldl`, `hdl`, `vldl` | REAL | Baseline + 12th month only |
| `egfr`, `homa_ir`, `serum_creatinine` | REAL | Baseline + 12th month only |
| `n_oral_antidiabetics` | INT | All visits |
| `drug_1`, `dose_1`, `drug_2`, `dose_2` | TEXT/REAL | All visits |
| `diet_soft_drinks`, `diet_junk_foods`, `diet_vegetables`, `diet_fruits`, `diet_eggs_protein`, `diet_moringa`, `diet_nuts_seeds`, `diet_extra_meals` | REAL | All visits (days/week 0–7) |
| `eq5d_mobility`, `eq5d_pain`, `eq5d_anxiety`, `eq5d_health_vas` | TEXT/REAL | Baseline + 12th month only |
| `gad7_score` | INT | Baseline + 12th month only (0–21) |
| `phq9_score` | INT | Baseline + 12th month only (0–27) |

---

## API Endpoints

Base URL when running locally: `http://127.0.0.1:8000`  
Interactive docs: `http://127.0.0.1:8000/docs`

### Patient Endpoints

| Method | Path | What it returns |
|---|---|---|
| GET | `/api/patients/` | List of all patients (pid, arm, age, gender, uphc) |
| GET | `/api/patients/{pid}` | Full patient record — demographics + all 5 visits as nested JSON |
| GET | `/api/patients/{pid}/latest` | Latest attended visit: HbA1c, weight, BMI, BP, drug count, diet snapshot |
| GET | `/api/patients/{pid}/summary` | Complete structured JSON (used as LLM input) |
| GET | `/api/patients/{pid}/trends` | HbA1c, weight, BMI, BP, waist across all attended visits |

### Diet Advice Endpoint

| Method | Path | What it does |
|---|---|---|
| POST | `/api/diet/{pid}/advice` | Fetches patient data → sends to Claude → returns structured diet advice JSON |

**Diet advice response shape:**
```json
{
  "pid": "3-10-13",
  "patient_label": "P-3-10-13",
  "arm": "Usual diet",
  "age": 51,
  "gender": "Female",
  "clinical_snapshot": {
    "latest_hba1c": 6.3,
    "baseline_hba1c": 11.2,
    "latest_bmi": 35.66,
    "hypertension": "Yes",
    "diabetes_duration": 1
  },
  "diet_advice": {
    "current_diet_assessment": "...",
    "priority_changes": ["...", "...", "..."],
    "recommended_foods": ["...", "..."],
    "foods_to_reduce": ["...", "..."],
    "meal_pattern_advice": "...",
    "arm_specific_guidance": "...",
    "targets_next_visit": "...",
    "important_note": "..."
  }
}
```

---

## Setup & Running

### Step 1 — Set your API key
Edit `.env`:
```
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxx
```

### Step 2 — Seed the database (run once, or after CSV changes)
```bash
cd /Users/samridhisaini/Tanuh/CKM_data_analysis
source venv/bin/activate
python -m ckm_api.seed
# Output: Seeded 5 patients and 25 visits into ckm.db
```

### Step 3 — Start the API server
```bash
source venv/bin/activate
uvicorn ckm_api.main:app --reload --host 127.0.0.1 --port 8000
```

### Step 4 — Call the endpoints

**Get all patients:**
```bash
curl http://127.0.0.1:8000/api/patients/
```

**Get full record for patient 1-3-3:**
```bash
curl http://127.0.0.1:8000/api/patients/1-3-3
```

**Get latest visit snapshot:**
```bash
curl http://127.0.0.1:8000/api/patients/3-10-13/latest
```

**Get HbA1c/weight/BP trends:**
```bash
curl http://127.0.0.1:8000/api/patients/4-14-17/trends
```

**Get LLM diet advice (requires ANTHROPIC_API_KEY in .env):**
```bash
curl -X POST http://127.0.0.1:8000/api/diet/4-16-11/advice
```

---

## How the LLM Dietician Works

### What gets sent to Claude

The `build_patient_json()` function in `crud.py` assembles a JSON object with:
- Patient demographics (age, gender, income, occupation, education)
- Comorbidities (HTN, heart attack, neuropathy, retinopathy)
- HbA1c trend across all visits
- Latest clinical data (BMI, BP, lipids, eGFR, HOMA-IR where available)
- Baseline clinical data for comparison
- Diet frequency (days/week) for 8 food categories
- Lifestyle data (smoking, alcohol, physical activity, sleep)
- Intervention arm (Low-Carb vs Usual diet)

This is then trimmed to the most relevant fields in `build_user_message()` in `prompts.py`.

### System Prompt Design

Claude is instructed to:
1. Be a clinical dietician for Tamil Nadu / urban Chennai patients
2. Give culturally appropriate advice (idli, dosa, ragi, millets — not generic Western food)
3. Tailor advice to the patient's income and occupation (a ₹1,000/month homemaker needs different advice than a ₹90,000/month professional)
4. Differentiate Low-Carb arm vs Usual diet arm recommendations
5. Return **only valid JSON** in a fixed schema

### LLM Response Parsing

The `dietician.py` module:
1. Calls `claude-sonnet-4-6` with a max of 1500 tokens
2. Strips markdown code fences if the model wraps in ` ```json ` blocks
3. Parses the JSON and returns a Python dict
4. Raises clear errors if the API key is missing or the JSON is invalid

---

## Installed Dependencies

Added to `venv/`:
- `fastapi` — web framework
- `uvicorn[standard]` — ASGI server
- `sqlalchemy` — ORM for SQLite
- `pydantic` — data validation and response schemas
- `anthropic` — Claude API SDK
- `python-dotenv` — loads `.env` file

---

## Extending This for 300 Patients

When the full 300-patient dataset is available:

1. **Replace the CSV:** drop the new `sample_to_iisc.csv` (or a new file) into the project root
2. **Re-seed:** `python -m ckm_api.seed` — this drops and rebuilds `ckm.db`
3. **No code changes needed** — all queries are parameterised by `pid`

For a production deployment with 300+ patients, consider:
- Switching `DATABASE_URL` in `database.py` from SQLite to **PostgreSQL**
- Adding a `POST /api/patients/` endpoint to insert new patients programmatically (instead of only via CSV seed)
- Adding authentication (API keys or JWT) to protect patient data
- Rate-limiting the `/api/diet/{pid}/advice` endpoint (each call costs Claude API tokens)

---

## Patient ID Reference

| PID | Label | Arm | UPHC |
|---|---|---|---|
| `1-3-3` | P1 | Low carbohydrate diet | R.K. Nagar UPHC |
| `2-7-11` | P2 | Low carbohydrate diet | Thanthai Periyar UPHC |
| `3-10-13` | P3 | Usual diet | Maduravoyal UHPC |
| `4-14-17` | P4 | Usual diet | SRKV UPHC |
| `4-16-11` | P5 | Usual diet | Voluntary Health Services UPHC |

---

*End of API context document*
