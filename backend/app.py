from flask import Flask, request, jsonify, url_for, redirect, session
from decorators import time_check
import service
from database import setup_db   #function for DB connections

app = Flask(__name__)

# GET: Get data as response
# POST: Create new record
# PUT: Update a record
# DELETE: Delete a record

#Users first prompted with button, then once click, spotify will authenticate them
#once we have access to spotify ID and Access token, we can route to features of app
#Authenticates the login
@app.route('/auth/spotify', methods=['GET'])          #i dont think the users see this, so you have an authPage endpoint so we can check for login detaisl
def loginAuth():

    #redirects them to spotify for login
	token = get_token() #grab access token (for us developers)
    
    #We check for the following:
    #if never logged in before, add into DB


    #if logged in before, pull up preexisting settings

	return token




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