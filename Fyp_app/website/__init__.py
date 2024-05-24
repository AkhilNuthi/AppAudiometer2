from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_migrate import Migrate
from flask_login import LoginManager #helps manage login related stuff
#import mysql.connector
#from .models import User, Mysql

db = SQLAlchemy()
DB_NAME = "database.db" 


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'dhvani' #encryption
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app) #telling the db we r using this app
    migrate = Migrate(app, db)
   

    from .views import views
    from .auth import auth
    # from .models import User, Audiogram 
    
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    from .models import User, Audiogram    
    #calling to check and define our models
    with app.app_context():
        db.create_all()
    
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    return app


#checking if db exists if not creating
# def create_database(app):
#     if not path.exists('website/'+ DB_NAME):
#         db.create_all()
#         print('created db!')

