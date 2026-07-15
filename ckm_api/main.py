from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from ckm_api.database import engine, Base
from ckm_api.routes import patients, diet

load_dotenv()  # reads ANTHROPIC_API_KEY from .env

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="CKM Dietician API",
    description=(
        "REST API for the CKM / LCD study dataset. "
        "Stores patient and visit data in SQLite and provides "
        "an LLM-powered personal dietician endpoint via Claude."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(patients.router, prefix="/api/patients", tags=["Patients"])
app.include_router(diet.router,     prefix="/api/diet",     tags=["Diet Advice"])


@app.get("/", tags=["Health"])
def root():
    return {
        "status": "running",
        "docs":   "/docs",
        "endpoints": {
            "list_patients":  "GET  /api/patients/",
            "patient_record": "GET  /api/patients/{pid}",
            "latest_visit":   "GET  /api/patients/{pid}/latest",
            "patient_summary":"GET  /api/patients/{pid}/summary",
            "trends":         "GET  /api/patients/{pid}/trends",
            "diet_advice":    "POST /api/diet/{pid}/advice",
        },
    }
