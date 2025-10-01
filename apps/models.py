# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
from email.policy import default
from apps import db
from sqlalchemy.exc import SQLAlchemyError
from apps.exceptions.exception import InvalidUsage
import datetime as dt
from sqlalchemy.orm import relationship
from enum import Enum
from apps import db

# 🏭 Tabel Supplier
class Supplier(db.Model):
    __tablename__ = 'supplier'
    id_supplier = db.Column(db.Integer, primary_key=True)
    nama_supplier = db.Column(db.String(100))
    alamat = db.Column(db.String(200))
    telepon = db.Column(db.String(20))
    email = db.Column(db.String(100))

    # Relasi ke produk
    products = db.relationship('Product', backref='supplier', lazy=True)

# 🥦 Tabel Product
class Product(db.Model):
    __tablename__ = 'product'
    id_product = db.Column(db.Integer, primary_key=True)
    nama_product = db.Column(db.String(100))
    kategori = db.Column(db.String(50))
    harga = db.Column(db.Float)
    stok = db.Column(db.Integer)
    satuan = db.Column(db.String(20))
    berat = db.Column(db.Float)
    tanggal_masuk = db.Column(db.Date)
    expired_date = db.Column(db.Date)
    deskripsi = db.Column(db.Text)
    gambar = db.Column(db.String(1024))

    id_supplier = db.Column(db.Integer, db.ForeignKey('supplier.id_supplier'))

    # Relasi ke orders
    orders = db.relationship('Orders', backref='product', lazy=True)

# 🧾 Tabel Orders
class Orders(db.Model):
    __tablename__ = 'orders'
    id_order = db.Column(db.Integer, primary_key=True)
    id_product = db.Column(db.Integer, db.ForeignKey('product.id_product'))
    id_supplier = db.Column(db.Integer, db.ForeignKey('supplier.id_supplier'))
    nama_pemesan = db.Column(db.String(100))
    jumlah = db.Column(db.Integer)
    tanggal_order = db.Column(db.Date)
    status_order = db.Column(db.String(50))

    # Relasi ke shipment
    shipments = db.relationship('Shipment', backref='order', lazy=True)

# 🚚 Tabel Shipment
class Shipment(db.Model):
    __tablename__ = 'shipment'
    id_shipment = db.Column(db.Integer, primary_key=True)
    id_order = db.Column(db.Integer, db.ForeignKey('orders.id_order'))
    distributor_name = db.Column(db.String(100))
    no_resi = db.Column(db.String(50))
    tanggal_kirim = db.Column(db.Date)
    status_kirim = db.Column(db.String(50)) 
