from app import db, create_app
from app.models import Label
from flask import request
from flask_restx import Api, Resource, fields
from app.utils import api_handler, RedisManager,api_handler
from schemas.notes_schema import NotesSchema
import jwt
from app.middleware import auth_user
import json

app = create_app()

api = Api(app=app, version='1.0', title='Labels API', description='Notes API',security='apikey',authorizations={
    'apikey': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization',
        'required': True
    }
},doc= '/docs')

@api.route('/labels')

class LabelsApi(Resource):
    method_decorators = [auth_user]

    @api_handler()
    def get(self, *args, **kwargs):
        labels = Label.query.filter_by(**kwargs).all()
        return {"message": "Data retrieved successfully from database", "status":200,'data': [label.to_json() for label in labels]}, 200

    @api.expect(api.model('createLabel', {"name":fields.String()}))
    @api_handler()
    def post(self,*args, **kwargs):
        data = request.get_json()
        label = Label(**data)
        db.session.add(label)
        db.session.commit()
        return {"message": "Label created successfully","status":201,"data":label.to_json()}, 201

    @api_handler
    @api.doc(params={'label_id': "Label Id"})
    def delete(self, *args, **kwargs):
        label = Label.query.filter_by(id=request.args.get('label_id'), **kwargs).first()
        if label:
            db.session.delete(label)
            db.session.commit()
            db.session.close()
            return {"message": "Label deleted successfully","status":200}, 200
        return {"message": "Label not found", "status":404}, 404


    @api_handler()
    @api.expect(api.model('updateLabel', {"id": fields.Integer(), "name": fields.String()}))
    def put(self, *args, **kwargs):
        data = request.get_json()
        label = Label.query.filter_by(id=data['id']).first()
        [setattr(label, key, value) for key, value in data.items()]
        db.session.commit()
        return {"message": "Label updated successfully","status":201,"data":label.to_json()}, 201

   