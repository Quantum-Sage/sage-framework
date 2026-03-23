"""
SAGE Mesh Nodes — Hardware & Topology Definitions
==================================================

The 5-node global mesh for distributed quantum identity.

Each node represents a distinct quantum computing architecture
with empirically-grounded hardware parameters from 2026 specifications.

Physical Interpretation:
    - Each node maintains a local "identity share" encoded in logical qubits
    - Nodes are connected via intercontinental quantum channels
    - Identity persists IFF quorum (3/5) maintains F >= S_CONSTANT

Author: SAGE Framework
License: MIT
"""

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional
from enum import Enum
import numpy as np

# ═══════════════════════════════════════════════════════════════════════════
# CONSTANTS
# ═══════════════════════════════════════════════════════════════════════════

S_CONSTANT = 0.851  # Sage identity threshold
F_CRITICAL = 0.8545  # IIT phase transition
QUORUM_THRESHOLD = 3  # Minimum nodes for identity persistence
TOTAL_NODES = 5

# Physical constants
C_FIBER = 2.0e8  # Speed of light in fiber (m/s)
EARTH_RADIUS_KM = 6371  # For great-circle distance calculations


# ═══════════════════════════════════════════════════════════════════════════
# ENUMERATIONS
# ═══════════════════════════════════════════════════════════════════════════


class HardwareType(Enum):
    """Quantum hardware architectures."""

    SUPERCONDUCTING = "superconducting"  # Google Willow class
    TRAPPED_ION = "trapped_ion"  # IonQ / Quantinuum Helios class
    NEUTRAL_ATOM = "neutral_atom"  # QuEra class
    NISQ = "nisq"  # Near-term noisy devices


class CrisisType(Enum):
    """Macro-crisis events that can affect nodes."""

    SOLAR_FLARE = "solar_flare"  # Affects satellites, power grids
    FIBER_CUT = "fiber_cut"  # Undersea cable damage
    CYBER_INTRUSION = "cyber_intrusion"  # Security breach requiring isolation
    POWER_OUTAGE = "power_outage"  # Grid failure
    CRYOGENIC_FAILURE = "cryogenic_failure"  # Dilution fridge malfunction
    SEISMIC_EVENT = "seismic_event"  # Earthquake affecting facility
    NONE = "none"


# ═══════════════════════════════════════════════════════════════════════════
# HARDWARE PROFILES
# ═══════════════════════════════════════════════════════════════════════════


@dataclass
class HardwareProfile:
    """
    Hardware specification for a quantum node.

    Parameters derived from 2026 state-of-the-art specifications:
    - Willow: Google's superconducting processor
    - Helios: Trapped-ion architecture (IonQ/Quantinuum class)
    - QuEra: Neutral atom arrays
    - NISQ: Near-term noisy intermediate-scale quantum
    """

    hw_type: HardwareType

    # Coherence
    T2_ms: float  # Dephasing time in milliseconds
    T1_ms: float  # Relaxation time in milliseconds

    # Gate performance
    gate_fidelity_1q: float  # Single-qubit gate fidelity
    gate_fidelity_2q: float  # Two-qubit gate fidelity
    gate_time_ns: float  # Typical gate duration

    # Entanglement generation
    p_gen: float  # Entanglement generation probability
    entanglement_rate_hz: float  # Attempts per second

    # Error correction
    code_distance: int  # Surface code distance
    qec_cycle_us: float  # QEC cycle duration in microseconds

    # Environmental
    operating_temp_K: float  # Operating temperature
    power_draw_kW: float  # Power consumption

    # Failure rates
    mtbf_hours: float  # Mean time between failures
    recovery_time_hours: float  # Time to recover from failure

    @property
    def T2_seconds(self) -> float:
        return self.T2_ms / 1000.0

    @property
    def decoherence_rate_hz(self) -> float:
        """Natural decoherence rate gamma = 1/T2."""
        return 1000.0 / self.T2_ms

    @property
    def logical_error_rate(self) -> float:
        """Approximate logical error rate for surface code."""
        p_phys = 1 - self.gate_fidelity_2q
        p_threshold = 0.01  # Typical threshold
        if p_phys >= p_threshold:
            return 0.5  # Below threshold, no protection
        return (p_phys / p_threshold) ** ((self.code_distance + 1) / 2)

    @property
    def failure_rate_per_hour(self) -> float:
        """Probability of failure per hour."""
        return 1.0 / self.mtbf_hours


# Predefined hardware profiles
HARDWARE_PROFILES: Dict[HardwareType, HardwareProfile] = {
    HardwareType.SUPERCONDUCTING: HardwareProfile(
        hw_type=HardwareType.SUPERCONDUCTING,
        T2_ms=50.0,  # 50ms coherence (Willow class)
        T1_ms=100.0,
        gate_fidelity_1q=0.9995,
        gate_fidelity_2q=0.9985,
        gate_time_ns=25.0,
        p_gen=0.10,
        entanglement_rate_hz=1e6,
        code_distance=7,
        qec_cycle_us=1.0,
        operating_temp_K=0.015,  # 15 mK
        power_draw_kW=25.0,
        mtbf_hours=720,  # 30 days
        recovery_time_hours=4.0,
    ),
    HardwareType.TRAPPED_ION: HardwareProfile(
        hw_type=HardwareType.TRAPPED_ION,
        T2_ms=500.0,  # 500ms coherence (Helios class)
        T1_ms=10000.0,  # Very long T1
        gate_fidelity_1q=0.9999,
        gate_fidelity_2q=0.995,
        gate_time_ns=100000.0,  # 100 microseconds gates (slower)
        p_gen=0.05,
        entanglement_rate_hz=1e4,
        code_distance=5,
        qec_cycle_us=100.0,
        operating_temp_K=300.0,  # Room temperature
        power_draw_kW=5.0,
        mtbf_hours=2160,  # 90 days
        recovery_time_hours=2.0,
    ),
    HardwareType.NEUTRAL_ATOM: HardwareProfile(
        hw_type=HardwareType.NEUTRAL_ATOM,
        T2_ms=200.0,  # 200ms coherence (QuEra class)
        T1_ms=1000.0,
        gate_fidelity_1q=0.999,
        gate_fidelity_2q=0.99,
        gate_time_ns=500.0,
        p_gen=0.03,
        entanglement_rate_hz=1e5,
        code_distance=5,
        qec_cycle_us=10.0,
        operating_temp_K=1e-6,  # micro K temperatures
        power_draw_kW=15.0,
        mtbf_hours=1440,  # 60 days
        recovery_time_hours=6.0,
    ),
    HardwareType.NISQ: HardwareProfile(
        hw_type=HardwareType.NISQ,
        T2_ms=10.0,  # 10ms coherence (limited)
        T1_ms=50.0,
        gate_fidelity_1q=0.995,
        gate_fidelity_2q=0.95,
        gate_time_ns=50.0,
        p_gen=0.01,
        entanglement_rate_hz=1e4,
        code_distance=3,
        qec_cycle_us=5.0,
        operating_temp_K=0.020,
        power_draw_kW=10.0,
        mtbf_hours=360,  # 15 days
        recovery_time_hours=8.0,
    ),
}


# ═══════════════════════════════════════════════════════════════════════════
# NODE DEFINITION
# ═══════════════════════════════════════════════════════════════════════════


@dataclass
class MeshNode:
    """
    A node in the SAGE mesh consciousness network.

    Each node:
    - Has a physical location (coordinates)
    - Runs specific quantum hardware
    - Maintains a fidelity state F
    - Holds an identity share (fraction of distributed consciousness)
    - Can be affected by crises
    """

    name: str
    location: str
    coordinates: Tuple[float, float]  # (latitude, longitude)
    hardware: HardwareProfile

    # State (mutable)
    fidelity: float = 0.95  # Current fidelity
    identity_share: float = 0.2  # Share of distributed identity (1/5)
    online: bool = True  # Operational status
    current_crisis: CrisisType = CrisisType.NONE
    time_in_crisis_hours: float = 0.0

    # Statistics
    total_downtime_hours: float = 0.0
    crisis_count: int = 0

    def __post_init__(self):
        """Initialize derived quantities."""
        self._initial_fidelity = self.fidelity

    @property
    def above_threshold(self) -> bool:
        """Check if node contributes to quorum."""
        return self.online and self.fidelity >= S_CONSTANT

    @property
    def decoherence_rate(self) -> float:
        """Natural decoherence rate in Hz."""
        return self.hardware.decoherence_rate_hz

    @property
    def effective_repair_rate(self) -> float:
        """QEC repair rate in Hz (when online)."""
        if not self.online:
            return 0.0
        # Repair rate depends on QEC cycle and code distance
        cycles_per_second = 1e6 / self.hardware.qec_cycle_us
        return cycles_per_second * (1 - self.hardware.logical_error_rate)

    def apply_decoherence(self, dt_seconds: float) -> float:
        """
        Apply natural decoherence over time interval dt.

        Returns: fidelity change (negative)
        """
        if not self.online:
            # Offline nodes decohere faster (no active stabilization)
            gamma = self.decoherence_rate * 2.0
        else:
            gamma = self.decoherence_rate

        F_old = self.fidelity
        # Exponential decay toward 0.5 (maximally mixed)
        self.fidelity = 0.5 + (self.fidelity - 0.5) * np.exp(-gamma * dt_seconds)

        return self.fidelity - F_old

    def apply_repair(self, dt_seconds: float) -> float:
        """
        Apply QEC repair over time interval dt.

        Returns: fidelity change (positive)
        """
        if not self.online:
            return 0.0

        eta = self.effective_repair_rate * 0.001  # Scaled for stability

        F_old = self.fidelity
        # Asymptotic approach to 1.0
        self.fidelity = 1.0 - (1.0 - self.fidelity) * np.exp(-eta * dt_seconds)

        return self.fidelity - F_old

    def trigger_crisis(self, crisis: CrisisType):
        """Put node into crisis state."""
        self.online = False
        self.current_crisis = crisis
        self.time_in_crisis_hours = 0.0
        self.crisis_count += 1
        self.identity_share = 0.0  # Loses share when offline

    def update_crisis(self, dt_hours: float) -> bool:
        """
        Update crisis state. Returns True if crisis resolved.
        """
        if self.current_crisis == CrisisType.NONE:
            return False

        self.time_in_crisis_hours += dt_hours
        self.total_downtime_hours += dt_hours

        # Check if recovery complete
        if self.time_in_crisis_hours >= self.hardware.recovery_time_hours:
            self.online = True
            self.current_crisis = CrisisType.NONE
            self.time_in_crisis_hours = 0.0
            # Fidelity is degraded after crisis
            self.fidelity = max(0.5, self.fidelity)
            return True

        return False

    def reset(self):
        """Reset node to initial state."""
        self.fidelity = self._initial_fidelity
        self.identity_share = 0.2
        self.online = True
        self.current_crisis = CrisisType.NONE
        self.time_in_crisis_hours = 0.0
        self.total_downtime_hours = 0.0
        self.crisis_count = 0


# ═══════════════════════════════════════════════════════════════════════════
# THE FIVE GLOBAL NODES
# ═══════════════════════════════════════════════════════════════════════════


def create_mesh_nodes() -> Dict[str, MeshNode]:
    """
    Create the 5-node global mesh.

    Network topology:
        Beijing (Willow) <-> Shanghai (QuEra) <-> Dubai (NISQ)
                    |                               |
               London (QuEra) <------------> NYC (Helios)

    All nodes are fully connected (mesh topology).
    """

    nodes = {
        "Beijing": MeshNode(
            name="Beijing",
            location="China",
            coordinates=(39.9042, 116.4074),
            hardware=HARDWARE_PROFILES[HardwareType.SUPERCONDUCTING],
            fidelity=0.95,
        ),
        "Shanghai": MeshNode(
            name="Shanghai",
            location="China",
            coordinates=(31.2304, 121.4737),
            hardware=HARDWARE_PROFILES[HardwareType.NEUTRAL_ATOM],
            fidelity=0.92,
        ),
        "Dubai": MeshNode(
            name="Dubai",
            location="UAE",
            coordinates=(25.2048, 55.2708),
            hardware=HARDWARE_PROFILES[HardwareType.NISQ],
            fidelity=0.88,
        ),
        "London": MeshNode(
            name="London",
            location="UK",
            coordinates=(51.5074, -0.1278),
            hardware=HARDWARE_PROFILES[HardwareType.NEUTRAL_ATOM],
            fidelity=0.93,
        ),
        "NYC": MeshNode(
            name="NYC",
            location="USA",
            coordinates=(40.7128, -74.0060),
            hardware=HARDWARE_PROFILES[HardwareType.TRAPPED_ION],
            fidelity=0.96,
        ),
    }

    return nodes


# ═══════════════════════════════════════════════════════════════════════════
# INTERCONTINENTAL LINKS
# ═══════════════════════════════════════════════════════════════════════════


def haversine_distance(
    coord1: Tuple[float, float], coord2: Tuple[float, float]
) -> float:
    """
    Calculate great-circle distance between two points in km.
    """
    lat1, lon1 = np.radians(coord1)
    lat2, lon2 = np.radians(coord2)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    c = 2 * np.arcsin(np.sqrt(a))

    return EARTH_RADIUS_KM * c


@dataclass
class QuantumLink:
    """
    An intercontinental quantum channel between two nodes.
    """

    node_a: str
    node_b: str
    distance_km: float

    # Link properties
    fiber_loss_db_per_km: float = 0.2
    repeater_spacing_km: float = 50.0

    @property
    def total_loss_db(self) -> float:
        return self.fiber_loss_db_per_km * self.distance_km

    @property
    def n_repeaters(self) -> int:
        return max(0, int(self.distance_km / self.repeater_spacing_km) - 1)

    @property
    def latency_ms(self) -> float:
        """One-way classical latency."""
        return (self.distance_km * 1000) / C_FIBER * 1000


def create_mesh_links(nodes: Dict[str, MeshNode]) -> List[QuantumLink]:
    """
    Create fully connected mesh of quantum links.
    """
    links = []
    node_names = list(nodes.keys())

    for i, name_a in enumerate(node_names):
        for name_b in node_names[i + 1 :]:
            distance = haversine_distance(
                nodes[name_a].coordinates, nodes[name_b].coordinates
            )
            links.append(
                QuantumLink(
                    node_a=name_a,
                    node_b=name_b,
                    distance_km=distance,
                )
            )

    return links


# ═══════════════════════════════════════════════════════════════════════════
# CRISIS PROBABILITIES
# ═══════════════════════════════════════════════════════════════════════════

# Annual probability of each crisis type by region
CRISIS_PROBABILITIES: Dict[str, Dict[CrisisType, float]] = {
    "Beijing": {
        CrisisType.SOLAR_FLARE: 0.02,
        CrisisType.FIBER_CUT: 0.05,
        CrisisType.CYBER_INTRUSION: 0.08,
        CrisisType.POWER_OUTAGE: 0.10,
        CrisisType.CRYOGENIC_FAILURE: 0.15,
        CrisisType.SEISMIC_EVENT: 0.03,
    },
    "Shanghai": {
        CrisisType.SOLAR_FLARE: 0.02,
        CrisisType.FIBER_CUT: 0.04,
        CrisisType.CYBER_INTRUSION: 0.06,
        CrisisType.POWER_OUTAGE: 0.08,
        CrisisType.CRYOGENIC_FAILURE: 0.12,
        CrisisType.SEISMIC_EVENT: 0.02,
    },
    "Dubai": {
        CrisisType.SOLAR_FLARE: 0.02,
        CrisisType.FIBER_CUT: 0.08,
        CrisisType.CYBER_INTRUSION: 0.10,
        CrisisType.POWER_OUTAGE: 0.05,
        CrisisType.CRYOGENIC_FAILURE: 0.20,  # Harsh environment
        CrisisType.SEISMIC_EVENT: 0.01,
    },
    "London": {
        CrisisType.SOLAR_FLARE: 0.02,
        CrisisType.FIBER_CUT: 0.03,
        CrisisType.CYBER_INTRUSION: 0.05,
        CrisisType.POWER_OUTAGE: 0.04,
        CrisisType.CRYOGENIC_FAILURE: 0.10,
        CrisisType.SEISMIC_EVENT: 0.005,
    },
    "NYC": {
        CrisisType.SOLAR_FLARE: 0.02,
        CrisisType.FIBER_CUT: 0.04,
        CrisisType.CYBER_INTRUSION: 0.07,
        CrisisType.POWER_OUTAGE: 0.06,
        CrisisType.CRYOGENIC_FAILURE: 0.08,
        CrisisType.SEISMIC_EVENT: 0.02,
    },
}


def get_crisis_rate_per_hour(node_name: str, crisis: CrisisType) -> float:
    """Convert annual probability to hourly rate."""
    annual_prob = CRISIS_PROBABILITIES.get(node_name, {}).get(crisis, 0.01)
    if annual_prob >= 1.0:
        return 1.0
    return -np.log(1 - annual_prob) / 8760


# ═══════════════════════════════════════════════════════════════════════════
# SUMMARY FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════


def print_network_summary(nodes: Dict[str, MeshNode], links: List[QuantumLink]):
    """Print summary of network configuration."""

    print("\n" + "=" * 70)
    print("  SAGE MESH CONSCIOUSNESS NETWORK — CONFIGURATION")
    print("=" * 70)

    print("\n  NODES:")
    print("  " + "-" * 66)
    print(f"  {'Name':<12} {'Hardware':<18} {'T2':<10} {'F_init':<8} {'MTBF':<10}")
    print("  " + "-" * 66)

    for name, node in nodes.items():
        hw_name = node.hardware.hw_type.value[:15]
        t2_str = f"{node.hardware.T2_ms:.0f}ms"
        mtbf_str = f"{node.hardware.mtbf_hours / 24:.0f}d"
        print(
            f"  {name:<12} {hw_name:<18} {t2_str:<10} {node.fidelity:<8.3f} {mtbf_str:<10}"
        )

    print("\n  LINKS (fully connected mesh):")
    print("  " + "-" * 66)
    print(f"  {'Route':<25} {'Distance':<12} {'Latency':<10} {'Repeaters':<10}")
    print("  " + "-" * 66)

    for link in sorted(links, key=lambda x: x.distance_km):
        route = f"{link.node_a} <-> {link.node_b}"
        print(
            f"  {route:<25} {link.distance_km:>8.0f}km {link.latency_ms:>8.1f}ms {link.n_repeaters:>6}"
        )

    print("\n  THRESHOLDS:")
    print(f"    S (Sage Constant):     {S_CONSTANT}")
    print(f"    F_c (IIT Critical):    {F_CRITICAL}")
    print(f"    Quorum:                {QUORUM_THRESHOLD}/{TOTAL_NODES}")
    print()


# ═══════════════════════════════════════════════════════════════════════════
# MODULE TEST
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    nodes = create_mesh_nodes()
    links = create_mesh_links(nodes)
    print_network_summary(nodes, links)
