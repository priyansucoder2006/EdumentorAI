def test_register_and_login(client):
    # Register
    res = client.post("/api/auth/register", json={
        "name": "Priya Patel",
        "email": "priya@example.com",
        "password": "secretpassword123",
        "preferred_language": "hi",
        "education_level": "intermediate"
    })
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["user"]["email"] == "priya@example.com"
    token = data["access_token"]

    # Get Profile
    profile_res = client.get("/api/auth/profile", headers={"Authorization": f"Bearer {token}"})
    assert profile_res.status_code == 200
    p_data = profile_res.json()
    assert p_data["preferred_language"] == "hi"

    # Login
    login_res = client.post("/api/auth/login", json={
        "email": "priya@example.com",
        "password": "secretpassword123"
    })
    assert login_res.status_code == 200
    assert "access_token" in login_res.json()
