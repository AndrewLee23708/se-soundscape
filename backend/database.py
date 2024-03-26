import mysql.connector

def setup_db():
    connection = mysql.connector.connect(host="localhost", port="3306", 
                            user = "root", password ="",
                            database = "soundscape")
    return connection

#side note: may have to configure mySQL config 'wait_timeout' as well




### Below is test of db connection
#
# Let's do a quick test to see if database is connecting

# conn = setup_db()        # first create connection object
# cursor = conn.cursor()   # Create cursor object to read/write

# selectquery = "SELECT * FROM Users"    # interact with database
# cursor.execute(selectquery)            # execture  
# records=cursor.fetchall()
# print("No. of registered users in the Scapes", cursor.rowcount)

# for row in records:                    #records are returned in form of table
#     print("spotify id: ", row[0])
#     print("access token: ", row[1])
#     print()

# cursor.close()
# conn.close()

#Data base connect success!!

#Helpful links:
# https://www.youtube.com/watch?v=_fu2z-6SbSU