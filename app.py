import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Jurnal Guru Pancasila", layout="wide")

# --- KONEKSI GOOGLE SHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)

# --- GANTI LINK DI BAWAH INI DENGAN LINK GOOGLE SHEETS BAPAK/IBU ---
URL_SHEET = "https://docs.google.com/spreadsheets/d/1hB5bipwoyv6VHHk2Cc1HfPYyknVV-y0WLx0Os5h1Ypg/edit?usp=drive_link"

# --- DATA MASTER SISWA ---
DAFTAR_SISWA = {
    "Kelas 7": ["AHMAD DHANI SAPUTRA", "KHAIRUL IBRAHIM", "MUHAMMAD ARDI", "MUHAMMAD FADHIL FADKHULURRAHMAN", "MUHAMMAD RIFA ALIF", "MUHAMMAD RIFKY", "MUHAMMAD ROBY", "RAFI'I HAMDI", "ROMIZAH"],
    "Kelas 8": ["MAULANA REZKI", "NESYA AULIA PUTRI", "RAHMAD HIDAYATULLAH", "SYARIF HIDAYAT"],
    "Kelas 9": ["AHMAD MUHAJIR", "JAUHAR LATIFFAH", "MUHAMMAD ANSARI", "MUHAMMAD HAFIDZ NAUFAL", "MUHAMMAD ILYAS"]
}

# --- TEMA TAMPILAN ---
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: white; }
    [data-testid="stSidebar"] { background-color: #112244; }
    .stButton>button { background-color: #2563eb; color: white; border-radius: 8px; width: 100%; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNGSI AMBIL DATA ---
def ambil_data(worksheet_name):
    try:
        # Menambahkan parameter ttl=0 agar data selalu segar (tidak tersimpan di cache)
        return conn.read(spreadsheet=URL_SHEET, worksheet=worksheet_name, ttl=0)
    except:
        return pd.DataFrame()

# --- FUNGSI SIMPAN DATA ---
def simpan_data(df_baru, worksheet_name):
    df_lama = ambil_data(worksheet_name)
    if not df_lama.empty:
        # Gabungkan data lama dengan data baru
        df_final = pd.concat([df_lama, df_baru], ignore_index=True)
    else:
        df_final = df_baru
    
    # Bersihkan baris kosong jika ada
    df_final = df_final.dropna(how='all')
    
    # Kirim ke Google Sheets
    conn.update(spreadsheet=URL_SHEET, worksheet=worksheet_name, data=df_final)
    st.cache_data.clear()

# --- NAVIGASI UTAMA ---
st.sidebar.title("MENU UTAMA")
menu = st.sidebar.radio("Pilih Fitur:", ["📝 Jurnal & Mapel", "📊 Penilaian Siswa", "👨‍🏫 Wali Kelas 8"])

# --- 1. JURNAL & MAPEL ---
if menu == "📝 Jurnal & Mapel":
    st.header("Jurnal Mengajar & Presensi Mapel")
    t1, t2 = st.tabs(["➕ Isi Jurnal Baru", "📋 Rekap Jurnal & Materi"])
    
    with t1:
        kls = st.selectbox("Pilih Kelas", list(DAFTAR_SISWA.keys()))
        with st.form("form_jurnal"):
            c1, c2 = st.columns(2)
            tgl = c1.date_input("Tanggal", datetime.now())
            materi = c2.text_input("Materi Pembelajaran", placeholder="Contoh: Norma dan Keadilan")
            
            st.write("---")
            st.write(f"**Presensi Siswa {kls}:**")
            status_mapel = {}
            for nama in DAFTAR_SISWA[kls]:
                col_n, col_o = st.columns([2, 1])
                col_n.write(nama)
                status_mapel[nama] = col_o.radio(f"S-{nama}", ["H", "S", "I", "A"], horizontal=True, key=f"j_{nama}", label_visibility="collapsed")
            
            if st.form_submit_button("Simpan ke Google Sheets"):
                if not materi:
                    st.error("Materi harus diisi!")
                else:
                    # Ambil hanya siswa yang tidak hadir
                    absen = [f"{n}({s})" for n, s in status_mapel.items() if s != "
