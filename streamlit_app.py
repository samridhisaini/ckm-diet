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
from ckm_api.llm.dietician import get_diet_advice, DEFAULT_MODEL

Base.metadata.create_all(bind=engine)
DB_PATH = os.path.abspath("ckm.db")

# ─── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="CKM Dietician", layout="wide", page_icon="🩺",
                   initial_sidebar_state="expanded")

st.markdown("""
<style>
  #MainMenu, footer { visibility: hidden; }
  .block-container { padding-top: 1.2rem; padding-bottom: 2rem; }

  /* Metric tiles */
  [data-testid="stMetric"] {
      background: #F8F9FA; border-radius: 10px;
      padding: 14px 16px; border: 1px solid #E9ECEF;
  }

  /* Meal cards */
  .meal-card { border-radius: 12px; padding: 16px 18px; min-height: 120px;
               border: 1px solid rgba(0,0,0,0.07); margin-bottom: 4px; }
  .bfast { background:#FFF8E1; border-left:4px solid #F9A825; }
  .lunch { background:#E8F5E9; border-left:4px solid #388E3C; }
  .dinner{ background:#E3F2FD; border-left:4px solid #1565C0; }
  .meal-label { font-size:11px; font-weight:700; text-transform:uppercase;
                letter-spacing:1px; color:#777; margin-bottom:8px; }
  .meal-text  { font-size:14px; color:#1a1a1a; line-height:1.5; }
  .rated-badge-good { color:#2E7D32; font-size:11px; font-weight:700; }
  .rated-badge-bad  { color:#B71C1C; font-size:11px; font-weight:700; }

  /* Priority items */
  .prio-item { background:#F3E5F5; border-left:3px solid #7B1FA2;
               border-radius:0 8px 8px 0; padding:9px 14px;
               margin-bottom:6px; font-size:14px; }

  /* Assessment box */
  .assess-box { background:#E3F2FD; border-left:4px solid #1565C0;
                border-radius:0 8px 8px 0; padding:14px 18px;
                margin-bottom:4px; font-size:14px; color:#0D47A1; }

  /* Avoid rows */
  .avoid-item { background:#FFF3E0; border-radius:8px; padding:10px 14px;
                margin-bottom:5px; font-size:14px; color:#BF360C; }

  /* Pre-submit summary */
  .save-preview { background:#F1F8E9; border:1px solid #AED581;
                  border-radius:8px; padding:12px 16px; font-size:13px;
                  color:#33691E; margin-bottom:8px; }

  /* Section headers */
  .sec-hdr { font-size:15px; font-weight:700; color:#333;
             margin:20px 0 10px 0; padding-bottom:6px;
             border-bottom:2px solid #E0E0E0; }

  /* Arm badge */
  .arm-badge { display:inline-block; padding:4px 14px; border-radius:20px;
               font-size:13px; font-weight:600; }

  /* Storage chip */
  .db-chip { background:#F0FFF4; border:1px solid #A5D6A7; border-radius:8px;
             padding:8px 14px; font-size:12px; color:#2E7D32;
             font-family:monospace; margin-top:26px; }
</style>
""", unsafe_allow_html=True)

# ─── Constants ─────────────────────────────────────────────────────────────────
VISIT_ORDER = ["Baseline", "3rd month", "6th month", "9th month", "12th month"]
MODEL_LABELS = {
    "gemini-2.5-flash": "Gemini 2.5 Flash ⚡",
    "gemini-2.5-pro":   "Gemini 2.5 Pro 🔬",
    "gemini-1.5-flash": "Gemini 1.5 Flash",
    "gemini-1.5-pro":   "Gemini 1.5 Pro",
}
MEAL_CFG = [
    ("breakfast", "🌅 Breakfast", "bfast"),
    ("lunch",     "☀️ Lunch",    "lunch"),
    ("dinner",    "🌙 Dinner",   "dinner"),
]

# ─── DB helpers ────────────────────────────────────────────────────────────────
def db_session(): return SessionLocal()

@st.cache_data(ttl=60)
def load_patients():
    db = db_session()
    try:
        result = []
        for p in db.query(models.Patient).all():
            visits = crud.get_visits(db, p.pid)
            hba1c = [v.hb_a1c for v in visits if v.hb_a1c is not None]
            result.append({"pid": p.pid, "arm": p.arm, "age": p.age,
                           "gender": p.gender, "uphc": p.uphc,
                           "hba1c_bl": hba1c[0] if hba1c else None,
                           "hba1c_last": hba1c[-1] if len(hba1c) > 1 else None})
        return result
    finally:
        db.close()

def load_patient_data(pid):
    db = db_session()
    try:   return crud.get_patient_with_visits(db, pid)
    finally: db.close()

def load_recs(pid):
    db = db_session()
    try:
        return [{"id": r.id, "model": r.model_used, "ts": r.generated_at,
                 "assessment": r.assessment,
                 "priority_changes": json.loads(r.priority_changes or "[]"),
                 "breakfast": r.breakfast, "lunch": r.lunch, "dinner": r.dinner,
                 "foods_to_avoid": json.loads(r.foods_to_avoid or "[]"),
                 "clinical_note": r.clinical_note}
                for r in crud.get_recommendations(db, pid)]
    finally:
        db.close()

def load_fb(rec_id):
    db = db_session()
    try:
        return {fb.field_name: (fb.rating, fb.notes or "")
                for fb in crud.get_feedback_for_recommendation(db, rec_id)}
    finally:
        db.close()

def load_all_fb():
    db = db_session()
    try:
        return [{"Submitted": (fb.submitted_at or "")[:16], "Patient": fb.pid,
                 "Rec ID": fb.recommendation_id, "Field": fb.field_name,
                 "Rating": "✅ Good" if fb.rating == "good" else "❌ Bad",
                 "Notes": fb.notes or "—"}
                for fb in crud.get_all_feedback(db)]
    finally:
        db.close()

def save_fb(rec_id, pid, items):
    db = db_session()
    try:
        crud.save_feedback_batch(db, rec_id, pid, items, "")
        db.commit()
        return True, None
    except Exception as e:
        db.rollback()
        return False, str(e)
    finally:
        db.close()

def save_edit(rec_id, fields):
    db = db_session()
    try:
        crud.update_recommendation(db, rec_id, fields)
        return True, None
    except Exception as e:
        return False, str(e)
    finally:
        db.close()

# Rating helpers — read directly from session_state (bypasses widget return value issues)
def ss_rating(field, rec_id):
    v = st.session_state.get(f"r_{field}_{rec_id}")
    if v in ("✅ Good", "✅"): return "good"
    if v in ("❌ Bad",  "❌"): return "bad"
    return None

def pill_default_from_fb(fb_map, field):
    r = fb_map.get(field, (None, ""))[0]
    return "✅ Good" if r == "good" else "❌ Bad" if r == "bad" else None

# ─── Sidebar ───────────────────────────────────────────────────────────────────
st.sidebar.title("🩺 CKM Dietician")
st.sidebar.markdown("---")

pts = load_patients()
if not pts:
    st.error("No patients. Run `python -m ckm_api.seed` first.")
    st.stop()

def pt_label(i, p):
    tag = "🔵 LC" if "carbohydrate" in (p["arm"] or "").lower() else "🟠 UD"
    hba = f"  HbA1c {p['hba1c_last']}%" if p["hba1c_last"] else ""
    return f"P{i+1} · {p['pid']}  {tag}{hba}"

pid_map  = {pt_label(i, p): p["pid"] for i, p in enumerate(pts)}
sel_pt   = st.sidebar.selectbox("Patient", list(pid_map.keys()))
sel_pid  = pid_map[sel_pt]

st.sidebar.markdown("---")
model_inv = {v: k for k, v in MODEL_LABELS.items()}
sel_model_label = st.sidebar.selectbox("AI Model", list(MODEL_LABELS.values()))
sel_model = model_inv[sel_model_label]

st.sidebar.markdown("---")
gen_btn = st.sidebar.button("🔄 Generate New Advice", use_container_width=True, type="primary")
st.sidebar.caption("🔵 LC = Low Carb Diet  ·  🟠 UD = Usual Diet")

# ─── Load patient ──────────────────────────────────────────────────────────────
patient, visits = load_patient_data(sel_pid)
if not patient:
    st.error(f"Patient {sel_pid} not found.")
    st.stop()

visits = sorted(visits, key=lambda v: VISIT_ORDER.index(v.visit_label)
                if v.visit_label in VISIT_ORDER else 99)
attended  = [v for v in visits if v.attended != "No"]
latest_v  = attended[-1] if attended else visits[-1]
hba1c_ser = [(v.visit_label, v.hb_a1c) for v in visits if v.hb_a1c is not None]
hba1c_d   = (hba1c_ser[-1][1] - hba1c_ser[0][1]) if len(hba1c_ser) >= 2 else None

# ─── Header ────────────────────────────────────────────────────────────────────
arm_col = "#1565C0" if "carbohydrate" in (patient.arm or "").lower() else "#E65100"
st.title(f"Patient {sel_pid}")
st.markdown(
    f'<span class="arm-badge" style="background:{arm_col}18; color:{arm_col}; '
    f'border:1px solid {arm_col}40">{patient.arm}</span>'
    f'<span style="color:#888; margin-left:14px; font-size:14px;">'
    f'Age {patient.age} · {patient.gender} · {patient.uphc} · '
    f'DM {patient.diabetes_duration_yr} yr</span>',
    unsafe_allow_html=True)
st.markdown("")

# ─── Generate ──────────────────────────────────────────────────────────────────
if gen_btn:
    with st.spinner(f"Calling {sel_model_label}…"):
        try:
            pjson = crud.build_patient_json(patient, visits)
            advice = get_diet_advice(pjson, model=sel_model)
            db = db_session()
            rec_obj = crud.save_recommendation(db, sel_pid, sel_model, advice)
            db.close()
            st.session_state["cur_rec_id"] = rec_obj.id
            st.session_state["gen_ok"] = (
                f"✅ Advice generated with {sel_model_label} — "
                f"saved to **recommendations** table, Row ID **{rec_obj.id}**"
            )
            st.cache_data.clear()
        except Exception as e:
            st.error(f"Generation failed: {e}")

if st.session_state.get("gen_ok"):
    st.success(st.session_state["gen_ok"])

# ─── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["📊 Clinical Overview", "🥗 Diet & Feedback", "📋 Feedback Log"])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — Clinical Overview
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        st.metric("HbA1c (latest)",
                  f"{latest_v.hb_a1c}%" if latest_v.hb_a1c else "—",
                  f"{hba1c_d:+.1f}%" if hba1c_d is not None else None,
                  delta_color="inverse")
    with c2: st.metric("BMI", f"{latest_v.bmi:.1f}" if latest_v.bmi else "—", latest_v.bmi_category or "")
    with c3:
        bp = f"{int(latest_v.sys_bp)}/{int(latest_v.dia_bp)}" if latest_v.sys_bp and latest_v.dia_bp else "—"
        st.metric("BP (mmHg)", bp)
    with c4: st.metric("Waist", f"{latest_v.waist_cm} cm" if latest_v.waist_cm else "—")
    with c5: st.metric("Antidiabetics",
                        str(latest_v.n_oral_antidiabetics) if latest_v.n_oral_antidiabetics is not None else "—")

    st.markdown("---")
    L, R = st.columns(2)
    with L:
        st.markdown('<div class="sec-hdr">Comorbidities</div>', unsafe_allow_html=True)
        for lbl, val in [("Hypertension", patient.hypertension), ("Heart Attack", patient.heart_attack),
                         ("Stroke", patient.stroke), ("Neuropathy", patient.neuropathy),
                         ("Retinopathy", patient.retinopathy), ("CKD", patient.ckd)]:
            icon = "🔴" if val == "Yes" else "🟢" if val == "No" else "⚪"
            st.write(f"{icon} **{lbl}:** {val or '—'}")
        st.markdown('<div class="sec-hdr" style="margin-top:18px">Demographics</div>', unsafe_allow_html=True)
        for lbl, val in [("Occupation", patient.occupation),
                         ("Education", f"{patient.education_years} yr" if patient.education_years else None),
                         ("Monthly income", f"₹{patient.income_monthly:,}" if patient.income_monthly else None),
                         ("Family members", str(patient.family_members) if patient.family_members else None),
                         ("Med adherence", patient.med_adherence)]:
            if val: st.write(f"**{lbl}:** {val}")
    with R:
        st.markdown('<div class="sec-hdr">HbA1c Trend</div>', unsafe_allow_html=True)
        if hba1c_ser:
            st.line_chart(pd.DataFrame(hba1c_ser, columns=["Visit","HbA1c (%)"]).set_index("Visit"),
                          color="#E53935", height=175)
        else: st.info("No HbA1c data.")
        st.markdown('<div class="sec-hdr">BMI Trend</div>', unsafe_allow_html=True)
        bmi_ser = [(v.visit_label, v.bmi) for v in visits if v.bmi]
        if bmi_ser:
            st.line_chart(pd.DataFrame(bmi_ser, columns=["Visit","BMI"]).set_index("Visit"),
                          color="#1E88E5", height=175)

    st.markdown("---")
    st.markdown('<div class="sec-hdr">Visit-by-Visit Summary</div>', unsafe_allow_html=True)
    rows = []
    for v in visits:
        rows.append({
            "Visit": v.visit_label, "Date": v.visit_date or "—", "Attended": v.attended or "—",
            "HbA1c (%)": v.hb_a1c or "—", "BMI": f"{v.bmi:.1f}" if v.bmi else "—",
            "BP": f"{int(v.sys_bp)}/{int(v.dia_bp)}" if v.sys_bp and v.dia_bp else "—",
            "Weight (kg)": v.weight_kg or "—",
            "Soft drinks/wk": v.diet_soft_drinks if v.diet_soft_drinks is not None else "—",
            "Junk food/wk": v.diet_junk_foods   if v.diet_junk_foods  is not None else "—",
            "Fruits/wk": v.diet_fruits           if v.diet_fruits      is not None else "—",
            "Vegetables/wk": v.diet_vegetables   if v.diet_vegetables  is not None else "—",
        })
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — Diet & Feedback
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    recs = load_recs(sel_pid)
    if not recs:
        st.info("ℹ️ No recommendations yet. Click **Generate New Advice** in the sidebar.")
    else:
        # Recommendation selector
        rec_labels = {
            f"#{r['id']} · {MODEL_LABELS.get(r['model'], r['model'])} · {r['ts'][:16]}": r
            for r in recs
        }
        default_idx = 0
        if "cur_rec_id" in st.session_state:
            for i, r in enumerate(recs):
                if r["id"] == st.session_state["cur_rec_id"]:
                    default_idx = i
                    break

        cs, ci = st.columns([3, 2])
        with cs:
            chosen_label = st.selectbox("📂 Select Recommendation", list(rec_labels.keys()),
                                        index=default_idx)
        rec = rec_labels[chosen_label]
        with ci:
            st.markdown(
                f'<div class="db-chip">💾 ckm.db → recommendations → row <b>{rec["id"]}</b></div>',
                unsafe_allow_html=True)

        fb_map = load_fb(rec["id"])

        # ── Assessment ────────────────────────────────────────────────────────
        st.markdown('<div class="sec-hdr">📝 Diet Assessment</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="assess-box">{rec["assessment"] or "—"}</div>', unsafe_allow_html=True)

        # ── Priority Changes ──────────────────────────────────────────────────
        if rec["priority_changes"]:
            st.markdown('<div class="sec-hdr">⚡ Priority Changes</div>', unsafe_allow_html=True)
            for i, ch in enumerate(rec["priority_changes"], 1):
                st.markdown(f'<div class="prio-item"><b>{i}.</b> {ch}</div>', unsafe_allow_html=True)

        st.markdown("---")

        # ── Meal Plan ─────────────────────────────────────────────────────────
        st.markdown('<div class="sec-hdr">🍽️ Meal Plan — Rate each suggestion</div>', unsafe_allow_html=True)
        meal_cols = st.columns(3)
        for (field, label, cls), col in zip(MEAL_CFG, meal_cols):
            with col:
                r_existing = fb_map.get(field, (None, ""))[0]
                badge = (f'<span class="rated-badge-good"> · ✅ Rated Good</span>' if r_existing == "good"
                         else f'<span class="rated-badge-bad"> · ❌ Rated Bad</span>' if r_existing == "bad"
                         else "")
                st.markdown(
                    f'<div class="meal-card {cls}">'
                    f'<div class="meal-label">{label}{badge}</div>'
                    f'<div class="meal-text">{rec.get(field) or "—"}</div>'
                    f'</div>', unsafe_allow_html=True)

                st.pills("Rate", ["✅ Good", "❌ Bad"],
                         default=pill_default_from_fb(fb_map, field),
                         key=f"r_{field}_{rec['id']}",
                         selection_mode="single",
                         label_visibility="collapsed")
                st.text_input("Note", value=fb_map.get(field, (None, ""))[1] or "",
                              placeholder="Optional note…",
                              key=f"note_{field}_{rec['id']}",
                              label_visibility="collapsed")

        st.markdown("---")

        # ── Foods to Avoid ────────────────────────────────────────────────────
        if rec["foods_to_avoid"]:
            st.markdown('<div class="sec-hdr">🚫 Foods to Avoid</div>', unsafe_allow_html=True)
            for i, food in enumerate(rec["foods_to_avoid"]):
                key = f"avoid_{i}"
                r_existing = fb_map.get(key, (None, ""))[0]
                a1, a2, a3 = st.columns([5, 2, 3])
                with a1:
                    st.markdown(f'<div class="avoid-item">🚫 {food}</div>', unsafe_allow_html=True)
                with a2:
                    default_av = ("✅" if r_existing == "good" else "❌" if r_existing == "bad" else None)
                    st.pills("Rate", ["✅", "❌"], default=default_av,
                             key=f"r_{key}_{rec['id']}",
                             selection_mode="single",
                             label_visibility="collapsed")
                with a3:
                    st.text_input("Note", value=fb_map.get(key, (None, ""))[1] or "",
                                  placeholder="Note…",
                                  key=f"note_{key}_{rec['id']}",
                                  label_visibility="collapsed")
            st.markdown("---")

        # ── Clinical Note ─────────────────────────────────────────────────────
        st.markdown('<div class="sec-hdr">⚕️ Clinical Note for Doctor</div>', unsafe_allow_html=True)
        clinical_text = rec["clinical_note"] or "None"
        if clinical_text.strip().lower() == "none":
            st.success("✅ No urgent clinical flags.")
        else:
            st.warning(f"⚠️ {clinical_text}")

        n1, n2 = st.columns([2, 4])
        with n1:
            st.pills("Rate flag", ["✅ Good", "❌ Bad"],
                     default=pill_default_from_fb(fb_map, "clinical_note"),
                     key=f"r_clinical_note_{rec['id']}",
                     selection_mode="single",
                     label_visibility="collapsed")
        with n2:
            st.text_input("Comment", value=fb_map.get("clinical_note", (None, ""))[1] or "",
                          placeholder="Comment on this flag…",
                          key=f"note_clinical_note_{rec['id']}",
                          label_visibility="collapsed")

        st.markdown("---")

        # ── Edit stored recommendation (collapsed) ────────────────────────────
        with st.expander("✏️ Edit stored recommendation"):
            e_assess = st.text_area("Assessment", value=rec["assessment"] or "", height=70,
                                    key=f"e_assess_{rec['id']}")
            e_prio = st.text_area("Priority changes (one per line)",
                                  value="\n".join(rec["priority_changes"]), height=85,
                                  key=f"e_prio_{rec['id']}")
            ec1, ec2, ec3 = st.columns(3)
            with ec1: e_bf = st.text_area("Breakfast", value=rec["breakfast"] or "", height=80, key=f"e_bf_{rec['id']}")
            with ec2: e_lu = st.text_area("Lunch",     value=rec["lunch"]     or "", height=80, key=f"e_lu_{rec['id']}")
            with ec3: e_di = st.text_area("Dinner",    value=rec["dinner"]    or "", height=80, key=f"e_di_{rec['id']}")
            e_av = st.text_area("Foods to avoid (one per line)",
                                value="\n".join(rec["foods_to_avoid"]), height=75,
                                key=f"e_av_{rec['id']}")
            e_cn = st.text_area("Clinical note", value=rec["clinical_note"] or "", height=70,
                                key=f"e_cn_{rec['id']}")
            if st.button("💾 Save edits", key=f"do_edit_{rec['id']}"):
                ok, err = save_edit(rec["id"], {
                    "assessment": e_assess.strip(),
                    "priority_changes": json.dumps([l.strip() for l in e_prio.splitlines() if l.strip()]),
                    "breakfast": e_bf.strip(), "lunch": e_lu.strip(), "dinner": e_di.strip(),
                    "foods_to_avoid": json.dumps([l.strip() for l in e_av.splitlines() if l.strip()]),
                    "clinical_note": e_cn.strip(),
                })
                if ok:
                    st.success(f"✅ Row {rec['id']} updated.")
                    st.cache_data.clear()
                    st.rerun()
                else:
                    st.error(f"Edit failed: {err}")

        st.markdown("---")

        # ── Collect pending ratings from session_state ─────────────────────────
        pending = {}

        for field, _, _ in MEAL_CFG:
            r = ss_rating(field, rec["id"])
            if r:
                note = st.session_state.get(f"note_{field}_{rec['id']}", "")
                pending[field] = (r, note)

        for i in range(len(rec["foods_to_avoid"])):
            key = f"avoid_{i}"
            v = st.session_state.get(f"r_{key}_{rec['id']}")
            r = "good" if v == "✅" else "bad" if v == "❌" else None
            if r:
                note = st.session_state.get(f"note_{key}_{rec['id']}", "")
                pending[key] = (r, note)

        r_cn = ss_rating("clinical_note", rec["id"])
        if r_cn:
            pending["clinical_note"] = (r_cn, st.session_state.get(f"note_clinical_note_{rec['id']}", ""))

        # ── Pre-submit summary ─────────────────────────────────────────────────
        FIELD_NAMES = {"breakfast": "Breakfast", "lunch": "Lunch", "dinner": "Dinner",
                       "clinical_note": "Clinical note",
                       **{f"avoid_{i}": f"Avoid #{i+1}" for i in range(10)}}

        if pending:
            parts = [f"{'✅' if r=='good' else '❌'} {FIELD_NAMES.get(f, f)}"
                     for f, (r, _) in pending.items()]
            st.markdown(
                f'<div class="save-preview">Ready to save {len(pending)} rating(s): '
                f'{" · ".join(parts)}</div>',
                unsafe_allow_html=True)
        else:
            st.caption("👆 Rate at least one item above using ✅ Good or ❌ Bad, then submit.")

        # ── Persistent success after submit ───────────────────────────────────
        fb_key = f"fb_ok_{rec['id']}"
        if st.session_state.get(fb_key):
            st.success(st.session_state[fb_key])

        # ── Buttons ───────────────────────────────────────────────────────────
        b1, b2 = st.columns([3, 1])
        with b1:
            if st.button("💾 Submit Feedback", type="primary",
                         use_container_width=True, key=f"sub_{rec['id']}"):
                if not pending:
                    st.warning("Please rate at least one item before submitting.")
                else:
                    ok, err = save_fb(rec["id"], sel_pid, pending)
                    if ok:
                        st.session_state[fb_key] = (
                            f"✅ {len(pending)} rating(s) saved to database — "
                            f"table: feedback · recommendation ID {rec['id']} · "
                            f"fields: {', '.join(pending)}"
                        )
                        st.cache_data.clear()
                        st.rerun()
                    else:
                        st.error(f"❌ Save failed: {err}")
        with b2:
            if st.button("🗑️ Clear", use_container_width=True, key=f"clr_{rec['id']}"):
                for field, _, _ in MEAL_CFG:
                    for prefix in ("r_", "note_"):
                        k = f"{prefix}{field}_{rec['id']}"
                        st.session_state.pop(k, None)
                for i in range(len(rec["foods_to_avoid"])):
                    for prefix in ("r_avoid_", "note_avoid_"):
                        k = f"{prefix}{i}_{rec['id']}"
                        st.session_state.pop(k, None)
                for k in (f"r_clinical_note_{rec['id']}", f"note_clinical_note_{rec['id']}"):
                    st.session_state.pop(k, None)
                st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — Feedback Log
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown('<div class="sec-hdr">📋 All Submitted Feedback</div>', unsafe_allow_html=True)
    all_fb = load_all_fb()

    if not all_fb:
        st.info("No feedback submitted yet. Go to **Diet & Feedback** tab to rate recommendations.")
    else:
        df = pd.DataFrame(all_fb)
        fc1, fc2, fc3 = st.columns(3)
        with fc1: pf = st.multiselect("Patient", sorted(df["Patient"].unique()))
        with fc2: ff = st.multiselect("Field",   sorted(df["Field"].unique()))
        with fc3: rf = st.multiselect("Rating",  sorted(df["Rating"].unique()))
        if pf: df = df[df["Patient"].isin(pf)]
        if ff: df = df[df["Field"].isin(ff)]
        if rf: df = df[df["Rating"].isin(rf)]

        st.dataframe(df, use_container_width=True, hide_index=True)
        st.markdown("---")
        s1, s2, s3, s4 = st.columns(4)
        gn = (df["Rating"] == "✅ Good").sum()
        bn = (df["Rating"] == "❌ Bad").sum()
        with s1: st.metric("Total ratings", len(df))
        with s2: st.metric("✅ Good", gn)
        with s3: st.metric("❌ Bad",  bn)
        with s4: st.metric("Approval rate", f"{gn/(gn+bn)*100:.0f}%" if gn + bn else "—")
