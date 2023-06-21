def test_signup(client):
    response = client.get("/api/public/authorisation/signup")
    assert response.status_code == 405

    response = client.post(
        "/api/public/authorisation/signup", 
        json={
            "email": "testuser@test.com",
            "password": "testpassword",
            "username": "testuser",
        }
    )
    assert response.status_code == 200
    assert response.json() == {"message": "User created"}


def test_signup_already_exists(client):
    test_signup(client)
    response = client.get("/api/public/authorisation/signup")
    assert response.status_code == 405

    response = client.post(
        "/api/public/authorisation/signup", 
        json={
            "email": "testuser@test.com",
            "password": "testpassword",
            "username": "testuser",
        }
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "Email already registered"}


def test_signin(client):
    test_signup(client)
    response = client.post(
        "/api/public/authorisation/signin", 
        json={
            "email": "testuser@test.com",
            "password": "testpassword",
        }
    )
    assert response.status_code == 200
    assert response.json().get("token") is not None


def test_signin_bad_password(client):
    test_signup(client)
    response = client.post(
        "/api/public/authorisation/signin", 
        json={
            "email": "testuser@test.com",
            "password": "testpasswords",
        }
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Bad email or password"}


def test_signin_bad_email(client):
    test_signup(client)
    response = client.post(
        "/api/public/authorisation/signin", 
        json={
            "email": "testuser@test",
            "password": "testpassword",
        }
    )
    assert response.status_code == 422
    assert response.json() == {'detail': [{'loc': ['body', 'email'], 'msg': 'value is not a valid email address', 'type': 'value_error.email'}]}


def test_signin_no_password(client):
    test_signup(client)
    response = client.post(
        "/api/public/authorisation/signin", 
        json={
            "email": "testuser@test.com",
        }
    )
    assert response.status_code == 422
    assert response.json() == {'detail': [{'loc': ['body', 'password'], 'msg': 'field required', 'type': 'value_error.missing'}]}


def test_signin_no_body(client):
    test_signup(client)
    response = client.post(
        "/api/public/authorisation/signin", 
    )
    assert response.status_code == 422
    assert response.json() == {'detail': [{'loc': ['body'], 'msg': 'field required', 'type': 'value_error.missing'}]}


def test_signin_empty_body(client):
    test_signup(client)
    response = client.post(
        "/api/public/authorisation/signin", 
        json={}
    )
    assert response.status_code == 422
    assert response.json() == {'detail': [{'loc': ['body', 'email'], 'msg': 'field required', 'type': 'value_error.missing'}, {'loc': ['body', 'password'], 'msg': 'field required', 'type': 'value_error.missing'}]}