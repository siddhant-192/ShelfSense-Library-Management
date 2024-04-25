from flask import jsonify, request, make_response
from models import *
# from security_framework import roles_accepted, auth_token_required
from flask_security import roles_accepted, auth_token_required
from flask_restful import Resource
from sqlalchemy import desc
from redis_caching.instances import cache

# Feedback operations
class feedback(Resource):
    @auth_token_required
    @roles_accepted('admin', 'user')
    @cache.cached(timeout=10)
    def get(self):
        feedbacks = feedbackTable.query.all()
        feedback_info = []
        for feedback in feedbacks:
            feedback_info.append({
                'id': feedback.id,
                'user_id': feedback.user_id,
                'feedback': feedback.feedback
            })
        return make_response(jsonify(feedback_info), 200)

    @auth_token_required
    @roles_accepted('admin', 'user')
    def post(self):
        data = request.get_json()
        user_id = data['user_id']
        book_id = data['book_id']
        feedback_msg = data['feedback_msg']

        feedback_entry = feedbackTable.query.filter_by(user_id=user_id, book_id=book_id).first()

        if feedback_entry:
            feedback_entry.feedback = feedback_msg
            feedback_entry.date = datetime.now()
            db.session.commit()
            return make_response(jsonify({'message': 'Feedback updated successfully'}), 200)
        else:
            feedback_entry = feedbackTable(user_id=user_id, feedback=feedback_msg, book_id=book_id, date_created=datetime.now())
            print(feedback_entry)
            db.session.add(feedback_entry)
            db.session.commit()
            return make_response(jsonify({'message': 'Feedback created successfully'}), 201)



class feedback_by_bookid(Resource):
    @auth_token_required
    @roles_accepted('admin', 'user')
    def post(self):
        data = request.get_json()
        book_id = data['book_id']

        feedbacks = feedbackTable.query.filter_by(book_id=book_id).all()

        feedback_info = []
        for feedback_item in feedbacks:
            user = User.query.get(feedback_item.user_id)
            feedback_info.append({
                'id': feedback_item.id,
                'book_id': feedback_item.book_id,
                'user_id': feedback_item.user_id,
                'username': user.username if user else None,
                'feedback': feedback_item.feedback
            })

        return make_response(jsonify(feedback_info), 200)
    
    

#get feedback by userid
class feedback_by_userid(Resource):
    @auth_token_required
    @roles_accepted('admin', 'user')
    @cache.cached(timeout=10)
    def get(self):
        data = request.get_json()
        user_id = data['user_id']
        feedbacks = feedbackTable.query.filter_by(user_id=user_id).all()
        feedback_info = []
        for feedback_item in feedbacks:
            user = User.query.get(feedback_item.user_id)
            feedback_info.append({
                'id': feedback_item.id,
                'book_id': feedback_item.book.id,
                'user_id': feedback_item.user.id,
                'username': user.username if user else None,
                'feedback': feedback_item.feedback
            })
        return make_response(jsonify(feedback_info), 200)

#get feedback by userid and bookid
class feedback_by_userid_bookid(Resource):
    @auth_token_required
    @roles_accepted('admin', 'user')
    @cache.cached(timeout=10)
    def get(self):
        data = request.get_json()
        userId = data['user_id']
        bookId = data['book_id']
        feedback_entry = feedbackTable.query.filter_by(user_id=userId, book_id=bookId)
        if feedback_entry:
            feedback_info = []
            
            user = User.query.get(feedback_entry.user_id)
            feedback_info.append({
                'id': feedback_entry.id,
                'book_id': feedback_entry.book_id,
                'user_id': feedback_entry.user_id,
                'username': user.username,
                'feedback': feedback_entry.feedback
            })
            return make_response(jsonify(feedback_info), 200)
        else:
            return make_response(jsonify({}), 404)
