from flask import Blueprint, jsonify, request
from apps import db
from apps.models import Supplier, Product, Orders

# Inisialisasi blueprint
api_blueprint = Blueprint('api_blueprint', __name__)

# -------------------------------
# GET /api/suppliers
# -------------------------------
@api_blueprint.route('/api/suppliers', methods=['GET'])
def get_suppliers():
    suppliers = Supplier.query.all()
    result = []

    for s in suppliers:
        result.append({
            "id_supplier": s.id_supplier,
            "nama_supplier": s.nama_supplier,
            "kota": s.kota
        })

    return jsonify(result)


# -------------------------------
# GET /api/products
# -------------------------------
@api_blueprint.route('/api/products', methods=['GET'])
def get_products():
    products = Product.query.all()
    result = []

    for p in products:
        result.append({
            "id_product": p.id_product,
            "nama_product": p.nama_product,
            "harga": p.harga,
            "expired_date": p.expired_date.strftime('%Y-%m-%d') if p.expired_date else None,
            "stok": p.stok,
            "id_supplier": p.id_supplier  # ✅ tambahkan ini
        })

    return jsonify(result)


@api_blueprint.route('/api/supplier/routes', methods=['GET'])
def get_supplier_routes():
    id_order = request.args.get('id_order')
    id_supplier = request.args.get('id_supplier')

    if not id_order or not id_supplier:
        return jsonify({"error": "id_order dan id_supplier wajib diisi"}), 400

    supplier = Supplier.query.get(id_supplier)
    order = Orders.query.get(id_order)

    if not supplier or not order:
        return jsonify({"error": "Data tidak ditemukan"}), 404

    kota_supplier = supplier.kota
    kota_retail = order.asal_pemesan

    return jsonify({
        "asal": kota_supplier,
        "tujuan": kota_retail
    })


# -------------------------------
# POST /api/orders (ini udah worked sama alden)
# -------------------------------
from datetime import datetime
from flask import request, jsonify
from apps import db
from apps.models import Product, Orders, OrderDetail
@api_blueprint.route('/api/orders', methods=['POST'])
def create_order():
    data = request.get_json()

    id_retail = data.get('id_retail')
    items = data.get('items', [])

    if not id_retail or not items:
        return jsonify({"error": "Data tidak lengkap"}), 400

    total_berat_order = 0
    id_supplier_ref = None

    try:
        
        # 🔹 Tentukan asal_pemesan berdasarkan id_retail
        if id_retail == 1:
            asal_pemesan = "Surabaya"
        elif id_retail == 2:
            asal_pemesan = "Banyuwangi"
        else:
            asal_pemesan = "Tidak Diketahui"  # default fallback

        # 🧾 Buat order kosong dulu
        new_order = Orders(
            id_retail=id_retail,  # ✅ simpan id_retail ke tabel
            nama_pemesan=f"Retail {id_retail}",
            asal_pemesan=asal_pemesan,
            total_berat=0,
            tanggal_order=datetime.now().date(),
            status_order="Menunggu Konfirmasi"
        )


        # Loop setiap item produk
        for item in items:
            id_product = item.get('id_product')
            jumlah = item.get('qty', 0)  # retail kirim pakai "qty"

            product = Product.query.get(id_product)
            if not product:
                db.session.rollback()
                return jsonify({"error": f"Produk {id_product} tidak ditemukan"}), 404

            if jumlah > product.stok:
                db.session.rollback()
                return jsonify({"error": f"Stok tidak cukup untuk produk {id_product}"}), 400

            berat_item = (product.berat or 0) * jumlah
            total_berat_order += berat_item
            id_supplier_ref = product.id_supplier

            # Tambah ke order_detail
            new_detail = OrderDetail(
                id_order=new_order.id_order,
                id_product=id_product,
                id_supplier=product.id_supplier,
                jumlah=jumlah,
                berat=berat_item
            )
            db.session.add(new_detail)

        # Update total berat order
        new_order.total_berat = total_berat_order
        db.session.commit()

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

    return jsonify({
        "message": "Pemesanan multiple item berhasil disimpan",
        "id_order": new_order.id_order,
        "id_supplier": id_supplier_ref,
        "total_berat": total_berat_order,
        "jumlah_item": len(items)
    }), 201
import requests

## BISMILLAH FIX
@api_blueprint.route('/api/pesanan_retail', methods=['POST'])
def create_order_alt3():
    data = request.get_json()
    id_retail = data.get('id_retail')
    items = data.get('items', [])

    # 🧩 Validasi awal
    if not id_retail or not items:
        return jsonify({"error": "Data tidak lengkap"}), 400

    total_order = 0
    total_kuantitas = 0
    id_supplier_ref = None

    try:
        # 🔹 Tentukan asal_pemesan berdasarkan id_retail
        if id_retail == 1:
            asal_pemesan = "Surabaya" #KELOMPOK ALDEN
        elif id_retail == 2:
            asal_pemesan = "Banyuwangi" #KELOMPOK NAJLA
        else:
            asal_pemesan = "Tidak Diketahui"

        # 🧾 Buat order baru
        new_order = Orders(
            id_retail=id_retail,
            nama_pemesan=f"Retail {id_retail}",
            asal_pemesan=asal_pemesan,
            total_order=0,        # awalnya 0
            total_kuantitas=0,    # awalnya 0
            tanggal_order=datetime.now().date(),
            status_order="Menunggu Konfirmasi"
        )
        db.session.add(new_order)
        db.session.flush()  # supaya id_order langsung kebaca

        # 🔹 Loop setiap item produk
        for item in items:
            id_product = item.get('id_product')
            kuantitas = item.get('qty', 0)

            product = Product.query.get(id_product)
            if not product:
                db.session.rollback()
                return jsonify({"error": f"Produk {id_product} tidak ditemukan"}), 404

            if kuantitas > product.stok:
                db.session.rollback()
                return jsonify({"error": f"Stok tidak cukup untuk produk {id_product}"}), 400

            # 🔢 Hitung subtotal & berat total per item
            harga_satuan = float(product.harga or 0)
            subtotal = harga_satuan * kuantitas
            berat_item = float(product.berat or 0) * kuantitas

            # Tambahkan ke total order
            total_order += subtotal
            total_kuantitas += kuantitas

            id_supplier_ref = product.id_supplier

            # 💾 Simpan detail order
            new_detail = OrderDetail(
                id_order=new_order.id_order,
                id_product=id_product,
                id_supplier=product.id_supplier,
                kuantitas=kuantitas,
                berat=berat_item,
                jumlah_harga=subtotal
            )
            db.session.add(new_detail)


        # 🔁 Update total di tabel orders
        new_order.total_order = total_order
        new_order.total_kuantitas = total_kuantitas

        db.session.commit()

        # ====================================================
        # 🚀 HIT KE 2 EKSPEDISI
        ekspedisi_results = {}
        supplier = Supplier.query.get(id_supplier_ref)

        if supplier:
            payload_ekspedisi = {
                "asal_pengirim": (supplier.kota or "").lower(),
                "tujuan": (new_order.asal_pemesan or "").lower(),
                "kuantitas": total_kuantitas  # 📦 ganti total_berat → total_kuantitas
            }
            print("Payload ke ekspedisi:", payload_ekspedisi)

            ekspedisi_urls = {
                "ekspedisi_A": "https://denis-connectable-lawson.ngrok-free.dev/api/biaya", #KELOMPOK ARYA
                "ekspedisi_B": "https://bc545e44d560.ngrok-free.app/api/quote"#KELOMPOK MANDA
            }

            for nama, url in ekspedisi_urls.items():
                try:
                    res = requests.post(url, json=payload_ekspedisi, timeout=5)
                    hasil = res.json()
                    harga = hasil.get("harga_pengiriman") or hasil.get("harga")

                    ekspedisi_results[nama] = {
                        "url": url,
                        "harga": harga,
                        "estimasi": hasil.get("estimasi_pengiriman") or hasil.get("estimasi"),
                        "id_distributor": hasil.get("id_distributor"),
                        "nama_distributor": hasil.get("nama_distributor"),
                        "raw_response": hasil
                    }
                except Exception as e:
                    ekspedisi_results[nama] = {
                        "url": url,
                        "error": str(e)
                    }

        # ====================================================
        # 🚀 CALLBACK KE RETAIL
        try:
            distributor_options = []

            for nama, data_ekspedisi in ekspedisi_results.items():
                raw = data_ekspedisi.get("raw_response", {})
                if raw and raw.get("status") == "success":
                    distributor_options.append({
                        "id_distributor": raw.get("id_distributor"),
                        "nama_distributor": raw.get("nama_distributor"),
                        "harga_pengiriman": raw.get("harga_pengiriman"),
                        "estimasi": raw.get("estimasi_pengiriman") or raw.get("estimasi")
                    })

            payload_retail = {
                "message": "Pesanan sudah diterima oleh supplier dan menunggu konfirmasi distributor",
                "id_order": new_order.id_order,
                "id_supplier": id_supplier_ref,
                "id_retail": id_retail,
                "total_order": float(total_order),
                "total_kuantitas": total_kuantitas,
                "jumlah_item": len(items),
                "distributor_options": distributor_options
            }

            headers = {"Content-Type": "application/json"}

            retail_endpoints = {
                1: "http://192.168.100.112:5000/api/orders/order-callback",
                2: "http://192.168.100.113:5000/api/orders/order-callback"
            }

            url_retail_callback = retail_endpoints.get(id_retail)
            if url_retail_callback:
                try:
                    res = requests.post(url_retail_callback, json=payload_retail, headers=headers, timeout=5)
                    print(f"✅ Callback dikirim ke Retail {id_retail} ({res.status_code})")
                except Exception as e:
                    print(f"⚠️ Gagal kirim callback ke Retail {id_retail}: {str(e)}")
            else:
                print("⚠️ ID Retail tidak dikenali, callback dibatalkan")

        except Exception as e:
            print("⚠️ Error umum saat callback ke Retail:", str(e))

        # ====================================================
        # ✅ Response ke frontend
        return jsonify({
            "message": "Pemesanan multiple item berhasil disimpan",
            "id_order": new_order.id_order,
            "id_supplier": id_supplier_ref,
            "id_retail": id_retail,
            "total_order": float(total_order),
            "total_kuantitas": total_kuantitas,
            "jumlah_item": len(items),
            "ongkir": ekspedisi_results
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
    
@api_blueprint.route('/api/pesanan_distributor', methods=['POST'])
def kirim_ke_distributor():
    data = request.get_json()
    id_order = data.get('id_order')
    id_distributor = data.get('id_distributor')

    # 🧩 Validasi dasar
    if not id_order or not id_distributor:
        return jsonify({"error": "id_order dan id_distributor wajib diisi"}), 400

    try:
        # 🔍 Ambil data order & detail
        order = Orders.query.get(id_order)
        if not order:
            return jsonify({"error": f"Order {id_order} tidak ditemukan"}), 404

        order_details = OrderDetail.query.filter_by(id_order=id_order).all()
        if not order_details:
            return jsonify({"error": f"Tidak ada detail untuk order {id_order}"}), 404

        supplier = Supplier.query.get(order_details[0].id_supplier)
        if not supplier:
            return jsonify({"error": "Supplier tidak ditemukan"}), 404

        # 🗺️ Mapping ID ke Nama Distributor
        distributor_mapping = {
            1: "Distribusi Nusantara", #KELOMPOK MANDA
            2: "Cahaya Logistik", #KELOMPOK ARYA
        }
        nama_distributor = distributor_mapping.get(id_distributor, "Distributor Tidak Dikenal")

        # 🔹 Ambil nama barang & kuantitas
        barang_list = []
        for detail in order_details:
            product = Product.query.get(detail.id_product)
            if product.stok < detail.kuantitas:
                db.session.rollback()
                return jsonify({"error": f"Stok tidak cukup untuk produk {product.nama_product}"}), 400

            # 🔢 Kurangi stok saat dikirim ke distributor
            product.stok -= detail.kuantitas
            barang_list.append({
                "id_barang": product.id_product,
                "nama_barang": product.nama_product,
                "kuantitas": detail.kuantitas
            })

        # ✏️ Update status order
        order.status_order = "Pesanan Dikirim ke Distributor"
        db.session.commit()

        # 📦 Payload ke Distributor
        payload_distributor = {
            "id_order": order.id_order,
            "id_retail": order.id_retail,
            "nama_supplier": supplier.nama_supplier,
            "nama_distributor": nama_distributor,
            "asal_supplier": supplier.kota,
            "tujuan_retail": order.asal_pemesan,
            "barang_dipesan": barang_list
        }

        headers = {"Content-Type": "application/json"}

        # 📨 URL Distributor
        distributor_endpoints = {
            2: "https://denis-connectable-lawson.ngrok-free.dev/api/pengiriman", #KELOMPOK ARYA
            1: "https://bc545e44d560.ngrok-free.app/api/shipments" #KELOMPOK MANDA
        }
        url_distributor = distributor_endpoints.get(id_distributor)

        if url_distributor:
            try:
                res = requests.post(url_distributor, json=payload_distributor, headers=headers, timeout=5)
                try:
                    hasil = res.json()
                    print(f"✅ Callback dikirim ke Distributor {id_distributor} ({res.status_code})")
                    print("📦 Response JSON:", hasil)
                except ValueError:
                    print(f"⚠️ Distributor {id_distributor} balas non-JSON atau kosong. Status:", res.status_code)
                    print("📜 Raw response:", res.text)
                hasil = res.json()
                print(f"✅ Callback dikirim ke Distributor {id_distributor} ({res.status_code})")

                # ✅ Jika distributor balas status success
                if hasil.get("status") == "success":
                    biaya_pengiriman = hasil.get("biaya_pengiriman", 0)
                    eta_date = hasil.get("eta_delivery_date")
                    no_resi = hasil.get("no_resi")

                    # 💾 Update ke tabel orders
                    order.harga_pengiriman = biaya_pengiriman
                    order.total_pembayaran = (order.total_order or 0) + biaya_pengiriman
                    order.id_distributor = id_distributor
                    order.eta_delivery_date = eta_date
                    order.no_resi = no_resi
                    db.session.commit()

                    # 🚀 Callback ke Retail
                    payload_retail = {
                        "message": "Pesanan sedang dikirim ke distributor",
                        "id_order": order.id_order,
                        "id_retail": order.id_retail,
                        "total_pembayaran": float(order.total_pembayaran or 0),
                        "no_resi": order.no_resi
                    }


                    retail_endpoints = {
                        1: "http://192.168.100.112:5000/api/orders/resi",
                        2: "http://192.168.100.107:5000/api/orders/resi"
                    }
                    url_retail = retail_endpoints.get(order.id_retail)

                    if url_retail:
                        try:
                            res_retail = requests.post(url_retail, json=payload_retail, headers=headers, timeout=5)
                            print(f"✅ Callback ke Retail {order.id_retail} ({res_retail.status_code})")
                        except Exception as e:
                            print(f"⚠️ Gagal kirim callback ke Retail {order.id_retail}: {str(e)}")

            except Exception as e:
                print(f"⚠️ Gagal kirim ke Distributor {id_distributor}: {str(e)}")
        else:
            print("⚠️ ID Distributor tidak dikenali, callback dibatalkan")

        # ✅ Respon sukses ke frontend
        return jsonify({
            "message": "Pesanan berhasil diteruskan ke distributor",
            "id_order": order.id_order,
            "status_order": order.status_order,
            "harga_pengiriman": float(order.harga_pengiriman or 0),
            "total_pembayaran": float(order.total_pembayaran or 0),
            "no_resi": order.no_resi
        }), 201


    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


import requests
from flask import jsonify
@api_blueprint.route('/api/send_quote/<int:id_order>', methods=['POST'])
def send_quote(id_order):
    # 🔹 Ambil data order
    order = Orders.query.get(id_order)
    if not order:
        return jsonify({"error": "Order tidak ditemukan"}), 404

    # 🔹 Ambil data supplier pertama (contoh id=2)
    supplier = Supplier.query.get(2)
    if not supplier:
        return jsonify({"error": "Supplier tidak ditemukan"}), 404

    # 🔹 Buat payload untuk dikirim (semua dilower biar aman)
    payload = {
        "asal_pengirim": (supplier.kota or "").lower(),    # dari tabel supplier
        "tujuan": (order.asal_pemesan or "").lower(),      # dari tabel orders
        "kuantitas": order.total_berat or 0                # dari tabel orders
    }
    print("Payload yang dikirim ke /quote:", payload)

    try:
        # 🔹 Kirim POST ke service quote
        response = requests.post("http://192.168.0.51:5000/api/quote", json=payload)
        
        # 🔹 Ambil hasil JSON dari service quote
        result = response.json()
        
        # Pastikan service mengembalikan 'harga'
        harga = result.get('harga_pengiriman') 

        if harga is None:
            return jsonify({
                "message": "Response dari quote tidak mengandung harga",
                "raw_response": result
            }), 502

        # 🔹 (Opsional) Simpan harga ke order, kalau kamu mau
        # order.total_harga = harga
        # db.session.commit()

        return jsonify({
            "message": "Harga ongkir berhasil diterima",
            "payload_dikirim": payload,
            "harga": harga,
            "response_asli": result
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500