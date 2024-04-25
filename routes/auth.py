from flask import jsonify, request, make_response
from models import *
from security_framework import user_datastore, bcrypt, login_user, roles_accepted, current_user, logout_user, auth_token_required
from flask_restful import Resource
import uuid
from redis_caching.instances import cache


#Register a new user
class register(Resource):
    def post(self):
        data = request.get_json()
        email = data['email']
        password = data['password']
        username = data['userName']
        user = User.query.filter_by(email=email).first()
        if user:
            return make_response(jsonify({'message': 'User already exists'}), 400)
        else:
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            fs_uniquifier = str(uuid.uuid4())  # Generate a unique string using uuid
            user = User(email=email, password=hashed_password, username=username, fs_uniquifier=fs_uniquifier)
            db.session.add(user)
            db.session.commit()
            user_datastore.add_role_to_user(user, 'user')
            db.session.commit()
            return make_response(jsonify({'message': 'User created successfully'}), 201)  


#Login
class login(Resource):
    def post(self):
        data = request.get_json()
        email = data['email']
        password = data['password']
        user = user_datastore.find_user(email=email)
        # user = User.query.filter_by(email=email).first()
        if user and (bcrypt.checkpw(password.encode('utf-8'), user.password)):
            # auth_token = user.get_auth_token()
            login_user(user) # session based login
            db.session.commit()
            auth_token = user.get_auth_token() # token based login
            return make_response(jsonify({'message': 'User logged in successfully', 'auth_token': auth_token, 'id': current_user.id, 'email': current_user.email, 'userName':current_user.username ,'roles': [role.name for role in current_user.roles]}), 200)
        else:
            return make_response(jsonify({'message': 'Invalid email or password.'}), 400)
        

#Logout
class logout(Resource):
    def get(self):
        logout_user()
        db.session.commit()
        return make_response(jsonify({'message': 'User logged out successfully'}), 200)
    

#Update user
class update_user(Resource):
    @auth_token_required
    @roles_accepted('admin')
    def put(self, user_id):
        user = User.query.get(user_id)
        if not user:
            return make_response(jsonify({'message': 'User not found'}), 400)
        data = request.get_json()
        username = data.get('username')
        if username is not None:
            user.username = username
        db.session.commit()
        return make_response(jsonify({'message': 'User updated successfully'}), 200)


#Delete user
from flask import jsonify, request, make_response
from models import *
from security_framework import roles_accepted, auth_token_required
from flask_restful import Resource

class delete_user(Resource):
    @auth_token_required
    @roles_accepted('admin')
    def delete(self, user_id):
        user = User.query.get(user_id)
        if not user:
            return make_response(jsonify({'message': 'User not found'}), 400)

        # Delete all feedback records associated with the user
        feedback_records = feedbackTable.query.filter_by(user_id=user_id).all()
        for feedback in feedback_records:
            db.session.delete(feedback)

        # Delete all book issue records associated with the user
        issued_books = bookissue.query.filter_by(user_id=user_id).all()
        for issued_book in issued_books:
            book = Book.query.get(issued_book.book_id)
            book.issue_status = False
            db.session.delete(issued_book)

        # Delete the user's role
        user_datastore.remove_role_from_user(user, 'user')

        # Delete the user
        db.session.delete(user)
        db.session.commit()

        return make_response(jsonify({'message': 'User and all associated records deleted successfully'}), 200)
    

#Get user details
class get_user(Resource):
    @auth_token_required
    @roles_accepted('admin', 'user')
    @cache.cached(timeout=5)
    def get(self, user_id):
        user = User.query.get(user_id)
        if not user:
            return make_response(jsonify({'message': 'User not found'}), 400)
        return make_response(jsonify({'id': user.id, 
                                      'email': user.email, 
                                      'username': user.username, 
                                      'roles': [role.name for role in user.roles], 
                                      'last_login_at': user.last_login_at, 
                                      'last_login_ip':user.last_login_ip, 
                                      'login_count': user.login_count,
                                      'current_login_at': user.current_login_at}), 200)
    
#Get all users
class get_all_users(Resource):
    @auth_token_required
    @roles_accepted('admin')
    @cache.cached(timeout=10)
    def get(self):
        users = User.query.all()
        user_list = []
        for user in users:
            user_list.append({'id': user.id, 
                              'email': user.email, 
                              'username': user.username,  
                              'last_login_at': user.last_login_at, 
                              'last_login_ip':user.last_login_ip, 
                              'login_count': user.login_count,
                              'current_login_at': user.current_login_at})
        return make_response(jsonify(user_list), 200)