# Supply Chain Management — Supplier Integration Module

**Proyek Akademik | Integrasi Aplikasi Korporasi | Universitas Airlangga | 2025**

## Gambaran Proyek

Supplier Integration Module adalah aplikasi web berbasis **Python, Flask, dan MySQL** yang dikembangkan untuk menyimulasikan integrasi proses bisnis antara tiga sistem independen dalam rantai pasok: **Retail, Supplier, dan Distributor**.

Dalam skenario proyek, Supplier berperan sebagai pemasok sayuran beku yang menerima pesanan dari Retail, memvalidasi stok, meminta penawaran biaya pengiriman kepada Distributor, dan memproses pengiriman melalui Distributor yang dipilih Retail.

Komunikasi antarsistem menggunakan **REST API, JSON, dan mekanisme callback** untuk pertukaran informasi pesanan, biaya pengiriman, status, serta nomor resi.

## Fitur Utama

- **Manajemen Produk:** Pengelolaan data produk dan persediaan melalui fitur CRUD, termasuk pembaruan stok dan informasi kedaluwarsa.
- **Pemrosesan Pesanan Retail:** Penerimaan pesanan melalui API, validasi produk dan stok, perhitungan total pesanan, serta penyimpanan data transaksi.
- **Integrasi Distributor:** Permintaan penawaran ongkos kirim, pengolahan respons beberapa Distributor, dan penerusan pesanan kepada Distributor terpilih.
- **Callback Antarsistem:** Pengiriman informasi pilihan Distributor, total pembayaran, status pengiriman, dan nomor resi kepada Retail.
- **Notifikasi Dashboard:** Popup notifikasi ketika Retail mengirim pesanan baru, penawaran ongkos kirim diterima dari Distributor, dan pesanan diteruskan kepada Distributor terpilih.

## Alur Integrasi

1. **Retail → Supplier:** Retail mengirimkan pesanan melalui API, termasuk identitas Retail, daftar produk, dan kuantitas.
2. **Supplier:** Sistem memvalidasi stok, menghitung total pesanan, dan menyimpan informasi ke database.
3. **Supplier → Distributor:** Supplier meminta penawaran biaya pengiriman kepada Distributor yang terhubung.
4. **Distributor → Supplier → Retail:** Supplier menerima penawaran dan mengirimkan pilihan Distributor beserta ongkos kirim kepada Retail melalui callback.
5. **Retail → Supplier:** Retail memilih Distributor yang akan menangani pengiriman.
6. **Supplier → Distributor:** Supplier meneruskan pesanan kepada Distributor terpilih.
7. **Distributor → Supplier:** Distributor mengembalikan informasi pengiriman, termasuk biaya, estimasi kedatangan, dan nomor resi.
8. **Supplier → Retail:** Supplier memperbarui status pesanan dan stok, kemudian mengirimkan total pembayaran serta nomor resi kepada Retail.

Aktivitas penting selama proses integrasi juga menghasilkan notifikasi pada dashboard Supplier.

## REST API

Modul Supplier menyediakan endpoint berikut:

| Method | Endpoint | Fungsi |
|---|---|---|
| GET | `/api/suppliers` | Menyediakan informasi Supplier kepada Retail |
| GET | `/api/products` | Menyediakan daftar produk, harga, dan stok |
| POST | `/api/pesanan_retail` | Menerima dan memproses pesanan dari Retail |
| POST | `/api/pesanan_distributor` | Memproses pilihan Distributor dan meneruskan pesanan |
| GET | `/api/notifications` | Mengambil notifikasi aktivitas pesanan untuk dashboard Supplier |

Supplier juga mengirimkan callback ke endpoint milik Retail, yaitu `/api/orders/order-callback` untuk pilihan Distributor dan `/api/orders/resi` untuk informasi pengiriman.

## Teknologi

| Teknologi | Penggunaan |
|---|---|
| Python & Flask | Backend, REST API, dan logika pemrosesan pesanan |
| MySQL | Database produk, pesanan, dan transaksi |
| REST API & JSON | Komunikasi dan pertukaran data antarsistem |
| HTML, CSS, JavaScript | Antarmuka dashboard dan notifikasi |
| ngrok | Koneksi antarmodul selama pengujian |
| Git & GitHub | Version control dan kolaborasi |

Antarmuka aplikasi menggunakan Flask Material Dashboard sebagai template dasar yang disesuaikan dengan kebutuhan modul Supplier.

## Integration Testing & Debugging

Pengujian integrasi dilakukan bersama tim pengembang Retail dan Distributor untuk memastikan komunikasi API dan alur pemrosesan pesanan berjalan sesuai rancangan.

Pengujian mencakup penerimaan pesanan, validasi stok, permintaan ongkos kirim, callback, pemrosesan pilihan Distributor, pembaruan status pesanan, serta notifikasi dashboard.

Berdasarkan hasil pengujian, dilakukan **debugging dan penyempurnaan logika backend** untuk menangani permasalahan komunikasi API dan pemrosesan pesanan antarmodul.
