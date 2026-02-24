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
            materi = c2.text_input("Materi Pembelajaran")
            
            st.write("---")
            st.write(f"**Presensi Siswa {kls}:**")
            
            status_mapel = {}
            for nama in DAFTAR_SISWA[kls]:
                col_n, col_o = st.columns([1, 2])
                col_n.write(f"{nama}")
                status_mapel[nama] = col_o.radio(f"S-{nama}", ["H", "S", "I", "A"], horizontal=True, key=f"m_{kls}_{nama}", label_visibility="collapsed")
            
            if st.form_submit_button("Simpan Jurnal & Absen"):
                if not materi:
                    st.error("Materi harus diisi!")
                else:
                    # LOGIKA BARU: Ambil hanya yang tidak hadir
                    tidak_hadir = [f"{nama} ({st})" for nama, st in status_mapel.items() if st != "H"]
                    ringkasan = ", ".join(tidak_hadir) if tidak_hadir else "Semua Hadir"
                    
                    simpan_data({
                        "Tanggal": str(tgl), 
                        "Kelas": kls, 
                        "Materi": materi, 
                        "Keterangan Absen": ringkasan,
                        "Detail": ", ".join([f"{n}({s})" for n, s in status_mapel.items()])
                    }, FILE_JURNAL)
                    st.success(f"✅ Jurnal Berhasil Disimpan!")

    with tab_rekap_jurnal:
        if os.path.isfile(FILE_JURNAL):
            df_j = pd.read_excel(FILE_JURNAL)
            df_j['Tanggal'] = pd.to_datetime(df_j['Tanggal']).dt.strftime('%d %b %Y')
            
            # Pengaman kolom jika ganti nama
            kolom = ["Tanggal", "Kelas", "Materi"]
            if "Keterangan Absen" in df_j.columns: kolom.append("Keterangan Absen")
            elif "Ringkasan Presensi" in df_j.columns: kolom.append("Ringkasan Presensi")

            f_kls_j = st.selectbox("Filter Kelas:", ["Semua"] + list(DAFTAR_SISWA.keys()), key="f_j")
            if f_kls_j != "Semua": df_j = df_j[df_j['Kelas'] == f_kls_j]
            
            st.dataframe(df_j[kolom], use_container_width=True)
        else:
            st.info("Belum ada data jurnal.")

# --- 2. PENILAIAN SISWA ---
elif menu == "📊 Penilaian Siswa":
    t1, t2, t3 = st.tabs(["➕ Input Nilai", "🔎 Rekap Nilai", "📉 Analisis KKM"])
    with t1:
        cx, cy = st.columns(2)
        k_n = cx.selectbox("Kelas Penilaian", list(DAFTAR_SISWA.keys()))
        j_d = cx.selectbox("Jenis Penilaian", ["Tugas", "UH", "PTS", "PAS"])
        m_p = cy.text_input("Materi Pokok / KD")
        lbl = hitung_urutan(k_n, j_d)
        cy.info(f"Label: **{lbl}**")
        with st.form("f_nilai"):
            list_n = []
            for nama in DAFTAR_SISWA[k_n]:
                cn, cs = st.columns([2, 1])
                cn.write(nama)
                skor = cs.number_input(f"Nilai {nama}", 0, 100, 0, key=f"v_{nama}")
                list_n.append({"Nama": nama, "Kelas": k_n, "Jenis Dasar": j_d, "Materi Pokok": m_p, "Jenis Spesifik": lbl, "Nilai": skor})
            if st.form_submit_button("Simpan"):
                simpan_data(list_n, FILE_NILAI); st.success("✅ Tersimpan!"); st.rerun()
    with t2:
        if os.path.isfile(FILE_NILAI):
            df_n = pd.read_excel(FILE_NILAI)
            f_k = st.selectbox("
