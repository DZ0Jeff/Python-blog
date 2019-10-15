from flask import Flask, render_template, flash, redirect, url_for, logging, session, request
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from data import Articles

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


    class RegisterForm(Form):
        name = StringField('Name', [validators.Length(min=1, max=50)])
        username = StringField('Username', [validators.Length(min=4, max=25)])
        email = StringField('Email', [validators.Length(min=6, max=50)])
        password = PasswordField('Password', [
            validators.DataRequired(),
            validators.EqualTo('confirm', message='Password does not match')
        ])
        confirm = PasswordField('Confirm password')


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
