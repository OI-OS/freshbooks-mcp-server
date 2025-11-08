# FreshBooks MCP Server - AI Agent Installation Guide

This guide provides comprehensive installation instructions for AI agents installing the FreshBooks MCP server in OI OS (Brain Trust 4) environments, as well as end-user setup instructions.

## Table of Contents

1. [AI Agent Quick Installation](#ai-agent-quick-installation)
2. [Prerequisites](#prerequisites)
3. [Full Installation Steps](#full-installation-steps)
4. [Configuring Authentication](#configuring-authentication)
5. [Connecting to OI OS](#connecting-to-oi-os)
6. [Creating Intent Mappings](#creating-intent-mappings)
7. [Creating Parameter Rules](#creating-parameter-rules)
8. [End User Setup](#end-user-setup)
9. [Verification & Testing](#verification--testing)
10. [Troubleshooting](#troubleshooting)

---

## AI Agent Quick Installation

**⚠️ For AI Agents: Use Direct Calls for Reliability**

AI agents should prefer **direct `brain-trust4 call` commands** over natural language queries for maximum reliability. Natural language commands can timeout or have parameter extraction issues. Direct calls bypass intent mapping and parameter extraction, providing consistent results.

**Example:**
```bash
# ✅ RECOMMENDED for AI agents: Direct call
./brain-trust4 call freshbooks-mcp-server get_clients '{}'

# ⚠️ FALLBACK: Natural language (may timeout or fail parameter extraction)
./oi "get freshbooks clients"
```

For AI agents using OI OS, execute the following commands:

```bash
# 1. Install the server
./oi install https://github.com/OI-OS/freshbooks-mcp-server.git

# 2. Install Python dependencies
cd MCP-servers/freshbooks-mcp-server
pip3 install httpx --user
cd ../../

# 3. Configure authentication in project root .env file
# Option A: OAuth (Recommended) - See "Configuring Authentication" section for detailed instructions
# Add to .env:
# FRESHBOOKS_CLIENT_ID=your_oauth_client_id_here
# FRESHBOOKS_CLIENT_SECRET=your_oauth_client_secret_here
# FRESHBOOKS_REDIRECT_URI=https://localhost:8080/callback
# FRESHBOOKS_BUSINESS_ID=your_business_id_here
#
# Option B: API Token - See "Configuring Authentication" section for detailed instructions
# Add to .env:
# FRESHBOOKS_API_TOKEN=your_api_token_here
# FRESHBOOKS_BUSINESS_ID=your_business_id_here

# 4. Connect the server to OI OS
# NOTE: For OAuth authentication, use simple_oauth_server.py
# NOTE: brain-trust4 automatically loads .env file from project root
export $(grep -E "^FRESHBOOKS" .env | xargs)
./brain-trust4 connect freshbooks-mcp-server python3 ./MCP-servers/freshbooks-mcp-server/src/freshbooks_mcp/simple_oauth_server.py

# 4a. Authenticate (first time only - opens browser for OAuth)
# This requires user interaction in a browser
# After authorization, you'll get a code - exchange it using:
# python3 MCP-servers/freshbooks-mcp-server/exchange_code.py <authorization_code>
# OR use API token authentication with mcp_server.py instead:
# ./brain-trust4 connect freshbooks-mcp-server python3 ./MCP-servers/freshbooks-mcp-server/mcp_server.py

# 5. Create intent mappings and parameter rules (single optimized transaction)
sqlite3 brain-trust4.db << 'SQL'
BEGIN TRANSACTION;

-- Intent mappings for FreshBooks MCP server (35 mappings)
INSERT OR REPLACE INTO intent_mappings (keyword, server_name, tool_name, priority) VALUES 
('freshbooks authenticate', 'freshbooks-mcp-server', 'authenticate', 10),
('freshbooks auth', 'freshbooks-mcp-server', 'authenticate', 10),
('freshbooks login', 'freshbooks-mcp-server', 'authenticate', 10),
('freshbooks get identity', 'freshbooks-mcp-server', 'get_identity', 10),
('freshbooks identity', 'freshbooks-mcp-server', 'get_identity', 10),
('freshbooks whoami', 'freshbooks-mcp-server', 'get_identity', 10),
('freshbooks get clients', 'freshbooks-mcp-server', 'get_clients', 10),
('freshbooks clients', 'freshbooks-mcp-server', 'get_clients', 10),
('freshbooks list clients', 'freshbooks-mcp-server', 'get_clients', 10),
('freshbooks show clients', 'freshbooks-mcp-server', 'get_clients', 10),
('freshbooks get invoices', 'freshbooks-mcp-server', 'get_invoices', 10),
('freshbooks invoices', 'freshbooks-mcp-server', 'get_invoices', 10),
('freshbooks list invoices', 'freshbooks-mcp-server', 'get_invoices', 10),
('freshbooks show invoices', 'freshbooks-mcp-server', 'get_invoices', 10),
('freshbooks get projects', 'freshbooks-mcp-server', 'get_projects', 10),
('freshbooks projects', 'freshbooks-mcp-server', 'get_projects', 10),
('freshbooks list projects', 'freshbooks-mcp-server', 'get_projects', 10),
('freshbooks show projects', 'freshbooks-mcp-server', 'get_projects', 10),
('freshbooks get expenses', 'freshbooks-mcp-server', 'get_expenses', 10),
('freshbooks expenses', 'freshbooks-mcp-server', 'get_expenses', 10),
('freshbooks list expenses', 'freshbooks-mcp-server', 'get_expenses', 10),
('freshbooks show expenses', 'freshbooks-mcp-server', 'get_expenses', 10),
('freshbooks get time entries', 'freshbooks-mcp-server', 'get_time_entries', 10),
('freshbooks time entries', 'freshbooks-mcp-server', 'get_time_entries', 10),
('freshbooks list time entries', 'freshbooks-mcp-server', 'get_time_entries', 10),
('freshbooks show time entries', 'freshbooks-mcp-server', 'get_time_entries', 10),
('freshbooks create client', 'freshbooks-mcp-server', 'create_client', 10),
('freshbooks add client', 'freshbooks-mcp-server', 'create_client', 10),
('freshbooks new client', 'freshbooks-mcp-server', 'create_client', 10),
('freshbooks create invoice', 'freshbooks-mcp-server', 'create_invoice', 10),
('freshbooks add invoice', 'freshbooks-mcp-server', 'create_invoice', 10),
('freshbooks new invoice', 'freshbooks-mcp-server', 'create_invoice', 10),
('freshbooks create project', 'freshbooks-mcp-server', 'create_project', 10),
('freshbooks add project', 'freshbooks-mcp-server', 'create_project', 10),
('freshbooks new project', 'freshbooks-mcp-server', 'create_project', 10);

-- Parameter rules for FreshBooks MCP server (10 rules)
-- Read operations: no required parameters
INSERT OR REPLACE INTO parameter_rules (server_name, tool_name, tool_signature, required_fields, field_generators, patterns) VALUES
('freshbooks-mcp-server', 'authenticate', 'freshbooks-mcp-server::authenticate', '[]', '{}', '[]'),
('freshbooks-mcp-server', 'get_identity', 'freshbooks-mcp-server::get_identity', '[]', '{}', '[]'),
('freshbooks-mcp-server', 'get_clients', 'freshbooks-mcp-server::get_clients', '[]', '{}', '[]'),
('freshbooks-mcp-server', 'get_invoices', 'freshbooks-mcp-server::get_invoices', '[]', '{}', '[]'),
('freshbooks-mcp-server', 'get_projects', 'freshbooks-mcp-server::get_projects', '[]', '{}', '[]'),
('freshbooks-mcp-server', 'get_expenses', 'freshbooks-mcp-server::get_expenses', '[]', '{}', '[]'),
('freshbooks-mcp-server', 'get_time_entries', 'freshbooks-mcp-server::get_time_entries', '[]', '{}', '[]');

-- Create operations: have required fields
INSERT OR REPLACE INTO parameter_rules (server_name, tool_name, tool_signature, required_fields, field_generators, patterns) VALUES
('freshbooks-mcp-server', 'create_client', 'freshbooks-mcp-server::create_client', '["first_name", "last_name"]', '{"first_name": {"FromQuery": "freshbooks-mcp-server::create_client.first_name"}, "last_name": {"FromQuery": "freshbooks-mcp-server::create_client.last_name"}}', '[]'),
('freshbooks-mcp-server', 'create_invoice', 'freshbooks-mcp-server::create_invoice', '["client_id", "lines"]', '{"client_id": {"FromQuery": "freshbooks-mcp-server::create_invoice.client_id"}, "lines": {"FromQuery": "freshbooks-mcp-server::create_invoice.lines"}}', '[]'),
('freshbooks-mcp-server', 'create_project', 'freshbooks-mcp-server::create_project', '["name", "client_id"]', '{"name": {"FromQuery": "freshbooks-mcp-server::create_project.name"}, "client_id": {"FromQuery": "freshbooks-mcp-server::create_project.client_id"}}', '[]');

COMMIT;
SQL

# 6. Add parameter extractors to TOML (already in parameter_extractors.toml.default)
# The extractors for create_client, create_invoice, and create_project are already configured

# 7. Verify installation
./oi list | grep freshbooks
./brain-trust4 call freshbooks-mcp-server get_identity '{}'
./oi "freshbooks get clients"
```

---

## Prerequisites

- Python 3.8 or higher (Python 3.9+ recommended)
- pip (Python package manager)
- FreshBooks account with API access
- OI OS (Brain Trust 4) installed and configured

---

## Full Installation Steps

### Step 1: Clone Repository

The `oi install` command automatically clones the repository to `MCP-servers/freshbooks-mcp-server/`. If installing manually:

```bash
git clone https://github.com/OI-OS/freshbooks-mcp-server.git MCP-servers/freshbooks-mcp-server
cd MCP-servers/freshbooks-mcp-server
```

### Step 2: Install Dependencies

```bash
pip3 install httpx --user
```

**Note:** The `mcp` package requires Python 3.10+, but this server uses `mcp_server.py` which implements the MCP protocol manually and works with Python 3.9+.

### Step 3: Configure Authentication

See [Configuring Authentication](#configuring-authentication) section below.

### Step 4: Connect to OI OS

**Option A: OAuth Authentication (Recommended if you have OAuth credentials)**

```bash
cd /path/to/oi-os-root
export $(grep -E "^FRESHBOOKS" .env | xargs)
./brain-trust4 connect freshbooks-mcp-server python3 ./MCP-servers/freshbooks-mcp-server/src/freshbooks_mcp/simple_oauth_server.py

# Authenticate (first time only - opens browser)
./brain-trust4 call freshbooks-mcp-server authenticate '{}'
```

**Option B: API Token Authentication (If you have an API token)**

```bash
cd /path/to/oi-os-root
./brain-trust4 connect freshbooks-mcp-server python3 ./MCP-servers/freshbooks-mcp-server/mcp_server.py
```

---

## Configuring Authentication

FreshBooks MCP server supports two authentication methods:

### Option 1: OAuth Authentication (Recommended)

OAuth provides automatic token refresh and is the recommended method for production use.

#### Getting OAuth Credentials

1. **Visit FreshBooks Developer Portal**
   - Go to https://www.freshbooks.com/api/authentication
   - Or visit: https://my.freshbooks.com/#/developer
   - Log in with your FreshBooks account

2. **Create OAuth Application**
   - Click "Create New App" or "Register Application"
   - Fill in application details:
     - **App Name**: e.g., "OI OS MCP Server"
     - **Redirect URI**: `https://localhost:8080/callback`
     - **Description**: (optional) Description of your application
   - Save the application

3. **Copy OAuth Credentials**
   - **Client ID**: Copy from the application details page
   - **Client Secret**: Copy from the application details page (keep this secure!)
   - **Redirect URI**: Must be exactly `https://localhost:8080/callback`

4. **Get Business/Account Information**
   - **Business ID**: Found in your FreshBooks account URL or settings
   - **Account ID**: Found in your FreshBooks account (e.g., "BV5Ord" format)

#### Setting OAuth Environment Variables

Add the following to your `.env` file in the **project root**:

```bash
# FreshBooks OAuth Configuration
FRESHBOOKS_CLIENT_ID=your_oauth_client_id_here
FRESHBOOKS_CLIENT_SECRET=your_oauth_client_secret_here
FRESHBOOKS_REDIRECT_URI=https://localhost:8080/callback

# FreshBooks Account Information (obtained after authentication)
FRESHBOOKS_BUSINESS_ID=your_business_id_here
FRESHBOOKS_ACCOUNT_ID=your_account_id_here
```

#### OAuth Authentication Flow

1. **Connect the OAuth server:**
   ```bash
   export $(grep -E "^FRESHBOOKS" .env | xargs)
   ./brain-trust4 connect freshbooks-mcp-server python3 ./MCP-servers/freshbooks-mcp-server/src/freshbooks_mcp/simple_oauth_server.py
   ```

2. **Authenticate (first time only):**
   ```bash
   ./brain-trust4 call freshbooks-mcp-server authenticate '{}'
   ```
   - This opens a browser for OAuth authorization
   - After authorization, you'll receive an authorization code
   - The server automatically exchanges the code for an access token
   - Token is saved to `~/.freshbooks_token`

3. **Manual Token Exchange (if automatic flow times out):**
   - After browser authorization, copy the authorization code from the callback URL
   - Exchange it using:
     ```bash
     export $(grep -E "^FRESHBOOKS" .env | xargs)
     python3 MCP-servers/freshbooks-mcp-server/exchange_code.py <authorization_code>
     ```
   - This saves the token to `~/.freshbooks_token`

**Note:** OAuth tokens expire after ~12 hours. The OAuth server automatically handles token refresh.

### Option 2: API Token Authentication

For simpler setup, you can use a direct API token (requires manual token refresh).

#### Getting API Token

1. **Log in to FreshBooks**
   - Go to https://www.freshbooks.com
   - Log in to your account

2. **Generate API Token**
   - Go to Settings → Integrations → API
   - Click "Generate API Token" or "Create Token"
   - Copy the token immediately (you won't be able to see it again)
   - **Important:** Save the token securely - it cannot be retrieved later

3. **Get Business ID**
   - The Business ID is typically found in your FreshBooks account settings
   - It may also be in the API documentation or URL
   - Format: Usually a numeric string (e.g., "14150281")

#### Setting API Token Environment Variables

Add the following to your `.env` file in the **project root**:

```bash
# FreshBooks API Token Configuration
FRESHBOOKS_API_TOKEN=your_api_token_here
FRESHBOOKS_BUSINESS_ID=your_business_id_here
```

**Important:** 
- The `.env` file should be in the OI OS project root directory (not in the freshbooks-mcp-server directory)
- `brain-trust4` automatically loads environment variables from `.env` when connecting servers
- Never commit your `.env` file to version control
- API tokens may expire and need to be regenerated manually

---

## Connecting to OI OS

### Step 1: Connect the Server

From your OI OS project root:

```bash
./brain-trust4 connect freshbooks-mcp-server python3 ./MCP-servers/freshbooks-mcp-server/mcp_server.py
```

**Note:** The server uses `mcp_server.py` which implements the MCP protocol manually and works with Python 3.9+. The `src/freshbooks_mcp/server.py` file requires the `mcp` package which needs Python 3.10+.

### Step 2: Verify Connection

```bash
./oi list
# Should show "freshbooks-mcp-server" in the server list

./oi status freshbooks-mcp-server
# Should show server status and capabilities

# Test with direct call (most reliable method)
./brain-trust4 call freshbooks-mcp-server get_identity '{}'
```

---

## Creating Intent Mappings

Intent mappings connect natural language queries to specific FreshBooks MCP tools. Create them using SQL INSERT statements.

### Database Location

```bash
sqlite3 brain-trust4.db
```

### All FreshBooks MCP Server Intent Mappings

Run this optimized single SQL statement to create all 35 intent mappings:

```sql
INSERT OR REPLACE INTO intent_mappings (keyword, server_name, tool_name, priority) VALUES 
('freshbooks authenticate', 'freshbooks-mcp-server', 'authenticate', 10),
('freshbooks auth', 'freshbooks-mcp-server', 'authenticate', 10),
('freshbooks login', 'freshbooks-mcp-server', 'authenticate', 10),
('freshbooks get identity', 'freshbooks-mcp-server', 'get_identity', 10),
('freshbooks identity', 'freshbooks-mcp-server', 'get_identity', 10),
('freshbooks whoami', 'freshbooks-mcp-server', 'get_identity', 10),
('freshbooks get clients', 'freshbooks-mcp-server', 'get_clients', 10),
('freshbooks clients', 'freshbooks-mcp-server', 'get_clients', 10),
('freshbooks list clients', 'freshbooks-mcp-server', 'get_clients', 10),
('freshbooks show clients', 'freshbooks-mcp-server', 'get_clients', 10),
('freshbooks get invoices', 'freshbooks-mcp-server', 'get_invoices', 10),
('freshbooks invoices', 'freshbooks-mcp-server', 'get_invoices', 10),
('freshbooks list invoices', 'freshbooks-mcp-server', 'get_invoices', 10),
('freshbooks show invoices', 'freshbooks-mcp-server', 'get_invoices', 10),
('freshbooks get projects', 'freshbooks-mcp-server', 'get_projects', 10),
('freshbooks projects', 'freshbooks-mcp-server', 'get_projects', 10),
('freshbooks list projects', 'freshbooks-mcp-server', 'get_projects', 10),
('freshbooks show projects', 'freshbooks-mcp-server', 'get_projects', 10),
('freshbooks get expenses', 'freshbooks-mcp-server', 'get_expenses', 10),
('freshbooks expenses', 'freshbooks-mcp-server', 'get_expenses', 10),
('freshbooks list expenses', 'freshbooks-mcp-server', 'get_expenses', 10),
('freshbooks show expenses', 'freshbooks-mcp-server', 'get_expenses', 10),
('freshbooks get time entries', 'freshbooks-mcp-server', 'get_time_entries', 10),
('freshbooks time entries', 'freshbooks-mcp-server', 'get_time_entries', 10),
('freshbooks list time entries', 'freshbooks-mcp-server', 'get_time_entries', 10),
('freshbooks show time entries', 'freshbooks-mcp-server', 'get_time_entries', 10),
('freshbooks create client', 'freshbooks-mcp-server', 'create_client', 10),
('freshbooks add client', 'freshbooks-mcp-server', 'create_client', 10),
('freshbooks new client', 'freshbooks-mcp-server', 'create_client', 10),
('freshbooks create invoice', 'freshbooks-mcp-server', 'create_invoice', 10),
('freshbooks add invoice', 'freshbooks-mcp-server', 'create_invoice', 10),
('freshbooks new invoice', 'freshbooks-mcp-server', 'create_invoice', 10),
('freshbooks create project', 'freshbooks-mcp-server', 'create_project', 10),
('freshbooks add project', 'freshbooks-mcp-server', 'create_project', 10),
('freshbooks new project', 'freshbooks-mcp-server', 'create_project', 10);
```

### Verifying Intent Mappings

```bash
# List all FreshBooks intent mappings
sqlite3 brain-trust4.db "SELECT * FROM intent_mappings WHERE server_name = 'freshbooks-mcp-server' ORDER BY priority DESC;"

# Or use OI command
./oi intent list | grep freshbooks
```

---

## Creating Parameter Rules

**⚠️ CRITICAL: Parameter rules must be created in the database for parameter extraction to work.**

Parameter rules define which fields are required and how to extract them from natural language queries. The OI OS parameter engine **only extracts required fields** - optional fields are skipped even if extractors exist.

### Why Parameter Rules Are Needed

- **Required fields are extracted**: The parameter engine processes required fields and invokes their extractors
- **Optional fields are skipped**: Optional fields are ignored during parameter extraction, even if extractors exist
- **Database-driven**: Parameter rules are stored in the `parameter_rules` table in `brain-trust4.db`

### Creating Parameter Rules

**Read Operations:** All read operations have no required parameters (they accept empty objects `{}`):

```sql
INSERT OR REPLACE INTO parameter_rules (server_name, tool_name, tool_signature, required_fields, field_generators, patterns) VALUES
('freshbooks-mcp-server', 'authenticate', 'freshbooks-mcp-server::authenticate', '[]', '{}', '[]'),
('freshbooks-mcp-server', 'get_identity', 'freshbooks-mcp-server::get_identity', '[]', '{}', '[]'),
('freshbooks-mcp-server', 'get_clients', 'freshbooks-mcp-server::get_clients', '[]', '{}', '[]'),
('freshbooks-mcp-server', 'get_invoices', 'freshbooks-mcp-server::get_invoices', '[]', '{}', '[]'),
('freshbooks-mcp-server', 'get_projects', 'freshbooks-mcp-server::get_projects', '[]', '{}', '[]'),
('freshbooks-mcp-server', 'get_expenses', 'freshbooks-mcp-server::get_expenses', '[]', '{}', '[]'),
('freshbooks-mcp-server', 'get_time_entries', 'freshbooks-mcp-server::get_time_entries', '[]', '{}', '[]');
```

**Create Operations:** Create operations have required fields that need to be extracted from natural language:

```sql
INSERT OR REPLACE INTO parameter_rules (server_name, tool_name, tool_signature, required_fields, field_generators, patterns) VALUES
('freshbooks-mcp-server', 'create_client', 'freshbooks-mcp-server::create_client', '["first_name", "last_name"]', '{"first_name": {"FromQuery": "freshbooks-mcp-server::create_client.first_name"}, "last_name": {"FromQuery": "freshbooks-mcp-server::create_client.last_name"}}', '[]'),
('freshbooks-mcp-server', 'create_invoice', 'freshbooks-mcp-server::create_invoice', '["client_id", "lines"]', '{"client_id": {"FromQuery": "freshbooks-mcp-server::create_invoice.client_id"}, "lines": {"FromQuery": "freshbooks-mcp-server::create_invoice.lines"}}', '[]'),
('freshbooks-mcp-server', 'create_project', 'freshbooks-mcp-server::create_project', '["name", "client_id"]', '{"name": {"FromQuery": "freshbooks-mcp-server::create_project.name"}, "client_id": {"FromQuery": "freshbooks-mcp-server::create_project.client_id"}}', '[]');
```

**Note:** Parameter extractors for these fields are defined in `parameter_extractors.toml.default`. The extractors automatically parse natural language queries to extract required fields like names, IDs, dates, etc.

### Verifying Parameter Rules

```bash
# List all FreshBooks parameter rules
sqlite3 brain-trust4.db "SELECT tool_signature, required_fields FROM parameter_rules WHERE server_name = 'freshbooks-mcp-server';"

# Check specific tool rule
sqlite3 brain-trust4.db "SELECT * FROM parameter_rules WHERE tool_signature = 'freshbooks-mcp-server::get_clients';"
```

---

## End User Setup

### First-Time Setup

1. **Choose Authentication Method**
   - **OAuth (Recommended)**: Automatic token refresh, more secure
   - **API Token**: Simpler setup, requires manual token refresh

2. **Get Credentials**
   
   **For OAuth:**
   - Visit https://www.freshbooks.com/api/authentication
   - Create OAuth application with redirect URI: `https://localhost:8080/callback`
   - Copy Client ID and Client Secret
   - See [Configuring Authentication](#configuring-authentication) section for detailed steps
   
   **For API Token:**
   - Log in to FreshBooks
   - Go to Settings → Integrations → API
   - Generate an API token
   - Note your Business ID
   - See [Configuring Authentication](#configuring-authentication) section for detailed steps

3. **Configure Environment Variables**
   - Add credentials to `.env` file in project root (see [Configuring Authentication](#configuring-authentication) section)

4. **Connect the Server**
   
   **For OAuth:**
   ```bash
   export $(grep -E "^FRESHBOOKS" .env | xargs)
   ./brain-trust4 connect freshbooks-mcp-server python3 ./MCP-servers/freshbooks-mcp-server/src/freshbooks_mcp/simple_oauth_server.py
   ```
   
   **For API Token:**
   ```bash
   ./brain-trust4 connect freshbooks-mcp-server python3 ./MCP-servers/freshbooks-mcp-server/mcp_server.py
   ```

5. **Authenticate (OAuth only)**
   ```bash
   # This opens browser for OAuth authorization
   ./brain-trust4 call freshbooks-mcp-server authenticate '{}'
   
   # If it times out, manually exchange the authorization code:
   # python3 MCP-servers/freshbooks-mcp-server/exchange_code.py <authorization_code>
   ```

6. **Test the Connection**
   ```bash
   ./oi "freshbooks get identity"
   ./oi "freshbooks get clients"
   ```

---

## Verification & Testing

### Test Direct Calls

```bash
# Test get_identity (no parameters needed)
./brain-trust4 call freshbooks-mcp-server get_identity '{}'

# Test get_clients
./brain-trust4 call freshbooks-mcp-server get_clients '{}'

# Test get_invoices
./brain-trust4 call freshbooks-mcp-server get_invoices '{}'

# Test get_projects
./brain-trust4 call freshbooks-mcp-server get_projects '{}'

# Test get_expenses
./brain-trust4 call freshbooks-mcp-server get_expenses '{}'

# Test get_time_entries
./brain-trust4 call freshbooks-mcp-server get_time_entries '{}'
```

### Test Natural Language Queries

```bash
# Test read operations
./oi "freshbooks get clients"
./oi "freshbooks list invoices"
./oi "freshbooks show projects"
./oi "freshbooks get identity"
./oi "freshbooks list expenses"
./oi "freshbooks show time entries"

# Test create operations (requires parameters)
./oi "freshbooks create client John Doe"
./oi "freshbooks create client Jane Smith email jane@example.com"
./oi "freshbooks create project Website Redesign for client 123"
./oi "freshbooks create invoice for client 123"
```

---

## Troubleshooting

### Server Connection Issues

**Error: "Server closed connection"**
- Check that Python 3.9+ is installed: `python3 --version`
- Verify `httpx` is installed: `pip3 list | grep httpx`
- Check server logs for errors

**Error: "MCP Error -1: Unknown error"**
- Ensure environment variables are set in `.env` file
- Verify the `.env` file is in the project root
- Check that `FRESHBOOKS_API_TOKEN` and `FRESHBOOKS_BUSINESS_ID` are set

### Authentication Issues

**Error: "FreshBooks API token must be set"**
- Add `FRESHBOOKS_API_TOKEN` to `.env` file in project root
- Restart the server connection after updating `.env`

**Error: "Could not determine account_id"**
- Call `get_identity` first to initialize the account_id
- The server automatically calls `get_identity` on first use if account_id is not set

### Python Version Issues

**Error: "ModuleNotFoundError: No module named 'mcp'"**
- This is expected - the server uses `mcp_server.py` which doesn't require the `mcp` package
- Ensure you're using `mcp_server.py`, not `src/freshbooks_mcp/server.py`

**Error: "Requires-Python >=3.10"**
- The `mcp` package requires Python 3.10+, but `mcp_server.py` works with Python 3.9+
- Use `mcp_server.py` instead of `src/freshbooks_mcp/server.py`

### Tool Call Issues

**Error: "Unknown method"**
- Verify intent mappings are created in the database
- Check that the tool name matches exactly (case-sensitive)

**Error: "No parameters extracted"**
- Verify parameter rules are created in the database
- Check that `required_fields` is set correctly (empty array `[]` for FreshBooks tools)

---

## Available Tools

The FreshBooks MCP server provides the following tools:

### Read Operations (No Parameters Required)

1. **`authenticate`** - Start OAuth authentication flow with FreshBooks (opens browser)
2. **`get_identity`** - Get FreshBooks identity information and business memberships
3. **`get_clients`** - Get all clients from FreshBooks
4. **`get_invoices`** - Get all invoices from FreshBooks
5. **`get_projects`** - Get all projects from FreshBooks
6. **`get_expenses`** - Get all expenses from FreshBooks
7. **`get_time_entries`** - Get all time tracking entries from FreshBooks

### Create Operations (Parameters Required)

8. **`create_client`** - Create a new client in FreshBooks
   - **Required:** `first_name`, `last_name`
   - **Optional:** `email`, `phone`, `address`, `city`, `state`, `country`, `postal_code`
   - **Example:** `./oi "freshbooks create client John Doe email john@example.com"`

9. **`create_invoice`** - Create a new invoice in FreshBooks
   - **Required:** `client_id`, `lines` (array of line items)
   - **Optional:** `date`, `due_date`, `notes`
   - **Example:** `./oi "freshbooks create invoice for client 123"`

10. **`create_project`** - Create a new project in FreshBooks
    - **Required:** `name`, `client_id`
    - **Optional:** `description`, `bill_method`, `rate`
    - **Example:** `./oi "freshbooks create project Website Redesign for client 123"`

**Note:** Read operations accept empty parameter objects `{}`. Create operations require specific parameters that are automatically extracted from natural language queries using the parameter extractors defined in `parameter_extractors.toml.default`.

---

## Additional Resources

- [FreshBooks API Documentation](https://www.freshbooks.com/api)
- [MCP Protocol Documentation](https://modelcontextprotocol.io)
- [OI OS Documentation](../README.md)

---

## License

MIT License - see LICENSE file in the repository for details.

