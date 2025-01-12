"""Authentication endpoint tests."""

from fastapi.testclient import TestClient
from httpx import AsyncClient, Response
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi import HTTPException, status
from api.auth.service import AuthService
from api.auth.middleware import verify_token
from api.auth.routes import get_auth_service, get_token
from api.main import app

def test_read_main(client: TestClient) -> None:
    """Test root endpoint."""
    response = client.get("/api/v1/")
    assert response.status_code == 200

def test_github_login(client: TestClient) -> None:
    """Test GitHub login endpoint."""
    response = client.get("/api/v1/auth/login")
    assert response.status_code == 200
    data = response.json()
    assert "auth_url" in data
    assert "state" in data

@pytest.mark.asyncio
async def test_github_callback(client: TestClient, mock_github_api, mock_auth_service) -> None:
    """Test GitHub callback endpoint."""
    base_url = "http://testserver"
    
    # First get a valid state
    login_response = client.get("/api/v1/auth/login")
    state = login_response.json()["state"]
    
    # Test with invalid code
    mock_auth_service.validate_state.return_value = True  # State is valid
    mock_auth_service.exchange_code_for_token.side_effect = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Invalid code"
    )
    
    # Mock the response
    mock_response = AsyncMock(spec=Response)
    mock_response.status_code = status.HTTP_400_BAD_REQUEST
    mock_response.json.return_value = {"detail": "Invalid code"}
    
    async with AsyncClient(app=app, base_url=base_url) as ac:
        with patch.object(ac, "get", return_value=mock_response):
            response = await ac.get(
                "/api/v1/auth/github",
                params={"code": "invalid_code", "state": state}
            )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "Invalid code"

@pytest.fixture
def mock_github_api():
    """Mock GitHub API responses."""
    with patch("httpx.AsyncClient.post") as mock_post, \
         patch("httpx.AsyncClient.get") as mock_get:
        mock_post.return_value.status_code = 201
        mock_post.return_value.json.return_value = {
            "id": "test_gist_id",
            "files": {
                "test.json": {
                    "filename": "test.json",
                    "content": "{}"
                }
            }
        }
        
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "id": "test_gist_id",
            "files": {
                "test.json": {
                    "filename": "test.json",
                    "content": "{}"
                }
            }
        }
        
        yield

@pytest.fixture
def mock_verify_token():
    """Mock verify_token dependency."""
    with patch("api.auth.middleware.verify_token") as mock:
        mock.return_value = "gho_test_token"  # Return GitHub token directly
        yield mock

@pytest.fixture
def mock_auth_service():
    """Mock auth service."""
    mock = AsyncMock(spec=AuthService)
    
    # Configure default behaviors
    mock.generate_github_login_url.return_value = {
        "auth_url": "https://github.com/login/oauth/authorize",
        "state": "test_state"
    }
    mock.validate_state.return_value = True
    mock.exchange_code_for_token.return_value = {
        "access_token": "gho_test_token",
        "token_type": "bearer",
        "scope": "gist"
    }
    mock.create_gist.return_value = {
        "id": "test_gist_id",
        "files": {
            "test.json": {
                "filename": "test.json",
                "content": "{}"
            }
        }
    }
    mock.update_gist.return_value = {
        "id": "test_gist_id",
        "files": {
            "test.json": {
                "filename": "test.json",
                "content": "{}"
            }
        }
    }
    mock.get_user_gists.return_value = [{
        "id": "test_gist_id",
        "files": {
            "test.json": {
                "filename": "test.json",
                "content": "{}"
            }
        }
    }]
    
    app.dependency_overrides[get_auth_service] = lambda: mock
    yield mock
    app.dependency_overrides.pop(get_auth_service, None)

@pytest.mark.asyncio
async def test_create_gist(client: TestClient, mock_github_api, mock_auth_service, mock_verify_token) -> None:
    """Test gist creation endpoint."""
    base_url = "http://testserver"
    
    # Test without auth
    mock_response = AsyncMock(spec=Response)
    mock_response.status_code = status.HTTP_401_UNAUTHORIZED
    mock_response.json.return_value = {"detail": "Not authenticated"}
    
    app.dependency_overrides[get_token] = lambda: None  # No token
    async with AsyncClient(app=app, base_url=base_url) as ac:
        with patch.object(ac, "post", return_value=mock_response):
            response = await ac.post(
                "/api/v1/auth/gists",
                headers={}  # No authorization header
            )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    # Test with auth
    mock_response = AsyncMock(spec=Response)
    mock_response.status_code = status.HTTP_201_CREATED
    mock_response.json.return_value = {
        "id": "test_gist_id",
        "files": {
            "test.json": {
                "filename": "test.json",
                "content": "{}"
            }
        }
    }
    
    app.dependency_overrides[get_token] = lambda: "gho_test_token"  # Valid GitHub token
    async with AsyncClient(app=app, base_url=base_url) as ac:
        with patch.object(ac, "post", return_value=mock_response):
            response = await ac.post(
                "/api/v1/auth/gists",
                headers={"Authorization": "Bearer gho_test_token"},
                json={
                    "filename": "test.json",
                    "content": "{}",
                    "description": "Test gist"
                }
            )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["id"] == "test_gist_id"

@pytest.mark.asyncio
async def test_update_gist(client: TestClient, mock_github_api, mock_auth_service, mock_verify_token) -> None:
    """Test gist update endpoint."""
    base_url = "http://testserver"
    gist_id = "test_gist_id"
    
    # Test without auth
    mock_response = AsyncMock(spec=Response)
    mock_response.status_code = status.HTTP_401_UNAUTHORIZED
    mock_response.json.return_value = {"detail": "Not authenticated"}
    
    app.dependency_overrides[get_token] = lambda: None  # No token
    async with AsyncClient(app=app, base_url=base_url) as ac:
        with patch.object(ac, "patch", return_value=mock_response):
            response = await ac.patch(
                f"/api/v1/auth/gists/{gist_id}",
                headers={}  # No authorization header
            )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    # Test with auth
    mock_response = AsyncMock(spec=Response)
    mock_response.status_code = status.HTTP_200_OK
    mock_response.json.return_value = {
        "id": "test_gist_id",
        "files": {
            "test.json": {
                "filename": "test.json",
                "content": "{}"
            }
        }
    }
    
    app.dependency_overrides[get_token] = lambda: "gho_test_token"  # Valid GitHub token
    async with AsyncClient(app=app, base_url=base_url) as ac:
        with patch.object(ac, "patch", return_value=mock_response):
            response = await ac.patch(
                f"/api/v1/auth/gists/{gist_id}",
                headers={"Authorization": "Bearer gho_test_token"},
                json={
                    "filename": "test.json",
                    "content": "{}",
                    "description": "Updated test gist"
                }
            )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == "test_gist_id"

@pytest.mark.asyncio
async def test_get_gists(client: TestClient, mock_github_api, mock_auth_service, mock_verify_token) -> None:
    """Test get gists endpoint."""
    base_url = "http://testserver"
    
    # Test without auth
    mock_response = AsyncMock(spec=Response)
    mock_response.status_code = status.HTTP_401_UNAUTHORIZED
    mock_response.json.return_value = {"detail": "Not authenticated"}
    
    app.dependency_overrides[get_token] = lambda: None  # No token
    async with AsyncClient(app=app, base_url=base_url) as ac:
        with patch.object(ac, "get", return_value=mock_response):
            response = await ac.get(
                "/api/v1/auth/gists",
                headers={}  # No authorization header
            )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    # Test with auth
    mock_response = AsyncMock(spec=Response)
    mock_response.status_code = status.HTTP_200_OK
    mock_response.json.return_value = [{
        "id": "test_gist_id",
        "files": {
            "test.json": {
                "filename": "test.json",
                "content": "{}"
            }
        }
    }]
    
    app.dependency_overrides[get_token] = lambda: "gho_test_token"  # Valid GitHub token
    async with AsyncClient(app=app, base_url=base_url) as ac:
        with patch.object(ac, "get", return_value=mock_response):
            response = await ac.get(
                "/api/v1/auth/gists",
                headers={"Authorization": "Bearer gho_test_token"}
            )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert data[0]["id"] == "test_gist_id"
