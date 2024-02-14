from flask import request
from .models import User
import jwt
from.utils import JWT

def auth_user(func):
    def wrapper(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return {"message": "Token not found","status":404,"data":{}}, 404
        try:
            data = JWT.to_decode(token,'login')
            user = User.query.filter_by(id=data['user_id']).first()
            if not user:
                return {"message": "User not found","status":404,"data":{}}, 404
            request.json.update({"user_id":user.id}) if request.method in ['POST', 'PUT'] else kwargs.update({"user_id":user.id})
        except jwt.PyJWTError:
            return {"message": "Invalid Token", "status":401, "data":{}}, 401
        except Exception as e:
            return {"message": str(e), "status":400, "data":{}}, 400
        return func(*args, **kwargs) 

    wrapper.__name__ = func.__name__
    return wrapper