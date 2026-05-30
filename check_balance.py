#!/usr/bin/env python3
"""Query DeepSeek API account balance."""

import os
import sys
import requests

DEEPSEEK_BASE = "https://api.deepseek.com"


def get_balance(api_key: str) -> dict:
    resp = requests.get(
        f"{DEEPSEEK_BASE}/user/balance",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Accept": "application/json",
        },
        timeout=15,
    )
    resp.raise_for_status()
    return resp.json()


def main():
    if len(sys.argv) > 1:
        api_key = sys.argv[1]
    else:
        api_key = os.environ.get("DEEPSEEK_API_KEY")
        if not api_key:
            print("Usage: python check_balance.py <API_KEY>")
            print("   or: set DEEPSEEK_API_KEY environment variable")
            sys.exit(1)

    try:
        data = get_balance(api_key)
        print(data)
    except requests.HTTPError as e:
        print(f"HTTP error: {e.response.status_code} {e.response.text}")
        sys.exit(1)
    except requests.RequestException as e:
        print(f"Request failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
