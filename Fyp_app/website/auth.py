from flask import Blueprint, render_template ,request , flash, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from .models import User, Mysql
from flask_login import login_user, login_required, logout_user, current_user
import random
mysql = Mysql()

def generate_user_id():
    # Generate a new random user ID
    user_id = random.randint(100000, 999999)
    return user_id
def insert_user_id_to_audiogram(user_id, user_email):
    # Add the required SQL query to insert the user's email (user ID) into the audiogram table
    sql = f"INSERT INTO audiogram (id, userid) VALUES ({user_id}, '{user_email}')"
    # sql = f"INSERT INTO audiogram (id, userid, l500, l1000, l2000, l3000, l4000, l6000, l8000, r500, r1000, r2000, r3000, r4000, r6000, r8000) VALUES ({user_id}, {user_email}, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)"
    
    mysql.cursor.execute(sql)
    mysql.mydb.commit()

auth = Blueprint('auth', __name__)
 
@auth.route('/login' , methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first() #querying user mail
        if user:
            if check_password_hash(user.password, password):#checking the entered password
                flash("You are logged in", category='success')
                login_user(user, remember=True)
                # user_id = generate_user_id()
                # insert_user_id_to_audiogram(user_id, email)
                return redirect(url_for('views.home'))
            else:
                flash('Invalid Password', category= 'error')
        else:
            flash('User not found',category= 'error')
        #insert blank row everythin else 0
        

    return render_template("login.html", user= current_user) #can pass variable from here to ur templates(varname = "something")

@auth.route('/logout')
@login_required #it says user is req to log in  before
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/sign-up', methods = ['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email is already taken','error')

        if(len(email)< 4):
            flash('email must be > 4 characters', category='error')
        elif len(first_name) < 2:
            flash('firstname must be > 1 character', category='error')
        elif password1 != password2 :
            flash('pwds dont match!', category='error')
        elif len(password1) < 3:
            flash('pwd should be greater than 3 characters', category='error')
        else: 
            # save user to database here
            new_user = User(email= email, first_name = first_name, password=generate_password_hash(password1, method='pbkdf2:sha256'))
            
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('Acount created!!', category='success')

            user_id = generate_user_id()
            insert_user_id_to_audiogram(user_id, email)


            return redirect(url_for('views.home'))

    return render_template("sign_up.html", user = current_user)








































































# from flask import Blueprint, render_template ,request , flash, redirect, url_for
# from .models import User
# from werkzeug.security import generate_password_hash, check_password_hash
# from . import db
# from flask_login import login_user, login_required, logout_user, current_user

# auth = Blueprint('auth', __name__)
 
# @auth.route('/login' , methods = ['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         email = request.form['email']
#         password = request.form['password']
#         user = User.query.filter_by(email=email).first() #querying user mail
#         if user:
#             if check_password_hash(user.password, password):#checking the entered password
#                 flash("You are logged in", category='success')
#                 login_user(user, remember=True)
#                 return redirect(url_for('views.home'))
#             else:
#                 flash('Invalid Password', category= 'error')
#         else:
#             flash('User not found',category= 'error')

#     return render_template("login.html", user= current_user) #can pass variable from here to ur templates(varname = "something")

# @auth.route('/logout')
# @login_required #it says user is req to log in  before
# def logout():
#     logout_user()
#     return redirect(url_for('auth.login'))

# @auth.route('/sign-up', methods = ['GET', 'POST'])
# def sign_up():
#     if request.method == 'POST':
#         email = request.form.get('email')
#         first_name = request.form.get('firstName')
#         password1 = request.form.get('password1')
#         password2 = request.form.get('password2')

#         user = User.query.filter_by(email=email).first()
#         if user:
#             flash('Email is already taken','error')

#         if(len(email)< 4):
#             flash('email must be > 4 characters', category='error')
#         elif len(first_name) < 2:
#             flash('firstname must be > 1 character', category='error')
#         elif password1 != password2 :
#             flash('pwds dont match!', category='error')
#         elif len(password1) < 3:
#             flash('pwd should be greater than 3 characters', category='error')
#         else: 
#             # save user to database here
#             new_user = User(email= email, first_name = first_name, password=generate_password_hash(password1, method='pbkdf2:sha256'))
#             db.session.add(new_user)
#             db.session.commit()
#             login_user(new_user, remember=True)
#             flash('Acount created!!', category='success')
#             return redirect(url_for('views.home'))

#     return render_template("sign_up.html", user = current_user)