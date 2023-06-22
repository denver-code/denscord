from tests.routes.test_auth import test_signup


def test_same_channel_name(client):
    test_signup(client)
    token1 = client.post(
    "/api/public/authorisation/signin", 
    json={
        "email": "testuser@test.com",
        "password": "testpassword",
    }).json().get("token", "")

    client.post("/api/private/guild", headers={"Authorisation":token1},
        json={
            "name": "Test Guild",
            "description": "Public server for testing purposes",
            "is_private": False
    })

    guild_id = client.get("/api/private/guild", headers={"Authorisation":token1}).json()[0].get("id", "")

    client.post(f"/api/private/guild/{guild_id}/channel/", headers={"Authorisation":token1},
                json={
                    "name": "test-channel",
                    "description": "Public channel for testing purposes",
                })

    client.post(f"/api/private/guild/{guild_id}/channel/", headers={"Authorisation":token1},
                json={
                    "name": "test-channel",
                    "description": "Public channel for testing purposes",
                })

    client.post(f"/api/private/guild/{guild_id}/channel/", headers={"Authorisation":token1},
                json={
                    "name": "test-channel",
                    "description": "Public channel for testing purposes",
                })
    
    channels = client.get(f"/api/private/guild/{guild_id}/channel/", headers={"Authorisation":token1}).json()

    assert len(channels) == 3

    assert channels[0].get("name", "") == "test-channel"
    assert channels[1].get("name", "") == "test-channel-1"
    assert channels[2].get("name", "") == "test-channel-2"

    