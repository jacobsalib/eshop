from flask import Blueprint, render_template
from flask_login import login_required, current_user

views = Blueprint('views', __name__)

@views.route('/', methods=['GET', 'POST'])
def home():
    return render_template('index.html')

@views.route("/<string:page_name>", methods=['GET', 'POST'])
def html_page(page_name):
    return  render_template(page_name)

@views.route('/confirm.html', methods=['GET', 'POST'])
def created():
    return render_template('confirm.html')

# @views.route('/glasses.html', methods=['GET', 'POST'])
# @login_required
# def access_glasses():
#     return render_template('glasses.html')

# @views.route('/shop.html', methods=['GET', 'POST'])
# @login_required
# def access_shop():
#     return render_template('shop.html')
