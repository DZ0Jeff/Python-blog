from flask import Flask
from routes import router
from flaskext.mysql import MySQL


app = Flask(__name__)
app.secret_key="ejdpweajd"

#database
mysql = MySQL()

app.config['MYSQL_DATABASE_HOST'] = "localhost"
app.config['MYSQL_DATABASE_PORT'] = 3306
app.config['MYSQL_DATABASE_USER'] = "root"
app.config['MYSQL_DATABASE_PASSWORD'] = ""
app.config['MYSQL_DATABASE_DB'] = "blogx"

mysql.init_app(app)

#Routes
router(app, mysql)

if __name__ == "__main__":
    app.run(debug=True)