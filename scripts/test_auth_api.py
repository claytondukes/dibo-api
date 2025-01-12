#!/usr/bin/env python3
"""Test script for auth API endpoints."""

import os
import json
import httpx
import asyncio
import webbrowser
from datetime import datetime

# API configuration
BASE_URL = "http://localhost:8000/api/v1"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

def open_chrome(url: str) -> None:
    """Open URL in Chrome browser."""
    chrome_path = {
        "darwin": "open -a '/Applications/Google Chrome.app' %s",
    }.get("darwin")
    
    try:
        webbrowser.get(chrome_path).open(url)
    except Exception as e:
        print(f"Failed to open Chrome: {e}")
        print("Please open this URL manually:")
        print(url)

async def test_auth_flow():
    """Test the auth flow and gist creation."""
    async with httpx.AsyncClient() as client:
        try:
            if not GITHUB_TOKEN:
                # Get login URL from our API
                response = await client.get(f"{BASE_URL}/auth/login")
                response.raise_for_status()
                login_data = response.json()
                
                print("\n=== Instructions ===")
                print("To get a GitHub token:")
                print("1. Opening Chrome to complete GitHub OAuth...")
                open_chrome(login_data['auth_url'])
                print("2. After authorization, you'll get a JSON response")
                print("3. Copy the access_token value from that response")
                print("4. Set that token as GITHUB_TOKEN environment variable:")
                print("   export GITHUB_TOKEN=your_token_here")
                print("5. Run this script again")
                return
            
            # Create a test gist through our API
            gist_data = {
                "filename": "test_gist.json",
                "content": json.dumps({
                    "test": True,
                    "timestamp": datetime.now().isoformat()
                }, indent=2),
                "description": "Test gist created via DIBO API"
            }
            
            print("\n=== Creating Gist via DIBO API ===")
            response = await client.post(
                f"{BASE_URL}/auth/gists",
                headers={
                    "Authorization": f"Bearer {GITHUB_TOKEN}"
                },
                json=gist_data
            )
            response.raise_for_status()
            print(f"Status: {response.status_code}")
            print("Response:", json.dumps(response.json(), indent=2))
            
            print("\n=== Getting Gists via DIBO API ===")
            response = await client.get(
                f"{BASE_URL}/auth/gists",
                headers={
                    "Authorization": f"Bearer {GITHUB_TOKEN}"
                }
            )
            response.raise_for_status()
            print(f"Status: {response.status_code}")
            print("Response:", json.dumps(response.json(), indent=2))
            
        except httpx.HTTPError as e:
            print(f"\nError: {e}")
            if hasattr(e, 'response'):
                print(f"Response: {e.response.text}")
            raise

if __name__ == "__main__":
    asyncio.run(test_auth_flow())
