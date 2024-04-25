from flask import Flask, request, jsonify, make_response
from models import *
# from flask_security import Security, SQLAlchemyUserDatastore, login_user, roles_accepted, current_user, logout_user, auth_token_required
from security_framework import login_user, roles_accepted, current_user, logout_user, security, user_datastore
import bcrypt
import secrets
from flask_cors import CORS
from flask_restful import Api
from celery_files.worker import celery_init_app
import flask_excel as excel
from celery import Celery
from celery.schedules import crontab
from celery_files.tasks import daily_reminder, monthly_report
from datetime import datetime, date
from sqlalchemy import func
from redis_caching.instances import cache

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///./library_management_db.sqlite3'
app.config['SECRET_KEY']='super-secret'
app.config['SECURITY_PASSWORD_HASH'] = 'bcrypt'
app.config['SECURITY_PASSWORD_SALT'] = secrets.SystemRandom().getrandbits(128)
app.config['SECURITY_TRACKABLE'] = True
app.config['SECURITY_PERMISSIONS'] = False
app.config['SMTP_SERVER'] = 'localhost'
app.config['SMTP_PORT'] = 1025
app.config['SENDER_EMAIL'] = 'siddhant@mantri.com'
app.config['SENDER_PASSWORD'] = ''
app.config['CACHE_TYPE'] = 'RedisCache'
app.config['CACHE_DEFAULT_TIMEOUT'] = 300
app.config['CACHE_REDIS_HOST'] = 'localhost'
app.config['CACHE_REDIS_PORT'] = 6379
app.config['CACHE_REDIS_DB'] = 3


app.config['SECURITY_TOKEN_AUTHENTICATION_HEADER'] = 'Authorization'

api = Api(app)
app.app_context().push()


db.init_app(app)
app.app_context().push()

cache.init_app(app)

CORS(app)

celery_app = celery_init_app(app)

excel.init_excel(app)

# user_datastore = SQLAlchemyUserDatastore(db, User, Role)
# security=Security(app, user_datastore)

security.init_app(app, user_datastore)

# Function to create roles
def create_roles():
    # Define roles and their permissions
    roles_permissions = {
        'admin': 'admin-access',
        'user': 'user-access',
    }
    # Iterate over each role
    for role_name, role_permissions in roles_permissions.items():
        # Check if the role already exists
        role = Role.query.filter_by(name=role_name).first()
        # If the role does not exist, create it
        if not role:
            role = Role(name=role_name, description=role_permissions)
            # Add the new role to the session
            db.session.add(role)
    # Commit the session to save the changes
    db.session.commit()


# Function to create an admin user
def admin_user_creation():
    # Get the admin role
    admin_role = Role.query.filter_by(name='admin').first()
    # Check if there is already a user with the admin role
    admin_user = User.query.filter(User.roles.any(id=admin_role.id)).first()

    # If there is no admin user, create one
    if not admin_user:
        # Define the admin email and password
        admin_email = 'admin@abc.com'  # Change this email as needed
        admin_password = 'admin'
        # Hash the password
        hashed_password = bcrypt.hashpw(admin_password.encode('utf-8'), bcrypt.gensalt())

        # Create the admin user
        admin_user = user_datastore.create_user(email=admin_email, password=hashed_password)
        # Add the admin role to the user
        user_datastore.add_role_to_user(admin_user, 'admin')
        # user_datastore.add_role_to_user(genral_user, 'user')

        # Commit the session to save the changes
        db.session.commit()
        return True
    return False


from routes.auth import *
api.add_resource(register, '/api/register')
api.add_resource(login, '/api/login')
api.add_resource(logout, '/api/logout')
api.add_resource(update_user, '/api/update_user/<int:user_id>')
api.add_resource(delete_user, '/api/delete_user/<int:user_id>')
api.add_resource(get_user, '/api/get_user/<int:user_id>')
api.add_resource(get_all_users, '/api/get_all_users')

from routes.section import *
api.add_resource(section, '/api/section')
api.add_resource(section_id, '/api/section/<int:section_id>')
api.add_resource(section_search, '/api/section_search')


from routes.book import *
api.add_resource(book, '/api/books')
api.add_resource(book_id, '/api/books/<int:book_id>')
api.add_resource(issue_book, '/api/issue_book')
api.add_resource(return_book, '/api/return_book')
api.add_resource(book_search, '/api/book_search/<string:book_name>')
api.add_resource(book_issue_status, '/api/book_issue_status')
api.add_resource(issued_books, '/api/issued_books/<int:user_id>')
api.add_resource(search_book_by_author, '/api/search_book_by_author')
api.add_resource(all_issued_books, '/api/all_issued_books')

from routes.feedback import *
api.add_resource(feedback, '/api/feedback')
api.add_resource(feedback_by_bookid, '/api/feedback_by_bookid')
api.add_resource(feedback_by_userid, '/api/feedback_by_userid')
api.add_resource(feedback_by_userid_bookid, '/api/feedback_by_userid_bookid')


@celery_app.on_after_configure.connect
def send_tasks(sender, **kwargs):
    # Schedule the daily reminder task
    sender.add_periodic_task(
        crontab(hour=12, minute=30),
        daily_reminder.s('please login to the application.'),
    )

    # Schedule the monthly report task
    sender.add_periodic_task(
        crontab(hour=12, minute=30, day_of_month=1),
        monthly_report.s(),
    )


if __name__ == '__main__':
    db.create_all()
    create_roles()
    admin_user_creation()
    app.run(debug=True)