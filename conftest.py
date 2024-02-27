import pytest
from app import create_app,db
from flask_restx import Api
from routes import user_route
from pathlib import Path
import os

@pytest.fixture

def test_app():
    path = Path(__file__).resolve().parent
    app = create_app()
    app.config['SQLALCHEMY_DATABASE_URI'] ='sqlite:///' + os.path.join(path, 'test.sqlite3')
    app.config['TESTING'] = True
    with app.app_context():
        db.create_all()
    api = Api(app)
    api.add_resource(user_route.UserAPI, '/api/v1/register')
    api.add_resource(user_route.LoginAPI, '/api/v1/login')
    yield app
    with app.app_context():
        db.drop_all()

@pytest.fixture
def user_client(test_app):
    return test_app.test_client()
