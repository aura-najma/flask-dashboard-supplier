# -*- encoding: utf-8 -*-
"""
Custom Supplier Module (based on AppSeed)
"""

import wtforms
from sqlalchemy import func
from apps.home import blueprint
from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from jinja2 import TemplateNotFound
from apps import db
from apps.models import Product, Orders, Shipment, Supplier  # Pastikan ini sudah ada di models.py
from apps.authentication.models import Users
from flask_wtf import FlaskForm

# 🏠 DASHBOARD
@blueprint.route('/')
@blueprint.route('/index')
@login_required
def index():
    total_products = Product.query.count()
    total_orders = Orders.query.count()
    top_product_query = (
        db.session.query(Product.nama_product, func.sum(Orders.jumlah).label('total_terjual'))
        .join(Orders, Orders.id_product == Product.id_product)
        .group_by(Product.id_product)
        .order_by(func.sum(Orders.jumlah).desc())
        .first()
    )

    top_product = top_product_query.nama_product if top_product_query else "Belum Ada Order"
    total_pendapatan_query = (
        db.session.query(func.sum(Product.harga * Orders.jumlah))
        .join(Orders, Orders.id_product == Product.id_product)
        .scalar()
    )
    total_pendapatan = total_pendapatan_query if total_pendapatan_query else 0
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

# EDIT PRODUK
@blueprint.route('/products/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_product(id):


    return render_template('pages/edit_product.html', product=product)

# DELETE PRODUK
@blueprint.route('/products/delete/<int:id>')
@login_required
def delete_product(id):

    return redirect(url_for('home_blueprint.products'))

# VIEW DETAIL PRODUK
@blueprint.route('/products/view/<int:id>')
@login_required
def view_product(id):
    return render_template('pages/view_product.html', product=product)

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