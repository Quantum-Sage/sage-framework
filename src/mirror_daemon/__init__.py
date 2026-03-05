"""
SAGE Mirror Daemon — Sub-package
=================================
Refactored from mirror_daemon_v2.py (1,897-line monolith).

Modules:
    quantum_primitives  — Pauli matrices, ket/density_matrix, fidelity, noise channels
    backends            — QuantumBackend ABC + SimulatedBackend, HostileBackend, stubs
    feedback            — InjectionGuard, AdaptiveThreshold
    logging_data        — DataPoint, ExperimentLogger, DaemonConfig
    analysis            — StatisticalAnalyzer, BlochTrajectoryPlotter
"""

from .quantum_primitives import (
    ComplexMatrix,
    PAULI_I,
    PAULI_X,
    PAULI_Y,
    PAULI_Z,
    ket,
    density_matrix,
    fidelity,
    von_neumann_entropy,
    logical_error_rate,
    bloch_coordinates,
    apply_depolarizing_noise,
    apply_dephasing,
    apply_amplitude_damping,
)
from .backends import (
    SurfaceCodeSyndrome,
    SurfaceCodeQEC,
    ChannelResult,
    QuantumBackend,
    SimulatedBackend,
    HostileBackend,
    QuEraBackend,
    HeliosBackend,
)
from .feedback import InjectionGuard, AdaptiveThreshold
from .logging_data import DataPoint, ExperimentLogger, DaemonConfig
from .analysis import StatisticalAnalyzer, BlochTrajectoryPlotter

__all__ = [
    # Primitives
    "ComplexMatrix",
    "PAULI_I",
    "PAULI_X",
    "PAULI_Y",
    "PAULI_Z",
    "ket",
    "density_matrix",
    "fidelity",
    "von_neumann_entropy",
    "logical_error_rate",
    "bloch_coordinates",
    "apply_depolarizing_noise",
    "apply_dephasing",
    "apply_amplitude_damping",
    # Backends
    "SurfaceCodeSyndrome",
    "SurfaceCodeQEC",
    "ChannelResult",
    "QuantumBackend",
    "SimulatedBackend",
    "HostileBackend",
    "QuEraBackend",
    "HeliosBackend",
    # Feedback
    "InjectionGuard",
    "AdaptiveThreshold",
    # Logging
    "DataPoint",
    "ExperimentLogger",
    "DaemonConfig",
    # Analysis
    "StatisticalAnalyzer",
    "BlochTrajectoryPlotter",
]
