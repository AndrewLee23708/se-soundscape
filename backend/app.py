import requests
from flask import Flask, request, jsonify, make_response, redirect, session
from flask_cors import CORS
import os
from spotipy.oauth2 import SpotifyOAuth

from decorators import time_check
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


@app.route('/callback')
def callback():
    token_info = sp_oauth.get_access_token(request.args["code"])
    resp = make_response(
        redirect(f'http://localhost:3000/map?token={token_info["access_token"]}'))
    return resp


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


@app.route('/pin', methods=["POST"])
def pin():
    # takes in pin object and stores it
    data = request.get_json()
    return jsonify({"pin created"})

#users would have access to all profiles and shared profiles
# **note: profile = scapes
@app.route('/profiles/<int:profile_id>', methods=['GET', 'PUT', 'POST', 'DELETE'])
def profile_operations(profile_id):

    # Update the profile with the provided ID
    if request.method == 'GET':
        scape_details = service_get_all_scapes_for_user(profile_id)
        return jsonify(scape_details), 200

    elif request.method == 'POST':
        # Create a new profile
        data = request.get_json()
        return jsonify(service_add_new_scape(profile_id, data)), 201

    elif request.method == 'DELETE':
        # Delete the profile with the provided ID
        return jsonify(service_delete_scape_service(profile_id)), 204

    else:
        return jsonify({"error": "Method not allowed"}), 405

### implement shared feature later on
# @app.route('/profiles/<profileId>', methods=['POST'])
# def share_profile(profileId):
#     data = request.get_json()
#     return add_profile_service(profileId, data)

# upon clicking a scape, we will load all the pins on the map

@app.route('/scapes/<int:scape_id>/pins', methods=['GET'])
def get_pins_for_scape(scape_id):
    # Retrieve and return all pins for the given scape
    pins = get_pins_by_scape_service(scape_id)  # Service that handles the business logic for getting pins
    return jsonify(pins), 200


#pin operations
@app.route('/pins', methods=['POST'])
def add_pin():
    data = request.get_json()
    return add_pin_service(data), 201  # HTTP 201 Created for successful resource creation

@app.route('/pins/<int:pin_id>', methods=['DELETE'])
def delete_pin(pin_id):
    return delete_pin_service(pin_id), 204  # HTTP 204 No Content for successful deletion without response body

@app.route('/pins/<int:pin_id>', methods=['PUT'])
def edit_pin(pin_id):
    data = request.get_json()
    return edit_pin_service(pin_id, data), 200  # HTTP 200 OK for successful update


### place holder, but we need to find a way to send current location to server as POST rquest, and have server check against Pin locations:
### Need information from Google maps API
@app.route('/pins/check-location', methods=['POST'])
def check_pin_location():
    data = request.get_json()
    user_location = data.get('location')

    # Assuming 'check_user_within_pin' is a service that returns pin data if the user is within a pin's location
    pin_info = check_user_within_pin_service(user_location)
    if pin_info:
        return jsonify(pin_info), 200
    else:
        return jsonify({"error": "No pins nearby"}), 404




if __name__ == '__main__':
    app.run(debug=True)









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