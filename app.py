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

# --- NAVIGASI UTAMA (Bagian yang sempat hilang) ---
st.sidebar.title("MENU UTAMA")
menu = st.sidebar.radio("Pilih Fitur:", ["📝 Jurnal & Mapel", "📊 Penilaian Siswa", "👨‍🏫 Wali Kelas 8"])

# --- 1. JURNAL & MAPEL ---
if menu == "📝 Jurnal & Mapel":
    st.header("Jurnal Mengajar & Presensi Mapel")
    
    # Pilih kelas di luar form agar daftar siswa update otomatis
    kls = st.selectbox("Pilih Kelas", list(DAFTAR_SISWA.keys()))
    
    with st.form("form_jurnal"):
        c1, c2 = st.columns(2)
        tgl = c1.date_input("Tanggal", datetime.now())
        c1.info(f"Mengisi data untuk: **{kls}**")
        materi = c2.text_input("Materi Pembelajaran", placeholder="Masukkan materi...")
        
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
                abs_str = ", ".join([f"{n}: {s}" for n, s in status_mapel.items()])
                simpan_data({
                    "Tanggal": str(tgl), "Kelas": kls, "Materi": materi, "Presensi": abs_str
                }, FILE_JURNAL)
                st.success(f"✅ Jurnal {kls} Berhasil Disimpan!")

# --- 2. PENILAIAN SISWA ---
elif menu == "📊 Penilaian Siswa":
    t1, t2, t3 = st.tabs(["➕ Input Nilai", "🔎 Rekap Nilai", "📉 Analisis KKM"])
    
    with t1:
        with st.expander("Form Input Nilai Baru", expanded=True):
            cx, cy = st.columns(2)
            k_n = cx.selectbox("Pilih Kelas Penilaian", list(DAFTAR_SISWA.keys()))
            j_d = cx.selectbox("Jenis Penilaian", ["Tugas", "UH", "PTS", "PAS"])
            m_p = cy.text_input("Materi Pokok / KD")
            lbl = hitung_urutan(k_n, j_d)
            cy.info(f"Label Otomatis: **{lbl}**")
            
            with st.form("f_nilai"):
                list_n = []
                for nama in DAFTAR_SISWA[k_n]:
                    cn, cs = st.columns([2, 1])
                    cn.write(nama)
                    skor = cs.number_input(f"Nilai {nama}", 0, 100, 0, key=f"v_{nama}")
                    list_n.append({"Nama": nama, "Kelas": k_n, "Jenis Dasar": j_d, "Materi Pokok": m_p, "Jenis Spesifik": lbl, "Nilai": skor})
                if st.form_submit_button("Simpan Semua Nilai"):
                    simpan_data(list_n, FILE_NILAI)
                    st.success("✅ Nilai Tersimpan!"); st.rerun()

    with t2:
        if os.path.isfile(FILE_NILAI):
            df_n = pd.read_excel(FILE_NILAI)
            f_k = st.selectbox("Tampilkan Kelas:", list(DAFTAR_SISWA.keys()))
            df_f = df_n[df_n["Kelas"] == f_k]
            if not df_f.empty:
                pivot = df_f.pivot_table(index="Nama", columns="Jenis Spesifik", values="Nilai", aggfunc='first').reset_index()
                st.dataframe(pivot, use_container_width=True)
            else: st.warning("Data kosong.")

    with t3:
        if os.path.isfile(FILE_NILAI):
            kkm = st.number_input("Standar KKM:", 0, 100, 75)
            f_a = st.selectbox("Analisis Kelas:", list(DAFTAR_SISWA.keys()), key="analis_k")
            df_a = pd.read_excel(FILE_NILAI)
            df_a = df_a[df_a["Kelas"] == f_a]
            if not df_a.empty:
                rerata = df_a.groupby("Nama")["Nilai"].mean().reset_index()
                rerata["Status"] = rerata["Nilai"].apply(lambda x: "✅ TUNTAS" if x >= kkm else "❌ REMEDIAL")
                st.table(rerata)

# --- 3. WALI KELAS 8 ---
elif menu == "👨‍🏫 Wali Kelas 8":
    tw1, tw2 = st.tabs(["📝 Input Harian WK", "📊 Rekap Kehadiran"])
    
    with tw1:
        st.subheader("Absensi Pagi (Wali Kelas 8)")
        with st.form("f_wk8"):
            tgl_w = st.date_input("Tanggal Absen", datetime.now())
            data_w = []
            for nama in DAFTAR_SISWA["Kelas 8"]:
                c_n, c_o = st.columns([1, 1])
                c_n.write(f"**{nama}**")
                st_w = c_o.radio(f"S", ["H", "S", "I", "A"], horizontal=True, key=f"wk8_{nama}", label_visibility="collapsed")
                map_w = {"H": "Hadir", "S": "Sakit", "I": "Izin", "A": "Alpa"}
                data_w.append({"Tanggal": str(tgl_w), "Nama": nama.strip(), "Status": map_w[st_w]})
            if st.form_submit_button("Simpan Absensi Wali Kelas"):
                simpan_data(data_w, FILE_ABSEN_WALI)
                st.success("✅ Absensi Berhasil Disimpan!")

    with tw2:
        if os.path.isfile(FILE_ABSEN_WALI):
            df_w = pd.read_excel(FILE_ABSEN_WALI)
            df_w['Tanggal'] = pd.to_datetime(df_w['Tanggal'])
            
            mode = st.selectbox("Mode Rekap:", ["Per Bulan", "Kustom (Semester)"])
            df_f_w = df_w.copy()
            
            if mode == "Per Bulan":
                b_p = st.selectbox("Pilih Bulan:", range(1, 13), format_func=lambda x: datetime(2026, x, 1).strftime('%B'))
                df_f_w = df_w[df_w['Tanggal'].dt.month == b_p]
            else:
                c_1, c_2 = st.columns(2)
                t_1 = c_1.date_input("Mulai", value=datetime(2026, 1, 1))
                t_2 = c_2.date_input("Sampai", value=datetime.now())
                df_f_w = df_w[(df_w['Tanggal'] >= pd.Timestamp(t_1)) & (df_w['Tanggal'] <= pd.Timestamp(t_2))]

            rekap_w = []
            for i, nama in enumerate(DAFTAR_SISWA["Kelas 8"], start=1):
                df_s = df_f_w[df_f_w['Nama'] == nama]
                h, s, iz, al = len(df_s[df_s['Status']=="Hadir"]), len(df_s[df_s['Status']=="Sakit"]), len(df_s[df_s['Status']=="Izin"]), len(df_s[df_s['Status']=="Alpa"])
                rekap_w.append({"No": i, "Nama Siswa": nama, "H": h, "S": s, "I": iz, "A": al, "Total (SIA)": s+iz+al})
            
            if not df_f_w.empty:
                st.table(pd.DataFrame(rekap_w).set_index('No'))
                st.download_button("📥 Download Rekap", pd.DataFrame(rekap_w).to_csv(index=False).encode('utf-8'), "rekap_absen_wk8.csv", "text/csv")
            else: st.warning("Tidak ada data.")
