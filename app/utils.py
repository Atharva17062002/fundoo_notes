from pydantic import ValidationError
from flask import request
from flask_mail import Message
from settings import settings
import jwt
import json
from . import mail
import redis

def api_handler(body = None, query = None):
    def custom_validator(function):
        def wrapper(*args, **kwargs):
            try:
                if body:
                    body(**request.get_json())
                if query:
                    pass
                return function(*args, **kwargs)
            except ValidationError as e:
                return {"message": json.loads(e.json()),"status": 400,"data":{}},400
            except Exception as e:
                return {"message": str(e),"status": 400,"data":{}},400
        wrapper.__name__ = function.__name__
        return wrapper
    custom_validator.__name__ = api_handler.__name__
    return custom_validator


class JWT:

    key = settings.jwt_key
    algorithm = settings.jwt_algo

    @classmethod
    def to_encode(cls,payload):
        encoded = jwt.encode(payload,cls.key,algorithm= cls.algorithm)
        return encoded
    
    @classmethod
    def to_decode(cls,encoded,aud):
        decoded = jwt.decode(encoded,cls.key,algorithms= [cls.algorithm],audience= aud)
        return decoded

    
def send_mail(user,email,token):
    msg= Message("Welcome to Fundoo Notes! Verify Your Email to Get Started", sender = f"{settings.sender}", recipients=[email])

    msg.body = f'''

Dear {user},

Welcome to Fundoo_Notes! We're thrilled to have you as part of our community. To get started, please verify your email address by entering the following verification token within the website:

Verification Link: {f'{settings.base_uri}/api/verify?token={token}'}

This verification step ensures the security of your account and helps us keep our community safe. If you didn't create an account with Fundoo_Notes, please ignore this email.

Thank you for choosing Fundoo_Notes! If you have any questions or need assistance, feel free to reach out to our support team at 17.atharva@gmail.com.

Best regards,
Fundoo_Notes Team'''
    mail.send(msg)

class RedisManager:
    redis_client = redis.StrictRedis(host=settings.redis_host, port=settings.redis_port, db=settings.redis_db)
    
    @classmethod
    def save(cls, key, field, value):
        cls.redis_client.hset(key, field, value)

    @classmethod
    def get(cls,key):
        return cls.redis_client.hgetall(key)

    @classmethod
    def delete(cls,key,field):
        cls.redis_client.hdel(key, field)



