import streamlit as st
import pandas as pd
from datetime import datetime
import calendar
import plotly.express as px
from streamlit_gsheets import GSheetsConnection

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Sistem Informasi Guru Pancasila", layout="wide", page_icon="📊")

# --- 2. KONEKSI GOOGLE SHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)
URL_SHEET = st.secrets["connections"]["gsheets"]["spreadsheet"]

# --- 3. DATA MASTER SISWA ---
DAFTAR_SISWA = {
    "Kelas 7": ["AHMAD DHANI SAPUTRA", "KHAIRUL IBRAHIM", "MUHAMMAD ARDI", "MUHAMMAD FADHIL FADKHULURRAHMAN", "MUHAMMAD RIFA ALIF", "MUHAMMAD RIFKY", "MUHAMMAD ROBY", "RAFI'I HAMDI", "ROMIZAH"],
    "Kelas 8": ["MAULANA REZKI", "NESYA AULIA PUTRI", "RAHMAD HIDAYATULLAH", "SYARIF HIDAYAT"],
    "Kelas 9": ["AHMAD MUHAJIR", "JAUHAR LATIFFAH", "MUHAMMAD ANSARI", "MUHAMMAD HAFIDZ NAUFAL", "MUHAMMAD ILYAS"]
}

# --- 4. FUNGSI AMBIL & SIMPAN ---
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
        st.error(f"Gagal menyimpan: {e}")
        return False

# --- TAMPILAN MENU ---
with st.sidebar:
    st.title("🛠️ MENU UTAMA")
    menu = st.selectbox("Pilih Fitur:", ["📝 Input Jurnal", "📊 Input Nilai Siswa", "👨‍🏫 Wali Kelas 8", "📂 Rekap Data"])

# --- FUNGSI PEMBANTU UNTUK FILTER TANGGAL ---
def filter_periode_ui(key_prefix):
    st.markdown("### 🗓️ Atur Periode Rekap")
    opsi = st.selectbox("Pilih Jenis Rekap:", ["Bulanan", "Persemester / Custom"], key=f"opsi_{key_prefix}")
    if opsi == "Bulanan":
        c1, c2 = st.columns(2)
        with c1:
            list_bulan = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
            bulan_nama = st.selectbox("Pilih Bulan:", list_bulan, index=datetime.now().month - 1, key=f"bln_{key_prefix}")
            bulan_angka = list_bulan.index(bulan_nama) + 1
        with c2:
            tahun = st.selectbox("Pilih Tahun:", [2024, 2025, 2026], index=1, key=f"thn_{key_prefix}")
        tgl_mulai = datetime(tahun, bulan_angka, 1).date()
        tgl_selesai = datetime(tahun, bulan_angka, calendar.monthrange(tahun, bulan_angka)[1]).date()
    else:
        c1, c2 = st.columns(2)
        with c1:
            tgl_mulai = st.date_input("Dari Tanggal", datetime.now().replace(day=1), key=f"start_{key_prefix}")
        with c2:
            tgl_selesai = st.date_input("Sampai Tanggal", datetime.now(), key=f"end_{key_prefix}")
    return tgl_mulai, tgl_selesai

# --- LOGIK INPUT ---
if menu == "📝 Input Jurnal":
    st.header("Jurnal & Presensi Mengajar")
    kls = st.selectbox("Pilih Kelas", list(DAFTAR_SISWA.keys()))
    with st.form("form_jurnal"):
        tgl = st.date_input("Tanggal", datetime.now())
        mtr = st.text_input("Materi Pembelajaran")
        st.write("**Presensi Siswa (Pilih jika tidak hadir):**")
        presensi = {}
        for nama in DAFTAR_SISWA[kls]:
            presensi[nama] = st.radio(nama, ["H", "S", "I", "A"], horizontal=True, key=f"j_{nama}")
        if st.form_submit_button("Simpan Ke Jurnal"):
            if mtr:
                absen_ket = ", ".join([f"{n}({s})" for n, s in presensi.items() if s != "H"])
                df_j = pd.DataFrame([{"Tanggal": str(tgl), "Kelas": kls, "Materi": mtr, "Keterangan_Absen": absen_ket if absen_ket else "Hadir Semua"}])
                if simpan_data(df_j, "Jurnal"): st.success("✅ Tersimpan!")
            else: st.warning("Materi kosong!")

elif menu == "📊 Input Nilai Siswa":
    st.header("Input Nilai Siswa")
    kls = st.selectbox("Pilih Kelas", list(DAFTAR_SISWA.keys()))
    with st.form("form_nilai"):
        mtr_n = st.text_input("Nama Tugas/Ujian")
        nilai_list = []
        for nama in DAFTAR_SISWA[kls]:
            n_val = st.number_input(f"Nilai {nama}", 0, 100, 75)
            nilai_list.append({"Tanggal": str(datetime.now().date()), "Nama": nama, "Kelas": kls, "Materi": mtr_n, "Nilai": n_val})
        if st.form_submit_button("Simpan Nilai"):
            if mtr_n and simpan_data(pd.DataFrame(nilai_list), "Nilai"): st.success("✅ Berhasil!")

elif menu == "👨‍🏫 Wali Kelas 8":
    st.header("Absensi Harian Kelas 8")
    with st.form("form_wk"):
        tgl_w = st.date_input("Tanggal", datetime.now())
        wk_list = []
        for nama in DAFTAR_SISWA["Kelas 8"]:
            st_w = st.radio(nama, ["H", "S", "I", "A"], horizontal=True, key=f"wk_{nama}")
            wk_list.append({"Tanggal": str(tgl_w), "Nama": nama, "Status": st_w})
        if st.form_submit_button("Simpan Absensi Wali"):
            if simpan_data(pd.DataFrame(wk_list), "AbsenWali"): st.success("✅ Berhasil!")

# --- MENU REKAP ---
elif menu == "📂 Rekap Data":
    st.header("📂 Rekapitulasi & Laporan")
    mode_cetak = st.checkbox("🔍 Aktifkan Mode Cetak")
    tab1, tab2, tab3 = st.tabs(["📜 Jurnal", "📊 Nilai", "👨‍🏫 Wali Kelas"])

    with tab1:
        df_jurnal = ambil_data("Jurnal")
        if not df_jurnal.empty:
            df_jurnal['Tanggal'] = pd.to_datetime(df_jurnal['Tanggal']).dt.date
            tm, ts = filter_periode_ui("jurnal")
            kls_p = st.selectbox("Pilih Kelas:", list(DAFTAR_SISWA.keys()))
            df_f = df_jurnal[(df_jurnal['Tanggal'] >= tm) & (df_jurnal['Tanggal'] <= ts) & (df_jurnal['Kelas'] == kls_p)]
            
            if not df_f.empty:
                rekap_list = []
                for _, row in df_f.iterrows():
                    status_hari = {nama: "H" for nama in DAFTAR_SISWA[kls_p]}
                    ket = str(row['Keterangan_Absen']) # Paksa jadi string untuk cegah error float
                    if ket != "Hadir Semua" and ket != "nan":
                        for p in ket.split(", "):
                            for n in DAFTAR_SISWA[kls_p]:
                                if f"{n}(" in p: 
                                    try: status_hari[n] = p.split("(")[1].replace(")", "")
                                    except: pass
                    for n, s in status_hari.items(): rekap_list.append({"Nama": n, "Status": s})
                
                df_rkp = pd.DataFrame(rekap_list)
                tabel = df_rkp.groupby(['Nama', 'Status']).size().unstack(fill_value=0)
                for c in ['H', 'S', 'I', 'A']:
                    if c not in tabel.columns: tabel[c] = 0
                
                if mode_cetak: st.table(tabel[['H', 'S', 'I', 'A']])
                else: st.dataframe(tabel[['H', 'S', 'I', 'A']], width='stretch')
            else: st.warning("Data kosong.")

    with tab2:
        df_nilai = ambil_data("Nilai")
        if not df_nilai.empty:
            kls_n = st.selectbox("Pilih Kelas:", list(DAFTAR_SISWA.keys()), key="kn")
            nama_n = st.selectbox("Pilih Siswa:", DAFTAR_SISWA[kls_n], key="sn")
            df_n_sis = df_nilai[(df_nilai['Nama'] == nama_n) & (df_nilai['Kelas'] == kls_n)]
            if not df_n_sis.empty:
                fig = px.line(df_n_sis, x="Materi", y="Nilai", markers=True, title=f"Tren Nilai: {nama_n}")
                st.plotly_chart(fig)
            else: st.info("Belum ada nilai.")

    with tab3:
        df_wk = ambil_data("AbsenWali")
        if not df_wk.empty:
            df_wk['Tanggal'] = pd.to_datetime(df_wk['Tanggal']).dt.date
            tm, ts = filter_periode_ui("w")
            df_wk_f = df_wk[(df_wk['Tanggal'] >= tm) & (df_wk['Tanggal'] <= ts)]
            if not df_wk_f.empty:
                rkp_wk = df_wk_f.groupby(['Nama', 'Status']).size().unstack(fill_value=0)
                for c in ['H', 'S', 'I', 'A']:
                    if c not in rkp_wk.columns: rkp_wk[c] = 0
                if mode_cetak: st.table(rkp_wk[['H', 'S', 'I', 'A']])
                else: st.dataframe(rkp_wk[['H', 'S', 'I', 'A']], width='stretch')
