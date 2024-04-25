from flask_security import Security, SQLAlchemyUserDatastore, login_user, roles_accepted, current_user, logout_user, auth_token_required
from models import *
import bcrypt
# from flask import current_app as app

user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security=Security()