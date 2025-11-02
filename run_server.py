#!/usr/bin/env python3
"""Simple wrapper to run the FreshBooks MCP server."""

import os
import sys
import asyncio

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from freshbooks_mcp.server import main

if __name__ == "__main__":
    asyncio.run(main())


