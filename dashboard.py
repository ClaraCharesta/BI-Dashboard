import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="BI Dashboard Kematian Indonesia",
    page_icon="📊",
    layout="wide"
)

# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown("""
<style>

html, body, [class*="css"] {
    font-family: 'Segoe UI', sans-serif;
}

/* ======================================================
BACKGROUND
====================================================== */

.stApp {
    background: linear-gradient(
        180deg,
        #F4F9FF 0%,
        #E0F2FE 100%
    );
}

/* ======================================================
SIDEBAR
====================================================== */

section[data-testid="stSidebar"] {
    background: linear-gradient(
        180deg,
        #60A5FA 0%,
        #93C5FD 50%,
        #BFDBFE 100%
    );
    border-right: 2px solid #93C5FD;
}

section[data-testid="stSidebar"] * {
    color: #0F172A !important;
    font-weight: 500;
}

/* ======================================================
TITLE
====================================================== */

.title-style {
    font-size: 42px;
    font-weight: 800;
    color: #0F172A;
    margin-bottom: 5px;
}

.subtitle-style {
    color: #334155;
    font-size: 17px;
    margin-bottom: 20px;
}

/* ======================================================
KPI CARD (FIXED HEIGHT + ALIGN)
====================================================== */

.kpi-card {
    background: linear-gradient(135deg, #2563EB, #3B82F6);
    padding: 22px;
    border-radius: 24px;
    box-shadow: 0px 8px 24px rgba(37,99,235,0.25);
    color: white;
    transition: 0.3s;

    /* 🔥 FIX UTAMA */
    height: 140px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    text-align: center;
    overflow: hidden;
}

.kpi-card:hover {
    transform: translateY(-5px);
    box-shadow: 0px 12px 28px rgba(37,99,235,0.35);
}

.kpi-title {
    font-size: 15px;
    font-weight: 600;
    opacity: 0.9;
}

.kpi-value {
    font-size: clamp(16px, 2vw, 34px);
    font-weight: bold;
    margin-top: 10px;
    line-height: 1.2;
    text-align: center;
}

/* ======================================================
CHART CARD
====================================================== */

.chart-card {
    background: white;
    padding: 20px;
    border-radius: 24px;
    box-shadow: 0px 6px 18px rgba(0,0,0,0.08);
    margin-bottom: 22px;
    border: 1px solid #BFDBFE;
}

/* ======================================================
INSIGHT BOX
====================================================== */

.insight-box {
    background: linear-gradient(135deg, #1D4ED8, #60A5FA);
    padding: 25px;
    border-radius: 22px;
    color: white;
    font-size: 16px;
    font-weight: 500;
    box-shadow: 0px 8px 20px rgba(59,130,246,0.25);
}

/* ======================================================
STREAMLIT METRIC
====================================================== */

div[data-testid="metric-container"] {
    background: white;
    border-radius: 20px;
    padding: 18px;
    border: 1px solid #DBEAFE;
    box-shadow: 0px 4px 10px rgba(0,0,0,0.05);
}

/* ======================================================
TABLE
====================================================== */

[data-testid="stDataFrame"] {
    background: white;
    border-radius: 18px;
    padding: 10px;
}

/* ======================================================
BUTTON
====================================================== */

.stButton>button {
    background: linear-gradient(135deg, #2563EB, #1D4ED8);
    color: white;
    border: none;
    border-radius: 12px;
    padding: 10px 18px;
    font-weight: 600;
}

.stButton>button:hover {
    background: linear-gradient(135deg, #1D4ED8, #1E40AF);
    color: white;
}

/* ======================================================
SELECTBOX
====================================================== */

section[data-testid="stSidebar"] div[data-baseweb="select"] {
    background-color: white;
    border-radius: 12px;
}

/* ======================================================
SCROLLBAR
====================================================== */

::-webkit-scrollbar {
    width: 10px;
}

::-webkit-scrollbar-thumb {
    background: #3B82F6;
    border-radius: 10px;
}

::-webkit-scrollbar-track {
    background: #DBEAFE;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# MYSQL CONNECTION
# =========================================================

username = "root"
password = ""
host = "localhost"
database = "bi_kematian"

engine = create_engine(
    f"mysql+pymysql://{username}:{password}@{host}/{database}"
)

# =========================================================
# LOAD DATA
# =========================================================

query = """
SELECT 
    fd.total_deaths,
    dc.cause_name,
    dy.year,
    dt.type_name
FROM fact_deaths fd
JOIN dim_cause dc
    ON fd.cause_id = dc.cause_id
JOIN dim_year dy
    ON fd.year_id = dy.year_id
JOIN dim_type dt
    ON fd.type_id = dt.type_id
"""

df = pd.read_sql(query, engine)

# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.markdown("## 📊 Dashboard Filter")
    st.markdown("---")

    st.info(
        f"""
        📌 Total Data : {len(df):,}

        📅 Tahun Tersedia : {df['year'].min()} - {df['year'].max()}

        🩺 Total Kategori : {df['type_name'].nunique()}
        """
    )

    st.markdown("### 📅 Filter Tahun")

    min_year = int(df["year"].min())
    max_year = int(df["year"].max())

    year_range = st.slider(
        "Rentang Tahun",
        min_value=min_year,
        max_value=max_year,
        value=(min_year, max_year)
    )

    st.markdown("### 🩺 Filter Kategori")

    selected_type = st.multiselect(
        "Pilih Kategori Penyebab",
        sorted(df["type_name"].unique()),
        default=sorted(df["type_name"].unique())
    )

    


filtered_df = df[
    (df["year"] >= year_range[0]) &
    (df["year"] <= year_range[1]) &
    (df["type_name"].isin(selected_type))
]




# =========================================================
# HEADER
# =========================================================

st.markdown("""
<div class="title-style">
📊 Dashboard BI Kematian Indonesia
</div>

<div class="subtitle-style">
Analisis penyebab kematian di Indonesia berbasis Business Intelligence 
untuk mendukung pengambilan keputusan sektor kesehatan.
</div>
""", unsafe_allow_html=True)

st.write("")

# =========================================================
# HANDLE EMPTY DATA
# =========================================================

if filtered_df.empty:
    st.warning("⚠️ Tidak ada data berdasarkan filter.")
    st.stop()

# =========================================================
# KPI
# =========================================================

total_deaths = int(filtered_df["total_deaths"].sum())

year_group = filtered_df.groupby("year")["total_deaths"].sum()

highest_year = year_group.idxmax() if not year_group.empty else "-"

cause_group = filtered_df.groupby("cause_name")["total_deaths"].sum()

top_cause = cause_group.idxmax() if not cause_group.empty else "-"

avg_deaths = int(filtered_df["total_deaths"].mean())

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">💀 Total Kematian</div>
        <div class="kpi-value">{total_deaths:,}</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">📅 Tahun Tertinggi</div>
        <div class="kpi-value">{highest_year}</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">⚠️ Penyebab Dominan</div>
        <div class="kpi-value">{top_cause}</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">📊 Rata-rata Kematian</div>
        <div class="kpi-value">{avg_deaths:,}</div>
    </div>
    """, unsafe_allow_html=True)

st.write("")

# =========================================================
# ROW 1
# =========================================================

st.markdown('<div class="chart-card">', unsafe_allow_html=True)

st.subheader("📈 Tren Kematian per Tahun")

year_chart = (
    filtered_df.groupby("year")["total_deaths"]
    .sum()
    .reset_index()
)

fig1 = px.line(
    year_chart,
    x="year",
    y="total_deaths",
    markers=True,
    color_discrete_sequence=["#4F46E5"]
)

fig1.update_layout(
    plot_bgcolor='white',
    paper_bgcolor='white'
)

st.plotly_chart(fig1, use_container_width=True)

st.markdown('</div>', unsafe_allow_html=True)


st.markdown('<div class="chart-card">', unsafe_allow_html=True)

st.subheader("🩺 Distribusi Kategori")

type_chart = (
    filtered_df.groupby("type_name")["total_deaths"]
    .sum()
    .reset_index()
    .sort_values(by="total_deaths", ascending=True)
)

if not type_chart.empty:

    fig2 = px.bar(
        type_chart,
        x="total_deaths",
        y="type_name",
        orientation="h",
        text="total_deaths",
        color="total_deaths",
        color_continuous_scale="Blues"
    )

    fig2.update_traces(
        texttemplate='%{text:,}',
        textposition='outside'
    )

    fig2.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        xaxis_title="Total Kematian",
        yaxis_title="Kategori Penyebab",
        coloraxis_showscale=False,
        margin=dict(l=120, r=40, t=40, b=40)
    )

    st.plotly_chart(fig2, use_container_width=True)
else:
    st.info("Tidak ada data kategori.")

# =========================================================
# ROW 2
# =========================================================

st.markdown('<div class="chart-card">', unsafe_allow_html=True)

st.subheader("🔥 Top 10 Penyebab Kematian")

top10 = (
    filtered_df.groupby("cause_name")["total_deaths"]
    .sum()
    .reset_index()
    .sort_values(by="total_deaths", ascending=False)
    .head(10)
)

if not top10.empty:

    fig3 = px.bar(
        top10,
        x="total_deaths",
        y="cause_name",
        orientation="h",
        color="total_deaths",
        color_continuous_scale="Purples"
    )

    fig3.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white'
    )

    st.plotly_chart(fig3, use_container_width=True)

else:
    st.info("Tidak ada data penyebab kematian.")

st.markdown('</div>', unsafe_allow_html=True)


st.markdown('<div class="chart-card">', unsafe_allow_html=True)

st.subheader("🌳 Distribusi Penyebab")

def classify_type(x):
    x = str(x).lower()

    # 🌋 Alam
    if any(k in x for k in [
        "gempa", "tsunami", "banjir", "longsor", "gunung", "erupsi",
        "angin", "topan", "petir"
    ]):
        return "🌋 Bencana Alam"

    # ⚠️ Sosial / External cause (INI YANG DIPERLUAS)
    elif any(k in x for k in [
        "kecelakaan", "transport", "tabrakan", "jatuh",
        "keracunan", "overdosis", "bunuh", "kekerasan",
        "kriminal", "serangan", "trauma"
    ]):
        return "⚠️ Bencana Sosial"

    # 🧬 Penyakit
    else:
        return "🧬 Non-Alam (Penyakit)"

# =========================
# ADD CATEGORY COLUMN
# =========================
filtered_df = filtered_df.copy()
filtered_df["category"] = filtered_df["type_name"].apply(classify_type)

# =========================
# GROUP DATA (FIXED)
# =========================
tree = (
    filtered_df.groupby(
        ["category", "type_name", "cause_name"]
    )["total_deaths"]
    .sum()
    .reset_index()
)

# =========================
# TREEMAP
# =========================
if not tree.empty:

    fig4 = px.treemap(
    tree,
    path=["category", "type_name", "cause_name"],
    values="total_deaths",
    color="category",
    color_discrete_map={
        "🌋 Bencana Alam": "#EF4444",
        "⚠️ Bencana Sosial": "#F59E0B",
        "🧬 Non-Alam (Penyakit)": "#3B82F6"
    }
)

    fig4.update_traces(
        textinfo="label+value+percent entry"
    )

    fig4.update_layout(
        margin=dict(t=30, l=10, r=10, b=10),
        paper_bgcolor="white"
    )

    st.plotly_chart(fig4, use_container_width=True)

else:
    st.info("Tidak ada data distribusi.")

# =========================================================
# FEATURE 1
# SMART INSIGHT
# =========================================================

st.subheader("🧠 Smart Insight")

trend = (
    year_chart["total_deaths"]
    .pct_change()
    .mean()
)

if pd.isna(trend):
    insight = """
    Data belum cukup untuk menganalisis tren kematian.
    """
elif trend > 0:
    insight = """
    Terjadi kecenderungan peningkatan jumlah kematian dari tahun ke tahun.
    Pemerintah perlu meningkatkan upaya preventif terhadap penyebab kematian dominan.
    """
else:
    insight = """
    Terjadi penurunan jumlah kematian secara umum.
    Hal ini dapat menunjukkan efektivitas kebijakan kesehatan nasional.
    """

st.markdown(f"""
<div class="insight-box">
{insight}
</div>
""", unsafe_allow_html=True)

st.write("")

# =========================================================
# FEATURE 2
# GROWTH ANALYSIS
# =========================================================

st.markdown('<div class="chart-card">', unsafe_allow_html=True)

st.subheader("📊 Pertumbuhan Kematian Tahunan")

growth = year_chart.copy()

growth["growth_percent"] = (
    growth["total_deaths"]
    .pct_change() * 100
)

fig5 = px.area(
    growth,
    x="year",
    y="growth_percent",
    color_discrete_sequence=["#7C3AED"]
)

fig5.update_layout(
    plot_bgcolor='white',
    paper_bgcolor='white'
)

st.plotly_chart(fig5, use_container_width=True)

st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# FEATURE 3
# CATEGORY COMPARISON
# =========================================================

st.markdown('<div class="chart-card">', unsafe_allow_html=True)

st.subheader("⚖️ Perbandingan Kategori per Tahun")

stacked = (
    filtered_df.groupby(
        ["year", "type_name"]
    )["total_deaths"]
    .sum()
    .reset_index()
)

if not stacked.empty:

    fig6 = px.bar(
        stacked,
        x="year",
        y="total_deaths",
        color="type_name",
        barmode="stack",
        color_discrete_sequence=px.colors.qualitative.Set2
    )

    fig6.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white'
    )

    st.plotly_chart(fig6, use_container_width=True)

else:
    st.info("Tidak ada data perbandingan kategori.")

st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# FEATURE 4
# RISK SIMULATION
# =========================================================

st.markdown('<div class="chart-card">', unsafe_allow_html=True)

st.subheader("📌 Simulasi Risiko Penyebab Kematian")

available_causes = sorted(
    filtered_df["cause_name"].dropna().unique()
)

if available_causes:

    selected_cause = st.selectbox(
        "Pilih Penyebab",
        available_causes
    )

    sim_data = (
        filtered_df[
            filtered_df["cause_name"] == selected_cause
        ]
        .groupby("year")["total_deaths"]
        .sum()
        .reset_index()
    )

    if not sim_data.empty:

        avg = int(sim_data["total_deaths"].mean())

        st.warning(
            f"Rata-rata kematian akibat {selected_cause} adalah {avg:,} kasus per tahun."
        )

        fig7 = px.line(
            sim_data,
            x="year",
            y="total_deaths",
            markers=True,
            color_discrete_sequence=["#EF4444"]
        )

        fig7.update_layout(
            plot_bgcolor="white",
            paper_bgcolor="white"
        )

        st.plotly_chart(
            fig7,
            use_container_width=True,
            key=f"risk_simulation_{selected_cause}"
        )

else:
    st.info("Tidak ada penyebab kematian pada kategori yang dipilih.")

st.markdown('</div>', unsafe_allow_html=True)



# =========================================================
# FEATURE 6
# SMART RECOMMENDATION ENGINE (UPGRADED)
# =========================================================

st.markdown('<div class="chart-card">', unsafe_allow_html=True)

st.subheader("💡 Smart Recommendation Engine")

# =========================================================
# 1. TOP CAUSE ANALYSIS
# =========================================================

top_cause_value = cause_group.max() if not cause_group.empty else 0
top_cause_name = cause_group.idxmax() if not cause_group.empty else "-"

# =========================================================
# 2. TREND ANALYSIS
# =========================================================

trend_value = (
    year_chart["total_deaths"].pct_change().mean()
)

# =========================================================
# 3. EARLY WARNING (TOP 5)
# =========================================================

latest_year = filtered_df["year"].max()

latest_data = (
    filtered_df[filtered_df["year"] == latest_year]
    .groupby("cause_name")["total_deaths"]
    .sum()
    .reset_index()
)

top_risk = latest_data.sort_values(
    by="total_deaths",
    ascending=False
).head(3)

# =========================================================
# 4. RISK SCORING SYSTEM
# =========================================================

risk_score = 0

if top_cause_value > filtered_df["total_deaths"].mean():
    risk_score += 1

if trend_value is not None and trend_value > 0:
    risk_score += 1

if not top_risk.empty and top_risk.iloc[0]["total_deaths"] > filtered_df["total_deaths"].mean():
    risk_score += 1

if risk_score >= 3:
    risk_level = "🔴 HIGH RISK"
elif risk_score == 2:
    risk_level = "🟠 MEDIUM RISK"
else:
    risk_level = "🟢 LOW RISK"

# =========================================================
# 5. OUTPUT RECOMMENDATION
# =========================================================

st.markdown(f"""
### 📊 Risk Level: {risk_level}

---

### 🔍 Key Findings

• Penyebab dominan: **{top_cause_name}**  
• Kontribusi terbesar berasal dari kategori penyakit yang konsisten tinggi  
• Tren kematian: {"meningkat 📈" if trend_value and trend_value > 0 else "menurun 📉 atau stabil"}  

---



""")

# =========================================================
# 6. DYNAMIC RECOMMENDATION (BASED ON DATA)
# =========================================================

# =========================================================
# SMART CLASSIFICATION ENGINE (FINAL FIX FOR INDONESIA DATASET)
# =========================================================

st.markdown("### 🎯 Prioritas Kebijakan")

if top_cause_name != "-":

    cause = str(top_cause_name).lower()

    type_series = filtered_df[
        filtered_df["cause_name"] == top_cause_name
    ]["type_name"]

    top_type = type_series.mode().values[0] if not type_series.empty else "-"
    type_text = str(top_type).lower()

    # =====================================================
    # 🔴 1. BENCANA / EXTERNAL CAUSE (FIX TSUNAMI ISSUE)
    # =====================================================
    disaster_keywords = [
        "tsunami", "gempa", "banjir", "longsor", "erupsi",
        "angin", "topan", "puting beliung", "kebakaran",
        "ledakan", "petir", "kecelakaan", "transportasi",
        "kerusuhan", "konflik", "keracunan", "kebocoran",
        "kecelakaan industri", "kecelakaan kerja"
    ]

    if any(k in cause for k in disaster_keywords) or "sebab luar" in type_text:

        st.error("""
        🔴 PRIORITAS BENCANA & KECELAKAAN:

        • Sistem peringatan dini bencana  
        • Penguatan mitigasi & evakuasi  
        • Keselamatan transportasi & kerja  
        • Manajemen respons darurat cepat  
        """)

    # =====================================================
    # 🟠 2. PENYAKIT MENULAR
    # =====================================================
    elif any(k in cause for k in [
        "dbd", "dengue", "covid", "tb", "tuberkulosis",
        "malaria", "kolera", "difteri", "campak",
        "antraks", "rabies", "hepatitis", "flu", "cikungunya",
        "meningitis", "tetanus", "leptospirosis"
    ]) or "menular" in type_text:

        st.warning("""
        🟠 PRIORITAS PENYAKIT MENULAR:

        • Vaksinasi & imunisasi  
        • Deteksi & isolasi dini  
        • Peningkatan sanitasi lingkungan  
        • Pengendalian wabah & KLB  
        """)

    # =====================================================
    # 🔵 3. PENYAKIT TIDAK MENULAR
    # =====================================================
    elif any(k in cause for k in [
        "stroke", "diabetes", "hipertensi",
        "jantung", "neoplasma", "kanker",
        "ginjal", "pernapasan", "asma"
    ]) or "tidak menular" in type_text:

        st.info("""
        🔵 PRIORITAS PENYAKIT TIDAK MENULAR:

        • Screening penyakit kronis  
        • Kampanye gaya hidup sehat  
        • Pengurangan risiko (rokok, obesitas)  
        • Pemeriksaan kesehatan rutin  
        """)

    # =====================================================
    # ⚪ 4. DEFAULT / PERINATAL / UNKNOWN
    # =====================================================
    else:

        st.success("""
        ⚪ PRIORITAS UMUM:

        • Penguatan sistem kesehatan  
        • Monitoring data penyakit  
        • Peningkatan layanan medis  
        • Investigasi lebih lanjut diperlukan  
        """)






# =========================================================
# FOOTER
# =========================================================

st.write("")

st.markdown("""
---
### 📌 Tentang Dashboard

Dashboard Business Intelligence ini dikembangkan untuk membantu:
- Monitoring tren kematian nasional
- Analisis penyakit dominan
- Evaluasi kategori penyakit
- Early warning kesehatan masyarakat
- Mendukung pengambilan keputusan berbasis data

👨‍⚕️ Target User:
- Dinas Kesehatan
- Peneliti Kesehatan
- Pemerintah
- Pengambil Kebijakan
""")