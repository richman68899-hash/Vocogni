# Vocogni — Checklist Kesiapan Publikasi Dokumen Legal

**Status saat ini: BELUM SIAP UNTUK PUBLIKASI SEBAGAI KONTRAK FINAL.**  
Checklist ini sengaja memisahkan naskah Ketentuan Layanan dari kontrol produk yang membuatnya transparan dan dapat dijalankan.

## A. Identitas dan kontrak elektronik

- [ ] Tentukan siapa pengelola layanan secara sah: nama pribadi atau badan usaha yang tepat. Jangan mengarang nama perusahaan atau memakai identitas pihak lain.
- [ ] Lengkapi alamat korespondensi dan email yang aktif, dipantau, dan cocok untuk keluhan serta permintaan data.
- [ ] Tetapkan tanggal berlaku, nomor versi, serta proses perubahan dan pemberitahuan.
- [ ] Tinjau Ketentuan Layanan bersama orang tua/wali pengelola dan penasihat hukum Indonesia. Pengelola yang masih di bawah umur tidak boleh menganggap dapat sendiri mengikat pihak lain atau menandatangani perjanjian komersial tanpa memperhatikan ketentuan kecakapan hukum dan kewenangan perwakilan.
- [ ] Pastikan teks kontrak untuk pengguna di Indonesia tersedia dalam Bahasa Indonesia dan informasi kontraktual ditampilkan jelas sebelum pengguna menerimanya.
- [ ] Tambahkan mekanisme penerimaan Ketentuan yang nyata (misalnya kotak centang yang tidak dicentang sebelumnya), simpan versi/timestamp persetujuan, dan jangan menganggap sekadar mengakses aplikasi sebagai persetujuan jika persetujuan afirmatif diperlukan.
- [ ] Jangan memublikasikan draf dengan placeholder dalam tanda kurung siku.

## B. Anak dan persetujuan wali — blocker publikasi

- [ ] Tetapkan kelompok usia pengguna yang benar-benar akan diterima dan sesuaikan proses orientasi pengguna.
- [ ] Karena Layanan berpotensi digunakan pelajar di bawah umur, rancang mekanisme persetujuan orang tua/wali yang sesuai dan dapat dibuktikan. Jangan mengandalkan hanya pada pernyataan anak.
- [ ] Pisahkan persetujuan pemrosesan data pribadi dari persetujuan Ketentuan jika hukum mensyaratkannya; jelaskan tujuan, jenis data, dasar pemrosesan, retensi, pihak penerima, dan hak subjek data dengan bahasa sederhana.
- [ ] Uji alur persetujuan/penolakan wali dan pastikan pengguna anak yang belum mendapat persetujuan yang diwajibkan tidak mulai diproses di luar dasar hukum yang sah.
- [ ] Tentukan bagaimana wali dapat mengajukan pertanyaan, menarik persetujuan bila berlaku, atau meminta akses/koreksi/penghapusan data.

## C. Kebijakan Privasi — blocker publikasi

- [ ] Tulis dan publikasikan **Kebijakan Privasi terpisah**; Ketentuan Layanan ini bukan penggantinya.
- [ ] Inventarisasi semua data yang benar-benar dikumpulkan: identifier akun/OIDC, nama/email yang tersedia dari provider, profil (termasuk umur/kelas dan minat jika diisi), pengaturan, catatan, folder, milestones, whiteboards bila disimpan, kemajuan kursus, jawaban, diagnostik, skor, percobaan, dan log operasional yang dikumpulkan hosting.
- [ ] Petakan tujuan dan dasar hukum setiap kategori data, siapa yang bisa mengaksesnya, berapa lama disimpan, bagaimana penghapusan dilakukan, dan cadangan apa yang dapat bertahan setelah penghapusan utama.
- [ ] Konfirmasi pengaturan produksi dan ketentuan pengolah data untuk Auth0/penyedia identitas yang aktif, hosting Streamlit, Supabase, serta layanan lain yang benar-benar dipakai. Dokumentasikan lokasi pemrosesan dan transfer lintas negara jika ada; jangan menebak lokasi.
- [ ] Konfirmasi batas akses database, kebijakan kunci rahasia, backup, logging, prosedur respons insiden, dan siapa yang menerima laporan.
- [ ] Buat dan uji proses untuk permintaan akses, koreksi, pembaruan, penarikan persetujuan, penghapusan, dan pengaduan subjek data.
- [ ] Pastikan proses penanganan insiden memenuhi kewajiban pemberitahuan hukum yang berlaku; jangan menjanjikan batas waktu atau proses yang belum dapat dijalankan.
- [ ] Verifikasi kembali pernyataan bahwa versi saat ini tidak mengirimkan profil/kemajuan ke model AI generatif sebelum tiap rilis. Jika integrasi AI/analitik baru dibuat, lakukan penilaian privasi, perbarui pemberitahuan, dan kumpulkan persetujuan yang dibutuhkan **sebelum** mengaktifkan pemrosesan baru.

## D. Kejujuran produk dan perlindungan konsumen

- [ ] Pastikan deskripsi produk menyebut status prototipe dan tidak menjanjikan nilai, hasil belajar, atau diagnosis yang tervalidasi.
- [ ] Tinjau contoh pertanyaan, hasil diagnostik, label “verified”, umpan balik otomatis, dan rekomendasi agar maknanya tidak dilebih-lebihkan.
- [ ] Jika ada biaya, pembelian, atau langganan, tampilkan jumlah total, biaya tambahan, cara pembayaran, pembatalan, pengembalian dana, dan persetujuan sebelum transaksi. Jika belum ada fitur pembayaran, jangan menampilkan syarat seolah fitur itu sudah berjalan.
- [ ] Sediakan jalur kontak untuk kesalahan materi, masalah akun, laporan keamanan, keluhan, dan permintaan data.
- [ ] Periksa ketentuan agar tidak menghapus hak konsumen yang tidak dapat dikesampingkan berdasarkan hukum.

## E. Pemasangan di aplikasi

- [ ] Tampilkan tautan Ketentuan Layanan dan Kebijakan Privasi dari lokasi yang mudah ditemukan (misalnya halaman masuk dan footer/pengaturan).
- [ ] Buka dokumen tanpa mengharuskan pengguna masuk terlebih dahulu.
- [ ] Simpan versi dokumen yang diterima; minta persetujuan ulang jika perubahan material memerlukannya.
- [ ] Uji alur pengguna baru, pengguna yang sudah ada, pengguna anak, penolakan persetujuan, sign-out, serta permintaan penutupan akun.
- [ ] Jalankan review keamanan dan uji manual pada deployment produksi sebelum menganggap kontrol ini berfungsi.

## F. Perlindungan anak dan kewajiban PSE

- [ ] Minta penasihat hukum menilai penerapan **PP No. 17 Tahun 2025 tentang Tata Kelola Penyelenggaraan Sistem Elektronik dalam Pelindungan Anak** terhadap kelompok usia, fitur, tingkat risiko, dan operasi Vocogni. Jangan menganggap pencantuman klausul persetujuan wali saja sudah memenuhi semua kewajiban perlindungan anak.
- [ ] Tentukan safeguard berbasis usia, penilaian risiko, desain/pengaturan akun anak, mekanisme persetujuan dan penarikan persetujuan wali, serta prosedur penanganan permintaan/keluhan yang berlaku untuk Vocogni.
- [ ] Nilai bersama penasihat hukum apakah Vocogni wajib mendaftar sebagai **Penyelenggara Sistem Elektronik Lingkup Privat (PSE Lingkup Privat)** dan melalui proses yang sesuai sebelum operasi publik. Panduan resmi Komdigi mencantumkan beberapa kategori layanan online, termasuk layanan penawaran/penyediaan jasa dan pemrosesan data pribadi untuk kegiatan operasional.
- [ ] Jangan mengklaim telah terdaftar, memperoleh izin, atau mematuhi kewajiban PSE sampai statusnya dibuktikan dengan dokumen resmi.

## Referensi hukum awal (periksa kembali saat publikasi)

1. **UU Republik Indonesia No. 27 Tahun 2022 tentang Pelindungan Data Pribadi** — mencakup hak subjek data, transparansi/persetujuan, data pribadi anak, kewajiban pengendali, dan pemberitahuan kegagalan pelindungan data. Sumber resmi JDIH Komdigi: https://jdih.komdigi.go.id/produk_hukum/view/id/832
2. **PP Republik Indonesia No. 71 Tahun 2019 tentang Penyelenggaraan Sistem dan Transaksi Elektronik** — mengatur kewajiban penyelenggara sistem elektronik dan ketentuan kontrak elektronik; Pasal 47 menyatakan kontrak elektronik yang ditujukan kepada penduduk Indonesia harus dibuat dalam Bahasa Indonesia. Sumber resmi JDIH Komdigi: https://jdih.komdigi.go.id/produk_hukum/view/id/695
3. **UU Republik Indonesia No. 8 Tahun 1999 tentang Perlindungan Konsumen** — perlu diperhatikan saat menyusun informasi produk, klausul baku, dan ketentuan tanggung jawab. Identifikasi naskah resmi dan ketentuan yang berlaku saat peninjauan final.
4. **PP Republik Indonesia No. 17 Tahun 2025 tentang Tata Kelola Penyelenggaraan Sistem Elektronik dalam Pelindungan Anak** — tercatat berlaku pada JDIH Komdigi; penasihat hukum perlu menilai kewajiban operasional yang sesuai. Sumber resmi: https://jdih.komdigi.go.id/produk_hukum/view/id/965/t/peraturan%20pemerintah%20nomor%2017%20tahun%202025
5. **Panduan kriteria pendaftaran PSE Lingkup Privat Komdigi** — gunakan untuk penilaian awal, bukan sebagai pengganti keputusan hukum atas fakta operasional Vocogni. Sumber resmi: https://pse.komdigi.go.id/panduan/kriteria-pendaftaran-pse-lingkup-privat

Referensi ini adalah titik awal untuk pemeriksaan, bukan pernyataan bahwa Vocogni sudah mematuhi seluruh kewajiban hukum. Penasihat hukum perlu memverifikasi peraturan pelaksana, kewajiban PSE yang mungkin berlaku, dan fakta operasional aktual sebelum publikasi.
