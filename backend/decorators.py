from flask import request, jsonify, session
import time

def check_authenticated(func):
    def wrapper(*args, **kwargs):

        data = request.get_json(silent=True)    

        session_user_id = session.get('user_id')           # Extract user_id from session
        
        func_user_id = data.get('user_id') if data else None   # Extract user_id from the request's JSON data
        
        if session_user_id and session_user_id == func_user_id:
            return func(*args, **kwargs)
        else:
            return jsonify({'error': 'Unauthorized access'}), 401
    
    wrapper.__name__ = func.__name__
    return wrapper


#decorator to check time
def time_check(func):
    def wrapper():
        t1 = time.time()
        func()
        t2 = time.time() - t1
        print(f'{func.__name__} ran in {t2} seconds')
    return wrapper



### Functions are traeted like objects, 

#decorator: check authentication
# def check_authenticated(user):
#     def decorator(func):
#         def wrapper(*args, **kwargs):
#             if not user.is_authenticated():
#                 raise Exception("User not authenticated!")
#             return func(*args, **kwargs)
#         return wrapper
#     return decorator

###
#
#       Tests Decorators
# 
###


# @time_check
# def sample_query():
#     time.sleep(3.0)


# @time_check
# def do_that():
#     time.sleep(1.7)

# do_this()
# do_that()
# print('Done')
