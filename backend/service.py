from dotenv import load_dotenv
import base64  #encode auth_string using base64
from requests import post
import json
import models
from database import setup_db

#Service layer connects app.py to models.py, does exceptional handling and apply other business rules.
# First work with intial DB without scapes 

############

"""Fetches all pins associated with a given user ID."""

############


### check/validate if user in db, if not, save to user to db
def save_user(user_id):
    if not user_id:
        return {"error": "Invalid user ID provided", "success": False}
    
    # Check if the user exists
    if models.check_user_exists_db(user_id):
        return {"message": "User already exists", "success": True}
    
    # Insert new user if not present
    if models.insert_new_user_db(user_id):
        return {"message": "User added successfully", "success": True}
    else:
        return {"error": "Failed to add user", "success": False}


### save pin for user
def get_pins_for_user(user_id):
    if not user_id:
        return {"error": "Invalid user ID provided", "success": False}
    
    pins = models.fetch_user_pins_from_db(user_id)
    if pins is not None:
        return {"pins": pins, "success": True}
    else:
        return {"error": "Failed to fetch pins", "success": False}
    

###  add a new pin for user
def add_pin_for_user(user_id, pin_data):
    # Make sure values exist
    required_fields = ['name', 'lat', 'lng', 'radius', 'uri']
    if not all(pin_data.get(field) for field in required_fields):
        return {"error": "Missing required pin data"}

    try:
        latitude = float(pin_data['lat'])
        longitude = float(pin_data['lng'])
        radius = float(pin_data['radius'])

        if not (-90 <= latitude <= 90):
            return {"error": "Latitude out of range"}
        if not (-180 <= longitude <= 180):
            return {"error": "Longitude out of range"}
        if radius < 0:
            return {"error": "Radius must be non-negative"}
        
    except ValueError:
        return {"error": "Latitude, longitude, and radius must be valid numbers"}
    
    # Run model query
    pin_id = models.add_pin_in_db(user_id, pin_data)
    print(pin_id)

    if not pin_id:
        return {"error": "Failed to add pin", "success": False}



### update pins for users
def update_pin(user_id, pin_id, pin_data):
    print(user_id)
    print(pin_data['lat'])
    print(pin_data['lng'])
    print(pin_data['radius'])
    print(pin_data['name'])
    print(pin_data['uri'])

    '''
    # Data validation could go here
    if not all([user_id, pin_id, pin_data.get('name'), pin_data.get('lat'), pin_data.get('lng'), pin_data.get('radius'), pin_data.get('uri')]):
        return {"error": "Invalid data provided", "success": False}
    '''
    
    try:
        if not (-90 <= float(pin_data['lat']) <= 90) or not (-180 <= float(pin_data['lng']) <= 180):
            return {"error": "Latitude or longitude out of range", "success": False}
        if float(pin_data['radius']) < 0:
            return {"error": "Radius must be non-negative", "success": False}
    except ValueError:
        return {"error": "Latitude, longitude, and radius must be valid numbers", "success": False}

    print('going to models')
    # Update the pin in the database
    if models.update_pin_in_db(user_id, pin_id, pin_data):
        return {"message": "Pin updated successfully", "success": True}
    else:
        return {"error": "Failed to update pin", "success": False}



### delete pins
def delete_pin(user_id, pin_id):
    if not user_id or not pin_id:
        return {"error": "Missing user ID or pin ID", "success": False}
    
    if models.delete_pin_from_db(user_id, pin_id):
        return {"message": "Pin deleted successfully", "success": True}
    else:
        return {"error": "Failed to delete pin", "success": False}














# ############################################################

# '''
# Functions to implement once we incorporate scapes
# '''

# ############################################################

# ##### Scape Related Functions
# ### We use get_token() function to validate user authentication

# #Retrieves all scapes for a specific user after validating their authentication.
# def service_get_all_scapes_for_user(user_id):

#     if user_id and isinstance(user_id, int):  # Basic check to ensure user_id is valid
#         return get_all_scapes_for_user(user_id)
#     else:
#         return {"error": "Invalid User ID"}

# #Adds a new scape after validating user's access token and checking inputs.
# def service_add_new_scape(user_id, scape_name, visibility_status, shareable_link):

#     access_token = get_user_spotify_token(user_id)
#     if not access_token:
#         return {"error": "Authentication required"}

#     if isinstance(scape_name, str) and scape_name.strip() and isinstance(visibility_status, str) and isinstance(shareable_link, str):
#         return models.add_new_scape(user_id, scape_name, visibility_status, shareable_link)
#     else:
#         return {"error": "Invalid input data"}

# #Updates an existing scape only if the user is authenticated and owns the scape.
# def service_update_scape(user_id, scape_id, scape_name, visibility_status, shareable_link):
    
#     access_token = get_user_spotify_token(user_id)
#     if not access_token:
#         return {"error": "Authentication required"}

#     if all([isinstance(scape_id, int), isinstance(scape_name, str) and scape_name.strip(),
#             isinstance(visibility_status, str), isinstance(shareable_link, str)]):
#         return models.update_scape(scape_id, scape_name, visibility_status, shareable_link)
#     else:
#         return {"error": "Invalid data provided for update"}

# # Deletes a scape after validating that the user is authenticated and owns the scape.
# def service_delete_scape(user_id, scape_id):

#     access_token = get_user_spotify_token(user_id)
#     if not access_token:
#         return {"error": "Authentication required"}

#     if isinstance(scape_id, int):
#         return models.delete_scape(scape_id)
#     else:
#         return {"error": "Invalid Scape ID for deletion"}


# ##### Pin functions: Users have choosen a scape at this point and can manipulate pins

# # Fetch pins based on scape_id
# def service_get_pins_by_scape(scape_id):
#     # Add business rule before fetching pins

#     if scape_id and isinstance(scape_id, int):  # Basic validation example
#         return models.get_pins_by_scape(scape_id)
#     else:
#         return {"error": "Invalid Scape ID"}


# ### Users and outsiders can look at pin details for now, will be updated later on
# def service_get_pin_details(pin_id):
#     # business rules to be implemented before fetching pins

#     if pin_id and isinstance(pin_id, int):
#         return models.get_pin_details(pin_id)
#     else:
#         return {"error": "Invalid Pin ID"}


# ### Editing pins: Business Logic + authenticate user_id for each of these function
# # add pin
# def service_add_pin(user_id, scape_id, location, latitude, longitude, radius, priority, playlist_id, date_created):
   
#     # authentication (once sharing is created)

#     # business rules: check if the pin data is valid
#     if not location.strip():  # Ensure location is not empty or whitespace
#         return {"error": "Invalid location"}
#     if not (-90 <= latitude <= 90):
#         return {"error": "Latitude out of range"}
#     if not (-180 <= longitude <= 180):
#         return {"error": "Longitude out of range"}
#     if radius < 0:
#         return {"error": "Radius must be non-negative"}
#     if priority < 0:
#         return {"error": "Priority must be non-negative"}
#     if not isinstance(playlist_id, int) or playlist_id < 1:  # Assuming playlist_id should be a positive integer
#         return {"error": "Invalid playlist ID"}

#     #Check variable types
#     if all([isinstance(scape_id, int), location, isinstance(latitude, (int, float)), 
#             isinstance(longitude, (int, float)), isinstance(radius, (int, float)), 
#             isinstance(priority, int), playlist_id]):
#         return models.pin_add(scape_id, location, latitude, longitude, radius, priority, playlist_id, date_created)
#     else:
#         return {"error": "Invalid pin data"}

# # update pins
# def service_update_pin(user_id, pin_id, scape_id, location, latitude, longitude, radius, priority, playlist_id):
    
#     # Authentication (once sharing is created)
    
#     # Business rules and data validation
#     if not all([isinstance(pin_id, int), isinstance(scape_id, int), location.strip(),
#                  -90 <= latitude <= 90, -180 <= longitude <= 180, radius >= 0, priority >= 0, isinstance(playlist_id, int) and playlist_id > 0]):
#         return {"error": "Invalid data provided for update"}
    
#     return models.update_pin(pin_id, scape_id, location, latitude, longitude, radius, priority, playlist_id)


# # delete pins
# def service_delete_pin(user_id, pin_id):
    
#     # Authentication (once sharing is created)

#     if not access_token or not isinstance(pin_id, int):
#         return {"error": "Authentication required or invalid pin ID"}
    
#     return models.delete_pin(pin_id)
