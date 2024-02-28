import pytest
from app import create_app,db
from flask_restx import Api
from routes import user_route, notes_route, label_route
from pathlib import Path
import os

@pytest.fixture

def test_app():
    path = Path(__file__).resolve().parent
    app = create_app("testing")
    with app.app_context():
        db.create_all()
    api = Api(app)
    api.add_resource(user_route.UserAPI, '/api/v1/register','/api/v1/verify')
    api.add_resource(user_route.LoginAPI, '/api/v1/login')
    api.add_resource(notes_route.NotesApi, '/api/v1/notes')
    api.add_resource(notes_route.NoteTrash, '/api/v1/notes/trash')
    api.add_resource(notes_route.NoteArchived, '/api/v1/notes/archived')
    api.add_resource(notes_route.NoteCollaborator, '/api/v1/notes/collab')
    api.add_resource(label_route.LabelsApi,'/api/v1/labels','/api/v1/labels/<string:label_name>')   
    yield app
    with app.app_context():
        db.drop_all()

@pytest.fixture
def user_client(test_app):
    return test_app.test_client()

@pytest.fixture
def login_token(user_client):
    register_data = {
        "username": "Fundoo_Notes",
        "email": "17.atharva@gmail.com",
        "password": "Secure123",
        "location": "Bangalore"
    }
    response = user_client.post('/api/v1/register', json=register_data,headers={'Content-Type': 'application/json'})
    register_data = {
        "username": "Fundoo_N",
        "email": "1.7.a.t.h.m.u@gmail.com",
        "password": "Secure123",
        "location": "Bangalore"
    }
    response = user_client.post('/api/v1/register', json=register_data,headers={'Content-Type': 'application/json'})
    new_user_data = response.get_json()['data']['id']
    login_data = {
        "username": "Fundoo_Notes",
        "password": "Secure123"
    }
    response = user_client.post('/api/v1/login', json=login_data,headers={'Content-Type': 'application/json'})
    token = response.get_json()['token']
    return token