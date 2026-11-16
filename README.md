# Supply Chain Management — Supplier Integration Module

## 1. Gambaran Proyek

Supplier Integration Module merupakan aplikasi web berbasis **Python, Flask, dan MySQL** yang dikembangkan untuk menyimulasikan integrasi proses bisnis dalam rantai pasok yang melibatkan tiga sistem independen, yaitu **Retail, Supplier, dan Distributor**.

Dalam simulasi proyek Ujian Tengah Semester (UTS) untuk mata kuliah Integrasi Aplikasi Korporasi (IAK) ini, modul Supplier merepresentasikan CV Sehat Sayur Sejahtera, perusahaan pemasok sayuran beku yang berlokasi di Malang.

Supplier bertanggung jawab untuk mengelola produk dan persediaan, menerima pesanan dari Retail, melakukan validasi pesanan, meminta penawaran biaya pengiriman kepada Distributor, serta meneruskan pesanan kepada Distributor yang dipilih Retail.

Integrasi antarmodul dilakukan melalui **REST API menggunakan pertukaran data JSON**, termasuk mekanisme request/response dan callback untuk menyinkronkan informasi pesanan dan pengiriman. Proyek ini merupakan tugas kelompok yang melibatkan pengembangan modul Retail, Supplier, dan Distributor oleh tim yang berbeda.

## 2. Fitur Utama

### A. Pengelolaan Produk dan Persediaan

Modul Supplier menyediakan fitur untuk:

- Menampilkan daftar produk yang tersedia, termasuk harga, stok, kategori, dan tanggal kedaluwarsa.
- Menambahkan produk baru ke database Supplier.
- Memperbarui dan menghapus informasi produk.
- Menambahkan stok produk yang telah habis sebagai batch persediaan baru.
- Memeriksa ketersediaan dan kuantitas produk sebelum pesanan dari Retail diproses.

### B. Penerimaan dan Pemrosesan Pesanan dari Retail

Ketika Retail mengirimkan pesanan melalui API, modul Supplier akan:

1. Menerima informasi identitas Retail serta daftar produk dan kuantitas yang dipesan.
2. Memeriksa kelengkapan data pesanan.
3. Memvalidasi apakah setiap produk tersedia dan jumlah stok mencukupi.
4. Mengembalikan respons kesalahan apabila produk tidak ditemukan atau stok tidak mencukupi.
5. Membuat pesanan baru pada tabel `orders` dan menyimpan rincian produk pada tabel `order_detail`.
6. Menghitung total kuantitas serta total harga produk.
7. Memberikan status awal pesanan **Menunggu Konfirmasi**.

### C. Integrasi Penawaran Pengiriman dengan Distributor

Setelah pesanan Retail diterima dan divalidasi, modul Supplier mengirimkan permintaan penawaran biaya pengiriman kepada sistem Distributor yang terhubung.

Permintaan berisi informasi asal pengiriman, tujuan pengiriman, dan total kuantitas produk.

Setiap Distributor mengembalikan respons yang memuat identitas Distributor dan informasi biaya pengiriman. Hasil dari beberapa Distributor kemudian dikumpulkan oleh Supplier.

Supplier meneruskan daftar opsi Distributor dan biaya pengiriman kepada Retail melalui API callback. Dengan demikian, Retail dapat memilih Distributor yang akan menangani pengiriman pesanannya.

### D. Pemrosesan Pemilihan Distributor dan Pengiriman

Setelah Retail mengirimkan pilihan Distributor, modul Supplier melakukan proses berikut:

1. Menerima ID pesanan dan ID Distributor yang dipilih Retail.
2. Mengambil informasi pesanan terkait dari database.
3. Memvalidasi kembali data pesanan dan ketersediaan produk.
4. Meneruskan rincian pesanan kepada sistem Distributor terpilih melalui API.
5. Menerima respons Distributor berupa status pengiriman, biaya pengiriman, estimasi kedatangan, dan nomor resi.
6. Menyimpan informasi pengiriman ke database Supplier.
7. Menghitung total pembayaran berdasarkan harga produk dan biaya pengiriman.
8. Mengurangi stok produk sesuai jumlah yang dipesan.
9. Memperbarui status pesanan menjadi **Pesanan Dikirim ke Distributor**.
10. Mengirim callback kepada Retail berisi total pembayaran dan nomor resi.

### E. Notifikasi Aktivitas Pesanan pada Dashboard Supplier

Modul Supplier dilengkapi mekanisme notifikasi untuk membantu pengguna dashboard Supplier memantau aktivitas pemesanan yang berlangsung melalui API.

Notifikasi mencakup tiga kejadian utama:

| Kejadian | Sumber aktivitas | Informasi yang diterima pengguna dashboard Supplier |
|---|---|---|
| Pesanan baru | Retail mengirimkan pesanan kepada Supplier | Adanya pesanan baru dari Retail |
| Penawaran ongkos kirim | Distributor mengembalikan respons atas permintaan Supplier | Informasi bahwa penawaran biaya pengiriman telah diterima |
| Pemrosesan pengiriman | Retail memilih Distributor, kemudian Supplier meneruskan pesanan kepada Distributor terpilih | Informasi bahwa pesanan telah diteruskan untuk pengiriman |

Notifikasi dihasilkan melalui fungsi `push_notification()` pada backend dan dapat diambil melalui endpoint `/api/notifications` untuk ditampilkan sebagai popup pada antarmuka Supplier.

Mekanisme ini membantu pengguna Supplier memantau proses integrasi tanpa harus memeriksa setiap respons API secara manual.

## 3. Alur Integrasi Antarsistem

Proses bisnis dimulai dari Retail sebagai pihak pemesan, sementara Supplier bertindak sebagai pengelola pesanan dan penghubung dengan Distributor.

**Tahap 1 — Penerimaan pesanan**

- Retail mengirimkan pesanan ke API Supplier.
- Supplier memvalidasi produk, stok, dan jumlah pesanan.
- Supplier menyimpan pesanan dan menghitung total harga produk.

**Tahap 2 — Permintaan dan pemilihan Distributor**

- Supplier mengirim permintaan biaya pengiriman kepada Distributor yang terhubung.
- Distributor mengembalikan penawaran biaya pengiriman.
- Supplier mengirimkan pilihan Distributor kepada Retail melalui callback.
- Retail memilih Distributor dan mengirimkan pilihannya kepada Supplier.

**Tahap 3 — Pengiriman pesanan**

- Supplier meneruskan rincian pesanan kepada Distributor terpilih.
- Distributor mengembalikan biaya pengiriman, estimasi kedatangan, dan nomor resi.
- Supplier menyimpan informasi pengiriman, memperbarui status pesanan, dan mengurangi stok.
- Supplier mengirimkan informasi pembayaran serta nomor resi kepada Retail.

**Tahap 4 — Notifikasi**

- Backend Supplier menghasilkan notifikasi pada tahapan API yang relevan.
- Dashboard Supplier mengambil data notifikasi melalui `/api/notifications`.
- Pengguna Supplier melihat pembaruan aktivitas pemesanan melalui popup.

## 4. REST API

### Endpoint utama modul Supplier

| Method | Endpoint | Fungsi |
|---|---|---|
| GET | `/api/suppliers` | Menyediakan daftar Supplier beserta identitas dan kota asal kepada Retail |
| GET | `/api/products` | Menyediakan daftar produk Supplier, termasuk harga, stok, dan tanggal kedaluwarsa |
| POST | `/api/pesanan_retail` | Menerima pesanan dari Retail, melakukan validasi, dan memproses permintaan penawaran ongkos kirim |
| POST | `/api/pesanan_distributor` | Menerima pilihan Distributor dari Retail dan meneruskan pesanan kepada Distributor terpilih |

### Endpoint pendukung

`/api/notifications` digunakan oleh frontend Supplier untuk memperoleh data notifikasi aktivitas pesanan.

### Mekanisme Callback

Supplier juga berkomunikasi dengan endpoint milik Retail untuk memperbarui informasi pesanan:

| Endpoint tujuan Retail | Fungsi |
|---|---|
| `/api/orders/order-callback` | Mengirim daftar opsi Distributor beserta informasi biaya pengiriman |
| `/api/orders/resi` | Mengirim informasi total pembayaran dan nomor resi setelah pengiriman diproses |

### Contoh request pesanan dari Retail

Retail mengirimkan data pesanan kepada Supplier melalui:

`POST /api/pesanan_retail`

```json
{
  "id_retail": 2,
  "items": [
    {
      "id_product": 1,
      "qty": 10
    },
    {
      "id_product": 2,
      "qty": 10
    }
  ]
}
```

Supplier memvalidasi kedua produk, menyimpan pesanan, menghitung total harga dan kuantitas, serta mengirimkan permintaan penawaran biaya pengiriman kepada Distributor yang terhubung.

### Contoh request pemilihan Distributor dari Retail

Setelah menerima daftar pilihan Distributor, Retail mengirimkan:

`POST /api/pesanan_distributor`

```json
{
  "id_order": 214,
  "id_distributor": 1
}
```

Supplier kemudian mengambil rincian pesanan dan meneruskannya kepada Distributor dengan ID yang dipilih.

Respons dari Distributor dapat mencakup:

```json
{
  "status": "success",
  "biaya_pengiriman": 500500,
  "eta_delivery_date": "2025-10-09",
  "no_resi": "RESI-20251006-704AAD"
}
```

Setelah informasi tersebut diproses, Supplier memperbarui data pesanan dan mengirimkan nomor resi beserta total pembayaran kepada Retail.

*Contoh payload di atas berasal dari skenario pengujian yang didokumentasikan dalam laporan proyek, bukan transaksi komersial.*

## 5. Struktur Database

Modul Supplier menggunakan MySQL untuk menyimpan data operasional.

| Tabel | Fungsi |
|---|---|
| `supplier` | Menyimpan identitas dan informasi kontak Supplier |
| `product` | Menyimpan data produk, harga, stok, kategori, dan tanggal kedaluwarsa |
| `orders` | Menyimpan data utama pesanan, termasuk identitas pemesan dan status pesanan |
| `order_detail` | Menyimpan rincian produk dan kuantitas dalam setiap pesanan |
| `users` | Menyimpan data akun pengguna aplikasi Supplier |

Relasi antara data produk, pesanan, dan rincian pesanan digunakan untuk mendukung validasi produk, perhitungan transaksi, serta pembaruan persediaan selama proses integrasi.

## 6. Teknologi yang Digunakan

- **Python:** Pemrosesan logika backend, validasi, dan komunikasi antarsistem.
- **Flask:** Pengembangan aplikasi web, endpoint API, dan pemrosesan HTTP request/response.
- **MySQL:** Penyimpanan data produk, persediaan, pesanan, dan informasi transaksi.
- **REST API & JSON:** Pertukaran data pesanan, informasi produk, penawaran pengiriman, dan callback.
- **HTML, CSS, JavaScript:** Antarmuka dashboard dan interaksi pengguna, termasuk tampilan notifikasi.
- **ngrok:** Menghubungkan aplikasi yang dikembangkan oleh tim berbeda selama pengujian integrasi.
- **Git & GitHub:** Pengelolaan kode dan kolaborasi proyek.

Antarmuka proyek menggunakan **Flask Material Dashboard** sebagai template dasar, yang kemudian disesuaikan dengan kebutuhan modul Supplier.

## 7. Integration Testing dan Debugging

Pengujian integrasi dilakukan bersama tim pengembang modul Retail dan Distributor untuk memeriksa kesesuaian komunikasi API dan memastikan proses pemesanan dapat berlangsung antarsistem.

Cakupan pengujian meliputi:

1. **Penerimaan pesanan:** Memeriksa apakah Supplier dapat menerima dan membaca data pesanan yang dikirim Retail.
2. **Validasi pesanan:** Memeriksa penanganan produk yang tidak ditemukan atau stok yang tidak mencukupi.
3. **Penawaran biaya pengiriman:** Memeriksa pertukaran request/response antara Supplier dan Distributor.
4. **Callback ke Retail:** Memeriksa pengiriman daftar pilihan Distributor beserta ongkos kirimnya.
5. **Pemrosesan Distributor terpilih:** Memeriksa apakah Supplier dapat menerima pilihan Retail dan meneruskan pesanan kepada Distributor yang sesuai.
6. **Pembaruan informasi pengiriman:** Memeriksa penyimpanan status pesanan, biaya pengiriman, dan nomor resi.
7. **Notifikasi frontend:** Memeriksa apakah aktivitas API yang relevan dapat ditampilkan sebagai notifikasi pada dashboard Supplier.

Hasil pengujian bersama digunakan untuk mengidentifikasi masalah integrasi, melakukan debugging, dan menyempurnakan implementasi backend serta komunikasi API.

## 8. Kontribusi Pribadi

Proyek ini dikembangkan secara berkelompok. Kontribusi utama saya berfokus pada pengembangan API, penyempurnaan backend, dan pengujian integrasi.

**REST API Development**

Mengembangkan endpoint API dan mekanisme integrasi untuk pertukaran informasi pesanan, penawaran biaya pengiriman, pemilihan Distributor, dan callback antara modul Supplier, Retail, dan Distributor.

**Backend Development & Refinement**

Menyempurnakan logika backend untuk pemrosesan pesanan Retail, termasuk validasi data, penghitungan pesanan, pembaruan status, dan pengolahan respons antarsistem.

**Integration Testing & Debugging**

Melakukan pengujian integrasi bersama tim Retail dan Distributor, menelusuri masalah yang muncul selama pengujian, dan memperbaiki implementasi backend serta API berdasarkan hasil pengujian tersebut.

**API-Driven Notifications**

Mengembangkan integrasi notifikasi pada dashboard Supplier menggunakan mekanisme backend dan endpoint `/api/notifications` untuk menampilkan pembaruan aktivitas pemesanan.

## 9. Dokumentasi Proyek

Dokumentasi teknis dan alur integrasi sistem dijelaskan dalam laporan UTS mata kuliah Integrasi Aplikasi Korporasi, mencakup:

- Gambaran arsitektur dan alur modul Supplier.
- Struktur database dan fitur CRUD.
- Daftar endpoint REST API.
- Contoh request dan response JSON.
- Proses callback antara Supplier dan Retail.
- Bukti pengujian integrasi API.
- Tampilan notifikasi pemesanan pada dashboard.

## 10. Catatan Pengembangan

Proyek ini merupakan simulasi integrasi aplikasi untuk keperluan akademik. Sistem Retail, Supplier, dan Distributor dikembangkan oleh tim berbeda, kemudian dihubungkan untuk menguji pertukaran data dan alur pemrosesan pesanan.

Pengujian dilakukan dalam lingkungan pengembangan dengan bantuan ngrok untuk mengakses endpoint antarmodul. Proyek ini tidak diklaim sebagai aplikasi supply chain produksi yang digunakan secara komersial.

Template antarmuka berasal dari Flask Material Dashboard; ketentuan lisensi dan atribusi template tetap mengikuti proyek asal.
