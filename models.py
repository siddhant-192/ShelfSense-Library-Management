from flask_sqlalchemy import *
from sqlalchemy.orm import relationship, backref
from flask_security import UserMixin
from datetime import datetime

db = SQLAlchemy()

#table for role id against the user id
class UserRoles(db.Model):
    __tablename__ = 'user_roles'
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column('user_id', db.Integer(), db.ForeignKey('user.id'))
    role_id = db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))


#table for the available roles
class Role(db.Model):
    __tablename__ = 'role'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

    def get_permissions(self):
        # Return a list of permissions for this role
        # For example, you could return a list of strings representing the permissions
        return [self.description]


#table for the user
class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    username = db.Column(db.String(255), unique=True, nullable=True)
    password = db.Column(db.String(255), nullable=False)
    confirmed_at = db.Column(db.DateTime())
    last_login_at = db.Column(db.DateTime())  # Add column for last login date
    current_login_at = db.Column(db.DateTime())  # Add column for current login date
    last_login_ip = db.Column(db.String(100))  # Add column for last login IP address
    current_login_ip = db.Column(db.String(100))  # Add column for current login IP address
    login_count = db.Column(db.Integer)  # Add column for total login count
    active = db.Column(db.Boolean())
    fs_uniquifier = db.Column(db.String(64), unique=True, nullable=False)
    roles = relationship('Role', secondary='user_roles',
                         backref=backref('users', lazy='dynamic')) # required
    
    def __init__(self, email, password, active=True, roles=None, **kwargs):
        super().__init__(**kwargs)
        self.email = email
        self.password = password
        self.active = active

        user_role = Role.query.filter_by(name='user').first()

        if roles is None:
            self.roles=[user_role]
        else:
            self.roles = []


#table for section
class Section(db.Model):
    __tablename__ = 'section'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    description = db.Column(db.String())

    def search(self):
        return {
            'id': self.id,
            'name': self.name,
            'date_created': self.date_created,
            'description': self.description
        }
    

#table for book
class Book(db.Model):
    __tablename__ = 'book'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text())
    authors = db.Column(db.String())
    issue_status = db.Column(db.Boolean, default=False)  # Add the issue_status column

    section_id = db.Column(db.Integer, db.ForeignKey('section.id'))

    def search(self):
        return {
            'id': self.id,
            'name': self.name,
            'content': self.content,
            'authors': self.authors,
            'section_id': self.section_id
        }
    
#table for book issue tracking
class bookissue(db.Model):
    __tablename__ = 'book_issues'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    date_issued = db.Column(db.DateTime, default=datetime.utcnow)
    return_date = db.Column(db.DateTime)

    def search(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'book_id': self.book_id,
            'date_issued': self.date_issued,
            'return_date': self.return_date
        }

#table for user feedback of books
class feedbackTable(db.Model):
    __tablename__ = 'feedbackTable'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    feedback = db.Column(db.Text())
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def search(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'book_id': self.book_id,
            'feedback': self.feedback,
            'date_created': self.date_created
        }