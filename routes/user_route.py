from app import create_app, db
from flask import request, jsonify
from app.models import User
from schemas.user_schema import UserSchema
from app.utils import api_handler
from flask_restx import Api, Resource
# from app.utils import send_mail
import jwt
from settings import settings
from app.tasks import celery_send_email

app = create_app()
api = Api(app=app, 
        version='1.0', 
        title='User API', 
        description='A simple User API', 
        prefix = '/api/v1')


@api.route('/user', '/user/<int:id>', '/verify')
class UserAPI(Resource):

    @api_handler(body=UserSchema)
    def post(self):
        data = request.get_json()
        user = User(**data)
        db.session.add(user)
        db.session.commit()
        token = jwt.encode({"user_id": user.id}, settings.jwt_key, algorithm=settings.jwt_algo)
        # send_mail(user.username,user.email,token)
        celery_send_email.delay(user.username,user.email,token,"Welcome to Fundoo Notes! Verify Your Email to Get Started",f'''

Dear {user},

Welcome to Fundoo_Notes! We're thrilled to have you as part of our community. To get started, please verify your email address by entering the following verification token within the website:

Verification Link: {f'{settings.user_uri}/api/verify?token={token}'}

This verification step ensures the security of your account and helps us keep our community safe. If you didn't create an account with Fundoo_Notes, please ignore this email.

Thank you for choosing Fundoo_Notes! If you have any questions or need assistance, feel free to reach out to our support team at 17.atharva@gmail.com.

Best regards,
Fundoo_Notes Team''')
        db.session.refresh(user)
        db.session.close()
        return {"message": "User registered successfully","status":201,"data":user.to_json}, 201

    def delete(self, id):
        user = User.query.filter_by(id=id).first()
        if user:
            db.session.delete(user)
            db.session.commit()
            db.session.close()
            return jsonify({"message": "User deleted successfully"})
        return jsonify({"message": "User not found"})

    def get(self):
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

    def post(self):
        data = request.get_json()
        user = User.query.filter_by(username=data['username']).first()
        if user and user.verify_password(data['password']):
            return jsonify({"message":"Login successful","token": user.generate_token(aud = "login",exp = 60)})
        return jsonify({"message": "Invalid credentials"})
