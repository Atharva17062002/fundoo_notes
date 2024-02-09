
from app import create_app, db
from flask import request, jsonify
from app.models import User
from schemas.user_schema import UserSchema
from app.utils import api_handler

app = create_app()

@app.post('/register')
@api_handler(body=UserSchema)
def register():
    data = request.get_json()
    user = User(**data)
    db.session.add(user)
    db.session.commit()
    db.session.refresh(user)
    db.session.close()
    return jsonify({"message": "User registered successfully","status":201,
    "data":user.to_json}), 201

@app.get('/login')
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()
    if user and user.password == data['password']:
        return jsonify({"message": "Login successful"})
    return jsonify({"message": "Invalid credentials"})
