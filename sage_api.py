#!/usr/bin/env python3
"""
SAGE API Server — Commercial Monetization Layer
=================================================
Flask REST API wrapping all SAGE tools behind authenticated endpoints.

Revenue Model:
  - Per-query pricing for consulting-grade analysis
  - API key authentication
  - Rate limiting (100 req/hr per key)
  - JSON response format for integration

Endpoints:
  POST /api/cold-chain       — Vaccine cold chain analysis ($5-50)
  POST /api/drug-delivery    — Drug delivery LP optimization ($25-100)
  POST /api/network-plan     — Quantum network feasibility ($10-75)
  POST /api/tournament       — Evolutionary tournament run ($15)
  GET  /api/health           — Health check (free)

Usage:
  python sage_api.py
  # Then: curl -H "X-API-Key: sage-demo-key-001" \\
  #            -X POST http://127.0.0.1:8000/api/cold-chain \\
  #            -H "Content-Type: application/json" \\
  #            -d '{"budget": 2000}'
"""

import json
import time
import sys
import os
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

# ============================================================================
# APP CONFIGURATION
# ============================================================================

app = Flask(__name__)

# API Keys — in production, use a database or environment variables
API_KEYS = {
    "sage-demo-key-001": {"name": "Demo User", "tier": "free", "rate_limit": 100},
    "sage-pro-key-001": {"name": "Pro User", "tier": "pro", "rate_limit": 1000},
}

# Add any keys from environment
env_key = os.environ.get("SAGE_API_KEY")
if env_key:
    API_KEYS[env_key] = {"name": "Env User", "tier": "pro", "rate_limit": 500}

# Rate limiting state
request_counts = defaultdict(list)  # key -> [timestamps]

SAGE_VERSION = "6.0"

# ============================================================================
# AUTH & RATE LIMITING
# ============================================================================


def require_api_key(f):
    """Decorator: require valid API key in X-API-Key header."""

    @wraps(f)
    def decorated(*args, **kwargs):
        api_key = request.headers.get("X-API-Key")
        if not api_key or api_key not in API_KEYS:
            return jsonify(
                {
                    "error": "Invalid or missing API key",
                    "hint": "Include 'X-API-Key: your-key' in request headers",
                }
            ), 401

        # Rate limiting
        key_info = API_KEYS[api_key]
        now = time.time()
        hour_ago = now - 3600

        # Clean old entries
        request_counts[api_key] = [t for t in request_counts[api_key] if t > hour_ago]

        if len(request_counts[api_key]) >= key_info["rate_limit"]:
            return jsonify(
                {
                    "error": "Rate limit exceeded",
                    "limit": key_info["rate_limit"],
                    "window": "1 hour",
                    "retry_after_seconds": int(
                        3600 - (now - request_counts[api_key][0])
                    ),
                }
            ), 429

        request_counts[api_key].append(now)
        return f(*args, **kwargs)

    return decorated


# ============================================================================
# ENDPOINTS
# ============================================================================


@app.route("/api/health", methods=["GET"])
def health():
    """Free health check endpoint."""
    return jsonify(
        {
            "status": "healthy",
            "version": SAGE_VERSION,
            "framework": "SAGE — Synthetic Adaptive Generation Engine",
            "endpoints": [
                "POST /api/cold-chain",
                "POST /api/drug-delivery",
                "POST /api/network-plan",
                "POST /api/tournament",
                "GET  /api/health",
            ],
        }
    )


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
        return jsonify(
            {
                "status": "success",
                "result": result,
                "query": {"budget": budget, "n_stages": len(stages)},
                "pricing": {"tier": "per-query", "base_cost_usd": 5 + len(stages) * 5},
            }
        )
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/drug-delivery", methods=["POST"])
@require_api_key
def api_drug_delivery():
    """
    Drug delivery LP optimization.

    Body (JSON):
      target: str (default "brain")
      barriers: list[dict] (optional) — custom barrier definitions

    Returns: R&D Capital Allocation Matrix + LP-optimal vehicle selection
    """
    data = request.get_json(silent=True) or {}
    barriers = data.get("barriers", DEFAULT_BARRIERS)

    try:
        result = drug_delivery_analysis(barriers)
        return jsonify(
            {
                "status": "success",
                "result": result,
                "query": {"n_barriers": len(barriers)},
                "pricing": {
                    "tier": "per-query",
                    "base_cost_usd": 25 + len(barriers) * 10,
                },
            }
        )
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
        label = "Beijing → London (default)"

    sat_tier = data.get("satellite_tier", "LEO_2027")

    try:
        result = analyze_route(distance, label, sat_tier)
        return jsonify(
            {
                "status": "success",
                "result": result,
                "query": {
                    "distance_km": distance,
                    "route": label,
                    "satellite_tier": sat_tier,
                },
                "pricing": {
                    "tier": "per-query",
                    "base_cost_usd": 10 + int(distance / 200),
                },
            }
        )
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
    generations = min(data.get("generations", 30), 100)  # Cap at 100
    pop_size = min(data.get("pop_size", 60), 200)  # Cap at 200

    try:
        hardware = MockHardwareInterface()
        result = run_tournament(hardware, generations, pop_size)

        # Strip verbose history for API response
        api_result = {k: v for k, v in result.items() if k != "history"}

        return jsonify(
            {
                "status": "success",
                "result": api_result,
                "query": {"generations": generations, "pop_size": pop_size},
                "pricing": {"tier": "per-run", "base_cost_usd": 15},
            }
        )
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/presets", methods=["GET"])
def api_presets():
    """List available preset routes and satellite tiers."""
    return jsonify(
        {
            "routes": {k: v for k, v in PRESET_ROUTES.items()},
            "satellite_tiers": {k: v["label"] for k, v in SATELLITE_TIERS.items()},
        }
    )


# ============================================================================
# ENTRYPOINT
# ============================================================================

if __name__ == "__main__":
    port = int(os.environ.get("SAGE_PORT", 8000))
    print()
    print("=" * 60)
    print("  💰 SAGE API Server v6.0 — Commercial Endpoint")
    print("=" * 60)
    print(f"  URL: http://127.0.0.1:{port}")
    print(f"  Demo Key: sage-demo-key-001")
    print()
    print("  Endpoints:")
    print("    POST /api/cold-chain      — Vaccine logistics")
    print("    POST /api/drug-delivery   — Pharma R&D optimization")
    print("    POST /api/network-plan    — Quantum network feasibility")
    print("    POST /api/tournament      — Evolutionary simulation")
    print("    GET  /api/health          — Health check")
    print("    GET  /api/presets         — Available configurations")
    print()
    print("  Example:")
    print(f'    curl -H "X-API-Key: sage-demo-key-001" \\')
    print(f"         -X POST http://127.0.0.1:{port}/api/cold-chain \\")
    print(f'         -H "Content-Type: application/json" \\')
    print(f"         -d '{{\"budget\": 2000}}'")
    print()

    app.run(host="0.0.0.0", port=port, debug=False, threaded=True)
