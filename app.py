import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="Jurnal Guru Pancasila", layout="wide")

# Koneksi otomatis menggunakan Secrets [connections.gsheets]
conn = st.connection("gsheets", type=GSheetsConnection)

# GANTI LINK DI BAWAH INI DENGAN LINK BARU HASIL "SAVE AS GOOGLE SHEETS"
URL_SHEET = "https://docs.google.com/spreadsheets/d/1M8ZQzyinx2ur0c4SR-JrARoe5LsAMRf-9-zU9vUi2-k/edit?gid=92340672#gid=92340672"

DAFTAR_SISWA = {
    "Kelas 7": ["AHMAD DHANI SAPUTRA", "KHAIRUL IBRAHIM", "MUHAMMAD ARDI", "MUHAMMAD FADHIL FADKHULURRAHMAN", "MUHAMMAD RIFA ALIF", "MUHAMMAD RIFKY", "MUHAMMAD ROBY", "RAFI'I HAMDI", "ROMIZAH"],
    "Kelas 8": ["MAULANA REZKI", "NESYA AULIA PUTRI", "RAHMAD HIDAYATULLAH", "SYARIF HIDAYAT"],
    "Kelas 9": ["AHMAD MUHAJIR", "JAUHAR LATIFFAH", "MUHAMMAD ANSARI", "MUHAMMAD HAFIDZ NAUFAL", "MUHAMMAD ILYAS"]
}

def ambil_data(worksheet_name):
    try:
        return conn.read(spreadsheet=URL_SHEET, worksheet=worksheet_name, ttl=0)
    except:
        return pd.DataFrame()

def simpan_data(df_baru, worksheet_name):
    try:
        df_lama = ambil_data(worksheet_name)
        df_final = pd.concat([df_lama, df_baru], ignore_index=True) if not df_lama.empty else df_baru
        conn.update(spreadsheet=URL_SHEET, worksheet=worksheet_name, data=df_final)
        st.cache_data.clear()
        return True
    except Exception as e:
        st.error(f"Error: {e}")
        return False

st.sidebar.title("MENU UTAMA")
menu = st.sidebar.radio("Pilih Fitur:", ["📝 Jurnal", "📊 Nilai", "👨‍🏫 Wali Kelas"])

if menu == "📝 Jurnal":
    st.header("Jurnal Mengajar")
    kls = st.selectbox("Pilih Kelas", list(DAFTAR_SISWA.keys()))
    with st.form("f_jurnal"):
        tgl = st.date_input("Tanggal", datetime.now())
        materi = st.text_input("Materi Pembelajaran")
        status = {n: st.radio(n, ["H", "S", "I", "A"], horizontal=True) for n in DAFTAR_SISWA[kls]}
        if st.form_submit_button("Simpan"):
            absen = ", ".join([f"{n}({s})" for n, s in status.items() if s != "H"])
            df = pd.DataFrame([{"Tanggal": str(tgl), "Kelas": kls, "Materi": materi, "Absen": absen}])
            if simpan_data(df, "Jurnal"): st.success("Tersimpan!")

elif menu == "📊 Nilai":
    st.header("Input Nilai")
    kls = st.selectbox("Kelas", list(DAFTAR_SISWA.keys()))
    with st.form("f_nilai"):
        mat = st.text_input("Materi")
        nilai_data = []
        for n in DAFTAR_SISWA[kls]:
            skor = st.number_input(f"Nilai {n}", 0, 100, 75)
            nilai_data.append({"Tanggal": str(datetime.now().date()), "Nama": n, "Kelas": kls, "Materi": mat, "Nilai": skor})
        if st.form_submit_button("Simpan Nilai"):
            if simpan_data(pd.DataFrame(nilai_data), "Nilai"): st.success("Nilai Masuk!")

elif menu == "👨‍🏫 Wali Kelas":
    st.header("Absensi Kelas 8")
    with st.form("f_wk"):
        tgl = st.date_input("Tanggal", datetime.now())
        data_w = [{"Tanggal": str(tgl), "Nama": n, "Status": st.radio(n, ["H", "S", "I", "A"], horizontal=True)} for n in DAFTAR_SISWA["Kelas 8"]]
        if st.form_submit_button("Simpan"):
            if simpan_data(pd.DataFrame(data_w), "AbsenWali"): st.success("Wali Kelas Aman!")
