from database import get_db_connection

#simple get all users
def get_all_users():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    cursor.close()
    connection.close()
    return users

def add_new_user(SpotifyUserID, Access_Token):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("INSERT INTO users (SpotifyUserID, Access Token) VALUES (%s, %s)", (SpotifyUserID, Access_Token))
    connection.commit()
    user_id = cursor.lastrowid
    cursor.close()
    connection.close()
    return user_id


