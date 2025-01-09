#!/usr/bin/env python3
"""Script to test all API endpoints."""

import asyncio
import json
import webbrowser
from typing import Dict, Any, List

import httpx
from rich.console import Console
from rich.table import Table

API_BASE = "http://localhost:8000/api/v1"
console = Console()

async def authenticate() -> str:
    """Handle OAuth authentication flow."""
    async with httpx.AsyncClient() as client:
        # Get auth URL
        console.print("[yellow]Initiating authentication...[/yellow]")
        response = await client.get(f"{API_BASE}/auth/login")
        response.raise_for_status()
        auth_data = response.json()
        
        # Open auth URL in browser
        auth_url = auth_data["auth_url"]
        console.print("\n[yellow]Opening GitHub authentication in your browser...[/yellow]")
        try:
            webbrowser.open(auth_url)
        except Exception as e:
            console.print(f"\n[red]Failed to open browser automatically. Please open this URL manually:[/red]")
            console.print(f"[blue]{auth_url}[/blue]")
        
        # Wait for user to complete auth
        console.print("\n[yellow]After authenticating in the browser, copy the access token from the response and paste it below.[/yellow]")
        token = input("\nEnter the access token: ").strip()
        return token

async def test_endpoint(
    client: httpx.AsyncClient,
    method: str,
    endpoint: str,
    headers: Dict[str, str] = None,
    data: Dict[str, Any] = None
) -> Dict[str, Any]:
    """Test a single endpoint and return the result."""
    try:
        if method == "GET":
            response = await client.get(
                f"{API_BASE}{endpoint}",
                headers=headers,
                follow_redirects=True  # Follow redirects automatically
            )
        elif method == "POST":
            response = await client.post(
                f"{API_BASE}{endpoint}",
                headers=headers,
                json=data,
                follow_redirects=True  # Follow redirects automatically
            )
        
        status_code = response.status_code
        try:
            response_data = response.json()
        except:
            response_data = response.text

        return {
            "endpoint": endpoint,
            "method": method,
            "status": status_code,
            "success": 200 <= status_code < 300,
            "response": response_data
        }
    except Exception as e:
        return {
            "endpoint": endpoint,
            "method": method,
            "status": 0,
            "success": False,
            "response": str(e)
        }

async def test_all_endpoints() -> None:
    """Test all available API endpoints."""
    # Get authentication token
    token = await authenticate()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # Define endpoints to test
    endpoints = [
        # Root endpoints
        {"method": "GET", "endpoint": "/docs"},
        {"method": "GET", "endpoint": "/redoc"},
        {"method": "GET", "endpoint": "/openapi.json"},
        
        # Game endpoints (with trailing slashes)
        {"method": "GET", "endpoint": "/game/classes/"},
        {"method": "GET", "endpoint": "/game/constraints/"},
        {"method": "GET", "endpoint": "/game/gear/"},
        {"method": "GET", "endpoint": "/game/gems/"},
        {"method": "GET", "endpoint": "/game/sets/"},
        {"method": "GET", "endpoint": "/game/stats/"},
        {"method": "GET", "endpoint": "/game/synergies/"},
        
        # Auth endpoints (already authenticated)
        {"method": "GET", "endpoint": "/auth/login"},
    ]
    
    # Create results table
    table = Table(title="API Endpoint Test Results")
    table.add_column("Method", style="cyan")
    table.add_column("Endpoint", style="blue")
    table.add_column("Status", style="magenta")
    table.add_column("Success", style="green")
    table.add_column("Response Preview", style="yellow")
    
    async with httpx.AsyncClient() as client:
        results = []
        for endpoint_info in endpoints:
            result = await test_endpoint(
                client,
                endpoint_info["method"],
                endpoint_info["endpoint"],
                headers=headers
            )
            results.append(result)
            
            # Create response preview
            response_preview = str(result["response"])
            if len(response_preview) > 50:
                response_preview = response_preview[:47] + "..."
            
            # Add result to table
            table.add_row(
                result["method"],
                result["endpoint"],
                str(result["status"]),
                "✅" if result["success"] else "❌",
                response_preview
            )
            
            # Save detailed response for logging
            if not result["success"]:
                console.print(f"\n[red]Failed endpoint details:[/red]")
                console.print(f"Endpoint: {result['endpoint']}")
                console.print(f"Response: {result['response']}")
    
    # Print results table
    console.print("\n")
    console.print(table)
    
    # Print summary
    total = len(results)
    successful = sum(1 for r in results if r["success"])
    console.print(f"\nSummary: {successful}/{total} endpoints successful")

if __name__ == "__main__":
    asyncio.run(test_all_endpoints())
