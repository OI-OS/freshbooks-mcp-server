#!/usr/bin/env python3
"""FreshBooks OAuth MCP Server implementation."""

import asyncio
import json
import os
import sys
import webbrowser
import urllib.parse
from typing import Any, Dict, List, Optional
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import time

import httpx
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    ListToolsRequest,
    ListToolsResult,
    Tool,
    TextContent,
)
from pydantic import BaseModel, Field


class OAuthCallbackHandler(BaseHTTPRequestHandler):
    """HTTP handler for OAuth callback."""
    
    def do_GET(self):
        """Handle GET requests."""
        if self.path.startswith('/callback'):
            # Parse query parameters
            query_params = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            
            # Send response
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            if 'code' in query_params:
                code = query_params['code'][0]
                self.server.auth_code = code
                self.wfile.write(b'<html><body><h1>Authorization successful!</h1><p>You can close this window.</p></body></html>')
            else:
                error = query_params.get('error', ['Unknown error'])[0]
                self.server.auth_error = error
                self.wfile.write(f'<html><body><h1>Authorization failed!</h1><p>Error: {error}</p></body></html>'.encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        """Suppress log messages."""
        pass


class FreshBooksOAuthConfig(BaseModel):
    """FreshBooks OAuth configuration."""
    client_id: str = Field(..., description="FreshBooks OAuth client ID")
    client_secret: str = Field(..., description="FreshBooks OAuth client secret")
    redirect_uri: str = Field(default="http://localhost:8080/callback", description="OAuth redirect URI")
    base_url: str = Field(default="https://api.freshbooks.com", description="FreshBooks API base URL")
    auth_url: str = Field(default="https://auth.freshbooks.com/oauth/authorize", description="FreshBooks OAuth authorization URL")
    token_url: str = Field(default="https://api.freshbooks.com/auth/oauth/token", description="FreshBooks OAuth token URL")


class FreshBooksOAuthClient:
    """FreshBooks OAuth API client."""
    
    def __init__(self, config: FreshBooksOAuthConfig):
        self.config = config
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None
        self.account_id: Optional[str] = None
        self.business_id: Optional[str] = None
        self.client = httpx.AsyncClient(
            base_url=config.base_url,
            headers={
                "Content-Type": "application/json",
            },
            timeout=30.0,
        )
    
    async def start_oauth_flow(self) -> str:
        """Start OAuth flow and return authorization URL."""
        params = {
            'response_type': 'code',
            'client_id': self.config.client_id,
            'redirect_uri': self.config.redirect_uri,
            'scope': 'user:profile:read accounting:read'
        }
        
        auth_url = f"{self.config.auth_url}?" + urllib.parse.urlencode(params)
        return auth_url
    
    async def exchange_code_for_token(self, auth_code: str) -> Dict[str, Any]:
        """Exchange authorization code for access token."""
        data = {
            'grant_type': 'authorization_code',
            'client_id': self.config.client_id,
            'client_secret': self.config.client_secret,
            'redirect_uri': self.config.redirect_uri,
            'code': auth_code
        }
        
        response = await self.client.post(
            self.config.token_url,
            data=data,
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )
        response.raise_for_status()
        return response.json()
    
    async def set_access_token(self, access_token: str):
        """Set access token and update client headers."""
        self.access_token = access_token
        self.client.headers.update({
            "Authorization": f"Bearer {access_token}"
        })
    
    async def get_identity(self) -> Dict[str, Any]:
        """Get FreshBooks identity information."""
        response = await self.client.get("/auth/api/v1/users/me")
        response.raise_for_status()
        result = response.json()
        
        # Extract business information if available
        if "response" in result and "business_memberships" in result["response"]:
            business_memberships = result["response"]["business_memberships"]
            if business_memberships:
                business = business_memberships[0]["business"]
                self.account_id = business["account_id"]
                self.business_id = str(business["id"])
        
        return result
    
    async def get_clients(self) -> Dict[str, Any]:
        """Get all clients."""
        if not self.account_id:
            return {"error": "No account_id available. Please authenticate first."}
        
        response = await self.client.get(f"/accounting/account/{self.account_id}/users/clients")
        response.raise_for_status()
        return response.json()
    
    async def get_invoices(self) -> Dict[str, Any]:
        """Get all invoices."""
        if not self.account_id:
            return {"error": "No account_id available. Please authenticate first."}
        
        response = await self.client.get(f"/accounting/account/{self.account_id}/invoices/invoices")
        response.raise_for_status()
        return response.json()
    
    async def get_projects(self) -> Dict[str, Any]:
        """Get all projects."""
        if not self.account_id:
            return {"error": "No account_id available. Please authenticate first."}
        
        response = await self.client.get(f"/accounting/account/{self.account_id}/projects/projects")
        response.raise_for_status()
        return response.json()
    
    async def get_expenses(self) -> Dict[str, Any]:
        """Get all expenses."""
        if not self.account_id:
            return {"error": "No account_id available. Please authenticate first."}
        
        response = await self.client.get(f"/accounting/account/{self.account_id}/expenses/expenses")
        response.raise_for_status()
        return response.json()
    
    async def get_time_entries(self) -> Dict[str, Any]:
        """Get all time entries."""
        if not self.account_id:
            return {"error": "No account_id available. Please authenticate first."}
        
        response = await self.client.get(f"/accounting/account/{self.account_id}/time_entries/time_entries")
        response.raise_for_status()
        return response.json()
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()


class FreshBooksOAuthMCPServer:
    """FreshBooks OAuth MCP Server."""
    
    def __init__(self):
        self.server = Server("freshbooks-oauth-mcp")
        self.freshbooks_client: Optional[FreshBooksOAuthClient] = None
        self.callback_server: Optional[HTTPServer] = None
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Setup MCP server handlers."""
        
        @self.server.list_tools()
        async def handle_list_tools() -> List[Tool]:
            """List available tools."""
            return [
                Tool(
                    name="authenticate",
                    description="Start OAuth authentication flow with FreshBooks",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                ),
                Tool(
                    name="get_identity",
                    description="Get FreshBooks identity information",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                ),
                Tool(
                    name="get_clients",
                    description="Get all clients from FreshBooks",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                ),
                Tool(
                    name="get_invoices",
                    description="Get all invoices from FreshBooks",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                ),
                Tool(
                    name="get_projects",
                    description="Get all projects from FreshBooks",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                ),
                Tool(
                    name="get_expenses",
                    description="Get all expenses from FreshBooks",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                ),
                Tool(
                    name="get_time_entries",
                    description="Get all time entries from FreshBooks",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                ),
            ]
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            """Handle tool calls."""
            if name == "authenticate":
                return await self._handle_authenticate()
            
            if not self.freshbooks_client or not self.freshbooks_client.access_token:
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "error": "Not authenticated. Please call 'authenticate' first.",
                        "available_tools": ["authenticate"]
                    }, indent=2)
                )]
            
            try:
                if name == "get_identity":
                    result = await self.freshbooks_client.get_identity()
                elif name == "get_clients":
                    result = await self.freshbooks_client.get_clients()
                elif name == "get_invoices":
                    result = await self.freshbooks_client.get_invoices()
                elif name == "get_projects":
                    result = await self.freshbooks_client.get_projects()
                elif name == "get_expenses":
                    result = await self.freshbooks_client.get_expenses()
                elif name == "get_time_entries":
                    result = await self.freshbooks_client.get_time_entries()
                else:
                    return [TextContent(
                        type="text",
                        text=json.dumps({"error": f"Unknown tool: {name}"}, indent=2)
                    )]
                
                return [TextContent(
                    type="text",
                    text=json.dumps(result, indent=2)
                )]
                
            except Exception as e:
                return [TextContent(
                    type="text",
                    text=json.dumps({"error": str(e)}, indent=2)
                )]
    
    async def _handle_authenticate(self) -> List[TextContent]:
        """Handle OAuth authentication."""
        try:
            # Initialize client if not already done
            if not self.freshbooks_client:
                client_id = os.getenv("FRESHBOOKS_CLIENT_ID")
                client_secret = os.getenv("FRESHBOOKS_CLIENT_SECRET")
                
                if not client_id or not client_secret:
                    return [TextContent(
                        type="text",
                        text=json.dumps({
                            "error": "FreshBooks client ID and secret must be set in environment variables",
                            "required_vars": ["FRESHBOOKS_CLIENT_ID", "FRESHBOOKS_CLIENT_SECRET"]
                        }, indent=2)
                    )]
                
                config = FreshBooksOAuthConfig(
                    client_id=client_id,
                    client_secret=client_secret
                )
                self.freshbooks_client = FreshBooksOAuthClient(config)
            
            # Start callback server
            self.callback_server = HTTPServer(('localhost', 8080), OAuthCallbackHandler)
            self.callback_server.auth_code = None
            self.callback_server.auth_error = None
            
            # Start server in background thread
            server_thread = threading.Thread(target=self.callback_server.serve_forever)
            server_thread.daemon = True
            server_thread.start()
            
            # Get authorization URL
            auth_url = await self.freshbooks_client.start_oauth_flow()
            
            # Open browser
            webbrowser.open(auth_url)
            
            # Wait for callback
            timeout = 300  # 5 minutes
            start_time = time.time()
            
            while time.time() - start_time < timeout:
                if self.callback_server.auth_code:
                    # Exchange code for token
                    token_response = await self.freshbooks_client.exchange_code_for_token(
                        self.callback_server.auth_code
                    )
                    
                    # Set access token
                    await self.freshbooks_client.set_access_token(token_response['access_token'])
                    
                    # Get identity to extract account info
                    identity = await self.freshbooks_client.get_identity()
                    
                    # Stop callback server
                    self.callback_server.shutdown()
                    
                    return [TextContent(
                        type="text",
                        text=json.dumps({
                            "success": "Authentication successful!",
                            "access_token": token_response.get('access_token', '')[:20] + "...",
                            "account_id": self.freshbooks_client.account_id,
                            "business_id": self.freshbooks_client.business_id,
                            "identity": identity
                        }, indent=2)
                    )]
                
                elif self.callback_server.auth_error:
                    # Stop callback server
                    self.callback_server.shutdown()
                    
                    return [TextContent(
                        type="text",
                        text=json.dumps({
                            "error": f"Authentication failed: {self.callback_server.auth_error}"
                        }, indent=2)
                    )]
                
                await asyncio.sleep(1)
            
            # Timeout
            self.callback_server.shutdown()
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "error": "Authentication timeout. Please try again."
                }, indent=2)
            )]
            
        except Exception as e:
            if self.callback_server:
                self.callback_server.shutdown()
            
            return [TextContent(
                type="text",
                text=json.dumps({"error": str(e)}, indent=2)
            )]
    
    async def run(self):
        """Run the MCP server."""
        from mcp.server.stdio import stdio_server
        
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="freshbooks-oauth-mcp",
                    server_version="0.1.0",
                    capabilities=self.server.get_capabilities(
                        notification_options=None,
                        experimental_capabilities={}
                    )
                )
            )


async def main():
    """Main entry point."""
    server = FreshBooksOAuthMCPServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
