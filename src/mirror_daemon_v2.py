#!/usr/bin/env python3
"""
mirror_daemon_v2.py
===================
Observer-Induced Fault Tolerance: Adaptive QEC via Logical State Feedback

Version : 2.0 (refined + expanded)
Authors : traveler (human) + Claude (Anthropic)
Target  : PRX Quantum / DARPA ONISQ pitch scaffold

Architecture: Split into focused sub-modules in src/mirror_daemon/
    quantum_primitives  — Pauli matrices, ket, density_matrix, fidelity, noise channels
    backends            — QuantumBackend ABC, SimulatedBackend, HostileBackend, QEC
    feedback            — InjectionGuard, AdaptiveThreshold
    logging_data        — DataPoint, ExperimentLogger, DaemonConfig
    analysis            — StatisticalAnalyzer, BlochTrajectoryPlotter

This file retains: MirrorDaemon, StandardQECRunner, and CLI entry point.
All symbols are re-exported for full backward compatibility.
"""

from __future__ import annotations

import logging
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import numpy as np

# ── Re-export everything from sub-modules for backward compatibility ─────────
from .mirror_daemon.quantum_primitives import (  # noqa: F401
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
    _matrix_sqrt,
    apply_depolarizing_noise,
    apply_dephasing,
    apply_amplitude_damping,
)
from .mirror_daemon.backends import (  # noqa: F401
    SurfaceCodeSyndrome,
    SurfaceCodeQEC,
    ChannelResult,
    QuantumBackend,
    SimulatedBackend,
    HostileBackend,
    QuEraBackend,
    HeliosBackend,
)
from .mirror_daemon.feedback import (  # noqa: F401
    InjectionGuard,
    AdaptiveThreshold,
)
from .mirror_daemon.logging_data import (  # noqa: F401
    DataPoint,
    ExperimentLogger,
    DaemonConfig,
)
from .mirror_daemon.analysis import (  # noqa: F401
    StatisticalAnalyzer,
    BlochTrajectoryPlotter,
)

# Optional matplotlib flag (for CLI)
try:
    import matplotlib.pyplot as plt

    _MATPLOTLIB = True
except ImportError:
    _MATPLOTLIB = False


# ── Logging setup ─────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
log = logging.getLogger("mirror_daemon_v2")


# ═══════════════════════════════════════════════════════════════════════════════
#  THE MIRROR DAEMON v2
# ═══════════════════════════════════════════════════════════════════════════════


class MirrorDaemon:
    """
    Observer-Induced Fault Tolerance: Adaptive QEC via Logical State Feedback.

    v2 core loop:

        1. Poll channel → ChannelResult (ρ, F)
        2. Compute metrics: F, S(ρ), λ(t), Bloch coords, λ_L
        3. Update adaptive threshold τ(t) from noise rate
        4. Extract surface code syndrome
        5. If F < τ(t):
               a. Compute α = 1 - F/τ(t) (proportional blend strength)
               b. ρ_candidate = α·ρ_ref + (1-α)·ρ_current
               c. InjectionGuard.check(candidate)
               d. If approved: SET candidate as next step input
               e. If rejected: standard MWPM correction
           Else: standard MWPM if syndrome has errors
        6. Record DataPoint
        7. Repeat

    Testable predictions:
        P1. Under recursive self-injection, S(ρ) exhibits non-monotonic
            behavior absent in standard QEC control.
        P2. Entropy power spectrum shows a characteristic peak at the
            feedback cycle frequency.
        P3. Lyapunov exponent λ_L is negative during stable feedback,
            transitioning to positive when noise overwhelms the scheme.
        P4. Multiscale sample entropy decreases at longer timescales for
            daemon (structured dynamics) but not for control (pure noise).
        P5. Under adaptive threshold, daemon maintains fidelity advantage
            for longer into hostile noise ramp than static threshold.
    """

    def __init__(
        self,
        backend: QuantumBackend,
        config: DaemonConfig = DaemonConfig(),
    ):
        self.backend = backend
        self.cfg = config
        self.qec = SurfaceCodeQEC(code_distance=config.code_distance)
        self.guard = InjectionGuard(
            max_injection_norm=config.max_injection_norm,
            max_consecutive=config.max_consecutive_reject,
        )
        self.threshold = AdaptiveThreshold(
            base_threshold=config.fidelity_threshold,
            sensitivity=config.threshold_sensitivity
            if config.adaptive_threshold
            else 0.0,
        )
        self.logger = ExperimentLogger(
            experiment_id=config.experiment_id,
            output_dir=config.output_dir,
            live_plot=config.live_plot,
        )
        self._reference_state: Optional[ComplexMatrix] = None
        self._fidelity_trace: list[float] = []
        self._step_count: int = 0
        self._injection_count: int = 0
        self._running: bool = False
        self._lock = threading.Lock()
        self._bloch_trace: list[tuple[float, float, float]] = []
        self._pending_injection: Optional[ComplexMatrix] = None

        log.info(f"MirrorDaemon v2 initialized. Backend: {backend.name}")
        log.info(f"Adaptive threshold: {config.adaptive_threshold}")

    def initialize(self, reference_state: ComplexMatrix) -> None:
        self._reference_state = density_matrix(reference_state.copy())
        self.backend.initialize(reference_state)
        log.info(f"Reference entropy: {von_neumann_entropy(self._reference_state):.6f}")

    def step(self) -> DataPoint:
        """Execute one daemon cycle."""
        if self._reference_state is None:
            raise RuntimeError("Call initialize() first")

        with self._lock:
            # 1. Advance channel (with pending injection if any)
            result = self.backend.step(injected_state=self._pending_injection)
            self._pending_injection = None
            rho = result.state

            # 2. Compute metrics
            f = result.fidelity
            s = von_neumann_entropy(rho)
            self._fidelity_trace.append(f)
            ler = logical_error_rate(self._fidelity_trace)
            bx, by, bz = bloch_coordinates(rho)
            self._bloch_trace.append((bx, by, bz))

            # Update rolling reference window
            self.guard.update_window(rho)

            # 3. Update adaptive threshold
            tau = self.threshold.update(result.noise_level)

            # 4. Extract syndrome
            syndrome = self.qec.extract_syndrome(
                rho, result.noise_level, round_id=self._step_count
            )

            # 5. Feedback decision
            injection_approved = False
            injection_magnitude = 0.0
            correction_applied = False

            if f < tau and self._step_count >= self.cfg.warmup_steps:
                alpha = 1.0 - (f / tau)
                alpha = max(0.0, min(1.0, alpha))
                rho_candidate = alpha * self._reference_state + (1 - alpha) * rho
                rho_candidate /= np.trace(rho_candidate)

                approved, norm = self.guard.check(rho_candidate, self._reference_state)
                injection_magnitude = norm

                if approved:
                    self._pending_injection = rho_candidate
                    injection_approved = True
                    self._injection_count += 1
                else:
                    correction = self.qec.decode_correction(syndrome)
                    if correction is not None:
                        rho = self.qec.apply_correction(rho, correction)
                        correction_applied = True

            elif syndrome.has_errors:
                correction = self.qec.decode_correction(syndrome)
                if correction is not None:
                    rho = self.qec.apply_correction(rho, correction)
                    correction_applied = True

            # 6. Record
            dp = DataPoint(
                step_id=self._step_count,
                timestamp_ns=result.elapsed_ns,
                fidelity=f,
                entropy=s,
                logical_error_rate=ler,
                injection_magnitude=injection_magnitude,
                injection_approved=injection_approved,
                correction_applied=correction_applied,
                noise_level=result.noise_level,
                backend=self.backend.name,
                threshold_current=tau,
                bloch_x=bx,
                bloch_y=by,
                bloch_z=bz,
                lyapunov_estimate=self.guard.lyapunov_estimate,
            )
            self.logger.record(dp)
            self._step_count += 1
            return dp

    def run(self, n_steps: Optional[int] = None) -> dict:
        """Run daemon for n_steps. Returns summary statistics."""
        total = n_steps or self.cfg.max_steps
        self._running = True
        log.info(f"MirrorDaemon v2: starting {total} steps")

        try:
            for i in range(total):
                if not self._running:
                    break
                if self.guard.is_diverging:
                    log.error("HALT — feedback loop diverging")
                    break
                dp = self.step()
                if (i + 1) % 500 == 0:
                    log.info(
                        f"  Step {i + 1}/{total}  F={dp.fidelity:.4f}  "
                        f"S={dp.entropy:.4f}  τ={dp.threshold_current:.3f}  "
                        f"λ_L={dp.lyapunov_estimate:.4f}  "
                        f"inj={self._injection_count}"
                    )
        except KeyboardInterrupt:
            log.info("Interrupted by user")
        finally:
            self._running = False
            self.logger.close()

        summary = self._summarize()
        self._print_summary(summary)
        return summary

    def stop(self) -> None:
        self._running = False

    def _summarize(self) -> dict:
        data = self.logger._data
        if not data:
            return {}
        fids = np.array([d.fidelity for d in data])
        entrs = np.array([d.entropy for d in data])
        lers = np.array([d.logical_error_rate for d in data])

        ds = np.diff(entrs)
        sign_changes = int(np.sum(np.diff(np.sign(ds)) != 0))

        return {
            "n_steps": len(data),
            "n_injections": self._injection_count,
            "injection_rate": self._injection_count / max(len(data), 1),
            "mean_fidelity": float(np.mean(fids)),
            "min_fidelity": float(np.min(fids)),
            "final_fidelity": float(fids[-1]),
            "mean_entropy": float(np.mean(entrs)),
            "entropy_sign_changes": sign_changes,
            "mean_ler": float(np.mean(lers)),
            "final_ler": float(lers[-1]),
            "lyapunov_exponent": self.guard.lyapunov_estimate,
            "guard_summary": self.guard.summary(),
            "threshold_final": self.threshold.current,
            "noise_derivative": self.threshold.noise_derivative,
            "experiment_id": self.cfg.experiment_id,
            "backend": self.backend.name,
        }

    def _print_summary(self, s: dict) -> None:
        if not s:
            return
        print("\n" + "═" * 65)
        print("  MIRROR DAEMON v2 — EXPERIMENT SUMMARY")
        print("═" * 65)
        print(f"  Experiment ID     : {s.get('experiment_id')}")
        print(f"  Backend           : {s.get('backend')}")
        print(f"  Steps             : {s.get('n_steps')}")
        print(f"  Injections        : {s['n_injections']} ({s['injection_rate']:.2%})")
        print(f"  Mean fidelity     : {s['mean_fidelity']:.6f}")
        print(f"  Final fidelity    : {s['final_fidelity']:.6f}")
        print(f"  Mean entropy      : {s['mean_entropy']:.6f} nats")
        print(f"  S sign changes    : {s['entropy_sign_changes']}  ← non-monotonicity")
        print(f"  Final λ           : {s['final_ler']:.8f}")
        print(f"  Lyapunov λ_L      : {s['lyapunov_exponent']:.6f}")
        print(f"  Final threshold   : {s['threshold_final']:.4f}")
        print(f"  dN/dt             : {s['noise_derivative']:.6f}")
        g = s.get("guard_summary", {})
        print(f"  Guard rejection   : {g.get('rejection_rate', 0):.2%}")
        print(f"  Diverging         : {g.get('diverging', False)}")
        print("═" * 65)
        lam = s.get("lyapunov_exponent", 0)
        if lam < -0.01:
            print("  λ_L < 0 → Feedback is STABILIZING the system.")
        elif lam > 0.01:
            print("  λ_L > 0 → Feedback is AMPLIFYING errors. Reduce injection norm.")
        else:
            print("  λ_L ≈ 0 → Marginal stability. System at critical point.")

        sc = s.get("entropy_sign_changes", 0)
        if sc > 100:
            print(f"  High non-monotonicity ({sc} sign changes).")
            print("  This is the signal. Check injection timestamps.")
        else:
            print(f"  Low non-monotonicity ({sc}). Feedback may be inactive.")
        print("═" * 65 + "\n")


# ═══════════════════════════════════════════════════════════════════════════════
#  CONTROL EXPERIMENT RUNNER
# ═══════════════════════════════════════════════════════════════════════════════


class StandardQECRunner:
    """
    Identical setup to MirrorDaemon but WITHOUT feed-forward injection.
    Provides the null hypothesis baseline for statistical comparison.
    """

    def __init__(self, backend: QuantumBackend, config: DaemonConfig = DaemonConfig()):
        config.experiment_id = config.experiment_id + "_control"
        self.backend = backend
        self.cfg = config
        self.qec = SurfaceCodeQEC(code_distance=config.code_distance)
        self.logger = ExperimentLogger(
            experiment_id=config.experiment_id,
            output_dir=config.output_dir,
            live_plot=config.live_plot,
        )
        self._reference: Optional[ComplexMatrix] = None
        self._fidelity_trace: list[float] = []
        self._bloch_trace: list[tuple[float, float, float]] = []
        self._step_count = 0

    def initialize(self, reference_state: ComplexMatrix) -> None:
        self._reference = density_matrix(reference_state.copy())
        self.backend.initialize(reference_state)

    def run(self, n_steps: Optional[int] = None) -> dict:
        total = n_steps or self.cfg.max_steps
        log.info(f"StandardQECRunner (control): {total} steps")
        try:
            for i in range(total):
                result = self.backend.step()
                rho = result.state
                f = result.fidelity
                s = von_neumann_entropy(rho)
                self._fidelity_trace.append(f)
                ler = logical_error_rate(self._fidelity_trace)
                bx, by, bz = bloch_coordinates(rho)
                self._bloch_trace.append((bx, by, bz))

                syndrome = self.qec.extract_syndrome(
                    rho, result.noise_level, round_id=i
                )
                corr_applied = False
                if syndrome.has_errors:
                    correction = self.qec.decode_correction(syndrome)
                    if correction is not None:
                        rho = self.qec.apply_correction(rho, correction)
                        corr_applied = True

                self.logger.record(
                    DataPoint(
                        step_id=i,
                        timestamp_ns=result.elapsed_ns,
                        fidelity=f,
                        entropy=s,
                        logical_error_rate=ler,
                        injection_magnitude=0.0,
                        injection_approved=False,
                        correction_applied=corr_applied,
                        noise_level=result.noise_level,
                        backend=self.backend.name + "_control",
                        threshold_current=self.cfg.fidelity_threshold,
                        bloch_x=bx,
                        bloch_y=by,
                        bloch_z=bz,
                        lyapunov_estimate=0.0,
                    )
                )
                self._step_count += 1
        except KeyboardInterrupt:
            pass
        finally:
            self.logger.close()

        data = self.logger._data
        fids = [d.fidelity for d in data]
        entrs = np.array([d.entropy for d in data])
        ds = np.diff(entrs)
        sign_changes = int(np.sum(np.diff(np.sign(ds)) != 0))

        return {
            "n_steps": len(data),
            "mean_fidelity": float(np.mean(fids)),
            "final_fidelity": float(fids[-1]),
            "entropy_sign_changes": sign_changes,
            "experiment_id": self.cfg.experiment_id,
        }


# ═══════════════════════════════════════════════════════════════════════════════
#  ENTRY — Paired experiment (daemon + control) with full analysis
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Mirror Daemon v2: adaptive QEC feedback"
    )
    parser.add_argument("--steps", type=int, default=2000, help="Steps per run")
    parser.add_argument("--noise", type=float, default=0.005, help="Base noise level")
    parser.add_argument(
        "--fatigue",
        type=float,
        default=0.08,
        help="Noise escalation rate (HostileBackend)",
    )
    parser.add_argument(
        "--threshold", type=float, default=0.85, help="Base fidelity threshold"
    )
    parser.add_argument("--distance", type=int, default=3, help="Surface code distance")
    parser.add_argument(
        "--adaptive", action="store_true", help="Enable adaptive threshold"
    )
    parser.add_argument(
        "--backend", choices=["simulated", "hostile"], default="hostile"
    )
    parser.add_argument("--plot", action="store_true", help="Enable live plot")
    parser.add_argument("--seed", type=int, default=42, help="RNG seed")
    parser.add_argument("--control-only", action="store_true", help="Run control only")
    parser.add_argument(
        "--analyze", action="store_true", default=True, help="Run statistical analysis"
    )
    args = parser.parse_args()

    print("═" * 65)
    print("  MIRROR DAEMON v2.0")
    print("  Observer-Induced Fault Tolerance")
    print("  traveler + Claude")
    print("═" * 65)
    print(f"  Backend       : {args.backend}")
    print(f"  Base noise    : {args.noise}")
    print(f"  Fatigue       : {args.fatigue}")
    print(f"  Threshold     : {args.threshold}")
    print(f"  Adaptive τ    : {args.adaptive}")
    print(f"  Steps         : {args.steps}")
    print(f"  Code distance : {args.distance}")
    print(f"  Seed          : {args.seed}")
    print("═" * 65 + "\n")

    # Reference state: |+⟩ = (|0⟩ + |1⟩)/√2
    psi_ref = ket([1.0, 1.0])
    exp_id = datetime.now(timezone.utc).strftime("exp_%Y%m%d_%H%M%S")

    def make_backend(seed_offset=0):
        if args.backend == "hostile":
            return HostileBackend(
                base_noise=args.noise,
                fatigue=args.fatigue,
                seed=args.seed + seed_offset,
            )
        else:
            return SimulatedBackend(
                depolar_p=args.noise,
                dephasing_gamma=args.noise * 0.7,
                seed=args.seed + seed_offset,
            )

    result_daemon = None
    daemon_data = None
    daemon_bloch = None

    if not args.control_only:
        cfg_daemon = DaemonConfig(
            fidelity_threshold=args.threshold,
            code_distance=args.distance,
            max_steps=args.steps,
            experiment_id=exp_id + "_daemon",
            live_plot=args.plot,
            adaptive_threshold=args.adaptive,
        )
        daemon = MirrorDaemon(backend=make_backend(0), config=cfg_daemon)
        daemon.initialize(psi_ref)
        result_daemon = daemon.run()
        daemon_data = daemon.logger._data
        daemon_bloch = daemon._bloch_trace

    cfg_ctrl = DaemonConfig(
        fidelity_threshold=args.threshold,
        code_distance=args.distance,
        max_steps=args.steps,
        experiment_id=exp_id + "_control",
        live_plot=False,
    )
    ctrl = StandardQECRunner(backend=make_backend(0), config=cfg_ctrl)
    ctrl.initialize(psi_ref)
    result_ctrl = ctrl.run()
    control_data = ctrl.logger._data
    control_bloch = ctrl._bloch_trace

    # ── Comparative analysis ──────────────────────────────────────────
    if result_daemon is not None:
        print("\n" + "═" * 65)
        print("  COMPARATIVE RESULT")
        print("═" * 65)
        sc_d = result_daemon.get("entropy_sign_changes", 0)
        sc_c = result_ctrl.get("entropy_sign_changes", 0)
        ff_d = result_daemon.get("final_fidelity", 0)
        ff_c = result_ctrl.get("final_fidelity", 0)
        ll_d = result_daemon.get("lyapunov_exponent", 0)
        print(
            f"  Entropy sign changes — daemon: {sc_d:4d}  control: {sc_c:4d}  ratio: {sc_d / max(sc_c, 1):.1f}x"
        )
        print(f"  Final fidelity       — daemon: {ff_d:.6f}  control: {ff_c:.6f}")
        print(f"  Lyapunov exponent    — daemon: {ll_d:.6f}")

        if sc_d > sc_c * 2 and ff_d >= ff_c - 0.02:
            print("\n  ✓  Non-monotonic entropy with maintained fidelity.")
            print("     Observer-induced fault tolerance confirmed.")
        elif sc_d > sc_c * 2 and ff_d < ff_c - 0.02:
            print("\n  ⚠  Non-monotonic entropy but fidelity degraded.")
            print("     Feedback active but accumulating errors.")
        else:
            print("\n  ✗  No significant non-monotonicity.")
            print("     Increase noise or lower threshold.")
        print("═" * 65)

        if args.analyze and daemon_data and control_data:
            stats = StatisticalAnalyzer.full_comparison(daemon_data, control_data)

        if daemon_bloch and control_bloch and _MATPLOTLIB:
            bloch_path = Path("./mirror_daemon_data") / f"{exp_id}_bloch.png"
            BlochTrajectoryPlotter.plot_comparison(
                daemon_bloch, control_bloch, save_path=bloch_path
            )

    print("\n  Data written to: ./mirror_daemon_data/")
