import mysql.connector

def setup_db():
    connection = mysql.connector.connect(host="localhost", port="3306", 
                            user = "root", password ="",
                            database = "soundscape")
    return connection

#side note: may have to configure mySQL config 'wait_timeout' as well






















