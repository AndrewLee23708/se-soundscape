from dotenv import load_dotenv
import os
import base64  #encode auth_string using base64
from requests import post
import json

# 1 request access token by esnding id,secret to spotify
# 2 spotify returns temporary access token 
# 3 User uses access token for requests to spotify webapi
# 4 spotify returns JSON object

#load environment variables
load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")


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

def handle_google_maps_redirect():
    # Logic to handle Google Maps interaction
    pass