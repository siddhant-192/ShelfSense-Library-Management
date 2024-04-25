from flask import jsonify, request, make_response
from models import *
# from security_framework import roles_accepted, auth_token_required
from flask_security import roles_accepted, auth_token_required
from flask_restful import Resource
from redis_caching.instances import cache


#Section operations
class section(Resource):
    @auth_token_required
    @roles_accepted('admin', 'user')
    @cache.cached(timeout=10)
    def get(self):
        sections = Section.query.all()
        section_info=[]
        for section in sections:
            section_info_temp = {
            'id': section.id,
            'name': section.name,
            'description': section.description,
            }
            section_info.append(section_info_temp)
        return make_response(jsonify(section_info), 200)
        
    
    @auth_token_required
    @roles_accepted('admin')
    def post(self):
        data = request.get_json()
        name = data['name']
        description = data['description']
        section = Section.query.filter_by(name=name).first()
        if section:
            return make_response(jsonify({'message': 'Section already exists'}), 400)
        else:
            section = Section(name=name, description=description)
            db.session.add(section)
            db.session.commit()
            return make_response(jsonify({'message': 'Section created successfully'}), 201)
        

#Section operations with id
class section_id(Resource):
    @auth_token_required
    @roles_accepted('admin', 'user')
    @cache.cached(timeout=10)
    def get(self, section_id):
        section = Section.query.get(section_id)
        section_info = {}
        if not section:
            return make_response(jsonify({'message': 'Section not found'}), 400)
        section_info = {
            'id': section.id,
            'name': section.name,
            'description': section.description
        }
        return make_response(jsonify(section_info), 200)
    
    @auth_token_required
    @roles_accepted('admin')
    def put(self, section_id):
        data = request.get_json()
        name = data['name']
        description = data['description']
        section = Section.query.get(section_id)
        if not section:
            return make_response(jsonify({'message': 'Section not found'}), 400)
        if name is not None:
            section.name = name
        if description is not None:
            section.description = description
        db.session.commit()
        return make_response(jsonify({'message': 'Section updated successfully'}), 200)
    
    @auth_token_required
    @roles_accepted('admin')
    def delete(self, section_id):
        section = Section.query.get(section_id)
        if not section:
            return make_response(jsonify({'message': 'Section not found'}), 400)

        # Delete all books associated with the section
        books = Book.query.filter_by(section_id=section_id).all()
        for book in books:
            # Delete all issued records for the book
            issued_records = bookissue.query.filter_by(book_id=book.id).all()
            for record in issued_records:
                db.session.delete(record)

            # Delete the book
            db.session.delete(book)

        # Delete the section
        db.session.delete(section)
        db.session.commit()
        return make_response(jsonify({'message': 'Section and associated books/records deleted successfully'}), 200)
    

#Search section by text in name
class section_search(Resource):
    @auth_token_required
    @roles_accepted('admin', 'user')
    def post(self):
        data = request.get_json()
        section_name = data['section_name']
        sections = Section.query.filter(Section.name.ilike(f"%{section_name}%")).all()
        section_info = []
        for section in sections:
            section_info_temp = {
                'id': section.id,
                'name': section.name,
                'description': section.description,
            }
            section_info.append(section_info_temp)
        return make_response(jsonify(section_info), 200)