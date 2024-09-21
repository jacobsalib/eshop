from flask import Blueprint, render_template
from flask_login import login_required, current_user
from .models import Product


views = Blueprint('views', __name__)

@views.route('/', methods=['GET', 'POST'])
def home():
    return render_template('index.html')


@views.route("/<string:page_name>", methods=['GET', 'POST'])
def html_page(page_name):
    products = Product.query.all()
    return  render_template(page_name , products=products)


@views.route('/confirm.html', methods=['GET', 'POST'])
def created():
    return render_template('confirm.html')


@views.route('/glasses.html', methods=['GET', 'POST'])
def view_glasses():
    products = Product.query.all()
    return  render_template('glasses.html',products=products)


@views.route("/<string:product_name>", methods=['GET', 'POST'])
def ppage(page_name):
    return  render_template(page_name.html)


@views.route('/cart.html')
@login_required
def cart():
    return render_template('cart.html', current_user=current_user)


@views.route('/order_confirmation.html')
@login_required
def order_confirmation():
    return render_template('order_confirmation.html', current_user=current_user)
