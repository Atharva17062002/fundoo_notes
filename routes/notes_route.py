from app import db, create_app
from app.models import Notes, User
from flask import request
from flask_restx import Api, Resource
from app.utils import api_handler, RedisManager
from schemas.notes_schema import NotesSchema
import jwt
from app.middleware import auth_user
import json
from redbeat import RedBeatSchedulerEntry as Task
from celery.schedules import crontab
from app.tasks import c_app
import celery


app = create_app()

api = Api(app=app, version='1.0', title='Notes API', description='Notes API')
@api.route('/notes', '/notes/<int:id>')
class NotesApi(Resource):

    method_decorators = [auth_user]

    @api_handler()
    def get(self, *args, **kwargs):
        red = RedisManager.get(f'user_{kwargs["user_id"]}')
        user = User.query.filter_by(id=kwargs['user_id']).first()
        shared_notes = [note.to_json() for note in user.c_notes]
        if red:
            red = [json.loads(note) for note in red.values()]
            cache = list(filter(lambda note: note['is_archived'] == False and note['is_trash'] == False, red))
            shared_notes.extend(cache)
            return {'message':"Data retrieved successfully from redis", "status":200,"data":shared_notes}
        notes = Notes.query.filter_by(**kwargs).all()
        all_notes = [note.to_json() for note in notes]
        all_notes.extend(shared_notes)
        print(user.c_notes)
        return {"message": "Data retrieved successfully from database", "status":200,'data': all_notes}

    @api_handler(body=NotesSchema)
    def post(self):
        data  = request.get_json()
        notes = Notes(**data)
        db.session.add(notes)
        db.session.commit()
        reminder = notes.reminder
        if reminder:
            date, _time = data['reminder'].split("T")
            date = date.split("-")
            _time = _time.split(":")

            reminder_task = Task(name=f'user_{notes.user_id}-note_{notes.id}',
                task='app.tasks.celery_send_email',
                schedule=crontab(
                    minute=_time[1],
                    hour=_time[0],
                    day_of_month=date[2],
                    month_of_year=date[1]
                ),
                app = c_app,                
                args= [notes.user.username, notes.user.email, "Hello world"])    
            reminder_task.save() 
        RedisManager.save(f'user_{notes.user_id}', f'note_{notes.id}', json.dumps(notes.to_json()))
        db.session.close()
        return {"message": "Notes added successfully","status":201,"data":notes.to_json()}, 201

    def delete(self, *args, **kwargs):
        notes = Notes.query.filter_by(**kwargs).first()
        RedisManager.delete(f'user_{notes.user_id}', f'note_{notes.id}')
        db.session.delete(notes)
        db.session.commit()
        return {"message": "Notes deleted successfully","status":200}, 200

    api_handler()
    def put(self, *args, **kwargs):
        data  = request.get_json()
        note = Notes.query.filter_by(id=data['id'], user_id=data['user_id']).first()
        [setattr(note, key, value) for key, value in data.items()]
        RedisManager.save(f'user_{note.user_id}', f'note_{note.id}',json.dumps(note.to_json()))
        # notes.title = data['title']
        # notes.description = data['description']
        # notes.color = data['color']
        # notes.reminder = data['reminder']
        db.session.commit()
        # db.session.close()
        return {"message": "Notes updated successfully","status":201,"data":note.to_json()}, 201

@api.route('/notes/archived', '/notes/archive/<int:id>')
class NoteArchived(Resource):
    method_decorators = [auth_user]

    def put(self, *args, **kwargs):
        data = request.get_json()
        note = Notes.query.filter_by(id=data['id'], user_id=data['user_id']).first()
        note.is_archived = True if not note.is_archived else False
        db.session.commit()
        RedisManager.save(f'user_{note.user_id}', f'note_{note.id}', json.dumps(note.to_json()))
        # db.session.close()
        return {"message": "Note archived successfully","status":200,"data":note.to_json()}, 200
    
    def get(self, *args, **kwargs):
        notes = Notes.query.filter_by(user_id=kwargs['user_id'], is_archived = True, is_trash=False).all()
        return {"message": "Note archived retrived successfully","status":200,"data":[note.to_json() for note in notes]}, 200

    
@api.route('/notes/trash', '/notes/trash/<int:id>')
class NoteTrash(Resource):
    method_decorators = [auth_user]

    def put(self, *args, **kwargs):
        data = request.get_json()
        note = Notes.query.filter_by(id=data['id'], user_id=data['user_id']).first()
        note.is_trash = True if not note.is_trash else False
        db.session.commit()
        RedisManager.save(f'user_{note.user_id}', f'note_{note.id}', json.dumps(note.to_json()))
        # db.session.close()
        return {"message": "Note trashed successfully","status":200,"data":note.to_json()}, 200
    
    def get(self, *args, **kwargs):
        notes = Notes.query.filter_by(user_id=kwargs['user_id'], is_trash = True, is_archived=False).all()
        return {"message": "Note trashed retrived successfully","status":200,"data":[note.to_json() for note in notes]}, 200

@api.route('/collab', '/collab')

class NoteCollaborator(Resource):
    method_decorators = [auth_user]

    def post(self):
        try:
            data = request.get_json()
            if(data['user_id'] in data['user_ids']):
                return {"message": "User is already a collaborator","status":403}, 403
            note = Notes.query.filter_by(id=data['id'], user_id=data['user_id']).first()
            if not note:
                return {"message": "Note not found","status":404}, 404
            note.c_users.extend([User.query.filter_by(id=id).first() for id in data['user_ids']])
            
            db.session.commit()
            RedisManager.save(f'user_{note.user_id}', f'note_{note.id}', json.dumps(note.to_json()))
            # db.session.close()
            return {"message": "Note collaborator added successfully","status":200,"data":note.to_json()}, 200
        except Exception as e:
            return {"message": e,"status":500}, 500

    def delete(self,*args, **kwargs):
        try:
            data = request.get_json()
            note = Notes.query.filter_by(id=data['id'], user_id=kwargs['user_id']).first()
            
            if not note:
                return {"message": "Note not found","status":404}, 404
            [note.c_users.remove(user) for user in [User.query.filter_by(id=id).first() for id in data['user_ids']]]
            db.session.commit()
            # RedisManager.save(f'user_{note.user_id}', f'note_{note.id}', json.dumps(note.to_json()))
            # db.session.close()
            return {"message": "Note collaborator removed successfully","status":200,"data":note.to_json()}, 200
        except Exception as e:
            return {"message": str(e),"status":500}, 500
