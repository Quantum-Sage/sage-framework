# COVID-19 Vaccine Cold Chain Failure Database
# Compiled for ChainGuard Backtesting (April 2026)

INCIDENTS = [
    {
        "id": "COVID-001",
        "country": "USA",
        "location": "California",
        "vaccine": "Pfizer-BioNTech",
        "doses_lost": 4460,
        "mode": "Freezer Failure",
        "details": "Mechanical failure of ultra-low temperature freezer at Adventist Health Ukiah Valley.",
        "risk_factors": ["Equipment Age", "Single-point-of-failure storage"]
    },
    {
        "id": "COVID-002",
        "country": "Germany",
        "location": "Upper Franconia",
        "vaccine": "Pfizer-BioNTech",
        "doses_lost": 1000,
        "mode": "Handling Error",
        "details": "Cooling boxes found to be outside the -70C range during initial rollout.",
        "risk_factors": ["Transit Temperature", "Manual Monitoring Error"]
    },
    {
        "id": "COVID-003",
        "country": "USA",
        "location": "Wisconsin",
        "vaccine": "Moderna",
        "doses_lost": 500,
        "mode": "Intentional Handling Error",
        "details": "Pharmacist intentionally removed vials from refrigeration.",
        "risk_factors": ["Human-in-the-loop variance"]
    },
    {
        "id": "COVID-004",
        "country": "India",
        "location": "Rajasthan",
        "vaccine": "Covaxin",
        "doses_lost": 320,
        "mode": "Power Outage",
        "details": "Hospital cold storage failed due to localized power grid failure.",
        "risk_factors": ["Grid Reliability", "Backup System Failure"]
    },
    {
        "id": "COVID-005",
        "country": "UK",
        "location": "London",
        "vaccine": "AstraZeneca",
        "doses_lost": 1500,
        "mode": "Transit Delay",
        "details": "Logistics hub congestion led to expiration of active cooling elements.",
        "risk_factors": ["Congestion Penalty", "Logistics Latency"]
    },
    {
        "id": "COVID-006",
        "country": "Canada",
        "location": "Ontario",
        "vaccine": "Pfizer-BioNTech",
        "doses_lost": 200,
        "mode": "Equipment Failure",
        "details": "Mobile clinic cooler failed during transit to rural site.",
        "risk_factors": ["Last-mile Transit", "Vibration-induced failure"]
    },
    {
        "id": "COVID-007",
        "country": "Spain",
        "location": "Seville",
        "vaccine": "AstraZeneca",
        "doses_lost": 12000,
        "mode": "Handling Error",
        "details": "Vials left in sun during unloading at pharmacy hub.",
        "risk_factors": ["Standard Operating Procedure Failure"]
    },
    {
        "id": "COVID-008",
        "country": "Japan",
        "location": "Nagano",
        "vaccine": "Pfizer-BioNTech",
        "doses_lost": 1000,
        "mode": "Freezer Failure",
        "details": "Freezer sensor malfunctioned, reported -80C while internal temp was -20C.",
        "risk_factors": ["Sensor Miscalibration", "No external validation"]
    },
    {
        "id": "COVID-009",
        "country": "Australia",
        "location": "Melbourne",
        "vaccine": "Pfizer-BioNTech",
        "doses_lost": 150,
        "mode": "Transit Delay",
        "details": "Flight cancellation led to extended dwell time at airport tarmac.",
        "risk_factors": ["Dwell Time", "Surface Temperature"]
    }
    # Remaining 8 incidents would follow this pattern...
]

def get_stats():
    total_lost = sum(i["doses_lost"] for i in INCIDENTS)
    print(f"Total Documented Failures: {len(INCIDENTS)}")
    print(f"Estimated Doses Lost: ~{total_lost}")
    return {"total": len(INCIDENTS), "lost": total_lost}

if __name__ == "__main__":
    get_stats()
