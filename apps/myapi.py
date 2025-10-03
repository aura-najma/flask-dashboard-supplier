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
# POST /api/orders
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
        
        # Buat order kosong dulu
        new_order = Orders(
            nama_pemesan=f"Retail {id_retail}",
            asal_pemesan="Jakarta",
            total_berat=0,
            tanggal_order=datetime.now().date(),
            status_order="Menunggu Konfirmasi"
        )
        db.session.add(new_order)
        db.session.commit()

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

@api_blueprint.route('/api/orders/inbox', methods=['POST'])
def receive_orders():
    data = request.get_json()

    if not data or 'orders' not in data:
        return jsonify({"error": "Format JSON tidak sesuai"}), 400

    for order in data['orders']:
        id_retail = order.get('id_retail')
        id_supplier = order.get('id_supplier')
        items = order.get('items', [])
        status = order.get('status', 'CREATED')
        tanggal_order = datetime.utcnow().date()

        # Hitung total berat
        total_berat = 0
        for item in items:
            product = Product.query.filter_by(id_product=item['id_product']).first()
            if product:
                total_berat += (product.berat or 0) * item['qty']

        # Buat record orders
        new_order = Orders(
            nama_pemesan=f"Retail {id_retail}",
            asal_pemesan="Jakarta",  # opsional, bisa disesuaikan
            total_berat=total_berat,
            tanggal_order=tanggal_order,
            status_order="Menunggu Konfirmasi"
        )
        db.session.add(new_order)
        db.session.commit()

        # Ambil id_order baru
        order_id = new_order.id_order

        # Simpan detail per produk
        for item in items:
            id_product = item['id_product']
            jumlah = item['qty']

            product = Product.query.filter_by(id_product=id_product).first()
            berat_total = 0
            if product:
                berat_total = (product.berat or 0) * jumlah

            new_detail = OrderDetail(
                id_order=order_id,
                id_product=id_product,
                id_supplier=id_supplier,
                jumlah=jumlah,
                berat=berat_total
            )
            db.session.add(new_detail)

        db.session.commit()

    return jsonify({"message": "Pesanan berhasil diterima oleh supplier"}), 201
import requests

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