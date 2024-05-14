import pytest
from service import update_pin  # Adjusted import

# Define valid inputs for a successful update
def get_valid_inputs():
    return {
        "user_id": 1,  # Assuming there needs to be a user_id based on your service functions
        "pin_id": 1,
        "pin_data": {  # Adjusted to pass a dictionary for pin_data as expected by your function
            "lat": 45.0,
            "lng": -73.0,
            "radius": 100,
            "location": "Test Location",
            "priority": 1
        }
    }

# Location: Empty string
def test_update_pin_with_empty_location():
    valid_inputs = get_valid_inputs()
    valid_inputs['pin_data']['location'] = ""  # Empty location
    with pytest.raises(ValueError):
        update_pin(**valid_inputs)  # Adjusted call

# Latitude: Invalid range
@pytest.mark.parametrize("latitude", [-91, 91])  # Use this decorator to parameterize various inputs
def test_update_pin_with_invalid_latitude(latitude):
    valid_inputs = get_valid_inputs()
    valid_inputs['pin_data']['lat'] = latitude
    with pytest.raises(ValueError):
        update_pin(**valid_inputs)

# Longitude: Invalid range
@pytest.mark.parametrize("longitude", [-181, 181])
def test_update_pin_with_invalid_longitude(longitude):
    valid_inputs = get_valid_inputs()
    valid_inputs['pin_data']['lng'] = longitude
    with pytest.raises(ValueError):
        update_pin(**valid_inputs)

# Radius: Test various invalid cases
@pytest.mark.parametrize("radius", [9999, 0, -1])
def test_update_pin_with_invalid_radius(radius):
    valid_inputs = get_valid_inputs()
    valid_inputs['pin_data']['radius'] = radius
    with pytest.raises(ValueError):
        update_pin(**valid_inputs)

# Priority: Negative number
@pytest.mark.parametrize("priority", [-1])
def test_update_pin_with_negative_priority(priority):
    valid_inputs = get_valid_inputs()
    valid_inputs['pin_data']['priority'] = priority
    with pytest.raises(ValueError):
        update_pin(**valid_inputs)

# PlaylistID: Assuming playlist ID is part of pin_data in your real service
def test_update_pin_with_invalid_playlist_id():
    valid_inputs = get_valid_inputs()
    valid_inputs['pin_data']['playlist_id'] = 'invalid_playlist'  # Changed to a string assuming it should be a URL or ID
    with pytest.raises(ValueError):
        update_pin(**valid_inputs)

# Pin_ID: Invalid ID (non-existing pin)
def test_update_pin_with_invalid_pin_id():
    valid_inputs = get_valid_inputs()
    valid_inputs['pin_id'] = 9999  # Non-existing Pin ID
    with pytest.raises(ValueError):
        update_pin(**valid_inputs)
