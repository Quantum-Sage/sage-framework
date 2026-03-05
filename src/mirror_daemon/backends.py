"""
Quantum Backends & QEC
=======================
Surface code syndrome/QEC classes, the QuantumBackend ABC, and all
concrete backend implementations (SimulatedBackend, HostileBackend,
QuEraBackend stub, HeliosBackend stub).

Extracted from mirror_daemon_v2.py (Sections 2-3).
"""

from __future__ import annotations

import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional

import numpy as np
from numpy.typing import NDArray

from .quantum_primitives import (
    ComplexMatrix,
    PAULI_X,
    PAULI_Y,
    PAULI_Z,
    density_matrix,
    fidelity,
    apply_depolarizing_noise,
    apply_dephasing,
    apply_amplitude_damping,
)

log = logging.getLogger("mirror_daemon_v2")


# ═══════════════════════════════════════════════════════════════════════════════
#  SURFACE CODE QEC
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class SurfaceCodeSyndrome:
    """Result of a syndrome measurement round."""

    z_stabilizers: NDArray[np.int8]
    x_stabilizers: NDArray[np.int8]
    timestamp_ns: int = 0
    round_id: int = 0

    @property
    def has_errors(self) -> bool:
        return bool(
            np.any(self.z_stabilizers == -1) or np.any(self.x_stabilizers == -1)
        )

    @property
    def error_weight(self) -> int:
        return int(np.sum(self.z_stabilizers == -1) + np.sum(self.x_stabilizers == -1))


class SurfaceCodeQEC:
    """
    Simplified distance-d surface code. For simulation we operate on a
    logical qubit (2×2 ρ). Syndrome extraction is probabilistic,
    consistent with a distance-d code's error detection capability.

    For real hardware: replace extract_syndrome() with ancilla readout.
    For rigorous decoding: use PyMatching for actual MWPM.
    """

    def __init__(self, code_distance: int = 3):
        self.d = code_distance
        self.n_z = (code_distance - 1) * code_distance // 2
        self.n_x = self.n_z
        log.debug(f"SurfaceCodeQEC: d={code_distance}, n_z={self.n_z}")

    def extract_syndrome(
        self,
        rho: ComplexMatrix,
        noise_level: float,
        round_id: int = 0,
    ) -> SurfaceCodeSyndrome:
        """Simulate syndrome extraction from density matrix."""
        off_diag = float(np.abs(rho[0, 1]))
        flip_prob = noise_level * (1.0 - off_diag)
        z_synds = np.where(np.random.random(self.n_z) < flip_prob, -1, 1).astype(
            np.int8
        )
        x_synds = np.where(np.random.random(self.n_x) < flip_prob, -1, 1).astype(
            np.int8
        )
        return SurfaceCodeSyndrome(
            z_stabilizers=z_synds,
            x_stabilizers=x_synds,
            timestamp_ns=time.time_ns(),
            round_id=round_id,
        )

    def decode_correction(
        self, syndrome: SurfaceCodeSyndrome
    ) -> Optional[ComplexMatrix]:
        """MWPM decoder (simplified). Returns correction operator or None."""
        if not syndrome.has_errors:
            return None
        w = syndrome.error_weight
        if w == 1:
            return PAULI_X.copy()
        elif w == 2:
            return PAULI_Z.copy()
        else:
            return PAULI_Y.copy()

    def apply_correction(
        self,
        rho: ComplexMatrix,
        correction: ComplexMatrix,
    ) -> ComplexMatrix:
        """Apply correction: ρ → C ρ C†"""
        return correction @ rho @ correction.conj().T


# ═══════════════════════════════════════════════════════════════════════════════
#  HARDWARE ABSTRACTION LAYER
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class ChannelResult:
    """What comes back from one channel step."""

    state: ComplexMatrix
    fidelity: float
    noise_level: float
    elapsed_ns: int
    step_id: int
    metadata: dict = field(default_factory=dict)


class QuantumBackend(ABC):
    """Hardware abstraction. All backends expose same interface to MirrorDaemon."""

    @abstractmethod
    def initialize(self, reference_state: ComplexMatrix) -> None: ...

    @abstractmethod
    def step(self, injected_state: Optional[ComplexMatrix] = None) -> ChannelResult: ...

    @abstractmethod
    def get_current_state(self) -> ComplexMatrix: ...

    @property
    @abstractmethod
    def name(self) -> str: ...


class SimulatedBackend(QuantumBackend):
    """
    Simulated depolarizing + dephasing + amplitude damping channel.
    Models Willow-class performance at configurable noise rates.
    """

    def __init__(
        self,
        depolar_p: float = 0.001,
        dephasing_gamma: float = 0.0007,
        amplitude_gamma: float = 0.0003,
        step_duration_ns: int = 100,
        seed: Optional[int] = None,
    ):
        self.depolar_p = depolar_p
        self.dephasing_gamma = dephasing_gamma
        self.amplitude_gamma = amplitude_gamma
        self.step_duration_ns = step_duration_ns
        self._rng = np.random.default_rng(seed)
        self._state: Optional[ComplexMatrix] = None
        self._reference: Optional[ComplexMatrix] = None
        self._step_count = 0

    @property
    def name(self) -> str:
        return (
            f"SimulatedBackend(p={self.depolar_p}, "
            f"γ_φ={self.dephasing_gamma}, γ_1={self.amplitude_gamma})"
        )

    def initialize(self, reference_state: ComplexMatrix) -> None:
        self._reference = density_matrix(reference_state.copy())
        self._state = self._reference.copy()
        self._step_count = 0
        log.info("SimulatedBackend initialized.")

    def step(self, injected_state: Optional[ComplexMatrix] = None) -> ChannelResult:
        if self._state is None:
            raise RuntimeError("Backend not initialized.")
        t0 = time.time_ns()

        if injected_state is not None:
            self._state = density_matrix(injected_state)

        rho = self._state.copy()
        rho = apply_depolarizing_noise(rho, self.depolar_p)
        rho = apply_dephasing(rho, self.dephasing_gamma)
        rho = apply_amplitude_damping(rho, self.amplitude_gamma)

        # Stochastic perturbation (shot noise)
        eps = self.depolar_p * 0.1
        d = rho.shape[0]
        kick = self._rng.normal(0, eps, (d, d)) + 1j * self._rng.normal(0, eps, (d, d))
        kick = (kick + kick.conj().T) / 2
        rho = rho + kick * eps
        rho = rho / np.trace(rho)

        f_val = fidelity(rho, self._reference)
        elapsed = time.time_ns() - t0

        self._state = rho
        self._step_count += 1

        return ChannelResult(
            state=rho,
            fidelity=f_val,
            noise_level=self.depolar_p,
            elapsed_ns=elapsed + self.step_duration_ns,
            step_id=self._step_count,
            metadata={"backend": "simulated"},
        )

    def get_current_state(self) -> ComplexMatrix:
        if self._state is None:
            raise RuntimeError("Backend not initialized.")
        return self._state.copy()


class HostileBackend(QuantumBackend):
    """
    Adversarial noise model with fatigue-driven escalation.

    The noise level escalates over time: p(t) = p_base + fatigue * t
    This models an adversary or environment that becomes progressively
    more hostile — the worst-case scenario for any QEC scheme.
    """

    def __init__(
        self,
        base_noise: float = 0.005,
        fatigue: float = 0.08,
        dephasing_ratio: float = 0.7,
        amplitude_ratio: float = 0.3,
        step_duration_ns: int = 100,
        seed: Optional[int] = None,
    ):
        self.base_noise = base_noise
        self.fatigue = fatigue
        self.dephasing_ratio = dephasing_ratio
        self.amplitude_ratio = amplitude_ratio
        self.step_duration_ns = step_duration_ns
        self._rng = np.random.default_rng(seed)
        self._state: Optional[ComplexMatrix] = None
        self._reference: Optional[ComplexMatrix] = None
        self._step_count = 0
        self._current_noise = base_noise

    @property
    def name(self) -> str:
        return f"HostileBackend(fatigue={self.fatigue})"

    def initialize(self, reference_state: ComplexMatrix) -> None:
        self._reference = density_matrix(reference_state.copy())
        self._state = self._reference.copy()
        self._step_count = 0
        self._current_noise = self.base_noise
        log.info(f"HostileBackend initialized. fatigue={self.fatigue}")

    def step(self, injected_state: Optional[ComplexMatrix] = None) -> ChannelResult:
        if self._state is None:
            raise RuntimeError("Backend not initialized.")
        t0 = time.time_ns()

        if injected_state is not None:
            self._state = density_matrix(injected_state)

        # Escalating noise
        self._current_noise = self.base_noise + self.fatigue * self._step_count / 100.0

        rho = self._state.copy()
        p_depol = min(self._current_noise, 0.999)
        rho = apply_depolarizing_noise(rho, p_depol)
        rho = apply_dephasing(rho, self._current_noise * self.dephasing_ratio)
        rho = apply_amplitude_damping(
            rho, min(self._current_noise * self.amplitude_ratio, 0.999)
        )

        # Stochastic perturbation
        eps = max(self._current_noise * 0.05, 1e-6)
        d = rho.shape[0]
        kick = self._rng.normal(0, eps, (d, d)) + 1j * self._rng.normal(0, eps, (d, d))
        kick = (kick + kick.conj().T) / 2
        rho = rho + kick * eps
        rho = rho / np.trace(rho)

        # Ensure valid density matrix (eigenvalue clipping)
        eigvals, eigvecs = np.linalg.eigh(rho)
        eigvals = np.maximum(eigvals, 0.0)
        eigvals = eigvals / eigvals.sum()
        rho = eigvecs @ np.diag(eigvals) @ eigvecs.conj().T

        f_val = fidelity(rho, self._reference)
        elapsed = time.time_ns() - t0

        self._state = rho
        self._step_count += 1

        return ChannelResult(
            state=rho,
            fidelity=f_val,
            noise_level=self._current_noise,
            elapsed_ns=elapsed + self.step_duration_ns,
            step_id=self._step_count,
            metadata={"fatigue": self.fatigue},
        )

    def get_current_state(self) -> ComplexMatrix:
        if self._state is None:
            raise RuntimeError("Backend not initialized.")
        return self._state.copy()


class QuEraBackend(QuantumBackend):
    """QuEra neutral-atom backend stub. Requires: pip install bloqade"""

    def __init__(self, api_token: str = "", device: str = "aquila"):
        self.device = device
        log.warning("QuEraBackend is a stub. Implement via bloqade SDK.")

    @property
    def name(self) -> str:
        return f"QuEraBackend(device={self.device})"

    def initialize(self, reference_state: ComplexMatrix) -> None:
        raise NotImplementedError("QuEra backend: implement via bloqade.")

    def step(self, injected_state: Optional[ComplexMatrix] = None) -> ChannelResult:
        raise NotImplementedError

    def get_current_state(self) -> ComplexMatrix:
        raise NotImplementedError


class HeliosBackend(QuantumBackend):
    """Google Helios fluxonium backend stub. Requires: pip install cirq-google"""

    def __init__(self, project_id: str = "", processor_id: str = "helios"):
        self.processor_id = processor_id
        log.warning("HeliosBackend is a stub. Implement via cirq-google.")

    @property
    def name(self) -> str:
        return f"HeliosBackend(processor={self.processor_id})"

    def initialize(self, reference_state: ComplexMatrix) -> None:
        raise NotImplementedError("Helios backend: implement via cirq-google.")

    def step(self, injected_state: Optional[ComplexMatrix] = None) -> ChannelResult:
        raise NotImplementedError

    def get_current_state(self) -> ComplexMatrix:
        raise NotImplementedError
