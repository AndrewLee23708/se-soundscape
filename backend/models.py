from database import setup_db

# models will contain main CRUD functions
# it will define all queries needed for this project

#LIST OF ALL QUERY METHODS:



### User queries

#simple get list of all users
def get_all_users():
    connection = setup_db()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    cursor.close()
    connection.close()
    return users

# fetches the Spotify access token for a given user ID from the database
def get_user_spotify_token(user_id):
    connection = setup_db()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT Access_Token FROM Users WHERE SpotifyUserID = %s", (user_id))
    result = cursor.fetchone()
    cursor.close()
    connection.close()
    return result['Access_Token'] if result else None


#add new user
def add_new_user(SpotifyUserID, Access_Token):
    connection = setup_db()
    cursor = connection.cursor()
    cursor.execute("INSERT INTO users (SpotifyUserID, Access Token) VALUES (%s, %s)", (SpotifyUserID, Access_Token))    #parameterized queries to prevent injections?
    connection.commit()
    user_id = cursor.lastrowid    #most recent
    cursor.close()
    connection.close()
    return user_id

#delete user
def delete_user(spotify_user_id):
    connection = setup_db()
    cursor = connection.cursor()
    cursor.execute("DELETE FROM Users WHERE SpotifyUserID = %s", (spotify_user_id,))
    connection.commit()
    deleted_rows = cursor.rowcount
    cursor.close()
    connection.close()
    return deleted_rows     #return number of deleted rows

#update user
def update_user_access_token(spotify_user_id, access_token):
    """
    Updates an existing user's access token and returns the number of affected rows.
    """
    connection = setup_db()
    cursor = connection.cursor()
    cursor.execute("""
        UPDATE Users 
        SET Access_Token = %s 
        WHERE SpotifyUserID = %s
        """, (access_token, spotify_user_id))
    connection.commit()
    updated_rows = cursor.rowcount
    cursor.close()
    connection.close()
    return updated_rows


### Scape Related Queries

#fetch all profiles of a user
def get_all_scapes_for_user(user_id):
    connection = setup_db()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Scape WHERE UserID = %s", (user_id,))
    scapes = cursor.fetchall()
    cursor.close()
    connection.close()
    return scapes

def add_new_scape(user_id, scape_name, visibility_status, shareable_link):
    connection = setup_db()
    cursor = connection.cursor()
    cursor.execute("""
        INSERT INTO Scape (UserID, ScapeName, VisibilityStatus, ShareableLink, DateCreated) 
        VALUES (%s, %s, %s, %s, NOW())
        """, (user_id, scape_name, visibility_status, shareable_link))
    connection.commit()
    scape_id = cursor.lastrowid
    cursor.close()
    connection.close()
    return scape_id

# Updates an existing scape, share through links first 
def update_scape(scape_id, scape_name, visibility_status, shareable_link):
    connection = setup_db()
    cursor = connection.cursor()
    cursor.execute("""
        UPDATE Scape 
        SET ScapeName = %s, VisibilityStatus = %s, ShareableLink = %s 
        WHERE Scape_ID = %s
        """, (scape_name, visibility_status, shareable_link, scape_id))
    connection.commit()
    updated_rows = cursor.rowcount
    cursor.close()
    connection.close()
    return updated_rows        #returns the number of affected rows.
 
#delete a Scape
def delete_scape(scape_id):
    connection = setup_db()
    cursor = connection.cursor()
    cursor.execute("DELETE FROM Scape WHERE Scape_ID = %s", (scape_id,))
    connection.commit()
    deleted_rows = cursor.rowcount
    cursor.close()
    connection.close()
    return deleted_rows         #returns the number of affected rows.



### Pin related queries      ## location is a string variable with name of place.

# Load all pins for a specific profile (scape), allows us to load all pins available on map 
# Returns a table of pins and their info
# Decision to load only initial pin attributes initially, may change later on
def get_pins_by_profile(scape_id):
    connection = setup_db()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("""
        SELECT Pin_ID, Latitude, Longitude 
        FROM Pin 
        INNER JOIN Scape ON Pin.ScapeID = Scape.Scape_ID 
        WHERE Scape.Scape_ID = %s""", (scape_id,))
    pins = cursor.fetchall()
    cursor.close()
    connection.close()
    return pins     

# Load pin detail (when user selects a pin)
# when users select pin, this shows up
def get_pin_details(pin_id):
    connection = setup_db()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("""
        SELECT * 
        FROM Pin 
        WHERE Pin_ID = %s
        """, (pin_id,))
    pin_details = cursor.fetchone()
    cursor.close()
    connection.close()
    return pin_details

#Add pins
def pin_add(ScapeID, Location, Latitude, Longitude, Radius, Priority, PlaylistID, DateCreated):
    connection = setup_db()
    cursor = connection.cursor()
    cursor.execute(""" INSERT INTO Pin (ScapeID, Location, Latitude, Longitude, Radius, Priority, PlaylistID, DateCreated)         
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""", 
        (ScapeID, Location, Latitude, Longitude, Radius, Priority, PlaylistID, DateCreated))                   #note, careful not to change pin_id (AUTO INCREMENT)
    connection.commit()
    pin_id = cursor.lastrowid  # Corrected variable name to reflect that it's the ID of the pin
    cursor.close()
    connection.close()
    return pin_id  # Return the ID of the newly added pin

# Update an existing pin
def update_pin(Pin_ID, ScapeID, Location, Latitude, Longitude, Radius, Priority, PlaylistID):
    connection = setup_db()
    cursor = connection.cursor()
    cursor.execute("""
        UPDATE Pin 
        SET ScapeID = %s, Location = %s, Latitude = %s, Longitude = %s, Radius = %s, Priority = %s, PlaylistID = %s 
        WHERE Pin_ID = %s """, 
        (ScapeID, Location, Latitude, Longitude, Radius, Priority, PlaylistID, Pin_ID))
    connection.commit()
    updated_rows = cursor.rowcount
    cursor.close()
    connection.close()
    return updated_rows

# Delete a pin
def delete_pin(Pin_ID):
    connection = setup_db()
    cursor = connection.cursor()
    cursor.execute("DELETE FROM Pin WHERE Pin_ID = %s", (Pin_ID))
    connection.commit()
    deleted_rows = cursor.rowcount
    cursor.close()
    connection.close()
    return deleted_rows