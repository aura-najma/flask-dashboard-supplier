# -*- encoding: utf-8 -*-
"""
Custom Supplier Module (based on AppSeed)
"""

import wtforms, os
from datetime import date
from math import ceil
from collections import defaultdict
from werkzeug.utils import secure_filename
from sqlalchemy import func
from apps.home import blueprint
from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from jinja2 import TemplateNotFound
from apps import db
from apps.models import Product, Orders, Shipment, Supplier, OrderDetail  # Pastikan ini sudah ada di models.py
from apps.authentication.models import Users
from flask_wtf import FlaskForm
# Import API routes
from api import *
class ProfileForm(FlaskForm):
    pass  # nanti field-nya ditambahkan dinamis di route

# 🏠 DASHBOARD
@blueprint.route('/')
@blueprint.route('/index')
@login_required
def index():
    # Total Produk
    total_products = Product.query.count()

    # Total Order
    total_orders = Orders.query.count()

    # Produk Terlaris (Top Product)
    top_product_query = (
        db.session.query(Product.nama_product, func.sum(OrderDetail.kuantitas).label('total_terjual'))
        .join(OrderDetail, OrderDetail.id_product == Product.id_product)
        .group_by(Product.id_product)
        .order_by(func.sum(OrderDetail.kuantitas).desc())
        .first()
    )
    top_product = top_product_query.nama_product if top_product_query else "Belum Ada Order"

    # Total Pendapatan (harga * jumlah)
    total_pendapatan_query = (
        db.session.query(func.sum(Product.harga * OrderDetail.kuantitas))
        .join(OrderDetail, OrderDetail.id_product == Product.id_product)
        .scalar()
    )
    total_pendapatan = total_pendapatan_query if total_pendapatan_query else 0

    # Context untuk template
    context = {
        'segment': 'dashboard',
        'title': 'Dashboard Supplier',
        'total_products': total_products,
        'total_orders': total_orders,
        'top_product': top_product,
        'total_pendapatan': total_pendapatan
    }

    return render_template('pages/index.html', **context)
# 📦 PRODUK


# VIEW PRODUK
@blueprint.route('/products')
@login_required
def products():
    page = request.args.get('page', 1, type=int)
    products_paginated = Product.query.order_by(Product.id_product.asc()).paginate(page=page, per_page=10)

    context = {
        'segment': 'products',
        'title': 'Kelola Produk',
        'products': products_paginated,
        'today': date.today().isoformat()  # 👈 kirim ke template
    }
    return render_template('pages/products.html', **context)

# 🆕 TAMBAH PRODUK (Auto-generate ID SY001)
@blueprint.route('/products/add', methods=['GET', 'POST'])
@login_required
def add_product():
    if request.method == 'POST':
        # Ambil semua data dari form
        nama = request.form['nama_product']
        kategori = request.form['kategori']
        harga = request.form['harga']
        stok = request.form['stok']
        satuan = request.form['satuan']
        berat = request.form['berat']
        tanggal_masuk = request.form['tanggal_masuk']
        expired_date = request.form['expired_date']
        deskripsi = request.form['deskripsi']
        id_supplier = request.form.get('id_supplier', 1)

        # ✅ Generate ID Product Otomatis (format SY001, SY002, dst)
        last_product = Product.query.order_by(Product.id_product.desc()).first()
        if last_product and last_product.id_product.startswith("SY"):
            try:
                last_number = int(last_product.id_product[2:])
                new_id = f"SY{last_number + 1:03d}"
            except:
                new_id = "SY001"
        else:
            new_id = "SY001"

        # 🔹 Gambar bisa dari upload atau link
        gambar_path = None

        # 1️⃣ Upload file gambar
        if 'gambar_upload' in request.files and request.files['gambar_upload'].filename != '':
            file = request.files['gambar_upload']
            filename = secure_filename(file.filename)
            upload_folder = 'static/uploads'
            os.makedirs(upload_folder, exist_ok=True)
            filepath = os.path.join(upload_folder, filename)
            file.save(filepath)
            gambar_path = f'/static/uploads/{filename}'

        # 2️⃣ Gunakan link gambar jika tersedia
        elif request.form.get('gambar_link'):
            gambar_path = request.form['gambar_link']

        # 3️⃣ Validasi minimal harus ada gambar
        if not gambar_path:
            flash('⚠️ Harap upload gambar atau isi URL gambar!', 'warning')
            return redirect(url_for('home_blueprint.add_product'))

        # 🚀 Simpan produk baru
        new_product = Product(
            id_product=new_id,
            nama_product=nama,
            kategori=kategori,
            harga=harga,
            stok=stok,
            satuan=satuan,
            berat=berat,
            tanggal_masuk=tanggal_masuk,
            expired_date=expired_date,
            deskripsi=deskripsi,
            gambar=gambar_path,
            id_supplier=id_supplier
        )

        try:
            db.session.add(new_product)
            db.session.commit()
            flash(f'✅ Produk "{nama}" berhasil ditambahkan dengan ID {new_id}!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'❌ Gagal menyimpan produk! Error: {e}', 'danger')

        return redirect(url_for('home_blueprint.products'))

    # GET → tampilkan halaman form
    return render_template('pages/add_product.html')

# TAMBAH STOK PRODUK
@blueprint.route('/products/add_stock/<string:id>', methods=['POST'])
@login_required
def add_stock(id):
    # Ambil produk berdasarkan ID
    product = Product.query.get_or_404(id)

    # ✅ Validasi: hanya boleh tambah stok kalau stok = 0
    if product.stok != 0:
        flash(f'Produk "{product.nama_product}" masih memiliki stok {product.stok}. Tambah stok hanya bisa dilakukan jika stok = 0.', 'warning')
        return redirect(url_for('home_blueprint.products'))

    try:
        # Ambil jumlah stok dan tanggal expired baru
        tambahan = int(request.form.get('jumlah_tambah', 0))
        expired_date = request.form.get('expired_date')

        # Validasi input
        if tambahan <= 0:
            flash('Jumlah tambahan stok harus lebih dari 0.', 'warning')
            return redirect(url_for('home_blueprint.products'))

        if not expired_date:
            flash('Tanggal kadaluarsa wajib diisi.', 'warning')
            return redirect(url_for('home_blueprint.products'))

        # Update stok dan expired date
        product.stok = tambahan
        product.expired_date = expired_date

        # Simpan ke database
        db.session.commit()

        flash(f'Stok produk "{product.nama_product}" berhasil ditambah sebanyak {tambahan} dengan expired date {expired_date}.', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'Gagal menambah stok: {e}', 'danger')

    return redirect(url_for('home_blueprint.products'))


@blueprint.route('/products/edit/<string:id>', methods=['GET', 'POST'])
@login_required
def edit_product(id):
    product = Product.query.get_or_404(id)

    if request.method == 'POST':
        # Update data dari form
        product.nama_product = request.form['nama_product']
        product.harga = request.form['harga']
        product.deskripsi = request.form['deskripsi']
        product.berat = request.form['berat']

        # ✅ Update gambar kalau ada upload baru
        if 'gambar' in request.files:
            file = request.files['gambar']

            # Cek kalau user benar-benar pilih file baru
            if file and file.filename != '':
                filename = secure_filename(file.filename)

                # 📁 Folder static/uploads di root
                upload_path = os.path.join('static', 'uploads', filename)
                os.makedirs(os.path.dirname(upload_path), exist_ok=True)

                # Simpan file ke folder
                file.save(upload_path)

                # Simpan path relatif (untuk <img src="..."> di template)
                product.gambar = f'/static/uploads/{filename}'

        # Simpan perubahan
        db.session.commit()
        flash('Produk berhasil diperbarui!', 'success')

        # Kembali ke halaman daftar produk
        return redirect(url_for('home_blueprint.products'))

    return render_template('pages/edit_product.html', product=product)

# DELETE PRODUK
@blueprint.route('/products/delete/<string:id>')
@login_required
def delete_product(id):
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    flash('Produk berhasil dihapus!', 'success')
    return redirect(url_for('home_blueprint.products'))

# VIEW DETAIL PRODUK
@blueprint.route('/products/view/<string:id>')
@login_required
def view_product(id):
    # 1️⃣ Ambil data produk berdasarkan ID
    product = Product.query.get_or_404(id)

    # 2️⃣ (Opsional) Ambil nama supplier biar bisa ditampilkan
    supplier = Supplier.query.get(product.id_supplier) if product.id_supplier else None

    # 3️⃣ Buat context buat dikirim ke template
    context = {
        'product': product,
        'supplier': supplier
    }
    print("DEBUG SUPPLIER:", product.id_supplier, supplier)

    # 4️⃣ Render ke halaman detail
    return render_template('pages/view_product.html', **context)

# 🧾 PESANAN
@blueprint.route('/orders')
@login_required
def orders():
    page = request.args.get('page', 1, type=int)
    per_page = 10  # jumlah data per halaman

    # Total data di tabel orders
    total_data = Orders.query.count()

    # Ambil orders untuk halaman saat ini
    orders = (
        Orders.query
        .order_by(Orders.id_order.asc())  # urut dari kecil ke besar
        .limit(per_page)
        .offset((page - 1) * per_page)
        .all()
    )

    # Ambil semua detail order untuk orders di halaman ini
    order_ids = [o.id_order for o in orders]
    order_details = (
        OrderDetail.query.filter(OrderDetail.id_order.in_(order_ids)).all()
        if order_ids else []
    )

    # Gabungkan semua detail per order (list)
    details_dict = defaultdict(list)
    for d in order_details:
        details_dict[d.id_order].append(d)

    data = [(o, details_dict.get(o.id_order, [])) for o in orders]

    total_pages = ceil(total_data / per_page)

    context = {
        'segment': 'orders',
        'title': 'Pesanan Masuk',
        'data': data,
        'page': page,
        'total_pages': total_pages
    }

    return render_template('pages/orders.html', **context)

# 🚚 PENGIRIMAN
@blueprint.route('/shipments')
@login_required
def shipments():
    shipments = Shipment.query.all()
    context = {
        'segment': 'shipments',
        'title': 'Data Pengiriman',
        'shipments': shipments
    }
    return render_template('pages/shipments.html', **context)

# 🚚 PENGIRIMAN (lanjutan)
@blueprint.route('/shipments/detail/<int:id>')
@login_required
def detail_shipments(id):
    # Ambil data pesanan berdasarkan ID yang diklik
    order = Orders.query.get_or_404(id)
    
    # Semua data terkait (seperti order_details dan shipment) sudah bisa diakses
    # melalui relasi yang didefinisikan di models.py
    
    context = {
        'segment': 'orders', # Agar menu 'Pesanan' tetap aktif
        'title': f'Detail Pesanan #{order.id_order}',
        'order': order
    }
    return render_template('pages/detail_shipments.html', **context)
# 👤 PROFIL SUPPLIER
@blueprint.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    supplier = Supplier.query.first()  # Ganti filter sesuai user login nanti

    # Field yang hanya bisa dibaca
    readonly_fields = ['id_supplier', 'email']
    full_width_fields = []  # Bisa isi ['alamat'] kalau ingin lebar penuh

    # Tambahkan field dinamis ke form
    for column in Supplier.__table__.columns:  # ✅ gunakan __table__
        if column.name not in readonly_fields:
            field = wtforms.StringField(column.name.title())
            setattr(ProfileForm, column.name, field)

    # Isi form dengan data supplier
    form = ProfileForm(obj=supplier)

    context = {
        'segment': 'profile',
        'title': 'Profil Supplier',
        'supplier': supplier,
        'form': form,
        'readonly_fields': readonly_fields,
        'full_width_fields': full_width_fields,
    }

    return render_template('pages/profile.html', **context)


# 🧠 Fallback template (404 / 500)
@blueprint.route('/<template>')
@login_required
def route_template(template):
    try:
        if not template.endswith('.html'):
            template += '.html'
        segment = get_segment(request)
        return render_template("pages/" + template, segment=segment)
    except TemplateNotFound:
        return render_template('home/page-404.html'), 404
    except:
        return render_template('home/page-500.html'), 500

# Helper
def get_segment(request):
    try:
        segment = request.path.split('/')[-1]
        return segment if segment else 'index'
    except:
        return None
# Custom template filter
@blueprint.app_template_filter("replace_value")
def replace_value(value, arg="_"):
    """
    Mengganti karakter tertentu (default: underscore) dengan spasi, lalu kapitalisasi awal kata.
    Contoh:
    "user_name" -> "User Name"
    """
    try:
        return value.replace(arg, " ").title()
    except Exception:
        return value

