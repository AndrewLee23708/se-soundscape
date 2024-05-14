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

##########################

# Spotify Related Endpoints #

##########################


### Responsible for logging user in through spotify url
# it will return all necesaary information for user_id info from profile by fetching user_id from user_info
@app.route('/login', methods=["GET"])
def login():
    """
    Redirects to Spotify's authorization URL for user login and app authorization.
    
    Returns:
    - Redirection to Spotify login URL.
    """
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url, code=302)

### Callback spotify API to get user to login through spotify, fetch access code and user id
# modified callback to save/check for user
@app.route('/callback')
def callback():
    """
    Handles the callback from the Spotify OAuth flow. This endpoint is hit after the user
    authorizes with Spotify. It exchanges the authorization code received with Spotify for an
    access token. It then fetches the Spotify user's ID and attempts to save the user in the database.
    If successful, it redirects the user to the main application with the access token and user ID
    included in the query parameters.

    Parameters:
    - code (str): An authorization code passed as a query parameter by Spotify.

    Returns:
    - Redirect: Redirects the user to the main map page of the application with access token
      and user ID as query parameters if the user is successfully saved in the database, or
      if saving fails, simply redirects without the user ID.
    
    Side effects:
    - Fetches user data from Spotify.
    - Attempts to save user information in the database.
    - Redirects the user to a different part of the application.
    """
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
    """
    Retrieves and returns Spotify user information using a provided access token.
    The endpoint extracts the 'token' from the incoming JSON payload, which is then used
    to make a request to the Spotify "Get Current User's Profile" API.

    Returns:
        A JSON response containing Spotify user profile data.
    """
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
    """
    Provides the Google API key stored in environment variables.
    This key is used for integrating Google services into the application.

    Returns:
        A JSON response containing the Google Maps API key.
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    return jsonify({"google_api_key": api_key})


### Fetches Spotify playlist to return to front end
@app.route('/playlists', methods=["POST"])
def playlists():
    """
    Retrieves a list of Spotify playlists for the authenticated user using a Spotify access token.
    This endpoint expects a POST request with a JSON payload that includes the Spotify access token.

    Returns:
    json: A JSON response containing a list of playlists from the Spotify API. The structure
          of the returned JSON directly reflects the structure provided by the Spotify API
          for playlists.

    Raises:
    KeyError: If 'token' is not found in the POSTed JSON.
    requests.exceptions.RequestException: If the request to Spotify API fails.
    """
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
    """
    Fetches the current playback state and information about the currently playing track from Spotify's Web API.
    This endpoint requires a valid Spotify access token passed via JSON payload in the 'token' field.

    Returns:
        A JSON response containing the current playback state and track information.
    """
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
    """
    Toggles the shuffle mode for Spotify playback using the Spotify Web API.
    The endpoint reads the Spotify access token from the incoming JSON payload.

    Returns:
        A JSON response confirming the change in the shuffle state.
    """
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
    """
    Starts playback of a Spotify URI on the specified device using the Spotify Web API.
    Receives the Spotify access token, device ID, and context URI (playlist, album, or track) through the request JSON.

    Returns:
        A JSON response indicating successful initiation of playback.
    """
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
    """
    Pauses the current Spotify playback on the specified device using the Spotify Web API.
    The endpoint uses the provided Spotify access token and device ID from the request JSON.

    Returns:
        A JSON response indicating successful pause of playback.
    """
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

@app.route('/createpin', methods=['POST'])
def save_pin():

    """
    Receives a JSON object containing user ID and pin data, stores the pin in the backend,
    and generates a pin ID.

    Parameters:
    - None explicitly; reads from JSON in POST request which should include:
        * user_id (str): The user's ID.
        * pin (dict): The pin data including:
            - name (str): Name of the pin.
            - lat (float): Latitude of the pin location.
            - lng (float): Longitude of the pin location.
            - radius (float): Radius of the pin's area of effect.
            - uri (str): Spotify URI linked with the pin.

    Returns:
    - JSON: Either the generated pin ID or an error message if the operation fails.
    """

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


@app.route('/fetchpins', methods=['POST'])
def fetch_user_pins():

    """
    Retrieves all pin objects for a specified user ID sent via a POST request.

    Parameters:
    - None explicitly; reads user_id from JSON in POST request.

    Returns:
    - JSON: A list of all pin objects associated with the user or an error message.
    """

    data = request.get_json()  # Get data from POST request
    user_id = data.get('user_id')  # Extract user_id from data

    pins = service.get_pins_for_user(user_id)
    return jsonify(pins), 200


@app.route('/editpin', methods=['POST'])
def modify_pin():
    """
    Updates a specific pin based on the provided pin_id and user_id with new pin data.

    Parameters:
    - None explicitly; expects a JSON object in POST request containing:
        * pin_id (int): The ID of the pin to be updated.
        * user_id (str): The user's ID who owns the pin.
        * pin (dict): Updated data for the pin.

    Returns:
    - JSON: Confirmation message if the update is successful or an error message if it fails.
    """
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


@app.route('/deletepin', methods=['POST'])
def delete_pin():
    """
    Deletes a specific pin identified by pin_id and associated with the user_id.

    Parameters:
    - None explicitly; expects a JSON object in POST request containing:
        * pin_id (int): The ID of the pin to be deleted.
        * user_id (str): The user's ID who owns the pin.

    Returns:
    - JSON: Confirmation message if the deletion is successful or an error message if it fails.
    """
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