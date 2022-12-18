from flask import Flask , redirect , render_template, request, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import  create_engine, MetaData, Table, Column, Integer, String, ForeignKey
from flask_login import LoginManager , UserMixin , login_required ,login_user, logout_user, current_user
import re
from datetime import datetime

app=Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///db.db'
app.config['SECRET_KEY']='981031'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=True
app.config['SQLALCHEMY_BINDS'] = {
    'my_sql1': 'sqlite:///tvnshow.db',
}
db = SQLAlchemy(app)


login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'get_home'
login_manager.init_app(app)

class User(UserMixin,db.Model):
    id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    first_name = db.Column(db.String(200))
    last_name = db.Column(db.String(200))
    email = db.Column(db.String(200))
    password = db.Column(db.String(200))

class TVShow(db.Model):
    __bind_key__ = 'my_sql1'
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    title = db.Column(db.String(200))
    network = db.Column(db.String(200))
    release_date =  db.Column(db.Date())
    description = db.Column(db.String(4000))
    email = db.Column(db.String(200))
    first_name= db.Column(db.String(200))
    last_name= db.Column(db.String(200))

@app.before_first_request
def create_tables():
    db.create_all()


@login_manager.user_loader
def get(id):
    return User.query.get(id)

@app.route('/',methods=['GET'])
def get_home():
     return render_template('login.html')

@app.route('/shows',methods=['GET'])
@login_required
def get_shows():
    ####
    myresult = {'first_name': '', 'last_name': '', 'email': '', 'password': '', 'confirm_password': '', 'tv_shows': None}
    myresult['email'] = session["email"]
    # myresult['password'] = session["password"]
    myresult['first_name'] = session["first_name"]
    myresult['last_name'] = session["last_name"]
    myresult['tv_shows'] = TVShow.query.all()
    return render_template('shows.html', result=myresult)


@app.route('/shows/new', methods=['GET'])
def create_shows_original():
    return render_template('shows_add.html')

@app.route('/shows/add', methods=['POST'])
def create_shows():
    title = request.form['title']
    network = request.form['network']
    temp_release_date = request.form['release_date']
    expiration_year  = int(temp_release_date[:4])
    expiration_month =  int(temp_release_date[5:7])
    expiration_date = int(temp_release_date[8:10])
    release_date =datetime(expiration_year,expiration_month,expiration_date)
    description = request.form['description']
    my_show =  TVShow(title=title,network=network,release_date=release_date,description=description,email=session['email'],first_name=session['first_name'],last_name=session['last_name'])
    db.session.add(my_show)
    db.session.commit()
    # TVShow.query.add(my_show)
    # TVShow.query.commit()
    ####
    myresult = {'first_name': '', 'last_name': '', 'email': '', 'password': '', 'confirm_password': '', 'tv_shows': None}
    myresult['email'] = session["email"]
    # myresult['password'] = session["password"]
    myresult['first_name'] = session["first_name"]
    myresult['last_name'] = session["last_name"]
    myresult['tv_shows'] = TVShow.query.all()
    return render_template('shows.html', result=myresult)

@app.route('/shows/<int:id>', methods=['GET'])
def shows_item(id):
    my_show = TVShow.query.filter_by(id=id).first_or_404()
    print('------------------------------')
    myresult = {'id': '', 'title': '', 'network': '', 'release_date': None, 'description': '', 'first_name':'', 'last_name': ''}
    myresult['id'] = id
    myresult['title']= my_show.title
    myresult['network'] = my_show.network
    myresult['release_date'] = my_show.release_date
    myresult['description'] = my_show.description
    myresult['first_name'] = my_show.first_name
    myresult['last_name'] = my_show.last_name
    return render_template('tvshow_item.html', result=myresult)

@app.route('/shows/edit/<int:id>', methods=['GET'])
def edit_item(id):
    my_show = TVShow.query.filter_by(id=id).first_or_404()
    myresult = {'id': '', 'title': '', 'network': '', 'release_date': None, 'description': '', 'first_name':'', 'last_name': '', 'id': 0}
    myresult['id'] = id
    myresult['title']= my_show.title
    myresult['network'] = my_show.network
    myresult['release_date'] = my_show.release_date
    myresult['description'] = my_show.description
    myresult['first_name'] = my_show.first_name
    myresult['last_name'] = my_show.last_name
    myresult['id'] = id
    return render_template('shows_edit.html', result=myresult)

@app.route('/shows/update/<int:id>', methods=['POST'])
def update_item(id):
    title = request.form['title']
    network = request.form['network']
    release_date = request.form['release_date']
    description = request.form['description']
    ### Update Database
    my_show = TVShow.query.filter_by(id=id).first_or_404()
    my_show.title = title
    my_show.network = network
    print('=-==========')
    print(release_date)
    expiration_year  = int(release_date[:4])
    expiration_month =  int(release_date[5:7])
    expiration_date = int(release_date[8:10])
    my_show.release_date =datetime(expiration_year,expiration_month,expiration_date)
    my_show.description = description
    db.session.commit()
    # TVShow.commit()
    myresult = {'id': '', 'first_name': '', 'last_name': '', 'email': '', 'password': '', 'confirm_password': '', 'tv_shows': None}
    myresult['email'] = session["email"]
    myresult['id'] = id
    # myresult['password'] = session["password"]
    myresult['first_name'] = session["first_name"]
    myresult['last_name'] = session["last_name"]
    myresult['tv_shows'] = TVShow.query.all()
    return render_template('shows.html', result=myresult)

@app.route('/shows/delete/<int:id>', methods=['POST'])
def delete_item(id):
    myshow = TVShow.query.filter_by(id=id).first_or_404()
    db.session.delete(myshow)
    db.session.commit()
    myresult = {'id': '', 'first_name': '', 'last_name': '', 'email': '', 'password': '', 'confirm_password': '', 'tv_shows': None}
    myresult['email'] = session["email"]
    # myresult['password'] = session["password"]
    myresult['first_name'] = session["first_name"]
    myresult['last_name'] = session["last_name"]
    myresult['tv_shows'] = TVShow.query.all()
    return render_template('shows.html', result=myresult)

@app.route('/login',methods=['POST'])
def login_post():
    email = request.form['email']
    password = request.form['password']
    myresult = {'first_name': '', 'last_name': '', 'email': '', 'password': '', 'confirm_password': '', 'tv_shows': None}
    #Set myresult
    myresult['email'] = email
    # myresult['password'] = password
    #
    if ((email == '') or (password == '')):
        return redirect('/')
    else:
        user = User.query.filter_by(email=email).first()
        if (user):
            if (user.password != password):
                flash('Password is incorrect!')
                return redirect('/')
            else:
                myresult['first_name'] = user.first_name
                myresult['last_name'] = user.last_name
                myresult['email'] = email
                login_user(user)
                session['email'] = email
                session['first_name'] = user.first_name
                session['last_name'] = user.last_name
                # Get user's data
                myresult["tv_shows"] = TVShow.query.all()
                return render_template('shows.html', result=myresult)
                # return redirect('/shows', result=email)
        else:
            flash('Email is not existed!')
            return redirect('/')

@app.route('/signup',methods=['POST'])
def signup_post():
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    email = request.form['email']
    password = request.form['password']
    confirm_password = request.form['confirm_password']
    myresult = {'first_name': '', 'last_name': '', 'email': '', 'password': '', 'confirm_password': '', 'tv_shows': None}
    #Set myresult
    myresult['first_name'] = first_name
    myresult['last_name'] = last_name
    myresult['email'] = email
    # myresult['password'] = password
    # myresult['confirm_password'] = confirm_password

    #
    if ((first_name == '') or (last_name == '') or (email == '') or (password == '') or (confirm_password == '')):
        flash('All fields must be required')
        return redirect('/')
    elif ((len(first_name) < 2) or  (len(last_name) < 2)):
        flash('First name and Last name must be at least 2 characters')
        return redirect('/')
    elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
        flash("Invalid email address!", "danger")
        return redirect('/')
    elif not re.match(r'[A-Za-z0-9]+', first_name):
        flash("Username must contain only characters and numbers!", "danger")
        return redirect('/')
    elif not re.match(r'[A-Za-z0-9]+', last_name):
        flash("Username must contain only characters and numbers!", "danger")
        return redirect('/')
    if (password !=  confirm_password):
        flash('Confirm Password is incorrect!')
        return redirect('/')
    else:       
        user = User(first_name=first_name,last_name=last_name,email=email,password=password)
        db.session.add(user)
        db.session.commit()
        session['email'] = email
        session['first_name'] = first_name
        session['last_name'] = last_name
        login_user(user)
        myresult = {'first_name': '', 'last_name': '', 'email': '', 'password': '', 'confirm_password': '', 'tv_shows': None}
        myresult['email'] = email
        # myresult['password'] = session["password"]
        myresult['first_name'] = first_name
        myresult['last_name'] = last_name
        myresult['tv_shows'] = TVShow.query.all()
        return render_template('shows.html', result=myresult)

@app.route('/logout',methods=['GET'])
def logout():
    logout_user()
    session['email'] = ''
    session['first_name'] = ''
    session['last_name'] = ''
    return redirect('/')


if __name__=='__main__':
    app.run(debug=True)