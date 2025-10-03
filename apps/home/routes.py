# -*- encoding: utf-8 -*-
"""
Custom Supplier Module (based on AppSeed)
"""

import wtforms, os
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
        db.session.query(Product.nama_product, func.sum(OrderDetail.jumlah).label('total_terjual'))
        .join(OrderDetail, OrderDetail.id_product == Product.id_product)
        .group_by(Product.id_product)
        .order_by(func.sum(OrderDetail.jumlah).desc())
        .first()
    )
    top_product = top_product_query.nama_product if top_product_query else "Belum Ada Order"

    # Total Pendapatan (harga * jumlah)
    total_pendapatan_query = (
        db.session.query(func.sum(Product.harga * OrderDetail.jumlah))
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
@blueprint.route('/products')
@login_required

# VIEW PRODUK
def products():
    products = Product.query.all()
    context = {
        'segment': 'products',
        'title': 'Kelola Produk',
        'products': products
    }
    return render_template('pages/products.html', products=products)

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

    # 4️⃣ Render ke halaman detail
    return render_template('pages/view_product.html', **context)

# 🧾 PESANAN
@blueprint.route('/orders')
@login_required
def orders():
    orders = Orders.query.all()
    context = {
        'segment': 'orders',
        'title': 'Pesanan Masuk',
        'orders': orders
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

# 👤 PROFIL SUPPLIER
@blueprint.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    class ProfileForm(FlaskForm):
        pass

    readonly_fields = Users.readonly_fields if hasattr(Users, 'readonly_fields') else ['id', 'username', 'email']
    for column in Users.__table__.columns:
        if column.name not in readonly_fields:
            field = wtforms.StringField(column.name.title())
            setattr(ProfileForm, column.name, field)

    form = ProfileForm(obj=current_user)

    if form.validate_on_submit():
        for field_name, field_value in form.data.items():
            if field_name not in readonly_fields:
                setattr(current_user, field_name, field_value)
        db.session.commit()
        return redirect(url_for('home_blueprint.profile'))

    context = {
        'segment': 'profile',
        'title': 'Profil Supplier',
        'form': form,
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

