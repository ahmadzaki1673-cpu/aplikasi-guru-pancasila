# --- 1. JURNAL & MAPEL ---
if menu == "📝 Jurnal & Mapel":
    st.header("Jurnal Mengajar & Presensi Mapel")
    
    # Bagian ini penting: Kita definisikan kelas dulu di luar form agar daftar siswa terupdate
    kls = st.selectbox("Pilih Kelas", list(DAFTAR_SISWA.keys()))
    
    with st.form("form_jurnal"):
        c1, c2 = st.columns(2)
        tgl = c1.date_input("Tanggal", datetime.now())
        # Tampilkan nama kelas yang dipilih sebagai konfirmasi (read-only)
        c1.info(f"Mengisi data untuk: **{kls}**")
        materi = c2.text_input("Materi Pembelajaran", placeholder="Masukkan materi...")
        
        st.write("---")
        st.write(f"**Presensi Siswa {kls}:**")
        
        status_mapel = {}
        # Sekarang daftar siswa akan otomatis berubah mengikuti kelas yang dipilih di atas
        for nama in DAFTAR_SISWA[kls]:
            col_n, col_o = st.columns([1, 2])
            col_n.write(f"{nama}")
            # Memberikan key unik yang menyertakan nama kelas agar tidak tertukar
            status_mapel[nama] = col_o.radio(
                f"S-{nama}", 
                ["H", "S", "I", "A"], 
                horizontal=True, 
                key=f"m_{kls}_{nama}", 
                label_visibility="collapsed"
            )
        
        st.write("---")
        submit_jurnal = st.form_submit_button("Simpan Jurnal & Absen")
        
        if submit_jurnal:
            if not materi:
                st.error("Materi harus diisi!")
            else:
                abs_str = ", ".join([f"{n}: {s}" for n, s in status_mapel.items()])
                simpan_data({
                    "Tanggal": str(tgl), 
                    "Kelas": kls, 
                    "Materi": materi, 
                    "Presensi": abs_str
                }, FILE_JURNAL)
                st.success(f"✅ Jurnal {kls} Berhasil Disimpan!")
