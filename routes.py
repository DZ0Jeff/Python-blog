from flask import Flask, render_template, flash, redirect, url_for, logging, session, request
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from data import Articles
from classes import RegisterForm
from functools import wraps


data = Articles()

def router(app, database):
    #index
    @app.route('/')
    def index():
        return render_template('home.html')

    #about
    @app.route('/about')
    def about():
        return render_template('about.html')


    #list of articles
    @app.route('/articles')
    def articles():
        return render_template('articles.html', articles = data)

    #article
    @app.route('/article/<string:id>/')
    def article(id):
        return render_template('article.html', id=id)
    
    # Check if user logged in
    def is_logged_in(f):
        @wraps(f)
        def wrap(*args, **kwargs):
            if 'logged_in' in session:
                return f(*args, **kwargs)
            else:
                flash('Unauthorized, Please login', 'danger')
                return redirect(url_for('login'))
        return wrap

    #register
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        form = RegisterForm(request.form)
        if request.method == 'POST' and form.validate():
            name = form.name.data
            email = form.email.data
            username = form.username.data
            password = sha256_crypt.encrypt(str(form.password.data))

            connection = database.connect()
            cursor = connection.cursor()
            cursor.execute("INSERT INTO users(name, email, username, password) VALUES (%s,%s,%s,%s)",(name, email, username, password))

            #commit do DB
            connection.commit()

            cursor.close()

            flash('You are registered and can log in, Success :)')

            return redirect(url_for('index'))
        
        return render_template('register.html', form=form)

    #login
    @app.route('/login', methods=['GET','POST'])
    def login():
        if request.method == 'POST':
            # get HTML fields
            username = request.form['username']
            password_candidate = request.form['password']
        
            #Cursor
            
            connection = database.connect()
            cursor = connection.cursor()
            #cursor = database.connect().cursor()
            result = cursor.execute("SELECT * FROM users WHERE username = %s", [username])

            if result > 0:
                data = cursor.fetchone()
                passoword = data[4]

                #compare password
                if sha256_crypt.verify(password_candidate, passoword):
                    #passed
                    session['logged_in'] = True
                    session['username'] = username

                    flash('You are now logged in', 'Sucess :)')
                    return redirect(url_for('dashboard'))

                else:
                    #password dint match
                    error = 'invalid login'
                    return render_template('login.html', error=error)
                cursor.close()

            else:
                # erro or null
                error = 'Username or password not found'
                return render_template('login.html', error=error)

        return render_template('login.html')


    #dashboard
    @app.route('/dashboard')
    @is_logged_in
    def dashboard():
        return render_template('dashboard.html')   

    #logout
    @app.route('/logout')
    def logout():
        session.clear()
        flash('You are now logged out')
        return redirect(url_for('login'))
