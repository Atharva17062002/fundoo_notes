from app import db, create_app
from app.models import Notes, User
from flask import request
from flask_restx import Api, Resource, fields
from app.utils import api_handler, RedisManager
from schemas.notes_schema import NotesSchema
from redbeat import RedBeatSchedulerEntry as Task
from celery.schedules import crontab
from app.middleware import auth_user

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = create_app()

limiter = Limiter(get_remote_address, app=app, default_limits=["200 per day", "50 per hour"])

api = Api(app=app, version='1.0', title='Notes API', description='Notes API', security='apikey', authorizations={
    'apikey': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization',
        'required': True
    }
}, doc='/docs', prefix='/api/v1')

@api.route('/notes')
class NotesApi(Resource):
    """Resource for managing notes."""

    method_decorators = [auth_user]

    @api_handler()
    @limiter.limit("5 per minute")
    def get(self, *args, **kwargs):
        """Retrieve notes.

        Description:
        This endpoint retrieves notes either from Redis cache or from the database based on the provided user ID.

        Parameter:
        kwargs (dict): Keyword arguments containing user ID.

        Return:
        dict: A dictionary containing the retrieved notes with an HTTP status code.
        """

        # Fetch notes from Redis if available
        red = RedisManager.get(f'user_{kwargs["user_id"]}')
        user = User.query.filter_by(id=kwargs['user_id']).first()
        shared_notes = [note.to_json() for note in user.c_notes]

        if red:
            red = [json.loads(note) for note in red.values()]
            cache = list(filter(lambda note: not note['is_archived'] and not note['is_trash'], red))
            shared_notes.extend(cache)
            return {'message': "Data retrieved successfully from redis", "status": 200, "data": shared_notes}

        notes = Notes.query.filter_by(**kwargs).all()
        all_notes = [note.to_json() for note in notes]
        all_notes.extend(shared_notes)
        return {"message": "Data retrieved successfully from database", "status": 200, 'data': all_notes}

    @api.expect(api.model('Addnotes', {"title": fields.String(), "description": fields.String(), "color": fields.String(), "reminder": fields.String()}))
    @api_handler(body=NotesSchema)
    @limiter.limit("5 per minute")
    def post(self):
        """Add a new note.

        Description:
        This endpoint adds a new note to the database and schedules a reminder task if provided.

        Parameter:
        None

        Return:
        dict: A dictionary containing a success message, the added note data, and an HTTP status code.
        """

        data = request.get_json()
        notes = Notes(**data)
        db.session.add(notes)
        db.session.commit()

        # Schedule reminder if provided
        reminder = notes.reminder
        if reminder:
            date, _time = data['reminder'].split("T")
            date = date.split("-")
            _time = _time.split(":")
            reminder_task = Task(
                name=f'user_{notes.user_id}-note_{notes.id}',
                task='app.tasks.celery_send_email',
                schedule=crontab(
                    minute=_time[1],
                    hour=_time[0],
                    day_of_month=date[2],
                    month_of_year=date[1]
                ),
                app=c_app,
                args=[notes.user.username, notes.user.email, "Hello world"]
            )
            reminder_task.save()

        # Store in Redis
        RedisManager.save(f'user_{notes.user_id}', f'note_{notes.id}', json.dumps(notes.to_json()))
        db.session.close()
        return {"message": "Notes added successfully", "status": 201, "data": notes.to_json()}, 201

    @api_handler()
    @limiter.limit("5 per minute")
    def delete(self, *args, **kwargs):
        """Delete a note.

        Description:
        This endpoint deletes a note from the database based on the provided note ID.

        Parameter:
        kwargs (dict): Keyword arguments containing note ID.

        Return:
        dict: A dictionary containing a success message or a user not found message with HTTP status code 200 or 404, respectively.
        """

        note_id = request.args.get('note_id')
        if not note_id:
            return {"message": "Please provide note id", "status": 400, "data": {}}, 400
        notes = Notes.query.filter_by(id=int(note_id), **kwargs).first()
        RedisManager.delete(f'user_{notes.user_id}', f'note_{notes.id}')
        db.session.delete(notes)
        db.session.commit()
        return {"message": "Notes deleted successfully", "status": 200}, 200

    @api.expect(api.model('Updatenotes', {"id": fields.Integer(), "title": fields.String(), "description": fields.String(), "color": fields.String()}))
    @api_handler()
    @limiter.limit("5 per minute")
    def put(self, *args, **kwargs):
        """Update a note.

        Description:
        This endpoint updates a note in the database based on the provided note ID and user ID.

        Parameter:
        kwargs (dict): Keyword arguments containing note ID and user ID.

        Return:
        dict: A dictionary containing a success message, updated note data, and an HTTP status code.
        """

        data = request.get_json()
        note = Notes.query.filter_by(id=data['id'], user_id=data['user_id']).first()
        [setattr(note, key, value) for key, value in data.items()]
        RedisManager.save(f'user_{note.user_id}', f'note_{note.id}', json.dumps(note.to_json()))
        db.session.commit()
        return {"message": "Notes updated successfully", "status": 200, "data": note.to_json()}, 200

@api.route('/notes/archived')
class NoteArchived(Resource):
    """Resource for managing archived notes."""

    method_decorators = [auth_user]

    @api_handler()
    @limiter.limit("5 per minute")
    def put(self, *args, **kwargs):
        """Archive a note.

        Description:
        This endpoint archives a note in the database based on the provided note ID and user ID.

        Parameter:
        kwargs (dict): Keyword arguments containing note ID and user ID.

        Return:
        dict: A dictionary containing a success message, updated note data, and an HTTP status code.
        """

        data = request.get_json()
        note = Notes.query.filter_by(id=data['id'], user_id=data['user_id']).first()
        note.is_archived = not note.is_archived
        db.session.commit()
        RedisManager.save(f'user_{note.user_id}', f'note_{note.id}', json.dumps(note.to_json()))
        return {"message": "Note archived successfully", "status": 200, "data": note.to_json()}, 200

    @api_handler()
    @limiter.limit("5 per minute")
    def get(self, *args, **kwargs):
        """Retrieve archived notes.

        Description:
        This endpoint retrieves archived notes from the database based on the provided user ID.

        Parameter:
        kwargs (dict): Keyword arguments containing user ID.

        Return:
        dict: A dictionary containing the retrieved archived notes with an HTTP status code.
        """

        notes = Notes.query.filter_by(user_id=kwargs['user_id'], is_archived=True, is_trash=False).all()
        return {"message": "Note archived retrieved successfully", "status": 200, "data": [note.to_json() for note in notes]}, 200

@api.route('/notes/trash')
class NoteTrash(Resource):
    """Resource for managing trashed notes."""

    method_decorators = [auth_user]

    @api_handler()
    @limiter.limit("5 per minute")
    def put(self, *args, **kwargs):
        """Trash a note.

        Description:
        This endpoint trashes a note in the database based on the provided note ID and user ID.

        Parameter:
        kwargs (dict): Keyword arguments containing note ID and user ID.

        Return:
        dict: A dictionary containing a success message, updated note data, and an HTTP status code.
        """

        data = request.get_json()
        note = Notes.query.filter_by(id=data['id'], user_id=data['user_id']).first()
        note.is_trash = not note.is_trash
        db.session.commit()
        RedisManager.save(f'user_{note.user_id}', f'note_{note.id}', json.dumps(note.to_json()))
        return {"message": "Note trashed successfully", "status": 200, "data": note.to_json()}, 200

    @api_handler()
    @limiter.limit("5 per minute")
    def get(self, *args, **kwargs):
        """Retrieve trashed notes.

        Description:
        This endpoint retrieves trashed notes from the database based on the provided user ID.

        Parameter:
        kwargs (dict): Keyword arguments containing user ID.

        Return:
        dict: A dictionary containing the retrieved trashed notes with an HTTP status code.
        """

        notes = Notes.query.filter_by(user_id=kwargs['user_id'], is_trash=True, is_archived=False).all()
        return {"message": "Note trashed retrieved successfully", "status": 200, "data": [note.to_json() for note in notes]}, 200

@api.route('/notes/collab')
class NoteCollaborator(Resource):
    """Resource for managing note collaborators."""

    method_decorators = [auth_user]

    @api_handler()
    @limiter.limit("5 per minute")
    def post(self):
        """Add a collaborator to a note.

        Description:
        This endpoint adds a collaborator to a note in the database based on the provided note ID and user ID.

        Parameter:
        None

        Return:
        dict: A dictionary containing a success message, updated note data, and an HTTP status code.
        """

        try:
            data = request.get_json()
            if data['user_id'] in data['user_ids']:
                return {"message": "User is already a collaborator", "status": 403}, 403
            note = Notes.query.filter_by(id=data['id'], user_id=data['user_id']).first()
            if not note:
                return {"message": "Note not found", "status": 404}, 404
            note.c_users.extend([User.query.filter_by(id=id).first() for id in data['user_ids']])
            db.session.commit()
            RedisManager.save(f'user_{note.user_id}', f'note_{note.id}', json.dumps(note.to_json()))
            return {"message": "Note collaborator added successfully", "status": 200, "data": note.to_json()}, 200
        except Exception as e:
            return {"message": str(e), "status": 500}, 500

    @api_handler()
    @limiter.limit("5 per minute")
    def delete(self, *args, **kwargs):
        """Remove a collaborator from a note.

        Description:
        This endpoint removes a collaborator from a note in the database based on the provided note ID and user ID.

        Parameter:
        kwargs (dict): Keyword arguments containing user ID.

        Return:
        dict: A dictionary containing a success message, updated note data, and an HTTP status code.
        """

        try:
            data = request.get_json()
            note = Notes.query.filter_by(id=data['id'], user_id=kwargs['user_id']).first()
            if not note:
                return {"message": "Note not found", "status": 404}, 404
            [note.c_users.remove(user) for user in [User.query.filter_by(id=id).first() for id in data['user_ids']]]
            db.session.commit()
            return {"message": "Note collaborator removed successfully", "status": 200, "data": note.to_json()}, 200
        except Exception as e:
            return {"message": str(e), "status": 500}, 500