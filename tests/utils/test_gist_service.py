"""Tests for the GistService class."""

from datetime import datetime
from typing import Dict, Any
from unittest.mock import AsyncMock, Mock, patch

import httpx
import pytest
from fastapi import HTTPException

from api.utils.gists import GistService, Gist


@pytest.fixture
def mock_response() -> Dict[str, Any]:
    """Create a mock gist response."""
    return {
        "url": "https://api.github.com/gists/abc123",
        "id": "abc123",
        "description": "Test gist",
        "public": True,
        "created_at": "2023-12-01T00:00:00Z",
        "updated_at": "2023-12-01T00:00:00Z",
        "files": {
            "test.json": {
                "filename": "test.json",
                "content": '{"test": true}',
                "raw_url": "https://gist.githubusercontent.com/raw/abc123/test.json",
                "size": 15,
                "language": "JSON",
                "truncated": False
            }
        }
    }


@pytest.fixture
def gist_service() -> GistService:
    """Create a GistService instance with a mock token."""
    return GistService("mock_token")


@pytest.mark.asyncio
async def test_create_gist_success(gist_service: GistService, mock_response: Dict[str, Any]) -> None:
    """Test successful gist creation."""
    mock_response_obj = Mock()
    mock_response_obj.status_code = 201
    mock_response_obj.json = AsyncMock(return_value=mock_response)
    mock_response_obj.aread = AsyncMock()
    mock_response_obj.raise_for_status = Mock()

    mock_post = AsyncMock(return_value=mock_response_obj)

    with patch.object(gist_service._client, "post", mock_post):
        files = {"test.json": {"content": '{"test": true}'}}
        gist = await gist_service.create_gist(files, "Test gist")

        assert isinstance(gist, Gist)
        assert gist.id == "abc123"
        assert gist.description == "Test gist"
        assert len(gist.files) == 1
        assert gist.files[0].filename == "test.json"
        assert gist.files[0].content == '{"test": true}'


@pytest.mark.asyncio
async def test_create_gist_unauthorized(gist_service: GistService) -> None:
    """Test gist creation with invalid token."""
    mock_post = AsyncMock()
    mock_post.side_effect = httpx.HTTPStatusError(
        "401 Unauthorized",
        request=Mock(),
        response=Mock(status_code=401)
    )

    with patch.object(gist_service._client, "post", mock_post):
        with pytest.raises(HTTPException) as exc_info:
            await gist_service.create_gist({"test.json": {"content": "test"}})

        assert exc_info.value.status_code == 401
        assert "Invalid GitHub token" in exc_info.value.detail


@pytest.mark.asyncio
async def test_get_gist_success(gist_service: GistService, mock_response: Dict[str, Any]) -> None:
    """Test successful gist retrieval."""
    mock_response_obj = Mock()
    mock_response_obj.status_code = 200
    mock_response_obj.json = AsyncMock(return_value=mock_response)
    mock_response_obj.aread = AsyncMock()
    mock_response_obj.raise_for_status = Mock()

    mock_get = AsyncMock(return_value=mock_response_obj)

    with patch.object(gist_service._client, "get", mock_get):
        gist = await gist_service.get_gist("abc123")

        assert isinstance(gist, Gist)
        assert gist.id == "abc123"
        assert gist.description == "Test gist"
        assert len(gist.files) == 1
        assert gist.files[0].filename == "test.json"


@pytest.mark.asyncio
async def test_get_gist_not_found(gist_service: GistService) -> None:
    """Test gist retrieval with non-existent ID."""
    mock_get = AsyncMock()
    mock_get.side_effect = httpx.HTTPStatusError(
        "404 Not Found",
        request=Mock(),
        response=Mock(status_code=404)
    )

    with patch.object(gist_service._client, "get", mock_get):
        with pytest.raises(HTTPException) as exc_info:
            await gist_service.get_gist("nonexistent")

        assert exc_info.value.status_code == 404
        assert "Gist not found" in exc_info.value.detail


@pytest.mark.asyncio
async def test_update_gist_success(gist_service: GistService, mock_response: Dict[str, Any]) -> None:
    """Test successful gist update."""
    mock_response_obj = Mock()
    mock_response_obj.status_code = 200
    mock_response_obj.json = AsyncMock(return_value=mock_response)
    mock_response_obj.aread = AsyncMock()
    mock_response_obj.raise_for_status = Mock()

    mock_patch = AsyncMock(return_value=mock_response_obj)

    with patch.object(gist_service._client, "patch", mock_patch):
        files = {"test.json": {"content": '{"test": true}'}}
        gist = await gist_service.update_gist("abc123", files, "Updated test gist")

        assert isinstance(gist, Gist)
        assert gist.id == "abc123"
        assert len(gist.files) == 1
        assert gist.files[0].filename == "test.json"


@pytest.mark.asyncio
async def test_update_gist_forbidden(gist_service: GistService) -> None:
    """Test gist update with insufficient permissions."""
    mock_patch = AsyncMock()
    mock_patch.side_effect = httpx.HTTPStatusError(
        "403 Forbidden",
        request=Mock(),
        response=Mock(status_code=403)
    )

    with patch.object(gist_service._client, "patch", mock_patch):
        with pytest.raises(HTTPException) as exc_info:
            await gist_service.update_gist(
                "abc123",
                {"test.json": {"content": "test"}}
            )

        assert exc_info.value.status_code == 403
        assert "Insufficient permissions" in exc_info.value.detail
