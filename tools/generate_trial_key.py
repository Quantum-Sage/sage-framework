#!/usr/bin/env python3
"""
ChainGuard Utility — Provision Trial API Keys
=============================================
Quickly generates 14-day Pro-tier sandbox keys for prospective enterprise clients.

Usage:
  python generate_trial_key.py "McKesson Canada"
"""

import os
import json
import uuid
import sys
from datetime import datetime, timedelta

def main(client_name):
    # Path to your API keys database
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    api_keys_file = os.path.join(base_dir, "api_keys.json")
    
    if not os.path.exists(api_keys_file):
        print(f"Error: Could not find {api_keys_file}")
        return

    # Load existing keys
    with open(api_keys_file, "r", encoding="utf-8") as f:
        api_keys = json.load(f)

    # Generate a unique professional key for the client
    # Format: cg_live_sandbox_<uuid_short>
    key_uuid = str(uuid.uuid4())[:8]
    client_slug = client_name.lower().replace(" ", "_")[:12]
    new_key = f"cg_sandbox_{client_slug}_{key_uuid}"

    # Provision as a 'pro' tier key but with a flag for later cleanup
    api_keys[new_key] = {
        "name": f"Trial: {client_name}",
        "tier": "pro",
        "stripe_customer_id": f"trial_{client_slug}",
        "calls_this_month": 0,
        "reset_month": datetime.utcnow().month,
        "expires_at": (datetime.utcnow() + timedelta(days=14)).isoformat(),
        "is_trial": True
    }

    # Save back to database
    with open(api_keys_file, "w", encoding="utf-8") as f:
        json.dump(api_keys, f, indent=2)

    print("-" * 60)
    print(f"SUCCESS: Sandbox key provisioned for {client_name}")
    print(f"API Key:  {new_key}")
    print(f"Expires:  {api_keys[new_key]['expires_at']}")
    print("-" * 60)
    print("Next step: Send this key to the client for their 14-day trial.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python generate_trial_key.py \"Client Name\"")
    else:
        main(sys.argv[1])
