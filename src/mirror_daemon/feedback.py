"""
Feedback Control
=================
InjectionGuard (prevents feedback divergence, tracks Lyapunov exponent)
and AdaptiveThreshold (noise-responsive fidelity threshold).

Extracted from mirror_daemon_v2.py (Sections 4, 4B).
"""

from __future__ import annotations

import logging

import numpy as np
from numpy.typing import NDArray

ComplexMatrix = NDArray[np.complex128]

log = logging.getLogger("mirror_daemon_v2")


class InjectionGuard:
    """
    Prevents feedback injection magnitude from growing unchecked.

    v2 upgrade: now tracks a running Lyapunov exponent estimate from
    the injection norm series. If λ_L trends positive, the feedback loop
    is amplifying errors and the guard becomes more conservative.
    """

    def __init__(
        self,
        max_injection_norm: float = 0.3,
        max_consecutive: int = 5,
        reference_window: int = 30,
    ):
        self.max_norm = max_injection_norm
        self.max_consecutive = max_consecutive
        self.window_size = reference_window
        self._consecutive = 0
        self._total_injections = 0
        self._total_rejections = 0
        self._norm_history: list[float] = []
        self._state_window: list[ComplexMatrix] = []

    def update_window(self, state: ComplexMatrix) -> None:
        """Call after every step to keep rolling reference current."""
        self._state_window.append(state.copy())
        if len(self._state_window) > self.window_size:
            self._state_window.pop(0)

    def _window_mean(self, fallback: ComplexMatrix) -> ComplexMatrix:
        """Mean of recent states as rolling reference."""
        if not self._state_window:
            return fallback
        return np.mean(self._state_window, axis=0)

    def check(
        self,
        candidate: ComplexMatrix,
        reference: ComplexMatrix,
    ) -> tuple[bool, float]:
        """
        Returns (approved, norm). Norm measured against rolling window mean.
        """
        rolling_ref = self._window_mean(reference)
        norm = float(np.linalg.norm(candidate - rolling_ref, "fro"))
        self._norm_history.append(norm)
        self._total_injections += 1

        if norm > self.max_norm:
            self._consecutive += 1
            self._total_rejections += 1
            log.warning(
                f"InjectionGuard: REJECTED ‖δψ‖={norm:.4f} > {self.max_norm}. "
                f"Consecutive: {self._consecutive}"
            )
            if self._consecutive >= self.max_consecutive:
                log.error("InjectionGuard: HALT — feedback loop may be diverging.")
            return False, norm
        else:
            self._consecutive = 0
            return True, norm

    @property
    def lyapunov_estimate(self) -> float:
        """
        Estimate the maximal Lyapunov exponent from the injection norm series.

        λ_L = lim_{n→∞} (1/n) Σ ln(‖δψ_i‖ / ‖δψ_{i-1}‖)

        Positive λ_L → diverging feedback (error amplification)
        Negative λ_L → converging feedback (stabilizing)
        Zero λ_L → marginal stability (edge of chaos)
        """
        if len(self._norm_history) < 10:
            return 0.0
        norms = np.array(self._norm_history)
        norms = np.clip(norms, 1e-12, None)
        log_ratios = np.diff(np.log(norms))
        return float(np.mean(log_ratios))

    @property
    def rejection_rate(self) -> float:
        if self._total_injections == 0:
            return 0.0
        return self._total_rejections / self._total_injections

    @property
    def is_diverging(self) -> bool:
        return self._consecutive >= self.max_consecutive

    def summary(self) -> dict:
        return {
            "total_injections": self._total_injections,
            "total_rejections": self._total_rejections,
            "rejection_rate": self.rejection_rate,
            "consecutive_now": self._consecutive,
            "diverging": self.is_diverging,
            "mean_norm": float(np.mean(self._norm_history))
            if self._norm_history
            else 0.0,
            "max_norm_seen": float(np.max(self._norm_history))
            if self._norm_history
            else 0.0,
            "lyapunov_exponent": self.lyapunov_estimate,
        }


class AdaptiveThreshold:
    """
    Dynamically adjusts the fidelity feedback threshold based on
    the noise rate and its derivative.

    τ(t) = τ_base - β · max(dN/dt, 0)

    Under escalating noise (dN/dt > 0): threshold drops, allowing
    more aggressive feedback intervention.
    Under stable noise (dN/dt ≈ 0): threshold stays at τ_base.
    Under decreasing noise (dN/dt < 0): threshold rises above τ_base.

    β is the sensitivity parameter. β = 0 recovers static threshold.
    """

    def __init__(
        self,
        base_threshold: float = 0.85,
        sensitivity: float = 0.05,
        min_threshold: float = 0.55,
        max_threshold: float = 0.95,
        noise_window: int = 20,
    ):
        self.base = base_threshold
        self.beta = sensitivity
        self.min_t = min_threshold
        self.max_t = max_threshold
        self._noise_history: list[float] = []
        self._window = noise_window
        self._current = base_threshold

    def update(self, noise_level: float) -> float:
        """Record current noise and return updated threshold."""
        self._noise_history.append(noise_level)

        if len(self._noise_history) < 3:
            self._current = self.base
            return self._current

        # Estimate dN/dt from recent window
        recent = np.array(self._noise_history[-self._window :])
        if len(recent) < 3:
            self._current = self.base
            return self._current

        # Linear regression for noise rate
        t = np.arange(len(recent), dtype=np.float64)
        slope = np.polyfit(t, recent, 1)[0]

        # Adjust threshold
        adjustment = self.beta * max(slope, 0)
        self._current = np.clip(self.base - adjustment, self.min_t, self.max_t)

        return self._current

    @property
    def current(self) -> float:
        return self._current

    @property
    def noise_derivative(self) -> float:
        if len(self._noise_history) < 3:
            return 0.0
        recent = np.array(self._noise_history[-self._window :])
        t = np.arange(len(recent), dtype=np.float64)
        return float(np.polyfit(t, recent, 1)[0])
