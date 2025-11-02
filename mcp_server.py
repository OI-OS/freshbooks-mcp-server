#!/usr/bin/env python3
"""FreshBooks MCP Server using proper MCP protocol."""

import asyncio
import json
import os
import sys
from typing import Any, Dict, List

import httpx


class FreshBooksMCPServer:
    """FreshBooks MCP Server."""
    
    def __init__(self):
        self.api_token = os.getenv("FRESHBOOKS_API_TOKEN")
        self.business_id = os.getenv("FRESHBOOKS_BUSINESS_ID")
        self.base_url = "https://api.freshbooks.com"
        self.account_id = None
        
        if not self.api_token:
            self._send_error("FreshBooks API token must be set in environment variables")
            return
        
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {self.api_token}",
                "Content-Type": "application/json",
            },
            timeout=30.0,
        )
    
    def _send_response(self, response: Dict[str, Any]):
        """Send a JSON response."""
        print(json.dumps(response))
        sys.stdout.flush()
    
    def _send_error(self, message: str):
        """Send an error response."""
        self._send_response({"error": message})
    
    async def handle_initialize(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle initialization request."""
        return {
            "jsonrpc": "2.0",
            "id": request.get("id"),
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "serverInfo": {
                    "name": "freshbooks-mcp",
                    "version": "0.1.0"
                }
            }
        }
    
    async def handle_list_tools(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle list tools request."""
        tools = [
            {
                "name": "get_identity",
                "description": "Get FreshBooks identity information and business memberships",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "get_clients",
                "description": "Get all clients from FreshBooks",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "get_invoices",
                "description": "Get all invoices from FreshBooks",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "get_projects",
                "description": "Get all projects from FreshBooks",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "get_expenses",
                "description": "Get all expenses from FreshBooks",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "get_time_entries",
                "description": "Get all time entries from FreshBooks",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        ]
        
        return {
            "jsonrpc": "2.0",
            "id": request.get("id"),
            "result": {
                "tools": tools
            }
        }
    
    async def handle_call_tool(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tool call request."""
        params = request.get("params", {})
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        try:
            if tool_name == "get_identity":
                result = await self.get_identity()
            elif tool_name == "get_clients":
                result = await self.get_clients()
            elif tool_name == "get_invoices":
                result = await self.get_invoices()
            elif tool_name == "get_projects":
                result = await self.get_projects()
            elif tool_name == "get_expenses":
                result = await self.get_expenses()
            elif tool_name == "get_time_entries":
                result = await self.get_time_entries()
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "error": {
                        "code": -32601,
                        "message": f"Unknown tool: {tool_name}"
                    }
                }
            
            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(result, indent=2)
                        }
                    ]
                }
            }
            
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "error": {
                    "code": -32603,
                    "message": str(e)
                }
            }
    
    async def get_identity(self) -> Dict[str, Any]:
        """Get FreshBooks identity information."""
        response = await self.client.get("/auth/api/v1/users/me")
        result = response.json()
        
        # Extract business information if available
        if "response" in result and "business_memberships" in result["response"]:
            business_memberships = result["response"]["business_memberships"]
            if business_memberships:
                # Use the first business if no specific business_id is set
                business = business_memberships[0]["business"]
                self.account_id = business["account_id"]
                if not self.business_id:
                    self.business_id = str(business["id"])
        
        return result
    
    async def _ensure_account_id(self) -> bool:
        """Ensure we have an account_id, get it from identity if needed."""
        if not self.account_id:
            try:
                identity = await self.get_identity()
                if not self.account_id:
                    return False
            except Exception:
                return False
        return True
    
    async def get_clients(self) -> Dict[str, Any]:
        """Get all clients."""
        if not await self._ensure_account_id():
            return {"error": "Could not determine account_id. Please call get_identity first."}
        
        response = await self.client.get(f"/accounting/account/{self.account_id}/users/clients")
        return response.json()
    
    async def get_invoices(self) -> Dict[str, Any]:
        """Get all invoices."""
        if not await self._ensure_account_id():
            return {"error": "Could not determine account_id. Please call get_identity first."}
        
        response = await self.client.get(f"/accounting/account/{self.account_id}/invoices/invoices")
        return response.json()
    
    async def get_projects(self) -> Dict[str, Any]:
        """Get all projects."""
        if not await self._ensure_account_id():
            return {"error": "Could not determine account_id. Please call get_identity first."}
        
        response = await self.client.get(f"/accounting/account/{self.account_id}/projects/projects")
        return response.json()
    
    async def get_expenses(self) -> Dict[str, Any]:
        """Get all expenses."""
        if not await self._ensure_account_id():
            return {"error": "Could not determine account_id. Please call get_identity first."}
        
        response = await self.client.get(f"/accounting/account/{self.account_id}/expenses/expenses")
        return response.json()
    
    async def get_time_entries(self) -> Dict[str, Any]:
        """Get all time entries."""
        if not await self._ensure_account_id():
            return {"error": "Could not determine account_id. Please call get_identity first."}
        
        response = await self.client.get(f"/accounting/account/{self.account_id}/time_entries/time_entries")
        return response.json()
    
    async def run(self):
        """Run the MCP server."""
        while True:
            try:
                line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
                if not line:
                    break
                
                request = json.loads(line.strip())
                method = request.get("method")
                
                if method == "initialize":
                    response = await self.handle_initialize(request)
                elif method == "initialized":
                    # No response needed for initialized notification
                    continue
                elif method == "tools/list":
                    response = await self.handle_list_tools(request)
                elif method == "tools/call":
                    response = await self.handle_call_tool(request)
                else:
                    response = {
                        "jsonrpc": "2.0",
                        "id": request.get("id"),
                        "error": {
                            "code": -32601,
                            "message": f"Unknown method: {method}"
                        }
                    }
                
                self._send_response(response)
                
            except json.JSONDecodeError:
                continue
            except Exception as e:
                self._send_error(f"Server error: {e}")
                break
    
    async def close(self):
        """Close the HTTP client."""
        if hasattr(self, 'client'):
            await self.client.aclose()


async def main():
    """Main entry point."""
    server = FreshBooksMCPServer()
    try:
        await server.run()
    finally:
        await server.close()


if __name__ == "__main__":
    asyncio.run(main())
