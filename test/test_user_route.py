import pytest

def test_register_should_return_success(user_client):
    register_data = {
        "username": "Fundoo_Notes",
        "email": "17.atharva@gmail.com",
        "password": "Secure123",
        "location": "Bangalore"
    }
    response = user_client.post('/api/v1/register', json=register_data,headers={'Content-Type': 'application/json'})
    assert response.status_code == 201


def test_login_should_return_success(user_client):
    register_data = {
        "username": "Fundoo_Notes",
        "email": "17.atharva@gmail.com",
        "password": "Secure123",
        "location": "Bangalore"
    }
    response = user_client.post('/api/v1/register', json=register_data,headers={'Content-Type': 'application/json'})
    assert response.status_code == 201
    login_data = {
        "username": "Fundoo_Notes",
        "password": "Secure123"
    }
    response = user_client.post('/api/v1/login', json=login_data,headers={'Content-Type': 'application/json'})
    assert response.status_code == 200

def test_login_should_return_invalid_response(user_client):
    register_data = {
        "username": "Fundoo_Notes",
        "email": "17.atharva@gmail.com",
        "password": "Secure123",
        "location": "Bangalore"
    }
    response = user_client.post('/api/v1/register', json=register_data,headers={'Content-Type': 'application/json'})
    assert response.status_code == 201
    login_data = {
        "username": "Fundoo_Notes",
        "password": "Secure12"
    }
    response = user_client.post('/api/v1/login', json=login_data,headers={'Content-Type': 'application/json'})
    assert response.status_code == 401

def test_verification_should_return_valid_response(user_client):
    register_data = {
        "username": "Fundoo_Notes",
        "email": "17.atharva@gmail.com",
        "password": "Secure123",
        "location": "Bangalore"
    }
    response = user_client.post('/api/v1/register', json=register_data,headers={'Content-Type': 'application/json'})
    token = response.get_json()['token']
    verify = user_client.get(f'/api/v1/verify?token={token}',headers={'Content-Type': 'application/json'})
    assert verify.status_code == 200
    login_data = {
        "username": "Fundoo_Notes",
        "password": "Secure123"
    }
    response = user_client.post('/api/v1/login', json=login_data,headers={'Content-Type': 'application/json'})
    assert response.status_code == 200



