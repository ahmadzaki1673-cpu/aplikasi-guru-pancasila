import streamlit as st
import pandas as pd
from datetime import datetime
import calendar
import plotly.express as px # Untuk grafik
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

# --- 5. TAMPILAN MENU SIDEBAR ---
with st.sidebar:
    st.title("🛠️ MENU UTAMA")
    menu = st.selectbox("Pilih Fitur:", ["📝 Input Jurnal", "📊 Input Nilai Siswa", "👨‍🏫 Wali Kelas 8", "📂 Rekap Data"])
    st.divider()
    st.info("Aplikasi Jurnal Guru Pancasila v3.0 - Fitur Cetak & Grafik Aktif")

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

# --- LOGIK INPUT (TETAP SAMA) ---
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
                if simpan_data(df_j, "Jurnal"): st.success("✅ Data Berhasil Disimpan!")
            else: st.warning("Materi tidak boleh kosong!")

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
            if mtr_n and simpan_data(pd.DataFrame(nilai_list), "Nilai"): st.success("✅ Nilai Berhasil Disimpan!")

elif menu == "👨‍🏫 Wali Kelas 8":
    st.header("Absensi Harian Kelas 8")
    with st.form("form_wk"):
        tgl_w = st.date_input("Tanggal", datetime.now())
        wk_list = []
        for nama in DAFTAR_SISWA["Kelas 8"]:
            st_w = st.radio(nama, ["H", "S", "I", "A"], horizontal=True, key=f"wk_{nama}")
            wk_list.append({"Tanggal": str(tgl_w), "Nama": nama, "Status": st_w})
        if st.form_submit_button("Simpan Absensi Wali"):
            if simpan_data(pd.DataFrame(wk_list), "AbsenWali"): st.success("✅ Absensi Berhasil Disimpan!")

# --- MENU 4: REKAP DATA (VERSI TERBARU: GRAFIK & CETAK) ---
elif menu == "📂 Rekap Data":
    st.header("📂 Rekapitulasi & Laporan")
    
    # Tombol Mode Cetak (Menyederhanakan tampilan untuk PDF)
    mode_cetak = st.checkbox("🔍 Aktifkan Mode Cetak (Hilangkan tombol-tombol agar rapi saat di PDF)")

    tab1, tab2, tab3 = st.tabs(["📜 Rekap Jurnal & Absen", "📊 Grafik & Rekap Nilai", "👨‍🏫 Rekap Wali Kelas"])

    # --- TAB 1: REKAP JURNAL ---
    with tab1:
        st.subheader("Rekap Kehadiran Jurnal Mengajar")
        df_jurnal = ambil_data("Jurnal")
        if not df_jurnal.empty:
            df_jurnal['Tanggal'] = pd.to_datetime(df_jurnal['Tanggal']).dt.date
            t_mulai, t_selesai = filter_periode_ui("jurnal")
            kls_pilih = st.selectbox("Pilih Kelas:", list(DAFTAR_SISWA.keys()))
            
            df_j_fil = df_jurnal[(df_jurnal['Tanggal'] >= t_mulai) & (df_jurnal['Tanggal'] <= t_selesai) & (df_jurnal['Kelas'] == kls_pilih)]

            if not df_j_fil.empty:
                # Proses Hitung Absen
                rekap_j_list = []
                for _, row in df_j_fil.iterrows():
                    status_hari_ini = {nama: "H" for nama in DAFTAR_SISWA[kls_pilih]}
                    if row['Keterangan_Absen'] != "Hadir Semua":
                        for p in row['Keterangan_Absen'].split(", "):
                            for n in DAFTAR_SISWA[kls_pilih]:
                                if f"{n}(" in p: status_hari_ini[n] = p.split("(")[1].replace(")", "")
                    for n, s in status_hari_ini.items(): rekap_j_list.append({"Nama": n, "Status": s})
                
                df_rekap_j = pd.DataFrame(rekap_j_list)
                tabel_j = df_rekap_j.groupby(['Nama', 'Status']).size().unstack(fill_value=0)
                for c in ['H', 'S', 'I', 'A']:
                    if c not in tabel_j.columns: tabel_j[c] = 0
                tabel_j = tabel_j[['H', 'S', 'I', 'A']]
                
                # Header Laporan Formal
                if mode_cetak:
                    st.markdown(f"<h3 style='text-align: center;'>LAPORAN KEHADIRAN SISWA {kls_pilih.upper()}</h3>", unsafe_allow_html=True)
                    st.markdown(f"<p style='text-align: center;'>Periode: {t_mulai} s/d {t_selesai}</p>", unsafe_allow_html=True)
                
                st.table(tabel_j) # Menggunakan st.table agar semua data terlihat saat dicetak
            else: st.warning("Data tidak ditemukan.")

    # --- TAB 2: REKAP NILAI & GRAFIK ---
    with tab2:
        st.subheader("Grafik Perkembangan Nilai")
        df_nilai = ambil_data("Nilai")
        if not df_nilai.empty:
            # Filter Grafik
            c_kls, c_sis = st.columns(2)
            with c_kls: kls_n = st.selectbox("Pilih Kelas:", list(DAFTAR_SISWA.keys()), key="k_n")
            with c_sis: nama_n = st.selectbox("Pilih Siswa:", DAFTAR_SISWA[kls_n], key="s_n")
            
            df_n_sis = df_nilai[(df_nilai['Nama'] == nama_n) & (df_nilai['Kelas'] == kls_n)]
            
            if not df_n_sis.empty:
                # GRAFIK GARIS (PERKEMBANGAN)
                fig = px.line(df_n_sis, x="Materi", y="Nilai", title=f"Tren Nilai: {nama_n}", markers=True, text="Nilai")
                fig.update_traces(textposition="top center")
                st.plotly_chart(fig, use_container_width=True)
                
                # GRAFIK BATANG (RATA-RATA KELAS)
                df_kls_avg = df_nilai[df_nilai['Kelas'] == kls_n].groupby('Materi')['Nilai'].mean().reset_index()
                fig2 = px.bar(df_kls_avg, x="Materi", y="Nilai", title=f"Rata-rata Nilai Kelas {kls_n}", color="Nilai")
                st.plotly_chart(fig2, use_container_width=True)

                st.write("**Detail Nilai:**")
                st.dataframe(df_n_sis[['Tanggal', 'Materi', 'Nilai']], use_container_width=True)
            else: st.info("Siswa ini belum memiliki data nilai.")

    # --- TAB 3: REKAP WALI KELAS ---
    with tab3:
        st.subheader("Rekap Absensi Wali Kelas")
        df_wk = ambil_data("AbsenWali")
        if not df_wk.empty:
            df_wk['Tanggal'] = pd.to_datetime(df_wk['Tanggal']).dt.date
            tm, ts = filter_periode_ui("wali_fix")
            df_wk_f = df_wk[(df_wk['Tanggal'] >= tm) & (df_wk['Tanggal'] <= ts)]
            
            if not df_wk_f.empty:
                rekap_wk = df_wk_f.groupby(['Nama', 'Status']).size().unstack(fill_value=0)
                for c in ['H', 'S', 'I', 'A']:
                    if c not in rekap_wk.columns: rekap_wk[c] = 0
                rekap_wk = rekap_wk[['H', 'S', 'I', 'A']]
                
                if mode_cetak:
                    st.markdown("<h3 style='text-align: center;'>REKAPITULASI ABSENSI HARIAN KELAS 8</h3>", unsafe_allow_html=True)
                    st.markdown(f"<p style='text-align: center;'>Periode: {tm} s/d {ts}</p>", unsafe_allow_html=True)
                
                st.table(rekap_wk)
                
                # Grafik Pie (Persentase Kehadiran Kelas)
                st.markdown("### 📊 Persentase Kehadiran Kelas")
                total_status = df_wk_f['Status'].value_counts().reset_index()
                fig3 = px.pie(total_status, values='count', names='Status', color='Status', 
                             color_discrete_map={'H':'green', 'S':'blue', 'I':'yellow', 'A':'red'})
                st.plotly_chart(fig3)
            else: st.warning("Data kosong.")

    # INSTRUKSI CETAK
    if not mode_cetak:
        st.divider()
        st.info("💡 **Tips Cetak ke PDF:** Centang 'Aktifkan Mode Cetak' di atas, lalu tekan **Ctrl + P** di keyboard laptop Anda. Pilih 'Save as PDF' pada menu printer.")
