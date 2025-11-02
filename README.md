# FreshBooks MCP Server

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

## Installation

```bash
pip install freshbooks-mcp-server
```

Or install from source:

```bash
git clone https://github.com/OI-OS/freshbooks-mcp-server.git
cd freshbooks-mcp-server
pip install -e .
```

## Configuration

1. Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

2. Fill in your FreshBooks credentials in `.env`:
   - `FRESHBOOKS_API_TOKEN` - Your FreshBooks API token (for simple authentication)
   - `FRESHBOOKS_BUSINESS_ID` - Your FreshBooks business ID (for simple authentication)
   - `FRESHBOOKS_CLIENT_ID` - Your OAuth client ID (for OAuth authentication)
   - `FRESHBOOKS_CLIENT_SECRET` - Your OAuth client secret (for OAuth authentication)

**Note:** Never commit your `.env` file or token files to version control. They are already excluded in `.gitignore`.

## Quick Start

```python
from freshbooks_mcp import FreshbooksMCPServer

# Initialize the server
server = FreshbooksMCPServer()

# Start the server
server.start()
```

## License

MIT License - see LICENSE file for details
