from flask import Flask, request, jsonify, url_for, redirect, session
from decorators import time_check
import service
from database import setup_db   #function for DB connections

app = Flask(__name__)

#once we have access to spotify ID and Access token, we can route to features of app
#Authenticates the login
@app.route('/loginAuth', methods=['GET', 'POST'])          #i dont think the users see this, so you have an authPage endpoint so we can check for login detaisl
def loginAuth():

    #redirects them to spotify for login
	token = get_token() #grab access token (for us developers)
    
    #We check for the following:
    #if never logged in before, add into DB


    #if logged in before, pull up preexisting settings

	return token

#users would have access to all profiles and shared profiles
@app.route('/profiles/<profileId>', methods=['PUT'])
def change_profile(profileId):
    data = request.get_json()
    return change_profile_service(profileId, data)


@app.route('/profiles/<profileId>', methods=['POST'])
def add_profile(profileId):
    data = request.get_json()
    return add_profile_service(profileId, data)


@app.route('/profiles/<profileId>', methods=['DELETE'])
def delete_profile(profileId):
    data = request.get_json()
    return add_profile_service(profileId, data)


@app.route('/profiles/<profileId>', methods=['POST'])
def share_profile(profileId):
    data = request.get_json()
    return add_profile_service(profileId, data)


@app.route('/pins', methods=['POST'])
def add_pin():
    data = request.get_json()
    return add_pin_service(data)

@app.route('/pins/<pinId>', methods=['DELETE'])
def delete_pin(pinId):
    return delete_pin_service(pinId)

@app.route('/pins/<pinId>', methods=['PUT'])
def edit_pin(pinId):
    data = request.get_json()
    return edit_pin_service(pinId, data)







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


