from flaskr import db
from flaskr.models import Properties, ProductAccess, Site


def get_property(key):
    prop = Properties.query.filter(Properties.key == key).first()
    if prop:
        return prop.value
    return None


def update_property(key, value):
    current_value = Properties.query.filter(Properties.key == key).first()
    if current_value:
        current_value.value = value
    else:
        db.session.add(Properties(key=key, value=value))
    db.session.commit()


def delete_property(key):
    Properties.query.filter(Properties.key == key).delete()
    db.session.commit()


def get_properties():
    properties = {}
    for prop in Properties.query.all():
        properties[prop.key] = prop.value
    return properties


def get_products():
    return db.session.query(ProductAccess.name, ProductAccess.site_id, ProductAccess.url).distinct().order_by(
        ProductAccess.url.desc()).all()


def get_sites():
    return db.session.query(Site.url).distinct().all()
