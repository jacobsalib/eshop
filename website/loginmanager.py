from flask_login import LoginManager
from .models import User
from flask import Flask

# app = Flask(__name__)
# login_manager = LoginManager()
# login_manager.login_view = 'auth.login'
# login_manager.init_app(app)

# @login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))