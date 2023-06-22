from tests.routes.test_auth import test_signup


def test_check_channel_name_lenght_cutter(client):
    test_signup(client)
    token1 = client.post(
    "/api/public/authorisation/signin", 
    json={
        "email": "testuser@test.com",
        "password": "testpassword",
    }).json().get("token", "")

    client.post("/api/private/guild", headers={"Authorisation":token1},
        json={
            "name": "1234567891234567",
            "description": "Public server for testing purposes",
            "is_private": False
    })

    name = client.get("/api/private/guild", headers={"Authorisation":token1}).json()[0].get("name", "")

    assert len(name) == 15