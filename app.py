import streamlit as st
import pandas as pd
from datetime import datetime
import calendar
from streamlit_gsheets import GSheetsConnection

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Jurnal Guru Pancasila", layout="wide", page_icon="📝")

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

# --- 5. TAMPILAN MENU SIDEBAR ---
st.sidebar.title("🛠️ MENU UTAMA")
menu = st.sidebar.selectbox("Pilih Fitur:", ["📝 Input Jurnal", "📊 Input Nilai Siswa", "👨‍🏫 Wali Kelas 8", "📂 Rekap Data"])

# --- KODE MENU LAINNYA (JURNAL, NILAI, WALI KELAS) TETAP SAMA ---
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
                if simpan_data(df_j, "Jurnal"):
                    st.success("✅ Data Jurnal Berhasil Disimpan!")
            else:
                st.warning("Materi tidak boleh kosong!")

elif menu == "📊 Input Nilai Siswa":
    st.header("Input Nilai Siswa")
    kls = st.selectbox("Pilih Kelas", list(DAFTAR_SISWA.keys()))
    with st.form("form_nilai"):
        mtr_n = st.text_input("Nama Tugas/Ujian (Contoh: UH-1)")
        nilai_list = []
        for nama in DAFTAR_SISWA[kls]:
            n_val = st.number_input(f"Nilai {nama}", 0, 100, 75)
            nilai_list.append({"Tanggal": str(datetime.now().date()), "Nama": nama, "Kelas": kls, "Materi": mtr_n, "Nilai": n_val})
        
        if st.form_submit_button("Simpan Nilai"):
            if mtr_n:
                if simpan_data(pd.DataFrame(nilai_list), "Nilai"):
                    st.success(f"✅ Nilai {mtr_n} Berhasil Disimpan!")
            else:
                st.warning("Nama Materi/Ujian harus diisi!")

elif menu == "👨‍🏫 Wali Kelas 8":
    st.header("Absensi Harian Kelas 8")
    with st.form("form_wk"):
        tgl_w = st.date_input("Tanggal", datetime.now())
        wk_list = []
        for nama in DAFTAR_SISWA["Kelas 8"]:
            st_w = st.radio(nama, ["H", "S", "I", "A"], horizontal=True, key=f"wk_{nama}")
            wk_list.append({"Tanggal": str(tgl_w), "Nama": nama, "Status": st_w})
        
        if st.form_submit_button("Simpan Absensi Wali"):
            if simpan_data(pd.DataFrame(wk_list), "AbsenWali"):
                st.success("✅ Absensi Wali Kelas Berhasil Disimpan!")

# --- MENU 4: REKAP DATA (VERSI DROPDOWN DINAMIS) ---
elif menu == "📂 Rekap Data":
    st.header("📂 Rekapitulasi Data")
    tab1, tab2, tab3 = st.tabs(["📜 Rekap Jurnal", "📊 Rekap Nilai", "👨‍🏫 Rekap Absen Wali"])

    with tab1:
        st.subheader("Riwayat Jurnal Mengajar")
        df_jurnal = ambil_data("Jurnal")
        if not df_jurnal.empty:
            filter_kls = st.multiselect("Filter Kelas:", list(DAFTAR_SISWA.keys()), default=list(DAFTAR_SISWA.keys()))
            df_filtered = df_jurnal[df_jurnal['Kelas'].isin(filter_kls)]
            st.dataframe(df_filtered, use_container_width=True)
        else:
            st.info("Belum ada data jurnal.")

    with tab2:
        st.subheader("Rekap Nilai Siswa")
        df_nilai = ambil_data("Nilai")
        if not df_nilai.empty:
            col1, col2 = st.columns(2)
            with col1:
                f_kls_n = st.selectbox("Pilih Kelas:", ["Semua"] + list(DAFTAR_SISWA.keys()))
            with col2:
                f_nama_n = st.text_input("Cari Nama Siswa:")
            
            df_n_fil = df_nilai.copy()
            if f_kls_n != "Semua":
                df_n_fil = df_n_fil[df_n_fil['Kelas'] == f_kls_n]
            if f_nama_n:
                df_n_fil = df_n_fil[df_n_fil['Nama'].str.contains(f_nama_n, case=False)]
            
            st.dataframe(df_n_fil, use_container_width=True)
        else:
            st.info("Belum ada data nilai.")

    with tab3:
        st.subheader("Rekap Kehadiran Siswa Kelas 8 (Wali Kelas)")
        df_wk = ambil_data("AbsenWali")
        
        if not df_wk.empty:
            df_wk['Tanggal'] = pd.to_datetime(df_wk['Tanggal']).dt.date
            
            st.markdown("### 🗓️ Atur Periode Rekap")
            # DROPDOWN PILIHAN JENIS REKAP
            opsi_rekap = st.selectbox("Pilih Jenis Rekap:", ["Bulanan", "Persemester / Custom Tanggal"])
            
            if opsi_rekap == "Bulanan":
                c1, c2 = st.columns(2)
                with c1:
                    list_bulan = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", 
                                 "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
                    bulan_nama = st.selectbox("Pilih Bulan:", list_bulan, index=datetime.now().month - 1)
                    bulan_angka = list_bulan.index(bulan_nama) + 1
                with c2:
                    tahun = st.selectbox("Pilih Tahun:", [2024, 2025, 2026], index=1)
                
                # Hitung tanggal mulai dan akhir bulan otomatis
                tgl_mulai = datetime(tahun, bulan_angka, 1).date()
                hari_terakhir = calendar.monthrange(tahun, bulan_angka)[1]
                tgl_selesai = datetime(tahun, bulan_angka, hari_terakhir).date()
                
            else: # Jika Persemester / Custom
                c1, c2 = st.columns(2)
                with c1:
                    tgl_mulai = st.date_input("Dari Tanggal", datetime.now().replace(day=1))
                with c2:
                    tgl_selesai = st.date_input("Sampai Tanggal", datetime.now())

            # Filter Data
            mask = (df_wk['Tanggal'] >= tgl_mulai) & (df_wk['Tanggal'] <= tgl_selesai)
            df_wk_filtered = df_wk.loc[mask]
            
            if not df_wk_filtered.empty:
                st.info(f"Menampilkan Data: **{tgl_mulai.strftime('%d %B %Y')}** s/d **{tgl_selesai.strftime('%d %B %Y')}**")
                
                # Pivot Table
                rekap_final = df_wk_filtered.groupby(['Nama', 'Status']).size().unstack(fill_value=0)
                
                # Pastikan H, S, I, A ada
                for col in ['H', 'S', 'I', 'A']:
                    if col not in rekap_final.columns:
                        rekap_final[col] = 0
                
                rekap_final = rekap_final[['H', 'S', 'I', 'A']]
                rekap_final['Total Hari'] = rekap_final.sum(axis=1)
                
                st.dataframe(rekap_final, use_container_width=True)
                
                # Tombol Download
                csv = rekap_final.to_csv().encode('utf-8')
                st.download_button(label="📥 Download Rekap", data=csv, file_name=f'rekap_{opsi_rekap}_{tgl_mulai}.csv', mime='text/csv')
            else:
                st.warning("Data tidak ditemukan pada periode ini.")
        else:
            st.info("Belum ada data.")
