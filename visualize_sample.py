import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec
import matplotlib.ticker as mticker
import warnings
warnings.filterwarnings('ignore')

# ── Data load ──────────────────────────────────────────────────────────────
df = pd.read_csv('sample_to_iisc.csv')

VISIT_ORDER = ['Baseline', '3rd month', '6th month', '9th month', '12th month']
PIDS = df['pid'].unique().tolist()

ARM_COLOR = {
    'Low carbohydrate diet': '#2196F3',
    'Usual diet':            '#FF5722',
}
PID_LABEL = {pid: f"P{i+1}" for i, pid in enumerate(PIDS)}

def pid_arm(pid):
    return df.loc[df['pid'] == pid, 'arm'].iloc[0]

def arm_color(pid):
    return ARM_COLOR[pid_arm(pid)]

def pivot(col):
    """Return wide table: index=pid, columns=visit (ordered)."""
    pt = df.pivot_table(index='pid', columns='followup', values=col, aggfunc='first')
    return pt.reindex(columns=[v for v in VISIT_ORDER if v in pt.columns])

def score_gad(row):
    MAP = {'Not at all': 0, 'Several days': 1,
           'More than half the days': 2, 'Nearly every day': 3}
    cols = ['nervous','control_worry','worry_things','trouble','restless','irritable','afraid']
    vals = [MAP.get(str(row.get(c, 'Not at all')), 0) for c in cols]
    return sum(vals)

def score_phq(row):
    MAP = {'Not at all': 0, 'Several days': 1,
           'More than half the days': 2, 'Nearly every day': 3}
    cols = ['little_int','feeling_down','asleep','little_energy',
            'poor_appetite','feel_bad','trouble_concentrate','speak_slowly','hurt_yourself']
    vals = [MAP.get(str(row.get(c, 'Not at all')), 0) for c in cols]
    return sum(vals)

def score_eq5d(row):
    MAP = {'No problems': 1, 'Slight problems': 2, 'Moderate problems': 3,
           'Severe problems': 4, 'Extreme problems': 5}
    MA2 = {'No pain': 1, 'Slight pain': 2, 'Moderate pain': 3,
           'Severe pain': 4, 'Extreme pain': 5}
    MA3 = {'Not anxious': 1, 'Slight': 2, 'Moderate': 3, 'Severe': 4, 'Extreme': 5}
    cols = ['mobility','self_care','usual_activity']
    s = sum(MAP.get(str(row.get(c, 'No problems')), 1) for c in cols)
    s += MA2.get(str(row.get('pain', 'No pain')), 1)
    s += MA3.get(str(row.get('anxiety', 'Not anxious')), 1)
    return s

df['gad7']  = df.apply(score_gad,  axis=1)
df['phq9']  = df.apply(score_phq,  axis=1)
df['eq5d_sum'] = df.apply(score_eq5d, axis=1)

# ── Helpers ────────────────────────────────────────────────────────────────
def line_trend(ax, pt, ylabel, title, markers=True):
    # stagger end-label vertical offsets to avoid overlap
    pid_last_y = {}
    for pid in PIDS:
        if pid not in pt.index:
            continue
        row = pt.loc[pid]
        y_vals = [row[v] for v in pt.columns if pd.notna(row[v])]
        if y_vals:
            pid_last_y[pid] = y_vals[-1]

    # sort PIDs by their last y value for smart stagger
    sorted_by_last = sorted(pid_last_y.keys(), key=lambda p: pid_last_y[p])
    stagger_offset = {}
    for rank, pid in enumerate(sorted_by_last):
        stagger_offset[pid] = (rank - len(sorted_by_last)//2) * 4  # pts offset

    for pid in PIDS:
        if pid not in pt.index:
            continue
        row = pt.loc[pid]
        x_vals = [i for i, v in enumerate(pt.columns) if pd.notna(row[v])]
        y_vals = [row[v] for v in pt.columns if pd.notna(row[v])]
        if not x_vals:
            continue
        color = arm_color(pid)
        ax.plot(x_vals, y_vals,
                marker='o' if markers else None,
                color=color, lw=2, ms=6,
                label=f"{PID_LABEL[pid]} ({pid_arm(pid)[:3]}…)")
        # value labels at each data point
        for xi, yi in zip(x_vals, y_vals):
            ax.annotate(f"{yi:.1f}", (xi, yi),
                        textcoords='offset points', xytext=(0, 6),
                        ha='center', fontsize=7, color=color)
        # patient ID label at the END of the line (right side)
        last_x, last_y = x_vals[-1], y_vals[-1]
        ax.annotate(
            PID_LABEL[pid],
            xy=(last_x, last_y),
            xytext=(8, stagger_offset.get(pid, 0)),
            textcoords='offset points',
            fontsize=8, fontweight='bold', color=color,
            va='center',
            bbox=dict(boxstyle='round,pad=0.15', fc='white', ec=color, lw=0.8, alpha=0.85),
        )
    ax.set_xticks(range(len(pt.columns)))
    ax.set_xticklabels(list(pt.columns), rotation=25, ha='right', fontsize=8)
    ax.set_ylabel(ylabel, fontsize=9)
    ax.set_title(title, fontsize=10, fontweight='bold')
    ax.grid(axis='y', linestyle='--', alpha=0.4)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

VISIT_COLORS = {
    'Baseline':   '#78909C',
    '3rd month':  '#42A5F5',
    '6th month':  '#AB47BC',
    '9th month':  '#FFA726',
    '12th month': '#43A047',
}

def bar_compare(ax, bl_dict, end_dict, ylabel, title):
    """Two-bar (Baseline vs 12th month) with patient labels on x-axis."""
    pids_sorted = list(PIDS)
    x = np.arange(len(pids_sorted))
    w = 0.35
    bl_vals  = [bl_dict.get(p,  np.nan) for p in pids_sorted]
    end_vals = [end_dict.get(p, np.nan) for p in pids_sorted]
    bars1 = ax.bar(x - w/2, bl_vals,  w, label='Baseline',   color='#78909C', alpha=0.88)
    bars2 = ax.bar(x + w/2, end_vals, w, label='12th month', color='#43A047', alpha=0.88)
    for bar in bars1 + bars2:
        h = bar.get_height()
        if pd.notna(h) and h > 0:
            ax.text(bar.get_x() + bar.get_width()/2, h + 0.5,
                    f"{h:.1f}", ha='center', va='bottom', fontsize=6.5)
    xtick_labels = [f"{PID_LABEL[p]}\n({pid_arm(p)[:4]}…)" for p in pids_sorted]
    ax.set_xticks(x)
    ax.set_xticklabels(xtick_labels, fontsize=7.5)
    ax.set_ylabel(ylabel, fontsize=9)
    ax.set_title(title, fontsize=10, fontweight='bold')
    ax.legend(fontsize=7.5)
    ax.grid(axis='y', linestyle='--', alpha=0.4)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)


def bar_all_visits(ax, col, ylabel, title):
    """Multi-bar: one group per patient, one bar per visit."""
    pt = pivot(col)
    visits_present = list(pt.columns)
    n_visits = len(visits_present)
    n_pids   = len(PIDS)
    total_w  = 0.8
    w        = total_w / n_visits
    offsets  = np.linspace(-total_w/2 + w/2, total_w/2 - w/2, n_visits)
    x        = np.arange(n_pids)

    for vi, visit in enumerate(visits_present):
        vals = [pt.loc[p, visit] if p in pt.index and pd.notna(pt.loc[p, visit])
                else np.nan for p in PIDS]
        bars = ax.bar(x + offsets[vi], vals, w,
                      label=visit, color=VISIT_COLORS.get(visit, '#aaa'),
                      alpha=0.88, edgecolor='white', linewidth=0.5)
        for bar, v in zip(bars, vals):
            if pd.notna(v) and v > 0:
                ax.text(bar.get_x() + bar.get_width()/2, v + 0.3,
                        f"{v:.1f}", ha='center', va='bottom', fontsize=5.5, rotation=90)

    xtick_labels = [f"{PID_LABEL[p]}\n({pid_arm(p)[:4]}…)" for p in PIDS]
    ax.set_xticks(x)
    ax.set_xticklabels(xtick_labels, fontsize=7.5)
    ax.set_ylabel(ylabel, fontsize=9)
    ax.set_title(title, fontsize=10, fontweight='bold')
    ax.legend(fontsize=6.5, ncol=2, loc='upper right')
    ax.grid(axis='y', linestyle='--', alpha=0.4)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

SAVE_DIR = 'plots/'

# ═══════════════════════════════════════════════════════════════════════════
# FIGURE 1 — Patient Demographics Overview
# ═══════════════════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(14, 3.5))
ax.axis('off')
bl = df[df['followup'] == 'Baseline'].set_index('pid')

table_data = []
headers = ['Patient', 'Arm', 'Age', 'Gender', 'Education (yrs)',
           'Occupation', 'Income (₹/mo)', 'DM Duration (yrs)',
           'BMI Category', 'Hypertension']
for pid in PIDS:
    r = bl.loc[pid]
    table_data.append([
        PID_LABEL[pid],
        'Low-Carb' if 'Low' in r['arm'] else 'Usual',
        int(r['age_bl']),
        r['gender_bl'],
        int(r['education_bl']),
        r['occupation_bl'],
        f"₹{int(r['month_income_bl']):,}",
        int(r['diab_dur_bl']),
        r['bmi_cat'].replace('Obese (≥25.0)', 'Obese').replace('Overweight (23.0–24.9)', 'Overweight').replace('Normal (18.5–22.9)', 'Normal'),
        r['hypertension'],
    ])

tbl = ax.table(cellText=table_data, colLabels=headers,
               loc='center', cellLoc='center')
tbl.auto_set_font_size(False)
tbl.set_fontsize(8.5)
tbl.scale(1, 1.7)
for (row, col), cell in tbl.get_celld().items():
    if row == 0:
        cell.set_facecolor('#37474F')
        cell.set_text_props(color='white', fontweight='bold')
    else:
        pid = PIDS[row - 1]
        cell.set_facecolor(arm_color(pid) + '22')
    cell.set_edgecolor('#BDBDBD')

# Legend patches
patches = [mpatches.Patch(color=v, label=k) for k, v in ARM_COLOR.items()]
ax.legend(handles=patches, loc='upper right', fontsize=8, bbox_to_anchor=(1, 0.15))

plt.title('Patient Demographics at Baseline  (n = 5)', fontsize=12, fontweight='bold', pad=12)
plt.tight_layout()
plt.savefig(f'{SAVE_DIR}fig1_demographics.png', dpi=150, bbox_inches='tight')
plt.close()
print("Saved fig1_demographics.png")

# ═══════════════════════════════════════════════════════════════════════════
# FIGURE 2 — Clinical Trends Over Time (HbA1c, Weight, SBP, DBP)
# ═══════════════════════════════════════════════════════════════════════════
fig, axes = plt.subplots(2, 2, figsize=(14, 9))
fig.suptitle('Clinical Outcome Trends Across Follow-Up Visits', fontsize=13, fontweight='bold')

line_trend(axes[0,0], pivot('hb_a1c'), 'HbA1c (%)',         'HbA1c Over Time')
line_trend(axes[0,1], pivot('weight'),  'Weight (kg)',        'Body Weight Over Time')
line_trend(axes[1,0], pivot('sys_bp'),  'Systolic BP (mmHg)', 'Systolic Blood Pressure Over Time')
line_trend(axes[1,1], pivot('dia_bp'),  'Diastolic BP (mmHg)','Diastolic Blood Pressure Over Time')

# Shared legend
handles, labels = [], []
for pid in PIDS:
    handles.append(plt.Line2D([0],[0], color=arm_color(pid), lw=2, marker='o', ms=6))
    labels.append(f"{PID_LABEL[pid]} – {pid_arm(pid)}")
fig.legend(handles, labels, loc='lower center', ncol=3, fontsize=8,
           bbox_to_anchor=(0.5, -0.02), frameon=True)

plt.tight_layout(rect=[0, 0.06, 0.93, 1])
plt.savefig(f'{SAVE_DIR}fig2_clinical_trends.png', dpi=150, bbox_inches='tight')
plt.close()
print("Saved fig2_clinical_trends.png")

# ═══════════════════════════════════════════════════════════════════════════
# FIGURE 3 — Metabolic Markers: All Visits per Patient
# NOTE: Lipid/eGFR/HOMA-IR only collected at Baseline and 12th month;
#       intermediate visit bars will be absent for those markers.
# ═══════════════════════════════════════════════════════════════════════════
fig, axes = plt.subplots(2, 3, figsize=(16, 9))
fig.suptitle('Metabolic Markers Across All Visits — Patients Labelled (P1–P5)',
             fontsize=13, fontweight='bold')

for col, ylabel, title, ax in [
    ('tot_chol',  'mg/dL',         'Total Cholesterol',  axes[0,0]),
    ('trig',      'mg/dL',         'Triglycerides',       axes[0,1]),
    ('low_lipo',  'mg/dL',         'LDL Cholesterol',     axes[0,2]),
    ('hig_lipo',  'mg/dL',         'HDL Cholesterol',     axes[1,0]),
    ('egfr',      'mL/min/1.73m²', 'eGFR',               axes[1,1]),
    ('homa_ir',   'score',         'HOMA-IR',             axes[1,2]),
]:
    bar_all_visits(ax, col, ylabel, title)

# shared visit-colour legend at bottom
visit_patches = [mpatches.Patch(color=VISIT_COLORS[v], label=v) for v in VISIT_ORDER]
fig.legend(handles=visit_patches, loc='lower center', ncol=5, fontsize=8,
           bbox_to_anchor=(0.5, -0.01), frameon=True, title='Visit')

plt.tight_layout(rect=[0, 0.05, 1, 1])
plt.savefig(f'{SAVE_DIR}fig3_metabolic_all_visits.png', dpi=150, bbox_inches='tight')
plt.close()
print("Saved fig3_metabolic_all_visits.png")

# ═══════════════════════════════════════════════════════════════════════════
# FIGURE 4 — Follow-up Attendance Heatmap
# ═══════════════════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(9, 4))

visits = ['3rd month', '6th month', '9th month', '12th month']
attend_map = {}
for pid in PIDS:
    row = []
    for v in visits:
        sub = df[(df['pid'] == pid) & (df['followup'] == v)]
        if sub.empty:
            row.append(-1)
        else:
            val = sub['part_came_followup'].iloc[0]
            row.append(1 if val == 'Yes' else 0 if val == 'No' else -1)
    attend_map[pid] = row

mat = np.array([attend_map[p] for p in PIDS], dtype=float)
mat[mat == -1] = np.nan

from matplotlib.colors import ListedColormap
cmap = ListedColormap(['#EF5350', '#66BB6A'])

im = ax.imshow(mat, cmap=cmap, vmin=0, vmax=1, aspect='auto')
ax.set_xticks(range(len(visits)))
ax.set_xticklabels(visits, fontsize=9)
ax.set_yticks(range(len(PIDS)))
ax.set_yticklabels([f"{PID_LABEL[p]}\n({pid_arm(p)[:8]}…)" for p in PIDS], fontsize=8)
ax.set_title('Follow-up Attendance (Green = Attended, Red = Missed)', fontsize=10, fontweight='bold')

for i in range(len(PIDS)):
    for j in range(len(visits)):
        val = mat[i, j]
        if not np.isnan(val):
            txt = 'Attended' if val == 1 else 'Missed'
            ax.text(j, i, txt, ha='center', va='center', fontsize=8, fontweight='bold',
                    color='white')
        else:
            ax.text(j, i, 'No data', ha='center', va='center', fontsize=7, color='#757575')

ax.spines[:].set_visible(False)
plt.tight_layout()
plt.savefig(f'{SAVE_DIR}fig4_attendance.png', dpi=150, bbox_inches='tight')
plt.close()
print("Saved fig4_attendance.png")

# ═══════════════════════════════════════════════════════════════════════════
# FIGURE 5 — Oral Antidiabetic Drug Count Heatmap
# ═══════════════════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(10, 4))

pt_drugs = pivot('n_oral_antidiabetics')
mat_drugs = pt_drugs.values.astype(float)

cmap_d = plt.cm.YlOrRd
im = ax.imshow(mat_drugs, cmap=cmap_d, vmin=0, vmax=3, aspect='auto')
ax.set_xticks(range(len(pt_drugs.columns)))
ax.set_xticklabels(list(pt_drugs.columns), fontsize=9)
ax.set_yticks(range(len(PIDS)))
ax.set_yticklabels([f"{PID_LABEL[p]} ({pid_arm(p)[:8]}…)" for p in PIDS], fontsize=8)
ax.set_title('Number of Oral Antidiabetic Drugs per Visit', fontsize=10, fontweight='bold')

for i in range(mat_drugs.shape[0]):
    for j in range(mat_drugs.shape[1]):
        v = mat_drugs[i, j]
        if not np.isnan(v):
            ax.text(j, i, str(int(v)), ha='center', va='center',
                    fontsize=10, fontweight='bold',
                    color='white' if v >= 2 else '#333')

plt.colorbar(im, ax=ax, label='# drugs', shrink=0.8)
ax.spines[:].set_visible(False)
plt.tight_layout()
plt.savefig(f'{SAVE_DIR}fig5_drug_count_heatmap.png', dpi=150, bbox_inches='tight')
plt.close()
print("Saved fig5_drug_count_heatmap.png")

# ═══════════════════════════════════════════════════════════════════════════
# FIGURE 6 — GAD-7 & PHQ-9 Scores (Baseline vs 12th Month)
# ═══════════════════════════════════════════════════════════════════════════
fig, axes = plt.subplots(1, 3, figsize=(14, 5))
fig.suptitle('Mental Health Scores: Baseline vs 12th Month', fontsize=12, fontweight='bold')

# GAD-7
for score_col, ylabel, title, ax in [
    ('gad7',      'GAD-7 Score (0–21)',  'GAD-7 (Anxiety)',    axes[0]),
    ('phq9',      'PHQ-9 Score (0–27)',  'PHQ-9 (Depression)', axes[1]),
    ('health_range', 'VAS (0–100)',      'EQ-5D Health VAS',   axes[2]),
]:
    pt_s = pivot(score_col)
    bl_d  = {}
    end_d = {}
    for p in PIDS:
        if p in pt_s.index:
            if 'Baseline' in pt_s.columns and pd.notna(pt_s.loc[p,'Baseline']):
                bl_d[p] = pt_s.loc[p,'Baseline']
            if '12th month' in pt_s.columns and pd.notna(pt_s.loc[p,'12th month']):
                end_d[p] = pt_s.loc[p,'12th month']
    bar_compare(ax, bl_d, end_d, ylabel, title)

plt.tight_layout()
plt.savefig(f'{SAVE_DIR}fig6_mental_health.png', dpi=150, bbox_inches='tight')
plt.close()
print("Saved fig6_mental_health.png")

# ═══════════════════════════════════════════════════════════════════════════
# FIGURE 7 — Diet Frequency at Baseline (days/week)
# ═══════════════════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(12, 5))

diet_cols = {
    'eggs_protein':    'Eggs/\nProtein',
    'more_fruits':     'Fruits',
    'more_vegetables': 'Vegetables',
    'moringa_squashes':'Moringa/\nSquashes',
    'nuts_seeds':      'Nuts/\nSeeds',
    'more_meal':       'Extra\nMeals',
    'soft_drinks':     'Soft\nDrinks',
    'junk_foods':      'Junk\nFoods',
}

bl_diet = df[df['followup'] == 'Baseline'].set_index('pid')
x = np.arange(len(diet_cols))
w = 0.15
offsets = np.linspace(-(len(PIDS)-1)*w/2, (len(PIDS)-1)*w/2, len(PIDS))

for i, pid in enumerate(PIDS):
    vals = [bl_diet.loc[pid, c] if pd.notna(bl_diet.loc[pid, c]) else 0
            for c in diet_cols]
    ax.bar(x + offsets[i], vals, w,
           label=f"{PID_LABEL[pid]} ({pid_arm(pid)[:8]}…)",
           color=arm_color(pid), alpha=0.7 + 0.06*i,
           edgecolor='white')

ax.set_xticks(x)
ax.set_xticklabels(list(diet_cols.values()), fontsize=9)
ax.set_ylabel('Days per week (0–7)', fontsize=9)
ax.set_title('Dietary Intake Frequency at Baseline (days/week)', fontsize=11, fontweight='bold')
ax.set_ylim(0, 8)
ax.axhline(7, color='grey', lw=0.8, linestyle='--', label='Daily (7)')
ax.legend(fontsize=7.5, loc='upper left', ncol=2)
ax.grid(axis='y', linestyle='--', alpha=0.4)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
plt.tight_layout()
plt.savefig(f'{SAVE_DIR}fig7_diet_baseline.png', dpi=150, bbox_inches='tight')
plt.close()
print("Saved fig7_diet_baseline.png")

# ═══════════════════════════════════════════════════════════════════════════
# FIGURE 8 — Physical Activity & Sleep
# ═══════════════════════════════════════════════════════════════════════════
fig, axes = plt.subplots(1, 2, figsize=(13, 5))
fig.suptitle('Physical Activity & Sleep Hours Across Visits', fontsize=12, fontweight='bold')

# Walking days
line_trend(axes[0], pivot('days_walk'), 'Days walked/week', 'Walking Days per Week')

# Sleep hours
line_trend(axes[1], pivot('hours_sleep'), 'Hours/night', 'Sleep Hours per Night')

handles, labels = [], []
for pid in PIDS:
    handles.append(plt.Line2D([0],[0], color=arm_color(pid), lw=2, marker='o', ms=6))
    labels.append(f"{PID_LABEL[pid]} – {pid_arm(pid)}")
fig.legend(handles, labels, loc='lower center', ncol=3, fontsize=8,
           bbox_to_anchor=(0.5, -0.04), frameon=True)

plt.tight_layout(rect=[0, 0.08, 1, 1])
plt.savefig(f'{SAVE_DIR}fig8_activity_sleep.png', dpi=150, bbox_inches='tight')
plt.close()
print("Saved fig8_activity_sleep.png")

# ═══════════════════════════════════════════════════════════════════════════
# FIGURE 9 — EQ-5D Domain Heatmap — ALL 5 VISITS
# EQ-5D was collected only at Baseline and 12th month by study protocol;
# 3rd/6th/9th month panels are shown with "Not collected" indication.
# ═══════════════════════════════════════════════════════════════════════════
eq_map = {
    'mobility':      'Mobility',
    'self_care':     'Self-Care',
    'usual_activity':'Usual Activity',
    'pain':          'Pain',
    'anxiety':       'Anx./Dep.',
}
mob_map  = {'No problems':1,'Slight problems':2,'Moderate problems':3,'Severe problems':4,'Extreme problems':5}
pain_map = {'No pain':1,'Slight pain':2,'Moderate pain':3,'Severe pain':4,'Extreme pain':5}
anx_map  = {'Not anxious':1,'Slight':2,'Moderate':3,'Severe':4,'Extreme':5}

def eq_score(val, col):
    if col == 'pain':
        return pain_map.get(str(val), np.nan)
    elif col == 'anxiety':
        return anx_map.get(str(val), np.nan)
    else:
        return mob_map.get(str(val), np.nan)

fig, axes = plt.subplots(1, 5, figsize=(20, 4.5))
fig.suptitle(
    'EQ-5D Quality-of-Life Domains Across All Visits  (1 = No problems → 5 = Extreme)\n'
    'Patient labels shown on Y-axis (P1–P5)',
    fontsize=11, fontweight='bold', y=1.02
)

labels_txt = ['', 'No prob.', 'Slight', 'Moderate', 'Severe', 'Extreme']
all_visits = ['Baseline', '3rd month', '6th month', '9th month', '12th month']

for ax, visit in zip(axes, all_visits):
    sub = df[df['followup'] == visit].set_index('pid')
    mat = np.full((len(PIDS), len(eq_map)), np.nan)
    has_data = False
    for i, pid in enumerate(PIDS):
        if pid in sub.index:
            for j, col in enumerate(eq_map):
                score = eq_score(sub.loc[pid, col], col)
                if pd.notna(score):
                    has_data = True
                mat[i, j] = score

    ax.set_title(visit, fontsize=9, fontweight='bold',
                 color='#333' if has_data else '#999')

    if has_data:
        im = ax.imshow(mat, cmap='RdYlGn_r', vmin=1, vmax=5, aspect='auto')
        for i in range(len(PIDS)):
            for j in range(len(eq_map)):
                v = mat[i, j]
                if not np.isnan(v):
                    ax.text(j, i, labels_txt[int(v)],
                            ha='center', va='center', fontsize=6.5, color='black',
                            fontweight='bold' if int(v) > 1 else 'normal')
        ax.set_xticks(range(len(eq_map)))
        ax.set_xticklabels(list(eq_map.values()), rotation=30, ha='right', fontsize=7)
        ax.set_yticks(range(len(PIDS)))
        ax.set_yticklabels([f"{PID_LABEL[p]}\n({pid_arm(p)[:4]}…)" for p in PIDS], fontsize=7)
    else:
        # grey "not collected" panel
        ax.set_facecolor('#F5F5F5')
        ax.text(0.5, 0.5, 'Not collected\nat this visit',
                ha='center', va='center', transform=ax.transAxes,
                fontsize=9, color='#BDBDBD', style='italic')
        ax.set_xticks(range(len(eq_map)))
        ax.set_xticklabels(list(eq_map.values()), rotation=30, ha='right', fontsize=7, color='#BDBDBD')
        ax.set_yticks(range(len(PIDS)))
        ax.set_yticklabels([f"{PID_LABEL[p]}" for p in PIDS], fontsize=7, color='#BDBDBD')

    ax.spines[:].set_visible(False)

# one shared colorbar for the two panels that have data
sm = plt.cm.ScalarMappable(cmap='RdYlGn_r', norm=plt.Normalize(vmin=1, vmax=5))
sm.set_array([])
cbar = fig.colorbar(sm, ax=axes[-1], shrink=0.85, pad=0.04, label='Severity score')
cbar.set_ticks([1, 2, 3, 4, 5])
cbar.set_ticklabels(['1\nNo prob.', '2\nSlight', '3\nModerate', '4\nSevere', '5\nExtreme'])

plt.tight_layout()
plt.savefig(f'{SAVE_DIR}fig9_eq5d_all_visits.png', dpi=150, bbox_inches='tight')
plt.close()
print("Saved fig9_eq5d_all_visits.png")

# ═══════════════════════════════════════════════════════════════════════════
# FIGURE 10 — BMI Category & Waist Circumference
# ═══════════════════════════════════════════════════════════════════════════
fig, axes = plt.subplots(1, 2, figsize=(13, 5))
fig.suptitle('BMI and Waist Circumference Over Time', fontsize=12, fontweight='bold')

line_trend(axes[0], pivot('bmi'),   'BMI (kg/m²)',    'BMI Trend')
line_trend(axes[1], pivot('waist'), 'Waist (cm)',     'Waist Circumference Trend')

# BMI reference lines
axes[0].axhline(18.5, color='green',  linestyle=':', lw=1, label='Normal lower (18.5)')
axes[0].axhline(23.0, color='orange', linestyle=':', lw=1, label='Overweight (23.0)')
axes[0].axhline(25.0, color='red',    linestyle=':', lw=1, label='Obese (25.0)')
axes[0].legend(fontsize=7, loc='upper right')

handles, labels = [], []
for pid in PIDS:
    handles.append(plt.Line2D([0],[0], color=arm_color(pid), lw=2, marker='o', ms=6))
    labels.append(f"{PID_LABEL[pid]} – {pid_arm(pid)}")
fig.legend(handles, labels, loc='lower center', ncol=3, fontsize=8,
           bbox_to_anchor=(0.5, -0.04), frameon=True)

plt.tight_layout(rect=[0, 0.08, 0.93, 1])
plt.savefig(f'{SAVE_DIR}fig10_bmi_waist.png', dpi=150, bbox_inches='tight')
plt.close()
print("Saved fig10_bmi_waist.png")

# ═══════════════════════════════════════════════════════════════════════════
# FIGURE 11 — Arm Comparison: HbA1c Change (Baseline → 12th Month)
# ═══════════════════════════════════════════════════════════════════════════
fig, axes = plt.subplots(1, 2, figsize=(13, 5))
fig.suptitle('Arm Comparison: Change from Baseline to 12th Month', fontsize=12, fontweight='bold')

compare_vars = [
    ('hb_a1c', 'ΔHbA1c (%)', axes[0]),
    ('weight',  'ΔWeight (kg)', axes[1]),
]
for col, ylabel, ax in compare_vars:
    pt = pivot(col)
    changes = {}
    for pid in PIDS:
        if pid in pt.index:
            bl_v  = pt.loc[pid, 'Baseline']   if 'Baseline'   in pt.columns else np.nan
            end_v = pt.loc[pid, '12th month'] if '12th month' in pt.columns else np.nan
            if pd.notna(bl_v) and pd.notna(end_v):
                changes[pid] = end_v - bl_v

    colors = [arm_color(pid) for pid in changes]
    bars = ax.bar([PID_LABEL[p] for p in changes],
                  list(changes.values()),
                  color=colors, edgecolor='white', linewidth=1.2)
    ax.axhline(0, color='black', lw=0.8)
    for bar, (pid, val) in zip(bars, changes.items()):
        ax.text(bar.get_x() + bar.get_width()/2,
                val + (0.05 if val >= 0 else -0.15),
                f"{val:+.2f}", ha='center', va='bottom', fontsize=8, fontweight='bold')
    ax.set_ylabel(ylabel, fontsize=9)
    ax.set_title(ylabel.replace('Δ','Change in '), fontsize=10, fontweight='bold')
    ax.grid(axis='y', linestyle='--', alpha=0.4)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

patches = [mpatches.Patch(color=v, label=k) for k, v in ARM_COLOR.items()]
fig.legend(handles=patches, loc='lower center', ncol=2, fontsize=9,
           bbox_to_anchor=(0.5, -0.04))
plt.tight_layout(rect=[0, 0.08, 1, 1])
plt.savefig(f'{SAVE_DIR}fig11_arm_comparison_change.png', dpi=150, bbox_inches='tight')
plt.close()
print("Saved fig11_arm_comparison_change.png")

print("\nAll 11 figures saved to plots/")
