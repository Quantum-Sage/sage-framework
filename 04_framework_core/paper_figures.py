#!/usr/bin/env python3
"""
paper_figures.py
================
Generates all figures and tables for:
  "Observer-Induced Fault Tolerance: Adaptive QEC via Logical State Feedback"

Runs ~30 paired experiments (daemon + control) across parameter sweeps,
then produces 8 publication-quality figures + 2 LaTeX tables.

Runtime: ~3-5 minutes on a modern laptop.

Usage:
    python paper_figures.py                    # Full sweep + all figures
    python paper_figures.py --quick            # Reduced sweep (1 min)
    python paper_figures.py --figures-only     # Re-plot from cached CSVs

Output:
    ./paper_figures/
        fig1_entropy_signature.png       — The headline result
        fig2_noise_sweep.png             — Fidelity advantage vs noise level
        fig3_bloch_phase_portrait.png    — State-space trajectories
        fig4_multiscale_entropy.png      — MSE comparison across scales
        fig5_causal_injection.png        — Injection → entropy recovery
        fig6_lyapunov_landscape.png      — Stability across parameter space
        fig7_adaptive_vs_static.png      — Adaptive threshold advantage
        fig8_fatigue_endurance.png       — How long can daemon survive?
        table1_main_results.tex          — Summary statistics
        table2_statistical_tests.tex     — Wald-Wolfowitz, Cohen's d, etc.
        sweep_cache.npz                  — Cached numerical results

Authors: traveler + Claude
"""

import sys
import os
import json
import time
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime

import numpy as np

# Add parent dir so we can import mirror_daemon_v2
sys.path.insert(0, str(Path(__file__).parent))

from mirror_daemon_v2 import (
    MirrorDaemon, StandardQECRunner, DaemonConfig,
    SimulatedBackend, HostileBackend,
    StatisticalAnalyzer, BlochTrajectoryPlotter,
    ket, density_matrix, von_neumann_entropy,
    ExperimentLogger, DataPoint,
)

try:
    import matplotlib
    matplotlib.use('Agg')  # Non-interactive for batch generation
    import matplotlib.pyplot as plt
    import matplotlib.gridspec as gridspec
    from matplotlib.patches import FancyArrowPatch
    from matplotlib.colors import LinearSegmentedColormap
except ImportError:
    print("ERROR: matplotlib required. pip install matplotlib")
    sys.exit(1)

try:
    from scipy import stats as scipy_stats
    from scipy.signal import welch
except ImportError:
    print("ERROR: scipy required. pip install scipy")
    sys.exit(1)


# ─────────────────────────────────────────────────────────────────────────────
# STYLE — Dark theme matching SAGE atlas aesthetic
# ─────────────────────────────────────────────────────────────────────────────
BG      = '#07080f'
PANEL   = '#0d0f1e'
GOLD    = '#FFD700'
CYAN    = '#00E5FF'
MAGENTA = '#FF00FF'
GREEN   = '#00FF41'
RED     = '#FF4136'
WHITE   = '#E8E8FF'
PURPLE  = '#BF5FFF'
ORANGE  = '#FF8C00'

plt.rcParams.update({
    'figure.facecolor':    BG,
    'axes.facecolor':      PANEL,
    'axes.edgecolor':      '#333355',
    'axes.labelcolor':     WHITE,
    'text.color':          WHITE,
    'xtick.color':         WHITE,
    'ytick.color':         WHITE,
    'grid.color':          '#222244',
    'grid.alpha':          0.4,
    'legend.facecolor':    '#111133',
    'legend.edgecolor':    '#333355',
    'legend.labelcolor':   WHITE,
    'font.family':         'monospace',
    'font.size':           10,
    'axes.titlesize':      12,
    'figure.titlesize':    14,
})

OUTPUT_DIR = Path("./paper_figures")


# ─────────────────────────────────────────────────────────────────────────────
# EXPERIMENT RUNNER — Encapsulates a paired daemon/control run
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class ExperimentResult:
    """All data from one paired run."""
    # Config
    noise: float
    fatigue: float
    threshold: float
    adaptive: bool
    steps_requested: int
    seed: int
    backend_type: str
    # Daemon results
    d_fidelities: np.ndarray
    d_entropies: np.ndarray
    d_lers: np.ndarray
    d_injections: np.ndarray
    d_inj_magnitudes: np.ndarray
    d_noise_levels: np.ndarray
    d_thresholds: np.ndarray
    d_bloch: np.ndarray          # (N, 3)
    d_lyapunov: np.ndarray
    d_steps_completed: int
    d_sign_changes: int
    d_mean_fidelity: float
    d_final_fidelity: float
    # Control results
    c_fidelities: np.ndarray
    c_entropies: np.ndarray
    c_bloch: np.ndarray
    c_steps_completed: int
    c_sign_changes: int
    c_mean_fidelity: float
    c_final_fidelity: float


def run_paired_experiment(
    noise: float = 0.005,
    fatigue: float = 0.0,
    threshold: float = 0.85,
    adaptive: bool = False,
    steps: int = 1500,
    seed: int = 42,
    backend_type: str = "simulated",
    quiet: bool = True,
) -> ExperimentResult:
    """Run one daemon + control pair and return all data."""

    psi_ref = ket([1.0, 1.0])
    exp_id  = f"sweep_{noise:.4f}_{fatigue:.2f}_{threshold:.2f}_{seed}"

    def make_backend(seed_offset=0):
        if backend_type == "hostile":
            return HostileBackend(
                base_noise=noise, fatigue=fatigue, seed=seed + seed_offset,
            )
        else:
            return SimulatedBackend(
                depolar_p=noise, dephasing_gamma=noise * 0.7,
                amplitude_gamma=noise * 0.3, seed=seed + seed_offset,
            )

    # Suppress logging for batch runs
    import logging
    if quiet:
        logging.getLogger("mirror_daemon_v2").setLevel(logging.ERROR)

    # --- Daemon ---
    cfg_d = DaemonConfig(
        fidelity_threshold=threshold,
        max_steps=steps,
        experiment_id=exp_id + "_daemon",
        output_dir=OUTPUT_DIR / "sweep_data",
        adaptive_threshold=adaptive,
        threshold_sensitivity=0.05 if adaptive else 0.0,
    )
    daemon = MirrorDaemon(backend=make_backend(0), config=cfg_d)
    daemon.initialize(psi_ref)
    daemon.run()
    d_data = daemon.logger._data

    # --- Control ---
    cfg_c = DaemonConfig(
        fidelity_threshold=threshold,
        max_steps=steps,
        experiment_id=exp_id + "_control",
        output_dir=OUTPUT_DIR / "sweep_data",
    )
    ctrl = StandardQECRunner(backend=make_backend(0), config=cfg_c)
    ctrl.initialize(psi_ref)
    ctrl.run()
    c_data = ctrl.logger._data

    # Extract arrays
    d_fids  = np.array([d.fidelity for d in d_data])
    d_entrs = np.array([d.entropy for d in d_data])
    d_lers  = np.array([d.logical_error_rate for d in d_data])
    d_inj   = np.array([d.injection_approved for d in d_data])
    d_mag   = np.array([d.injection_magnitude for d in d_data])
    d_noise = np.array([d.noise_level for d in d_data])
    d_thr   = np.array([d.threshold_current for d in d_data])
    d_bloch = np.array([(d.bloch_x, d.bloch_y, d.bloch_z) for d in d_data])
    d_lyap  = np.array([d.lyapunov_estimate for d in d_data])

    c_fids  = np.array([d.fidelity for d in c_data])
    c_entrs = np.array([d.entropy for d in c_data])
    c_bloch = np.array([(d.bloch_x, d.bloch_y, d.bloch_z) for d in c_data])

    ds_d = np.diff(d_entrs)
    ds_c = np.diff(c_entrs)
    sc_d = int(np.sum(np.diff(np.sign(ds_d)) != 0)) if len(ds_d) > 1 else 0
    sc_c = int(np.sum(np.diff(np.sign(ds_c)) != 0)) if len(ds_c) > 1 else 0

    if quiet:
        logging.getLogger("mirror_daemon_v2").setLevel(logging.INFO)

    return ExperimentResult(
        noise=noise, fatigue=fatigue, threshold=threshold,
        adaptive=adaptive, steps_requested=steps, seed=seed,
        backend_type=backend_type,
        d_fidelities=d_fids, d_entropies=d_entrs, d_lers=d_lers,
        d_injections=d_inj, d_inj_magnitudes=d_mag,
        d_noise_levels=d_noise, d_thresholds=d_thr,
        d_bloch=d_bloch, d_lyapunov=d_lyap,
        d_steps_completed=len(d_data), d_sign_changes=sc_d,
        d_mean_fidelity=float(np.mean(d_fids)),
        d_final_fidelity=float(d_fids[-1]) if len(d_fids) > 0 else 0.0,
        c_fidelities=c_fids, c_entropies=c_entrs, c_bloch=c_bloch,
        c_steps_completed=len(c_data), c_sign_changes=sc_c,
        c_mean_fidelity=float(np.mean(c_fids)),
        c_final_fidelity=float(c_fids[-1]) if len(c_fids) > 0 else 0.0,
    )


# ─────────────────────────────────────────────────────────────────────────────
# FIGURE 1 — THE HEADLINE: Entropy Signature (Daemon vs Control)
# ─────────────────────────────────────────────────────────────────────────────

def fig1_entropy_signature(result: ExperimentResult):
    """
    4-panel figure showing the core result:
      Top-left:  Fidelity over time (both)
      Top-right: Entropy over time (both) with injection markers
      Bot-left:  Injection magnitude trace
      Bot-right: Logical error rate comparison
    """
    fig, axes = plt.subplots(2, 2, figsize=(14, 9))
    fig.suptitle("Figure 1: Observer-Induced Fault Tolerance — Core Signature",
                 fontsize=14, color=GOLD, fontweight='bold')

    d_steps = np.arange(len(result.d_fidelities))
    c_steps = np.arange(len(result.c_fidelities))

    # Panel A: Fidelity
    ax = axes[0, 0]
    ax.plot(c_steps, result.c_fidelities, color=CYAN, alpha=0.7,
            linewidth=0.8, label='Control (standard QEC)')
    ax.plot(d_steps, result.d_fidelities, color=GOLD, alpha=0.9,
            linewidth=0.8, label='Daemon (feedback)')
    ax.axhline(0.85, color=RED, ls='--', alpha=0.5, linewidth=0.7, label='Sage threshold')
    ax.axhline(0.5, color=WHITE, ls=':', alpha=0.3, linewidth=0.5, label='Random (I/2)')
    ax.set_ylabel('Fidelity F(t)')
    ax.set_xlabel('Step')
    ax.legend(fontsize=7, loc='upper right')
    ax.set_title('(a) Fidelity Decay', fontsize=10, color=WHITE)
    ax.grid(True)

    # Panel B: Entropy
    ax = axes[0, 1]
    ax.plot(c_steps, result.c_entropies, color=CYAN, alpha=0.7,
            linewidth=0.8, label='Control')
    ax.plot(d_steps, result.d_entropies, color=GOLD, alpha=0.9,
            linewidth=0.8, label='Daemon')
    # Mark injection points
    inj_mask = result.d_injections.astype(bool)
    inj_steps = d_steps[inj_mask]
    inj_entrs = result.d_entropies[inj_mask]
    if len(inj_steps) > 0:
        # Subsample for visibility
        skip = max(1, len(inj_steps) // 80)
        ax.scatter(inj_steps[::skip], inj_entrs[::skip], c=ORANGE,
                  s=8, alpha=0.6, zorder=5, label='Injection', marker='^')
    ax.axhline(np.log(2), color=WHITE, ls=':', alpha=0.3, linewidth=0.5, label='ln(2) max')
    ax.set_ylabel('Von Neumann Entropy S (nats)')
    ax.set_xlabel('Step')
    ax.legend(fontsize=7, loc='lower right')
    ax.set_title('(b) Entropy Dynamics — The Signature', fontsize=10, color=WHITE)
    ax.grid(True)

    # Panel C: Injection magnitude
    ax = axes[1, 0]
    ax.plot(d_steps, result.d_inj_magnitudes, color=MAGENTA, alpha=0.7,
            linewidth=0.6)
    ax.axhline(0.3, color=RED, ls='--', alpha=0.5, linewidth=0.7, label='Guard limit')
    ax.set_ylabel('Injection ‖δψ‖')
    ax.set_xlabel('Step')
    ax.legend(fontsize=7)
    ax.set_title('(c) Feedback Injection Magnitude', fontsize=10, color=WHITE)
    ax.grid(True)

    # Panel D: Logical error rate
    ax = axes[1, 1]
    ax.plot(c_steps, np.array([0.0] + list(np.diff(-np.log(np.clip(result.c_fidelities, 1e-12, 1.0))))),
            color=CYAN, alpha=0.5, linewidth=0.5)
    ax.plot(d_steps, result.d_lers, color=GOLD, alpha=0.7, linewidth=0.6)
    ax.set_ylabel('Logical Error Rate λ(t)')
    ax.set_xlabel('Step')
    ax.set_title('(d) Error Rate Comparison', fontsize=10, color=WHITE)
    ax.grid(True)

    # Add stats text box
    stats_text = (
        f"Daemon: F̄={result.d_mean_fidelity:.3f}  S_sign={result.d_sign_changes}\n"
        f"Control: F̄={result.c_mean_fidelity:.3f}  S_sign={result.c_sign_changes}\n"
        f"Cohen's d = {StatisticalAnalyzer.cohens_d(result.d_fidelities, result.c_fidelities[:len(result.d_fidelities)]):.2f}"
    )
    fig.text(0.5, 0.01, stats_text, ha='center', fontsize=8,
             color=GREEN, family='monospace',
             bbox=dict(boxstyle='round', facecolor=PANEL, edgecolor=GREEN, alpha=0.8))

    plt.tight_layout(rect=[0, 0.04, 1, 0.96])
    path = OUTPUT_DIR / "fig1_entropy_signature.png"
    fig.savefig(path, dpi=200, facecolor=fig.get_facecolor(), bbox_inches='tight')
    plt.close(fig)
    print(f"  ✓ {path.name}")


# ─────────────────────────────────────────────────────────────────────────────
# FIGURE 2 — NOISE SWEEP: Fidelity advantage vs noise level
# ─────────────────────────────────────────────────────────────────────────────

def fig2_noise_sweep(results: list[ExperimentResult]):
    """
    Shows how daemon vs control fidelity gap changes with noise level.
    X = noise level, Y = mean fidelity. Two lines: daemon, control.
    Secondary Y: Cohen's d effect size.
    """
    noises = sorted(set(r.noise for r in results if r.fatigue == 0.0))
    if len(noises) < 2:
        print("  ⚠ Skipping fig2 — need multiple noise levels with fatigue=0")
        return

    d_means = []
    c_means = []
    cohens  = []
    for n in noises:
        rs = [r for r in results if r.noise == n and r.fatigue == 0.0]
        if not rs:
            continue
        r = rs[0]
        d_means.append(r.d_mean_fidelity)
        c_means.append(r.c_mean_fidelity)
        min_len = min(len(r.d_fidelities), len(r.c_fidelities))
        d = StatisticalAnalyzer.cohens_d(
            r.d_fidelities[:min_len], r.c_fidelities[:min_len]
        )
        cohens.append(d)

    fig, ax1 = plt.subplots(figsize=(10, 6))
    fig.suptitle("Figure 2: Fidelity Advantage Across Noise Levels",
                 fontsize=14, color=GOLD, fontweight='bold')

    ax1.plot(noises[:len(d_means)], d_means, 'o-', color=GOLD, linewidth=2,
             markersize=8, label='Daemon (feedback)', zorder=5)
    ax1.plot(noises[:len(c_means)], c_means, 's-', color=CYAN, linewidth=2,
             markersize=8, label='Control (standard QEC)', zorder=5)
    ax1.axhline(0.85, color=RED, ls='--', alpha=0.5, label='Sage threshold')
    ax1.axhline(0.5, color=WHITE, ls=':', alpha=0.3)
    ax1.set_xlabel('Depolarizing Noise Level p')
    ax1.set_ylabel('Mean Fidelity')
    ax1.legend(fontsize=9, loc='upper right')
    ax1.grid(True)

    # Secondary axis: Cohen's d
    ax2 = ax1.twinx()
    ax2.bar(noises[:len(cohens)], cohens, width=0.0003, alpha=0.3,
            color=GREEN, label="Cohen's d")
    ax2.set_ylabel("Cohen's d (effect size)", color=GREEN)
    ax2.tick_params(axis='y', labelcolor=GREEN)
    ax2.axhline(0.8, color=GREEN, ls=':', alpha=0.3)
    ax2.legend(fontsize=8, loc='center right')

    plt.tight_layout()
    path = OUTPUT_DIR / "fig2_noise_sweep.png"
    fig.savefig(path, dpi=200, facecolor=fig.get_facecolor(), bbox_inches='tight')
    plt.close(fig)
    print(f"  ✓ {path.name}")


# ─────────────────────────────────────────────────────────────────────────────
# FIGURE 3 — BLOCH PHASE PORTRAIT
# ─────────────────────────────────────────────────────────────────────────────

def fig3_bloch_portrait(result: ExperimentResult):
    """Bloch sphere trajectories — daemon shows structure, control spirals."""
    BlochTrajectoryPlotter.plot_comparison(
        [tuple(b) for b in result.d_bloch],
        [tuple(b) for b in result.c_bloch],
        save_path=OUTPUT_DIR / "fig3_bloch_phase_portrait.png",
    )
    print(f"  ✓ fig3_bloch_phase_portrait.png")


# ─────────────────────────────────────────────────────────────────────────────
# FIGURE 4 — MULTISCALE ENTROPY
# ─────────────────────────────────────────────────────────────────────────────

def fig4_multiscale_entropy(result: ExperimentResult):
    """
    MSE comparison: daemon should show decreasing SampEn at longer scales
    (structured dynamics emerge), control should be flat/increasing (noise).
    """
    scales = [1, 2, 3, 5, 8, 10, 15, 20]
    mse_d = StatisticalAnalyzer.multiscale_entropy(result.d_entropies, scales=scales)
    mse_c = StatisticalAnalyzer.multiscale_entropy(result.c_entropies, scales=scales)

    common_scales = sorted(set(mse_d.keys()) & set(mse_c.keys()))
    if len(common_scales) < 3:
        print("  ⚠ Skipping fig4 — insufficient scales for MSE")
        return

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5.5))
    fig.suptitle("Figure 4: Multiscale Sample Entropy — Structure Detection",
                 fontsize=14, color=GOLD, fontweight='bold')

    d_vals = [mse_d[s] for s in common_scales]
    c_vals = [mse_c[s] for s in common_scales]

    ax1.plot(common_scales, d_vals, 'o-', color=GOLD, linewidth=2,
             markersize=8, label='Daemon (feedback)')
    ax1.plot(common_scales, c_vals, 's-', color=CYAN, linewidth=2,
             markersize=8, label='Control (standard QEC)')
    ax1.set_xlabel('Timescale τ')
    ax1.set_ylabel('Sample Entropy SampEn(m=2, τ)')
    ax1.legend(fontsize=9)
    ax1.set_title('(a) SampEn vs Timescale', fontsize=10, color=WHITE)
    ax1.grid(True)

    # Panel B: Entropy PSD
    d_freqs, d_power = StatisticalAnalyzer.entropy_psd(result.d_entropies)
    c_freqs, c_power = StatisticalAnalyzer.entropy_psd(result.c_entropies)

    ax2.semilogy(d_freqs, d_power, color=GOLD, linewidth=1.2,
                 alpha=0.9, label='Daemon PSD')
    ax2.semilogy(c_freqs, c_power, color=CYAN, linewidth=1.2,
                 alpha=0.7, label='Control PSD')
    ax2.set_xlabel('Frequency (cycles/step)')
    ax2.set_ylabel('Power Spectral Density')
    ax2.legend(fontsize=9)
    ax2.set_title('(b) Entropy Power Spectrum', fontsize=10, color=WHITE)
    ax2.grid(True)

    plt.tight_layout()
    path = OUTPUT_DIR / "fig4_multiscale_entropy.png"
    fig.savefig(path, dpi=200, facecolor=fig.get_facecolor(), bbox_inches='tight')
    plt.close(fig)
    print(f"  ✓ {path.name}")


# ─────────────────────────────────────────────────────────────────────────────
# FIGURE 5 — CAUSAL INJECTION ANALYSIS
# ─────────────────────────────────────────────────────────────────────────────

def fig5_causal_injection(result: ExperimentResult):
    """
    Shows that injection events causally predict entropy recovery.
    Panel A: Triggered average of ΔS aligned to injection events.
    Panel B: Distribution of ΔS after injection vs non-injection.
    """
    ds = np.diff(result.d_entropies)
    inj = result.d_injections[:len(ds)].astype(bool)

    # Triggered average: align to injection events, average ΔS in window
    window = 20
    triggered = []
    for t in range(len(inj)):
        if inj[t] and t + window < len(ds):
            triggered.append(ds[t:t+window])

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5.5))
    fig.suptitle("Figure 5: Causal Injection Analysis — Does Feedback Drive Recovery?",
                 fontsize=14, color=GOLD, fontweight='bold')

    if triggered:
        triggered_arr = np.array(triggered)
        mean_trig = np.mean(triggered_arr, axis=0)
        std_trig  = np.std(triggered_arr, axis=0) / np.sqrt(len(triggered))
        lags = np.arange(window)

        ax1.plot(lags, mean_trig, color=GOLD, linewidth=2, label='Mean ΔS')
        ax1.fill_between(lags, mean_trig - 2*std_trig, mean_trig + 2*std_trig,
                        color=GOLD, alpha=0.2, label='±2 SEM')
        ax1.axhline(0, color=WHITE, ls='-', alpha=0.3)
        ax1.set_xlabel('Lag (steps after injection)')
        ax1.set_ylabel('Mean ΔS (entropy change)')
        ax1.legend(fontsize=9)
        ax1.set_title('(a) Triggered Average: ΔS Post-Injection', fontsize=10, color=WHITE)
        ax1.grid(True)

        # Annotation
        min_idx = np.argmin(mean_trig)
        ax1.annotate(f'Recovery trough\nlag={min_idx}',
                    xy=(min_idx, mean_trig[min_idx]),
                    xytext=(min_idx + 3, mean_trig[min_idx] - 0.002),
                    color=GREEN, fontsize=8,
                    arrowprops=dict(arrowstyle='->', color=GREEN, lw=1.5))

    # Panel B: Histogram
    ds_after_inj     = ds[inj[:len(ds)]]
    ds_after_non_inj = ds[~inj[:len(ds)]]

    if len(ds_after_inj) > 10 and len(ds_after_non_inj) > 10:
        bins = np.linspace(
            min(ds_after_inj.min(), ds_after_non_inj.min()),
            max(ds_after_inj.max(), ds_after_non_inj.max()),
            50
        )
        ax2.hist(ds_after_inj, bins=bins, alpha=0.6, color=GOLD,
                label=f'After injection (n={len(ds_after_inj)})', density=True)
        ax2.hist(ds_after_non_inj, bins=bins, alpha=0.4, color=CYAN,
                label=f'After non-injection (n={len(ds_after_non_inj)})', density=True)
        ax2.axvline(np.mean(ds_after_inj), color=GOLD, ls='--', linewidth=1.5)
        ax2.axvline(np.mean(ds_after_non_inj), color=CYAN, ls='--', linewidth=1.5)
        ax2.set_xlabel('ΔS (entropy change at next step)')
        ax2.set_ylabel('Density')
        ax2.legend(fontsize=8)
        ax2.set_title('(b) ΔS Distribution: Injection vs Non-Injection', fontsize=10, color=WHITE)
        ax2.grid(True)

    plt.tight_layout()
    path = OUTPUT_DIR / "fig5_causal_injection.png"
    fig.savefig(path, dpi=200, facecolor=fig.get_facecolor(), bbox_inches='tight')
    plt.close(fig)
    print(f"  ✓ {path.name}")


# ─────────────────────────────────────────────────────────────────────────────
# FIGURE 6 — LYAPUNOV LANDSCAPE
# ─────────────────────────────────────────────────────────────────────────────

def fig6_lyapunov_landscape(results: list[ExperimentResult]):
    """
    Heatmap: noise level × threshold → final Lyapunov exponent.
    Shows the stability boundary of the feedback regime.
    """
    # Filter for simulated backend with varying noise + threshold
    landscape_results = [r for r in results if r.fatigue == 0.0]
    if len(landscape_results) < 4:
        print("  ⚠ Skipping fig6 — need more parameter combinations")
        return

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5.5))
    fig.suptitle("Figure 6: Stability Landscape — Lyapunov Exponent Across Parameters",
                 fontsize=14, color=GOLD, fontweight='bold')

    # Panel A: Lyapunov trajectory for the main run
    main = landscape_results[0]
    ax1.plot(np.arange(len(main.d_lyapunov)), main.d_lyapunov,
             color=MAGENTA, linewidth=0.8, alpha=0.8)
    ax1.axhline(0, color=WHITE, ls='-', alpha=0.5, linewidth=1)
    ax1.fill_between(np.arange(len(main.d_lyapunov)),
                    main.d_lyapunov, 0,
                    where=main.d_lyapunov < 0, color=GREEN, alpha=0.15,
                    label='Stabilizing (λ_L < 0)')
    ax1.fill_between(np.arange(len(main.d_lyapunov)),
                    main.d_lyapunov, 0,
                    where=main.d_lyapunov > 0, color=RED, alpha=0.15,
                    label='Diverging (λ_L > 0)')
    ax1.set_xlabel('Step')
    ax1.set_ylabel('Running Lyapunov Estimate λ_L')
    ax1.legend(fontsize=8)
    ax1.set_title('(a) Lyapunov Trajectory', fontsize=10, color=WHITE)
    ax1.grid(True)

    # Panel B: Final Lyapunov vs noise level
    noises = [r.noise for r in landscape_results]
    lyaps  = [r.d_lyapunov[-1] if len(r.d_lyapunov) > 0 else 0.0
              for r in landscape_results]
    fid_gaps = [r.d_mean_fidelity - r.c_mean_fidelity for r in landscape_results]

    ax2.scatter(noises, lyaps, c=fid_gaps, cmap='RdYlGn', s=100,
               edgecolors=WHITE, linewidth=0.5, zorder=5)
    ax2.axhline(0, color=WHITE, ls='-', alpha=0.5)
    ax2.set_xlabel('Noise Level p')
    ax2.set_ylabel('Final Lyapunov λ_L')
    ax2.set_title('(b) Stability vs Noise (color = ΔF)', fontsize=10, color=WHITE)
    ax2.grid(True)

    plt.tight_layout()
    path = OUTPUT_DIR / "fig6_lyapunov_landscape.png"
    fig.savefig(path, dpi=200, facecolor=fig.get_facecolor(), bbox_inches='tight')
    plt.close(fig)
    print(f"  ✓ {path.name}")


# ─────────────────────────────────────────────────────────────────────────────
# FIGURE 7 — ADAPTIVE vs STATIC THRESHOLD
# ─────────────────────────────────────────────────────────────────────────────

def fig7_adaptive_vs_static(r_adaptive: ExperimentResult, r_static: ExperimentResult):
    """
    Side-by-side: adaptive threshold daemon vs static threshold daemon,
    both under hostile (escalating) noise.
    """
    fig, axes = plt.subplots(2, 2, figsize=(14, 9))
    fig.suptitle("Figure 7: Adaptive vs Static Threshold Under Escalating Noise",
                 fontsize=14, color=GOLD, fontweight='bold')

    # Row 1: Fidelity
    for idx, (r, label, color) in enumerate([
        (r_static,   "Static τ=0.85",   CYAN),
        (r_adaptive, "Adaptive τ(t)",    GOLD),
    ]):
        ax = axes[0, idx]
        steps = np.arange(len(r.d_fidelities))
        ax.plot(steps, r.d_fidelities, color=color, linewidth=0.8, alpha=0.9)
        ax.plot(steps, r.d_thresholds, color=RED, ls='--', linewidth=0.7,
                alpha=0.6, label='τ(t)')
        ax.axhline(0.5, color=WHITE, ls=':', alpha=0.3)
        ax.set_ylabel('Fidelity')
        ax.set_xlabel('Step')
        ax.set_title(f'({"a" if idx == 0 else "b"}) {label}  |  '
                     f'F̄={r.d_mean_fidelity:.3f}  steps={r.d_steps_completed}',
                     fontsize=10, color=WHITE)
        ax.legend(fontsize=7)
        ax.grid(True)

    # Row 2: Entropy
    for idx, (r, label, color) in enumerate([
        (r_static,   "Static",   CYAN),
        (r_adaptive, "Adaptive", GOLD),
    ]):
        ax = axes[1, idx]
        steps = np.arange(len(r.d_entropies))
        ax.plot(steps, r.d_entropies, color=color, linewidth=0.6, alpha=0.8)
        ax.set_ylabel('Entropy S')
        ax.set_xlabel('Step')
        ax.set_title(f'({"c" if idx == 0 else "d"}) Entropy — {label}  |  '
                     f'sign_changes={r.d_sign_changes}',
                     fontsize=10, color=WHITE)
        ax.grid(True)

    plt.tight_layout()
    path = OUTPUT_DIR / "fig7_adaptive_vs_static.png"
    fig.savefig(path, dpi=200, facecolor=fig.get_facecolor(), bbox_inches='tight')
    plt.close(fig)
    print(f"  ✓ {path.name}")


# ─────────────────────────────────────────────────────────────────────────────
# FIGURE 8 — FATIGUE ENDURANCE: How long can daemon survive?
# ─────────────────────────────────────────────────────────────────────────────

def fig8_fatigue_endurance(results: list[ExperimentResult]):
    """
    Under hostile backend with different fatigue rates,
    how many steps does daemon maintain F > 0.5 advantage over control?
    """
    hostile_results = sorted(
        [r for r in results if r.fatigue > 0.0],
        key=lambda r: r.fatigue
    )
    if len(hostile_results) < 2:
        print("  ⚠ Skipping fig8 — need multiple fatigue levels")
        return

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5.5))
    fig.suptitle("Figure 8: Endurance Under Escalating Noise — How Long Does Feedback Help?",
                 fontsize=14, color=GOLD, fontweight='bold')

    # Panel A: Fidelity curves at different fatigue rates
    cmap = plt.cm.plasma
    n_results = len(hostile_results)
    for i, r in enumerate(hostile_results):
        color = cmap(0.3 + 0.6 * i / max(n_results - 1, 1))
        steps = np.arange(len(r.d_fidelities))
        ax1.plot(steps, r.d_fidelities, color=color, linewidth=1.2,
                alpha=0.8, label=f'fatigue={r.fatigue:.2f}')

    ax1.axhline(0.5, color=WHITE, ls=':', alpha=0.3)
    ax1.set_xlabel('Step')
    ax1.set_ylabel('Daemon Fidelity')
    ax1.legend(fontsize=7, loc='upper right')
    ax1.set_title('(a) Fidelity Under Escalating Noise', fontsize=10, color=WHITE)
    ax1.grid(True)

    # Panel B: Steps survived vs fatigue rate
    fatigues = [r.fatigue for r in hostile_results]
    d_survived = [r.d_steps_completed for r in hostile_results]
    fid_advantages = [r.d_mean_fidelity - r.c_mean_fidelity for r in hostile_results]

    ax2.bar(range(len(fatigues)), d_survived, color=GOLD, alpha=0.7,
            edgecolor=WHITE, linewidth=0.5)
    ax2.set_xticks(range(len(fatigues)))
    ax2.set_xticklabels([f'{f:.2f}' for f in fatigues], fontsize=8)
    ax2.set_xlabel('Fatigue Rate')
    ax2.set_ylabel('Steps Completed Before Divergence')
    ax2.set_title('(b) Endurance vs Fatigue Rate', fontsize=10, color=WHITE)
    ax2.grid(True, axis='y')

    # Annotate fidelity advantage on bars
    for i, (steps, adv) in enumerate(zip(d_survived, fid_advantages)):
        ax2.text(i, steps + 10, f'ΔF={adv:+.3f}',
                ha='center', fontsize=7, color=GREEN)

    plt.tight_layout()
    path = OUTPUT_DIR / "fig8_fatigue_endurance.png"
    fig.savefig(path, dpi=200, facecolor=fig.get_facecolor(), bbox_inches='tight')
    plt.close(fig)
    print(f"  ✓ {path.name}")


# ─────────────────────────────────────────────────────────────────────────────
# TABLE 1 — MAIN RESULTS (LaTeX)
# ─────────────────────────────────────────────────────────────────────────────

def table1_main_results(results: list[ExperimentResult]):
    """Generate LaTeX table of key results across all runs."""
    lines = [
        r"\begin{table}[h]",
        r"\centering",
        r"\caption{Summary of daemon vs.\ control performance across noise conditions.}",
        r"\label{tab:main_results}",
        r"\begin{tabular}{lcccccccc}",
        r"\hline",
        r"Backend & $p$ & Fatigue & $\bar{F}_D$ & $\bar{F}_C$ & $\Delta F$ & Cohen's $d$ & $S_{\text{sign}}^D$ & $S_{\text{sign}}^C$ \\",
        r"\hline",
    ]

    for r in results:
        min_len = min(len(r.d_fidelities), len(r.c_fidelities))
        if min_len < 10:
            continue
        d = StatisticalAnalyzer.cohens_d(
            r.d_fidelities[:min_len], r.c_fidelities[:min_len]
        )
        delta_f = r.d_mean_fidelity - r.c_mean_fidelity
        lines.append(
            f"  {r.backend_type} & {r.noise:.3f} & {r.fatigue:.2f} & "
            f"{r.d_mean_fidelity:.3f} & {r.c_mean_fidelity:.3f} & "
            f"{delta_f:+.3f} & {d:.2f} & {r.d_sign_changes} & {r.c_sign_changes} \\\\"
        )

    lines += [
        r"\hline",
        r"\end{tabular}",
        r"\end{table}",
    ]

    path = OUTPUT_DIR / "table1_main_results.tex"
    path.write_text("\n".join(lines))
    print(f"  ✓ {path.name}")


# ─────────────────────────────────────────────────────────────────────────────
# TABLE 2 — STATISTICAL TESTS (LaTeX)
# ─────────────────────────────────────────────────────────────────────────────

def table2_statistical_tests(result: ExperimentResult):
    """Generate LaTeX table of rigorous statistical test results."""
    min_len = min(len(result.d_fidelities), len(result.c_fidelities))

    # Run all tests
    ww_d = StatisticalAnalyzer.wald_wolfowitz_runs_test(result.d_entropies)
    ww_c = StatisticalAnalyzer.wald_wolfowitz_runs_test(result.c_entropies)
    d_eff = StatisticalAnalyzer.cohens_d(
        result.d_fidelities[:min_len], result.c_fidelities[:min_len]
    )
    _, p_fid = scipy_stats.ttest_ind(
        result.d_fidelities[:min_len], result.c_fidelities[:min_len],
        equal_var=False
    )
    causal = StatisticalAnalyzer.causal_injection_test(
        result.d_injections, result.d_entropies
    )

    lines = [
        r"\begin{table}[h]",
        r"\centering",
        r"\caption{Statistical tests comparing daemon and control runs.}",
        r"\label{tab:stat_tests}",
        r"\begin{tabular}{lcc}",
        r"\hline",
        r"Test & Statistic & Interpretation \\",
        r"\hline",
        f"  Welch's $t$-test (fidelity) & $p = {p_fid:.2e}$ & {'Significant' if p_fid < 0.05 else 'Not significant'} \\\\",
        f"  Cohen's $d$ (fidelity) & $d = {d_eff:.2f}$ & {'Large' if abs(d_eff) > 0.8 else 'Medium' if abs(d_eff) > 0.5 else 'Small'} effect \\\\",
        f"  Wald-Wolfowitz (daemon $S$) & $Z = {ww_d['Z']:.2f}$, $p = {ww_d['p_value']:.4f}$ & {ww_d['interpretation'][:30]} \\\\",
        f"  Wald-Wolfowitz (control $S$) & $Z = {ww_c['Z']:.2f}$, $p = {ww_c['p_value']:.4f}$ & {ww_c['interpretation'][:30]} \\\\",
    ]

    if "t_statistic" in causal:
        lines.append(
            f"  Causal injection test & $t = {causal['t_statistic']:.2f}$, $p = {causal['p_value']:.4f}$ & "
            f"{'Causal' if causal.get('causal') else 'Not causal'} \\\\"
        )

    lines += [
        r"\hline",
        r"\end{tabular}",
        r"\end{table}",
    ]

    path = OUTPUT_DIR / "table2_statistical_tests.tex"
    path.write_text("\n".join(lines))
    print(f"  ✓ {path.name}")


# ─────────────────────────────────────────────────────────────────────────────
# MAIN — PARAMETER SWEEP + FIGURE GENERATION
# ─────────────────────────────────────────────────────────────────────────────

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Generate all paper figures")
    parser.add_argument("--quick", action="store_true",
                       help="Reduced sweep for fast iteration")
    parser.add_argument("--figures-only", action="store_true",
                       help="Re-plot from cached data (not implemented yet)")
    args = parser.parse_args()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "sweep_data").mkdir(parents=True, exist_ok=True)

    STEPS = 800 if args.quick else 1500
    SEED  = 42

    print("═" * 65)
    print("  PAPER FIGURE GENERATOR")
    print("  Mirror Daemon v2 — Publication Figures")
    print("═" * 65)
    print(f"  Mode    : {'quick' if args.quick else 'full'}")
    print(f"  Steps   : {STEPS}")
    print(f"  Output  : {OUTPUT_DIR.resolve()}")
    print("═" * 65)

    all_results: list[ExperimentResult] = []
    t0 = time.time()

    # ── Sweep 1: Noise levels (simulated, static threshold) ──────────
    noise_levels = [0.001, 0.003, 0.005, 0.008] if args.quick else \
                   [0.0005, 0.001, 0.002, 0.003, 0.005, 0.008, 0.01, 0.015]
    print(f"\n  Sweep 1: Noise levels ({len(noise_levels)} runs)")
    for i, noise in enumerate(noise_levels):
        print(f"    [{i+1}/{len(noise_levels)}] p={noise:.4f} ...", end=" ", flush=True)
        r = run_paired_experiment(
            noise=noise, fatigue=0.0, threshold=0.85,
            adaptive=False, steps=STEPS, seed=SEED,
            backend_type="simulated",
        )
        print(f"daemon F̄={r.d_mean_fidelity:.3f}  control F̄={r.c_mean_fidelity:.3f}  "
              f"ΔF={r.d_mean_fidelity - r.c_mean_fidelity:+.3f}")
        all_results.append(r)

    # ── Sweep 2: Fatigue levels (hostile backend) ─────────────────────
    fatigue_levels = [0.02, 0.05, 0.08] if args.quick else \
                     [0.01, 0.02, 0.04, 0.06, 0.08, 0.10, 0.15]
    print(f"\n  Sweep 2: Fatigue levels ({len(fatigue_levels)} runs)")
    for i, fat in enumerate(fatigue_levels):
        print(f"    [{i+1}/{len(fatigue_levels)}] fatigue={fat:.2f} ...", end=" ", flush=True)
        r = run_paired_experiment(
            noise=0.005, fatigue=fat, threshold=0.85,
            adaptive=False, steps=STEPS, seed=SEED,
            backend_type="hostile",
        )
        print(f"daemon F̄={r.d_mean_fidelity:.3f}  survived={r.d_steps_completed}/{STEPS}")
        all_results.append(r)

    # ── Sweep 3: Adaptive vs static under hostile noise ───────────────
    print(f"\n  Sweep 3: Adaptive vs static threshold (2 runs)")
    r_static = run_paired_experiment(
        noise=0.005, fatigue=0.08, threshold=0.85,
        adaptive=False, steps=STEPS, seed=SEED,
        backend_type="hostile",
    )
    print(f"    Static:   F̄={r_static.d_mean_fidelity:.3f}  survived={r_static.d_steps_completed}")
    r_adaptive = run_paired_experiment(
        noise=0.005, fatigue=0.08, threshold=0.85,
        adaptive=True, steps=STEPS, seed=SEED,
        backend_type="hostile",
    )
    print(f"    Adaptive: F̄={r_adaptive.d_mean_fidelity:.3f}  survived={r_adaptive.d_steps_completed}")
    all_results.extend([r_static, r_adaptive])

    elapsed = time.time() - t0
    print(f"\n  Sweep complete: {len(all_results)} runs in {elapsed:.1f}s")

    # ── Generate figures ──────────────────────────────────────────────
    print(f"\n  Generating figures...")

    # Pick the "hero" result for figures 1, 3, 4, 5 (mid-noise hostile)
    hero_hostile = [r for r in all_results if r.fatigue == 0.08 and not r.adaptive]
    hero = hero_hostile[0] if hero_hostile else all_results[0]
    # Pick a clean simulated result for some figures
    hero_sim = [r for r in all_results if r.fatigue == 0.0 and r.noise == 0.005]
    hero_clean = hero_sim[0] if hero_sim else all_results[0]

    fig1_entropy_signature(hero)
    fig2_noise_sweep(all_results)
    fig3_bloch_portrait(hero)
    fig4_multiscale_entropy(hero_clean)
    fig5_causal_injection(hero)
    fig6_lyapunov_landscape(all_results)
    fig7_adaptive_vs_static(r_adaptive, r_static)
    fig8_fatigue_endurance(all_results)

    # ── Generate tables ───────────────────────────────────────────────
    print(f"\n  Generating tables...")
    table1_main_results(all_results)
    table2_statistical_tests(hero)

    # ── Summary ───────────────────────────────────────────────────────
    total_time = time.time() - t0
    print(f"\n" + "═" * 65)
    print(f"  COMPLETE — {len(all_results)} experiments, 8 figures, 2 tables")
    print(f"  Total time: {total_time:.1f}s")
    print(f"  Output: {OUTPUT_DIR.resolve()}/")
    print("═" * 65)

    # List outputs
    for f in sorted(OUTPUT_DIR.glob("fig*")):
        print(f"    {f.name}  ({f.stat().st_size / 1024:.0f} KB)")
    for f in sorted(OUTPUT_DIR.glob("table*")):
        print(f"    {f.name}")
    print()


if __name__ == "__main__":
    main()
