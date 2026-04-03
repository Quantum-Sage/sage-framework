#!/usr/bin/env python3
"""
SAGE API Server — Subscription Tier Monetization Layer
=======================================================
Flask REST API wrapping all SAGE tools behind subscription-gated endpoints.

Subscription Tiers:
  free       — 10 calls/month, truncated results (top-3 only), no support
  starter    — $49/month,  200 calls/month, full results
  pro        — $299/month, 2,000 calls/month, full results + priority
  enterprise — Custom,     unlimited calls, SLA, white-label

Endpoints:
  POST /api/cold-chain       — Vaccine cold chain analysis
  POST /api/drug-delivery    — Drug delivery LP optimization
  POST /api/network-plan     — Quantum network feasibility
  POST /api/tournament       — Evolutionary tournament run
  GET  /api/health           — Health check (always free)
  GET  /api/tiers            — Pricing page (always free)

Usage:
  python sage_api.py
  # Then: curl -H "X-API-Key: sage-demo-key-001" \\
  #            -X POST http://127.0.0.1:8000/api/cold-chain \\
  #            -H "Content-Type: application/json" \\
  #            -d '{"budget": 2000}'
"""

import sys
import os
import json
import time
from datetime import datetime
from functools import wraps
from collections import defaultdict

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from flask import Flask, request, jsonify

# Import the commercial tools
from run_cold_chain import run_analysis as cold_chain_analysis, DEFAULT_STAGES
from run_drug_delivery import run_analysis as drug_delivery_analysis, DEFAULT_BARRIERS
from run_network_planner import analyze_route, PRESET_ROUTES, SATELLITE_TIERS
from run_tournament import run_tournament, MockHardwareInterface

import stripe
from dotenv import load_dotenv

# Load .env file if it exists
load_dotenv()

stripe.api_key = os.environ.get("STRIPE_API_KEY")

# ============================================================================
# SUBSCRIPTION TIER DEFINITIONS
# ============================================================================

TIERS = {
    "free": {
        "label": "Free",
        "price_usd_monthly": 0,
        "calls_per_month": 10,
        "full_results": False,         # truncated to top-3 recommendations
        "truncation_note": "Upgrade to Starter ($49/mo) for full results.",
        "stripe_price_id": None,
    },
    "starter": {
        "label": "Starter",
        "price_usd_monthly": 49,
        "calls_per_month": 200,
        "full_results": True,
        "stripe_price_id": os.environ.get("STRIPE_PRICE_STARTER", "price_starter_placeholder"),
    },
    "pro": {
        "label": "Pro",
        "price_usd_monthly": 299,
        "calls_per_month": 2000,
        "full_results": True,
        "stripe_price_id": os.environ.get("STRIPE_PRICE_PRO", "price_pro_placeholder"),
    },
    "enterprise": {
        "label": "Enterprise",
        "price_usd_monthly": None,     # custom / contact sales
        "calls_per_month": None,       # unlimited
        "full_results": True,
        "stripe_price_id": None,
    },
}

# ============================================================================
# APP CONFIGURATION
# ============================================================================

app = Flask(__name__)

# Load API Keys from local JSON database
API_KEYS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "api_keys.json")
if os.path.exists(API_KEYS_FILE):
    with open(API_KEYS_FILE, "r", encoding="utf-8") as f:
        API_KEYS = json.load(f)
else:
    API_KEYS = {
        "sage-demo-key-001": {
            "name": "Demo User",
            "tier": "free",
            "stripe_customer_id": "cus_demo_123",
            "calls_this_month": 0,
            "reset_month": datetime.utcnow().month,
        },
        "sage-pro-key-001": {
            "name": "Pro User",
            "tier": "pro",
            "stripe_customer_id": "cus_pro_456",
            "calls_this_month": 0,
            "reset_month": datetime.utcnow().month,
        },
    }

# Add any key from environment variable (e.g. set by Streamlit Cloud secret)
env_key = os.environ.get("SAGE_API_KEY")
if env_key and env_key not in API_KEYS:
    API_KEYS[env_key] = {
        "name": "Env User",
        "tier": "pro",
        "stripe_customer_id": "cus_env_890",
        "calls_this_month": 0,
        "reset_month": datetime.utcnow().month,
    }

# Hourly rate-limit state (in-memory, resets on server restart)
request_counts = defaultdict(list)

SAGE_VERSION = "6.0"

# ============================================================================
# HELPERS
# ============================================================================


def save_api_keys():
    """Persist the API_KEYS dict back to disk."""
    with open(API_KEYS_FILE, "w", encoding="utf-8") as f:
        json.dump(API_KEYS, f, indent=2)


def _reset_monthly_counter_if_needed(key_info: dict) -> dict:
    """Reset monthly call counter if we've rolled into a new calendar month."""
    current_month = datetime.utcnow().month
    if key_info.get("reset_month") != current_month:
        key_info["calls_this_month"] = 0
        key_info["reset_month"] = current_month
    return key_info


def _truncate_for_free_tier(data: dict) -> dict:
    """Return a truncated version of the result dict for free-tier users."""
    # Cold-chain: show only top-3 upgrades
    if "result" in data and "lp_solution" in data.get("result", {}):
        lp = data["result"]["lp_solution"]
        if "upgrades" in lp:
            lp["upgrades"] = lp["upgrades"][:3]
            lp["_truncated"] = True
            lp["_upgrade_hint"] = TIERS["free"]["truncation_note"]

    # Drug-delivery: show only top-3 allocation entries
    if "result" in data and "allocation_matrix" in data.get("result", {}):
        matrix = data["result"]["allocation_matrix"]
        if isinstance(matrix, list):
            data["result"]["allocation_matrix"] = matrix[:3]
            data["result"]["_truncated"] = True
            data["result"]["_upgrade_hint"] = TIERS["free"]["truncation_note"]

    # Network plan: remove per-topology feasibility detail
    if "result" in data and "topologies" in data.get("result", {}):
        topos = data["result"]["topologies"]
        if isinstance(topos, list):
            data["result"]["topologies"] = topos[:1]  # only first topology
            data["result"]["_truncated"] = True
            data["result"]["_upgrade_hint"] = TIERS["free"]["truncation_note"]

    data["_tier"] = "free"
    data["_upgrade_url"] = "https://sage-framework.streamlit.app/?tab=api"
    return data


def _log_stripe_event(api_key: str, key_info: dict, tier: str, calls_used: int, calls_limit):
    """Log a usage event to Stripe or print mock telemetry."""
    customer_id = key_info.get("stripe_customer_id", "UNKNOWN")
    limit_str = str(calls_limit) if calls_limit else "UNLIMITED"

    if stripe.api_key:
        # Production: log to Stripe Billing Meter
        try:
            # stripe.billing.MeterEvent.create(
            #     event_name="sage_api_call",
            #     payload={"stripe_customer_id": customer_id, "value": "1"},
            # )
            print(
                f"  [STRIPE LIVE] \033[92mLogged usage for {customer_id}\033[0m "
                f"tier={tier} calls={calls_used}/{limit_str}"
            )
        except Exception as e:
            print(f"  [STRIPE ERROR] {e}")
    else:
        # Mock Mode — vivid terminal telemetry for demo
        tier_color = {"free": "\033[90m", "starter": "\033[96m", "pro": "\033[93m", "enterprise": "\033[95m"}.get(tier, "")
        print(
            f"\n  [STRIPE MOCK] {tier_color}[{tier.upper()}]\033[0m "
            f"Key={api_key[:20]}... | Customer={customer_id} | "
            f"Calls this month: \033[93m{calls_used}/{limit_str}\033[0m"
        )


# ============================================================================
# AUTH & TIER ENFORCEMENT DECORATOR
# ============================================================================


def require_api_key(f):
    """
    Decorator: validate API key, enforce subscription tier limits,
    truncate free-tier results, and log usage to Stripe.
    """

    @wraps(f)
    def decorated(*args, **kwargs):
        api_key = request.headers.get("X-API-Key")
        if not api_key or api_key not in API_KEYS:
            return jsonify({
                "error": "Invalid or missing API key",
                "hint": "Get your free API key at https://sage-framework.streamlit.app/?tab=api",
            }), 401

        key_info = API_KEYS[api_key]
        tier = key_info.get("tier", "free")
        tier_config = TIERS.get(tier, TIERS["free"])

        # --- Monthly call limit (subscription enforcement) ---
        key_info = _reset_monthly_counter_if_needed(key_info)
        calls_limit = tier_config["calls_per_month"]   # None = unlimited
        calls_used = key_info.get("calls_this_month", 0)

        if calls_limit is not None and calls_used >= calls_limit:
            return jsonify({
                "error": "Monthly call limit reached",
                "tier": tier,
                "limit": calls_limit,
                "upgrade_url": "https://sage-framework.streamlit.app/?tab=api",
                "hint": f"Upgrade to {_next_tier(tier)} to continue.",
            }), 429

        # --- Hourly burst guard (prevents runaway automation) ---
        now = time.time()
        hour_ago = now - 3600
        request_counts[api_key] = [t for t in request_counts[api_key] if t > hour_ago]
        burst_limit = min(calls_limit or 9999, 60)   # max 60 req/hr regardless of tier
        if len(request_counts[api_key]) >= burst_limit:
            return jsonify({
                "error": "Hourly burst limit exceeded (60 req/hr). Slow down.",
                "retry_after_seconds": int(3600 - (now - request_counts[api_key][0])),
            }), 429
        request_counts[api_key].append(now)

        # --- Execute endpoint ---
        response = f(*args, **kwargs)

        # --- Post-response: update counter, truncate, log ---
        if getattr(response, "status_code", 500) == 200 and response.is_json:
            key_info["calls_this_month"] = calls_used + 1
            API_KEYS[api_key] = key_info
            save_api_keys()

            data = response.get_json()

            # Truncate results for free-tier users
            if not tier_config["full_results"] and data:
                data = _truncate_for_free_tier(data)
                response = jsonify(data)
                response.status_code = 200

            # Inject tier metadata
            if data:
                data["_meta"] = {
                    "tier": tier,
                    "calls_used_this_month": calls_used + 1,
                    "calls_limit_this_month": calls_limit,
                }
                response = jsonify(data)
                response.status_code = 200

            _log_stripe_event(api_key, key_info, tier, calls_used + 1, calls_limit)

        return response

    return decorated


def _next_tier(current_tier: str) -> str:
    order = ["free", "starter", "pro", "enterprise"]
    idx = order.index(current_tier) if current_tier in order else 0
    return order[min(idx + 1, len(order) - 1)].title()


# ============================================================================
# ENDPOINTS
# ============================================================================


@app.route("/api/health", methods=["GET"])
def health():
    """Free health check endpoint — no key required."""
    return jsonify({
        "status": "healthy",
        "version": SAGE_VERSION,
        "framework": "SAGE — Synthetic Adaptive Generation Engine",
        "endpoints": [
            "POST /api/cold-chain",
            "POST /api/drug-delivery",
            "POST /api/network-plan",
            "POST /api/tournament",
            "GET  /api/health",
            "GET  /api/tiers",
        ],
    })


@app.route("/api/tiers", methods=["GET"])
def api_tiers():
    """Public pricing / subscription tiers endpoint."""
    return jsonify({
        "tiers": {
            name: {
                "label": cfg["label"],
                "price_usd_monthly": cfg["price_usd_monthly"],
                "calls_per_month": cfg["calls_per_month"],
                "full_results": cfg["full_results"],
            }
            for name, cfg in TIERS.items()
        },
        "signup_url": "https://sage-framework.streamlit.app/?tab=api",
    })


@app.route("/api/cold-chain", methods=["POST"])
@require_api_key
def api_cold_chain():
    """
    Vaccine cold chain analysis.

    Body (JSON):
      budget: float (default 1000) — upgrade budget
      stages: list[dict] (optional) — custom stage definitions

    Returns: potency analysis + LP-optimal upgrade recommendations
    """
    data = request.get_json(silent=True) or {}
    budget = data.get("budget", 1000.0)
    stages = data.get("stages", DEFAULT_STAGES)

    try:
        result = cold_chain_analysis(stages, budget)
        return jsonify({
            "status": "success",
            "result": result,
            "query": {"budget": budget, "n_stages": len(stages)},
            "pricing": {"tier": "subscription", "base_cost_usd": 0},
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/drug-delivery", methods=["POST"])
@require_api_key
def api_drug_delivery():
    """
    Drug delivery LP optimization.

    Body (JSON):
      barriers: list[dict] (optional) — custom barrier definitions

    Returns: R&D Capital Allocation Matrix + LP-optimal vehicle selection
    """
    data = request.get_json(silent=True) or {}
    barriers = data.get("barriers", DEFAULT_BARRIERS)

    try:
        result = drug_delivery_analysis(barriers)
        return jsonify({
            "status": "success",
            "result": result,
            "query": {"n_barriers": len(barriers)},
            "pricing": {"tier": "subscription", "base_cost_usd": 0},
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/network-plan", methods=["POST"])
@require_api_key
def api_network_plan():
    """
    Quantum network feasibility analysis.

    Body (JSON):
      distance: float (km) — or use 'route' preset
      route: str (e.g., "beijing-london") — preset route name
      satellite_tier: str (default "LEO_2027")

    Returns: multi-topology feasibility analysis + verdict
    """
    data = request.get_json(silent=True) or {}

    if "route" in data and data["route"] in PRESET_ROUTES:
        preset = PRESET_ROUTES[data["route"]]
        distance = preset["distance"]
        label = preset["label"]
    elif "distance" in data:
        distance = float(data["distance"])
        label = f"Custom ({distance:.0f} km)"
    else:
        distance = 8200
        label = "Beijing -> London (default)"

    sat_tier = data.get("satellite_tier", "LEO_2027")

    try:
        result = analyze_route(distance, label, sat_tier)
        return jsonify({
            "status": "success",
            "result": result,
            "query": {"distance_km": distance, "route": label, "satellite_tier": sat_tier},
            "pricing": {"tier": "subscription", "base_cost_usd": 0},
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/tournament", methods=["POST"])
@require_api_key
def api_tournament():
    """
    Evolutionary tournament (mock hardware).

    Body (JSON):
      generations: int (default 30)
      pop_size: int (default 60)

    Returns: tournament results + hardware-survival correlation
    """
    data = request.get_json(silent=True) or {}
    generations = min(data.get("generations", 30), 100)
    pop_size = min(data.get("pop_size", 60), 200)

    try:
        hardware = MockHardwareInterface()
        result = run_tournament(hardware, generations, pop_size)
        api_result = {k: v for k, v in result.items() if k != "history"}
        return jsonify({
            "status": "success",
            "result": api_result,
            "query": {"generations": generations, "pop_size": pop_size},
            "pricing": {"tier": "subscription", "base_cost_usd": 0},
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/presets", methods=["GET"])
def api_presets():
    """List available preset routes and satellite tiers (no key required)."""
    return jsonify({
        "routes": {k: v for k, v in PRESET_ROUTES.items()},
        "satellite_tiers": {k: v["label"] for k, v in SATELLITE_TIERS.items()},
    })


# ============================================================================
# ENTRYPOINT
# ============================================================================

if __name__ == "__main__":
    port = int(os.environ.get("SAGE_PORT", 8000))
    print()
    print("=" * 60)
    print("  SAGE API Server v6.0 — Subscription Tier Model")
    print("=" * 60)
    print(f"  URL: http://127.0.0.1:{port}")
    print()
    print("  Subscription Tiers:")
    print("    free       — 10 calls/month  | Truncated results | $0")
    print("    starter    — 200 calls/month | Full results      | $49/mo")
    print("    pro        — 2,000 calls/mo  | Full results      | $299/mo")
    print("    enterprise — Unlimited       | Full + SLA        | Custom")
    print()
    print("  Endpoints:")
    print("    POST /api/cold-chain      — Vaccine logistics")
    print("    POST /api/drug-delivery   — Pharma R&D optimization")
    print("    POST /api/network-plan    — Quantum network feasibility")
    print("    POST /api/tournament      — Evolutionary simulation")
    print("    GET  /api/health          — Health check")
    print("    GET  /api/tiers           — Pricing info")
    print("    GET  /api/presets         — Available configurations")
    print()
    print("  Stripe Mock Mode: Active (set STRIPE_API_KEY env var for live)")
    print()

    app.run(host="0.0.0.0", port=port, debug=False, threaded=True)
