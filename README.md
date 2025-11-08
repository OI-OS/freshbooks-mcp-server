# FreshBooks MCP Server

> **⚠️ For AI Agents:** This repository includes an [OI.md](OI.md) file with comprehensive installation and configuration instructions specifically designed for AI agents installing this server in OI OS (Brain Trust 4) environments. Please refer to [OI.md](OI.md) for step-by-step setup instructions, intent mappings, parameter rules, and troubleshooting guidance.

<div align="center">

# Freshbooks Mcp Server

[![GitHub stars](https://img.shields.io/github/stars/OI-OS/freshbooks-mcp-server?style=social)](https://github.com/OI-OS/freshbooks-mcp-server/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/OI-OS/freshbooks-mcp-server?style=social)](https://github.com/OI-OS/freshbooks-mcp-server/network)
[![GitHub watchers](https://img.shields.io/github/watchers/OI-OS/freshbooks-mcp-server?style=social)](https://github.com/OI-OS/freshbooks-mcp-server/watchers)

[![License](https://img.shields.io/github/license/OI-OS/freshbooks-mcp-server?style=for-the-badge)](https://github.com/OI-OS/freshbooks-mcp-server/blob/main/LICENSE)
[![Issues](https://img.shields.io/github/issues/OI-OS/freshbooks-mcp-server?style=for-the-badge)](https://github.com/OI-OS/freshbooks-mcp-server/issues)
[![Pull Requests](https://img.shields.io/github/issues-pr/OI-OS/freshbooks-mcp-server?style=for-the-badge)](https://github.com/OI-OS/freshbooks-mcp-server/pulls)
[![Last Commit](https://img.shields.io/github/last-commit/OI-OS/freshbooks-mcp-server?style=for-the-badge)](https://github.com/OI-OS/freshbooks-mcp-server/commits)

[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![MCP](https://img.shields.io/badge/Model_Context_Protocol-DC143C?style=for-the-badge)](https://modelcontextprotocol.io)

[![Commit Activity](https://img.shields.io/github/commit-activity/m/OI-OS/freshbooks-mcp-server?style=flat-square)](https://github.com/OI-OS/freshbooks-mcp-server/pulse)
[![Code Size](https://img.shields.io/github/languages/code-size/OI-OS/freshbooks-mcp-server?style=flat-square)](https://github.com/OI-OS/freshbooks-mcp-server)
[![Contributors](https://img.shields.io/github/contributors/OI-OS/freshbooks-mcp-server?style=flat-square)](https://github.com/OI-OS/freshbooks-mcp-server/graphs/contributors)

</div>

A Model Context Protocol (MCP) server for integrating FreshBooks with GenAI applications.

## Overview

Small business accounting software

## Features

- Comprehensive FreshBooks API coverage
- Multiple authentication methods
- Enterprise-ready with rate limiting
- Full error handling and retry logic
- Async support for better performance

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- FreshBooks account with API access

## Installation

### Install from Source

1. Clone this repository:
```bash
git clone https://github.com/OI-OS/freshbooks-mcp-server.git
cd freshbooks-mcp-server
```

2. Install dependencies:
```bash
pip install -e .
```

Or install dependencies directly:
```bash
pip install httpx pydantic pydantic-settings python-dotenv mcp
```

3. Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

4. Configure your FreshBooks credentials in `.env`:
   - `FRESHBOOKS_API_TOKEN` - Your FreshBooks API token (for simple authentication)
   - `FRESHBOOKS_BUSINESS_ID` - Your FreshBooks business ID (for simple authentication)
   - `FRESHBOOKS_CLIENT_ID` - Your OAuth client ID (for OAuth authentication)
   - `FRESHBOOKS_CLIENT_SECRET` - Your OAuth client secret (for OAuth authentication)

**Note:** Never commit your `.env` file or token files to version control. They are already excluded in `.gitignore`.

## AI Installation Guide (OI OS / Brain Trust 4)

This section provides step-by-step instructions for AI assistants to install and configure the FreshBooks MCP server in OI OS environments.

### Step 1: Install via OI Command

```bash
./oi install https://github.com/OI-OS/freshbooks-mcp-server.git
```

The installation will:
- Clone the repository to `MCP-servers/freshbooks-mcp-server/`
- Install Python dependencies
- Auto-detect the server type

### Step 2: Build and Install Dependencies

```bash
cd MCP-servers/freshbooks-mcp-server
pip3 install -e .
```

### Step 3: Configure OAuth Credentials

Add the following to your project root `.env` file:

```bash
# FreshBooks OAuth Configuration
FRESHBOOKS_CLIENT_ID=your_client_id_here
FRESHBOOKS_CLIENT_SECRET=your_client_secret_here
FRESHBOOKS_REDIRECT_URI=https://localhost:8080/callback

# FreshBooks Account Information (obtained after authentication)
FRESHBOOKS_ACCOUNT_ID=your_account_id_here
FRESHBOOKS_BUSINESS_ID=your_business_id_here
FRESHBOOKS_BUSINESS_NAME=your_business_name
FRESHBOOKS_USER_EMAIL=your_email@example.com
FRESHBOOKS_USER_NAME=Your Name
```

### Step 4: Connect the Server

Connect the OAuth server variant:

```bash
export FRESHBOOKS_CLIENT_ID=your_client_id_here
export FRESHBOOKS_CLIENT_SECRET=your_client_secret_here
export FRESHBOOKS_REDIRECT_URI=https://localhost:8080/callback

./brain-trust4 connect freshbooks-mcp-server python3 ./MCP-servers/freshbooks-mcp-server/src/freshbooks_mcp/simple_oauth_server.py
```

### Step 5: Authenticate (First Time)

The OAuth flow requires manual browser interaction. Two methods:

#### Method A: Automatic Authentication (Interactive)

```bash
./brain-trust4 call freshbooks-mcp-server authenticate '{}'
```

This will:
1. Open a browser for OAuth authorization
2. Wait for user to complete authorization
3. Exchange authorization code for access token
4. Save token to `~/.freshbooks_token`

**Note:** This command may timeout if run non-interactively. Use Method B for automation.

#### Method B: Manual Token Exchange

1. **Get Authorization URL:**
   ```bash
   # Manually construct or trigger OAuth URL
   # URL format: https://auth.freshbooks.com/oauth/authorize?response_type=code&client_id=YOUR_CLIENT_ID&redirect_uri=https://localhost:8080/callback
   ```

2. **User completes authorization in browser** and receives authorization code

3. **Exchange code for access token:**
   ```bash
   export FRESHBOOKS_CLIENT_ID=your_client_id_here
   export FRESHBOOKS_CLIENT_SECRET=your_client_secret_here
   export FRESHBOOKS_REDIRECT_URI=https://localhost:8080/callback
   
   python3 -c "
   import asyncio
   import httpx
   import json
   import os
   import time
   
   async def exchange_code():
       client_id = os.getenv('FRESHBOOKS_CLIENT_ID')
       client_secret = os.getenv('FRESHBOOKS_CLIENT_SECRET')
       redirect_uri = os.getenv('FRESHBOOKS_REDIRECT_URI')
       auth_code = 'AUTHORIZATION_CODE_FROM_USER'  # Replace with actual code
       
       async with httpx.AsyncClient() as client:
           response = await client.post(
               'https://api.freshbooks.com/auth/oauth/token',
               data={
                   'grant_type': 'authorization_code',
                   'client_id': client_id,
                   'client_secret': client_secret,
                   'redirect_uri': redirect_uri,
                   'code': auth_code
               },
               headers={'Content-Type': 'application/x-www-form-urlencoded'}
           )
           result = response.json()
           print('Access Token:', result['access_token'])
           print('Account ID:', result['account_id'])
           print('Business ID:', result['business_id'])
           return result
   
   result = asyncio.run(exchange_code())
   "
   ```

4. **Save token to `~/.freshbooks_token`:**
   ```bash
   python3 -c "
   import json
   import time
   import os
   
   token_data = {
       'access_token': 'ACCESS_TOKEN_FROM_STEP_3',
       'account_id': 'ACCOUNT_ID_FROM_STEP_3',
       'business_id': 'BUSINESS_ID_FROM_STEP_3',
       'timestamp': time.time()
   }
   
   token_file = os.path.expanduser('~/.freshbooks_token')
   with open(token_file, 'w') as f:
       json.dump(token_data, f)
   
   print('✅ Token saved to', token_file)
   "
   ```

5. **Optional: Save as FRESHBOOKS_API_TOKEN**

   The OAuth access token can also be used as `FRESHBOOKS_API_TOKEN` for the standard server. Add to `.env`:

   ```bash
   FRESHBOOKS_API_TOKEN=your_oauth_access_token_here
   FRESHBOOKS_BUSINESS_ID=your_business_id_here
   ```

   **Important:** OAuth tokens expire in ~12 hours. The OAuth server automatically handles token refresh, while the standard server will need manual token updates.

### Step 6: Verify Installation

Test the connection:

```bash
./oi "get freshbooks clients"
```

Or directly:

```bash
./brain-trust4 call freshbooks-mcp-server get_clients '{}'
```

### Troubleshooting for AI Installations

- **"Not authenticated" error**: Run authentication flow (Step 5)
- **Token expired**: Re-authenticate or use OAuth server which auto-refreshes
- **Environment variables not found**: Export them before connecting server, or add to `.env` and source it
- **Module not found**: Ensure `pip3 install -e .` completed successfully in the server directory

### Quick Reference Commands

```bash
# Install
./oi install https://github.com/OI-OS/freshbooks-mcp-server.git

# Connect OAuth server
export FRESHBOOKS_CLIENT_ID=... FRESHBOOKS_CLIENT_SECRET=... FRESHBOOKS_REDIRECT_URI=...
./brain-trust4 connect freshbooks-mcp-server python3 ./MCP-servers/freshbooks-mcp-server/src/freshbooks_mcp/simple_oauth_server.py

# Connect standard server (if you have API token)
./brain-trust4 connect freshbooks-api python3 ./MCP-servers/freshbooks-mcp-server/src/freshbooks_mcp/server.py

# Test
./oi "get freshbooks clients"
```

## Configuration for AI Clients

### Using with Cursor

1. Open Cursor settings
2. Navigate to **Features** → **Model Context Protocol**
3. Click **Edit Config** or manually edit your MCP settings file:
   - **macOS/Linux**: `~/.cursor/mcp.json` or project-level `.cursor/mcp.json`
   - **Windows**: `%APPDATA%\Cursor\mcp.json` or project-level `.cursor\mcp.json`

4. Add the FreshBooks MCP server configuration:

```json
{
  "mcpServers": {
    "freshbooks": {
      "command": "python3",
      "args": ["/absolute/path/to/freshbooks-mcp-server/src/freshbooks_mcp/server.py"],
      "env": {
        "FRESHBOOKS_API_TOKEN": "your_freshbooks_api_token_here",
        "FRESHBOOKS_BUSINESS_ID": "your_business_id_here"
      }
    }
  }
}
```

**For OAuth authentication**, use:
```json
{
  "mcpServers": {
    "freshbooks-oauth": {
      "command": "python3",
      "args": ["/absolute/path/to/freshbooks-mcp-server/src/freshbooks_mcp/simple_oauth_server.py"],
      "env": {
        "FRESHBOOKS_CLIENT_ID": "your_oauth_client_id_here",
        "FRESHBOOKS_CLIENT_SECRET": "your_oauth_client_secret_here"
      }
    }
  }
}
```

**Alternative: Using project-level configuration**

Create `.cursor/mcp.json` in your project root:
```json
{
  "mcpServers": {
    "freshbooks": {
      "command": "python3",
      "args": ["./MCP-servers/freshbooks-mcp-server/src/freshbooks_mcp/server.py"],
      "env": {
        "FRESHBOOKS_API_TOKEN": "${FRESHBOOKS_API_TOKEN}",
        "FRESHBOOKS_BUSINESS_ID": "${FRESHBOOKS_BUSINESS_ID}"
      }
    }
  }
}
```

5. Restart Cursor to apply changes

### Using with Claude Desktop

1. Locate your Claude Desktop configuration file:
   - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
   - **Linux**: `~/.config/claude/claude_desktop_config.json`

2. Edit the configuration file and add:

```json
{
  "mcpServers": {
    "freshbooks": {
      "command": "python3",
      "args": ["/absolute/path/to/freshbooks-mcp-server/src/freshbooks_mcp/server.py"],
      "env": {
        "FRESHBOOKS_API_TOKEN": "your_freshbooks_api_token_here",
        "FRESHBOOKS_BUSINESS_ID": "your_business_id_here"
      }
    }
  }
}
```

3. Save the file and restart Claude Desktop

### Using with VS Code (with MCP Extension)

1. Install an MCP extension for VS Code (if available)
2. Create or edit `.vscode/mcp.json` in your project:

```json
{
  "servers": {
    "freshbooks": {
      "command": "python3",
      "args": ["/absolute/path/to/freshbooks-mcp-server/src/freshbooks_mcp/server.py"],
      "env": {
        "FRESHBOOKS_API_TOKEN": "your_freshbooks_api_token_here",
        "FRESHBOOKS_BUSINESS_ID": "your_business_id_here"
      },
      "type": "stdio"
    }
  }
}
```

### Using with Continue.dev

1. Open your Continue.dev configuration file:
   - Location: `~/.continue/config.json` (or `%USERPROFILE%\.continue\config.json` on Windows)

2. Add to the `mcpServers` array:

```json
{
  "mcpServers": [
    {
      "name": "freshbooks",
      "command": "python3",
      "args": ["/absolute/path/to/freshbooks-mcp-server/src/freshbooks_mcp/server.py"],
      "env": {
        "FRESHBOOKS_API_TOKEN": "your_freshbooks_api_token_here",
        "FRESHBOOKS_BUSINESS_ID": "your_business_id_here"
      }
    }
  ]
}
```

3. Restart Continue.dev

## Server Variants

This repository includes multiple server implementations:

1. **Standard Server** (`src/freshbooks_mcp/server.py`) - Uses MCP SDK with simple API token authentication
2. **OAuth Server** (`src/freshbooks_mcp/oauth_server.py`) - Full OAuth flow with token refresh
3. **Simple OAuth Server** (`src/freshbooks_mcp/simple_oauth_server.py`) - Simplified OAuth with interactive authentication
4. **Raw MCP Server** (`mcp_server.py`) - Direct MCP protocol implementation
5. **Simple Server** (`simple_server.py`) - Minimal implementation for testing

Choose the server that best fits your authentication needs.

## Quick Start

To test the server manually:

```bash
# Using the standard server
python3 src/freshbooks_mcp/server.py

# Or using the run script
python3 run_server.py
```

The server communicates via stdio (standard input/output) for MCP protocol.

## Available Tools

Once configured, the following FreshBooks tools will be available to your AI assistant:

### Read Operations
- **`get_clients`** - Get all clients from your FreshBooks account
- **`get_invoices`** - Retrieve all invoices
- **`get_projects`** - Get all projects
- **`get_expenses`** - Retrieve all expenses
- **`get_time_entries`** - Get all time tracking entries

### Write Operations (OAuth Server Only)
- **`create_client`** - Create a new client in FreshBooks
- **`create_invoice`** - Create a new invoice
- **`create_project`** - Create a new project

### OAuth-Specific Tools (OAuth Server)
- **`authenticate`** - Start the OAuth authentication flow (opens browser for authorization)

## Troubleshooting

### Server Not Appearing in Cursor/Claude

1. **Check Python path**: Ensure `python3` is in your PATH. Test with:
   ```bash
   which python3  # macOS/Linux
   where python3  # Windows
   ```

2. **Verify absolute paths**: Use absolute paths in your MCP configuration. Relative paths may not work.

3. **Check environment variables**: Ensure your FreshBooks credentials are correctly set in the `env` section of your MCP configuration.

4. **Restart the client**: After making configuration changes, fully restart Cursor, Claude Desktop, or your AI client.

5. **Check logs**: Look for error messages in:
   - Cursor: View → Output → select "Model Context Protocol"
   - Claude Desktop: Check application logs

### Authentication Issues

- **API Token**: Ensure your `FRESHBOOKS_API_TOKEN` is valid and has proper permissions
- **Business ID**: Verify your `FRESHBOOKS_BUSINESS_ID` matches your FreshBooks account
- **OAuth**: For OAuth servers, ensure your `FRESHBOOKS_CLIENT_ID` and `FRESHBOOKS_CLIENT_SECRET` are correct

### Python Module Not Found

If you get "ModuleNotFoundError", install dependencies:
```bash
cd /path/to/freshbooks-mcp-server
pip install -e .
```

## Getting FreshBooks API Credentials

1. **API Token Authentication**:
   - Log in to your FreshBooks account
   - Go to Settings → Integrations → API
   - Generate an API token
   - Note your Business/Account ID

2. **OAuth Authentication**:
   - Visit [FreshBooks Developer Portal](https://www.freshbooks.com/api/authentication)
   - Create a new OAuth application
   - Set redirect URI: `https://localhost:8080/callback`
   - Copy Client ID and Client Secret

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - see LICENSE file for details
