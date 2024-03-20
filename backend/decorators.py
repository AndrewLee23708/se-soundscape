import time

### Functions are traeted like objects, 

#decorator to check time
def time_check(func):
    def wrapper():
        t1 = time.time()
        func()
        t2 = time.time() - t1
        print(f'{func.__name__} ran in {t2} seconds')
    return wrapper

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
