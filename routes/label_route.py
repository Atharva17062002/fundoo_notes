from app import db, create_app
from app.models import Label
from flask import request
from flask_restx import Api, Resource
from app.utils import api_handler, RedisManager
from schemas.notes_schema import NotesSchema
import jwt
from app.middleware import auth_user
import json

app = create_app()

api = Api(app=app, version='1.0', title='Notes API', description='Notes API')

@api.route('/labels', '/labels/<string:name>')

class LabelsApi(Resource):
    method_decorators = [auth_user]

    def get(self, *args, **kwargs):
        labels = Label.query.filter_by(**kwargs).all()
        return {"message": "Data retrieved successfully from database", "status":200,'data': [label.to_json() for label in labels]}, 200

    def post(self,*args, **kwargs):
        data = request.get_json()
        label = Label(**data)
        db.session.add(label)
        db.session.commit()
        return {"message": "Label created successfully","status":201,"data":label.to_json()}, 201

    def delete(self, *args, **kwargs):
        label = Label.query.filter_by(**kwargs).first()
        if label:
            db.session.delete(label)
            db.session.commit()
            db.session.close()
            return {"message": "Label deleted successfully","status":200}, 200
        return {"message": "Label not found", "status":404}, 404
    
    def put(self, *args, **kwargs):
        data = request.get_json()
        label = Label.query.filter_by(**kwargs).first()
        [setattr(label, key, value) for key, value in data.items()]
        db.session.commit()
        return {"message": "Label updated successfully","status":201,"data":label.to_json()}, 201

   