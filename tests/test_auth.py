import pytest

# Mark every test in this file as async using anyio
pytestmark = pytest.mark.anyio
async def test_register_user_success(client):
    """Test that a new user can register successfully."""
    
    payload = {
        "email": "test@example.com",
        "password": "SecurePassword123!",
        "full_name": "Test User",
        "org_name": "Test Org"
    }
    
    # Pretend to be a user sending a POST request to register
    response = await client.post("/api/v1/auth/register", json=payload)
    
    # Verify the results
    assert response.status_code == 201
    data = response.json()
    
    # Registration returns a TokenResponse, not a User profile!
    assert "access_token" in data
    assert "refresh_token" in data
async def test_login_success(client):
    """Test that an existing user can log in and receive a JWT token."""
    
    # 1. Register a user first
    register_payload = {
        "email": "login@example.com",
        "password": "SecurePassword123!",
        "full_name": "Login User",
        "org_name": "Login Org"
    }
    await client.post("/api/v1/auth/register", json=register_payload)
    
    # 2. Try to log in as that user
    login_payload = {
        "email": "login@example.com",
        "password": "SecurePassword123!"
    }
    response = await client.post("/api/v1/auth/login", json=login_payload)
    
    # 3. Verify they got an access token
    assert response.status_code == 200
    data = response.json()
    
    assert "access_token" in data
    assert data["token_type"] == "bearer"