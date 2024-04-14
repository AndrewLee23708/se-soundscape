from dotenv import load_dotenv
import os
import base64  #encode auth_string using base64
from requests import post
import json
from haversine import haversine


#business handle these queries
import models

#Service layer connects app.py to models.py, does exceptional handling and apply other business rules.


# 1 request access token by esnding id,secret to spotify
# 2 spotify returns temporary access token 
# 3 User uses access token for requests to spotify webapi
# 4 spotify returns JSON object


#load environment variables
load_dotenv()
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

#### This is not the exact access method we needed, this is a place holder until actual token method is implemented.

#returns us spotify token
def get_token():
    auth_string = client_id + ":" + client_secret
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")
    
    url = "https://accounts.spotify.com/api/token"

    #headers associated with request, send POST request to URL
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}
    result = post(url, headers=headers, data=data)
    json_result = json.loads(result.content)
    token = json_result["access_token"]
    return token


token = get_token()
print(token)


# Google maps api

def handle_google_maps_redirect():
    # Logic to handle Google Maps interaction
    pass



############################################################

'''
Functions to deal with internal business rules for models.py
'''
############################################################

##### Scape Related Functions
### We use get_token() function to validate user authentication

#Retrieves all scapes for a specific user after validating their authentication.
def service_get_all_scapes_for_user(user_id):

    if user_id and isinstance(user_id, int):  # Basic check to ensure user_id is valid
        return get_all_scapes_for_user(user_id)
    else:
        return {"error": "Invalid User ID"}

#Adds a new scape after validating user's access token and checking inputs.
def service_add_new_scape(user_id, scape_name, visibility_status, shareable_link):

    access_token = get_user_spotify_token(user_id)
    if not access_token:
        return {"error": "Authentication required"}

    if isinstance(scape_name, str) and scape_name.strip() and isinstance(visibility_status, str) and isinstance(shareable_link, str):
        return add_new_scape(user_id, scape_name, visibility_status, shareable_link)
    else:
        return {"error": "Invalid input data"}

#Updates an existing scape only if the user is authenticated and owns the scape.
def service_update_scape(user_id, scape_id, scape_name, visibility_status, shareable_link):
    
    access_token = get_user_spotify_token(user_id)
    if not access_token:
        return {"error": "Authentication required"}

    if all([isinstance(scape_id, int), isinstance(scape_name, str) and scape_name.strip(),
            isinstance(visibility_status, str), isinstance(shareable_link, str)]):
        return update_scape(scape_id, scape_name, visibility_status, shareable_link)
    else:
        return {"error": "Invalid data provided for update"}

# Deletes a scape after validating that the user is authenticated and owns the scape.
def service_delete_scape(user_id, scape_id):

    access_token = get_user_spotify_token(user_id)
    if not access_token:
        return {"error": "Authentication required"}

    if isinstance(scape_id, int):
        return delete_scape(scape_id)
    else:
        return {"error": "Invalid Scape ID for deletion"}


##### Pin functions: Users have choosen a scape at this point and can manipulate pins

# Fetch pins
def service_get_pins_by_profile(scape_id):
    # Add business rule before fetching pins

    if scape_id and isinstance(scape_id, int):  # Basic validation example
        return get_pins_by_profile(scape_id)
    else:
        return {"error": "Invalid Scape ID"}

### Users and outsiders can look at pin details for now, will be updated later on
def service_get_pin_details(pin_id):
    # business rules to be implemented before fetching pins

    if pin_id and isinstance(pin_id, int):
        return get_pin_details(pin_id)
    else:
        return {"error": "Invalid Pin ID"}


### Editing pins: Business Logic + authenticate user_id for each of these function
# add pin
def service_add_pin(user_id, scape_id, location, latitude, longitude, radius, priority, playlist_id, date_created):
   
    # authentication
    access_token = get_user_spotify_token(user_id)
    if not access_token:
        return {"error": "Authentication required"}

    # business rules: check if the pin data is valid
    if not location.strip():  # Ensure location is not empty or whitespace
        return {"error": "Invalid location"}
    if not (-90 <= latitude <= 90):
        return {"error": "Latitude out of range"}
    if not (-180 <= longitude <= 180):
        return {"error": "Longitude out of range"}
    if radius < 0:
        return {"error": "Radius must be non-negative"}
    if priority < 0:
        return {"error": "Priority must be non-negative"}
    if not isinstance(playlist_id, int) or playlist_id < 1:  # Assuming playlist_id should be a positive integer
        return {"error": "Invalid playlist ID"}

    #Check variable types
    if all([isinstance(scape_id, int), location, isinstance(latitude, (int, float)), 
            isinstance(longitude, (int, float)), isinstance(radius, (int, float)), 
            isinstance(priority, int), playlist_id]):
        return pin_add(scape_id, location, latitude, longitude, radius, priority, playlist_id, date_created)
    else:
        return {"error": "Invalid pin data"}

# update pins
def service_update_pin(user_id, pin_id, scape_id, location, latitude, longitude, radius, priority, playlist_id):
    
    # Authentication check
    access_token = get_user_spotify_token(user_id)
    if not access_token:
        return {"error": "Authentication required"}
    
    # Business rules and data validation
    if not all([isinstance(pin_id, int), isinstance(scape_id, int), location.strip(),
                 -90 <= latitude <= 90, -180 <= longitude <= 180, radius >= 0, priority >= 0, isinstance(playlist_id, int) and playlist_id > 0]):
        return {"error": "Invalid data provided for update"}
    
    return update_pin(pin_id, scape_id, location, latitude, longitude, radius, priority, playlist_id)


# delete pins
def service_delete_pin(user_id, pin_id):
    # Authentication check
    access_token = get_user_spotify_token(user_id)

    if not access_token or not isinstance(pin_id, int):
        return {"error": "Authentication required or invalid pin ID"}
    
    return delete_pin(pin_id)




### Check if user is around a pin
### usage:
# :param user_location: A tuple containing the user's latitude and longitude.
# :return: A list of pins that the user is within the radius of.
def check_user_within_pin_service(user_location):

    pins = get_pins_by_profile(user_id)
    user_within_pins = []
    
    for pin in pins:
        pin_location = (pin['Latitude'], pin['Longitude'])
        distance = haversine(user_location, pin_location, unit='m')  # distance in meters
        
        if distance <= pin['Radius']:
            user_within_pins.append(pin)
    
    return user_within_pins