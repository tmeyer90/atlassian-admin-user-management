from flaskr import db


class Organisation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    org_id = db.Column(db.String(100), nullable=False, unique=True)
    name = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f'Organisation({self.name})'


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
    site_id = db.Column(db.String(50), nullable=False)
    url = db.Column(db.String(256), nullable=False)
    last_active = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f'ProductAccess({self.name}'


class Properties(db.Model):
    key = db.Column(db.String(50), primary_key=True)
    value = db.Column(db.String(50))
