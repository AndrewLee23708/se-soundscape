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
            WHERE pin_id = %s AND user_id = %s
            """
            cursor.execute(sql, (pin_data['name'], pin_data['lat'], pin_data['lng'], pin_data['radius'], pin_data['uri'], pin_id, user_id))
            connection.commit()
            print("executed query")
            print(user_id)
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






















# '''

# Original Queries with Only Scapes 

# '''

# ### User queries

# #simple get list of all users
# def get_all_users():
#     connection = setup_db()
#     cursor = connection.cursor(dictionary=True)
#     cursor.execute("SELECT * FROM users")
#     users = cursor.fetchall()
#     cursor.close()
#     connection.close()
#     return users

# # fetches the Spotify access token for a given user ID from the database
# def get_user_spotify_token(user_id):
#     connection = setup_db()
#     cursor = connection.cursor(dictionary=True)
#     cursor.execute("SELECT Access_Token FROM Users WHERE SpotifyUserID = %s", (user_id))
#     result = cursor.fetchone()
#     cursor.close()
#     connection.close()
#     return result['Access_Token'] if result else None


# #add new user
# def add_new_user(SpotifyUserID, Access_Token):
#     connection = setup_db()
#     cursor = connection.cursor()
#     cursor.execute("INSERT INTO users (SpotifyUserID, Access Token) VALUES (%s, %s)", (SpotifyUserID, Access_Token))    #parameterized queries to prevent injections?
#     connection.commit()
#     user_id = cursor.lastrowid    #most recent
#     cursor.close()
#     connection.close()
#     return user_id

# #delete user
# def delete_user(spotify_user_id):
#     connection = setup_db()
#     cursor = connection.cursor()
#     cursor.execute("DELETE FROM Users WHERE SpotifyUserID = %s", (spotify_user_id,))
#     connection.commit()
#     deleted_rows = cursor.rowcount
#     cursor.close()
#     connection.close()
#     return deleted_rows     #return number of deleted rows

# #update user
# def update_user_access_token(spotify_user_id, access_token):

#     connection = setup_db()
#     cursor = connection.cursor()
#     cursor.execute("""
#         UPDATE Users 
#         SET Access_Token = %s 
#         WHERE SpotifyUserID = %s
#         """, (access_token, spotify_user_id))
#     connection.commit()
#     updated_rows = cursor.rowcount
#     cursor.close()
#     connection.close()
#     return updated_rows


# ### Scape Related Queries

# #fetch all profiles of a user
# def get_all_scapes_for_user(user_id):
#     connection = setup_db()
#     cursor = connection.cursor(dictionary=True)
#     cursor.execute("SELECT * FROM Scape WHERE UserID = %s", (user_id,))
#     scapes = cursor.fetchall()
#     cursor.close()
#     connection.close()
#     return scapes

# def add_new_scape(user_id, scape_name, visibility_status, shareable_link):
#     connection = setup_db()
#     cursor = connection.cursor()
#     cursor.execute("""
#         INSERT INTO Scape (UserID, ScapeName, VisibilityStatus, ShareableLink, DateCreated) 
#         VALUES (%s, %s, %s, %s, NOW())
#         """, (user_id, scape_name, visibility_status, shareable_link))
#     connection.commit()
#     scape_id = cursor.lastrowid
#     cursor.close()
#     connection.close()
#     return scape_id

# # Updates an existing scape, share through links first 
# def update_scape(scape_id, scape_name, visibility_status, shareable_link):
#     connection = setup_db()
#     cursor = connection.cursor()
#     cursor.execute("""
#         UPDATE Scape 
#         SET ScapeName = %s, VisibilityStatus = %s, ShareableLink = %s 
#         WHERE Scape_ID = %s
#         """, (scape_name, visibility_status, shareable_link, scape_id))
#     connection.commit()
#     updated_rows = cursor.rowcount
#     cursor.close()
#     connection.close()
#     return updated_rows        #returns the number of affected rows.
 
# #delete a Scape
# def delete_scape(scape_id):
#     connection = setup_db()
#     cursor = connection.cursor()
#     cursor.execute("DELETE FROM Scape WHERE Scape_ID = %s", (scape_id,))
#     connection.commit()
#     deleted_rows = cursor.rowcount
#     cursor.close()
#     connection.close()
#     return deleted_rows         #returns the number of affected rows.



# ### Pin related queries      ## location is a string variable with name of place.

# # Load all pins for a specific scape, allows us to load all pins available on map 
# # Returns a table of pins and their info
# # Decision to load only initial pin attributes initially, may change later on
# def get_pins_by_scape(scape_id):
#     connection = setup_db()
#     cursor = connection.cursor(dictionary=True)
#     cursor.execute("""
#         SELECT Pin_ID, Latitude, Longitude 
#         FROM Pin 
#         INNER JOIN Scape ON Pin.ScapeID = Scape.Scape_ID 
#         WHERE Scape.Scape_ID = %s""", (scape_id,))
#     pins = cursor.fetchall()
#     cursor.close()
#     connection.close()
#     return pins     

# # Load pin detail (when user selects a pin)
# # when users select pin, this shows up
# def get_pin_details(pin_id):
#     connection = setup_db()
#     cursor = connection.cursor(dictionary=True)
#     cursor.execute("""
#         SELECT * 
#         FROM Pin 
#         WHERE Pin_ID = %s
#         """, (pin_id,))
#     pin_details = cursor.fetchone()
#     cursor.close()
#     connection.close()
#     return pin_details



# #Add pins
# def pin_add(ScapeID, Location, Latitude, Longitude, Radius, Priority, PlaylistID, DateCreated):
#     connection = setup_db()
#     cursor = connection.cursor()
#     cursor.execute(""" INSERT INTO Pin (ScapeID, Location, Latitude, Longitude, Radius, Priority, PlaylistID, DateCreated)         
#         VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""", 
#         (ScapeID, Location, Latitude, Longitude, Radius, Priority, PlaylistID, DateCreated))                   #note, careful not to change pin_id (AUTO INCREMENT)
#     connection.commit()
#     pin_id = cursor.lastrowid  # Corrected variable name to reflect that it's the ID of the pin
#     cursor.close()
#     connection.close()
#     return pin_id  # Return the ID of the newly added pin

# # Update an existing pin
# def update_pin(Pin_ID, ScapeID, Location, Latitude, Longitude, Radius, Priority, PlaylistID):
#     connection = setup_db()
#     cursor = connection.cursor()
#     cursor.execute("""
#         UPDATE Pin 
#         SET ScapeID = %s, Location = %s, Latitude = %s, Longitude = %s, Radius = %s, Priority = %s, PlaylistID = %s 
#         WHERE Pin_ID = %s """, 
#         (ScapeID, Location, Latitude, Longitude, Radius, Priority, PlaylistID, Pin_ID))
#     connection.commit()
#     updated_rows = cursor.rowcount
#     cursor.close()
#     connection.close()
#     return updated_rows

# # Delete a pin
# def delete_pin(Pin_ID):
#     connection = setup_db()
#     cursor = connection.cursor()
#     cursor.execute("DELETE FROM Pin WHERE Pin_ID = %s", (Pin_ID))
#     connection.commit()
#     deleted_rows = cursor.rowcount
#     cursor.close()
#     connection.close()
#     return deleted_rows






## Check later

# def add_pin_to_db(user_id, scape_id, location, latitude, longitude, radius, priority, playlist_id, date_created):
#     connection = setup_db()
#     try:
#         with connection.cursor() as cursor:
#             sql = """
#             INSERT INTO Pin (user_id, scape_id, location, latitude, longitude, radius, priority, playlist_id, date_created)
#             VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
#             """
#             cursor.execute(sql, (user_id, scape_id, location, latitude, longitude, radius, priority, playlist_id, date_created))
#             connection.commit()
#             return cursor.lastrowid  # Return the new pin ID generated by the database
#     except Exception as e:
#         print(f"Error adding pin: {e}")
#         return None
#     finally:
#         connection.close()

# def update_pin_in_db(pin_id, scape_id, location, latitude, longitude, radius, priority, playlist_id):
#     connection = setup_db()
#     try:
#         with connection.cursor() as cursor:
#             sql = """
#             UPDATE Pin SET scape_id = %s, location = %s, latitude = %s, longitude = %s, radius = %s, priority = %s, playlist_id = %s
#             WHERE pin_id = %s
#             """
#             cursor.execute(sql, (scape_id, location, latitude, longitude, radius, priority, playlist_id, pin_id))
#             connection.commit()
#             return cursor.rowcount > 0  # Return True if any rows were updated
#     except Exception as e:
#         print(f"Error updating pin: {e}")
#         return False
#     finally:
#         connection.close()