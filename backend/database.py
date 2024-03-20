from flask_mysqldb import MySQL

mysql = MySQL()

def setup_db(app):
    app.config['MYSQL_HOST'] = 'localhost'     #change if we move to remote server
    app.config['MYSQL_USER'] = 'root'
    app.config['MYSQL_PASSWORD'] = ''
    app.config['MYSQL_DB'] = 'soundscape'
    mysql.init_app(app)