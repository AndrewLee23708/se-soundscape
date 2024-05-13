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

### Responsible for logging user in
# make it return user_id info from profile by fetching user_id from user_info
@app.route('/login', methods=["GET"])
def login():
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url, code=302)

### Callback spotify API to get user to login through spotify, fetch access code and user id
# modified callback to save/check for user
@app.route('/callback')
def callback():
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

### Authenticates User
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

### Recieve google key via environment
@app.route('/googlekey', methods=["GET"])
def googlekey():
    api_key = os.getenv("GOOGLE_API_KEY")
    return jsonify({"google_api_key": api_key})

### Fetches Spotify playlist to return to front end
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


### Fetches Song playlist to return to front end
@app.route('/song', methods=["POST"])
def song():
    data = request.get_json()
    token = data.get('token')
    url = "https://api.spotify.com/v1/me/player"
    headers = {
        'Authorization': f'Bearer {token}',
    }
    response = requests.get(url, headers=headers)
    data = response.json()
    return jsonify(data)

### Shuffle feature for spotify
@app.route('/shuffle', methods=["POST"])
def shuffle():
    data = request.get_json()
    token = data.get('token')
    url = "https://api.spotify.com/v1/me/player/shuffle?state=true"
    headers = {
        'Authorization': f'Bearer {token}',
    }
    response = requests.get(url, headers=headers)
    data = response.json()
    return jsonify(data)

### Allows for playback Spotify API
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
    response = requests.put(url, headers=headers, json=data)
    return jsonify({"message": f'Playback of {uri} started successfully'})

### Allows for pause Spotify API
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
#@check_authenticated
def save_pin():
    print('creating pin')
    data = request.get_json()  # Get data from POST request
    user_id = data.get('user_id')  # Extract user_id from data
    pin_data = data.get('pin')  # Extract pin data from request

    pin_id = service.add_pin_for_user(user_id, pin_data)
    print('pin_id', pin_id)
    
    if pin_id:
        return jsonify({"pin_id": pin_id}), 201  #return pin ID
    else:
        return jsonify({"error": "Failed to save pin"}), 500


# Route ‘fetchpins’, POST
# YOU WILL RECEIVE: JSON Object: (user_id)
# YOU WILL DO: retrieve pin objects for user_id from backend
# YOU WILL RETURN: all of the user’s pin objects
# Endpoint to fetch all pins for a user given their Spotify User ID.

@app.route('/fetchpins', methods=['POST'])
#@check_authenticated
def fetch_user_pins():
    data = request.get_json()  # Get data from POST request
    user_id = data.get('user_id')  # Extract user_id from data

    pins = service.get_pins_for_user(user_id)
    return jsonify(pins), 200


# Route ‘modifypin’, POST
# YOU WILL RECEIVE: JSON Object: (pin_id, updated pin JSON object, user_id)
# YOU WILL DO: Update corresponding pin in database
# YOU WILL RETURN: nothing

@app.route('/editpin', methods=['POST'])
#@check_authenticated
def modify_pin():
    print('editing pin in backend')
    data = request.get_json()
    pin_id = data.get('pin_id')
    user_id = data.get('user_id')
    updated_pin = data.get('pin')

    print("pin Id is: ", pin_id)

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
#@check_authenticated
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


