from flask import Flask, render_template, flash, redirect, url_for, logging, session, request
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from data import Articles
from classes import RegisterForm


data = Articles()

def router(app, database):
    @app.route('/')
    def index():
        return render_template('home.html')


    @app.route('/about')
    def about():
        return render_template('about.html')


    @app.route('/articles')
    def articles():
        return render_template('articles.html', articles = data)


    @app.route('/article/<string:id>/')
    def article(id):
        return render_template('article.html', id=id)


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
                passoword = data['password']

                #compare password
                if sha256_crypt.verify(password_candidate, passoword):
                    app.logger.info('PASSWORD MATCHED')
                else:
                    app.logger.info('PASSWORD DONT MATCH!')

            else:
                app.logger.info('NO USER')

        return render_template('login.html')

        
