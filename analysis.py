"""
LCD Follow-Up Study — Data Analysis & Visualisation
NOTE: The CSV has only 5 real records (rows 2-6); rows 7-1187 are blank.
All plots use the 5 actual records only.
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.gridspec as gridspec
from matplotlib.colors import LinearSegmentedColormap
import seaborn as sns
import warnings
warnings.filterwarnings("ignore")

# ── Style ──────────────────────────────────────────────────────────────────────
BLUE   = "#4C72B0"
GREEN  = "#2ca02c"
RED    = "#d62728"
ORANGE = "#ff7f0e"
PURPLE = "#9467bd"
TEAL   = "#17becf"
GREY   = "#7f7f7f"

plt.rcParams.update({
    "figure.dpi":        150,
    "savefig.dpi":       150,
    "font.family":       "sans-serif",
    "axes.spines.top":   False,
    "axes.spines.right": False,
    "axes.titlesize":    12,
    "axes.labelsize":    10,
    "xtick.labelsize":   9,
    "ytick.labelsize":   9,
    "legend.fontsize":   9,
})

OUTDIR = "plots/"

# ── Load data — drop all-NaN rows ─────────────────────────────────────────────
df = pd.read_csv("lcd_follow_up.csv").dropna(how="all").reset_index(drop=True)
N = len(df)
assert N == 5, f"Expected 5 real records, got {N}"
print(f"Loaded {N} real records.\n")

# ── Code → Label lookups ───────────────────────────────────────────────────────
ZONE_MAP = {
    1: "Zone IV\n(Tondiarpet)",
    2: "Zone VI\n(Thiru-Vi-Ka Nagar)",
    3: "Zone XI\n(Valasaravakkam)",
    4: "Zone XIII\n(Adyar)",
}
UPHC_MAP = {
    1:"Elango Nagar", 2:"New Washermenpet", 3:"R.K. Nagar",
    4:"Sharma Nagar",  5:"K.P. Park",       6:"Kolathur",
    7:"Thanthai Periyar", 8:"TVK Nagar",    9:"Kamarajar Salai",
    10:"Maduravoyal", 11:"Nerkundram",      12:"Shakthinagar",
    13:"Ekkattuthangal", 14:"SRKV",         15:"Velachery",
    16:"Vol. Health Svcs",
}
FOLLOWUP_MAP = {1:"3rd month", 2:"6th month", 3:"9th month", 4:"12th month"}

# Patient short labels
P_LABELS = [
    f"P{i+1}\n({UPHC_MAP[int(df['uphc'].iloc[i])]})"
    for i in range(N)
]
P_SHORT  = [f"P{i+1}" for i in range(N)]

GAD7_COLS = ["Q67_nervous","Q68_control_worry","Q69_worry_things",
             "Q70_trouble","Q71_restless","Q72_irritable","Q73_afraid"]
PHQ9_COLS = ["Q74_little_int","Q75_feeling_down","Q76_asleep",
             "Q77_little_energy","Q78_poor_appetite","Q79_feel_bad",
             "Q80_trouble_concentrate","Q81_speak_slowly","Q82_hurt_yourself"]

GAD7_ITEMS = ["Feeling nervous","Not controlling worry",
              "Worrying too much","Trouble relaxing",
              "Restlessness","Irritability","Feeling afraid"]
PHQ9_ITEMS = ["Little interest/pleasure","Feeling down/hopeless",
              "Trouble sleeping","Little energy","Poor appetite",
              "Feeling bad about self","Trouble concentrating",
              "Moving/speaking slowly","Hurting yourself"]

EQ5D_COLS  = ["Q57_mobility","Q58_self_care","Q59_usual_activity",
              "Q60_pain","Q61_anxiety"]
EQ5D_NAMES = ["Mobility","Self-care","Usual activity","Pain","Anxiety/depression"]

DIET_COLS  = ["Q27_eggs_protein","Q28_more_fruits","Q29_more_vegetables",
              "Q30_moringa_squashes","Q31_nuts_seeds",
              "Q32_more_meal","Q33_soft_drinks","Q34_junk_foods"]
DIET_NAMES = ["Eggs/protein","Fruits","Vegetables",
              "Moringa/squashes","Nuts/seeds","More meals",
              "Soft drinks","Junk foods"]

PATIENT_COLORS = [BLUE, GREEN, ORANGE, PURPLE, TEAL]

def save(fig, name):
    path = OUTDIR + name
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    print(f"  saved → {path}")


# ══════════════════════════════════════════════════════════════════════════════
# 1. STUDY OVERVIEW
# ══════════════════════════════════════════════════════════════════════════════
print("[1] Study overview …")
fig, axes = plt.subplots(1, 3, figsize=(16, 5))
fig.suptitle("Study Overview — LCD Follow-Up (n=5, 12th-month visit, Feb 2026)",
             fontsize=13, fontweight="bold")

# 1a — Zone distribution
zone_vals = df["zone"].astype(int)
zone_counts = zone_vals.value_counts().sort_index()
zone_labels = [ZONE_MAP[z].replace("\n", " ") for z in zone_counts.index]
bar_colors = [PATIENT_COLORS[i % len(PATIENT_COLORS)] for i in range(len(zone_counts))]
bars = axes[0].bar(range(len(zone_counts)), zone_counts.values,
                   color=bar_colors, edgecolor="white", linewidth=0.8)
axes[0].set_xticks(range(len(zone_counts)))
axes[0].set_xticklabels(zone_labels, fontsize=8)
axes[0].set_ylabel("Number of participants")
axes[0].set_title("By Zone")
for bar, v in zip(bars, zone_counts.values):
    axes[0].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05,
                 str(v), ha="center", fontsize=11, fontweight="bold")
axes[0].set_ylim(0, zone_counts.max() + 0.7)

# 1b — UPHC distribution
uphc_vals = df["uphc"].astype(int)
uphc_counts = uphc_vals.value_counts().sort_index()
uphc_labels = [UPHC_MAP[u] for u in uphc_counts.index]
bars2 = axes[1].bar(range(len(uphc_counts)), uphc_counts.values,
                    color=[GREEN, ORANGE, TEAL], edgecolor="white", linewidth=0.8)
axes[1].set_xticks(range(len(uphc_counts)))
axes[1].set_xticklabels(uphc_labels, fontsize=8, rotation=15, ha="right")
axes[1].set_ylabel("Number of participants")
axes[1].set_title("By UPHC")
for bar, v in zip(bars2, uphc_counts.values):
    axes[1].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05,
                 str(v), ha="center", fontsize=11, fontweight="bold")
axes[1].set_ylim(0, uphc_counts.max() + 0.7)

# 1c — Key facts panel
axes[2].axis("off")
fu_label = FOLLOWUP_MAP[int(df["followup"].iloc[0])]
facts = [
    ("Total participants",        "5"),
    ("Follow-up visit",           fu_label),
    ("Attendance",                "5/5 (100%)"),
    ("Zones covered",             "3 of 4"),
    ("UPHCs covered",             "3 of 16"),
    ("Data collection dates",     "03–04 Feb 2026"),
    ("No-shows",                  "0"),
    ("Medication change reported","0"),
]
axes[2].set_xlim(0, 1); axes[2].set_ylim(0, 1)
axes[2].set_title("Key Facts", pad=6)
for i, (k, v) in enumerate(facts):
    y = 0.9 - i * 0.105
    axes[2].text(0.0, y, k + ":", fontsize=9, color=GREY, va="center")
    axes[2].text(1.0, y, v, fontsize=9, fontweight="bold", va="center", ha="right")
    axes[2].axhline(y - 0.045, color="#dddddd", linewidth=0.6, xmin=0, xmax=1)

fig.tight_layout()
save(fig, "01_study_overview.png")


# ══════════════════════════════════════════════════════════════════════════════
# 2. PARTICIPANT SUMMARY TABLE
# ══════════════════════════════════════════════════════════════════════════════
print("[2] Participant summary table …")

ZONE_SHORT = {1:"Zone IV\n(Tondiarpet)", 2:"Zone VI\n(Thiru-Vi-Ka Nagar)",
              3:"Zone XI\n(Valasaravakkam)", 4:"Zone XIII\n(Adyar)"}

table_data = {
    "Zone":           [ZONE_SHORT[int(z)] for z in df["zone"]],
    "UPHC":           [UPHC_MAP[int(u)] for u in df["uphc"]],
    "Ind. ID":        df["ind_id"].astype(int).tolist(),
    "Weight (kg)":    df["Q6_weight"].tolist(),
    "Waist (cm)":     df["Q7_waist"].tolist(),
    "SBP (mmHg)":     df["Q8_sys_bp"].tolist(),
    "DBP (mmHg)":     df["Q9_dia_bp"].tolist(),
    "HbA1c (%)":      df["Q18_HbA1c"].tolist(),
    "FBG (mg/dL)":    df["Q22a_fast_gluc"].tolist(),
    "TChol (mg/dL)":  df["Q19a_tot_chol"].tolist(),
    "Trig (mg/dL)":   df["Q19b_trig"].tolist(),
    "LDL (mg/dL)":    df["Q19c_low_lipo"].tolist(),
    "HDL (mg/dL)":    df["Q19e_hig_lipo"].tolist(),
    "Creat (mg/dL)":  df["Q20_ser_creat"].tolist(),
    "HOMA-IR":        df["Q21_homa_ir"].tolist(),
    "Sleep (h)":      df["Q55_hours_sleep"].tolist(),
    "EQ-VAS":         df["Q63_health_range"].tolist(),
}

rows   = P_SHORT
cols   = list(table_data.keys())
values = [[table_data[c][i] for c in cols] for i in range(N)]

fig, ax = plt.subplots(figsize=(20, 4))
ax.axis("off")
tbl = ax.table(
    cellText=values,
    rowLabels=rows,
    colLabels=cols,
    loc="center",
    cellLoc="center",
)
tbl.auto_set_font_size(False)
tbl.set_fontsize(8)
tbl.scale(1, 2.2)
# widen the first two data columns (Zone, UPHC)
for r in range(N + 1):
    tbl[r, 0].set_width(0.12)
    tbl[r, 1].set_width(0.10)
# Header & row-label styling
for (r, c), cell in tbl.get_celld().items():
    if r == 0 or c == -1:
        cell.set_facecolor("#2C3E50")
        cell.set_text_props(color="white", fontweight="bold")
    else:
        cell.set_facecolor("#F0F4F8" if r % 2 == 0 else "white")
    cell.set_edgecolor("#cccccc")

ax.set_title("Participant Summary — All 5 Records", fontsize=13,
             fontweight="bold", pad=12)
fig.tight_layout()
save(fig, "02_participant_summary_table.png")


# ══════════════════════════════════════════════════════════════════════════════
# 3. ANTHROPOMETRICS & BLOOD PRESSURE — Per-patient dot plot with ref lines
# ══════════════════════════════════════════════════════════════════════════════
print("[3] Anthropometrics & BP …")

metrics_anthro = [
    ("Q6_weight",  "Weight (kg)",               None,    None),
    ("Q7_waist",   "Waist circumference (cm)",  80,      None),   # high-risk >80 women / >90 men (use 90 approx)
    ("Q8_sys_bp",  "Systolic BP (mmHg)",        None,    130),    # target <130 for T2DM
    ("Q9_dia_bp",  "Diastolic BP (mmHg)",       None,    80),
]

fig, axes = plt.subplots(1, 4, figsize=(18, 5))
fig.suptitle("Anthropometrics & Blood Pressure (n=5, 12th month)",
             fontsize=13, fontweight="bold")

for ax, (col, label, ref_low, ref_high) in zip(axes, metrics_anthro):
    vals = df[col].tolist()
    for i, (v, p) in enumerate(zip(vals, P_SHORT)):
        ax.scatter(i, v, color=PATIENT_COLORS[i], s=120, zorder=5)
        ax.text(i, v, f" {v}", va="center", fontsize=8.5, color=PATIENT_COLORS[i])
    if ref_high:
        ax.axhline(ref_high, color=RED, linewidth=1.5, linestyle="--",
                   label=f"Target: {ref_high}")
    if ref_low:
        ax.axhline(ref_low, color=ORANGE, linewidth=1.5, linestyle="--",
                   label=f"Threshold: {ref_low}")
    ax.set_xticks(range(N))
    ax.set_xticklabels(P_SHORT)
    ax.set_ylabel(label)
    ax.set_title(label)
    yvals = vals
    pad = (max(yvals) - min(yvals)) * 0.25 + 2
    ax.set_ylim(min(yvals) - pad, max(yvals) + pad)
    if ref_high or ref_low:
        ax.legend(fontsize=8)

fig.tight_layout()
save(fig, "03_anthropometrics_bp.png")


# ══════════════════════════════════════════════════════════════════════════════
# 4. GLYCAEMIA & LIPID PROFILE — Per-patient dot plot with clinical ref lines
# ══════════════════════════════════════════════════════════════════════════════
print("[4] Glycaemia & lipids …")

# (col, label, target_line, target_label, higher_is_worse)
lab_panel = [
    ("Q18_HbA1c",     "HbA1c (%)",              7.0,  "Target <7%",         True),
    ("Q22a_fast_gluc","Fasting Glucose (mg/dL)", 126,  "Diabetes ≥126",      True),
    ("Q19a_tot_chol", "Total Cholesterol",        200,  "Desirable <200",     True),
    ("Q19b_trig",     "Triglycerides (mg/dL)",    150,  "Normal <150",        True),
    ("Q19c_low_lipo", "LDL (mg/dL)",              100,  "Optimal <100 (DM)",  True),
    ("Q19e_hig_lipo", "HDL (mg/dL)",              40,   "Low HDL <40",        False),
    ("Q20_ser_creat", "Serum Creatinine (mg/dL)", 1.2,  "Upper normal 1.2",   True),
    ("Q21_homa_ir",   "HOMA-IR",                  2.5,  "IR threshold 2.5",   True),
]

fig, axes = plt.subplots(2, 4, figsize=(20, 10))
fig.suptitle("Glycaemia & Lipid Profile — Per Participant (with Clinical Reference Lines)",
             fontsize=13, fontweight="bold")

for ax, (col, label, ref, ref_label, higher_bad) in zip(axes.flatten(), lab_panel):
    vals = df[col].tolist()
    for i, (v, p) in enumerate(zip(vals, P_SHORT)):
        color = PATIENT_COLORS[i]
        # flag if value is concerning
        flag = (v > ref) if higher_bad else (v < ref)
        marker = "D" if flag else "o"
        ax.scatter(i, v, color=color, s=130, zorder=5, marker=marker)
        ax.text(i, v, f"  {v}", va="center", fontsize=8, color=color)
    ax.axhline(ref, color=RED, linewidth=1.5, linestyle="--", label=ref_label)
    ax.set_xticks(range(N))
    ax.set_xticklabels(P_SHORT)
    ax.set_ylabel(label)
    ax.set_title(label)
    ypad = max((max(vals) - min(vals)) * 0.25, abs(ref) * 0.1) + 1
    ax.set_ylim(min(min(vals), ref) - ypad, max(max(vals), ref) + ypad)
    ax.legend(fontsize=7.5)

# Note about diamond marker
fig.text(0.5, -0.01,
         "◆ = value outside clinical target  |  ● = within target",
         ha="center", fontsize=9, color=GREY)
fig.tight_layout()
save(fig, "04_glycaemia_lipids.png")


# ══════════════════════════════════════════════════════════════════════════════
# 5. DIET — Heatmap (participants × food items, colour = days/week)
# ══════════════════════════════════════════════════════════════════════════════
print("[5] Diet heatmap …")

diet_matrix = df[DIET_COLS].values.astype(float)  # shape (5, 8)

fig, ax = plt.subplots(figsize=(12, 5))
# Split colourmap: healthy=green, unhealthy=red scale
im = ax.imshow(diet_matrix, aspect="auto", cmap="RdYlGn", vmin=0, vmax=7)

ax.set_xticks(range(len(DIET_NAMES)))
ax.set_xticklabels(DIET_NAMES, rotation=30, ha="right", fontsize=9)
ax.set_yticks(range(N))
ax.set_yticklabels(P_LABELS, fontsize=9)

# Annotate cells
for r in range(N):
    for c in range(len(DIET_COLS)):
        val = diet_matrix[r, c]
        txt_col = "black" if 2 <= val <= 5 else "white"
        ax.text(c, r, f"{int(val)}d/wk", ha="center", va="center",
                fontsize=9, fontweight="bold", color=txt_col)

cbar = fig.colorbar(im, ax=ax, orientation="vertical", fraction=0.03, pad=0.02)
cbar.set_label("Days per week (0–7)", fontsize=9)
cbar.set_ticks([0, 1, 2, 3, 4, 5, 6, 7])

ax.set_title("Dietary Habits — Days per Week  "
             "(Green = more days, Red = fewer; "
             "NOTE: for unhealthy items more days = worse)",
             fontsize=11, fontweight="bold")

# Highlight unhealthy items with a box
unhealthy_idx = [6, 7]  # soft drinks, junk foods
for c in unhealthy_idx:
    ax.add_patch(plt.Rectangle((c - 0.5, -0.5), 1, N,
                                fill=False, edgecolor="black",
                                linewidth=2, linestyle="--", zorder=10))
ax.text(6, -0.85, "⚠ Unhealthy items", ha="center", fontsize=8,
        color="black", style="italic")

fig.tight_layout()
save(fig, "05_diet_heatmap.png")


# ══════════════════════════════════════════════════════════════════════════════
# 6. PHYSICAL ACTIVITY & SLEEP
# ══════════════════════════════════════════════════════════════════════════════
print("[6] Physical activity & sleep …")

fig, axes = plt.subplots(1, 3, figsize=(17, 5))
fig.suptitle("Physical Activity & Sleep (n=5)", fontsize=13, fontweight="bold")

# 6a — Moderate activity: days/week + mins/session
mod_days = df["Q50_days_mod_activity"].tolist()     # all = 7
mod_mins = df["Q51_time_mod_activity"].tolist()     # varies
ax = axes[0]
bars = ax.bar(range(N), mod_mins, color=PATIENT_COLORS, edgecolor="white", linewidth=0.7)
ax.axhline(150/7, color=RED, linewidth=1.5, linestyle="--",
           label="WHO daily min (150 min/wk÷7)")
for bar, v in zip(bars, mod_mins):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
            f"{int(v)} min", ha="center", fontsize=9, fontweight="bold")
ax.set_xticks(range(N))
ax.set_xticklabels(P_SHORT)
ax.set_ylabel("Minutes per session")
ax.set_title("Moderate Activity\n(all do 7 days/week)")
ax.legend()
ax.set_ylim(0, max(mod_mins) + 25)

# 6b — Walking: yes/no + days + time
walk_vals    = df["Q52_walk"].tolist()          # 1=yes 2=no
walk_days    = df["Q53_days_walk"].tolist()
walk_mins    = df["Q54_time_walk"].tolist()
ax = axes[1]
walk_status = ["Walk" if w == 1 else "Don't walk" for w in walk_vals]
face_colors = [GREEN if w == 1 else "#dddddd" for w in walk_vals]
bars = ax.bar(range(N), [1]*N, color=face_colors, edgecolor="grey", linewidth=0.7)
for i, (ws, wd, wm) in enumerate(zip(walk_status, walk_days, walk_mins)):
    detail = f"{ws}"
    if ws == "Walk":
        detail += f"\n{int(wd) if not pd.isna(wd) else '?'}d/wk, {int(wm) if not pd.isna(wm) else '?'} min"
    axes[1].text(i, 0.5, detail, ha="center", va="center",
                 fontsize=9, fontweight="bold",
                 color="white" if ws == "Walk" else GREY)
ax.set_xticks(range(N))
ax.set_xticklabels(P_SHORT)
ax.set_yticks([])
ax.set_title("Regular Walking")
green_p  = mpatches.Patch(color=GREEN,   label="Walks regularly")
grey_p   = mpatches.Patch(color="#dddddd", label="Does not walk", linewidth=0.5)
ax.legend(handles=[green_p, grey_p], fontsize=8)

# 6c — Sleep hours
sleep_hrs = df["Q55_hours_sleep"].tolist()
ax = axes[2]
bar_cols = [RED if h < 7 else GREEN for h in sleep_hrs]
bars = ax.bar(range(N), sleep_hrs, color=bar_cols, edgecolor="white", linewidth=0.7)
ax.axhline(7, color=GREEN, linewidth=1.8, linestyle="--", label="Recommended (7h)")
for bar, v in zip(bars, sleep_hrs):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05,
            f"{int(v)}h", ha="center", fontsize=10, fontweight="bold")
ax.set_xticks(range(N))
ax.set_xticklabels(P_SHORT)
ax.set_ylabel("Hours per night")
ax.set_title("Hours of Sleep\n(all < recommended 7h)")
ax.set_ylim(0, 8.5)
ax.legend()

fig.tight_layout()
save(fig, "06_physical_activity_sleep.png")


# ══════════════════════════════════════════════════════════════════════════════
# 7. LIFESTYLE — Tobacco, Alcohol  (binary summary)
# ══════════════════════════════════════════════════════════════════════════════
print("[7] Lifestyle summary …")

lifestyle_vars = {
    "Current smoking\n(Q35)":          "Q35_cur_smoke",
    "Smokeless tobacco\n(Q39)":        "Q39_cur_smokeless",
    "Alcohol\n(Q43)":                  "Q43_cons_alcohol",
    "Vigorous\nactivity (Q46)":        "Q46_vig_phy_activity",
    "Sleep\ndisturbed (Q56)":          "Q56_sleep_distrub",
    "Medication\nchanged (Q64)":       "Q64_med_changes",
    "Statin\nprescribed (Q66)":        "Q66_statin",
}

fig, ax = plt.subplots(figsize=(13, 5))
n_vars = len(lifestyle_vars)
x = np.arange(n_vars)
width = 0.55

yes_counts = []
no_counts  = []
for col in lifestyle_vars.values():
    yes_counts.append((df[col] == 1).sum())
    no_counts.append((df[col] == 2).sum())

b1 = ax.bar(x, yes_counts, width, label="Yes (code=1)", color=ORANGE,
            edgecolor="white", linewidth=0.7)
b2 = ax.bar(x, no_counts,  width, bottom=yes_counts, label="No (code=2)",
            color=GREEN, edgecolor="white", linewidth=0.7, alpha=0.85)

# Annotate bars
for i, (y, n) in enumerate(zip(yes_counts, no_counts)):
    if y > 0:
        ax.text(i, y/2, str(y), ha="center", va="center",
                fontsize=11, fontweight="bold", color="white")
    if n > 0:
        ax.text(i, y + n/2, str(n), ha="center", va="center",
                fontsize=11, fontweight="bold", color="white")

ax.set_xticks(x)
ax.set_xticklabels(list(lifestyle_vars.keys()), fontsize=9)
ax.set_ylabel("Number of participants")
ax.set_ylim(0, N + 0.5)
ax.set_yticks(range(N + 1))
ax.set_title("Lifestyle & Clinical Flags — Yes / No Count (n=5)",
             fontsize=12, fontweight="bold")
ax.legend()
fig.tight_layout()
save(fig, "07_lifestyle_flags.png")


# ══════════════════════════════════════════════════════════════════════════════
# 8. COMORBIDITIES & MEDICATION ADHERENCE
# ══════════════════════════════════════════════════════════════════════════════
print("[8] Comorbidities & adherence …")

comorbidity_cols = {
    "Heart attack":         "Q10_hrt_attck",
    "Stroke":               "Q11_stroke",
    "Hypertension":         "Q12_hypertension",
    "CKD":                  "Q13_ckd",
    "Diabetic neuropathy":  "Q14_dia_neuro",
    "Diabetic retinopathy": "Q15_dia_retino",
    "Diabetic foot/ulcer":  "Q16_ulcer",
    "Other condition":      "Q17_other_med_con",
}
adherence_cols = {
    "Ever forget meds":    "Q23_ever_forget",
    "Careless at times":   "Q24_careless_at_times",
    "Stop taking meds":    "Q25_stop_taking_med",
    "Feel worse on meds":  "Q26_feel_worse_med",
}

fig, axes = plt.subplots(1, 2, figsize=(16, 6))
fig.suptitle("Comorbidities & Medication Adherence (n=5)", fontsize=13, fontweight="bold")

def binary_heatmap(ax, col_dict, title, yes_label="Yes (1)", no_label="No (2)"):
    data = np.array([[1 if df[c].iloc[r] == 1 else 0
                      for c in col_dict.values()]
                     for r in range(N)])
    cmap2 = LinearSegmentedColormap.from_list("yn", [GREEN, RED])
    im = ax.imshow(data, cmap=cmap2, vmin=0, vmax=1, aspect="auto")
    ax.set_xticks(range(len(col_dict)))
    ax.set_xticklabels(list(col_dict.keys()), rotation=35, ha="right", fontsize=9)
    ax.set_yticks(range(N))
    ax.set_yticklabels(P_SHORT)
    for r in range(N):
        for c in range(len(col_dict)):
            ax.text(c, r, "YES" if data[r, c] == 1 else "NO",
                    ha="center", va="center", fontsize=9, fontweight="bold",
                    color="white")
    ax.set_title(title, fontsize=11)
    yes_p = mpatches.Patch(color=RED,   label=yes_label)
    no_p  = mpatches.Patch(color=GREEN, label=no_label)
    ax.legend(handles=[yes_p, no_p], loc="upper right", fontsize=8,
              bbox_to_anchor=(1, -0.22))

binary_heatmap(axes[0], comorbidity_cols,
               "Comorbidities\n(all answered No)",
               "Yes — present", "No — absent")
binary_heatmap(axes[1], adherence_cols,
               "Medication Adherence Issues\n(all answered No — good adherence)",
               "Yes — issue reported", "No — no issue")

fig.tight_layout(rect=[0, 0.05, 1, 1])
save(fig, "08_comorbidities_adherence.png")


# ══════════════════════════════════════════════════════════════════════════════
# 9. EQ-5D QUALITY OF LIFE
# ══════════════════════════════════════════════════════════════════════════════
print("[9] EQ-5D quality of life …")

eq5d_matrix = df[EQ5D_COLS].values.astype(float)  # shape (5, 5)
vas_vals    = df["Q63_health_range"].tolist()

fig, axes = plt.subplots(1, 3, figsize=(20, 5))
fig.suptitle("Quality of Life — EQ-5D (n=5)", fontsize=13, fontweight="bold")

# 9a — EQ-5D heatmap (1=no problem … 5=extreme)
cmap_eq = LinearSegmentedColormap.from_list("eq", [GREEN, "#FFFFA0", RED])
im = axes[0].imshow(eq5d_matrix, cmap=cmap_eq, vmin=1, vmax=5, aspect="auto")
axes[0].set_xticks(range(5))
axes[0].set_xticklabels(EQ5D_NAMES, rotation=25, ha="right", fontsize=9)
axes[0].set_yticks(range(N))
axes[0].set_yticklabels(P_LABELS, fontsize=9)

severity_labels = {1:"None", 2:"Slight", 3:"Moderate", 4:"Severe", 5:"Extreme"}
for r in range(N):
    for c in range(5):
        v = int(eq5d_matrix[r, c])
        txt_col = "white" if v >= 4 else "black"
        axes[0].text(c, r, f"{severity_labels[v]}\n({v})",
                     ha="center", va="center", fontsize=8, color=txt_col)

cbar = fig.colorbar(im, ax=axes[0], fraction=0.04, pad=0.02)
cbar.set_ticks([1, 2, 3, 4, 5])
cbar.set_ticklabels(["1-No prob", "2-Slight", "3-Moderate", "4-Severe", "5-Extreme"])
axes[0].set_title("EQ-5D Domain Severity\n(1=No problems → 5=Extreme)", fontsize=11)

# 9b — EQ-VAS (0–100, self-rated overall health)
ax2 = axes[1]
bars_vas = ax2.bar(range(N), vas_vals, color=PATIENT_COLORS,
                   edgecolor="white", linewidth=0.7, alpha=0.9)
ax2.axhline(75, color=ORANGE, linewidth=1.4, linestyle="--", label="Good health (≥75)")
for bar, v in zip(bars_vas, vas_vals):
    ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
             str(int(v)), ha="center", fontsize=10, fontweight="bold")
ax2.set_xticks(range(N))
ax2.set_xticklabels(P_SHORT)
ax2.set_ylabel("EQ-VAS Score (0–100)")
ax2.set_ylim(0, 105)
ax2.set_title("EQ-VAS Self-Rated Overall Health\n(0=Worst → 100=Best imaginable)", fontsize=11)
ax2.legend(fontsize=8)

# 9c — Mental health score (Q62, 0–20 Likert-style)
ax3 = axes[2]
mh_vals = df["Q62_men_hlth"].tolist()
mh_colors = [RED if v >= 10 else ORANGE if v >= 5 else GREEN for v in mh_vals]
bars_mh = ax3.bar(range(N), mh_vals, color=mh_colors,
                  edgecolor="white", linewidth=0.7, alpha=0.9)
for bar, v in zip(bars_mh, mh_vals):
    ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.2,
             str(int(v)), ha="center", fontsize=10, fontweight="bold")
ax3.set_xticks(range(N))
ax3.set_xticklabels(P_SHORT)
ax3.set_ylabel("Mental Health Score")
ax3.set_ylim(0, max(mh_vals) + 3)
ax3.set_title("Mental Health Score (Q62)\n(Higher = more symptoms)", fontsize=11)
low_p  = mpatches.Patch(color=GREEN,  label="Low (0–4)")
mid_p  = mpatches.Patch(color=ORANGE, label="Moderate (5–9)")
high_p = mpatches.Patch(color=RED,    label="High (≥10)")
ax3.legend(handles=[low_p, mid_p, high_p], fontsize=8)

fig.tight_layout()
save(fig, "09_eq5d_qol.png")


# ══════════════════════════════════════════════════════════════════════════════
# 10. MENTAL HEALTH — GAD-7 & PHQ-9 item-level heatmaps + total scores
# ══════════════════════════════════════════════════════════════════════════════
print("[10] Mental health …")

gad_matrix = df[GAD7_COLS].values.astype(float)   # shape (5, 7)
phq_matrix = df[PHQ9_COLS].values.astype(float)   # shape (5, 9)
gad_totals = gad_matrix.sum(axis=1)
phq_totals = phq_matrix.sum(axis=1)

scale_labels = {0:"0 – Not at all", 1:"1 – Several days",
                2:"2 – >Half days", 3:"3 – Nearly daily"}

fig, axes = plt.subplots(2, 2, figsize=(18, 10))
fig.suptitle("Mental Health Screening — GAD-7 (Anxiety) & PHQ-9 (Depression)",
             fontsize=13, fontweight="bold")

cmap_mh = LinearSegmentedColormap.from_list("mh", [GREEN, "#FFFFA0", RED])

# 10a — GAD-7 heatmap
im1 = axes[0, 0].imshow(gad_matrix, cmap=cmap_mh, vmin=0, vmax=3, aspect="auto")
axes[0, 0].set_xticks(range(7))
axes[0, 0].set_xticklabels(GAD7_ITEMS, rotation=35, ha="right", fontsize=8.5)
axes[0, 0].set_yticks(range(N))
axes[0, 0].set_yticklabels(P_SHORT)
for r in range(N):
    for c in range(7):
        v = int(gad_matrix[r, c])
        axes[0, 0].text(c, r, scale_labels[v], ha="center", va="center",
                        fontsize=7.5, color="black" if v < 2 else "white")
axes[0, 0].set_title("GAD-7 Item Responses", fontsize=11)
fig.colorbar(im1, ax=axes[0, 0], fraction=0.04, pad=0.02,
             ticks=[0, 1, 2, 3]).set_ticklabels(
             ["0-Not at all","1-Several days","2->Half days","3-Nearly daily"])

# 10b — PHQ-9 heatmap
im2 = axes[0, 1].imshow(phq_matrix, cmap=cmap_mh, vmin=0, vmax=3, aspect="auto")
axes[0, 1].set_xticks(range(9))
axes[0, 1].set_xticklabels(PHQ9_ITEMS, rotation=35, ha="right", fontsize=8.5)
axes[0, 1].set_yticks(range(N))
axes[0, 1].set_yticklabels(P_SHORT)
for r in range(N):
    for c in range(9):
        v = int(phq_matrix[r, c])
        axes[0, 1].text(c, r, scale_labels[v], ha="center", va="center",
                        fontsize=7.5, color="black" if v < 2 else "white")
axes[0, 1].set_title("PHQ-9 Item Responses", fontsize=11)
fig.colorbar(im2, ax=axes[0, 1], fraction=0.04, pad=0.02,
             ticks=[0, 1, 2, 3]).set_ticklabels(
             ["0-Not at all","1-Several days","2->Half days","3-Nearly daily"])

# 10c — GAD-7 total scores bar
ax = axes[1, 0]
bar_colors_g = [GREEN if s <= 4 else ORANGE if s <= 9 else RED for s in gad_totals]
bars = ax.bar(P_SHORT, gad_totals, color=bar_colors_g, edgecolor="white", linewidth=0.7)
ax.axhline(5,  color=ORANGE, linewidth=1.5, linestyle="--", label="Mild (≥5)")
ax.axhline(10, color=RED,    linewidth=1.5, linestyle="--", label="Moderate (≥10)")
for bar, v in zip(bars, gad_totals):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05,
            str(int(v)), ha="center", fontsize=11, fontweight="bold")
ax.set_ylabel("Total GAD-7 Score (0–21)")
ax.set_title("GAD-7 Total Score per Participant\n(all in 'Minimal' range 0–4)")
ax.set_ylim(0, 12)
ax.legend(fontsize=8)

# 10d — PHQ-9 total scores bar
ax = axes[1, 1]
bar_colors_p = [GREEN if s <= 4 else ORANGE if s <= 9 else RED for s in phq_totals]
bars = ax.bar(P_SHORT, phq_totals, color=bar_colors_p, edgecolor="white", linewidth=0.7)
ax.axhline(5,  color=ORANGE, linewidth=1.5, linestyle="--", label="Mild (≥5)")
ax.axhline(10, color=RED,    linewidth=1.5, linestyle="--", label="Moderate (≥10)")
for bar, v in zip(bars, phq_totals):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
            str(int(v)), ha="center", fontsize=11, fontweight="bold")
ax.set_ylabel("Total PHQ-9 Score (0–27)")
ax.set_title("PHQ-9 Total Score per Participant\n(all in 'Minimal' range 0–4)")
ax.set_ylim(0, 8)
ax.legend(fontsize=8)

fig.tight_layout()
save(fig, "10_mental_health.png")


# ══════════════════════════════════════════════════════════════════════════════
# 11. KEY FINDINGS SUMMARY DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
print("[11] Summary dashboard …")

fig = plt.figure(figsize=(18, 9))
fig.patch.set_facecolor("#F7F9FC")
fig.suptitle("LCD Follow-Up Study — Key Findings Dashboard (n=5, 12th Month Visit)",
             fontsize=15, fontweight="bold", color="#2C3E50", y=1.01)

gs = gridspec.GridSpec(3, 5, figure=fig, hspace=0.6, wspace=0.5)

kpi_data = [
    # (title, value, colour, note)
    ("Participants",        "5",               BLUE,   "12th month visit"),
    ("Attendance",          "100%",            GREEN,  "All 5 attended"),
    ("HbA1c range",         "9.1–12.7%",       RED,    "All above 7% target"),
    ("Mean HbA1c",          f"{df['Q18_HbA1c'].mean():.1f}%", RED, "Poorly controlled DM"),
    ("FBG range",           "193–308 mg/dL",   RED,    "All diabetic range"),
    ("Mean Systolic BP",    f"{df['Q8_sys_bp'].mean():.0f} mmHg", ORANGE, "Target <130"),
    ("Smokers",             "0 / 5",           GREEN,  "None smoke"),
    ("Alcohol consumers",   "0 / 5",           GREEN,  "None drink"),
    ("Soft drinks",         "7/7 days",        RED,    "All 5 — daily consumption"),
    ("Moderate PA",         "5/5",             GREEN,  "All do 7 days/wk"),
    ("Vigorous PA",         "0/5",             ORANGE, "None do vigorous activity"),
    ("Mean sleep",          f"{df['Q55_hours_sleep'].mean():.1f} h/night", RED, "All below 7h recommended"),
    ("Mean EQ-VAS",         f"{df['Q63_health_range'].mean():.0f}/100", TEAL, "Self-rated health"),
    ("Comorbidities",       "None reported",   GREEN,  "All answered No"),
    ("Med adherence",       "Excellent",       GREEN,  "No issues in any patient"),
]

for i, (title, value, color, note) in enumerate(kpi_data):
    row, col = divmod(i, 5)
    ax = fig.add_subplot(gs[row, col])
    ax.set_facecolor(color + "15")
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.axis("off")
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.add_patch(plt.Rectangle((0,0),1,1, fill=False,
                                edgecolor=color, linewidth=1.5,
                                transform=ax.transAxes))
    ax.text(0.5, 0.68, value, ha="center", va="center", fontsize=16,
            fontweight="bold", color=color, transform=ax.transAxes)
    ax.text(0.5, 0.38, title, ha="center", va="center", fontsize=8.5,
            color="#2C3E50", transform=ax.transAxes, fontweight="bold")
    ax.text(0.5, 0.13, note, ha="center", va="center", fontsize=7,
            color=GREY, transform=ax.transAxes, style="italic")

save(fig, "11_summary_dashboard.png")

print("\n✅  All 11 plots saved to", OUTDIR)
print("\nNote: The CSV contains 5 real data rows + 1,181 blank rows.")
print("All plots use only the 5 real records.")
