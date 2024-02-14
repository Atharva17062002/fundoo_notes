from app import db, create_app
from app.models import Notes
from flask import request
from flask_restx import Api, Resource
from app.utils import api_handler
from schemas.notes_schema import NotesSchema
import jwt

app = create_app()

api = Api(app=app, version='1.0', title='Notes API', description='Notes API')
@api.route('/notes', '/notes/<int:user_id>','/notes/<int:user_id>/<int:note_id>')
class NotesApi(Resource):

    def get(self,user_id):
        notes = Notes.query.filter_by(user_id=user_id).all()
        return notes

    @api_handler(body=NotesSchema)
    def post(self):
        data  = request.get_json()
        notes = Notes(**data)
        db.session.add(notes)
        db.session.commit()
        # db.session.close()
        return {"message": "Notes added successfully","status":201,"data":notes.to_json()}, 201

    def delete(self, user_id,note_id):
        notes = Notes.query.filter_by(user_id=user_id, id = note_id).first()
        
        db.session.delete(notes)
        db.session.commit()
        # db.session.close()
        return {"message": "Notes deleted successfully","status":201,"data":notes.to_json()}, 201

    def put(self, user_id,note_id):
        notes = Notes.query.filter_by(user_id=user_id,id = note_id).first()
        data  = request.get_json()
        [setattr(notes, key, value) for key, value in data.items()]
        # notes.title = data['title']
        # notes.description = data['description']
        # notes.color = data['color']
        # notes.reminder = data['reminder']
        db.session.commit()
        # db.session.close()
        return {"message": "Notes updated successfully","status":201,"data":notes.to_json()}, 201
    

