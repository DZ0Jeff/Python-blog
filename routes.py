from flask import Flask, render_template, flash, redirect, url_for, logging, session, request
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from data import Articles
from classes import RegisterForm, ArticleForm
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
        #create a cursor
        connection = database.connect()
        cursor = connection.cursor()

        #Get results
        result = cursor.execute("SELECT * FROM articles")

        articles = cursor.fetchall()
        #articles = dict((key, value) for key, value in articles)

        if result > 0:
            return render_template('articles.html', articles=articles)

        else:
            msg = 'No articles Found'
            return render_template('articles.html', msg=msg)
        
        #close connection
        cursor.close()


    #article
    @app.route('/article/<string:id>/')
    def article(id):
        connection = database.connect()
        cursor = connection.cursor()

        #Get results
        result = cursor.execute("SELECT * FROM articles WHERE id = %s", [id])

        articles = cursor.fetchall()

        for article in articles:
            print(article)

        return render_template('article.html', article=article)
    
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
        #create a cursor
        connection = database.connect()
        cursor = connection.cursor()

        #Get results
        result = cursor.execute("SELECT * FROM articles")

        articles = cursor.fetchall()

        if result > 0:
            return render_template('dashboard.html', articles=articles)

        else:
            msg = 'No articles Found'
            return render_template('dashboard.html', msg=msg)
        
        #close connection
        cursor.close()


    #dashboard
    @app.route('/add_article', methods=['GET', 'POST'])
    @is_logged_in
    def add_article():
        form = ArticleForm(request.form)
        if request.method == 'POST' and form.validate():
            title = form.title.data
            body = form.body.data  

            #create handler
            connection = database.connect()
            cursor = connection.cursor()

            #execute
            cursor.execute("INSERT INTO articles(title, body, author) VALUES(%s, %s, %s)",(title, body, session['username']))
            
            #commit 
            connection.commit()

            #close
            cursor.close()

            flash('Article created','Sucess')

            return redirect(url_for('dashboard'))
        
        else: 
            print('Error!')

        return render_template('add_article.html', form=form)
    
    
    @app.route('/edit_article/<string:id>', methods=['GET', 'POST'])
    @is_logged_in
    def edit_article(id):
        #create cursor
        connection = database.connect()
        cursor = connection.cursor()

        #get article by id
        result = cursor.execute("SELECT * FROM articles WHERE id = %s", [id])
        article = cursor.fetchall()

        #get form
        form = ArticleForm(request.form)

        #populate the form
        for datas in article:
            form.title.data = datas[1]
            form.body.data = datas[2]


        if request.method == 'POST' and form.validate():
            title = request.form['title']
            body = request.form['body']  

            #create handler
            connection = database.connect()
            cursor = connection.cursor()

            #execute
            cursor.execute("UPDATE articles SET title=%s, body=%s WHERE id = %s", (title, body, id))
            
            #commit 
            connection.commit()

            #close
            cursor.close()

            flash('Article Updated','Sucess')

            return redirect(url_for('dashboard'))
        
        else: 
            print('Error!')

        return render_template('edit_article.html', form=form)
    
    @app.route('/delete_article/<string:id>', methods=['POST'])
    @is_logged_in
    def delete_article(id):
        connection = database.connect()
        cursor = connection.cursor()

        #delete
        cursor.execute("DELETE FROM articles WHERE id = %s", [id])

        #commit 
        connection.commit()

        #close
        cursor.close()

        flash('Article Deleted','Sucess')

        return redirect(url_for('dashboard'))

    #logout
    @app.route('/logout')
    @is_logged_in
    def logout():
        session.clear()
        flash('You are now logged out')
        return redirect(url_for('login'))
