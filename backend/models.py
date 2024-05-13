from database import setup_db

# models will contain main CRUD functions
# it will define all queries needed for this project

#LIST OF ALL QUERY METHODS:

#Check if user is in system
#return true or false, so we can run next query if needed
def check_user_exists_db(user_id):
    connection = setup_db()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT SpotifyUserID FROM Users WHERE SpotifyUserID = %s", (user_id,))
            return cursor.fetchone() is not None
    finally:
        connection.close()


#Insert new user into db
def insert_new_user_db(user_id):
    connection = setup_db()
    try:
        with connection.cursor() as cursor:
            cursor.execute("INSERT INTO Users (SpotifyUserID) VALUES (%s)", (user_id,))
            connection.commit()
            return True
    except Exception as e:
        print(f"Error inserting new user: {e}")
        return False
    finally:
        connection.close()

# Get all pins related to a user
def fetch_user_pins_from_db(user_id):
    connection = setup_db()
    try:
        with connection.cursor(dictionary=True) as cursor:
            sql = """
            SELECT * FROM Pin WHERE user_id = %s
            """
            cursor.execute(sql, (user_id,))
            return cursor.fetchall()  # Return a list of pin dictionaries
        
    except Exception as e:
        print(f"Error fetching pins: {e}")
        return None
    finally:
        connection.close()

#add a pin in db
#returns ID of created pin
def add_pin_in_db(user_id, pin_data):
    connection = setup_db()

    try:
        with connection.cursor() as cursor:
            sql = """
            INSERT INTO Pin (user_id, name, latitude, longitude, radius, uri)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (user_id, pin_data['name'], pin_data['lat'], pin_data['lng'], pin_data['radius'], pin_data['uri']))
            connection.commit()

            #debug this
            print ("cursor.lastrowid = ", cursor.lastrowid)
            
            return cursor.lastrowid  #return id of pin
        
    except Exception as e:
        print(f"Error adding pin: {e}")
        return None 
    finally:
        connection.close()


#update all pin in db
#returns true if updated
def update_pin_in_db(user_id, pin_id, pin_data):
    connection = setup_db()
    try:
        with connection.cursor() as cursor:
            sql = """
            UPDATE Pin SET name = %s, latitude = %s, longitude = %s, radius = %s, uri = %s
            WHERE pin_id = %s
            """
            cursor.execute(sql, (pin_data['name'], pin_data['lat'], pin_data['lng'], pin_data['radius'], pin_data['uri'], pin_id))
            connection.commit()
            print("executed query")
            print(user_id)
            print(pin_id)
            print(pin_data['lat'])
            print(pin_data['lng'])
            print(pin_data['radius'])
            print(pin_data['name'])
            print(pin_data['uri'])
            return cursor.rowcount > 0  # Returns True if there are rows updated
            
    except Exception as e:
        print(f"Error updating pin: {e}")
        return False
    finally:
        connection.close()


# delete pin from db
def delete_pin_from_db(user_id, pin_id):
    connection = setup_db()
    try:
        with connection.cursor() as cursor:
            sql = "DELETE FROM Pin WHERE pin_id = %s AND user_id = %s"
            cursor.execute(sql, (pin_id, user_id))
            connection.commit()
            return cursor.rowcount > 0  # Return True if any rows were deleted
    except Exception as e:
        print(f"Error deleting pin: {e}")
        return False
    finally:
        connection.close()



