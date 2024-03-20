from flask import Flask, request, jsonify
from database import setup_db, MySQL
from decorators import time_check
# from models

app = Flask(__name__)

#creates app configuration for database
setup_db(app)

# Initializes the MySQL connection object with the Flask app.
# This object will be used to interact with your MySQL database.
mysql = MySQL(app)  #side note: have to configure mySQL config 'wait_timeout' as well

### DB test endpoint
@app.route('/db-test')  # Test database connection
def test_db():
    try:
        cur = mysql.connection.cursor()  # All SQL is done through cursor

        # See how many users there are
        cur.execute("SELECT COUNT(*) FROM Users")
        result = cur.fetchone()  # This will be a tuple like (count,)
        cur.close()

        # Good practice to return JSON
        return jsonify({'number_of_users': result[0]})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/')    #default path (route)
def hello_world():
    return 'hello world!'

if __name__ == '__main__':
    app.run(debug=True)









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


