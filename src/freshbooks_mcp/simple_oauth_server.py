#!/usr/bin/env python3
"""Simple FreshBooks OAuth MCP Server implementation."""

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
import ssl
import tempfile
import subprocess

import httpx


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


class FreshBooksOAuthClient:
    """FreshBooks OAuth API client."""
    
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str = "https://localhost:8080/callback"):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.base_url = "https://api.freshbooks.com"
        self.auth_url = "https://auth.freshbooks.com/oauth/authorize"
        self.token_url = "https://api.freshbooks.com/auth/oauth/token"
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None
        self.account_id: Optional[str] = None
        self.business_id: Optional[str] = None
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                "Content-Type": "application/json",
            },
            timeout=30.0,
        )
    
    async def start_oauth_flow(self) -> str:
        """Start OAuth flow and return authorization URL."""
        params = {
            'response_type': 'code',
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri
        }
        
        auth_url = f"{self.auth_url}?" + urllib.parse.urlencode(params)
        return auth_url
    
    async def exchange_code_for_token(self, auth_code: str) -> Dict[str, Any]:
        """Exchange authorization code for access token."""
        data = {
            'grant_type': 'authorization_code',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'redirect_uri': self.redirect_uri,
            'code': auth_code
        }
        
        response = await self.client.post(
            self.token_url,
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
    
    async def create_client(self, first_name: str, last_name: str, email: str = None, phone: str = None, address: str = None, city: str = None, state: str = None, country: str = None, postal_code: str = None) -> Dict[str, Any]:
        """Create a new client."""
        if not self.account_id:
            return {"error": "No account_id available. Please authenticate first."}
        
        client_data = {
            "client": {
                "first_name": first_name,
                "last_name": last_name
            }
        }
        
        if email:
            client_data["client"]["email"] = email
        
        if phone:
            client_data["client"]["phone"] = phone
        
        if address or city or state or country or postal_code:
            client_data["client"]["address"] = {}
            if address:
                client_data["client"]["address"]["street"] = address
            if city:
                client_data["client"]["address"]["city"] = city
            if state:
                client_data["client"]["address"]["province"] = state
            if country:
                client_data["client"]["address"]["country"] = country
            if postal_code:
                client_data["client"]["address"]["postal_code"] = postal_code
        
        response = await self.client.post(f"/accounting/account/{self.account_id}/users/clients", json=client_data)
        response.raise_for_status()
        return response.json()
    
    async def create_invoice(self, client_id: int, lines: list, date: str = None, due_date: str = None, notes: str = None) -> Dict[str, Any]:
        """Create a new invoice."""
        if not self.account_id:
            return {"error": "No account_id available. Please authenticate first."}
        
        invoice_data = {
            "invoice": {
                "client_id": client_id,
                "lines": lines
            }
        }
        
        if date:
            invoice_data["invoice"]["date"] = date
        
        if due_date:
            invoice_data["invoice"]["due_date"] = due_date
        
        if notes:
            invoice_data["invoice"]["notes"] = notes
        
        response = await self.client.post(f"/accounting/account/{self.account_id}/invoices/invoices", json=invoice_data)
        response.raise_for_status()
        return response.json()
    
    async def create_project(self, name: str, client_id: int, description: str = None, bill_method: str = "project_rate", rate: float = None) -> Dict[str, Any]:
        """Create a new project."""
        if not self.account_id:
            return {"error": "No account_id available. Please authenticate first."}
        
        project_data = {
            "project": {
                "name": name,
                "client_id": client_id,
                "bill_method": bill_method
            }
        }
        
        if description:
            project_data["project"]["description"] = description
        
        if rate is not None:
            project_data["project"]["rate"] = rate
        
        response = await self.client.post(f"/accounting/account/{self.account_id}/projects/projects", json=project_data)
        response.raise_for_status()
        return response.json()
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()


class FreshBooksSimpleOAuthMCPServer:
    """Simple FreshBooks OAuth MCP Server."""
    
    def __init__(self):
        self.freshbooks_client: Optional[FreshBooksOAuthClient] = None
        self.callback_server: Optional[HTTPServer] = None
        self.token_file = os.path.expanduser("~/.freshbooks_token")
    
    def _send_response(self, response: Dict[str, Any]):
        """Send a JSON response."""
        print(json.dumps(response))
        sys.stdout.flush()
    
    def _send_error(self, message: str, id: Optional[int] = None):
        """Send an error response."""
        error_response = {
            "jsonrpc": "2.0",
            "error": {
                "code": -32000,
                "message": message
            }
        }
        if id is not None:
            error_response["id"] = id
        self._send_response(error_response)
    
    def _save_token(self, access_token: str, account_id: str, business_id: str):
        """Save access token to file."""
        token_data = {
            "access_token": access_token,
            "account_id": account_id,
            "business_id": business_id,
            "timestamp": time.time()
        }
        with open(self.token_file, 'w') as f:
            json.dump(token_data, f)
    
    def _load_token(self) -> Optional[Dict[str, Any]]:
        """Load access token from file."""
        try:
            if os.path.exists(self.token_file):
                with open(self.token_file, 'r') as f:
                    token_data = json.load(f)
                    # Check if token is less than 1 hour old
                    if time.time() - token_data.get('timestamp', 0) < 3600:
                        return token_data
        except (json.JSONDecodeError, KeyError, FileNotFoundError):
            pass
        return None
    
    async def handle_initialize(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle initialize request."""
        return {
            "jsonrpc": "2.0",
            "id": request.get("id"),
            "result": {
                "serverInfo": {
                    "name": "freshbooks-oauth-mcp",
                    "version": "0.1.0"
                },
                "capabilities": {
                    "tools": {}
                }
            }
        }
    
    async def handle_list_tools(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle list tools request."""
        tools = [
            {
                "name": "authenticate",
                "description": "Start OAuth authentication flow with FreshBooks",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "get_identity",
                "description": "Get FreshBooks identity information",
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
            },
            {
                "name": "create_client",
                "description": "Create a new client in FreshBooks",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "first_name": {"type": "string", "description": "Client's first name"},
                        "last_name": {"type": "string", "description": "Client's last name"},
                        "email": {"type": "string", "description": "Client's email address"},
                        "phone": {"type": "string", "description": "Client's phone number"},
                        "address": {"type": "string", "description": "Client's street address"},
                        "city": {"type": "string", "description": "Client's city"},
                        "state": {"type": "string", "description": "Client's state/province"},
                        "country": {"type": "string", "description": "Client's country"},
                        "postal_code": {"type": "string", "description": "Client's postal/ZIP code"}
                    },
                    "required": ["first_name", "last_name"]
                }
            },
            {
                "name": "create_invoice",
                "description": "Create a new invoice in FreshBooks",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "client_id": {"type": "integer", "description": "Client ID"},
                        "lines": {"type": "array", "description": "Invoice line items", "items": {"type": "object"}},
                        "date": {"type": "string", "description": "Invoice date (YYYY-MM-DD)"},
                        "due_date": {"type": "string", "description": "Due date (YYYY-MM-DD)"},
                        "notes": {"type": "string", "description": "Invoice notes"}
                    },
                    "required": ["client_id", "lines"]
                }
            },
            {
                "name": "create_project",
                "description": "Create a new project in FreshBooks",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "Project name"},
                        "client_id": {"type": "integer", "description": "Client ID"},
                        "description": {"type": "string", "description": "Project description"},
                        "bill_method": {"type": "string", "description": "Billing method (project_rate, task_rate, staff_rate)"},
                        "rate": {"type": "number", "description": "Project rate"}
                    },
                    "required": ["name", "client_id"]
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
            if tool_name == "authenticate":
                result = await self._handle_authenticate()
            elif tool_name == "get_identity":
                result = await self._handle_get_identity()
            elif tool_name == "get_clients":
                result = await self._handle_get_clients()
            elif tool_name == "get_invoices":
                result = await self._handle_get_invoices()
            elif tool_name == "get_projects":
                result = await self._handle_get_projects()
            elif tool_name == "get_expenses":
                result = await self._handle_get_expenses()
            elif tool_name == "get_time_entries":
                result = await self._handle_get_time_entries()
            elif tool_name == "create_client":
                result = await self._handle_create_client(arguments)
            elif tool_name == "create_invoice":
                result = await self._handle_create_invoice(arguments)
            elif tool_name == "create_project":
                result = await self._handle_create_project(arguments)
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
                        {"type": "text", "text": json.dumps(result, indent=2)}
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
    
    async def _handle_authenticate(self) -> Dict[str, Any]:
        """Handle OAuth authentication."""
        try:
            # Initialize client if not already done
            if not self.freshbooks_client:
                client_id = os.getenv("FRESHBOOKS_CLIENT_ID")
                client_secret = os.getenv("FRESHBOOKS_CLIENT_SECRET")
                
                if not client_id or not client_secret:
                    return {
                        "error": "FreshBooks client ID and secret must be set in environment variables",
                        "required_vars": ["FRESHBOOKS_CLIENT_ID", "FRESHBOOKS_CLIENT_SECRET"]
                    }
                
                self.freshbooks_client = FreshBooksOAuthClient(client_id, client_secret)
            
            # Start HTTPS callback server
            self.callback_server = HTTPServer(('localhost', 8080), OAuthCallbackHandler)
            self.callback_server.auth_code = None
            self.callback_server.auth_error = None
            
            # Create SSL context with self-signed certificate
            context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            
            # Generate a temporary self-signed certificate
            cert_file = tempfile.NamedTemporaryFile(mode='w', suffix='.pem', delete=False)
            key_file = tempfile.NamedTemporaryFile(mode='w', suffix='.pem', delete=False)
            
            try:
                # Generate self-signed certificate using openssl
                subprocess.run([
                    'openssl', 'req', '-x509', '-newkey', 'rsa:2048', '-keyout', key_file.name,
                    '-out', cert_file.name, '-days', '1', '-nodes', '-subj', '/CN=localhost'
                ], check=True, capture_output=True)
                
                context.load_cert_chain(cert_file.name, key_file.name)
                self.callback_server.socket = context.wrap_socket(self.callback_server.socket, server_side=True)
                
            except (subprocess.CalledProcessError, FileNotFoundError):
                # Fallback: create a simple SSL context without certificate
                context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE
                # This will cause a certificate warning but should work
                self.callback_server.socket = context.wrap_socket(self.callback_server.socket, server_side=True)
            
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
                    
                    # Save token for future use
                    self._save_token(
                        token_response['access_token'],
                        self.freshbooks_client.account_id,
                        self.freshbooks_client.business_id
                    )
                    
                    # Stop callback server
                    self.callback_server.shutdown()
                    
                    return {
                        "success": "Authentication successful!",
                        "access_token": token_response.get('access_token', '')[:20] + "...",
                        "account_id": self.freshbooks_client.account_id,
                        "business_id": self.freshbooks_client.business_id,
                        "identity": identity
                    }
                
                elif self.callback_server.auth_error:
                    # Stop callback server
                    self.callback_server.shutdown()
                    
                    return {
                        "error": f"Authentication failed: {self.callback_server.auth_error}"
                    }
                
                await asyncio.sleep(1)
            
            # Timeout
            self.callback_server.shutdown()
            
            return {
                "error": "Authentication timeout. Please try again."
            }
            
        except Exception as e:
            if self.callback_server:
                self.callback_server.shutdown()
            
            return {"error": str(e)}
    
    async def _ensure_authenticated(self) -> bool:
        """Ensure we have a valid access token."""
        # Try to load existing token
        token_data = self._load_token()
        if token_data:
            # Initialize client if not already done
            if not self.freshbooks_client:
                client_id = os.getenv("FRESHBOOKS_CLIENT_ID")
                client_secret = os.getenv("FRESHBOOKS_CLIENT_SECRET")
                
                if not client_id or not client_secret:
                    return False
                
                self.freshbooks_client = FreshBooksOAuthClient(client_id, client_secret)
            
            # Set the access token
            await self.freshbooks_client.set_access_token(token_data['access_token'])
            self.freshbooks_client.account_id = token_data.get('account_id')
            self.freshbooks_client.business_id = token_data.get('business_id')
            return True
        
        return False
    
    async def _handle_get_identity(self) -> Dict[str, Any]:
        """Handle get identity request."""
        if not await self._ensure_authenticated():
            return {"error": "Not authenticated. Please call 'authenticate' first."}
        
        return await self.freshbooks_client.get_identity()
    
    async def _handle_get_clients(self) -> Dict[str, Any]:
        """Handle get clients request."""
        if not await self._ensure_authenticated():
            return {"error": "Not authenticated. Please call 'authenticate' first."}
        
        return await self.freshbooks_client.get_clients()
    
    async def _handle_get_invoices(self) -> Dict[str, Any]:
        """Handle get invoices request."""
        if not await self._ensure_authenticated():
            return {"error": "Not authenticated. Please call 'authenticate' first."}
        
        return await self.freshbooks_client.get_invoices()
    
    async def _handle_get_projects(self) -> Dict[str, Any]:
        """Handle get projects request."""
        if not await self._ensure_authenticated():
            return {"error": "Not authenticated. Please call 'authenticate' first."}
        
        return await self.freshbooks_client.get_projects()
    
    async def _handle_get_expenses(self) -> Dict[str, Any]:
        """Handle get expenses request."""
        if not await self._ensure_authenticated():
            return {"error": "Not authenticated. Please call 'authenticate' first."}
        
        return await self.freshbooks_client.get_expenses()
    
    async def _handle_get_time_entries(self) -> Dict[str, Any]:
        """Handle get time entries request."""
        if not await self._ensure_authenticated():
            return {"error": "Not authenticated. Please call 'authenticate' first."}
        
        return await self.freshbooks_client.get_time_entries()
    
    async def _handle_create_client(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle create client request."""
        if not await self._ensure_authenticated():
            return {"error": "Not authenticated. Please call 'authenticate' first."}
        
        return await self.freshbooks_client.create_client(
            first_name=arguments.get("first_name"),
            last_name=arguments.get("last_name"),
            email=arguments.get("email"),
            phone=arguments.get("phone"),
            address=arguments.get("address"),
            city=arguments.get("city"),
            state=arguments.get("state"),
            country=arguments.get("country"),
            postal_code=arguments.get("postal_code")
        )
    
    async def _handle_create_invoice(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle create invoice request."""
        if not await self._ensure_authenticated():
            return {"error": "Not authenticated. Please call 'authenticate' first."}
        
        return await self.freshbooks_client.create_invoice(
            client_id=arguments.get("client_id"),
            lines=arguments.get("lines"),
            date=arguments.get("date"),
            due_date=arguments.get("due_date"),
            notes=arguments.get("notes")
        )
    
    async def _handle_create_project(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle create project request."""
        if not await self._ensure_authenticated():
            return {"error": "Not authenticated. Please call 'authenticate' first."}
        
        return await self.freshbooks_client.create_project(
            name=arguments.get("name"),
            client_id=arguments.get("client_id"),
            description=arguments.get("description"),
            bill_method=arguments.get("bill_method", "project_rate"),
            rate=arguments.get("rate")
        )
    
    async def run(self):
        """Run the MCP server."""
        while True:
            try:
                line = await asyncio.to_thread(sys.stdin.readline)
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
                self._send_error(f"Server internal error: {e}")


async def main():
    """Main entry point."""
    server = FreshBooksSimpleOAuthMCPServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
