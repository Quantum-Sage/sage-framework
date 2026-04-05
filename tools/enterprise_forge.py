#!/usr/bin/env python3
"""
SAGE Enterprise Utility — Manual Key Forge
==========================================
Generates unlimited Enterprise keys for high-value B2B Proof of Value (PoV).
Bypasses Stripe for strategic accounts like McKesson.

Usage:
  python enterprise_forge.py "Jean-Philippe (McKesson)"
"""

import os
import sys
import secrets

# Add parent directory to path so we can import database.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import database

def forge_enterprise_key(client_name):
    """Create a manual Enterprise key in the production database."""
    
    # Generate the high-entropy key
    # Format: cg_live_<secure_token>
    api_key = f"cg_live_{secrets.token_urlsafe(32)}"
    
    print("-" * 60)
    print(f"FORGING ENTERPRISE KEY FOR: {client_name}")
    print("-" * 60)
    
    try:
        database.create_or_update_customer(
            key=api_key,
            name=client_name,
            tier="enterprise",
            stripe_customer_id="manual_pov_bypass",
            is_trial=False,
            expires_at=None  # Enterprise keys are unlimited/permanent in V1
        )
        
        print("\nSUCCESS! Key provisioned in database.")
        print(f"API Key:  \033[95m{api_key}\033[0m")
        print("Tier:     ENTERPRISE (Unlimited Calls)")
        print("\nNext step: Send this securely to the client's CTO.")
        print("-" * 60)
        
    except Exception as e:
        print(f"ERROR: Could not forge key. {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python enterprise_forge.py \"Client Name\"")
    else:
        forge_enterprise_key(sys.argv[1])
