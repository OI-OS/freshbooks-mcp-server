#!/usr/bin/env python3
"""Simple FreshBooks MCP Server."""

import asyncio
import json
import os
import sys
from typing import Any, Dict, List

import httpx


class SimpleFreshBooksServer:
    """Simple FreshBooks MCP Server."""
    
    def __init__(self):
        self.api_token = os.getenv("FRESHBOOKS_API_TOKEN")
        self.business_id = os.getenv("FRESHBOOKS_BUSINESS_ID")
        self.base_url = "https://api.freshbooks.com"
        
        if not self.api_token or not self.business_id:
            print(json.dumps({
                "error": "FreshBooks API token and business ID must be set in environment variables",
                "required_vars": ["FRESHBOOKS_API_TOKEN", "FRESHBOOKS_BUSINESS_ID"]
            }), file=sys.stderr)
            sys.exit(1)
        
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {self.api_token}",
                "Content-Type": "application/json",
            },
            timeout=30.0,
        )
    
    async def get_clients(self) -> Dict[str, Any]:
        """Get all clients."""
        try:
            response = await self.client.get(f"/accounting/account/{self.business_id}/users/clients")
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    async def get_invoices(self) -> Dict[str, Any]:
        """Get all invoices."""
        try:
            response = await self.client.get(f"/accounting/account/{self.business_id}/invoices/invoices")
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    async def get_projects(self) -> Dict[str, Any]:
        """Get all projects."""
        try:
            response = await self.client.get(f"/accounting/account/{self.business_id}/projects/projects")
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    async def get_expenses(self) -> Dict[str, Any]:
        """Get all expenses."""
        try:
            response = await self.client.get(f"/accounting/account/{self.business_id}/expenses/expenses")
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    async def get_time_entries(self) -> Dict[str, Any]:
        """Get all time entries."""
        try:
            response = await self.client.get(f"/accounting/account/{self.business_id}/time_entries/time_entries")
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()


async def main():
    """Main entry point for testing."""
    server = SimpleFreshBooksServer()
    
    print("FreshBooks MCP Server started")
    print("Available tools: get_clients, get_invoices, get_projects, get_expenses, get_time_entries")
    
    # Test one of the endpoints
    try:
        result = await server.get_clients()
        print(f"Test result: {json.dumps(result, indent=2)}")
    except Exception as e:
        print(f"Test error: {e}")
    
    await server.close()


if __name__ == "__main__":
    asyncio.run(main())


