import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Jurnal Guru Pancasila", layout="wide")

# --- KONEKSI GOOGLE SHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)

# --- MASUKKAN LINK GOOGLE SHEETS BAPAK/IBU DI SINI ---
URL_SHEET = "https://docs.google.com/spreadsheets/d/1VTZg1gLVmdfKCNsKOfDz9EVrqE2wEBGb/edit?usp=sharing&ouid=116065546011273727460&rtpof=true&sd=true"

# --- DATA MASTER SISWA ---
DAFTAR_SISWA = {
    "Kelas 7": ["AHMAD DHANI SAPUTRA", "KHAIRUL IBRAHIM", "MUHAMMAD ARDI", "MUHAMMAD FADHIL FADKHULURRAHMAN", "MUHAMMAD RIFA ALIF", "MUHAMMAD RIFKY", "MUHAMMAD ROBY", "RAFI'I HAMDI", "ROMIZAH"],
    "Kelas 8": ["MAULANA REZKI", "NESYA AULIA PUTRI", "RAHMAD HIDAYATULLAH", "SYARIF HIDAYAT"],
    "Kelas 9": ["AHMAD MUHAJIR", "JAUHAR LATIFFAH", "MUHAMMAD ANSARI", "MUHAMMAD HAFIDZ NAUFAL", "MUHAMMAD ILYAS"]
}

# --- FUNGSI AMBIL DATA ---
def ambil_data(worksheet_name):
    try:
        return conn.read(spreadsheet=URL_SHEET, worksheet=worksheet_name, ttl=0)
    except:
        return pd.DataFrame()

# --- FUNGSI SIMPAN DATA ---
# --- FUNGSI SIMPAN DATA (VERSI ANTI-ERROR) ---
def simpan_data(df_baru, worksheet_name):
    try:
        # 1. Coba ambil data lama dari Google Sheets
        df_lama = conn.read(spreadsheet=URL_SHEET, worksheet=worksheet_name, ttl=0)
        
        # 2. Jika ada data lama, gabungkan dengan data baru
        if df_lama is not None and not df_lama.empty:
            df_final = pd.concat([df_lama, df_baru], ignore_index=True)
        else:
            df_final = df_baru
    except Exception:
        # 3. Jika gagal baca (karena sheet dianggap kosong), langsung pakai data baru
        df_final = df_baru
    
    # 4. Kirim data final kembali ke Google Sheets
    # Pastikan nama worksheet (Jurnal, Nilai, atau AbsenWali) persis sama
    conn.update(spreadsheet=URL_SHEET, worksheet=worksheet_name, data=df_final)
    st.cache_data.clear()
# --- 1. JURNAL & MAPEL ---
if menu == "📝 Jurnal & Mapel":
    st.header("Jurnal Mengajar & Presensi")
    t1, t2 = st.tabs(["➕ Isi Jurnal", "📋 Rekap Jurnal"])
    
    with t1:
        kls = st.selectbox("Pilih Kelas", list(DAFTAR_SISWA.keys()))
        with st.form("f_jurnal"):
            tgl = st.date_input("Tanggal", datetime.now())
            materi = st.text_input("Materi Pembelajaran")
            st.write("---")
            status_mapel = {}
            for nama in DAFTAR_SISWA[kls]:
                c_n, c_o = st.columns([2, 1])
                c_n.write(nama)
                status_mapel[nama] = c_o.radio(f"S-{nama}", ["H", "S", "I", "A"], horizontal=True, key=f"j_{nama}", label_visibility="collapsed")
            
            if st.form_submit_button("Simpan ke Google Sheets"):
                absen = [f"{n}({s})" for n, s in status_mapel.items() if s != "H"]
                ringkasan = ", ".join(absen) if absen else "Semua Hadir"
                df_j = pd.DataFrame([{"Tanggal": str(tgl), "Kelas": kls, "Materi": materi, "Keterangan Absen": ringkasan}])
                simpan_data(df_j, "Jurnal")
                st.success("Data Berhasil Tersimpan!")

    with t2:
        df_view = ambil_data("Jurnal")
        if not df_view.empty:
            st.dataframe(df_view, use_container_width=True)
        else: st.info("Belum ada data di Google Sheets.")

# --- 2. PENILAIAN SISWA ---
elif menu == "📊 Penilaian Siswa":
    st.header("Penilaian Siswa")
    kls_n = st.selectbox("Pilih Kelas", list(DAFTAR_SISWA.keys()), key="kn")
    with st.form("f_nilai"):
        j_d = st.selectbox("Jenis", ["Tugas", "UH", "PTS", "PAS"])
        mat = st.text_input("Materi Pokok")
        data_nilai = []
        for nama in DAFTAR_SISWA[kls_n]:
            c_n, c_v = st.columns([2, 1])
            c_n.write(nama)
            skor = c_v.number_input(f"Nilai {nama}", 0, 100, 75, key=f"v_{nama}")
            data_nilai.append({"Tanggal": str(datetime.now().date()), "Nama": nama, "Kelas": kls_n, "Jenis": j_d, "Materi": mat, "Nilai": skor})
        if st.form_submit_button("Simpan Nilai"):
            simpan_data(pd.DataFrame(data_nilai), "Nilai")
            st.success("Nilai Masuk!")

# --- 3. WALI KELAS 8 ---
elif menu == "👨‍🏫 Wali Kelas 8":
    st.header("Absensi Wali Kelas 8")
    with st.form("f_wk"):
        tgl_w = st.date_input("Tanggal", datetime.now())
        data_w = []
        for nama in DAFTAR_SISWA["Kelas 8"]:
            c_n, c_s = st.columns([2, 1])
            c_n.write(nama)
            st_w = c_s.radio(f"S-{nama}", ["H", "S", "I", "A"], horizontal=True, key=f"w_{nama}", label_visibility="collapsed")
            data_w.append({"Tanggal": str(tgl_w), "Nama": nama, "Status": st_w})
        if st.form_submit_button("Simpan Absen Wali"):
            simpan_data(pd.DataFrame(data_w), "AbsenWali")
            st.success("Absensi Wali Kelas Aman!")




