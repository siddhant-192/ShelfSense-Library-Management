from flask import jsonify, request, make_response
from models import *
# from security_framework import roles_accepted, auth_token_required
from flask_security import roles_accepted, auth_token_required
from flask_restful import Resource
from sqlalchemy import desc
from redis_caching.instances import cache

# Book operations
class book(Resource):
    @auth_token_required
    @roles_accepted('admin', 'user')
    @cache.cached(timeout=10)
    def get(self):
        books = Book.query.all()
        book_info = []
        for book in books:
            book_info.append({
                'id': book.id,
                'name': book.name,
                'authors': book.authors,
                'section_id': book.section_id,
                'content': book.content,
                'issue_status': book.issue_status
            })
        return make_response(jsonify(book_info), 200)

    @auth_token_required
    @roles_accepted('admin')
    def post(self):
        data = request.get_json()
        name = data['name']
        authors = data['authors']
        section_id = data['section_id']
        content = data['content']
        book = Book.query.filter_by(name=name).first()
        if book:
            return make_response(jsonify({'message': 'Book already exists'}), 400)
        else:
            book = Book(name=name, authors=authors, section_id=section_id, content=content)
            db.session.add(book)
            db.session.commit()
            return make_response(jsonify({'message': 'Book created successfully'}), 201)

# Book operations by id
class book_id(Resource):
    @auth_token_required
    @roles_accepted('admin', 'user')
    @cache.cached(timeout=10)
    def get(self, book_id):
        book = Book.query.get(book_id)
        if not book:
            return make_response(jsonify({'message': 'Book not found'}), 400)
        book_info = {
            'id': book.id,
            'name': book.name,
            'authors': book.authors,
            'section_id': book.section_id,
            'content': book.content
        }
        return make_response(jsonify(book_info), 200)

    @auth_token_required
    @roles_accepted('admin')
    def put(self, book_id):
        data = request.get_json()
        name = data['name']
        authors = data['authors']
        section_id = data['section_id']
        book = Book.query.get(book_id)
        if not book:
            return make_response(jsonify({'message': 'Book not found'}), 400)
        if name is not None:
            book.name = name
        if authors is not None:
            book.authors = authors
        if section_id is not None:
            book.section_id = section_id
        db.session.commit()
        return make_response(jsonify({'message': 'Book updated successfully'}), 200)

    @auth_token_required
    @roles_accepted('admin')
    def delete(self, book_id):
        book = Book.query.get(book_id)
        if not book:
            return make_response(jsonify({'message': 'Book not found'}), 400)

        # Delete all issued records associated with the book
        issued_records = bookissue.query.filter_by(book_id=book_id).all()
        for record in issued_records:
            db.session.delete(record)

        # Delete the book
        db.session.delete(book)
        db.session.commit()
        return make_response(jsonify({'message': 'Book and associated issued records deleted successfully'}), 200)

# Issue book
class issue_book(Resource):
    @auth_token_required
    @roles_accepted('admin', 'user')
    def post(self):
        data = request.get_json()
        user_id = data['user_id']
        book_id = data['book_id']
        user = User.query.get(user_id)
        book = Book.query.get(book_id)
        issued_books = bookissue.query.filter_by(user_id=user_id, return_date=None).all()
        if not user:
            return make_response(jsonify({'message': 'User not found'}), 400)
        if len(issued_books) >= 5:
            return make_response(jsonify({'message': 'User has already issued 5 books. No more can be alloted at once.'}), 200)
        if not book:
            return make_response(jsonify({'message': 'Book not found'}), 400)
        if book.issue_status:
            return make_response(jsonify({'message': 'Book already issued'}), 400)
        book.issue_status = True
        book_issue = bookissue(user_id=user_id, book_id=book_id, date_issued=datetime.now())
        db.session.add(book_issue)
        db.session.commit()
        return make_response(jsonify({'message': 'Book issued successfully'}), 200)

# Return book
class return_book(Resource):
    @auth_token_required
    @roles_accepted('admin', 'user')
    def post(self):
        data = request.get_json()
        book_id = data['book_id']
        user_id = data['user_id']
        
        book_issue = bookissue.query.filter_by(book_id=book_id, user_id=user_id, return_date=None).first()
        
        if book_issue is None:
            return make_response(jsonify({'message': 'Book not issued to this user'}), 400)
        
        book = Book.query.filter_by(id=book_id).first()
        
        if not book:
            return make_response(jsonify({'message': 'Book not found'}), 400)
        
        if not book.issue_status:
            return make_response(jsonify({'message': 'Book is not currently issued'}), 400)
        
        book.issue_status = False
        book_issue.return_date = datetime.now()
        print(book_issue.return_date)
        db.session.commit()
        
        return make_response(jsonify({'message': 'Book returned successfully'}), 200)



# book_issue_status
class book_issue_status(Resource):
    @auth_token_required
    @roles_accepted('admin', 'user')
    def post(self):
        data = request.get_json()
        book_id = data['book_id']
        user_id = data['user_id']
        
        book = Book.query.get(book_id)
        if not book:
            return make_response(jsonify({'message': 'Book not found'}), 400)

        book_issue = bookissue.query.filter_by(book_id=book_id, user_id=user_id, return_date=None).first()
        
        if not book.issue_status:
            return make_response(jsonify({'message': 0}), 200) # Book is available
        elif book_issue and int(book_issue.user_id) == int(user_id):
            return make_response(jsonify({'message': 1}), 200) # Book is issued to the user
        else:
            book_issue = bookissue.query.filter_by(book_id=book_id, return_date=None).first()
            issued_user = User.query.get(book_issue.user_id)
            username_issued = issued_user.username
            return make_response(jsonify({'message': 2, 'username_issued': username_issued}), 200) # Book is issued to another user


# Search book by name
class book_search(Resource):
    @auth_token_required
    @roles_accepted('admin','user')
    @cache.cached(timeout=10)
    def get(self, book_name):
        books = Book.query.filter(Book.name.ilike(f"%{book_name}%")).all()
        book_info = []
        for book in books:
            book_info.append({
                'id': book.id,
                'name': book.name,
                'authors': book.authors,
                'section_id': book.section_id,
                'content': book.content
            })
        return make_response(jsonify(book_info), 200)
    
#Search book by author string part
class search_book_by_author(Resource):
    @auth_token_required
    @roles_accepted('admin','user')
    @cache.cached(timeout=10)
    def get(self):
        author_name = request.args.get('author_name')
        if author_name is None:
            return make_response(jsonify({'message': 'Author name is required.'}), 400)

        books = Book.query.filter(Book.authors.ilike(f"%{author_name}%")).all()
        book_info = []
        for book in books:
            book_info.append({
                'id': book.id,
                'name': book.name,
                'authors': book.authors,
                'section_id': book.section_id,
                'content': book.content
            })
        return make_response(jsonify(book_info), 200)


#Get issued books to a user
class issued_books(Resource):
    @auth_token_required
    @roles_accepted('admin', 'user')
    @cache.cached(timeout=10)
    def get(self, user_id):
        issued_books = bookissue.query.filter_by(user_id=user_id).all()
        book_info = []
        for book in issued_books:
            book_info.append({
                'book_id': book.book_id,
                'date_issued': book.date_issued,
                'return_date': book.return_date,
                'user_id': book.user_id
            })
        return make_response(jsonify(book_info), 200)
    

#get all issued books
class all_issued_books(Resource):
    @auth_token_required
    @roles_accepted('admin', 'user')
    @cache.cached(timeout=10)
    def get(self):
        issued_books = bookissue.query.all()
        book_info = []
        for book in issued_books:
            user_issuing = User.query.get(book.user_id)
            book_info.append({
                'book_id': book.book_id,
                'date_issued': book.date_issued,
                'return_date': book.return_date,
                'user_id': book.user_id,
                'username': user_issuing.username
            })
        return make_response(jsonify(book_info), 200)