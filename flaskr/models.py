from flaskr import db
from datetime import datetime

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.String(30), nullable=False, unique=True)
    account_type = db.Column(db.String(30), nullable=False)
    account_status = db.Column(db.String(20), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    access_billable = db.Column(db.Boolean, nullable=False)
    last_active = db.Column(db.DateTime)
    product_accesses = db.relationship('ProductAccess', backref='user', lazy=True)

    def __repr__(self):
        return f'User({self.name} - {self.account_id})'


class ProductAccess(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    site_id = db.Column(db.String(50))
    url = db.Column(db.String(256))
    last_active = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f'ProductAccess({self.name})'


class Site(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(128), nullable=False)

    def __repr__(self):
        return f'Site({self.url})'

    def as_dict(self):
        return {
            "id": self.id,
            "url": self.url
        }

class Properties(db.Model):
    key = db.Column(db.String(50), primary_key=True)
    value = db.Column(db.String(50))


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    site = db.Column(db.String(50))
    app_key = db.Column(db.String(150))
    product = db.Column(db.String(50))
    plan = db.Column(db.String(10))
    billing_cycle = db.Column(db.String(50))
    next_billing = db.Column(db.String(10))

    def __repr__(self):
        return f'Product({self.site}, {self.product})'

    def as_dict(self):
        return {
            "id": self.id,
            "site": self.site,
            "app_key": self.app_key,
            "product": self.product,
            "plan": self.plan,
            "billing_cycle": self.billing_cycle,
            "next_billing": self.next_billing,
        }

