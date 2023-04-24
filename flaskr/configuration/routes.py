from flask import render_template, request, Blueprint, redirect, url_for, flash
from flaskr.util import constants as c
from flaskr.configuration import atlas_rest_endpoints as arp
import requests
from requests.auth import HTTPBasicAuth
from flaskr import db
from flaskr.models import Site, Product

from flaskr.util.functions import get_properties, update_property, delete_property, get_property, get_products

config = Blueprint('config', __name__)


@config.route("/configuration", methods=['GET'])
def configuration():
    return render_template('configuration.html',
                           products=get_products(),
                           properties=get_properties(),
                           c=c)


@config.route("/configuration/atlas", methods=['POST'])
def atlas_configuration():
    if request.form['action'] == 'post':
        try:
            api_key = request.form['apiKey']
            site = request.form['site']
            email = request.form['email']
            user_pat = request.form['pApiKey']
            if api_key != c.PW_OBF:
                r = requests.get(
                    url=arp.GET_ORGS,
                    headers={'Authorization': f"Bearer {api_key}"}
                )
                if r.status_code == 200:
                    update_property(c.ORG_NAME, r.json()['data'][0]['attributes']['name'])
                    update_property(c.ORG_ID, r.json()['data'][0]['id'])
                else:
                    flash(f"Error on organisation validation: {r.reason}", category='danger')
                    return redirect(url_for('config.configuration'))
                update_property(c.ORG_ID, r.json()['data'][0]['id'])
                update_property(c.ORG_API_KEY, api_key)
                update_property(c.ORG_API_KEY_VALID, request.form['validUntil'])
                flash('Successfully stored the organisation values', category='success')
            if user_pat != c.PW_OBF:
                r = requests.get(
                    url=arp.GET_MYSELF.replace('<SITE>', site),
                    auth=HTTPBasicAuth(email, user_pat)
                )
                if r.status_code != 200:
                    flash(f"Error on user validation: {r.reason}", category='danger')
                    return redirect(url_for('config.configuration'))
                update_property(c.ORG_SITE, site)
                update_property(c.USER_MAIL, email)
                update_property(c.USER_PAT, user_pat)
                update_property(c.USER_PAT_VALID, request.form['validPUntil'])
                db.session.add(Site(url=f'https://{site}.atlassian.net'))
                db.session.commit()
                flash('Successfully stored the personal values', category='success')
        except Exception as e:
            flash(f'Not possible to store the values: {e}', category='danger')
    if request.form['action'] == 'delete':
        delete_property(c.ORG_ID)
        delete_property(c.ORG_NAME)
        delete_property(c.ORG_API_KEY)
        delete_property(c.ORG_API_KEY_VALID)
        delete_property(c.ORG_SITE)
        delete_property(c.USER_MAIL)
        delete_property(c.USER_PAT)
        delete_property(c.USER_PAT_VALID)
    return redirect(url_for('config.configuration'))


@config.route("/configuration/sites", methods=['GET', 'POST'])
def sites_configuration():
    if request.method == 'POST':
        site = request.json[0]
        db_site = Site(url=site.get('site'))
        db.session.add(db_site)
        db.session.commit()
        return {'data': [db_site.as_dict()]}, 201
    return {'data': [dict(row) for row in db.session.query(Site.__table__).all()]}, 200


@config.route("/configuration/sites/<id>", methods=['PUT', 'DELETE'])
def site_configuration(id):
    if request.method == 'PUT':
        for idx, i in enumerate(str(id).split(',')):
            sites = request.json[idx]
            db_site = Site.query.filter(Site.id == i.strip()).first()
            if not db_site:
                flash(f"No site found with id: {i.strip()}", category='danger')
                return '', 400
            db_site.url = sites.get('site')
            db.session.add(db_site)
        db.session.commit()
        return {'data': [dict(row) for row in db.session.query(Site.__table__).all()]}, 201
    if request.method == 'DELETE':
        for i in str(id).split(','):
            Site.query.filter(Site.id == i.strip()).delete()
        db.session.commit()
        return '', 204


@config.route("/configuration/products", methods=['GET'])
def products_configuration():
    return {'data': [dict(row) for row in db.session.query(Product.__table__).all()]}, 200


@config.route("/configuration/products/<id>", methods=['PUT', 'DELETE'])
def product_configuration(id):
    if request.method == 'PUT':
        for idx, i in enumerate(str(id).split(',')):
            product = request.json[idx]
            db_product = Product.query.filter(Product.id == i.strip()).first()
            if not db_product:
                flash(f"No entry found with id: {i.strip()}", category='danger')
                return '', 400
            if product.get('plan'):
                db_product.plan = product.get('plan')
            if product.get('billing_cycle'):
                db_product.billing_cycle = product.get('billing_cycle')
            if product.get('next_billing'):
                db_product.next_billing = product.get('next_billing')
            db.session.add(db_product)
        db.session.commit()
        return {'data': [dict(row) for row in db.session.query(Product.__table__).all()]}, 201
    if request.method == 'DELETE':
        for i in str(id).split(','):
            Product.query.filter(Product.id == i.strip()).delete()
        db.session.commit()
        return '', 204


@config.route("/configuration/load-products", methods=['POST'])
def load_products():
    db.session.query(Product.__table__).delete()
    db.session.commit()
    user = get_property(c.USER_MAIL)
    user_pat = get_property(c.USER_PAT)
    for site in db.session.query(Site.__table__).all():
        # Check Jira
        r = requests.get(
            url=arp.GET_JIRA_APPS.replace('https://<SITE>.atlassian.net', site.url),
            auth=HTTPBasicAuth(user, user_pat))
        if r.status_code == 200:
            db.session.add(Product(
                site=site.url,
                app_key=c.JSW_KEY,
                product=c.JSW_NAME
            ))
            for appl in r.json()['plugins']:
                app_key = appl.get('key')
                if app_key == c.JSM_KEY or app_key == c.JWM_KEY:
                    db.session.add(Product(
                        site=site.url,
                        app_key=app_key,
                        product=appl.get('name')
                    ))
                    continue
                if appl.get('userInstalled'):
                    r = requests.get(
                        url=arp.GET_JIRA_APP_LICENSE.replace('https://<SITE>.atlassian.net', site.url).replace(
                            '<APP_KEY>', app_key),
                        auth=HTTPBasicAuth(user, user_pat)
                    )
                    if r.status_code == 200 and r.json().get('valid'):
                        db.session.add(Product(
                            site=site.url,
                            app_key=app_key,
                            product=appl.get('name')
                        ))
        db.session.commit()
        # Check Confluence
        r = requests.get(
            url=arp.GET_CONF_APPS.replace('https://<SITE>.atlassian.net', site.url),
            auth=HTTPBasicAuth(user, user_pat))
        if r.status_code == 200:
            db.session.add(Product(
                site=site.url,
                app_key=c.CONF_KEY,
                product=c.CONF_NAME
            ))
            for appl in r.json()['plugins']:
                app_key = appl.get('key')
                if appl.get('userInstalled'):
                    r = requests.get(
                        url=arp.GET_CONF_APP_LICENSE.replace('https://<SITE>.atlassian.net', site.url).replace(
                            '<APP_KEY>', app_key),
                        auth=HTTPBasicAuth(user, user_pat)
                    )
                    if r.status_code == 200 and r.json().get('valid'):
                        db.session.add(Product(
                            site=site.url,
                            app_key=app_key,
                            product=appl.get('name')
                        ))
        db.session.commit()
    return '', 200


@config.route("/atlas-rest-endpoints", methods=['GET'])
def atlas_rest_endpoints():
    endpoints = []
    for k, v in arp.__dict__.items():
        if 'BASE_URL' in k:
            continue
        if str(k).startswith('GET_'):
            endpoints.append({'url': v, 'method': 'GET'})
        if str(k).startswith('POST_'):
            endpoints.append({'url': v, 'method': 'POST'})
        if str(k).startswith('PUT_'):
            endpoints.append({'url': v, 'method': 'PUT'})
        if str(k).startswith('DELETE_'):
            endpoints.append({'url': v, 'method': 'DELETE'})
    return render_template('rest-end-points.html', endpoints=endpoints, properties=get_properties(), c=c)
