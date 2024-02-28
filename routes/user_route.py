from app import create_app, db
from flask import request, jsonify
from app.models import User
from schemas.user_schema import UserSchema
from app.utils import api_handler
from flask_restx import Api, Resource, fields
import jwt
from settings import settings
from app.tasks import celery_send_email

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = create_app()

limiter = Limiter(get_remote_address, app=app, default_limits=["200 per day", "50 per hour"])

api = Api(app=app, 
        version='1.0', 
        title='User API', 
        description='A simple User API', 
        prefix='/api/v1',
        doc='/docs')


@api.route('/register', '/verify')
class UserAPI(Resource):
    """Resource for user registration and verification."""
    
    @api.expect(api.model('register', {'username': fields.String(), 'email': fields.String(), 'password': fields.String(), 'location': fields.String()}))
    @api_handler(body=UserSchema)
    @limiter.limit("5 per minute")
    def post(self):
        """Register a new user.
        
        Description:
        This endpoint registers a new user by creating a User object with provided data, adding it to the database, and sending a verification email.

        Parameter:
        None
        
        Return:
        dict: A dictionary containing a success message, user data, and verification token with HTTP status code 201.
        """

        data = request.get_json()
        user = User(**data)
        db.session.add(user)
        db.session.commit()
        token = jwt.encode({"user_id": user.id}, settings.jwt_key, algorithm=settings.jwt_algo)
        celery_send_email.delay(user.username, user.email, token, "Welcome to Fundoo Notes! Verify Your Email to Get Started", f'''
Dear {user},

Welcome to Fundoo_Notes! We're thrilled to have you as part of our community. To get started, please verify your email address by entering the following verification token within the website:

Verification Link: {f'{settings.user_uri}/api/verify?token={token}'}

This verification step ensures the security of your account and helps us keep our community safe. If you didn't create an account with Fundoo_Notes, please ignore this email.

Thank you for choosing Fundoo_Notes! If you have any questions or need assistance, feel free to reach out to our support team at 17.atharva@gmail.com.

Best regards,
Fundoo_Notes Team''')
        db.session.refresh(user)
        db.session.close()
        return {"message": "User registered successfully", "status": 201, "data": user.to_json, 'token': token}, 201


    @api_handler()
    @limiter.limit("5 per minute")
    def delete(self, id):
        """Delete a user.
        
        Description:
        This endpoint deletes a user from the database based on the provided user ID.

        Parameter:
        id (int): The ID of the user to be deleted.

        Return:
        dict: A dictionary containing a success message or a user not found message with HTTP status code 200 or 404, respectively.
        """
        user = User.query.filter_by(id=id).first()
        if user:
            db.session.delete(user)
            db.session.commit()
            db.session.close()
            return jsonify({"message": "User deleted successfully"})
        return jsonify({"message": "User not found"})

    @api.doc(params={'token': "Give token"})
    @api_handler()
    @limiter.limit("5 per minute")
    def get(self):
        """Verify user.
        
        Description:
        This endpoint verifies a user based on the provided verification token.

        Parameter:
        token (str): The verification token sent to the user's email.

        Return:
        dict: A dictionary containing a success message, or a user not found message with HTTP status code 200 or 404, respectively.
        """
        token = request.args.get('token')
        if not token:
            return {'message': 'Token not found', 'status': 404}, 404
        user_id = jwt.decode(token, settings.jwt_key, algorithms=[settings.jwt_algo])["user_id"]
        user = User.query.filter_by(id=user_id).first()
        if not user:
            return {'message': 'user not found', 'status': 404}, 404
        user.is_verified = True
        db.session.commit()
        return {'message': "user verified successfully", 'status': 200}

@api.route('/login')
class LoginAPI(Resource):
    """Resource for user login."""
    
    @api.expect(api.model('login', {'username': fields.String(), 'password': fields.String()}))
    @api_handler()
    @limiter.limit("5 per minute")
    def post(self):
        """Authenticate user.
        
        Description:
        This endpoint authenticates a user based on the provided username and password.

        Parameter:
        None
        
        Return:
        dict: A dictionary containing a success message and an authentication token with HTTP status code 200, or an invalid credentials message with HTTP status code 401.
        """
        data = request.get_json()
        user = User.query.filter_by(username=data['username']).first()
        if user and user.verify_password(data['password']):
            return {"message": "Login successful", "token": user.generate_token(aud="login", exp=60), "status": 200}, 200
        return {"message": "Invalid credentials", "status": 401}, 401