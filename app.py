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
# CSS GLOBAL
# =============================================================================

STYLE = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

:root {
    --c-bg:           #F8FAFC;
    --c-card:         #FFFFFF;
    --c-sidebar:      #E0F2FE;
    --c-sidebar-text: #0369A1;
    --c-primary:      #4F46E5;
    --c-accent:       #10B981;
    --c-danger:       #EF4444;
    --c-text-main:    #1E293B;
    --c-text-muted:   #64748B;
    --c-border:       #E2E8F0;
    --radius:         8px;
}

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
    color: var(--c-text-main) !important;
}

.stApp { background-color: var(--c-bg) !important; }

#MainMenu, footer, header {
    visibility: hidden;
}

.block-container {
    padding: 2rem !important;
    max-width: 1100px !important;
}

section[data-testid="stSidebar"] {
    background-color: var(--c-sidebar) !important;
    border-right: 1px solid #BAE6FD !important;
}

.stButton > button {
    background: var(--c-primary) !important;
    color: white !important;
    font-weight: 600 !important;
    border-radius: 6px !important;
    border: none !important;
    padding: 0.75rem 1rem !important;
    width: 100% !important;
}

.metric-card {
    background: var(--c-card);
    border: 1px solid var(--c-border);
    border-radius: var(--radius);
    padding: 1rem;
    text-align: center;
}

.metric-value {
    font-size: 1.8rem;
    font-weight: 700;
    color: var(--c-primary);
}

.metric-label {
    font-size: 0.8rem;
    color: var(--c-text-muted);
    margin-top: 0.25rem;
}

.result-card {
    border-radius: 8px;
    padding: 1.5rem;
    margin-top: 1rem;
    text-align: center;
}

.result-card.patuh {
    background: #ECFDF5;
    border: 1px solid #A7F3D0;
}

.result-card.tidak-patuh {
    background: #FEF2F2;
    border: 1px solid #FECACA;
}

.result-status {
    font-size: 1.8rem;
    font-weight: 800;
}

.violation-box {
    background: #FEF2F2;
    border: 1px solid #FECACA;
    border-radius: 6px;
    padding: 1rem;
    margin-top: 1rem;
    color: #991B1B;
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
        model = pickle.load(open("model_svm.pkl", "rb"))
        scaler = pickle.load(open("scaler.pkl", "rb"))
        le_teknisi = pickle.load(open("le_teknisi.pkl", "rb"))
        return model, scaler, le_teknisi
    except:
        return None, None, None


@st.cache_data
def load_data():

    df = pd.read_excel(
        "data/ALL IN OUT SO PNK 2021 - 2025.xlsx",
        engine="openpyxl"
    )

    df.columns = df.columns.str.strip().str.upper()

    df = df.dropna(subset=["TANGGAL", "TEKNISI", "TIPE"])

    df["TANGGAL"] = pd.to_datetime(df["TANGGAL"])

    return df


model, scaler, le_teknisi = load_models()
df = load_data()

# =============================================================================
# BATAS PENGAMBILAN
# =============================================================================

BATAS_PER_TIPE = 3

# =============================================================================
# HELPER
# =============================================================================

def render_metric_card(icon, value, label):

    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-value">{icon} {value}</div>
            <div class="metric-label">{label}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_prediction_result(pred, teknisi, keterangan, violations=None):

    if pred == 0:
        css_class = "patuh"
        status = "PATUH"
        icon = "✅"
    else:
        css_class = "tidak-patuh"
        status = "TIDAK PATUH"
        icon = "⚠️"

    st.markdown(
        f"""
        <div class="result-card {css_class}">
            <div class="result-status">{icon} {status}</div>
            <br>
            Teknisi <strong>{teknisi}</strong>
            <br>
            <small>{keterangan}</small>
        </div>
        """,
        unsafe_allow_html=True
    )

    if violations:

        detail = " | ".join(
            [
                f"{tipe}: {jumlah}x"
                for tipe, jumlah in violations
            ]
        )

# =============================================================================
# ENCODE TEKNISI
# =============================================================================

def encode_teknisi(nama):

    if le_teknisi is None:
        return 0

    try:
        return int(le_teknisi.transform([nama])[0])
    except:
        return 0

# =============================================================================
# LOGIKA PREDIKSI (SUDAH DIPERBAIKI)
# =============================================================================

def predict_from_detail(df_harian):

    """
    PATUH:
        Semua tipe <= 3

    TIDAK PATUH:
        Ada tipe > 3
    """

    violations = []

    if df_harian.empty:
        return 0, violations

    # Hitung jumlah per tipe
    per_tipe = df_harian.groupby("TIPE").size()

    # Cek pelanggaran
    for tipe, jumlah in per_tipe.items():

        if jumlah > BATAS_PER_TIPE:

            violations.append(
                (tipe, int(jumlah))
            )

    # Jika ada pelanggaran
    if violations:
        return 1, violations

    # Jika semua aman
    return 0, violations

# =============================================================================
# FUNCTION PREDICT UNTUK REKAP
# =============================================================================

def predict(jumlah_tipe, total_pengambilan, enc_teknisi):
    """
    Rule:
    PATUH  -> semua tipe <= BATAS_PER_TIPE
    TIDAK PATUH -> jika jumlah pengambilan melebihi batas
    """

    if total_pengambilan > (jumlah_tipe * BATAS_PER_TIPE):
        return 1  # Tidak Patuh

    return 0  # Patuh

# =============================================================================
# SIDEBAR
# =============================================================================

st.sidebar.title("🛠️ Dashboard Kepatuhan Teknisi")
st.sidebar.write("SIDEBAR BERHASIL")

menu = st.sidebar.radio(
    "Menu",
    ["📊 Monitoring", "📈 Rekap Kepatuhan"]
)

# =============================================================================
# HALAMAN MONITORING
# =============================================================================

if menu == "📊 Monitoring":

    st.title("📊 Monitoring Kepatuhan Teknisi")
    teknisi_list = sorted(df["TEKNISI"].unique())
    teknisi = st.selectbox("Pilih Teknisi", teknisi_list)

    df_teknisi = df[df["TEKNISI"] == teknisi]
    df_teknisi = df[
        df["TEKNISI"] == teknisi
    ]

    col1, col2, col3 = st.columns(3)

    with col1:

        tahun_list = sorted(
            df_teknisi["TANGGAL"].dt.year.unique(),
            reverse=True
        )

        tahun = st.selectbox(
            "Tahun",
            tahun_list
        )

    df_tahun = df_teknisi[
        df_teknisi["TANGGAL"].dt.year == tahun
    ]

    with col2:

        bulan_list = sorted(
            df_tahun["TANGGAL"].dt.month.unique()
        )

        bulan_nama = st.selectbox(
            "Bulan",
            [
                calendar.month_name[i]
                for i in bulan_list
            ]
        )

    bulan_idx = list(calendar.month_name).index(bulan_nama)

    df_bulan = df_tahun[
        df_tahun["TANGGAL"].dt.month == bulan_idx
    ]

    with col3:

        tanggal_list = sorted(
            df_bulan["TANGGAL"].dt.date.unique()
        )

        tanggal_pilih = st.selectbox(
            "Tanggal",
            tanggal_list
        )

    # =============================================================================
    # FILTER HARIAN
    # =============================================================================

    df_harian = df_bulan[
        df_bulan["TANGGAL"].dt.date == tanggal_pilih
    ]

    total_pengambilan = len(df_harian)

    jumlah_tipe = df_harian["TIPE"].nunique()

    # =============================================================================
    # METRIK
    # =============================================================================

    c1, c2, c3 = st.columns(3)

    with c1:
        render_metric_card(
            "📦",
            total_pengambilan,
            "Total Pengambilan"
        )

    with c2:
        render_metric_card(
            "🗂️",
            jumlah_tipe,
            "Jumlah Tipe"
        )

    with c3:
        render_metric_card(
            "📅",
            tanggal_pilih.strftime("%d-%m-%Y"),
            "Tanggal"
        )

    st.markdown("---")

    # =============================================================================
    # DETAIL TIPE
    # =============================================================================

    detail_tipe = (
        df_harian
        .groupby("TIPE")
        .size()
        .reset_index(name="JUMLAH")
    )

    st.subheader("📋 Detail Pengambilan per Tipe")

    st.dataframe(
        detail_tipe,
        use_container_width=True,
        hide_index=True
    )

    # =============================================================================
    # PREDIKSI
    # =============================================================================

    if st.button("🔍 JALANKAN MODEL SVM", use_container_width=True):

        pred, violations = predict_from_detail(df_harian)

        if pred == 0:

            ket = (
                f"Semua tipe material "
                f"≤ {BATAS_PER_TIPE} pengambilan"
            )

        else:

            ket = (
                f"Terdapat tipe material "
                f"melebihi batas {BATAS_PER_TIPE}"
            )

        render_prediction_result(
            pred,
            teknisi,
            ket,
            violations
        )


# =============================================================================
# HALAMAN: REKAP KEPATUHAN
# =============================================================================

elif menu == "📈 Rekap Kepatuhan":
    import plotly.graph_objects as go
    import plotly.express as px

    st.markdown(
        '<div class="page-header"><h1>📈 Rekap Kepatuhan Teknisi</h1></div>',
        unsafe_allow_html=True,
    )

    if df.empty:
        st.warning("Data tidak tersedia. Pastikan file Excel sudah ada.")
    else:
        # ── Filter ───────────────────────────────────────────────────────────
        col_f1, col_f2, col_f3 = st.columns([1, 1, 1])

        with col_f1:
            tahun_list_all = sorted(df["TANGGAL"].dt.year.unique(), reverse=True)
            tahun_rekap    = st.selectbox("Tahun", tahun_list_all, key="rekap_tahun")

        with col_f2:
            mode_filter = st.selectbox("Tampilkan", ["Per Bulan", "Semua Bulan"], key="rekap_mode")

        df_tahun_rekap = df[df["TANGGAL"].dt.year == tahun_rekap]

        if mode_filter == "Per Bulan":
            bulan_avail = sorted(df_tahun_rekap["TANGGAL"].dt.month.unique())
            with col_f3:
                bulan_nama_rekap = st.selectbox(
                    "Bulan",
                    [calendar.month_name[i] for i in bulan_avail],
                    key="rekap_bulan",
                )
            bulan_idx_rekap = list(calendar.month_name).index(bulan_nama_rekap)
            df_scope    = df_tahun_rekap[df_tahun_rekap["TANGGAL"].dt.month == bulan_idx_rekap]
            scope_label = f"{bulan_nama_rekap} {tahun_rekap}"
        else:
            df_scope    = df_tahun_rekap
            scope_label = f"Tahun {tahun_rekap}"

        # ── Agregasi & Prediksi ───────────────────────────────────────────────
        if df_scope.empty:
            st.info("Tidak ada data untuk filter yang dipilih.")
        else:
            agg = (
                df_scope.groupby(["TEKNISI", df_scope["TANGGAL"].dt.date])
                .agg(
                    total_pengambilan=("TIPE", "count"),
                    jumlah_tipe=("TIPE", "nunique"),
                )
                .reset_index()
            )
            agg.columns = ["TEKNISI", "TANGGAL", "TOTAL", "TIPE"]

            def encode_tek(nama):
                try:
                    return int(le_teknisi.transform([nama])[0])
                except Exception:
                    return 0

            agg["ENC"]  = agg["TEKNISI"].apply(encode_tek)
            agg["PRED"] = agg.apply(
                lambda r: predict(int(r["TIPE"]), int(r["TOTAL"]), int(r["ENC"])), axis=1
            )
            agg["BULAN"] = pd.to_datetime(agg["TANGGAL"]).dt.month

            rekap = (
                agg.groupby("TEKNISI")["PRED"]
                .agg(
                    Patuh=lambda x: (x == 0).sum(),
                    Tidak_Patuh=lambda x: (x == 1).sum(),
                )
                .reset_index()
            )
            rekap["Total_Hari"] = rekap["Patuh"] + rekap["Tidak_Patuh"]
            rekap["Pct_Patuh"]  = (rekap["Patuh"] / rekap["Total_Hari"] * 100).round(1)
            rekap = rekap.sort_values("Patuh", ascending=False).reset_index(drop=True)

            total_patuh = int(rekap["Patuh"].sum())
            total_tidak = int(rekap["Tidak_Patuh"].sum())
            total_semua = total_patuh + total_tidak
            pct_overall = round(total_patuh / total_semua * 100, 1) if total_semua else 0

            st.markdown(f"**Periode:** {scope_label} &nbsp;·&nbsp; {len(rekap)} teknisi aktif")
            st.markdown("<br>", unsafe_allow_html=True)

            m1, m2, m3, m4 = st.columns(4)
            with m1:
                render_metric_card("✅", total_patuh, "Hari Patuh")
            with m2:
                render_metric_card("⚠️", total_tidak, "Hari Tidak Patuh")
            with m3:
                render_metric_card("📅", total_semua, "Total Hari Kerja")
            with m4:
                render_metric_card("📊", f"{pct_overall}%", "Tingkat Kepatuhan")

            st.markdown("<br>", unsafe_allow_html=True)

            # ── TAB — dinamis sesuai mode filter ─────────────────────────────
            if mode_filter == "Per Bulan":
                tab_labels = ["📊 Stacked Bar", "📋 Tabel Detail"]
            else:
                tab_labels = ["📊 Stacked Bar", "📈 Line Chart", "🔥 Heatmap", "📋 Tabel Detail"]

            tabs = st.tabs(tab_labels)

            # Data agregat per bulan
            tren = (
                agg.groupby("BULAN")["PRED"]
                .agg(
                    Patuh=lambda x: (x == 0).sum(),
                    Tidak_Patuh=lambda x: (x == 1).sum(),
                )
                .reset_index()
            )
            tren["Nama_Bulan"]      = tren["BULAN"].apply(lambda m: calendar.month_name[m])
            tren["Nama_Bulan_Abbr"] = tren["BULAN"].apply(lambda m: calendar.month_abbr[m])
            tren["Total"] = tren["Patuh"] + tren["Tidak_Patuh"]
            tren["Pct"]   = (tren["Patuh"] / tren["Total"] * 100).round(1)

            # ── TAB 1: STACKED BAR ────────────────────────────────────────────
            with tabs[0]:
                if mode_filter == "Per Bulan":
                    patuh_val = int(rekap["Patuh"].sum())
                    tdk_val   = int(rekap["Tidak_Patuh"].sum())
                    fig_stack = go.Figure()
                    fig_stack.add_trace(go.Bar(
                        name="Patuh", x=[scope_label], y=[patuh_val],
                        marker_color="#10B981", marker_line_width=0,
                        text=[patuh_val], textposition="inside",
                        textfont=dict(color="white", size=13), width=0.4,
                    ))
                    fig_stack.add_trace(go.Bar(
                        name="Tidak Patuh", x=[scope_label], y=[tdk_val],
                        marker_color="#EF4444", marker_line_width=0,
                        text=[tdk_val], textposition="inside",
                        textfont=dict(color="white", size=13), width=0.4,
                    ))
                    fig_stack.update_layout(
                        barmode="stack",
                        title=dict(text=f"Kepatuhan Keseluruhan — {scope_label}",
                                   font=dict(size=14, family="Inter")),
                        xaxis=dict(tickfont=dict(size=12)),
                        yaxis=dict(title="Jumlah Hari", gridcolor="#F1F5F9"),
                        legend=dict(orientation="h", yanchor="bottom", y=1.02,
                                    xanchor="right", x=1, font=dict(size=12)),
                        plot_bgcolor="white", paper_bgcolor="white",
                        font=dict(family="Inter", size=12),
                        margin=dict(t=70, b=60, l=50, r=20), height=400,
                    )
                    st.plotly_chart(fig_stack, use_container_width=True)
                    st.info(f"📌 Total **{patuh_val}** hari patuh dan **{tdk_val}** hari tidak patuh pada {scope_label}.")

                else:
                    fig_stack = go.Figure()
                    fig_stack.add_trace(go.Bar(
                        name="Patuh", x=tren["Nama_Bulan_Abbr"], y=tren["Patuh"],
                        marker_color="#10B981", marker_line_width=0,
                        text=tren["Patuh"], textposition="inside",
                        textfont=dict(color="white", size=11),
                        customdata=tren["Pct"],
                        hovertemplate="<b>%{x}</b><br>Patuh: %{y} hari<br>Tingkat Patuh: %{customdata}%<extra></extra>",
                    ))
                    fig_stack.add_trace(go.Bar(
                        name="Tidak Patuh", x=tren["Nama_Bulan_Abbr"], y=tren["Tidak_Patuh"],
                        marker_color="#EF4444", marker_line_width=0,
                        text=tren["Tidak_Patuh"], textposition="inside",
                        textfont=dict(color="white", size=11),
                        hovertemplate="<b>%{x}</b><br>Tidak Patuh: %{y} hari<extra></extra>",
                    ))
                    fig_stack.add_trace(go.Scatter(
                        name="% Patuh", x=tren["Nama_Bulan_Abbr"], y=tren["Pct"],
                        mode="lines+markers+text", yaxis="y2",
                        line=dict(color="#4F46E5", width=2, dash="dot"),
                        marker=dict(size=7, color="#4F46E5"),
                        text=[f"{v}%" for v in tren["Pct"]],
                        textposition="top center",
                        textfont=dict(size=9, color="#4F46E5"),
                    ))
                    fig_stack.update_layout(
                        barmode="stack",
                        title=dict(text=f"Stacked Bar Kepatuhan per Bulan — Tahun {tahun_rekap}",
                                   font=dict(size=14, family="Inter")),
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
                    st.plotly_chart(fig_stack, use_container_width=True)
                    bulan_terburuk = tren.loc[tren["Tidak_Patuh"].idxmax(), "Nama_Bulan"]
                    bulan_terbaik  = tren.loc[tren["Patuh"].idxmax(), "Nama_Bulan"]
                    st.info(f"📌 Bulan paling banyak pelanggaran: **{bulan_terburuk}** · Bulan paling patuh: **{bulan_terbaik}**")

            # ── TAB 2 & 3: hanya Semua Bulan ─────────────────────────────────
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
                        fill="tozeroy", fillcolor="rgba(16,185,129,0.10)",
                        hovertemplate="<b>%{x}</b><br>Patuh: %{y} hari<extra></extra>",
                    ))
                    fig_line.add_trace(go.Scatter(
                        name="Tidak Patuh", x=tren["Nama_Bulan_Abbr"], y=tren["Tidak_Patuh"],
                        mode="lines+markers+text",
                        line=dict(color="#EF4444", width=2.5),
                        marker=dict(size=9, color="#EF4444", line=dict(color="white", width=1.5)),
                        text=tren["Tidak_Patuh"], textposition="top center",
                        textfont=dict(size=10, color="#DC2626"),
                        fill="tozeroy", fillcolor="rgba(239,68,68,0.08)",
                        hovertemplate="<b>%{x}</b><br>Tidak Patuh: %{y} hari<extra></extra>",
                    ))
                    fig_line.update_layout(
                        title=dict(text=f"Tren Kepatuhan per Bulan — Tahun {tahun_rekap}",
                                   font=dict(size=14, family="Inter")),
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
                            [0.0,  "#F0FDF4"],
                            [0.33, "#BBF7D0"],
                            [0.66, "#FEF9C3"],
                            [1.0,  "#991B1B"],
                        ],
                        colorbar=dict(
                            title=dict(text="Jumlah Hari"),
                            tickfont=dict(size=10),
                        ),
                        text=heat_pivot.values,
                        texttemplate="%{text}",
                        textfont=dict(size=12, color="black"),
                        hovertemplate="Bulan: %{x}<br>%{y}: %{z}<extra></extra>",
                    ))
                    fig_heat.update_layout(
                        title=dict(text=f"Heatmap Kepatuhan per Bulan — Tahun {tahun_rekap}",
                                   font=dict(size=14, family="Inter")),
                        xaxis=dict(title="Bulan", tickfont=dict(size=11), side="bottom"),
                        yaxis=dict(title="", tickfont=dict(size=12), autorange="reversed"),
                        font=dict(family="Inter", size=12),
                        margin=dict(t=70, b=60, l=130, r=20),
                        height=300,
                        plot_bgcolor="white", paper_bgcolor="white",
                    )
                    st.plotly_chart(fig_heat, use_container_width=True)
                    st.caption("🟢 Hijau = nilai tinggi · 🟡 Kuning = sedang · 🔴 Merah = rendah/banyak pelanggaran")

            # ── TAB TERAKHIR: TABEL DETAIL ────────────────────────────────────
            with tabs[-1]:
                display_df = rekap.rename(columns={
                    "TEKNISI":     "Teknisi",
                    "Patuh":       "Hari Patuh",
                    "Tidak_Patuh": "Hari Tidak Patuh",
                    "Total_Hari":  "Total Hari",
                    "Pct_Patuh":   "% Patuh",
                })
                st.dataframe(
                    display_df.style.background_gradient(
                        subset=["% Patuh"], cmap="RdYlGn", vmin=0, vmax=100
                    ).format({"% Patuh": "{:.1f}%"}),
                    use_container_width=True,
                    hide_index=True,
                )
