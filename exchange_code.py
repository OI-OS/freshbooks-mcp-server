#!/usr/bin/env python3
"""Exchange OAuth authorization code for access token."""

import asyncio
import json
import os
import sys
import httpx

async def exchange_code_for_token(auth_code: str):
    """Exchange authorization code for access token."""
    client_id = os.getenv("FRESHBOOKS_CLIENT_ID")
    client_secret = os.getenv("FRESHBOOKS_CLIENT_SECRET")
    redirect_uri = os.getenv("FRESHBOOKS_REDIRECT_URI", "https://localhost:8080/callback")
    
    if not client_id or not client_secret:
        print("Error: FRESHBOOKS_CLIENT_ID and FRESHBOOKS_CLIENT_SECRET must be set", file=sys.stderr)
        sys.exit(1)
    
    token_url = "https://api.freshbooks.com/auth/oauth/token"
    
    data = {
        'grant_type': 'authorization_code',
        'client_id': client_id,
        'client_secret': client_secret,
        'redirect_uri': redirect_uri,
        'code': auth_code
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                token_url,
                data=data,
                headers={'Content-Type': 'application/x-www-form-urlencoded'}
            )
            response.raise_for_status()
            token_data = response.json()
            
            # Save token to file
            token_file = os.path.expanduser("~/.freshbooks_token")
            token_info = {
                "access_token": token_data.get("access_token"),
                "refresh_token": token_data.get("refresh_token"),
                "account_id": token_data.get("account_id"),
                "business_id": os.getenv("FRESHBOOKS_BUSINESS_ID"),
                "timestamp": __import__('time').time()
            }
            
            with open(token_file, 'w') as f:
                json.dump(token_info, f, indent=2)
            
            print(f"✅ Token exchange successful!")
            print(f"Access token saved to: {token_file}")
            print(f"Account ID: {token_info.get('account_id')}")
            print(f"Business ID: {token_info.get('business_id')}")
            
            return token_data
        except httpx.HTTPStatusError as e:
            print(f"Error: HTTP {e.response.status_code}", file=sys.stderr)
            print(f"Response: {e.response.text}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 exchange_code.py <authorization_code>", file=sys.stderr)
        sys.exit(1)
    
    auth_code = sys.argv[1]
    asyncio.run(exchange_code_for_token(auth_code))

