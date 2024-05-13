from dotenv import load_dotenv
from requests import post
import models

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
    
    # Else Insert new user 
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
    
    pin_id = models.add_pin_in_db(user_id, pin_data)
    print(pin_id)

    if not pin_id:
        return {"error": "Failed to add pin", "success": False}
    else:
        return pin_id



### update pins for users
def update_pin(user_id, pin_id, pin_data):

    print("pin_id at service is: {}", pin_id)
    try:
        if not (-90 <= float(pin_data['lat']) <= 90) or not (-180 <= float(pin_data['lng']) <= 180):
            return {"error": "Latitude or longitude out of range", "success": False}
        if float(pin_data['radius']) < 0:
            return {"error": "Radius must be non-negative", "success": False}
    except ValueError:
        return {"error": "Latitude, longitude, and radius must be valid numbers", "success": False}

    print('going to models')
    # Update the pin
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


