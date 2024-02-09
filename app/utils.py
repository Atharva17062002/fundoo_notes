from pydantic import ValidationError
from flask import request
import json

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


