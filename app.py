import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Jurnal Guru Pancasila", layout="wide")

# --- 2. KONEKSI GOOGLE SHEETS ---
# Kita buat koneksi standar tanpa memasukkan kunci ke dalam fungsi cache
conn = st.connection("gsheets", type=GSheetsConnection)

# --- 4. FUNGSI AMBIL DATA ---
def ambil_data(worksheet_name):
    try:
        # Kita hapus parameter ttl agar tidak terjadi UnhashableParamError
        return conn.read(
            spreadsheet=URL_SHEET, 
            worksheet=worksheet_name,
            service_account_info=st.secrets["gcp_service_account"]
        )
    except:
        return pd.DataFrame()

# --- 5. FUNGSI SIMPAN DATA ---
def simpan_data(df_baru, worksheet_name):
    try:
        df_lama = ambil_data(worksheet_name)
        if not df_lama.empty:
            df_final = pd.concat([df_lama, df_baru], ignore_index=True)
        else:
            df_final = df_baru
            
        # Tambahkan service_account_info di sini juga untuk izin menulis
        conn.update(
            spreadsheet=URL_SHEET, 
            worksheet=worksheet_name, 
            data=df_final,
            service_account_info=st.secrets["gcp_service_account"]
        )
        st.cache_data.clear()
        return True
    except Exception as e:
        st.error(f"Gagal menyimpan: {e}")
        return False

# --- 6. NAVIGASI ---
st.sidebar.title("MENU UTAMA")
menu = st.sidebar.radio("Pilih Fitur:", ["📝 Jurnal & Mapel", "📊 Penilaian Siswa", "👨‍🏫 Wali Kelas 8"])

# --- 7. LOGIKA MENU ---
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
                if materi:
                    absen = [f"{n}({s})" for n, s in status_mapel.items() if s != "H"]
                    ringkasan = ", ".join(absen) if absen else "Semua Hadir"
                    df_j = pd.DataFrame([{"Tanggal": str(tgl), "Kelas": kls, "Materi": materi, "Keterangan Absen": ringkasan}])
                    if simpan_data(df_j, "Jurnal"):
                        st.success("✅ Data Jurnal Berhasil Tersimpan!")
                else:
                    st.warning("Materi tidak boleh kosong!")

    with t2:
        df_view = ambil_data("Jurnal")
        if not df_view.empty:
            st.dataframe(df_view, use_container_width=True)
        else: st.info("Belum ada data di Google Sheets.")

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
            if simpan_data(pd.DataFrame(data_nilai), "Nilai"):
                st.success("✅ Nilai Berhasil Masuk!")

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
            if simpan_data(pd.DataFrame(data_w), "AbsenWali"):
                st.success("✅ Absensi Wali Kelas Aman!")


