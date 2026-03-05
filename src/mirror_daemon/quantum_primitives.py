"""
Quantum State Primitives
=========================
Pauli matrices, ket construction, density matrices, fidelity measures,
noise channels (depolarizing, dephasing, amplitude damping), and
Bloch sphere utilities.

Extracted from mirror_daemon_v2.py (Section 1).
"""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

# ── Type alias ────────────────────────────────────────────────────────────────
ComplexMatrix = NDArray[np.complex128]

# ── Pauli matrices (module-level constants) ───────────────────────────────────
PAULI_I = np.eye(2, dtype=np.complex128)
PAULI_X = np.array([[0, 1], [1, 0]], dtype=np.complex128)
PAULI_Y = np.array([[0, -1j], [1j, 0]], dtype=np.complex128)
PAULI_Z = np.array([[1, 0], [0, -1]], dtype=np.complex128)


def ket(amplitudes: list[complex]) -> ComplexMatrix:
    """Construct a normalized ket from amplitudes."""
    v = np.array(amplitudes, dtype=np.complex128)
    n = np.linalg.norm(v)
    if n < 1e-12:
        raise ValueError("Zero-norm ket")
    return (v / n).reshape(-1, 1)


def density_matrix(ket_or_dm: ComplexMatrix) -> ComplexMatrix:
    """Ensure we have a density matrix. Accepts ket or existing ρ."""
    if ket_or_dm.ndim == 1 or ket_or_dm.shape[1] == 1:
        psi = ket_or_dm.reshape(-1, 1)
        return psi @ psi.conj().T
    return ket_or_dm


def fidelity(rho: ComplexMatrix, sigma: ComplexMatrix) -> float:
    """
    Uhlmann fidelity F(ρ, σ) = (Tr √(√ρ σ √ρ))²
    For pure states σ = |ψ⟩⟨ψ|, simplifies to F = ⟨ψ|ρ|ψ⟩.
    """
    eigvals = np.linalg.eigvalsh(sigma)
    if np.sum(eigvals > 1e-10) == 1:
        idx = np.argmax(eigvals)
        vecs = np.linalg.eigh(sigma)[1]
        psi = vecs[:, idx].reshape(-1, 1)
        f_val = float(np.real(psi.conj().T @ rho @ psi).item())
        return max(0.0, min(1.0, f_val))
    sqrt_rho = _matrix_sqrt(rho)
    m = sqrt_rho @ sigma @ sqrt_rho
    f_val = float(np.real(np.trace(_matrix_sqrt(m))) ** 2)
    return max(0.0, min(1.0, f_val))


def von_neumann_entropy(rho: ComplexMatrix, eps: float = 1e-14) -> float:
    """S(ρ) = -Tr(ρ log ρ). Returns entropy in nats."""
    eigvals = np.linalg.eigvalsh(rho)
    eigvals = eigvals[eigvals > eps]
    return float(-np.sum(eigvals * np.log(eigvals)))


def logical_error_rate(fidelity_trace: list[float]) -> float:
    """λ = -d(ln F)/dt averaged over sliding window."""
    if len(fidelity_trace) < 2:
        return 0.0
    f = np.array(fidelity_trace[-20:], dtype=np.float64)
    f = np.clip(f, 1e-12, 1.0)
    dlnf = np.diff(np.log(f))
    return float(-np.mean(dlnf))


def bloch_coordinates(rho: ComplexMatrix) -> tuple[float, float, float]:
    """
    Extract Bloch sphere coordinates (x, y, z) from a single-qubit
    density matrix: ρ = (I + x·σ_x + y·σ_y + z·σ_z) / 2
    """
    x = float(np.real(np.trace(PAULI_X @ rho)))
    y = float(np.real(np.trace(PAULI_Y @ rho)))
    z = float(np.real(np.trace(PAULI_Z @ rho)))
    return (x, y, z)


def _matrix_sqrt(m: ComplexMatrix) -> ComplexMatrix:
    """Positive semidefinite matrix square root via eigendecomposition."""
    eigvals, eigvecs = np.linalg.eigh(m)
    eigvals = np.maximum(eigvals, 0.0)
    return eigvecs @ np.diag(np.sqrt(eigvals)) @ eigvecs.conj().T


def apply_depolarizing_noise(rho: ComplexMatrix, p: float) -> ComplexMatrix:
    """Depolarizing channel: ε(ρ) = (1-p)ρ + p(I/d)"""
    d = rho.shape[0]
    return (1 - p) * rho + p * (np.eye(d, dtype=np.complex128) / d)


def apply_dephasing(rho: ComplexMatrix, gamma: float) -> ComplexMatrix:
    """Dephasing (T2) channel: ρ_ij → ρ_ij · exp(-γ) for i ≠ j"""
    d = rho.shape[0]
    mask = np.ones_like(rho)
    for i in range(d):
        for j in range(d):
            if i != j:
                mask[i, j] = np.exp(-gamma)
    return rho * mask


def apply_amplitude_damping(rho: ComplexMatrix, gamma: float) -> ComplexMatrix:
    """
    Amplitude damping channel (T1 relaxation): |1⟩ → |0⟩ with rate γ.
    Kraus operators: K0 = [[1, 0], [0, √(1-γ)]], K1 = [[0, √γ], [0, 0]]
    """
    K0 = np.array([[1, 0], [0, np.sqrt(1 - gamma)]], dtype=np.complex128)
    K1 = np.array([[0, np.sqrt(gamma)], [0, 0]], dtype=np.complex128)
    return K0 @ rho @ K0.conj().T + K1 @ rho @ K1.conj().T
