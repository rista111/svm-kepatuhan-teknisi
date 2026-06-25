from __future__ import annotations

import calendar
import pickle
import numpy as np
import pandas as pd
import streamlit as st

# =============================================================================
# KONFIGURASI HALAMAN
# =============================================================================

st.set_page_config(
    page_title="Dashboard Kepatuhan Teknisi",
    page_icon="🛠️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =============================================================================
# CSS GLOBAL — TAMPILAN BARU
# =============================================================================

STYLE = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* ── Reset & base ─────────────────────────────────────── */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
}

.stApp {
    background-color: #F1F5F9 !important;
}

#MainMenu, footer, header { visibility: hidden; }

.block-container {
    padding: 1.5rem 2rem !important;
    max-width: 1200px !important;
}

/* ── Sidebar ──────────────────────────────────────────── */
section[data-testid="stSidebar"] {
    background: linear-gradient(160deg, #1E1B4B 0%, #312E81 60%, #3730A3 100%) !important;
    border-right: none !important;
}

section[data-testid="stSidebar"] * {
    color: #C7D2FE !important;
}

section[data-testid="stSidebar"] .stSelectbox label {
    color: #A5B4FC !important;
    font-size: 0.72rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.06em !important;
    text-transform: uppercase !important;
}

section[data-testid="stSidebar"] [data-baseweb="select"] > div {
    background: rgba(255,255,255,0.08) !important;
    border: 1px solid rgba(255,255,255,0.15) !important;
    border-radius: 8px !important;
    color: #E0E7FF !important;
}

section[data-testid="stSidebar"] [data-baseweb="select"] svg {
    fill: #A5B4FC !important;
}

/* ── Tombol utama ─────────────────────────────────────── */
.stButton > button {
    background: linear-gradient(135deg, #4F46E5 0%, #6366F1 100%) !important;
    color: white !important;
    font-weight: 600 !important;
    border-radius: 8px !important;
    border: none !important;
    padding: 0.65rem 1rem !important;
    width: 100% !important;
    font-size: 0.85rem !important;
    letter-spacing: 0.02em !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 2px 8px rgba(79,70,229,0.35) !important;
}

.stButton > button:hover {
    background: linear-gradient(135deg, #4338CA 0%, #4F46E5 100%) !important;
    box-shadow: 0 4px 14px rgba(79,70,229,0.45) !important;
    transform: translateY(-1px) !important;
}

/* ── Selectbox (main area) ────────────────────────────── */
[data-baseweb="select"] > div {
    border-radius: 8px !important;
    border-color: #E2E8F0 !important;
    background: #ffffff !important;
}

/* ── Dataframe ────────────────────────────────────────── */
[data-testid="stDataFrame"] {
    border-radius: 10px !important;
    overflow: hidden !important;
    border: 1px solid #E2E8F0 !important;
}

/* ── Info / success / error boxes ────────────────────── */
[data-testid="stAlert"] {
    border-radius: 10px !important;
}

/* ─────────────────── KOMPONEN KUSTOM ──────────────────── */

/* Topbar / page header */
.page-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 1.25rem;
}

.page-title {
    font-size: 1.3rem;
    font-weight: 700;
    color: #1E293B;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.page-subtitle {
    font-size: 0.8rem;
    color: #94A3B8;
    margin-top: 0.15rem;
}

.status-pill {
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
    background: #ECFDF5;
    border: 1px solid #A7F3D0;
    color: #065F46;
    padding: 0.3rem 0.85rem;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
}

.status-pill-inactive {
    background: #FEF2F2;
    border: 1px solid #FECACA;
    color: #991B1B;
}

/* Kartu metrik premium */
.metric-card {
    background: #ffffff;
    border: 1px solid #E2E8F0;
    border-radius: 12px;
    padding: 1rem 1.1rem 0.9rem;
    position: relative;
    overflow: hidden;
    transition: box-shadow 0.2s ease, transform 0.2s ease;
}

.metric-card:hover {
    box-shadow: 0 4px 16px rgba(0,0,0,0.08);
    transform: translateY(-2px);
}

.metric-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    border-radius: 12px 12px 0 0;
}

.metric-card.indigo::before { background: linear-gradient(90deg, #4F46E5, #818CF8); }
.metric-card.emerald::before { background: linear-gradient(90deg, #10B981, #34D399); }
.metric-card.rose::before { background: linear-gradient(90deg, #EF4444, #F87171); }
.metric-card.amber::before { background: linear-gradient(90deg, #F59E0B, #FCD34D); }
.metric-card.violet::before { background: linear-gradient(90deg, #8B5CF6, #A78BFA); }
.metric-card.sky::before { background: linear-gradient(90deg, #0EA5E9, #38BDF8); }

.metric-icon-wrap {
    width: 36px; height: 36px;
    border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.1rem;
    margin-bottom: 0.65rem;
}

.metric-icon-wrap.indigo { background: #EEF2FF; }
.metric-icon-wrap.emerald { background: #ECFDF5; }
.metric-icon-wrap.rose { background: #FFF1F2; }
.metric-icon-wrap.amber { background: #FFFBEB; }
.metric-icon-wrap.violet { background: #F5F3FF; }
.metric-icon-wrap.sky { background: #F0F9FF; }

.metric-value {
    font-size: 1.75rem;
    font-weight: 700;
    color: #1E293B;
    line-height: 1;
    margin-bottom: 0.25rem;
}

.metric-label {
    font-size: 0.75rem;
    color: #94A3B8;
    font-weight: 500;
}

.metric-note {
    font-size: 0.7rem;
    color: #CBD5E1;
    margin-top: 0.4rem;
}

/* Section header */
.section-header {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.9rem;
    font-weight: 600;
    color: #334155;
    margin: 1.1rem 0 0.65rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid #F1F5F9;
}

.section-header .badge {
    margin-left: auto;
    font-size: 0.7rem;
    font-weight: 500;
    color: #64748B;
    background: #F1F5F9;
    padding: 0.15rem 0.5rem;
    border-radius: 12px;
}

/* Bar chart kepatuhan per tipe */
.tipe-row {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    margin-bottom: 0.55rem;
}

.tipe-name {
    width: 80px;
    font-size: 0.78rem;
    color: #475569;
    font-weight: 500;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.tipe-track {
    flex: 1;
    background: #F1F5F9;
    border-radius: 4px;
    height: 8px;
    overflow: hidden;
}

.tipe-fill {
    height: 100%;
    border-radius: 4px;
    transition: width 0.4s ease;
}

.tipe-fill.safe { background: linear-gradient(90deg, #10B981, #34D399); }
.tipe-fill.danger { background: linear-gradient(90deg, #EF4444, #F87171); }

.tipe-count {
    width: 40px;
    font-size: 0.78rem;
    text-align: right;
    font-weight: 600;
}

.tipe-count.safe { color: #10B981; }
.tipe-count.danger { color: #EF4444; }

.tipe-tag {
    font-size: 0.65rem;
    padding: 0.1rem 0.4rem;
    border-radius: 10px;
    font-weight: 600;
    width: 48px;
    text-align: center;
}

.tipe-tag.safe { background: #ECFDF5; color: #065F46; }
.tipe-tag.danger { background: #FEF2F2; color: #991B1B; }

/* Kartu hasil prediksi */
.result-banner {
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    margin-top: 0.75rem;
    text-align: center;
    position: relative;
    overflow: hidden;
}

.result-banner.patuh {
    background: linear-gradient(135deg, #ECFDF5 0%, #D1FAE5 100%);
    border: 1px solid #6EE7B7;
}

.result-banner.tidak-patuh {
    background: linear-gradient(135deg, #FEF2F2 0%, #FEE2E2 100%);
    border: 1px solid #FCA5A5;
}

.result-icon { font-size: 2.2rem; margin-bottom: 0.4rem; }

.result-status {
    font-size: 1.4rem;
    font-weight: 800;
    letter-spacing: 0.04em;
}

.result-status.patuh { color: #065F46; }
.result-status.tidak-patuh { color: #991B1B; }

.result-name {
    font-size: 0.9rem;
    color: #334155;
    margin-top: 0.5rem;
}

.result-detail {
    font-size: 0.75rem;
    color: #64748B;
    margin-top: 0.3rem;
}

/* Violation chips */
.violation-chips {
    display: flex;
    flex-wrap: wrap;
    gap: 0.4rem;
    justify-content: center;
    margin-top: 0.75rem;
}

.v-chip {
    background: #FEE2E2;
    border: 1px solid #FCA5A5;
    color: #991B1B;
    padding: 0.2rem 0.65rem;
    border-radius: 20px;
    font-size: 0.72rem;
    font-weight: 600;
}

/* Sidebar branding */
.sidebar-brand {
    text-align: center;
    padding: 1.2rem 0.5rem 1.5rem;
    border-bottom: 1px solid rgba(255,255,255,0.1);
    margin-bottom: 1rem;
}

.sidebar-brand-icon { font-size: 2.2rem; margin-bottom: 0.4rem; }

.sidebar-brand-title {
    font-size: 0.85rem !important;
    font-weight: 700 !important;
    color: #E0E7FF !important;
    line-height: 1.35;
}

.sidebar-brand-sub {
    font-size: 0.7rem !important;
    color: #818CF8 !important;
    margin-top: 0.2rem;
}

.sidebar-model-badge {
    margin-top: 1.5rem;
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 8px;
    padding: 0.6rem 0.8rem;
    text-align: center;
    font-size: 0.72rem !important;
    color: #A5B4FC !important;
}

/* Tabs styling */
[data-baseweb="tab-list"] {
    background: #F8FAFC !important;
    border-radius: 10px !important;
    padding: 4px !important;
    gap: 4px !important;
}

[data-baseweb="tab"] {
    border-radius: 7px !important;
    font-size: 0.8rem !important;
    font-weight: 500 !important;
    padding: 0.4rem 1rem !important;
    color: #64748B !important;
}

[aria-selected="true"][data-baseweb="tab"] {
    background: #ffffff !important;
    color: #1E293B !important;
    box-shadow: 0 1px 4px rgba(0,0,0,0.08) !important;
}

/* Summary rekap card */
.rekap-summary {
    background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%);
    border-radius: 12px;
    padding: 1.2rem 1.5rem;
    margin-bottom: 1.25rem;
    display: flex;
    align-items: center;
    gap: 1rem;
}

.rekap-summary-text {
    color: #E0E7FF;
    font-size: 0.8rem;
}

.rekap-summary-big {
    color: #ffffff;
    font-size: 1.6rem;
    font-weight: 700;
}

/* Divider */
.divider {
    border: none;
    border-top: 1px solid #F1F5F9;
    margin: 1rem 0;
}
</style>
"""

st.markdown(STYLE, unsafe_allow_html=True)

# =============================================================================
# LOAD MODEL & DATA
# =============================================================================

@st.cache_resource
def load_models():
    try:
        model    = pickle.load(open("model_svm.pkl",  "rb"))
        scaler   = pickle.load(open("scaler.pkl",     "rb"))
        le_tek   = pickle.load(open("le_teknisi.pkl", "rb"))
        return model, scaler, le_tek
    except Exception:
        return None, None, None


@st.cache_data
def load_data():
    df = pd.read_excel(
        "data/ALL IN OUT SO PNK 2021 - 2025.xlsx",
        engine="openpyxl",
    )
    df.columns = df.columns.str.strip().str.upper()
    df = df.dropna(subset=["TANGGAL", "TEKNISI", "TIPE"])
    df["TANGGAL"] = pd.to_datetime(df["TANGGAL"])
    return df


model, scaler, le_teknisi = load_models()
df = load_data()

BATAS_PER_TIPE = 3

# =============================================================================
# HELPER RENDER
# =============================================================================

def metric_card(icon, value, label, color="indigo", note=""):
    note_html = f'<div class="metric-note">{note}</div>' if note else ""
    st.markdown(
        f"""
        <div class="metric-card {color}">
            <div class="metric-icon-wrap {color}">{icon}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-label">{label}</div>
            {note_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_header(icon, title, badge=""):
    badge_html = f'<span class="badge">{badge}</span>' if badge else ""
    st.markdown(
        f'<div class="section-header">{icon} {title}{badge_html}</div>',
        unsafe_allow_html=True,
    )


def render_tipe_bars(detail_tipe: pd.DataFrame):
    """Bar horizontal per tipe dengan warna merah/hijau otomatis."""
    max_val = max(detail_tipe["JUMLAH"].max(), BATAS_PER_TIPE + 1)
    for _, row in detail_tipe.iterrows():
        tipe    = str(row["TIPE"])
        jumlah  = int(row["JUMLAH"])
        pct     = min(jumlah / max_val * 100, 100)
        is_over = jumlah > BATAS_PER_TIPE
        cls     = "danger" if is_over else "safe"
        tag     = "⚠ Lebih" if is_over else "✓ OK"
        st.markdown(
            f"""
            <div class="tipe-row">
                <div class="tipe-name">{tipe}</div>
                <div class="tipe-track">
                    <div class="tipe-fill {cls}" style="width:{pct}%"></div>
                </div>
                <div class="tipe-count {cls}">{jumlah}×</div>
                <div class="tipe-tag {cls}">{tag}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_result(pred, teknisi, violations):
    if pred == 0:
        icon = "✅"
        cls  = "patuh"
        status_lbl = "PATUH"
        detail = f"Semua tipe material ≤ {BATAS_PER_TIPE} pengambilan"
        chips  = ""
    else:
        icon = "⚠️"
        cls  = "tidak-patuh"
        status_lbl = "TIDAK PATUH"
        detail = f"Terdapat tipe melebihi batas {BATAS_PER_TIPE} pengambilan"
        chip_items = " ".join(
            f'<span class="v-chip">{t}: {j}×</span>'
            for t, j in violations
        )
        chips = f'<div class="violation-chips">{chip_items}</div>'

    st.markdown(
        f"""
        <div class="result-banner {cls}">
            <div class="result-icon">{icon}</div>
            <div class="result-status {cls}">{status_lbl}</div>
            <div class="result-name">Teknisi <strong>{teknisi}</strong></div>
            <div class="result-detail">{detail}</div>
            {chips}
        </div>
        """,
        unsafe_allow_html=True,
    )

# =============================================================================
# LOGIKA PREDIKSI
# =============================================================================

def predict_from_detail(df_harian):
    violations = []
    if df_harian.empty:
        return 0, violations
    per_tipe = df_harian.groupby("TIPE").size()
    for tipe, jumlah in per_tipe.items():
        if jumlah > BATAS_PER_TIPE:
            violations.append((tipe, int(jumlah)))
    return (1, violations) if violations else (0, violations)


def predict(jumlah_tipe, total_pengambilan, enc_teknisi):
    return 1 if total_pengambilan > (jumlah_tipe * BATAS_PER_TIPE) else 0


def encode_teknisi(nama):
    if le_teknisi is None:
        return 0
    try:
        return int(le_teknisi.transform([nama])[0])
    except Exception:
        return 0

# =============================================================================
# SIDEBAR
# =============================================================================

with st.sidebar:
    st.markdown(
        """
        <div class="sidebar-brand">
            <div class="sidebar-brand-icon">🛠️</div>
            <div class="sidebar-brand-title">Dashboard Kepatuhan<br>Teknisi</div>
            <div class="sidebar-brand-sub">Sistem Monitoring Material</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    menu = st.selectbox(
        "NAVIGASI",
        ["📊 Monitoring Harian", "📈 Rekap Kepatuhan"],
    )

    model_status = "● Model Aktif" if model is not None else "○ Model Tidak Ada"
    model_color  = "#10B981" if model is not None else "#EF4444"
    st.markdown(
        f"""
        <div class="sidebar-model-badge">
            <span style="color:{model_color}">{model_status}</span><br>
            <span>SVM Classifier v1.0</span><br>
            <span style="color:#6366F1">Batas: {BATAS_PER_TIPE}× per tipe</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

# =============================================================================
# HALAMAN: MONITORING HARIAN
# =============================================================================

if menu == "📊 Monitoring Harian":

    st.markdown(
        """
        <div class="page-header">
            <div>
                <div class="page-title">📊 Monitoring Kepatuhan Harian</div>
                <div class="page-subtitle">Analisis pengambilan material per teknisi</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Filter ────────────────────────────────────────────────────────────────
    teknisi_list = sorted(df["TEKNISI"].unique())
    teknisi = st.selectbox("👤 Pilih Teknisi", teknisi_list)

    df_teknisi = df[df["TEKNISI"] == teknisi]

    col1, col2, col3 = st.columns(3)

    with col1:
        tahun_list = sorted(df_teknisi["TANGGAL"].dt.year.unique(), reverse=True)
        tahun = st.selectbox("📅 Tahun", tahun_list)

    df_tahun = df_teknisi[df_teknisi["TANGGAL"].dt.year == tahun]

    with col2:
        bulan_list = sorted(df_tahun["TANGGAL"].dt.month.unique())
        bulan_nama = st.selectbox(
            "🗓️ Bulan",
            [calendar.month_name[i] for i in bulan_list],
        )

    bulan_idx = list(calendar.month_name).index(bulan_nama)
    df_bulan  = df_tahun[df_tahun["TANGGAL"].dt.month == bulan_idx]

    with col3:
        tanggal_list  = sorted(df_bulan["TANGGAL"].dt.date.unique())
        tanggal_pilih = st.selectbox("📆 Tanggal", tanggal_list)

    # ── Data harian ───────────────────────────────────────────────────────────
    df_harian         = df_bulan[df_bulan["TANGGAL"].dt.date == tanggal_pilih]
    total_pengambilan = len(df_harian)
    jumlah_tipe       = df_harian["TIPE"].nunique()
    n_melanggar       = int(
        df_harian.groupby("TIPE").size().gt(BATAS_PER_TIPE).sum()
    )

    # ── Kartu metrik ──────────────────────────────────────────────────────────
    section_header("📊", "Ringkasan Hari Ini")
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        metric_card("📦", total_pengambilan, "Total Pengambilan", "indigo",
                    note="seluruh tipe material")
    with c2:
        metric_card("🗂️", jumlah_tipe, "Jumlah Tipe", "sky",
                    note="tipe unik hari ini")
    with c3:
        metric_card(
            "⚠️" if n_melanggar else "✅",
            n_melanggar,
            "Tipe Melebihi Batas",
            "rose" if n_melanggar else "emerald",
            note=f"batas {BATAS_PER_TIPE}× per tipe",
        )
    with c4:
        metric_card("📅", tanggal_pilih.strftime("%d/%m/%Y"), "Tanggal", "violet")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Detail tipe ───────────────────────────────────────────────────────────
    detail_tipe = (
        df_harian.groupby("TIPE")
        .size()
        .reset_index(name="JUMLAH")
        .sort_values("JUMLAH", ascending=False)
    )

    col_bar, col_tbl = st.columns([1.4, 1])

    with col_bar:
        section_header("📋", "Pengambilan per Tipe", badge=f"batas = {BATAS_PER_TIPE}×")
        if detail_tipe.empty:
            st.info("Tidak ada data pengambilan untuk tanggal ini.")
        else:
            render_tipe_bars(detail_tipe)

        st.markdown("<br>", unsafe_allow_html=True)

        # Tombol prediksi
        if st.button("🔍 Jalankan Model SVM — Cek Kepatuhan"):
            pred, violations = predict_from_detail(df_harian)
            render_result(pred, teknisi, violations)

    with col_tbl:
        section_header("📄", "Tabel Detail", badge=f"{len(detail_tipe)} tipe")

        if not detail_tipe.empty:
            detail_display = detail_tipe.copy()
            detail_display["STATUS"] = detail_display["JUMLAH"].apply(
                lambda x: "✅ Patuh" if x <= BATAS_PER_TIPE else "⚠️ Tidak Patuh"
            )
            st.dataframe(
                detail_display.rename(columns={
                    "TIPE": "Tipe",
                    "JUMLAH": "Jumlah",
                    "STATUS": "Status",
                }),
                use_container_width=True,
                hide_index=True,
                height=min(300, 40 + len(detail_display) * 36),
            )

            # Mini statistik
            avg = detail_tipe["JUMLAH"].mean()
            mx  = detail_tipe["JUMLAH"].max()
            st.markdown(
                f"""
                <div style="background:#F8FAFC;border:1px solid #E2E8F0;border-radius:8px;
                            padding:0.65rem 0.85rem;margin-top:0.5rem;font-size:0.75rem;color:#64748B;">
                    📈 Rata-rata: <strong style="color:#1E293B">{avg:.1f}×</strong> &nbsp;|&nbsp;
                    🔺 Maks: <strong style="color:#1E293B">{mx}×</strong> &nbsp;|&nbsp;
                    📦 Total: <strong style="color:#1E293B">{total_pengambilan}</strong>
                </div>
                """,
                unsafe_allow_html=True,
            )


# =============================================================================
# HALAMAN: REKAP KEPATUHAN
# =============================================================================

elif menu == "📈 Rekap Kepatuhan":
    import plotly.graph_objects as go

    st.markdown(
        """
        <div class="page-header">
            <div>
                <div class="page-title">📈 Rekap Kepatuhan Teknisi</div>
                <div class="page-subtitle">Analisis tren & perbandingan kepatuhan semua teknisi</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if df.empty:
        st.warning("Data tidak tersedia. Pastikan file Excel sudah ada.")
        st.stop()

    # ── Filter ────────────────────────────────────────────────────────────────
    col_f1, col_f2, col_f3 = st.columns([1, 1, 1])

    with col_f1:
        tahun_list_all = sorted(df["TANGGAL"].dt.year.unique(), reverse=True)
        tahun_rekap    = st.selectbox("📅 Tahun", tahun_list_all, key="rekap_tahun")

    with col_f2:
        mode_filter = st.selectbox(
            "🔍 Mode Tampilan",
            ["Per Bulan", "Semua Bulan"],
            key="rekap_mode",
        )

    df_tahun_rekap = df[df["TANGGAL"].dt.year == tahun_rekap]

    if mode_filter == "Per Bulan":
        bulan_avail = sorted(df_tahun_rekap["TANGGAL"].dt.month.unique())
        with col_f3:
            bulan_nama_rekap = st.selectbox(
                "🗓️ Bulan",
                [calendar.month_name[i] for i in bulan_avail],
                key="rekap_bulan",
            )
        bulan_idx_rekap = list(calendar.month_name).index(bulan_nama_rekap)
        df_scope    = df_tahun_rekap[df_tahun_rekap["TANGGAL"].dt.month == bulan_idx_rekap]
        scope_label = f"{bulan_nama_rekap} {tahun_rekap}"
    else:
        df_scope    = df_tahun_rekap
        scope_label = f"Tahun {tahun_rekap}"

    # ── Agregasi & prediksi ───────────────────────────────────────────────────
    if df_scope.empty:
        st.info("Tidak ada data untuk filter yang dipilih.")
        st.stop()

    agg = (
        df_scope.groupby(["TEKNISI", df_scope["TANGGAL"].dt.date])
        .agg(total_pengambilan=("TIPE", "count"), jumlah_tipe=("TIPE", "nunique"))
        .reset_index()
    )
    agg.columns = ["TEKNISI", "TANGGAL", "TOTAL", "TIPE"]
    agg["ENC"]   = agg["TEKNISI"].apply(encode_teknisi)
    agg["PRED"]  = agg.apply(
        lambda r: predict(int(r["TIPE"]), int(r["TOTAL"]), int(r["ENC"])), axis=1
    )
    agg["BULAN"] = pd.to_datetime(agg["TANGGAL"]).dt.month

    rekap = (
        agg.groupby("TEKNISI")["PRED"]
        .agg(Patuh=lambda x: (x == 0).sum(), Tidak_Patuh=lambda x: (x == 1).sum())
        .reset_index()
    )
    rekap["Total_Hari"] = rekap["Patuh"] + rekap["Tidak_Patuh"]
    rekap["Pct_Patuh"]  = (rekap["Patuh"] / rekap["Total_Hari"] * 100).round(1)
    rekap = rekap.sort_values("Patuh", ascending=False).reset_index(drop=True)

    total_patuh = int(rekap["Patuh"].sum())
    total_tidak = int(rekap["Tidak_Patuh"].sum())
    total_semua = total_patuh + total_tidak
    pct_overall = round(total_patuh / total_semua * 100, 1) if total_semua else 0

    # ── Banner rekap ──────────────────────────────────────────────────────────
    st.markdown(
        f"""
        <div class="rekap-summary">
            <div style="font-size:2.2rem">📊</div>
            <div>
                <div class="rekap-summary-big">{pct_overall}% Kepatuhan</div>
                <div class="rekap-summary-text">
                    Periode: <strong>{scope_label}</strong> &nbsp;·&nbsp;
                    {len(rekap)} teknisi aktif &nbsp;·&nbsp;
                    {total_semua} total hari kerja
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Kartu metrik ringkasan ─────────────────────────────────────────────────
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        metric_card("✅", total_patuh, "Hari Patuh", "emerald")
    with m2:
        metric_card("⚠️", total_tidak, "Hari Tidak Patuh", "rose")
    with m3:
        metric_card("📅", total_semua, "Total Hari Kerja", "sky")
    with m4:
        metric_card("👥", len(rekap), "Teknisi Aktif", "violet")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Tren per bulan ────────────────────────────────────────────────────────
    tren = (
        agg.groupby("BULAN")["PRED"]
        .agg(Patuh=lambda x: (x == 0).sum(), Tidak_Patuh=lambda x: (x == 1).sum())
        .reset_index()
    )
    tren["Nama_Bulan"]      = tren["BULAN"].apply(lambda m: calendar.month_name[m])
    tren["Nama_Bulan_Abbr"] = tren["BULAN"].apply(lambda m: calendar.month_abbr[m])
    tren["Total"]           = tren["Patuh"] + tren["Tidak_Patuh"]
    tren["Pct"]             = (tren["Patuh"] / tren["Total"] * 100).round(1)

    # ── Tab ───────────────────────────────────────────────────────────────────
    if mode_filter == "Per Bulan":
        tab_labels = ["📊 Grafik Kepatuhan", "📋 Tabel Teknisi"]
    else:
        tab_labels = ["📊 Stacked Bar", "📈 Line Tren", "🔥 Heatmap", "📋 Tabel Teknisi"]

    tabs = st.tabs(tab_labels)

    # ── TAB 1: Grafik ─────────────────────────────────────────────────────────
    with tabs[0]:
        if mode_filter == "Per Bulan":
            fig = go.Figure()
            fig.add_trace(go.Bar(
                name="Patuh", x=[scope_label], y=[total_patuh],
                marker_color="#10B981", marker_line_width=0,
                text=[total_patuh], textposition="inside",
                textfont=dict(color="white", size=14), width=0.35,
            ))
            fig.add_trace(go.Bar(
                name="Tidak Patuh", x=[scope_label], y=[total_tidak],
                marker_color="#EF4444", marker_line_width=0,
                text=[total_tidak], textposition="inside",
                textfont=dict(color="white", size=14), width=0.35,
            ))
            fig.update_layout(
                barmode="stack",
                title=dict(text=f"Kepatuhan — {scope_label}",
                           font=dict(size=14, family="Inter"), x=0),
                yaxis=dict(title="Jumlah Hari", gridcolor="#F1F5F9", tickfont=dict(size=11)),
                legend=dict(orientation="h", yanchor="bottom", y=1.02,
                            xanchor="right", x=1, font=dict(size=12)),
                plot_bgcolor="white", paper_bgcolor="white",
                font=dict(family="Inter", size=12),
                margin=dict(t=60, b=50, l=50, r=20), height=380,
            )
            st.plotly_chart(fig, use_container_width=True)
            pct_p = round(total_patuh / total_semua * 100, 1) if total_semua else 0
            st.info(f"📌 **{total_patuh}** hari patuh ({pct_p}%) dan **{total_tidak}** hari tidak patuh dari total **{total_semua}** hari kerja pada {scope_label}.")

        else:
            fig = go.Figure()
            fig.add_trace(go.Bar(
                name="Patuh", x=tren["Nama_Bulan_Abbr"], y=tren["Patuh"],
                marker_color="#10B981", marker_line_width=0,
                text=tren["Patuh"], textposition="inside",
                textfont=dict(color="white", size=11),
                customdata=tren["Pct"],
                hovertemplate="<b>%{x}</b><br>Patuh: %{y} hari<br>Tingkat: %{customdata}%<extra></extra>",
            ))
            fig.add_trace(go.Bar(
                name="Tidak Patuh", x=tren["Nama_Bulan_Abbr"], y=tren["Tidak_Patuh"],
                marker_color="#EF4444", marker_line_width=0,
                text=tren["Tidak_Patuh"], textposition="inside",
                textfont=dict(color="white", size=11),
                hovertemplate="<b>%{x}</b><br>Tidak Patuh: %{y} hari<extra></extra>",
            ))
            fig.add_trace(go.Scatter(
                name="% Patuh", x=tren["Nama_Bulan_Abbr"], y=tren["Pct"],
                mode="lines+markers+text", yaxis="y2",
                line=dict(color="#4F46E5", width=2.5),
                marker=dict(size=8, color="#4F46E5",
                            line=dict(color="white", width=1.5)),
                text=[f"{v}%" for v in tren["Pct"]],
                textposition="top center",
                textfont=dict(size=9, color="#4F46E5"),
            ))
            fig.update_layout(
                barmode="stack",
                title=dict(text=f"Stacked Bar Kepatuhan per Bulan — {tahun_rekap}",
                           font=dict(size=14, family="Inter"), x=0),
                xaxis=dict(title="Bulan", tickfont=dict(size=11)),
                yaxis=dict(title="Jumlah Hari", gridcolor="#F1F5F9"),
                yaxis2=dict(title="% Patuh", overlaying="y", side="right",
                            range=[0, 130], showgrid=False, ticksuffix="%"),
                legend=dict(orientation="h", yanchor="bottom", y=1.02,
                            xanchor="right", x=1, font=dict(size=12)),
                plot_bgcolor="white", paper_bgcolor="white",
                font=dict(family="Inter", size=12),
                margin=dict(t=70, b=60, l=50, r=60), height=440,
            )
            st.plotly_chart(fig, use_container_width=True)
            bulan_terburuk = tren.loc[tren["Tidak_Patuh"].idxmax(), "Nama_Bulan"]
            bulan_terbaik  = tren.loc[tren["Patuh"].idxmax(), "Nama_Bulan"]
            st.info(f"📌 Pelanggaran terbanyak: **{bulan_terburuk}** · Kepatuhan tertinggi: **{bulan_terbaik}**")

    # ── TAB 2 & 3: Semua Bulan ────────────────────────────────────────────────
    if mode_filter == "Semua Bulan":
        with tabs[1]:
            fig_line = go.Figure()
            fig_line.add_trace(go.Scatter(
                name="Patuh", x=tren["Nama_Bulan_Abbr"], y=tren["Patuh"],
                mode="lines+markers+text",
                line=dict(color="#10B981", width=2.5),
                marker=dict(size=9, color="#10B981", line=dict(color="white", width=1.5)),
                text=tren["Patuh"], textposition="top center",
                textfont=dict(size=10, color="#059669"),
                fill="tozeroy", fillcolor="rgba(16,185,129,0.08)",
                hovertemplate="<b>%{x}</b><br>Patuh: %{y} hari<extra></extra>",
            ))
            fig_line.add_trace(go.Scatter(
                name="Tidak Patuh", x=tren["Nama_Bulan_Abbr"], y=tren["Tidak_Patuh"],
                mode="lines+markers+text",
                line=dict(color="#EF4444", width=2.5),
                marker=dict(size=9, color="#EF4444", line=dict(color="white", width=1.5)),
                text=tren["Tidak_Patuh"], textposition="top center",
                textfont=dict(size=10, color="#DC2626"),
                fill="tozeroy", fillcolor="rgba(239,68,68,0.06)",
                hovertemplate="<b>%{x}</b><br>Tidak Patuh: %{y} hari<extra></extra>",
            ))
            fig_line.update_layout(
                title=dict(text=f"Tren Kepatuhan per Bulan — {tahun_rekap}",
                           font=dict(size=14, family="Inter"), x=0),
                xaxis=dict(title="Bulan", tickfont=dict(size=11), showgrid=False),
                yaxis=dict(title="Jumlah Hari", gridcolor="#F1F5F9"),
                legend=dict(orientation="h", yanchor="bottom", y=1.02,
                            xanchor="right", x=1, font=dict(size=12)),
                plot_bgcolor="white", paper_bgcolor="white",
                font=dict(family="Inter", size=12),
                margin=dict(t=70, b=60, l=50, r=20), height=420,
                hovermode="x unified",
            )
            st.plotly_chart(fig_line, use_container_width=True)
            if len(tren) >= 2:
                delta       = int(tren["Patuh"].iloc[-1]) - int(tren["Patuh"].iloc[0])
                arah        = "meningkat 📈" if delta > 0 else "menurun 📉" if delta < 0 else "stabil ➡️"
                bulan_awal  = tren["Nama_Bulan"].iloc[0]
                bulan_akhir = tren["Nama_Bulan"].iloc[-1]
                st.info(f"📌 Tren kepatuhan dari **{bulan_awal}** ke **{bulan_akhir}** **{arah}** (selisih {abs(delta)} hari).")

        with tabs[2]:
            heat_pivot = pd.DataFrame({
                "Patuh":       tren["Patuh"].values,
                "Tidak Patuh": tren["Tidak_Patuh"].values,
                "% Patuh":     tren["Pct"].values,
            }, index=tren["Nama_Bulan_Abbr"].values).T

            fig_heat = go.Figure(go.Heatmap(
                z=heat_pivot.values,
                x=heat_pivot.columns.tolist(),
                y=heat_pivot.index.tolist(),
                colorscale=[
                    [0.0, "#ECFDF5"], [0.33, "#A7F3D0"],
                    [0.66, "#FEF9C3"], [1.0,  "#991B1B"],
                ],
                colorbar=dict(title=dict(text="Nilai"), tickfont=dict(size=10)),
                text=heat_pivot.values,
                texttemplate="%{text}",
                textfont=dict(size=12, color="black"),
                hovertemplate="Bulan: %{x}<br>%{y}: %{z}<extra></extra>",
            ))
            fig_heat.update_layout(
                title=dict(text=f"Heatmap Kepatuhan per Bulan — {tahun_rekap}",
                           font=dict(size=14, family="Inter"), x=0),
                xaxis=dict(title="Bulan", tickfont=dict(size=11), side="bottom"),
                yaxis=dict(title="", tickfont=dict(size=12), autorange="reversed"),
                font=dict(family="Inter", size=12),
                margin=dict(t=70, b=60, l=130, r=20), height=300,
                plot_bgcolor="white", paper_bgcolor="white",
            )
            st.plotly_chart(fig_heat, use_container_width=True)
            st.caption("🟢 Hijau = nilai tinggi · 🟡 Kuning = sedang · 🔴 Merah = rendah / banyak pelanggaran")

    # ── TAB TERAKHIR: Tabel teknisi ───────────────────────────────────────────
    with tabs[-1]:
        section_header("👥", "Detail Kepatuhan per Teknisi", badge=f"{len(rekap)} teknisi")

        display_df = rekap.rename(columns={
            "TEKNISI":     "Teknisi",
            "Patuh":       "Hari Patuh",
            "Tidak_Patuh": "Hari Tidak Patuh",
            "Total_Hari":  "Total Hari",
            "Pct_Patuh":   "% Patuh",
        })

        st.dataframe(
            display_df.style
            .background_gradient(subset=["% Patuh"], cmap="RdYlGn", vmin=0, vmax=100)
            .format({"% Patuh": "{:.1f}%"})
            .bar(subset=["Hari Patuh"], color="#BBF7D0")
            .bar(subset=["Hari Tidak Patuh"], color="#FECACA"),
            use_container_width=True,
            hide_index=True,
            height=min(600, 60 + len(display_df) * 36),
        )

        # Top & bottom performer
        if len(rekap) >= 2:
            top = rekap.iloc[0]
            bot = rekap.sort_values("Pct_Patuh").iloc[0]
            col_top, col_bot = st.columns(2)
            with col_top:
                st.success(
                    f"🏆 **Teknisi Terbaik**: {top['TEKNISI']} "
                    f"— {top['Pct_Patuh']}% patuh ({int(top['Patuh'])} hari)"
                )
            with col_bot:
                st.warning(
                    f"⚠️ **Perlu Perhatian**: {bot['TEKNISI']} "
                    f"— {bot['Pct_Patuh']}% patuh ({int(bot['Tidak_Patuh'])} hari tidak patuh)"
                )
