#!/usr/bin/env python3
"""Script to test all API endpoints."""

import asyncio
import json
import os
from pathlib import Path
from typing import Dict, Any, List

import httpx
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table

# Load environment variables
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

# Build API base URL from environment variables
API_BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:8000')
API_V1_STR = os.getenv('API_V1_STR', '/api/v1')
API_BASE = f"{API_BASE_URL.rstrip('/')}{API_V1_STR}"

# Get project paths
project_root = Path(__file__).parent.parent
openapi_path = project_root / "api/docs/openapi.json"
if not openapi_path.exists():
    raise FileNotFoundError(
        f"OpenAPI spec not found at {openapi_path}. "
        "Make sure the API server is running to generate the spec."
    )

console = Console()

def load_endpoints_from_openapi() -> List[Dict[str, str]]:
    """Load all endpoints from the OpenAPI specification."""
    with open(openapi_path) as f:
        spec = json.load(f)
    
    endpoints = []
    for path, methods in spec["paths"].items():
        # Remove /api/v1 prefix if present
        endpoint = path.replace("/api/v1", "")
        for method in methods:
            endpoints.append({
                "method": method.upper(),
                "endpoint": endpoint,
                "tags": methods[method].get("tags", []),
                "summary": methods[method].get("summary", "")
            })
    return endpoints

async def browser_authenticate() -> str:
    """Handle OAuth authentication flow through browser."""
    async with httpx.AsyncClient() as client:
        # Get auth URL
        console.print("[yellow]Initiating browser authentication...[/yellow]")
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

async def get_auth_token() -> str:
    """Get authentication token from environment or browser auth."""
    token = os.getenv("GH_TOKEN")
    if token:
        console.print("[green]Using GitHub token from environment[/green]")
        return token
    
    console.print("[yellow]GH_TOKEN not found in environment, falling back to browser authentication[/yellow]")
    return await browser_authenticate()

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
                follow_redirects=True
            )
        elif method == "POST":
            response = await client.post(
                f"{API_BASE}{endpoint}",
                headers=headers,
                json=data,
                follow_redirects=True
            )
        elif method == "PUT":
            response = await client.put(
                f"{API_BASE}{endpoint}",
                headers=headers,
                json=data,
                follow_redirects=True
            )
        elif method == "DELETE":
            response = await client.delete(
                f"{API_BASE}{endpoint}",
                headers=headers,
                follow_redirects=True
            )
        elif method == "PATCH":
            response = await client.patch(
                f"{API_BASE}{endpoint}",
                headers=headers,
                json=data,
                follow_redirects=True
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

def create_results_table(results: List[Dict[str, Any]]) -> Table:
    """Create a rich table to display test results."""
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Method", style="dim")
    table.add_column("Endpoint")
    table.add_column("Status")
    table.add_column("Success", justify="center")
    
    for result in results:
        status_style = "green" if result["success"] else "red"
        table.add_row(
            result["method"],
            result["endpoint"],
            str(result["status"]),
            "✓" if result["success"] else "✗",
            style=status_style
        )
    return table

async def test_all_endpoints() -> None:
    """Test all available API endpoints."""
    try:
        # Get authentication token from environment or browser auth
        token = await get_auth_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        # Load endpoints from OpenAPI spec
        endpoints = load_endpoints_from_openapi()
        console.print(f"\n[yellow]Found {len(endpoints)} endpoints to test[/yellow]")
        
        # Test each endpoint
        results = []
        async with httpx.AsyncClient() as client:
            for endpoint_info in endpoints:
                console.print(f"\n[yellow]Testing {endpoint_info['method']} {endpoint_info['endpoint']}...[/yellow]")
                result = await test_endpoint(
                    client,
                    endpoint_info["method"],
                    endpoint_info["endpoint"],
                    headers=headers
                )
                results.append(result)
        
        # Display results
        console.print("\n[bold]Test Results:[/bold]")
        table = create_results_table(results)
        console.print(table)
        
        # Summary
        success_count = sum(1 for r in results if r["success"])
        console.print(f"\n[bold]Summary:[/bold] {success_count}/{len(results)} endpoints successful")
        
    except Exception as e:
        console.print(f"\n[red]Error: {str(e)}[/red]")

if __name__ == "__main__":
    asyncio.run(test_all_endpoints())
