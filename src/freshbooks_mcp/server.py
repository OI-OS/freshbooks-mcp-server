#!/usr/bin/env python3
"""FreshBooks MCP Server implementation."""

import asyncio
import json
import os
from typing import Any, Dict, List, Optional

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


class FreshBooksConfig(BaseModel):
    """FreshBooks configuration."""
    api_token: str = Field(..., description="FreshBooks API token")
    business_id: str = Field(..., description="FreshBooks business ID")
    base_url: str = Field(default="https://api.freshbooks.com", description="FreshBooks API base URL")


class FreshBooksClient:
    """FreshBooks API client."""
    
    def __init__(self, config: FreshBooksConfig):
        self.config = config
        self.client = httpx.AsyncClient(
            base_url=config.base_url,
            headers={
                "Authorization": f"Bearer {config.api_token}",
                "Content-Type": "application/json",
            },
            timeout=30.0,
        )
    
    async def get_clients(self) -> Dict[str, Any]:
        """Get all clients."""
        response = await self.client.get(f"/accounting/account/{self.config.business_id}/users/clients")
        return response.json()
    
    async def get_invoices(self) -> Dict[str, Any]:
        """Get all invoices."""
        response = await self.client.get(f"/accounting/account/{self.config.business_id}/invoices/invoices")
        return response.json()
    
    async def get_projects(self) -> Dict[str, Any]:
        """Get all projects."""
        response = await self.client.get(f"/accounting/account/{self.config.business_id}/projects/projects")
        return response.json()
    
    async def get_expenses(self) -> Dict[str, Any]:
        """Get all expenses."""
        response = await self.client.get(f"/accounting/account/{self.config.business_id}/expenses/expenses")
        return response.json()
    
    async def get_time_entries(self) -> Dict[str, Any]:
        """Get all time entries."""
        response = await self.client.get(f"/accounting/account/{self.config.business_id}/time_entries/time_entries")
        return response.json()
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()


class FreshBooksMCPServer:
    """FreshBooks MCP Server."""
    
    def __init__(self):
        self.server = Server("freshbooks-mcp")
        self.freshbooks_client: Optional[FreshBooksClient] = None
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Setup MCP server handlers."""
        
        @self.server.list_tools()
        async def handle_list_tools() -> List[Tool]:
            """List available tools."""
            return [
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
            if not self.freshbooks_client:
                # Initialize client if not already done
                api_token = os.getenv("FRESHBOOKS_API_TOKEN")
                business_id = os.getenv("FRESHBOOKS_BUSINESS_ID")
                
                if not api_token or not business_id:
                    return [TextContent(
                        type="text",
                        text=json.dumps({
                            "error": "FreshBooks API token and business ID must be set in environment variables",
                            "required_vars": ["FRESHBOOKS_API_TOKEN", "FRESHBOOKS_BUSINESS_ID"]
                        }, indent=2)
                    )]
                
                config = FreshBooksConfig(
                    api_token=api_token,
                    business_id=business_id
                )
                self.freshbooks_client = FreshBooksClient(config)
            
            try:
                if name == "get_clients":
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
    
    async def run(self):
        """Run the MCP server."""
        from mcp.server.stdio import stdio_server
        
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="freshbooks-mcp",
                    server_version="0.1.0",
                    capabilities=self.server.get_capabilities(
                        notification_options=None,
                        experimental_capabilities={}
                    )
                )
            )


async def main():
    """Main entry point."""
    server = FreshBooksMCPServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
