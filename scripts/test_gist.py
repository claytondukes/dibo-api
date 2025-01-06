#!/usr/bin/env python3
"""Script to test GitHub Gist functionality through our API."""

import json
import os
import sys
import webbrowser
from typing import Dict, Any

import httpx

API_BASE = "http://localhost:8000/api/v1"

async def authenticate() -> str:
    """Handle OAuth authentication flow."""
    async with httpx.AsyncClient() as client:
        # Get auth URL
        print("Initiating authentication...")
        response = await client.get(f"{API_BASE}/auth/login")
        response.raise_for_status()
        auth_data = response.json()
        
        # Open auth URL in browser
        auth_url = auth_data["auth_url"]
        print("\nOpening GitHub authentication in your browser...")
        webbrowser.get('chrome').open(auth_url)
        
        # Wait for user to complete auth
        print("\nAfter authenticating in the browser, copy the access token")
        print("from the response and paste it below.")
        token = input("\nEnter the access token: ").strip()
        
        if not token:
            print("Error: Access token is required")
            sys.exit(1)
            
        return token


async def test_api_endpoints() -> None:
    """Test the API endpoints for build management."""
    token = await authenticate()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    async with httpx.AsyncClient() as client:
        # Test data
        build_data = {
            "name": "Whirlwind Barbarian",
            "version": "1.0.0",
            "description": "A barbarian build focused on Whirlwind and AoE damage",
            "type": "pve",
            "focus": "dps",
            "level": 60,
            "build": {
                "gems": [
                    {
                        "name": "Blessing of the Worthy",
                        "rank": 5,
                        "quality": 5
                    }
                ],
                "skills": [
                    {
                        "name": "Whirlwind",
                        "essence": "The Gathering"
                    },
                    {
                        "name": "Sprint",
                        "essence": "Hunter's Sight"
                    },
                    {
                        "name": "Iron Skin",
                        "essence": "Flesh of Steel"
                    }
                ],
                "equipment": [
                    {
                        "name": "Grace of the Flagellant Helm",
                        "slot": "head",
                        "attributes": ["Strength", "Critical Hit Chance"]
                    },
                    {
                        "name": "Grace of the Flagellant Shoulders",
                        "slot": "shoulders",
                        "attributes": ["Strength", "Area Damage"]
                    },
                    {
                        "name": "Grace of the Flagellant Chest",
                        "slot": "chest",
                        "attributes": ["Strength", "Life"]
                    }
                ],
                "synergies": [
                    "The Gathering essence pulls enemies into Whirlwind",
                    "Hunter's Sight provides Critical Hit chance while moving",
                    "Grace set bonus increases DoT and channeled damage"
                ]
            },
            "stats": {
                "dps": 10000,
                "survival": 8000,
                "utility": 6000
            },
            "gear": {
                "head": {
                    "name": "Grace of the Flagellant Helm",
                    "attributes": ["Strength", "Critical Hit Chance"]
                },
                "shoulders": {
                    "name": "Grace of the Flagellant Shoulders",
                    "attributes": ["Strength", "Area Damage"]
                },
                "chest": {
                    "name": "Grace of the Flagellant Chest",
                    "attributes": ["Strength", "Life"]
                }
            },
            "sets": {
                "grace": {
                    "name": "Grace of the Flagellant",
                    "pieces": 3,
                    "bonus": "Increases all continual, channeled, and persistent ground damage by 15%"
                }
            },
            "skills": {
                "primary": {
                    "name": "Whirlwind",
                    "essence": "The Gathering",
                    "description": "A spinning attack that deals continuous damage to nearby enemies"
                },
                "utility": {
                    "name": "Sprint",
                    "essence": "Hunter's Sight",
                    "description": "Increases movement speed and Critical Hit Chance while moving"
                },
                "defensive": {
                    "name": "Iron Skin",
                    "essence": "Flesh of Steel",
                    "description": "Increases damage reduction"
                }
            },
            "paragon": {
                "tree": {
                    "name": "Survivor",
                    "points": 100
                }
            }
        }
        
        try:
            # First create a gist
            print("\nCreating gist...")
            response = await client.post(
                f"{API_BASE}/auth/gists",
                headers=headers,
                json={
                    "filename": "build.json",
                    "content": json.dumps(build_data, indent=2),
                    "description": "Whirlwind Barbarian build configuration"
                }
            )
            response.raise_for_status()
            result = response.json()
            gist_id = result["id"]
            print(f"Created gist with ID: {gist_id}")
            print(f"View at: https://gist.github.com/{gist_id}")
            
            # Get the build
            print("\nRetrieving build...")
            response = await client.get(
                f"{API_BASE}/game/builds/{gist_id}",
                headers=headers
            )
            response.raise_for_status()
            build = response.json()
            print("Retrieved build:")
            print(json.dumps(build, indent=2))
            
            # Update the build
            print("\nUpdating build...")
            build_data["version"] = "1.0.1"
            build_data["description"] = "Updated Whirlwind Barbarian build with improved synergies"
            response = await client.put(
                f"{API_BASE}/game/builds/{gist_id}",
                headers=headers,
                json=build_data
            )
            response.raise_for_status()
            updated = response.json()
            print("Build updated successfully")
            print(f"View updated build at: https://gist.github.com/{gist_id}")
            
        except httpx.HTTPStatusError as e:
            print(f"\nAPI Error: {e.response.status_code} - {e.response.text}")
            sys.exit(1)
        except Exception as e:
            print(f"\nUnexpected error: {str(e)}")
            sys.exit(1)


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_api_endpoints())
