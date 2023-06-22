from tests.routes.test_auth import test_signup

def test_get_profile(client):
    test_signup(client)
    token = client.post(
        "/api/public/authorisation/signin", 
        json={
            "email": "testuser@test.com",
            "password": "testpassword",
        }).json()["token"]
    
    response = client.get("/api/private/profile", headers={"Authorisation":token})
    assert response.status_code == 200
    assert response.json().get("username") == "testuser"
    assert response.json().get("email") == "testuser@test.com"
    assert response.json().get("avatar") == "https://www.gravatar.com/avatar/0bc83cb571cd1c50ba6f3e8a78ef1346"


def test_get_profile_bad_token(client):
    test_signup(client)
    token = client.post(
        "/api/public/authorisation/signin", 
        json={
            "email": "testuser@test.com",
            "password": "testpasswords",
        }).json().get("token", "")
    
    response = client.get("/api/private/profile", headers={"Authorisation":token})
    assert response.status_code == 401
    assert response.json() == {"detail": "Unauthorised"}


def test_get_user_profile(client):
    test_signup(client)
    token = client.post(
        "/api/public/authorisation/signin", 
        json={
            "email": "testuser@test.com",
            "password": "testpassword",
        }).json().get("token", "")
    
    _id = client.get("/api/private/profile", headers={"Authorisation":token}).json().get("id", "")
    response = client.get(f"/api/public/profile/{_id}")
    assert response.status_code == 200
    assert response.json().get("username") == "testuser"
    assert response.json().get("avatar") == "https://www.gravatar.com/avatar/0bc83cb571cd1c50ba6f3e8a78ef1346"


def test_get_bad_id_user_profile(client):
    response = client.get("/api/public/profile/fsdfsdfsdf")
    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid ID"}


def test_get_not_exist_id_user_profile(client):
    response = client.get("/api/public/profile/11111891a5d13e63599968cc")
    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}


def test_update_profile(client):
    test_signup(client)
    token = client.post(
        "/api/public/authorisation/signin", 
        json={
            "email": "testuser@test.com",
            "password": "testpassword",
        }).json().get("token", "")
    
    response = client.put("/api/private/profile", headers={"Authorisation":token},
                          json={
                                "username": "testuser2",
                                "avatar": "csigorek@gmail.com"
                          })
    assert response.status_code == 200
    assert response.json().get("username") == "testuser2"
    assert response.json().get("avatar") == "https://www.gravatar.com/avatar/a3d737e82a8c6c9999d447b42d7536b3?size=256&default=identicon"


def test_update_profile_empty_body(client):
    test_signup(client)
    token = client.post(
        "/api/public/authorisation/signin", 
        json={
            "email": "testuser@test.com",
            "password": "testpassword",
        }).json().get("token", "")
    
    response = client.put("/api/private/profile", headers={"Authorisation":token},
                          json={})
    assert response.status_code == 400
    assert response.json() == {"detail": "No data to update"}


def test_update_profile_no_body(client):
    test_signup(client)
    token = client.post(
        "/api/public/authorisation/signin", 
        json={
            "email": "testuser@test.com",
            "password": "testpassword",
        }).json().get("token", "")
    
    response = client.put("/api/private/profile", headers={"Authorisation":token})
    assert response.status_code == 422
    assert response.json() == {
        'detail': [{'loc': ['body'],
        'msg': 'field required',
        'type': 'value_error.missing'}],
    }


def test_update_profile_user_username(client):
    test_signup(client)
    token = client.post(
        "/api/public/authorisation/signin", 
        json={
            "email": "testuser@test.com",
            "password": "testpassword",
        }).json().get("token", "")
    
    response = client.put("/api/private/profile", headers={"Authorisation":token},
        json={
            "username": "testuser",
        }
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "Username already registered"}


def test_update_profile_bad_token(client):
    response = client.put("/api/private/profile", headers={"Authorisation":"asd"})
    assert response.status_code == 401
    assert response.json() == {"detail": "Unauthorised"}


def test_bulk_search(client):
    test_signup(client)
    token1 = client.post(
    "/api/public/authorisation/signin", 
    json={
        "email": "testuser@test.com",
        "password": "testpassword",
    }).json().get("token", "")
    user1 = client.get("/api/private/profile", headers={"Authorisation":token1}).json()

    _ = client.post(
        "/api/public/authorisation/signup", 
        json={
            "email": "testuser2@test.com",
            "password": "testpassword",
            "username": "testuser2",
        }
    )
    token2 = client.post(
    "/api/public/authorisation/signin", 
    json={
        "email": "testuser2@test.com",
        "password": "testpassword",
    }).json().get("token", "")
    user2 = client.get("/api/private/profile", headers={"Authorisation":token2}).json()

    del user1["email"]
    del user2["email"]

    response = client.post("/api/public/profile/bulk",
        json={
            "users": [
                user1["id"],
                user2["id"]
            ]
        }
    )
    assert response.status_code == 200
    assert response.json() == [
        user1,
        user2
    ]


def test_bulk_search_one_valid(client):
    test_signup(client)
    token1 = client.post(
    "/api/public/authorisation/signin", 
    json={
        "email": "testuser@test.com",
        "password": "testpassword",
    }).json().get("token", "")
    user1 = client.get("/api/private/profile", headers={"Authorisation":token1}).json()

    del user1["email"]

    response = client.post("/api/public/profile/bulk",
        json={
            "users": [
                user1["id"],
                "11111891a5d13e63599968cc"
            ]
        }
    )
    assert response.status_code == 200
    assert response.json() == [
        user1
    ]


def test_bulk_search_one_invalid(client):
    test_signup(client)
    token1 = client.post(
    "/api/public/authorisation/signin", 
    json={
        "email": "testuser@test.com",
        "password": "testpassword",
    }).json().get("token", "")
    user1 = client.get("/api/private/profile", headers={"Authorisation":token1}).json()

    del user1["email"]

    response = client.post("/api/public/profile/bulk",
        json={
            "users": [
                "11111891a5d13e63599968csdfe74sc"
            ]
        }
    )
    assert response.status_code == 200
    assert response.json() == []

