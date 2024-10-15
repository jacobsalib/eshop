from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import stripe
from flask_mail import Mail

db = SQLAlchemy()
mail = Mail()
DB_NAME= 'database.db'


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'gsdgaaf33adarrasd'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    # app.config['UPLOAD_FOLDER'] = './static/photos'
    app.config['UPLOAD_FOLDER'] = 'https://jacobsalib.pythonanywhere.com/static/images'

    stripe.api_key = 'sk_test_51PyIz6GCnsDUo2I6Oe2RmCdd9TIfcgSGizUh09Wz9e7KeMrr5G5LQtRTp3OLysm3GwzxqZ4UkGlWB50sRbxhUcU500zNPy1Cao'
    app.config['STRIPE_PUBLIC_KEY'] = 'pk_test_51PyIz6GCnsDUo2I6pa9gwkEqpk7KGOAiLT4frLH4ODssM1xWwGh2hiD97WUwS43qpta5GErUQpPKRjLZAb6Ovx1C00l88oWPWb'
    app.config['STRIPE_SECRET_KEY'] = 'sk_test_51PyIz6GCnsDUo2I6Oe2RmCdd9TIfcgSGizUh09Wz9e7KeMrr5G5LQtRTp3OLysm3GwzxqZ4UkGlWB50sRbxhUcU500zNPy1Cao'

    app.config['MAIL_SERVER'] = 'smtp.outlook.com'  
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = 'jacobsalib@hotmail.com'  
    app.config['MAIL_PASSWORD'] = '19966848ganning'  
    app.config['MAIL_DEFAULT_SENDER'] = 'jacobsalib@hotmail.com'  

    db.init_app(app)
    mail.init_app(app)


    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    from .models import User

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    

    with app.app_context():
        db.create_all()
        print('Created database!')

    
    return app