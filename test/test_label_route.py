import pytest

def test_add_label_should_return_success(user_client,login_token):
    label_data = {
        "name":"Label1",
        "user_id":1
    }
    response = user_client.post('/api/v1/labels', json=label_data,
    headers={'Content-Type': 'application/json', 'Authorization': login_token})
    assert response.status_code == 201

def test_get_labels_should_return_success(user_client,login_token):
    response = user_client.get('/api/v1/labels',headers={'Content-Type': 'application/json', 'Authorization': login_token})
    assert response.status_code == 200

def test_update_label_should_return_success(user_client,login_token):
    label_data = {
        "name":"Label1",
        "user_id":1
    }
    response = user_client.post('/api/v1/labels', json=label_data,
    headers={'Content-Type': 'application/json', 'Authorization': login_token})
    print(response.data)
    assert response.status_code == 201
    response = user_client.put(f'/api/v1/labels', json={
        "id":1,
        "name":"Labe",
        "user_id": 1
    },
    headers={'Content-Type': 'application/json', 'Authorization': login_token})
    print(response.data)
    assert response.status_code == 201

def test_delete_label_should_return_success(user_client,login_token):
    label_data = {
        "name":"Label1",
        "user_id":1
    }
    response = user_client.post('/api/v1/labels', json=label_data,
    headers={'Content-Type': 'application/json', 'Authorization': login_token})
    print(response.data)
    assert response.status_code == 201
    response = user_client.delete('/api/v1/labels?label_id=1',headers={'Content-Type': 'application/json', 'Authorization': login_token})
    print(response.data)
    assert response.status_code == 200