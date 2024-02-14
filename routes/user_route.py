from app import create_app, db
from flask import request, jsonify
from app.models import User
from schemas.user_schema import UserSchema
from app.utils import api_handler
from flask_restx import Api, Resource
from app.utils import send_mail
import jwt
from settings import settings

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
        send_mail(user.username,user.email,token)
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
            return jsonify({"message": "Login successful"})
        return jsonify({"message": "Invalid credentials"})


