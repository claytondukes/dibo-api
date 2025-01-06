"""GitHub Gist service for storing and retrieving build configurations."""

from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

import httpx
from fastapi import HTTPException


@dataclass
class GistFile:
    """Represents a file in a GitHub Gist."""
    
    filename: str
    content: str
    raw_url: Optional[str] = None
    size: Optional[int] = None
    language: Optional[str] = None
    truncated: bool = False


@dataclass
class Gist:
    """Represents a GitHub Gist."""
    
    id: str
    description: str
    public: bool
    created_at: str
    updated_at: str
    files: List[GistFile]


class GistService:
    """Service for interacting with GitHub Gists API."""

    def __init__(self, github_token: str):
        """Initialize the gist service.
        
        Args:
            github_token: GitHub personal access token
        """
        self._token = github_token
        self._base_url = "https://api.github.com"
        self._headers = {
            "Accept": "application/vnd.github.v3+json",
            "Authorization": f"Bearer {github_token}",
            "User-Agent": "Windsurf-API"
        }
        self._client = httpx.AsyncClient(
            base_url=self._base_url,
            headers=self._headers,
            timeout=30.0
        )

    def _handle_error(self, e: httpx.HTTPError, operation: str) -> HTTPException:
        """Handle HTTP errors from the GitHub API.
        
        Args:
            e: The HTTP error that occurred
            operation: Description of the operation being performed

        Returns:
            An appropriate HTTPException
        """
        if isinstance(e, httpx.HTTPStatusError):
            if e.response.status_code == 404:
                return HTTPException(
                    status_code=404,
                    detail=f"Gist not found"
                )
            elif e.response.status_code == 401:
                return HTTPException(
                    status_code=401,
                    detail="Unauthorized: Invalid GitHub token"
                )
            elif e.response.status_code == 403:
                return HTTPException(
                    status_code=403,
                    detail="Forbidden: Insufficient permissions"
                )
            else:
                return HTTPException(
                    status_code=e.response.status_code,
                    detail=f"GitHub API error: {str(e)}"
                )
        else:
            return HTTPException(
                status_code=500,
                detail=f"Failed to {operation}: {str(e)}"
            )

    async def create_gist(
        self,
        files: Dict[str, Dict[str, str]],
        description: Optional[str] = None,
        public: bool = True
    ) -> Gist:
        """Create a new gist.
        
        Args:
            files: Dictionary mapping filenames to file content
            description: Optional gist description
            public: Whether the gist should be public

        Returns:
            Created gist information

        Raises:
            HTTPException: If gist creation fails
        """
        try:
            response = await self._client.post(
                "/gists",
                json={
                    "files": files,
                    "description": description,
                    "public": public
                }
            )
            await response.aread()
            response.raise_for_status()
            data = await response.json()
            return self._parse_gist_response(data)
        except httpx.HTTPError as e:
            raise self._handle_error(e, "create gist")

    async def get_gist(self, gist_id: str) -> Gist:
        """Retrieve a gist by ID.
        
        Args:
            gist_id: ID of the gist to retrieve

        Returns:
            Gist information

        Raises:
            HTTPException: If gist not found or retrieval fails
        """
        try:
            response = await self._client.get(f"/gists/{gist_id}")
            await response.aread()
            response.raise_for_status()
            data = await response.json()
            return self._parse_gist_response(data)
        except httpx.HTTPError as e:
            raise self._handle_error(e, "retrieve gist")

    async def update_gist(
        self,
        gist_id: str,
        files: Dict[str, Dict[str, str]],
        description: Optional[str] = None
    ) -> Gist:
        """Update an existing gist.
        
        Args:
            gist_id: ID of the gist to update
            files: Dictionary mapping filenames to file content
            description: Optional new description

        Returns:
            Updated gist information

        Raises:
            HTTPException: If gist not found or update fails
        """
        try:
            data = {"files": files}
            if description:
                data["description"] = description

            response = await self._client.patch(
                f"/gists/{gist_id}",
                json=data
            )
            await response.aread()
            response.raise_for_status()
            data = await response.json()
            return self._parse_gist_response(data)
        except httpx.HTTPError as e:
            raise self._handle_error(e, "update gist")

    def _parse_gist_response(self, data: Dict[str, Any]) -> Gist:
        """Parse a GitHub API gist response into a Gist object.
        
        Args:
            data: Raw API response data

        Returns:
            Parsed Gist object
        """
        files = [
            GistFile(
                filename=file_data["filename"],
                content=file_data.get("content", ""),
                raw_url=file_data.get("raw_url"),
                size=file_data.get("size"),
                language=file_data.get("language"),
                truncated=file_data.get("truncated", False)
            )
            for file_data in data["files"].values()
        ]

        return Gist(
            id=data["id"],
            description=data.get("description", ""),
            public=data["public"],
            created_at=data["created_at"],
            updated_at=data["updated_at"],
            files=files
        )
