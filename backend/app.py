import requests
from flask import Flask, request, jsonify, make_response, redirect, session
from flask_cors import CORS
import os
import base64
from spotipy.oauth2 import SpotifyOAuth

from decorators import time_check, check_authenticated
import service
from database import setup_db  # function for DB connections

app = Flask(__name__)
app.secret_key = os.getenv("APP_SECRET")

CORS(app)

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
sp_oauth = SpotifyOAuth(
    client_id=client_id,
    client_secret=client_secret,
    redirect_uri="http://127.0.0.1:5000/callback",
    scope="streaming user-read-email user-read-private user-read-playback-state user-modify-playback-state"
)


@app.route('/login', methods=["GET"])
def login():
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url, code=302)

# make it return user_id info from profile by fetching user_id from user_info


# modified callback to save/check for user
@app.route('/callback')
def callback():
    print('calling back')
    authorization_code = request.args["code"]
    auth_options = {
        'url': 'https://accounts.spotify.com/api/token',
        'form': {
            'code': authorization_code,
            'redirect_uri': 'http://127.0.0.1:5000/callback',
            'grant_type': 'authorization_code'
        },
        'headers': {
            'content-type': 'application/x-www-form-urlencoded',
            'Authorization': 'Basic ' + base64.b64encode((client_id + ':' + client_secret).encode('utf-8')).decode('utf-8')
        }
    }
    # Send the POST request to exchange the authorization code for an access token
    response = requests.post(
        auth_options['url'], data=auth_options['form'], headers=auth_options['headers'])
    data = response.json()
    access_token =  data['access_token']
    # fetch username
    url = "https://api.spotify.com/v1/me"
    headers = {
        'Authorization': f'Bearer {access_token}',
    }
    response = requests.get(url, headers=headers)
    data = response.json()
    user_id = data['id']
   # Save the user ID to the database
    if service.save_user(user_id):
        session['user_id'] = user_id  # save this session in the backend
        print("User login/saved successfully")
    else:
        print("Failed to save user")
    resp = make_response(
        redirect(f'http://localhost:3000/map?token={access_token}&user_id={user_id}'))
    return resp


@app.route('/user', methods=["POST"])
def user():
    data = request.get_json()
    token = data.get('token')
    url = "https://api.spotify.com/v1/me"
    headers = {
        'Authorization': f'Bearer {token}',
    }
    response = requests.get(url, headers=headers)
    data = response.json()
    return jsonify(data)


@app.route('/googlekey', methods=["GET"])
def googlekey():
    api_key = os.getenv("GOOGLE_API_KEY")
    return jsonify({"google_api_key": api_key})


@app.route('/playlists', methods=["POST"])
def playlists():
    data = request.get_json()
    token = data.get('token')
    url = f"https://api.spotify.com/v1/me/playlists?limit=50"
    headers = {
        'Authorization': f'Bearer {token}',
    }
    response = requests.get(url, headers=headers)
    data = response.json()
    return jsonify(data)


@app.route('/play', methods=["POST"])
def play():
    data = request.get_json()
    token = data.get('token')
    device_id = data.get('device_id')
    uri = data.get('uri')
    url = f"https://api.spotify.com/v1/me/player/play?device_id={device_id}"
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    data = {
        "context_uri": uri
    }
    requests.put(url, headers=headers, json=data)
    return jsonify({"message": f'playback {uri} started'})


@app.route('/pause', methods=["POST"])
def pause():
    data = request.get_json()
    token = data.get('token')
    device_id = data.get('device_id')
    url = f"https://api.spotify.com/v1/me/player/pause?device_id={device_id}"
    headers = {
        'Authorization': f'Bearer {token}',
    }
    requests.put(url, headers=headers)
    return jsonify({"message": "playback stopped"})

##########################

# Pin related Endpoints #

##########################


'''

DEMO, STRAIGHT FROM PROFILE TO LIST OF PINS


'''

# route ‘save’, POST:
# YOU WILL RECEIVE: JSON Object: (user_id, pin JSON object)
# Pin JSON Object: {name, lat, lng, radius, uri)
# YOU WILL DO: store pin in backend for the user_id and generate pin id
# YOU WILL RETURN: return generated pin id


@app.route('/createpin', methods=['POST'])
@check_authenticated
def save_pin():
    data = request.get_json()  # Get data from POST request
    user_id = data.get('user_id')  # Extract user_id from data
    pin_data = data.get('pin')  # Extract pin data from request

    # Call a service function to save the pin and return the generated pin ID
    pin_id = service.save_pin_for_user(user_id, pin_data)
    if pin_id:
        return jsonify({"pin_id": pin_id}), 201  # Return the generated pin ID
    else:
        return jsonify({"error": "Failed to save pin"}), 500


# Route ‘fetchpins’, POST
# YOU WILL RECEIVE: JSON Object: (user_id)
# YOU WILL DO: retrieve pin objects for user_id from backend
# YOU WILL RETURN: all of the user’s pin objects
# Endpoint to fetch all pins for a user given their Spotify User ID.

@app.route('/fetchpins', methods=['POST'])
@check_authenticated
def fetch_user_pins():

    data = request.get_json()  # Get data from POST request
    user_id = data.get('user_id')  # Extract user_id from data

    pins = service.get_pins_for_user(user_id)

    if isinstance(pins, list):
        return jsonify(pins), 200  # Correct use of jsonify to send data
    else:
        # Appropriate error handling
        return jsonify({"error": "Failed to fetch pins"}), 500


# Route ‘modifypin’, POST
# YOU WILL RECEIVE: JSON Object: (pin_id, updated pin JSON object, user_id)
# YOU WILL DO: Update corresponding pin in database
# YOU WILL RETURN: nothing

@app.route('/modifypin', methods=['POST'])
@check_authenticated
def modify_pin():
    data = request.get_json()
    pin_id = data.get('pin_id')
    user_id = data.get('user_id')
    updated_pin = data.get('pin')

    success = service.update_pin(user_id, pin_id, updated_pin)
    if success:
        return jsonify({"message": "Pin updated successfully"}), 200
    else:
        return jsonify({"error": "Failed to update pin"}), 500


# Route ‘deletepin’, POST
# YOU WILL RECEIVE: JSON Object: (pin_id, user_id)
# YOU WILL DO: Delete corresponding pin in database
# YOU WILL RETURN: nothing

@app.route('/deletepin', methods=['POST'])
@check_authenticated
def delete_pin():
    data = request.get_json()
    pin_id = data.get('pin_id')
    user_id = data.get('user_id')

    if not pin_id or not user_id:
        return jsonify({"error": "Missing data"}), 400

    success = service.delete_pin(user_id, pin_id)
    if success:
        return jsonify({"message": "Pin deleted successfully"}), 200
    else:
        return jsonify({"error": "Failed to delete pin"}), 500


'''

SCAPES, STRAIGHT FROM PROFILE TO LIST OF PINS


'''


# users would have access to all profiles and shared profiles
# **note: profile are users, scapes are different maps they have
# ***note: front end can declare which endpoint method you want to call
# all operations to first menu where users can select their profiles

# @app.route('/scapes/<int:profile_id>', methods=['GET', 'POST', 'DELETE'])
# def scape_operations(profile_id):

#     # Update the profile with the provided ID
#     if request.method == 'GET':
#         scape_details = service.service_get_all_scapes_for_user(profile_id)
#         return jsonify(scape_details), 200

#     elif request.method == 'POST':
#         # Create a new profile
#         data = request.get_json()
#         return jsonify(service.service_add_new_scape(profile_id, data)), 201

#     elif request.method == 'DELETE':
#         # Delete the profile with the provided ID
#         return jsonify(service.service_delete_scape_service(profile_id)), 204

#     else:
#         return jsonify({"error": "Method not allowed"}), 405


# # Once user selects a scape, we return all available scapes
# @app.route('/scapes/<int:scape_id>/pins', methods=['GET'])
# def get_pins_for_scape(scape_id):
#     # Retrieve and return all pins for the given scape
#     pins = service.get_pins_by_scape_service(scape_id)  # Service that handles the business logic for getting pins
#     return jsonify(pins), 200


# ##### pin operations

# # take in pin id,
# @app.route('/pins', methods=['POST', 'GET'])
# def get_pin():
#     data = request.get_json()
#     id = data.get("id")
#     pin = data.get("pin")

#     service.service_get_pin_details(id)

#     return jsonify()

# @app.route('/pins', methods=['POST'])
# def add_pin():
#     data = request.get_json()
#     return service.service_add_pin(data), 201  # HTTP 201 Created for successful resource creation

# @app.route('/pins/<int:pin_id>', methods=['DELETE'])
# def delete_pin(pin_id):
#     return service.service_delete_pin(pin_id), 204  # HTTP 204 No Content for successful deletion without response body

# @app.route('/pins/<int:pin_id>', methods=['PUT'])
# def edit_pin(pin_id):
#     data = request.get_json()
#     return service.service_update_pin(pin_id, data), 200  # HTTP 200 OK for successful update

# if __name__ == '__main__':
#     app.run(debug=True)


# ### place holder, this is already implemented in front end, but we need to find a way to send current location to server as POST rquest, and have server check against Pin locations:
# ### Need information from Google maps API
# @app.route('/pins/check-location', methods=['POST'])
# def check_pin_location():
#     data = request.get_json()
#     user_location = data.get('location')

#     # Assuming 'check_user_within_pin' is a service that returns pin data if the user is within a pin's location
#     pin_info = check_user_within_pin_service(user_location)
#     if pin_info:
#         return jsonify(pin_info), 200
#     else:
#         return jsonify({"error": "No pins nearby"}), 404


# implement shared feature later on
# @app.route('/profiles/<profileId>', methods=['POST'])
# def share_profile(profileId):
#     data = request.get_json()
#     return add_profile_service(profileId, data)

# upon clicking a scape, we will load all the pins on the map


# ### DB test endpoint
# @app.route('/db-test')  # Test database connection
# def test_db():
#     try:
#         connection = setup_db()
#         cur = connection.cursor()  # All SQL is done through cursor

#         # See how many users there are
#         cur.execute("SELECT COUNT(*) FROM Users")
#         result = cur.fetchone()  # This will be a tuple like (count,)
#         cur.close()

#         # Good practice to return JSON
#         return jsonify({'number_of_users': result[0]})
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500


# #dynamic routing <>, URLs pass parameter and get another website
# #pass variable name
# @app.route('/get-user/<user_id>')
# def get_user(user_id):
#     user_data = {
#         "user_id": user_id,
#         "name": "John Doe",
#         "email": "john.doe@gmail.com"
#      }

#     #query parameter, extra value included after main path
#     extra = request.args.get("extra")
#     if extra:
#         user_data["extra"] = extra

#     return jsonify(user_data), 200  #return JSON, response code. Python dictionary ->Josnify -> json
#                                     #status code 200 of success

# #POST
# @app.route("/create-user", methods = ["POST"])
# def create_user():
#     data = request.get_json()

#     return jsonify(data), 201   #receive json

# def print_name(name):
#     return 'Hi, {}'.format(name)       #application can generate based on name given

# if __name__ == '__main__':           #main method?
#     app.run(debug=True)
