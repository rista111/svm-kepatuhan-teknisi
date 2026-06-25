from __future__ import annotations

import calendar
import pickle
import pandas as pd
import streamlit as st

# =============================================================================
# KONFIGURASI
# =============================================================================

st.set_page_config(
    page_title="Dashboard Kepatuhan Teknisi",
    page_icon="🛠️",
    layout="wide",
)

BATAS_PER_TIPE = 3  # Batas maksimal pengambilan per tipe material

# =============================================================================
# LOAD MODEL & DATA
# =============================================================================

@st.cache_resource
def load_models():
    try:
        model      = pickle.load(open("model_svm.pkl",  "rb"))
        scaler     = pickle.load(open("scaler.pkl",     "rb"))
        le_teknisi = pickle.load(open("le_teknisi.pkl", "rb"))
        return model, scaler, le_teknisi
    except Exception:
        return None, None, None


@st.cache_data
def load_data():
    df = pd.read_excel("data/ALL IN OUT SO PNK 2021 - 2025.xlsx", engine="openpyxl")
    df.columns = df.columns.str.strip().str.upper()
    df = df.dropna(subset=["TANGGAL", "TEKNISI", "TIPE"])
    df["TANGGAL"] = pd.to_datetime(df["TANGGAL"])
    return df


model, scaler, le_teknisi = load_models()
df = load_data()

# =============================================================================
# FUNGSI PREDIKSI
# =============================================================================

def cek_kepatuhan(df_harian):
    """
    Cek apakah teknisi patuh pada hari tertentu.
    Patuh     = semua tipe <= BATAS_PER_TIPE
    Tidak Patuh = ada tipe yang melebihi batas
    Mengembalikan: (status, daftar_pelanggaran)
    """
    if df_harian.empty:
        return "patuh", []

    jumlah_per_tipe = df_harian.groupby("TIPE").size()
    pelanggaran = [
        (tipe, int(jumlah))
        for tipe, jumlah in jumlah_per_tipe.items()
        if jumlah > BATAS_PER_TIPE
    ]

    if pelanggaran:
        return "tidak_patuh", pelanggaran
    return "patuh", []


def prediksi_rekap(total, jumlah_tipe):
    """Prediksi untuk rekap: tidak patuh jika total melebihi batas."""
    return "tidak_patuh" if total > (jumlah_tipe * BATAS_PER_TIPE) else "patuh"

# =============================================================================
# SIDEBAR — NAVIGASI
# =============================================================================

with st.sidebar:
    st.title("🛠️ Dashboard Kepatuhan")
    st.caption("Sistem Monitoring Material Teknisi")
    st.divider()

    menu = st.radio(
        "Pilih Halaman",
        ["📊 Monitoring Harian", "📈 Rekap Kepatuhan"],
    )

    st.divider()
    st.caption(f"Batas pengambilan: **{BATAS_PER_TIPE}×** per tipe")
    if model:
        st.success("✅ Model SVM aktif")
    else:
        st.warning("⚠️ Model tidak ditemukan")

# =============================================================================
# HALAMAN 1 — MONITORING HARIAN
# =============================================================================

if menu == "📊 Monitoring Harian":
    st.header("📊 Monitoring Kepatuhan Harian")

    # ── Filter teknisi & tanggal ──────────────────────────────────────────────
    teknisi = st.selectbox("Pilih Teknisi", sorted(df["TEKNISI"].unique()))
    df_teknisi = df[df["TEKNISI"] == teknisi]

    col1, col2, col3 = st.columns(3)

    with col1:
        tahun = st.selectbox(
            "Tahun",
            sorted(df_teknisi["TANGGAL"].dt.year.unique(), reverse=True),
        )

    df_tahun = df_teknisi[df_teknisi["TANGGAL"].dt.year == tahun]

    with col2:
        bulan_list = sorted(df_tahun["TANGGAL"].dt.month.unique())
        bulan_nama = st.selectbox(
            "Bulan",
            [calendar.month_name[b] for b in bulan_list],
        )

    bulan_idx = list(calendar.month_name).index(bulan_nama)
    df_bulan  = df_tahun[df_tahun["TANGGAL"].dt.month == bulan_idx]

    with col3:
        tanggal_pilih = st.selectbox(
            "Tanggal",
            sorted(df_bulan["TANGGAL"].dt.date.unique()),
        )

    # ── Data hari yang dipilih ────────────────────────────────────────────────
    df_harian = df_bulan[df_bulan["TANGGAL"].dt.date == tanggal_pilih]

    # ── Kartu ringkasan ───────────────────────────────────────────────────────
    st.divider()
    c1, c2, c3 = st.columns(3)
    c1.metric("📦 Total Pengambilan", len(df_harian))
    c2.metric("🗂️ Jumlah Tipe", df_harian["TIPE"].nunique())
    c3.metric("📅 Tanggal", tanggal_pilih.strftime("%d-%m-%Y"))

    # ── Tabel detail per tipe ─────────────────────────────────────────────────
    st.divider()
    st.subheader("Detail Pengambilan per Tipe")

    if df_harian.empty:
        st.info("Tidak ada data untuk tanggal ini.")
    else:
        tabel = (
            df_harian.groupby("TIPE")
            .size()
            .reset_index(name="Jumlah")
            .sort_values("Jumlah", ascending=False)
        )
        tabel["Status"] = tabel["Jumlah"].apply(
            lambda x: "✅ Patuh" if x <= BATAS_PER_TIPE else "⚠️ Tidak Patuh"
        )
        st.dataframe(tabel, use_container_width=True, hide_index=True)

    # ── Tombol prediksi ───────────────────────────────────────────────────────
    st.divider()
    if st.button("🔍 Cek Kepatuhan", type="primary"):
        status, pelanggaran = cek_kepatuhan(df_harian)

        if status == "patuh":
            st.success(
                f"✅ **PATUH** — Teknisi **{teknisi}** tidak ada pelanggaran hari ini."
            )
        else:
            tipe_list = ", ".join(f"{t} ({j}×)" for t, j in pelanggaran)
            st.error(
                f"⚠️ **TIDAK PATUH** — Teknisi **{teknisi}** melebihi batas pada: {tipe_list}"
            )

# =============================================================================
# HALAMAN 2 — REKAP KEPATUHAN
# =============================================================================

elif menu == "📈 Rekap Kepatuhan":
    import plotly.graph_objects as go

    st.header("📈 Rekap Kepatuhan Teknisi")

    if df.empty:
        st.warning("Data tidak tersedia.")
        st.stop()

    # ── Filter ────────────────────────────────────────────────────────────────
    col1, col2, col3 = st.columns(3)

    with col1:
        tahun_rekap = st.selectbox(
            "Tahun",
            sorted(df["TANGGAL"].dt.year.unique(), reverse=True),
        )

    with col2:
        mode = st.selectbox("Tampilkan", ["Per Bulan", "Semua Bulan"])

    df_tahun = df[df["TANGGAL"].dt.year == tahun_rekap]

    if mode == "Per Bulan":
        bulan_avail = sorted(df_tahun["TANGGAL"].dt.month.unique())
        with col3:
            bulan_nama = st.selectbox(
                "Bulan",
                [calendar.month_name[b] for b in bulan_avail],
            )
        bulan_idx  = list(calendar.month_name).index(bulan_nama)
        df_scope   = df_tahun[df_tahun["TANGGAL"].dt.month == bulan_idx]
        label      = f"{bulan_nama} {tahun_rekap}"
    else:
        df_scope = df_tahun
        label    = f"Tahun {tahun_rekap}"

    if df_scope.empty:
        st.info("Tidak ada data untuk filter ini.")
        st.stop()

    # ── Hitung kepatuhan per teknisi per hari ─────────────────────────────────
    agg = (
        df_scope
        .groupby(["TEKNISI", df_scope["TANGGAL"].dt.date])
        .agg(total=("TIPE", "count"), jenis=("TIPE", "nunique"))
        .reset_index()
    )
    agg.columns  = ["TEKNISI", "TANGGAL", "TOTAL", "JENIS"]
    agg["STATUS"] = agg.apply(
        lambda r: prediksi_rekap(r["TOTAL"], r["JENIS"]), axis=1
    )
    agg["BULAN"] = pd.to_datetime(agg["TANGGAL"]).dt.month

    # Rekap per teknisi
    rekap = (
        agg.groupby("TEKNISI")["STATUS"]
        .agg(
            Patuh       = lambda x: (x == "patuh").sum(),
            Tidak_Patuh = lambda x: (x == "tidak_patuh").sum(),
        )
        .reset_index()
    )
    rekap["Total"]     = rekap["Patuh"] + rekap["Tidak_Patuh"]
    rekap["% Patuh"]   = (rekap["Patuh"] / rekap["Total"] * 100).round(1)
    rekap = rekap.sort_values("% Patuh", ascending=False).reset_index(drop=True)

    # ── Ringkasan angka ───────────────────────────────────────────────────────
    total_patuh = int(rekap["Patuh"].sum())
    total_tidak = int(rekap["Tidak_Patuh"].sum())
    total_semua = total_patuh + total_tidak
    pct         = round(total_patuh / total_semua * 100, 1) if total_semua else 0

    st.caption(f"Periode: **{label}**")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("✅ Hari Patuh",       total_patuh)
    c2.metric("⚠️ Hari Tidak Patuh", total_tidak)
    c3.metric("📅 Total Hari Kerja", total_semua)
    c4.metric("📊 Tingkat Kepatuhan", f"{pct}%")

    st.divider()

    # ── Tab konten ────────────────────────────────────────────────────────────
    if mode == "Per Bulan":
        tab1, tab2 = st.tabs(["📊 Grafik", "📋 Tabel"])
    else:
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Stacked Bar", "📈 Line Chart", "🔥 Heatmap", "📋 Tabel"])

    # Tren per bulan (untuk semua bulan)
    tren = (
        agg.groupby("BULAN")["STATUS"]
        .agg(
            Patuh       = lambda x: (x == "patuh").sum(),
            Tidak_Patuh = lambda x: (x == "tidak_patuh").sum(),
        )
        .reset_index()
    )
    tren["Bulan"]  = tren["BULAN"].apply(lambda m: calendar.month_abbr[m])
    tren["Total"]  = tren["Patuh"] + tren["Tidak_Patuh"]
    tren["Pct"]    = (tren["Patuh"] / tren["Total"] * 100).round(1)

    # Tab Grafik / Stacked Bar
    with tab1:
        if mode == "Per Bulan":
            fig = go.Figure()
            fig.add_trace(go.Bar(name="Patuh",       x=[label], y=[total_patuh], marker_color="#10B981"))
            fig.add_trace(go.Bar(name="Tidak Patuh", x=[label], y=[total_tidak], marker_color="#EF4444"))
            fig.update_layout(barmode="stack", height=360, plot_bgcolor="white", paper_bgcolor="white")
            st.plotly_chart(fig, use_container_width=True)
        else:
            fig = go.Figure()
            fig.add_trace(go.Bar(name="Patuh",       x=tren["Bulan"], y=tren["Patuh"],       marker_color="#10B981"))
            fig.add_trace(go.Bar(name="Tidak Patuh", x=tren["Bulan"], y=tren["Tidak_Patuh"], marker_color="#EF4444"))
            fig.add_trace(go.Scatter(
                name="% Patuh", x=tren["Bulan"], y=tren["Pct"],
                mode="lines+markers", yaxis="y2",
                line=dict(color="#4F46E5", width=2),
                marker=dict(size=7, color="#4F46E5"),
            ))
            fig.update_layout(
                barmode="stack", height=400,
                yaxis2=dict(overlaying="y", side="right", range=[0, 130], ticksuffix="%"),
                plot_bgcolor="white", paper_bgcolor="white",
            )
            st.plotly_chart(fig, use_container_width=True)

    # Tab Line Chart (hanya Semua Bulan)
    if mode == "Semua Bulan":
        with tab2:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                name="Patuh", x=tren["Bulan"], y=tren["Patuh"],
                mode="lines+markers", line=dict(color="#10B981", width=2),
                fill="tozeroy", fillcolor="rgba(16,185,129,0.1)",
            ))
            fig.add_trace(go.Scatter(
                name="Tidak Patuh", x=tren["Bulan"], y=tren["Tidak_Patuh"],
                mode="lines+markers", line=dict(color="#EF4444", width=2),
                fill="tozeroy", fillcolor="rgba(239,68,68,0.08)",
            ))
            fig.update_layout(height=380, plot_bgcolor="white", paper_bgcolor="white")
            st.plotly_chart(fig, use_container_width=True)

        with tab3:
            pivot = pd.DataFrame({
                "Patuh":       tren["Patuh"].values,
                "Tidak Patuh": tren["Tidak_Patuh"].values,
                "% Patuh":     tren["Pct"].values,
            }, index=tren["Bulan"].values).T

            fig = go.Figure(go.Heatmap(
                z=pivot.values, x=pivot.columns.tolist(), y=pivot.index.tolist(),
                colorscale=[[0, "#ECFDF5"], [0.5, "#FEF9C3"], [1, "#991B1B"]],
                text=pivot.values, texttemplate="%{text}", textfont=dict(size=12),
            ))
            fig.update_layout(height=280, margin=dict(l=120))
            st.plotly_chart(fig, use_container_width=True)

    # Tab Tabel (selalu ada, posisi terakhir)
    with (tab2 if mode == "Per Bulan" else tab4):
        st.subheader(f"Detail Kepatuhan per Teknisi — {label}")
        tabel_rekap = rekap.rename(columns={
            "TEKNISI":     "Teknisi",
            "Tidak_Patuh": "Tidak Patuh",
            "Total":       "Total Hari",
        })
        st.dataframe(
            tabel_rekap.style
            .background_gradient(subset=["% Patuh"], cmap="RdYlGn", vmin=0, vmax=100)
            .format({"% Patuh": "{:.1f}%"}),
            use_container_width=True,
            hide_index=True,
        )

        # Info teknisi terbaik & terburuk
        if len(rekap) >= 2:
            terbaik = rekap.iloc[0]
            terburuk = rekap.iloc[-1]
            st.success(f"🏆 Terbaik: **{terbaik['TEKNISI']}** — {terbaik['% Patuh']}% patuh")
            st.warning(f"⚠️ Perlu perhatian: **{terburuk['TEKNISI']}** — {terburuk['% Patuh']}% patuh")
