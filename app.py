import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- TEMA DARK MODE ---
def local_css():
    st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    [data-testid="stSidebar"] { background-color: #112244; }
    h1, h2, h3, p, label { color: #ffffff !important; }
    .stRadio > div { flex-direction: row; gap: 10px; }
    .stRadio label { 
        background-color: #262730; padding: 5px 15px; border-radius: 5px; 
        border: 1px solid #3e4149; cursor: pointer; color: white !important;
    }
    input, select, textarea, [data-baseweb="select"] {
        background-color: #262730 !important;
        color: #ffffff !important;
        border: 1px solid #2563eb !important;
    }
    .stButton>button { 
        background-color: #2563eb; color: white; font-weight: bold; 
        border-radius: 8px; width: 100%; height: 3em;
    }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #112244; border-radius: 5px; padding: 10px; color: white;
    }
    </style>
    """, unsafe_allow_html=True)

local_css()

# --- DATABASE FILES ---
FILE_JURNAL = "data_jurnal_pancasila.xlsx"
FILE_NILAI = "data_nilai_pancasila.xlsx"
FILE_ABSEN_WALI = "data_absen_walikelas_8.xlsx"

# --- DATA MASTER SISWA ---
DAFTAR_SISWA = {
    "Kelas 7": ["AHMAD DHANI SAPUTRA", "KHAIRUL IBRAHIM", "MUHAMMAD ARDI", "MUHAMMAD FADHIL FADKHULURRAHMAN", "MUHAMMAD RIFA ALIF", "MUHAMMAD RIFKY", "MUHAMMAD ROBY", "RAFI'I HAMDI", "ROMIZAH"],
    "Kelas 8": ["MAULANA REZKI", "NESYA AULIA PUTRI", "RAHMAD HIDAYATULLAH", "SYARIF HIDAYAT"],
    "Kelas 9": ["AHMAD MUHAJIR", "JAUHAR LATIFFAH", "MUHAMMAD ANSARI", "MUHAMMAD HAFIDZ NAUFAL", "MUHAMMAD ILYAS"]
}

# --- FUNGSI SIMPAN ---
def simpan_data(data, nama_file):
    df_baru = pd.DataFrame(data) if isinstance(data, list) else pd.DataFrame([data])
    if not os.path.isfile(nama_file):
        df_baru.to_excel(nama_file, index=False)
    else:
        df_lama = pd.read_excel(nama_file)
        pd.concat([df_lama, df_baru], ignore_index=True).to_excel(nama_file, index=False)

def hitung_urutan(kelas, jenis_dasar):
    if not os.path.isfile(FILE_NILAI): return f"{jenis_dasar} 1"
    df = pd.read_excel(FILE_NILAI)
    if "Jenis Dasar" not in df.columns: return f"{jenis_dasar} 1"
    data_ada = df[(df["Kelas"] == kelas) & (df["Jenis Dasar"] == jenis_dasar)]
    return f"{jenis_dasar} {data_ada['Jenis Spesifik'].nunique() + 1}"

# --- NAVIGASI UTAMA ---
st.sidebar.title("MENU UTAMA")
menu = st.sidebar.radio("Pilih Fitur:", ["📝 Jurnal & Mapel", "📊 Penilaian Siswa", "👨‍🏫 Wali Kelas 8"])

# --- 1. JURNAL & MAPEL ---
if menu == "📝 Jurnal & Mapel":
    st.header("Jurnal Mengajar & Presensi Mapel")
    
    tab_isi, tab_rekap_jurnal = st.tabs(["➕ Isi Jurnal Baru", "📋 Rekap Jurnal & Materi"])
    
    with tab_isi:
        kls = st.selectbox("Pilih Kelas", list(DAFTAR_SISWA.keys()))
        with st.form("form_jurnal"):
            c1, c2 = st.columns(2)
            tgl = c1.date_input("Tanggal", datetime.now())
            materi = c2.text_input("Materi Pembelajaran", placeholder="Misal: Pancasila sebagai Dasar Negara")
            
            st.write("---")
            st.write(f"**Presensi Siswa {kls}:**")
            
            status_mapel = {}
            for nama in DAFTAR_SISWA[kls]:
                col_n, col_o = st.columns([1, 2])
                col_n.write(f"{nama}")
                status_mapel[nama] = col_o.radio(
                    f"S-{nama}", ["H", "S", "I", "A"], 
                    horizontal=True, key=f"m_{kls}_{nama}", 
                    label_visibility="collapsed"
                )
            
            if st.form_submit_button("Simpan Jurnal & Absen"):
                if not materi:
                    st.error("Materi harus diisi!")
                else:
                    # Membuat string singkat untuk presensi (H:8, S:1, dst)
                    stats = list(status_mapel.values())
                    ringkasan_abs = f"H:{stats.count('H')}, S:{stats.count('S')}, I:{stats.count('I')}, A:{stats.count('A')}"
                    
                    simpan_data({
                        "Tanggal": str(tgl), 
                        "Kelas": kls, 
                        "Materi": materi, 
                        "Ringkasan Presensi": ringkasan_abs,
                        "Detail Presensi": ", ".join([f"{n}({s})" for n, s in status_mapel.items()])
                    }, FILE_JURNAL)
                    st.success(f"✅ Jurnal {kls} Berhasil Disimpan!")

    with tab_rekap_jurnal:
        if os.path.isfile(FILE_JURNAL):
            df_j = pd.read_excel(FILE_JURNAL)
            df_j['Tanggal'] = pd.to_datetime(df_j['Tanggal']).dt.strftime('%d %b %Y')
            
            c_f1, c_f2 = st.columns([1, 2])
            f_kls_j = c_f1.selectbox("Filter Kelas:", ["Semua"] + list(DAFTAR_SISWA.keys()))
            cari_materi = c_f2.text_input("🔍 Cari Materi:", placeholder="Ketik judul materi...")
            
            # Filter Logika
            if f_kls_j != "Semua":
                df_j = df_j[df_j['Kelas'] == f_kls_j]
            if cari_materi:
                df_j = df_j[df_j['Materi'].str.contains(cari_materi, case=False, na=False)]
            
            if not df_j.empty:
                st.dataframe(df_j[["Tanggal", "Kelas", "Materi", "Ringkasan Presensi"]], use_container_width=True)
                
                with st.expander("Lihat Detail Presensi Per Siswa"):
                    st.table(df_j[["Tanggal", "Materi", "Detail Presensi"]])
            else:
                st.warning("Data jurnal tidak ditemukan.")
        else:
            st.info("Belum ada riwayat jurnal.")

# --- 2. PENILAIAN SISWA (Tetap Sama) ---
elif menu == "📊 Penilaian Siswa":
    t1, t2, t3 = st.tabs(["➕ Input Nilai", "🔎 Rekap Nilai", "📉 Analisis KKM"])
    
    with t1:
        with st.expander("Form Input Nilai Baru", expanded=True):
            cx, cy = st.columns(2)
            k_n = cx.selectbox("Pilih Kelas Penilaian", list(DAFTAR_SISWA.keys()))
            j_d = cx.selectbox("Jenis Penilaian", ["Tugas", "UH", "PTS", "PAS"])
            m_p = cy.text_input("Materi Pokok / KD")
            lbl = hitung_urutan(k_n, j_d)
            cy
