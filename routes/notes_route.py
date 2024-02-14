from app import db, create_app
from app.models import Notes
from flask import request
from flask_restx import Api, Resource
from app.utils import api_handler
from schemas.notes_schema import NotesSchema
import jwt
from app.middleware import auth_user

app = create_app()

api = Api(app=app, version='1.0', title='Notes API', description='Notes API')
@api.route('/notes', '/notes/<int:id>')
class NotesApi(Resource):

    method_decorators = [auth_user]

    @api_handler()
    def get(self, *args, **kwargs):
        print(kwargs)
        notes = Notes.query.filter_by(**kwargs).all()
        return {'data': [note.to_json() for note in notes]}

    @api_handler(body=NotesSchema)
    def post(self):
        data  = request.get_json()
        notes = Notes(**data)
        db.session.add(notes)
        db.session.commit()
        # db.session.close()
        return {"message": "Notes added successfully","status":201,"data":notes.to_json()}, 201

    def delete(self, *args, **kwargs):
        notes = Notes.query.filter_by(**kwargs).first()
        db.session.delete(notes)
        db.session.commit()
        # db.session.close()
        return {"message": "Notes deleted successfully","status":201,"data":notes.to_json()}, 201

    api_handler()
    def put(self, *args, **kwargs):
        data  = request.get_json()
        note = Notes.query.filter_by(id=data['id'], user_id=data['user_id']).first()
        [setattr(note, key, value) for key, value in data.items()]
        # notes.title = data['title']
        # notes.description = data['description']
        # notes.color = data['color']
        # notes.reminder = data['reminder']
        db.session.commit()
        # db.session.close()
        return {"message": "Notes updated successfully","status":201,"data":note.to_json()}, 201
    

