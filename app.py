"""
Student Marks Analyzer – Academic Performance Analysis System
Single-file version. Install and run:

    pip install streamlit pandas matplotlib plotly
    streamlit run app.py
"""
from __future__ import annotations

import html
import io
import re
import unicodedata
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402
import plotly.graph_objects as go  # noqa: E402
import streamlit as st  # noqa: E402

st.set_page_config(page_title="Student Marks Analyzer", page_icon="🎓", layout="wide", initial_sidebar_state="expanded")

# Auto-create a light theme config (applies from the next run onward)
try:
    _cfg = Path(__file__).resolve().parent / ".streamlit" / "config.toml"
    if not _cfg.exists():
        _cfg.parent.mkdir(exist_ok=True)
        _cfg.write_text(
            '[theme]\nbase = "light"\nprimaryColor = "#4F46E5"\nbackgroundColor = "#F5F7FB"\n'
            'secondaryBackgroundColor = "#FFFFFF"\ntextColor = "#1F2937"\n\n[browser]\ngatherUsageStats = false\n',
            encoding="utf-8",
        )
except Exception:  # noqa: BLE001
    pass

# ============================================================================
# CONSTANTS
# ============================================================================
META_COLUMNS = ["Register No", "Name", "Department", "Year", "Semester"]
RESULT_COLUMNS = ["Total", "Percentage", "Average", "Grade", "Status", "Rank"]
DEFAULT_SUBJECTS = ["Mathematics", "Python Programming", "Data Structures", "Machine Learning", "Database Systems"]
DEPARTMENTS = ["AI & DS", "CSE", "IT", "ECE", "EEE", "MECH", "CIVIL"]
GRADE_SCALE = [(90, "O"), (80, "A+"), (70, "A"), (60, "B+"), (50, "B"), (40, "C")]
GRADE_ORDER = ["O", "A+", "A", "B+", "B", "C", "F"]
GRADE_COLORS = {"O": "#4F46E5", "A+": "#7C3AED", "A": "#06B6D4", "B+": "#10B981", "B": "#84CC16", "C": "#F59E0B", "F": "#EF4444"}
PRIMARY, CYAN, GREEN, AMBER, RED, TEXT = "#4F46E5", "#06B6D4", "#10B981", "#F59E0B", "#EF4444", "#1F2937"
REG_PATTERN = re.compile(r"^[A-Za-z0-9]{5,20}$")
PAGES = ["📊  Dashboard", "➕  Add Marks", "🎓  Student Report", "🏆  Rankings & Search", "🗂️  Data Manager"]

SAMPLE_CSV = """Register No,Name,Department,Year,Semester,Mathematics,Python Programming,Data Structures,Machine Learning,Database Systems
24AD001,Aarav Kumar,AI & DS,2,3,92,95,88,90,85
24AD002,Priya Sharma,AI & DS,2,3,78,82,75,80,79
24AD003,Karthik Raja,AI & DS,2,3,65,70,62,58,66
24AD004,Divya Lakshmi,AI & DS,2,3,88,91,93,87,90
24AD005,Mohammed Irfan,AI & DS,2,3,55,60,48,52,58
24AD006,Sneha Reddy,AI & DS,2,3,72,68,74,70,77
24AD007,Vignesh Selvam,AI & DS,2,3,35,42,38,45,40
24AD008,Ananya Iyer,AI & DS,2,3,95,98,96,94,97
24AD009,Rahul Menon,AI & DS,2,3,60,55,58,62,50
24AD010,Meena Krishnan,AI & DS,2,3,82,79,85,83,80
24CS011,Harish Babu,CSE,2,3,70,74,66,72,68
24CS012,Nandhini Devi,CSE,2,3,58,64,61,59,63
24IT013,Surya Prakash,IT,2,3,44,50,41,47,52
24IT014,Keerthana Murugan,IT,2,3,85,80,89,84,86
24EC015,Arjun Nair,ECE,2,3,67,61,70,64,59
24EC016,Fathima Begum,ECE,2,3,38,45,50,42,55
"""

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html, body, .stApp, [class*="css"] { font-family: 'Inter', 'Segoe UI', sans-serif; }
.stApp { background: #F5F7FB; }
.block-container { padding-top: 1.5rem; padding-bottom: 3rem; max-width: 1400px; }
#MainMenu, footer { visibility: hidden; }
header[data-testid="stHeader"] { background: transparent; }
section[data-testid="stSidebar"] { background: #FFFFFF; border-right: 1px solid #E5E7EB; }
.brand { display: flex; align-items: center; gap: .75rem; padding: .25rem 0 1.1rem; }
.brand-logo { width: 44px; height: 44px; border-radius: 12px; font-size: 1.4rem; display: flex; align-items: center;
  justify-content: center; background: linear-gradient(135deg, #4F46E5, #06B6D4); box-shadow: 0 6px 16px rgba(79,70,229,.3); }
.brand-title { font-weight: 800; font-size: 1.1rem; color: #111827; line-height: 1.1; }
.brand-sub { font-size: .72rem; color: #6B7280; margin-top: 2px; }
.side-label { margin: 1.4rem 0 .4rem; font-size: .72rem; font-weight: 700; text-transform: uppercase; letter-spacing: .08em; color: #9CA3AF; }
.side-footer { margin-top: 1.5rem; font-size: .72rem; color: #9CA3AF; text-align: center; }
section[data-testid="stSidebar"] div[role="radiogroup"] { gap: .3rem; }
section[data-testid="stSidebar"] div[role="radiogroup"] > label { width: 100%; padding: .7rem .95rem; border-radius: 12px; cursor: pointer; transition: all .15s ease; }
section[data-testid="stSidebar"] div[role="radiogroup"] > label:hover { background: #EEF2FF; }
section[data-testid="stSidebar"] div[role="radiogroup"] > label > div:first-child { display: none; }
section[data-testid="stSidebar"] div[role="radiogroup"] > label p { font-weight: 600; font-size: .95rem; margin: 0; }
section[data-testid="stSidebar"] div[role="radiogroup"] > label:has(input:checked) { background: linear-gradient(135deg, #4F46E5, #6366F1); box-shadow: 0 6px 16px rgba(79,70,229,.28); }
section[data-testid="stSidebar"] div[role="radiogroup"] > label:has(input:checked) p { color: #FFFFFF !important; }
.hero { background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 55%, #06B6D4 100%); border-radius: 20px; padding: 1.6rem 1.9rem;
  margin-bottom: 1.25rem; color: #fff; box-shadow: 0 12px 30px rgba(79,70,229,.25); }
.hero-title { font-size: 1.75rem; font-weight: 800; line-height: 1.2; color: #fff; }
.hero-sub { margin-top: .35rem; font-size: .95rem; color: rgba(255,255,255,.85); }
.section-title { font-size: 1.1rem; font-weight: 700; color: #111827; margin: 1.5rem 0 .6rem; }
.kpi-card { background: #fff; border: 1px solid #E5E7EB; border-left: 5px solid var(--accent, #4F46E5); border-radius: 16px;
  padding: 1rem 1.15rem; min-height: 122px; height: 100%; box-shadow: 0 2px 10px rgba(17,24,39,.04); transition: transform .15s ease, box-shadow .15s ease; }
.kpi-card:hover { transform: translateY(-3px); box-shadow: 0 10px 24px rgba(17,24,39,.08); }
.kpi-top { display: flex; justify-content: space-between; align-items: center; gap: .5rem; }
.kpi-label { font-size: .74rem; font-weight: 700; text-transform: uppercase; letter-spacing: .05em; color: #6B7280; }
.kpi-icon { width: 34px; height: 34px; border-radius: 10px; font-size: 1rem; flex-shrink: 0; display: flex; align-items: center;
  justify-content: center; background: color-mix(in srgb, var(--accent, #4F46E5) 14%, white); }
.kpi-value { font-size: 1.65rem; font-weight: 800; color: #111827; margin-top: .4rem; line-height: 1.15; word-break: break-word; }
.kpi-sub { font-size: .8rem; color: #6B7280; margin-top: .25rem; }
.topper-strip { margin: 1rem 0 .25rem; padding: .85rem 1.1rem; border-radius: 14px; background: #FFFBEB; border: 1px solid #FDE68A; color: #92400E; font-size: .92rem; }
.profile-card { display: flex; align-items: center; gap: 1rem; padding: 1.1rem 1.3rem; margin: .6rem 0 1.1rem; background: #fff;
  border: 1px solid #E5E7EB; border-radius: 16px; box-shadow: 0 2px 10px rgba(17,24,39,.04); }
.avatar { width: 56px; height: 56px; border-radius: 16px; font-size: 1.5rem; font-weight: 800; color: #fff; display: flex;
  align-items: center; justify-content: center; flex-shrink: 0; background: linear-gradient(135deg, #4F46E5, #06B6D4); }
.profile-name { font-size: 1.25rem; font-weight: 800; color: #111827; }
.profile-meta { font-size: .88rem; color: #6B7280; margin-top: 2px; }
div[data-testid="stPlotlyChart"], div[data-testid="stDataFrame"], div[data-testid="stImage"], div[data-testid="stPyplotRootElement"] {
  background: #fff; border: 1px solid #E5E7EB; border-radius: 16px; padding: .5rem; box-shadow: 0 2px 10px rgba(17,24,39,.04); }
div[data-testid="stTabs"] button[role="tab"] { font-weight: 600; }
div[data-testid="stForm"] { background: #fff; border: 1px solid #E5E7EB; border-radius: 16px; padding: 1.2rem; }
.stButton > button, .stDownloadButton > button { border-radius: 10px; font-weight: 600; }
@media (max-width: 768px) {
  .block-container { padding-left: 1rem; padding-right: 1rem; }
  .hero { padding: 1.1rem 1.2rem; border-radius: 16px; }
  .hero-title { font-size: 1.35rem; }
  .kpi-value { font-size: 1.4rem; }
  .kpi-card { min-height: 100px; margin-bottom: .5rem; }
}
"""


# ============================================================================
# DATA LOGIC
# ============================================================================
def empty_dataset(subjects: list[str]) -> pd.DataFrame:
    data = {
        "Register No": pd.Series(dtype="object"),
        "Name": pd.Series(dtype="object"),
        "Department": pd.Series(dtype="object"),
        "Year": pd.Series(dtype="float64"),
        "Semester": pd.Series(dtype="float64"),
    }
    for s in subjects:
        data[s] = pd.Series(dtype="float64")
    return pd.DataFrame(data)


def get_subjects(df: pd.DataFrame) -> list[str]:
    return [c for c in df.columns if c not in META_COLUMNS and c not in RESULT_COLUMNS]


def normalize_dataset(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]
    subjects = get_subjects(df)
    df["Register No"] = df["Register No"].astype(str).str.strip().str.upper()
    df["Name"] = df["Name"].astype(str).str.strip()
    df["Department"] = df["Department"].astype(str).str.strip()
    df["Year"] = pd.to_numeric(df["Year"], errors="coerce").fillna(1).astype(int)
    df["Semester"] = pd.to_numeric(df["Semester"], errors="coerce").fillna(1).astype(int)
    for s in subjects:
        df[s] = pd.to_numeric(df[s], errors="coerce").fillna(0.0).astype(float)
    return df[META_COLUMNS + subjects].reset_index(drop=True)


def load_sample_data() -> pd.DataFrame:
    return normalize_dataset(pd.read_csv(io.StringIO(SAMPLE_CSV)))


def _clean(value) -> str:
    return "" if pd.isna(value) else str(value).strip()


def _to_int(value):
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if pd.isna(number) or number != int(number):
        return None
    return int(number)


def _valid_name(name: str) -> bool:
    if not 2 <= len(name) <= 60:
        return False
    for ch in name:
        if ch in " .'-":
            continue
        if unicodedata.category(ch)[0] not in ("L", "M"):  # letters + combining marks (Tamil/Hindi safe)
            return False
    return True


def validate_and_append(existing, new, subjects, max_marks):
    """Validate rows and append valid ones. Returns (dataframe, rows_added, errors)."""
    columns = META_COLUMNS + subjects
    new = new.copy().replace("", pd.NA).dropna(how="all")
    if new.empty:
        return existing, 0, ["No data to add. Please fill in at least one row."]

    seen = {str(r).upper() for r in existing["Register No"]} if not existing.empty else set()
    accepted, errors = [], []

    for position, (_, row) in enumerate(new.iterrows(), start=1):
        problems = []
        reg = _clean(row.get("Register No")).upper()
        name = _clean(row.get("Name"))
        dept = _clean(row.get("Department"))
        year = _to_int(row.get("Year"))
        sem = _to_int(row.get("Semester"))

        if not REG_PATTERN.match(reg):
            problems.append("register number must be 5–20 letters/digits (no spaces or symbols)")
        elif reg in seen:
            problems.append(f"register number {reg} already exists")
        if not _valid_name(name):
            problems.append("name must be 2–60 characters (letters, spaces, . ' - only)")
        if not dept:
            problems.append("department is required")
        if year is None or not 1 <= year <= 4:
            problems.append("year must be between 1 and 4")
        if sem is None or not 1 <= sem <= 8:
            problems.append("semester must be between 1 and 8")

        marks = {}
        for s in subjects:
            value = pd.to_numeric(row.get(s), errors="coerce")
            if pd.isna(value):
                problems.append(f"marks missing/invalid for {s}")
            elif value < 0 or value > max_marks:
                problems.append(f"{s} marks must be between 0 and {max_marks:g}")
            else:
                marks[s] = float(value)

        if problems:
            errors.append(f"{reg if reg else f'Row {position}'}: " + "; ".join(problems))
            continue
        seen.add(reg)
        accepted.append({"Register No": reg, "Name": name, "Department": dept, "Year": year, "Semester": sem, **marks})

    if not accepted:
        return existing, 0, errors
    added_df = pd.DataFrame(accepted, columns=columns)
    updated = added_df if existing.empty else pd.concat([existing[columns], added_df], ignore_index=True)
    return updated.reset_index(drop=True), len(accepted), errors


def import_csv(raw, current, mode, max_marks):
    raw = raw.copy()
    raw.columns = [str(c).strip() for c in raw.columns]
    missing = [c for c in META_COLUMNS if c not in raw.columns]
    if missing:
        return current, 0, [f"Missing required column(s): {', '.join(missing)}"]
    raw = raw.drop(columns=[c for c in RESULT_COLUMNS if c in raw.columns])
    new_subjects = get_subjects(raw)
    if not new_subjects:
        return current, 0, ["No subject columns found in the CSV."]
    if mode == "append":
        if set(new_subjects) != set(get_subjects(current)):
            return current, 0, ["Subject columns in the CSV do not match the current subjects. Use “Replace” instead."]
        base, subjects = current, get_subjects(current)
    else:
        base, subjects = empty_dataset(new_subjects), new_subjects
    updated, added, errors = validate_and_append(base, raw, subjects, max_marks)
    return (updated if added else current), added, errors


def grade_from_percentage(percentage: float) -> str:
    for threshold, grade in GRADE_SCALE:
        if percentage >= threshold:
            return grade
    return "F"


def compute_results(df, subjects, max_marks, pass_mark):
    res = df.copy()
    if res.empty or not subjects:
        for col in RESULT_COLUMNS:
            res[col] = pd.Series(dtype="object")
        return res
    marks = res[subjects].apply(pd.to_numeric, errors="coerce").fillna(0.0)
    res[subjects] = marks
    res["Total"] = marks.sum(axis=1)
    res["Percentage"] = (res["Total"] / (max_marks * len(subjects)) * 100).round(2)
    res["Average"] = marks.mean(axis=1).round(2)
    failed = (marks < pass_mark).any(axis=1)
    res["Status"] = ["Fail" if f else "Pass" for f in failed]
    res["Grade"] = ["F" if f else grade_from_percentage(p) for f, p in zip(failed, res["Percentage"])]
    res["Rank"] = res["Total"].rank(method="min", ascending=False).astype(int)
    return res


def class_summary(df, subjects, max_marks):
    hi, lo = df.loc[df["Total"].idxmax()], df.loc[df["Total"].idxmin()]
    passed = int((df["Status"] == "Pass").sum())
    return {
        "students": len(df), "passed": passed, "failed": len(df) - passed,
        "avg_pct": float(df["Percentage"].mean()), "pass_pct": passed / len(df) * 100,
        "highest_total": float(hi["Total"]), "highest_name": str(hi["Name"]),
        "lowest_total": float(lo["Total"]), "lowest_name": str(lo["Name"]),
        "max_total": max_marks * len(subjects),
    }


def subject_stats(df, subjects, max_marks, pass_mark):
    rows = []
    for s in subjects:
        col = df[s]
        rows.append({
            "Subject": s, "Average": round(float(col.mean()), 2), "Highest": float(col.max()), "Lowest": float(col.min()),
            "Average %": round(float(col.mean()) / max_marks * 100, 1), "Pass %": round(float((col >= pass_mark).mean() * 100), 1),
        })
    return pd.DataFrame(rows)


def student_report_frame(row, subjects, max_marks, pass_mark):
    rows = []
    for s in subjects:
        mark = float(row[s])
        pct = mark / max_marks * 100
        passed = mark >= pass_mark
        rows.append({
            "Subject": s, "Marks": mark, "Max Marks": float(max_marks), "Percentage": round(pct, 2),
            "Grade": grade_from_percentage(pct) if passed else "F", "Result": "Pass" if passed else "Fail",
        })
    return pd.DataFrame(rows)


def student_report_csv(row, frame, max_marks, subjects) -> bytes:
    overall = {
        "Subject": "OVERALL", "Marks": float(row["Total"]), "Max Marks": float(max_marks * len(subjects)),
        "Percentage": float(row["Percentage"]), "Grade": row["Grade"], "Result": row["Status"],
    }
    out = pd.concat([frame, pd.DataFrame([overall])], ignore_index=True)
    for i, col in enumerate(META_COLUMNS):
        out.insert(i, col, row[col])
    out["Class Rank"] = int(row["Rank"])
    return out.to_csv(index=False).encode("utf-8")


# ============================================================================
# CHARTS
# ============================================================================
def _style(fig, height=380, title=None):
    fig.update_layout(
        template="plotly_white", height=height,
        title=dict(text=title, x=0.01, font=dict(size=16, color=TEXT)) if title else None,
        font=dict(family="Inter, Segoe UI, sans-serif", color=TEXT),
        margin=dict(l=20, r=20, t=60 if title else 20, b=20),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(gridcolor="#E5E7EB")
    return fig


def fig_subject_bar(stats, max_marks):
    fig = go.Figure()
    for label, color in [("Highest", GREEN), ("Average", PRIMARY), ("Lowest", AMBER)]:
        fig.add_bar(x=stats["Subject"], y=stats[label], name=label, marker_color=color,
                    text=stats[label].round(0), textposition="outside", cliponaxis=False)
    fig.update_layout(barmode="group", bargap=0.25)
    fig.update_yaxes(range=[0, max_marks * 1.15], title="Marks")
    return _style(fig, 400, "Subject-wise Marks")


def fig_grade_pie(df):
    counts = df["Grade"].value_counts().reindex(GRADE_ORDER).fillna(0)
    counts = counts[counts > 0]
    fig = go.Figure(go.Pie(
        labels=counts.index, values=counts.values, hole=0.55, sort=False, textinfo="label+percent",
        marker=dict(colors=[GRADE_COLORS[g] for g in counts.index], line=dict(color="white", width=2)),
    ))
    fig.update_layout(legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5))
    return _style(fig, 400, "Grade Distribution")


def fig_student_line(df, class_avg):
    d = df.sort_values("Register No")
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=d["Register No"], y=d["Percentage"], mode="lines+markers", name="Student %",
        line=dict(color=PRIMARY, width=3, shape="spline"), marker=dict(size=9, color=PRIMARY, line=dict(color="white", width=2)),
        fill="tozeroy", fillcolor="rgba(79,70,229,0.08)", customdata=d[["Name", "Grade"]].values,
        hovertemplate="<b>%{customdata[0]}</b><br>Reg No: %{x}<br>Percentage: %{y:.1f}%<br>Grade: %{customdata[1]}<extra></extra>",
    ))
    fig.add_hline(y=class_avg, line_dash="dash", line_color=AMBER,
                  annotation_text=f"Class average {class_avg:.1f}%", annotation_position="top left")
    fig.update_yaxes(range=[0, 105], title="Percentage")
    fig.update_xaxes(title="Register number", type="category")
    return _style(fig, 380, "Student Performance (Percentage)")


def fig_student_vs_class(subjects, marks, class_avg, max_marks, name):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=subjects, y=list(marks.values), mode="lines+markers", name=name,
                             line=dict(color=PRIMARY, width=3), marker=dict(size=9)))
    fig.add_trace(go.Scatter(x=subjects, y=list(class_avg.values), mode="lines+markers", name="Class average",
                             line=dict(color=AMBER, width=3, dash="dash"), marker=dict(size=8)))
    fig.update_yaxes(range=[0, max_marks * 1.05], title="Marks")
    return _style(fig, 360, "Interactive: Student vs Class Average")


def _mpl_clean(ax):
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.spines["left"].set_color("#D1D5DB")
    ax.spines["bottom"].set_color("#D1D5DB")
    ax.tick_params(colors=TEXT, labelsize=9)
    ax.yaxis.grid(True, color="#E5E7EB")
    ax.set_axisbelow(True)


def mpl_percentage_hist(df):
    fig, ax = plt.subplots(figsize=(6, 3.9))
    bins = [0, 40, 50, 60, 70, 80, 90, 100]
    ax.hist(df["Percentage"], bins=bins, color=PRIMARY, edgecolor="white", rwidth=0.92)
    ax.set_xticks(bins)
    ax.set_xlabel("Percentage range", color=TEXT)
    ax.set_ylabel("Number of students", color=TEXT)
    ax.set_title("Score Distribution (Matplotlib)", loc="left", fontsize=12, fontweight="bold", color=TEXT)
    ax.yaxis.get_major_locator().set_params(integer=True)
    _mpl_clean(ax)
    fig.tight_layout()
    return fig


def mpl_student_bar(subjects, marks, class_avg, max_marks):
    fig, ax = plt.subplots(figsize=(6, 3.9))
    x, width = range(len(subjects)), 0.38
    ax.bar([i - width / 2 for i in x], list(marks.values), width, label="Student", color=PRIMARY)
    ax.bar([i + width / 2 for i in x], list(class_avg.values), width, label="Class average", color=AMBER)
    ax.set_xticks(list(x))
    ax.set_xticklabels([s.replace(" ", "\n", 1) for s in subjects], fontsize=8)
    ax.set_ylim(0, max_marks * 1.1)
    ax.set_ylabel("Marks", color=TEXT)
    ax.set_title("Subject Comparison (Matplotlib)", loc="left", fontsize=12, fontweight="bold", color=TEXT)
    ax.legend(frameon=False, fontsize=9)
    _mpl_clean(ax)
    fig.tight_layout()
    return fig


# ============================================================================
# UI HELPERS
# ============================================================================
def init_state():
    if "df" not in st.session_state:
        st.session_state.df = load_sample_data()
    st.session_state.setdefault("single_ver", 0)
    st.session_state.setdefault("bulk_ver", 0)


def flash(kind, message):
    st.session_state.setdefault("flash", []).append((kind, message))


def show_flash():
    funcs = {"success": st.success, "warning": st.warning, "error": st.error, "info": st.info}
    for kind, message in st.session_state.pop("flash", []):
        funcs.get(kind, st.info)(message)


def page_header(title, subtitle):
    st.markdown(
        f'<div class="hero"><div class="hero-title">{html.escape(title)}</div>'
        f'<div class="hero-sub">{html.escape(subtitle)}</div></div>', unsafe_allow_html=True)


def section(title):
    st.markdown(f'<div class="section-title">{html.escape(title)}</div>', unsafe_allow_html=True)


def kpi_card(label, value, sub="", accent="#4F46E5", icon=""):
    st.markdown(
        f'<div class="kpi-card" style="--accent:{accent}">'
        f'<div class="kpi-top"><div class="kpi-label">{html.escape(label)}</div><div class="kpi-icon">{icon}</div></div>'
        f'<div class="kpi-value">{html.escape(str(value))}</div><div class="kpi-sub">{html.escape(sub)}</div></div>',
        unsafe_allow_html=True)


def empty_state():
    st.info("No student records yet. Add students from **➕ Add Marks** or load sample data from **🗂️ Data Manager**.")


def commit_students(new_df, subjects, max_marks) -> int:
    updated, added, errors = validate_and_append(st.session_state.df, new_df, subjects, max_marks)
    if added:
        st.session_state.df = updated
        flash("success", f"✅ Added {added} student record(s) successfully.")
    if errors:
        bullets = "\n".join(f"- {e}" for e in errors[:15])
        more = f"\n- …and {len(errors) - 15} more issue(s)." if len(errors) > 15 else ""
        flash("warning", f"Skipped {len(errors)} issue(s):\n{bullets}{more}")
    return added


PROGRESS = st.column_config.ProgressColumn


# ============================================================================
# PAGES
# ============================================================================
def page_dashboard(res, subjects, max_marks, pass_mark):
    page_header("Performance Dashboard", "Class-wide academic insights at a glance")
    if res.empty:
        empty_state()
        return

    f1, _ = st.columns([1, 3])
    dept = f1.selectbox("Filter by department", ["All"] + sorted(res["Department"].unique().tolist()))
    view = res if dept == "All" else res[res["Department"] == dept]
    sm = class_summary(view, subjects, max_marks)

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        kpi_card("Total Students", sm["students"], f"{sm['passed']} passed • {sm['failed']} failed", "#4F46E5", "👥")
    with c2:
        kpi_card("Class Average", f"{sm['avg_pct']:.1f}%", f"Out of {sm['max_total']:.0f} marks total", "#06B6D4", "📈")
    with c3:
        kpi_card("Pass Percentage", f"{sm['pass_pct']:.1f}%", "Passed in all subjects", "#10B981", "✅")
    with c4:
        kpi_card("Highest Marks", f"{sm['highest_total']:.0f}", sm["highest_name"], "#F59E0B", "🏅")
    with c5:
        kpi_card("Lowest Marks", f"{sm['lowest_total']:.0f}", sm["lowest_name"], "#EF4444", "📉")

    toppers = view[view["Total"] == view["Total"].max()]["Name"].tolist()
    st.markdown(
        f'<div class="topper-strip">🏆 <b>Class topper{"s" if len(toppers) > 1 else ""}:</b> '
        f'{html.escape(", ".join(toppers))} &nbsp;•&nbsp; {sm["highest_total"]:.0f} / {sm["max_total"]:.0f} marks</div>',
        unsafe_allow_html=True)

    stats = subject_stats(view, subjects, max_marks, pass_mark)
    section("Subject-wise & Grade Analysis")
    a, b = st.columns([3, 2])
    a.plotly_chart(fig_subject_bar(stats, max_marks), width="stretch")
    b.plotly_chart(fig_grade_pie(view), width="stretch")

    section("Student Performance")
    st.plotly_chart(fig_student_line(view, sm["avg_pct"]), width="stretch")

    section("Subject Statistics & Score Distribution")
    c, d = st.columns([3, 2])
    with c:
        st.dataframe(stats, hide_index=True, width="stretch",
                     column_config={"Pass %": PROGRESS("Pass %", min_value=0, max_value=100, format="%.1f%%")})
    with d:
        fig = mpl_percentage_hist(view)
        st.pyplot(fig)
        plt.close(fig)


def page_add(subjects, max_marks):
    page_header("Add Marks", "Enter one student, many students at once, or import a CSV")
    show_flash()
    departments = sorted(set(DEPARTMENTS) | set(st.session_state.df["Department"].astype(str)))
    tab1, tab2, tab3 = st.tabs(["👤 Single student", "👥 Multiple students", "📤 Upload CSV"])

    with tab1:
        v = st.session_state.single_ver
        with st.form(f"single_form_{v}"):
            c1, c2 = st.columns(2)
            name = c1.text_input("Student name", key=f"name_{v}", placeholder="e.g. Sivadeepika")
            reg = c2.text_input("Register number", key=f"reg_{v}", placeholder="e.g. 24AD017")
            c3, c4, c5 = st.columns(3)
            dept = c3.selectbox("Department", departments, key=f"dept_{v}")
            year = c4.selectbox("Year", [1, 2, 3, 4], index=1, key=f"year_{v}")
            sem = c5.selectbox("Semester", list(range(1, 9)), index=2, key=f"sem_{v}")
            st.markdown(f"**Marks** (0 – {max_marks:g} per subject)")
            cols = st.columns(min(3, max(1, len(subjects))))
            marks = {}
            for i, s in enumerate(subjects):
                marks[s] = cols[i % len(cols)].number_input(
                    s, min_value=0.0, max_value=float(max_marks), value=0.0, step=1.0, key=f"m_{s}_{v}")
            submitted = st.form_submit_button("Add student", type="primary", width="stretch")
        if submitted:
            record = {"Register No": reg, "Name": name, "Department": dept, "Year": year, "Semester": sem, **marks}
            if commit_students(pd.DataFrame([record]), subjects, max_marks):
                st.session_state.single_ver += 1
            st.rerun()

    with tab2:
        st.caption("Click the empty bottom row to add students. Select rows to delete them.")
        config = {
            "Register No": st.column_config.TextColumn("Register No"),
            "Name": st.column_config.TextColumn("Name"),
            "Department": st.column_config.SelectboxColumn("Department", options=departments),
            "Year": st.column_config.NumberColumn("Year", min_value=1, max_value=4, step=1, format="%d"),
            "Semester": st.column_config.NumberColumn("Semester", min_value=1, max_value=8, step=1, format="%d"),
        }
        for s in subjects:
            config[s] = st.column_config.NumberColumn(s, min_value=0, max_value=float(max_marks), step=1)
        edited = st.data_editor(empty_dataset(subjects), num_rows="dynamic", width="stretch", hide_index=True,
                                column_config=config, key=f"bulk_{st.session_state.bulk_ver}")
        if st.button("Add all rows", type="primary", key="bulk_add"):
            if commit_students(edited, subjects, max_marks):
                st.session_state.bulk_ver += 1
            st.rerun()

    with tab3:
        st.caption("Required columns: Register No, Name, Department, Year, Semester + one column per subject.")
        st.download_button("⬇️ Download CSV template", empty_dataset(subjects).to_csv(index=False).encode("utf-8"),
                           file_name="marks_template.csv", mime="text/csv")
        uploaded = st.file_uploader("Upload a CSV file", type=["csv"])
        mode_label = st.radio("Import mode", ["Append to current data", "Replace current data"], horizontal=True)
        if st.button("Import CSV", type="primary", disabled=uploaded is None):
            try:
                raw = pd.read_csv(uploaded)
            except Exception as exc:  # noqa: BLE001
                st.error(f"Could not read the file: {exc}")
            else:
                mode = "append" if mode_label.startswith("Append") else "replace"
                updated, added, errors = import_csv(raw, st.session_state.df, mode, max_marks)
                if added:
                    st.session_state.df = updated
                    flash("success", f"✅ Imported {added} student record(s).")
                if errors:
                    flash("warning", f"Skipped {len(errors)} issue(s):\n" + "\n".join(f"- {e}" for e in errors[:15]))
                st.rerun()


def page_report(res, subjects, max_marks, pass_mark):
    page_header("Student Report", "Individual performance with subject-wise marks and grades")
    if res.empty:
        empty_state()
        return

    query = st.text_input("🔍 Search by register number", placeholder="e.g. 24AD001").strip()
    pool = res if not query else res[res["Register No"].str.contains(query, case=False, regex=False)]
    if pool.empty:
        st.warning(f"No student found with register number containing “{query}”.")
        return

    names = dict(zip(pool["Register No"], pool["Name"]))
    reg = st.selectbox("Select student", pool["Register No"].tolist(), format_func=lambda r: f"{r} — {names[r]}")
    row = res[res["Register No"] == reg].iloc[0]

    st.markdown(
        f'<div class="profile-card"><div class="avatar">{html.escape(str(row["Name"])[:1].upper())}</div>'
        f'<div><div class="profile-name">{html.escape(str(row["Name"]))}</div>'
        f'<div class="profile-meta">Reg No: <b>{html.escape(str(row["Register No"]))}</b> &nbsp;•&nbsp; '
        f'{html.escape(str(row["Department"]))} &nbsp;•&nbsp; Year {int(row["Year"])} / Semester {int(row["Semester"])}</div></div></div>',
        unsafe_allow_html=True)

    passed = row["Status"] == "Pass"
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        kpi_card("Total Marks", f"{row['Total']:.0f}", f"out of {max_marks * len(subjects):.0f}", "#4F46E5", "🧮")
    with c2:
        kpi_card("Percentage", f"{row['Percentage']:.1f}%", f"Average {row['Average']:.1f}", "#06B6D4", "📊")
    with c3:
        kpi_card("Grade", row["Grade"], "Overall grade", "#7C3AED", "🎖️")
    with c4:
        kpi_card("Result", row["Status"], "Pass in all subjects" if passed else "Failed in one or more",
                 "#10B981" if passed else "#EF4444", "✅" if passed else "⚠️")
    with c5:
        kpi_card("Class Rank", f"#{int(row['Rank'])}", f"of {len(res)} students", "#F59E0B", "🏆")

    report = student_report_frame(row, subjects, max_marks, pass_mark)
    class_avg = res[subjects].mean().round(2)

    section("Subject-wise Marks & Grades")
    shown = report.copy()
    shown["Result"] = shown["Result"].map({"Pass": "✅ Pass", "Fail": "❌ Fail"})
    st.dataframe(shown, hide_index=True, width="stretch",
                 column_config={"Percentage": PROGRESS("Percentage", min_value=0, max_value=100, format="%.1f%%")})

    section("Performance vs Class Average")
    a, b = st.columns(2)
    a.plotly_chart(fig_student_vs_class(subjects, row[subjects].astype(float), class_avg, max_marks, str(row["Name"])), width="stretch")
    with b:
        fig = mpl_student_bar(subjects, row[subjects].astype(float), class_avg, max_marks)
        st.pyplot(fig)
        plt.close(fig)

    st.download_button("⬇️ Download student report (CSV)", student_report_csv(row, report, max_marks, subjects),
                       file_name=f"report_{row['Register No']}.csv", mime="text/csv", type="primary")


def page_rankings(res, subjects):
    page_header("Rankings & Search", "Find students, sort by total marks and spot the toppers")
    if res.empty:
        empty_state()
        return

    section("Class Toppers")
    medals, accents = ["🥇", "🥈", "🥉"], ["#F59E0B", "#94A3B8", "#B45309"]
    top3 = res.sort_values(["Total", "Name"], ascending=[False, True]).head(3)
    for i, (col, (_, r)) in enumerate(zip(st.columns(3), top3.iterrows())):
        with col:
            kpi_card(f"{medals[i]} Rank {int(r['Rank'])}", r["Name"],
                     f"{r['Total']:.0f} marks • {r['Percentage']:.1f}% • Grade {r['Grade']}", accents[i], "🎓")

    section("Search & Sort")
    c1, c2, c3, c4 = st.columns([2, 2, 1.5, 1.5])
    query = c1.text_input("🔍 Search by register number", placeholder="e.g. 24AD0").strip()
    sort_by = c2.selectbox("Sort by", ["Total", "Percentage", "Name", "Register No"])
    order = c3.radio("Order", ["High → Low", "Low → High"])
    status = c4.selectbox("Status", ["All", "Pass", "Fail"])

    view = res.copy()
    if query:
        view = view[view["Register No"].str.contains(query, case=False, regex=False)]
    if status != "All":
        view = view[view["Status"] == status]
    view = view.sort_values(sort_by, ascending=order.startswith("Low"))

    if view.empty:
        st.warning("No students match your search.")
        return

    cols_show = ["Rank", "Register No", "Name", "Department"] + subjects + ["Total", "Percentage", "Grade", "Status"]
    st.caption(f"Showing {len(view)} of {len(res)} students")
    st.dataframe(view[cols_show], hide_index=True, width="stretch",
                 column_config={"Percentage": PROGRESS("Percentage", min_value=0, max_value=100, format="%.1f%%")})
    st.download_button("⬇️ Download this table (CSV)", view[cols_show].to_csv(index=False).encode("utf-8"),
                       file_name="ranked_students.csv", mime="text/csv")


def page_data(res, subjects, max_marks):
    page_header("Data Manager", "Load sample data, remove records and export everything")
    show_flash()

    section("Sample data")
    c1, c2, c3 = st.columns(3)
    if c1.button("Load sample data (replace all)", width="stretch"):
        st.session_state.df = load_sample_data()
        flash("success", "Sample data loaded.")
        st.rerun()
    if c2.button("Append sample students", width="stretch"):
        sample = load_sample_data()
        if set(get_subjects(sample)) != set(subjects):
            flash("error", "Sample subjects do not match the current subjects. Use “replace all” instead.")
        else:
            commit_students(sample, subjects, max_marks)
        st.rerun()
    if c3.button("Clear all records", width="stretch"):
        st.session_state.df = empty_dataset(subjects)
        flash("info", "All student records were removed.")
        st.rerun()

    if res.empty:
        empty_state()
        return

    section("Delete students")
    labels = {r["Register No"]: f"{r['Register No']} — {r['Name']}" for _, r in res.iterrows()}
    to_delete = st.multiselect("Select students to delete", list(labels), format_func=lambda k: labels[k])
    if st.button("Delete selected", disabled=not to_delete):
        df = st.session_state.df
        st.session_state.df = df[~df["Register No"].isin(to_delete)].reset_index(drop=True)
        flash("success", f"Deleted {len(to_delete)} record(s).")
        st.rerun()

    section("Full dataset with results")
    st.dataframe(res, hide_index=True, width="stretch",
                 column_config={"Percentage": PROGRESS("Percentage", min_value=0, max_value=100, format="%.1f%%")})
    st.download_button("⬇️ Download full results (CSV)", res.to_csv(index=False).encode("utf-8"),
                       file_name="student_results.csv", mime="text/csv", type="primary")


# ============================================================================
# MAIN
# ============================================================================
def main():
    st.markdown(f"<style>{CSS}</style>", unsafe_allow_html=True)
    init_state()

    with st.sidebar:
        st.markdown(
            '<div class="brand"><div class="brand-logo">🎓</div><div><div class="brand-title">Marks Analyzer</div>'
            '<div class="brand-sub">Academic Performance System</div></div></div>', unsafe_allow_html=True)
        page = st.radio("Navigation", PAGES, label_visibility="collapsed")
        st.markdown('<div class="side-label">Grading settings</div>', unsafe_allow_html=True)
        max_marks = st.number_input("Maximum marks per subject", min_value=10, max_value=1000, value=100, step=5)
        pass_pct = st.number_input("Pass mark per subject (%)", min_value=1, max_value=100, value=40, step=1)
        pass_mark = max_marks * pass_pct / 100
        with st.expander("Grade scale"):
            st.markdown(
                "| Percentage | Grade |\n|---|---|\n| 90 – 100 | O |\n| 80 – 89 | A+ |\n| 70 – 79 | A |\n"
                "| 60 – 69 | B+ |\n| 50 – 59 | B |\n| 40 – 49 | C |\n| Below 40 / any subject failed | F |")
        st.markdown('<div class="side-footer">Built with Streamlit • Pandas • Plotly</div>', unsafe_allow_html=True)

    df = st.session_state.df
    subjects = get_subjects(df)
    res = compute_results(df, subjects, max_marks, pass_mark)

    if subjects and not df.empty and (df[subjects] > max_marks).any().any():
        st.warning("Some stored marks exceed the maximum marks set in the sidebar. Increase the maximum or fix the data.")

    if page == PAGES[0]:
        show_flash()
        page_dashboard(res, subjects, max_marks, pass_mark)
    elif page == PAGES[1]:
        page_add(subjects, max_marks)
    elif page == PAGES[2]:
        show_flash()
        page_report(res, subjects, max_marks, pass_mark)
    elif page == PAGES[3]:
        show_flash()
        page_rankings(res, subjects)
    else:
        page_data(res, subjects, max_marks)


main()
