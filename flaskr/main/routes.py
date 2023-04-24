from flask import render_template, Blueprint
from flaskr.util import constants as c
from flaskr.configuration.routes import get_products, get_properties


main = Blueprint('main', __name__)


@main.route("/", methods=['GET'])
@main.route("/home", methods=['GET'])
def home():
    return render_template('home.html',
                           products=get_products(),
                           properties=get_properties(),
                           c=c)
