# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
from apps import db
from sqlalchemy.exc import SQLAlchemyError
from apps.exceptions.exception import InvalidUsage
import datetime as dt
from sqlalchemy.orm import relationship
from enum import Enum
# =======================
# Tabel SUPPLIER
# =======================
class Supplier(db.Model):
    __tablename__ = 'supplier'

    id_supplier = db.Column(db.Integer, primary_key=True)
    nama_supplier = db.Column(db.String(100), nullable=False)
    kota = db.Column(db.String(255))
    telepon = db.Column(db.String(20))
    email = db.Column(db.String(100))

    # Relasi: 1 Supplier bisa punya banyak Product dan banyak OrderDetail
    products = db.relationship('Product', back_populates='supplier', lazy=True)
    order_details = db.relationship('OrderDetail', back_populates='supplier', lazy=True)

    def __repr__(self):
        return f"<Supplier {self.nama_supplier}>"


# =======================
# Tabel PRODUCT
# =======================
class Product(db.Model):
    __tablename__ = 'product'

    id_product = db.Column(db.String(10), primary_key=True)
    nama_product = db.Column(db.String(100), nullable=False)
    kategori = db.Column(db.String(50))
    harga = db.Column(db.Float)
    stok = db.Column(db.Integer)
    satuan = db.Column(db.String(20))
    berat = db.Column(db.Float)
    tanggal_masuk = db.Column(db.Date)
    expired_date = db.Column(db.Date)
    deskripsi = db.Column(db.Text)
    gambar = db.Column(db.String(1024))

    # FK ke Supplier
    id_supplier = db.Column(db.Integer, db.ForeignKey('supplier.id_supplier'), nullable=False)

    # Relasi dua arah
    supplier = db.relationship('Supplier', back_populates='products')
    order_details = db.relationship('OrderDetail', back_populates='product', lazy=True)

    def __repr__(self):
        return f"<Product {self.id_product} - {self.nama_product}>"


# =======================
# Tabel ORDER
# =======================
class Orders(db.Model):
    __tablename__ = 'orders'

    id_order = db.Column(db.Integer, primary_key=True)
    nama_pemesan = db.Column(db.String(100), nullable=False)
    asal_pemesan = db.Column(db.String(100))
    total_berat = db.Column(db.Numeric(10, 2))
    tanggal_order = db.Column(db.Date)
    status_order = db.Column(db.String(50))

    # Relasi: 1 order punya banyak detail & 1 shipment
    order_details = db.relationship('OrderDetail', back_populates='order', lazy=True)
    shipment = db.relationship('Shipment', back_populates='order', uselist=False)

    def __repr__(self):
        return f"<Order {self.id_order} - {self.nama_pemesan}>"


# =======================
# Tabel ORDER DETAIL
# =======================
class OrderDetail(db.Model):
    __tablename__ = 'order_detail'

    id_detail = db.Column(db.Integer, primary_key=True)
    id_order = db.Column(db.Integer, db.ForeignKey('orders.id_order'), nullable=False)
    id_product = db.Column(db.String(10), db.ForeignKey('product.id_product'), nullable=False)
    id_supplier = db.Column(db.Integer, db.ForeignKey('supplier.id_supplier'), nullable=False)
    jumlah = db.Column(db.Integer)
    berat = db.Column(db.Numeric(10, 2))

    # Relasi dua arah
    order = db.relationship('Orders', back_populates='order_details')
    product = db.relationship('Product', back_populates='order_details')
    supplier = db.relationship('Supplier', back_populates='order_details')

    def __repr__(self):
        return f"<OrderDetail {self.id_detail} - Orders {self.id_order}>"


# =======================
# Tabel SHIPMENT
# =======================
class Shipment(db.Model):
    __tablename__ = 'shipment'

    id_shipment = db.Column(db.Integer, primary_key=True)
    id_order = db.Column(db.Integer, db.ForeignKey('orders.id_order'), nullable=False)
    distributor_name = db.Column(db.String(100))
    no_resi = db.Column(db.String(50))
    tanggal_kirim = db.Column(db.Date)
    status_kirim = db.Column(db.String(50))

    # Relasi dua arah
    order = db.relationship('Orders', back_populates='shipment')

    def __repr__(self):
        return f"<Shipment {self.id_shipment} - Orders {self.id_order}>"