# CKM / LCD Follow-Up — Data Analysis & Dietician API

Clinical data analysis and AI-powered dietary recommendation platform for the **CKM (Cardiovascular-Kidney-Metabolic) / LCD (Lifestyle Change for Diabetes) Follow-Up Programme** — a longitudinal study of Type 2 Diabetes patients across Urban Primary Health Centres (UPHCs) in Chennai, Tamil Nadu.

---

## What This Does

| Layer | What it is |
|---|---|
| **Data visualisation** | 11 matplotlib plots of patient clinical + dietary trends across 5 visits |
| **REST API** | FastAPI service exposing patient data as clean JSON endpoints |
| **AI Dietician** | Google Gemini generates structured, personalised meal advice per patient |
| **Dashboard** | Streamlit app for reviewing recommendations and submitting nutritionist feedback |

---

## Project Structure

```
CKM_data_analysis/
├── ckm_api/
│   ├── main.py            ← FastAPI app entry point
│   ├── database.py        ← SQLAlchemy engine (SQLite)
│   ├── models.py          ← ORM tables: Patient, Visit, Recommendation, Feedback
│   ├── schemas.py         ← Pydantic response models
│   ├── crud.py            ← All DB query and write functions
│   ├── seed.py            ← Loads CSV → SQLite (run once)
│   ├── routes/
│   │   ├── patients.py    ← Patient data endpoints
│   │   └── diet.py        ← Diet advice endpoint (calls Gemini)
│   └── llm/
│       ├── dietician.py   ← Gemini API call + JSON parsing
│       └── prompts.py     ← System prompt + patient message builder
├── streamlit_app.py       ← Interactive dashboard
├── visualize_sample.py    ← Generates all 11 clinical plots
├── sample_to_iisc.csv     ← Source dataset
├── ckm.db                 ← SQLite database (auto-created)
├── .env                   ← API keys (not committed)
├── requirements.txt
└── plots/                 ← Generated figures
```

---

## Setup

### 1. Clone and create a virtual environment

```bash
git clone <repo-url>
cd CKM_data_analysis
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Set your API key

Create a `.env` file in the project root:

```
GEMINI_API_KEY=your-google-gemini-api-key-here

# Optional — Vertex AI backend (requires GCP credentials)
# USE_VERTEX_AI=false
# VERTEX_PROJECT_ID=your-gcp-project-id
# VERTEX_LOCATION=us-central1
```

Get a free Gemini API key at [aistudio.google.com](https://aistudio.google.com).

### 3. Seed the database

```bash
python -m ckm_api.seed
# Output: Seeded 5 patients and 25 visits into ckm.db
```

---

## Running

### API Server

```bash
uvicorn ckm_api.main:app --reload --host 127.0.0.1 --port 8000
```

Interactive API docs: `http://127.0.0.1:8000/docs`

### Streamlit Dashboard

```bash
streamlit run streamlit_app.py
```

Opens at: `http://localhost:8501`

### Data Visualisation

```bash
python visualize_sample.py
# Saves 11 plots to plots/
```

---

## API Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/patients/` | List all patients |
| `GET` | `/api/patients/{pid}` | Full record — demographics + all 5 visits |
| `GET` | `/api/patients/{pid}/latest` | Latest attended visit snapshot |
| `GET` | `/api/patients/{pid}/summary` | Structured summary used by LLM |
| `GET` | `/api/patients/{pid}/trends` | HbA1c, weight, BMI, BP trends |
| `POST` | `/api/diet/{pid}/advice` | Generate AI diet advice and store in DB |

**Model selection** (pass as query param):

```bash
curl -X POST "http://127.0.0.1:8000/api/diet/1-3-3/advice?model=gemini-2.5-pro"
```

Supported models: `gemini-2.5-flash` (default), `gemini-2.5-pro`, `gemini-1.5-flash`, `gemini-1.5-pro`

---

## Database Schema

SQLite file: `ckm.db`

| Table | Rows | Description |
|---|---|---|
| `patients` | 1 per patient | Baseline demographics and comorbidities |
| `visits` | 1 per patient × visit | Clinical, dietary, and QoL data across 5 visits |
| `recommendations` | 1 per API call | Stored AI advice: assessment, meals, flags |
| `feedback` | 1 per rated field | Nutritionist ratings (good/bad) per advice field |

---

## Dashboard Features

**📊 Clinical Overview tab**
- Key metrics: HbA1c, BMI, BP, waist circumference
- Comorbidities and demographics panel
- HbA1c and BMI trend charts
- Full visit-by-visit data table

**🥗 Diet Recommendations tab**
- Select AI model and click **Generate New Advice**
- Confirmation banner with storage location (`ckm.db → recommendations → row ID`)
- Edit any advice field inline and save back to the database
- Rate each meal (Breakfast / Lunch / Dinner), foods to avoid, and clinical note as **Good / Bad**
- Feedback stored in `feedback` table linked to the recommendation

**📋 Feedback Log tab**
- All submitted ratings across all patients
- Filterable by patient, field, and rating
- Approval rate summary

---

## Dataset

- **Source:** CKM/LCD Follow-Up Programme, Chennai UPHCs
- **Patients:** 5 (sample) — full dataset ~300
- **Visits:** 5 per patient (Baseline, 3rd, 6th, 9th, 12th month)
- **Intervention arms:** Low Carbohydrate Diet vs Usual Diet
- **Key variables:** HbA1c, BMI, BP, lipid panel, eGFR, HOMA-IR, EQ-5D, GAD-7, PHQ-9, 8-item diet frequency

---

## Extending to 300 Patients

1. Replace `sample_to_iisc.csv` with the full dataset
2. Re-run `python -m ckm_api.seed` — drops and rebuilds `ckm.db`
3. No code changes needed

For production with 300+ patients, consider switching `DATABASE_URL` in `database.py` from SQLite to PostgreSQL or MySQL.

