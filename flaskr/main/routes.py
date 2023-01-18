import json

from flask import render_template, request, Blueprint, redirect, url_for, current_app
from flaskr import constants as c
from sqlalchemy import or_
import requests
from flaskr import db
from flaskr.models import Organisation, User, Properties, ProductAccess
import datetime

main = Blueprint('main', __name__)


@main.route("/", methods=['GET'])
@main.route("/home", methods=['GET'])
def home():
    organisation = Organisation.query.first()
    if organisation:
        return render_template('home.html', organisation=organisation.name, products=get_products())
    else:
        r = requests.get(
            url=c.GET_ORG + current_app.config['ORG_ID'],
            headers={'Authorization': f"Bearer {current_app.config['API_KEY']}"}
        )
        if r.status_code == 200:
            organisation = Organisation(org_id=r.json()['data']['id'], name=r.json()['data']['attributes']['name'])
            try:
                db.session.add(organisation)
                db.session.commit()
            except:
                pass
            return render_template('home.html', organisation=organisation.name)
        else:
            print(r.json())
        return render_template('home.html')


@main.route("/users", methods=['GET'])
def get_users():
    all_users = User.query.all()
    if len(all_users) == 0:
        return redirect(url_for('main.fetch_users'))
    users, end_date, days_inactive = handle_args_query(query=User.query, args=request.args)
    return render_template('user.html',
                           users=users,
                           title='Overview of all managed users',
                           organisation=get_organisation(),
                           last_sync=get_last_sync(),
                           duration=get_duration(),
                           products=get_products(),
                           includeInactive=request.args.get('includeInactive'),
                           includeNonBillable=request.args.get('includeNonBillable'),
                           showPois=request.args.get('showPois'),
                           daysInactive=days_inactive,
                           end_date=end_date)


@main.route("/users/fetch", methods=['GET', 'POST'])
def fetch_users():
    if request.method == 'GET':
        return render_template('user_fetch.html',
                               title="Fetch users")
    if request.method == 'POST':
        User.query.delete()
        ProductAccess.query.delete()
        db.session.commit()
        r = requests.get(
            url=c.GET_ORG + current_app.config['ORG_ID'] + '/users',
            headers={'Authorization': f"Bearer {current_app.config['API_KEY']}"}
        )
        if r.status_code == 200:
            user_sync_start = Properties.query.filter(Properties.key == 'user-sync-start').first()
            if user_sync_start:
                user_sync_start.value = datetime.datetime.now().strftime("%d.%m.%Y, %H:%M:%S")
            else:
                db.session.add(
                    Properties(key="user-sync-start", value=datetime.datetime.now().strftime("%d.%m.%Y, %H:%M:%S")))
            for user in r.json()['data']:
                last_active = user.get('last_active')
                if last_active:
                    last_active = datetime.datetime.strptime(last_active, '%Y-%m-%dT%H:%M:%S.%fZ')
                db_user = User(
                    account_id=user.get('account_id'),
                    account_type=user.get('account_type'),
                    account_status=user.get('account_status'),
                    name=user.get('name'),
                    email=user.get('email'),
                    access_billable=user.get('access_billable'),
                    last_active=last_active
                )
                db.session.add(db_user)
                for product in user.get('product_access'):
                    last_active = product.get('last_active')
                    if last_active:
                        last_active = datetime.datetime.strptime(last_active, '%Y-%m-%dT%H:%M:%S.%fZ')
                    db_product = ProductAccess(
                        name=product.get("name"),
                        site_id=product.get("siteId"),
                        url=product.get("url"),
                        last_active=last_active,
                        user_id=User.query.filter(User.account_id == user.get('account_id')).first().id
                    )
                    db.session.add(db_product)
            user_sync_end = Properties.query.filter(Properties.key == 'user-sync-end').first()
            if user_sync_end:
                user_sync_end.value = datetime.datetime.now().strftime("%d.%m.%Y, %H:%M:%S")
            else:
                db.session.add(
                    Properties(key="user-sync-end", value=datetime.datetime.now().strftime("%d.%m.%Y, %H:%M:%S")))
            db.session.commit()
        return redirect(url_for('main.get_users'))


@main.route("/user/<user_id>/products", methods=['GET'])
def get_user_products(user_id):
    product_access = ProductAccess.query.filter(ProductAccess.user_id == user_id).all()
    products = []
    for product in product_access:
        if product.last_active:
            last_active = product.last_active.strftime("%d.%m.%Y")
        else:
            last_active = 'Never'
        products.append({
            "name": product.name,
            "url": product.url,
            "last_active": last_active,
            "site_id": product.site_id
        })
    return products


@main.route("/product/<site_id>", methods=['GET'])
def product_info(site_id):
    all_products = ProductAccess.query.all()
    if len(all_products) == 0:
        return redirect(url_for('main.fetch_users'))
    name = request.args.get('name')
    query_products = db.session.query(User, ProductAccess).select_from(User).join(ProductAccess,
                                                                                  User.id == ProductAccess.user_id) \
        .filter(ProductAccess.site_id == site_id)
    query_url = ProductAccess.query.filter(ProductAccess.site_id == site_id).first()
    if name:
        query_products = query_products.filter(ProductAccess.name == name)
        title = query_url.url.replace('.atlassian.net', '') + " - " + name
    else:
        title = query_url.url.replace('.atlassian.net', '')
    results, end_date, days_inactive = handle_args_query(query=query_products, args=request.args)
    if not results:
        return render_template('product.html',
                               results=results,
                               title=title,
                               organisation=get_organisation())
    end_date = get_end_date(30)
    return render_template('product.html',
                           results=results,
                           title=title,
                           organisation=get_organisation(),
                           last_sync=get_last_sync(),
                           duration=get_duration(),
                           products=get_products(),
                           includeInactive=request.args.get('includeInactive'),
                           includeNonBillable=request.args.get('includeNonBillable'),
                           showPois=request.args.get('showPois'),
                           daysInactive=days_inactive,
                           end_date=end_date)


def handle_args_query(query, args):
    include_inactive = args.get('includeInactive')
    include_non_billable = args.get('includeNonBillable')
    show_pois = args.get('showPois')
    days_inactive = args.get('daysInactive')
    if show_pois and show_pois == 'true':
        include_inactive = 'false'
        include_non_billable = 'false'
    if include_inactive and include_inactive.lower() == 'false':
        query = query.filter(User.account_status == 'active')
    if include_non_billable and include_non_billable.lower() == 'false':
        query = query.filter(User.access_billable == True)
    if days_inactive:
        days_inactive = int(days_inactive)
        if days_inactive < 1:
            days_inactive = 1
        if days_inactive > 367:
            days_inactive = 367
        if days_inactive == 366:
            query = query.filter(User.last_active == None)
        else:
            query = query.filter(or_(User.last_active == None,
                                     User.last_active < datetime.datetime.now() - datetime.timedelta(
                                         days=days_inactive)))
        end_date = get_end_date(days_inactive)
    else:
        days_inactive = 30
        end_date = get_end_date(30)
    return query.all(), end_date, days_inactive


def get_products():
    return db.session.query(ProductAccess.name, ProductAccess.site_id, ProductAccess.url).distinct().order_by(ProductAccess.url.desc()).all()


def get_organisation():
    return Organisation.query.first().name


def get_last_sync():
    last_sync = Properties.query.filter(Properties.key == 'user-sync-end').first()
    if last_sync:
        return last_sync.value
    else:
        return 'Never'


def get_duration():
    last_sync = Properties.query.filter(Properties.key == 'user-sync-end').first()
    if last_sync:
        last_sync_dt = datetime.datetime.strptime(last_sync.value, "%d.%m.%Y, %H:%M:%S")
    else:
        return None
    begin_sync = Properties.query.filter(Properties.key == 'user-sync-start').first()
    if begin_sync:
        begin_sync_dt = datetime.datetime.strptime(begin_sync.value, "%d.%m.%Y, %H:%M:%S")
    if last_sync_dt and begin_sync_dt:
        return (last_sync_dt - begin_sync_dt).total_seconds()
    return None


def get_end_date(daysInactive):
    if daysInactive:
        return datetime.datetime.now() - datetime.timedelta(days=daysInactive)
    else:
        return None
