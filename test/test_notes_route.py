import pytest

def test_add_note_should_return_success(user_client, login_token):
    print(login_token)
    note_data = {
        "title": "test",
        "description": "test",
        "color": "test",
    }
    response = user_client.post('/api/v1/notes', json=note_data,
    headers={'Content-Type': 'application/json', 'Authorization': login_token})
    assert response.status_code == 201

def test_add_notes_should_return_bad_request(user_client,login_token):
    note_data = {
        "title": "test",
        "color": "test",
    }
    response = user_client.post('/api/v1/notes', json=note_data,
    headers={'Content-Type': 'application/json', 'Authorization': login_token})
    assert response.status_code == 400

def test_get_notes_should_return_success(user_client,login_token):
    note_data = {
        "title": "test",
        "description": "test",
        "color": "test",
    }
    response = user_client.post('/api/v1/notes', json=note_data,
    headers={'Content-Type': 'application/json', 'Authorization': login_token})
    assert response.status_code == 201
    response = user_client.get('/api/v1/notes',
    headers={'Content-Type': 'application/json', 'Authorization': login_token})
    assert response.status_code == 200

@pytest.mark.abc
def test_update_notes_should_return_success(user_client,login_token):
    note_data = {
        "title": "test",
        "description": "test",
        "color": "test",
    }
    response = user_client.post('/api/v1/notes', json=note_data,
    headers={'Content-Type': 'application/json', 'Authorization': login_token})
    assert response.status_code == 201
    note_id = response.get_json()['data']['id']
    updated_note_data = {
        "id": note_id,
        "title": "test",
        "description": "test",
        "color": "test",
    }
    response = user_client.put(f'/api/v1/notes', json=updated_note_data,
    headers={'Content-Type': 'application/json', 'Authorization': login_token})
    assert response.status_code == 200

def test_delete_notes_should_return_success(user_client,login_token):
    note_data = {
        "title": "test",
        "description": "test",
        "color": "test",
    }
    response = user_client.post('/api/v1/notes', json=note_data,
    headers={'Content-Type': 'application/json', 'Authorization': login_token})
    assert response.status_code == 201
    note_id = response.get_json()['data']['id']
    response = user_client.delete(f'/api/v1/notes?note_id={note_id}',
    headers={'Content-Type': 'application/json', 'Authorization': login_token})
    assert response.status_code == 200

def test_trash_notes_should_return_bad_request(user_client,login_token):
    note_data = {
        "title": "test",
        "description": "test",
        "color": "test",
    }
    response = user_client.post('/api/v1/notes', json=note_data,
    headers={'Content-Type': 'application/json', 'Authorization': login_token})
    assert response.status_code == 201
    note_id = response.get_json()['data']['id']
    response = user_client.put(f'/api/v1/notes/trash?note_id={note_id}',
    headers={'Content-Type': 'application/json', 'Authorization': login_token})
    print(response.data)
    assert response.status_code == 400

def test_trash_notes_should_return_success(user_client,login_token):
    note_data = {
        "title": "test",
        "description": "test",
        "color": "test",
    }
    response = user_client.post('/api/v1/notes', json=note_data,
    headers={'Content-Type': 'application/json', 'Authorization': login_token})
    assert response.status_code == 201
    note_id = response.get_json()['data']['id']
    response = user_client.put(f'/api/v1/notes/trash', json={"id": note_id},
    headers={'Content-Type': 'application/json', 'Authorization': login_token})
    print(response.data)
    assert response.status_code == 200

def test_get_trashed_notes_should_return_success(user_client,login_token):
    response = user_client.get('/api/v1/notes/trash',headers={'Content-Type': 'application/json', 'Authorization': login_token})
    assert response.status_code == 200


def test_archive_notes_should_return_success(user_client,login_token):
    note_data = {
        "title": "test",
        "description": "test",
        "color": "test",
    }
    response = user_client.post('/api/v1/notes', json=note_data,
    headers={'Content-Type': 'application/json', 'Authorization': login_token})
    assert response.status_code == 201
    note_id = response.get_json()['data']['id']
    response = user_client.get('/api/v1/notes/archived',json = {'id': note_id},headers={'Content-Type': 'application/json', 'Authorization': login_token})

def test_get_archived_notes_should_return_success(user_client,login_token):
    response = user_client.get('/api/v1/notes/archived',headers={'Content-Type': 'application/json', 'Authorization': login_token})
    assert response.status_code == 200

def test_collaborators_should_return_success(user_client,login_token):
    note_data = {
        "title": "test",
        "description": "test",
        "color": "test",
    }
    response = user_client.post('/api/v1/notes', json=note_data,
    headers={'Content-Type': 'application/json', 'Authorization': login_token})
    assert response.status_code == 201
    note_id = response.get_json()['data']['id']
    collab_ids = [2]
    response = user_client.post('/api/v1/notes/collab',json = {'id': note_id,'user_ids': collab_ids},headers={'Content-Type': 'application/json', 'Authorization': login_token})