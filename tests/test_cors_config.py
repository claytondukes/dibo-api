"""Test CORS configuration settings."""

import os
from typing import Generator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from api.core.config import Settings
from api.main import create_app


def create_test_app() -> FastAPI:
    """Create a test FastAPI application with minimal routes."""
    app = create_app()
    
    @app.get("/test")
    async def test_endpoint():
        return {"status": "ok"}
    
    return app


@pytest.fixture
def original_cors_settings():
    """Save and restore original CORS settings."""
    original = {
        "BACKEND_CORS_ORIGINS": os.environ.get("BACKEND_CORS_ORIGINS", ""),
        "ALLOW_CREDENTIALS": os.environ.get("ALLOW_CREDENTIALS", ""),
        "ALLOW_METHODS": os.environ.get("ALLOW_METHODS", ""),
        "ALLOW_HEADERS": os.environ.get("ALLOW_HEADERS", "")
    }
    yield original
    # Restore original values
    for key, value in original.items():
        if value:
            os.environ[key] = value
        elif key in os.environ:
            del os.environ[key]


@pytest.fixture
def settings(original_cors_settings) -> Settings:
    """Create test settings instance."""
    return Settings()


@pytest.fixture
def test_client(settings: Settings) -> Generator[TestClient, None, None]:
    """Create test client with CORS settings."""
    app = create_test_app()
    with TestClient(app) as client:
        yield client


def test_cors_origins_from_env(settings: Settings, original_cors_settings) -> None:
    """Test that CORS origins are loaded from .env file."""
    # Get the original origins from the fixture
    original_origins = original_cors_settings["BACKEND_CORS_ORIGINS"]
    if not original_origins:
        return  # Skip test if no origins configured
        
    env_origins = original_origins.split(",")
    expected_origins = [origin.strip() for origin in env_origins if origin.strip()]
    
    # Verify all expected origins are present
    assert settings.cors_origins == expected_origins
    
    # Verify the raw string matches
    assert settings.BACKEND_CORS_ORIGINS == original_origins


def test_cors_origins_with_new_origin(original_cors_settings) -> None:
    """Test adding a new origin to existing ones."""
    new_origin = "http://neworigin:8080"
    original_origins = original_cors_settings["BACKEND_CORS_ORIGINS"]
    
    if original_origins:
        os.environ["BACKEND_CORS_ORIGINS"] = f"{original_origins},{new_origin}"
    else:
        os.environ["BACKEND_CORS_ORIGINS"] = new_origin
    
    settings = Settings()
    assert new_origin in settings.cors_origins


def test_cors_origins_with_whitespace(original_cors_settings) -> None:
    """Test parsing CORS origins with extra whitespace."""
    test_origins = " http://test1.com , http://test2.com "
    os.environ["BACKEND_CORS_ORIGINS"] = test_origins
    
    settings = Settings()
    assert settings.cors_origins == ["http://test1.com", "http://test2.com"]


def test_cors_headers_integration(test_client: TestClient, original_cors_settings) -> None:
    """Test CORS headers in HTTP response."""
    # Get first allowed origin from current settings
    original_origins = original_cors_settings["BACKEND_CORS_ORIGINS"]
    if not original_origins:
        pytest.skip("No CORS origins configured")
        
    env_origins = original_origins.split(",")
    allowed_origin = next((origin.strip() for origin in env_origins if origin.strip()))
    
    # Test with allowed origin
    response = test_client.get(
        "/test",
        headers={"Origin": allowed_origin}
    )
    
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == allowed_origin
    
    # Test with non-allowed origin
    non_allowed_origin = "http://evil.com"
    response = test_client.get(
        "/test",
        headers={"Origin": non_allowed_origin}
    )
    
    assert response.status_code == 200
    assert "access-control-allow-origin" not in response.headers


def test_cors_preflight_request(test_client: TestClient, original_cors_settings) -> None:
    """Test CORS preflight request handling."""
    # Get first allowed origin from current settings
    original_origins = original_cors_settings["BACKEND_CORS_ORIGINS"]
    if not original_origins:
        pytest.skip("No CORS origins configured")
        
    env_origins = original_origins.split(",")
    allowed_origin = next((origin.strip() for origin in env_origins if origin.strip()))
    
    response = test_client.options(
        "/test",
        headers={
            "Origin": allowed_origin,
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "Content-Type"
        }
    )
    
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == allowed_origin
    assert "GET" in response.headers["access-control-allow-methods"]
    assert "Content-Type" in response.headers["access-control-allow-headers"]
