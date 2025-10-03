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
            "kategori": p.kategori,
            "harga": p.harga,
            "stok": p.stok,
            "satuan": p.satuan,
            "berat": p.berat,
            "deskripsi": p.deskripsi,
            "gambar": p.gambar
        })
    return jsonify(result)

# -------------------------------
# POST /api/orders
# -------------------------------
@api_blueprint.route('/api/orders', methods=['POST'])
def create_order():
    try:
        data = request.get_json()

        id_product = data.get('id_product')   # "SY001"
        jumlah = data.get('jumlah')
        tanggal = data.get('tanggal_order')
        id_supplier = data.get('id_supplier')

        if not id_product or not jumlah:
            return jsonify({"status": "error", "message": "id_product dan jumlah wajib diisi"}), 400

        # id_product bertipe string → gunakan filter_by
        produk = Product.query.filter_by(id_product=id_product).first()
        if not produk:
            return jsonify({"status": "error", "message": "Produk tidak ditemukan"}), 404

        if produk.stok < jumlah:
            return jsonify({"status": "error", "message": "Stok tidak cukup"}), 400

        produk.stok -= jumlah

        new_order = Orders(
            id_product=id_product,
            jumlah=jumlah,
            tanggal_order=tanggal,
            id_supplier=id_supplier
        )
        db.session.add(new_order)
        db.session.commit()

        return jsonify({
            "status": "success",
            "message": f"Pesanan {jumlah} unit untuk produk {produk.nama_product} berhasil dibuat."
        }), 201

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
