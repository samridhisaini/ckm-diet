import streamlit as st
import pandas as pd
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

from ckm_api.database import SessionLocal, engine, Base
from ckm_api import crud, models
from ckm_api.llm.dietician import get_diet_advice, AVAILABLE_MODELS, DEFAULT_MODEL

Base.metadata.create_all(bind=engine)

DB_PATH = os.path.abspath("ckm.db")

# ─── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CKM Dietician Dashboard",
    layout="wide",
    page_icon="🩺",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    .meal-card {
        background: white;
        border: 1px solid #E0E0E0;
        border-radius: 10px;
        padding: 16px;
        min-height: 110px;
        margin-bottom: 8px;
    }
    .meal-card h4 { margin: 0 0 8px 0; font-size: 14px; color: #555; }
    .meal-card p  { margin: 0; font-size: 15px; color: #1a1a1a; }
    .rec-meta {
        background: #F8F9FA;
        border-radius: 8px;
        padding: 10px 16px;
        margin-bottom: 12px;
        font-size: 13px;
        color: #444;
    }
    .stored-info {
        background: #E8F5E9;
        border-left: 4px solid #43A047;
        border-radius: 6px;
        padding: 10px 16px;
        margin-bottom: 16px;
        font-size: 13px;
        color: #2E7D32;
        font-family: monospace;
    }
    .arm-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 13px;
        font-weight: 600;
        margin-bottom: 12px;
    }
</style>
""", unsafe_allow_html=True)

VISIT_ORDER  = ["Baseline", "3rd month", "6th month", "9th month", "12th month"]
MODEL_LABELS = {
    "gemini-2.5-flash": "Gemini 2.5 Flash",
    "gemini-2.5-pro":   "Gemini 2.5 Pro",
    "gemini-1.5-flash": "Gemini 1.5 Flash",
    "gemini-1.5-pro":   "Gemini 1.5 Pro",
}

# ─── DB helpers ────────────────────────────────────────────────────────────────
def db_session():
    return SessionLocal()

@st.cache_data(ttl=30)
def load_patients():
    db = db_session()
    try:
        return [(p.pid, p.arm, p.age, p.gender, p.uphc) for p in db.query(models.Patient).all()]
    finally:
        db.close()

def load_patient_data(pid):
    db = db_session()
    try:
        return crud.get_patient_with_visits(db, pid)
    finally:
        db.close()

def load_recommendations(pid):
    db = db_session()
    try:
        recs = crud.get_recommendations(db, pid)
        return [
            (r.id, r.model_used, r.generated_at, r.assessment,
             r.priority_changes, r.breakfast, r.lunch, r.dinner,
             r.foods_to_avoid, r.clinical_note)
            for r in recs
        ]
    finally:
        db.close()

def load_feedback_for_rec(rec_id):
    db = db_session()
    try:
        fbs = crud.get_feedback_for_recommendation(db, rec_id)
        return {fb.field_name: (fb.rating, fb.notes) for fb in fbs}
    finally:
        db.close()

def load_all_feedback_rows():
    db = db_session()
    try:
        fbs = crud.get_all_feedback(db)
        return [(fb.submitted_at, fb.pid, fb.recommendation_id,
                 fb.field_name, fb.rating, fb.notes) for fb in fbs]
    finally:
        db.close()

def do_save_feedback(rec_id, pid, items):
    db = db_session()
    try:
        crud.save_feedback_batch(db, rec_id, pid, items, "")
    finally:
        db.close()

def do_update_recommendation(rec_id, fields):
    db = db_session()
    try:
        crud.update_recommendation(db, rec_id, fields)
    finally:
        db.close()

# ─── Sidebar ───────────────────────────────────────────────────────────────────
st.sidebar.title("🩺 CKM Dietician")
st.sidebar.markdown("---")

patients_raw = load_patients()
if not patients_raw:
    st.error("No patients found. Run `python -m ckm_api.seed` first.")
    st.stop()

pid_map = {f"P{i+1} — {pid}": pid for i, (pid, *_) in enumerate(patients_raw)}
selected_label = st.sidebar.selectbox("Patient", list(pid_map.keys()))
selected_pid   = pid_map[selected_label]

model_labels_inv  = {v: k for k, v in MODEL_LABELS.items()}
selected_model_label = st.sidebar.selectbox("AI Model", list(MODEL_LABELS.values()))
selected_model       = model_labels_inv[selected_model_label]

st.sidebar.markdown("---")
st.sidebar.caption("**Vertex AI:** Set `USE_VERTEX_AI=true` + `VERTEX_PROJECT_ID` in `.env` to route via Google Cloud.")
st.sidebar.markdown("---")
generate_btn = st.sidebar.button("🔄 Generate New Advice", use_container_width=True, type="primary")

# ─── Load patient ──────────────────────────────────────────────────────────────
patient, visits = load_patient_data(selected_pid)
if not patient:
    st.error(f"Patient {selected_pid} not found.")
    st.stop()

visits = sorted(visits, key=lambda v: VISIT_ORDER.index(v.visit_label)
                if v.visit_label in VISIT_ORDER else 99)
attended   = [v for v in visits if v.attended != "No"]
latest_v   = attended[-1] if attended else visits[-1]

hba1c_series = [(v.visit_label, v.hb_a1c) for v in visits if v.hb_a1c is not None]
hba1c_delta  = (hba1c_series[-1][1] - hba1c_series[0][1]) if len(hba1c_series) >= 2 else None

# ─── Header ────────────────────────────────────────────────────────────────────
arm_color = "#1565C0" if "carbohydrate" in (patient.arm or "").lower() else "#E65100"
st.title(f"Patient {selected_pid}")
st.markdown(
    f'<span class="arm-badge" style="background:{arm_color}20; color:{arm_color}; '
    f'border:1px solid {arm_color}50">{patient.arm}</span>'
    f' &nbsp; Age {patient.age} &nbsp;|&nbsp; {patient.gender}'
    f' &nbsp;|&nbsp; {patient.uphc} &nbsp;|&nbsp; DM {patient.diabetes_duration_yr} yr',
    unsafe_allow_html=True,
)

# ─── Generate advice ───────────────────────────────────────────────────────────
if generate_btn:
    with st.spinner(f"Calling {selected_model_label}…"):
        try:
            patient_json = crud.build_patient_json(patient, visits)
            advice = get_diet_advice(patient_json, model=selected_model)
            db = db_session()
            rec = crud.save_recommendation(db, selected_pid, selected_model, advice)
            db.close()
            st.session_state["current_rec_id"]  = rec.id
            st.session_state["last_saved_rec"]  = {
                "id":    rec.id,
                "model": selected_model,
                "ts":    rec.generated_at,
            }
            st.cache_data.clear()
        except Exception as e:
            st.error(f"Error: {e}")

# ─── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["📊 Clinical Overview", "🥗 Diet Recommendations", "📋 Feedback Log"])

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1 — Clinical Overview
# ═══════════════════════════════════════════════════════════════════════════════
with tab1:
    m1, m2, m3, m4, m5 = st.columns(5)
    with m1:
        st.metric("HbA1c (latest)",
                  f"{latest_v.hb_a1c}%" if latest_v.hb_a1c else "—",
                  delta=f"{hba1c_delta:+.1f}%" if hba1c_delta is not None else None,
                  delta_color="inverse")
    with m2:
        st.metric("BMI", f"{latest_v.bmi:.1f}" if latest_v.bmi else "—",
                  latest_v.bmi_category or "")
    with m3:
        bp = (f"{int(latest_v.sys_bp)}/{int(latest_v.dia_bp)}"
              if latest_v.sys_bp and latest_v.dia_bp else "—")
        st.metric("BP (mmHg)", bp)
    with m4:
        st.metric("Waist", f"{latest_v.waist_cm} cm" if latest_v.waist_cm else "—")
    with m5:
        oad = str(latest_v.n_oral_antidiabetics) if latest_v.n_oral_antidiabetics is not None else "—"
        st.metric("Oral Antidiabetics", oad)

    st.markdown("---")
    left, right = st.columns(2)

    with left:
        st.subheader("Comorbidities")
        for label, val in [
            ("Hypertension", patient.hypertension),
            ("Heart Attack",  patient.heart_attack),
            ("Stroke",        patient.stroke),
            ("Neuropathy",    patient.neuropathy),
            ("Retinopathy",   patient.retinopathy),
            ("CKD",           patient.ckd),
        ]:
            icon = "🔴" if val == "Yes" else "🟢" if val == "No" else "⚪"
            st.write(f"{icon} **{label}:** {val or '—'}")

        st.markdown("---")
        st.subheader("Demographics")
        st.write(f"**Occupation:** {patient.occupation or '—'}")
        st.write(f"**Education:** {patient.education_years} yr" if patient.education_years else "**Education:** —")
        st.write(f"**Monthly income:** ₹{patient.income_monthly:,}" if patient.income_monthly else "**Monthly income:** —")
        st.write(f"**Family members:** {patient.family_members or '—'}")
        st.write(f"**Medication adherence:** {patient.med_adherence or '—'}")

    with right:
        st.subheader("HbA1c Trend")
        if hba1c_series:
            df_hba1c = pd.DataFrame(hba1c_series, columns=["Visit", "HbA1c (%)"]).set_index("Visit")
            st.line_chart(df_hba1c, color="#E53935")
        else:
            st.info("No HbA1c data available.")

        st.subheader("BMI Trend")
        weight_series = [(v.visit_label, v.bmi) for v in visits if v.bmi]
        if weight_series:
            df_w = pd.DataFrame(weight_series, columns=["Visit", "BMI"]).set_index("Visit")
            st.line_chart(df_w, color="#1E88E5")
        else:
            st.info("No BMI data.")

    st.markdown("---")
    st.subheader("Visit-by-Visit Summary")
    rows = []
    for v in visits:
        rows.append({
            "Visit":          v.visit_label,
            "Date":           v.visit_date or "—",
            "Attended":       v.attended or "—",
            "Weight (kg)":    v.weight_kg or "—",
            "BMI":            f"{v.bmi:.1f}" if v.bmi else "—",
            "HbA1c (%)":      v.hb_a1c or "—",
            "BP":             f"{int(v.sys_bp)}/{int(v.dia_bp)}" if v.sys_bp and v.dia_bp else "—",
            "Soft drinks/wk": v.diet_soft_drinks if v.diet_soft_drinks is not None else "—",
            "Junk food/wk":   v.diet_junk_foods  if v.diet_junk_foods  is not None else "—",
            "Fruits/wk":      v.diet_fruits       if v.diet_fruits       is not None else "—",
            "Vegetables/wk":  v.diet_vegetables   if v.diet_vegetables   is not None else "—",
            "Sleep (hrs)":    v.hours_sleep if v.hours_sleep else "—",
        })
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2 — Diet Recommendations
# ═══════════════════════════════════════════════════════════════════════════════
with tab2:
    # ── Persistent confirmation banner ────────────────────────────────────────
    if "last_saved_rec" in st.session_state:
        saved = st.session_state["last_saved_rec"]
        if saved.get("id"):
            st.success(
                f"✅ Advice stored in database — "
                f"Table: `recommendations` · Row ID: **{saved['id']}** · "
                f"Model: {MODEL_LABELS.get(saved['model'], saved['model'])} · "
                f"Time: {saved['ts'][:16]}"
            )

    recs_raw = load_recommendations(selected_pid)

    if not recs_raw:
        st.info("No recommendations yet. Click **Generate New Advice** in the sidebar.")
    else:
        # Build selector
        rec_opts = {
            f"[{MODEL_LABELS.get(model, model)}] {ts[:16]}  (ID {rid})": {
                "id": rid, "model": model, "ts": ts,
                "assessment": assessment,
                "priority_changes": json.loads(priority or "[]"),
                "breakfast": breakfast, "lunch": lunch, "dinner": dinner,
                "foods_to_avoid": json.loads(foods or "[]"),
                "clinical_note": clinical_note,
            }
            for rid, model, ts, assessment, priority, breakfast, lunch, dinner, foods, clinical_note
            in recs_raw
        }

        default_idx = 0
        if "current_rec_id" in st.session_state:
            for i, rd in enumerate(rec_opts.values()):
                if rd["id"] == st.session_state["current_rec_id"]:
                    default_idx = i
                    break

        sel_rec_label = st.selectbox("📂 Recommendation to review", list(rec_opts.keys()), index=default_idx)
        rec = rec_opts[sel_rec_label]

        fb_map = load_feedback_for_rec(rec["id"])

        # ── Metadata + storage info ────────────────────────────────────────────
        st.markdown(
            f'<div class="rec-meta">'
            f'Model: <b>{MODEL_LABELS.get(rec["model"], rec["model"])}</b>'
            f' &nbsp;|&nbsp; Generated: <b>{rec["ts"][:16]}</b>'
            f' &nbsp;|&nbsp; ID: <b>{rec["id"]}</b>'
            f'</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div class="stored-info">'
            f'📁 Stored in: <b>{DB_PATH}</b> &nbsp;→&nbsp; '
            f'table: <b>recommendations</b> &nbsp;→&nbsp; row ID: <b>{rec["id"]}</b>'
            f'</div>',
            unsafe_allow_html=True,
        )

        # ── Edit stored recommendation ─────────────────────────────────────────
        with st.expander("✏️ Edit this recommendation (changes saved back to database)"):
            e_assessment = st.text_area(
                "Diet assessment",
                value=rec["assessment"] or "",
                height=80,
                key=f"e_assess_{rec['id']}",
            )
            e_priority_raw = st.text_area(
                "Priority changes (one per line)",
                value="\n".join(rec["priority_changes"]),
                height=100,
                key=f"e_prio_{rec['id']}",
            )
            ec1, ec2, ec3 = st.columns(3)
            with ec1:
                e_breakfast = st.text_area("Breakfast", value=rec["breakfast"] or "", height=80, key=f"e_bfast_{rec['id']}")
            with ec2:
                e_lunch = st.text_area("Lunch", value=rec["lunch"] or "", height=80, key=f"e_lunch_{rec['id']}")
            with ec3:
                e_dinner = st.text_area("Dinner", value=rec["dinner"] or "", height=80, key=f"e_dinner_{rec['id']}")
            e_avoid_raw = st.text_area(
                "Foods to avoid (one per line)",
                value="\n".join(rec["foods_to_avoid"]),
                height=90,
                key=f"e_avoid_{rec['id']}",
            )
            e_clinical = st.text_area(
                "Clinical note",
                value=rec["clinical_note"] or "",
                height=80,
                key=f"e_clinical_{rec['id']}",
            )

            if st.button("💾 Save changes to database", key=f"save_edit_{rec['id']}"):
                updated_fields = {
                    "assessment":       e_assessment.strip(),
                    "priority_changes": json.dumps(
                        [l.strip() for l in e_priority_raw.splitlines() if l.strip()]
                    ),
                    "breakfast":        e_breakfast.strip(),
                    "lunch":            e_lunch.strip(),
                    "dinner":           e_dinner.strip(),
                    "foods_to_avoid":   json.dumps(
                        [l.strip() for l in e_avoid_raw.splitlines() if l.strip()]
                    ),
                    "clinical_note":    e_clinical.strip(),
                }
                do_update_recommendation(rec["id"], updated_fields)
                st.success(f"✅ Row ID {rec['id']} updated in `recommendations` table.")
                st.cache_data.clear()
                st.rerun()

        st.markdown("---")

        # ── Assessment ─────────────────────────────────────────────────────────
        st.subheader("📝 Diet Assessment")
        st.info(rec["assessment"] or "—")

        # ── Priority Changes ───────────────────────────────────────────────────
        st.subheader("⚡ Priority Changes")
        for i, ch in enumerate(rec["priority_changes"], 1):
            st.write(f"**{i}.** {ch}")

        st.markdown("---")

        # ── Meal Cards ─────────────────────────────────────────────────────────
        st.subheader("🍽️ Meal Plan")
        meal_ratings, meal_notes = {}, {}
        meal_cfg = [
            ("breakfast", "🌅 Breakfast", rec["breakfast"]),
            ("lunch",     "☀️ Lunch",     rec["lunch"]),
            ("dinner",    "🌙 Dinner",    rec["dinner"]),
        ]
        cols = st.columns(3)
        for (field, label, text), col in zip(meal_cfg, cols):
            with col:
                st.markdown(
                    f'<div class="meal-card"><h4>{label}</h4><p>{text or "—"}</p></div>',
                    unsafe_allow_html=True,
                )
                existing = fb_map.get(field, ("—", ""))
                options  = ["good", "bad", "—"]
                r = st.radio("Rate", options,
                             index=options.index(existing[0]) if existing[0] in options else 2,
                             key=f"r_{field}_{rec['id']}", horizontal=True,
                             label_visibility="collapsed")
                n = st.text_input("Note", value=existing[1] or "",
                                  placeholder="Note…",
                                  key=f"n_{field}_{rec['id']}",
                                  label_visibility="collapsed")
                meal_ratings[field] = r
                meal_notes[field]   = n

        st.markdown("---")

        # ── Foods to Avoid ─────────────────────────────────────────────────────
        st.subheader("🚫 Foods to Avoid")
        avoid_ratings, avoid_notes = {}, {}
        for i, food in enumerate(rec["foods_to_avoid"]):
            key = f"avoid_{i}"
            existing = fb_map.get(key, ("—", ""))
            c1, c2, c3 = st.columns([5, 2, 3])
            with c1:
                st.write(f"• {food}")
            with c2:
                options = ["good", "bad", "—"]
                r = st.radio("Rate", options,
                             index=options.index(existing[0]) if existing[0] in options else 2,
                             key=f"r_{key}_{rec['id']}", horizontal=True,
                             label_visibility="collapsed")
                avoid_ratings[key] = r
            with c3:
                n = st.text_input("Note", value=existing[1] or "",
                                  placeholder="Note…",
                                  key=f"n_{key}_{rec['id']}",
                                  label_visibility="collapsed")
                avoid_notes[key] = n

        st.markdown("---")

        # ── Clinical Note ──────────────────────────────────────────────────────
        st.subheader("⚕️ Clinical Note for Doctor")
        existing_cn  = fb_map.get("clinical_note", ("—", ""))
        clinical_text = rec["clinical_note"] or "None"
        if clinical_text.lower() != "none":
            st.warning(clinical_text)
        else:
            st.success("None — no urgent flags.")

        c1, c2 = st.columns([2, 4])
        with c1:
            options = ["good", "bad", "—"]
            cn_r = st.radio("Rate", options,
                            index=options.index(existing_cn[0]) if existing_cn[0] in options else 2,
                            key=f"r_cn_{rec['id']}", horizontal=True,
                            label_visibility="collapsed")
        with c2:
            cn_n = st.text_input("Note", value=existing_cn[1] or "",
                                 placeholder="Comment on this flag…",
                                 key=f"n_cn_{rec['id']}",
                                 label_visibility="collapsed")

        st.markdown("---")

        # ── Submit feedback ────────────────────────────────────────────────────
        if st.button("💾 Submit Feedback", type="primary", key=f"sub_{rec['id']}"):
            items = {}
            for field in ["breakfast", "lunch", "dinner"]:
                if meal_ratings.get(field, "—") != "—":
                    items[field] = (meal_ratings[field], meal_notes.get(field, ""))
            for key in avoid_ratings:
                if avoid_ratings[key] != "—":
                    items[key] = (avoid_ratings[key], avoid_notes.get(key, ""))
            if cn_r != "—":
                items["clinical_note"] = (cn_r, cn_n)

            if not items:
                st.warning("Please rate at least one field before submitting.")
            else:
                do_save_feedback(rec["id"], selected_pid, items)
                st.success(
                    f"✅ {len(items)} rating(s) saved to database — "
                    f"table: `feedback` · linked to recommendation ID {rec['id']}"
                )
                st.rerun()

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3 — Feedback Log
# ═══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.subheader("📋 Feedback Log")
    all_fb = load_all_feedback_rows()

    if not all_fb:
        st.info("No feedback submitted yet.")
    else:
        RATING_ICON = {"good": "✅ Good", "bad": "❌ Bad"}
        rows = []
        for ts, pid, rec_id, field, rating, notes in all_fb:
            rows.append({
                "Submitted": (ts or "")[:16],
                "Patient":   pid,
                "Rec ID":    rec_id,
                "Field":     field,
                "Rating":    RATING_ICON.get(rating, rating or "—"),
                "Notes":     notes or "—",
            })
        df = pd.DataFrame(rows)

        fc1, fc2, fc3 = st.columns(3)
        with fc1:
            pf = st.multiselect("Patient", sorted(df["Patient"].unique()))
        with fc2:
            ff = st.multiselect("Field",   sorted(df["Field"].unique()))
        with fc3:
            rf = st.multiselect("Rating",  sorted(df["Rating"].unique()))

        if pf: df = df[df["Patient"].isin(pf)]
        if ff: df = df[df["Field"].isin(ff)]
        if rf: df = df[df["Rating"].isin(rf)]

        st.dataframe(df, use_container_width=True, hide_index=True)

        st.markdown("---")
        s1, s2, s3, s4 = st.columns(4)
        with s1: st.metric("Total ratings", len(df))
        with s2: st.metric("✅ Good", (df["Rating"] == "✅ Good").sum())
        with s3: st.metric("❌ Bad",  (df["Rating"] == "❌ Bad").sum())
        with s4:
            good_n  = (df["Rating"] == "✅ Good").sum()
            total_n = len(df[df["Rating"].isin(["✅ Good", "❌ Bad"])])
            st.metric("Approval rate", f"{good_n/total_n*100:.0f}%" if total_n else "—")
