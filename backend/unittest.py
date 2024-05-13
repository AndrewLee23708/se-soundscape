import pytest
from service import update_pin_service

#run through our business layer which catches errors and sends it to the model layer.

### Before you test, make sure you insert the following into your database

# Valid inputs for a successful update
def get_valid_inputs():
    return {
        "user_id": 999,  # Copy and paste your user__i
        "pin_id": 999,  # Assume this exists for the test in the DB
        "pin_data": {
            "name": "Test Location",
            "lat": 45.0,
            "lng": -73.0,
            "radius": 100,
            "uri": 'https://open.spotify.com/album/0s1mq36MFh8jBHUPeo5vjo?si=_29pJTvoThmvSbMHFxO1GA'
        }
    }

# Location: Empty string
def test_update_pin_with_empty_location():
    valid_inputs = get_valid_inputs()
    valid_inputs['location'] = ""  # Empty location
    with pytest.raises(ValueError):
        update_pin_service(**valid_inputs)

# Latitude: Invalid range
@pytest.mark.parametrize("latitude", [-91, 91])        #use this decorator to parameterize various inputs
def test_update_pin_with_invalid_latitude(latitude):
    valid_inputs = get_valid_inputs()
    valid_inputs['latitude'] = latitude
    with pytest.raises(ValueError):
        update_pin_service(**valid_inputs)

# Longitude: Invalid range
@pytest.mark.parametrize("longitude", [-181, 181])
def test_update_pin_with_invalid_longitude(longitude):
    valid_inputs = get_valid_inputs()
    valid_inputs['longitude'] = longitude
    with pytest.raises(ValueError):
        update_pin_service(**valid_inputs)

# Radius:Test various invalid cases
@pytest.mark.parametrize("radius", [9999, 0, -1])
def test_update_pin_with_invalid_radius(radius):
    valid_inputs = get_valid_inputs()
    valid_inputs['radius'] = radius
    with pytest.raises(ValueError):
        update_pin_service(**valid_inputs)

# Priority: Negative number
@pytest.mark.parametrize("radius", [9999, 0, -1])
def test_update_pin_with_negative_priority():
    valid_inputs = get_valid_inputs()
    valid_inputs['priority'] = -1
    with pytest.raises(ValueError):
        update_pin_service(**valid_inputs)

# PlaylistID: Invalid ID (non-existing on Spotify)
def test_update_pin_with_invalid_playlist_id():
    valid_inputs = get_valid_inputs()
    valid_inputs['playlist_id'] = 9999  # Non-existing Playlist ID on Spotify
    with pytest.raises(ValueError):
        update_pin_service(**valid_inputs)

# Pin_ID: Invalid ID (non-existing pin)
def test_update_pin_with_invalid_pin_id():
    valid_inputs = get_valid_inputs()
    valid_inputs['pin_id'] = 9999  #Non-existing Pin ID
    with pytest.raises(ValueError):
        update_pin_service(**valid_inputs)
