def test_index(client):
    response = client.get("/api/")
    assert response.status_code == 404