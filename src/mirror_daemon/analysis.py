"""
Statistical Analysis & Visualization
======================================
StatisticalAnalyzer (Wald-Wolfowitz, Cohen's d, PSD, sample entropy,
causal injection test) and BlochTrajectoryPlotter.

Extracted from mirror_daemon_v2.py (Sections 8-9).
"""

from __future__ import annotations

import logging
import warnings
from pathlib import Path
from typing import Optional

import numpy as np
from scipy import stats as scipy_stats

from .logging_data import DataPoint

# Optional matplotlib
try:
    import matplotlib.pyplot as plt

    _MATPLOTLIB = True
except ImportError:
    _MATPLOTLIB = False

log = logging.getLogger("mirror_daemon_v2")


class StatisticalAnalyzer:
    """
    Post-experiment statistical analysis for publication-grade rigor.

    Tests:
        1. Wald-Wolfowitz runs test on entropy sign changes
        2. Cohen's d effect size for fidelity difference
        3. Entropy power spectral density
        4. Multiscale sample entropy
        5. Granger-like causal injection test
    """

    @staticmethod
    def wald_wolfowitz_runs_test(entropy_series: np.ndarray) -> dict:
        """
        Wald-Wolfowitz runs test on the sign of dS/dt.

        A "run" is a consecutive sequence of same-sign changes.
        Under H0 (random), expected runs ≈ 2n₁n₂/(n₁+n₂) + 1
        """
        ds = np.diff(entropy_series)
        signs = np.sign(ds)
        signs = signs[signs != 0]

        if len(signs) < 20:
            return {"Z": 0.0, "p_value": 1.0, "interpretation": "insufficient data"}

        n_pos = int(np.sum(signs > 0))
        n_neg = int(np.sum(signs < 0))
        n = n_pos + n_neg

        if n_pos == 0 or n_neg == 0:
            return {"Z": 0.0, "p_value": 1.0, "interpretation": "all same sign"}

        runs = 1 + int(np.sum(np.diff(signs) != 0))
        mu = 2.0 * n_pos * n_neg / n + 1.0
        var = (2.0 * n_pos * n_neg * (2.0 * n_pos * n_neg - n)) / (n**2 * (n - 1.0))

        if var <= 0:
            return {"Z": 0.0, "p_value": 1.0, "interpretation": "degenerate"}

        Z = (runs - mu) / np.sqrt(var)
        p_value = 2.0 * (1.0 - scipy_stats.norm.cdf(abs(Z)))

        if Z > 1.96:
            interp = "SIGNIFICANT oscillation (too many runs, p < 0.05)"
        elif Z < -1.96:
            interp = "SIGNIFICANT monotonicity (too few runs, p < 0.05)"
        else:
            interp = "Not significant (consistent with random)"

        return {
            "Z": float(Z),
            "p_value": float(p_value),
            "n_runs": runs,
            "expected_runs": float(mu),
            "n_positive": n_pos,
            "n_negative": n_neg,
            "interpretation": interp,
        }

    @staticmethod
    def cohens_d(group1: np.ndarray, group2: np.ndarray) -> float:
        """Cohen's d effect size between two groups."""
        n1, n2 = len(group1), len(group2)
        var1, var2 = np.var(group1, ddof=1), np.var(group2, ddof=1)
        pooled_std = np.sqrt(((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2))
        if pooled_std < 1e-12:
            return 0.0
        return float((np.mean(group1) - np.mean(group2)) / pooled_std)

    @staticmethod
    def entropy_psd(entropy_series: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """
        Power spectral density of entropy timeseries via Welch's method.
        Returns (frequencies, power).
        """
        from scipy.signal import welch

        n = len(entropy_series)
        nperseg = min(256, n // 4) if n > 16 else n
        if nperseg < 4:
            return np.array([0.0]), np.array([0.0])
        freqs, power = welch(entropy_series, fs=1.0, nperseg=nperseg)
        return freqs, power

    @staticmethod
    def sample_entropy(series: np.ndarray, m: int = 2, r_frac: float = 0.2) -> float:
        """
        Sample entropy at embedding dimension m and tolerance r.

        SampEn = -ln(A/B) where:
            B = count of template matches of length m
            A = count of template matches of length m+1

        Low SampEn → regular, predictable (structured dynamics).
        High SampEn → irregular, unpredictable (noise-dominated).
        """
        N = len(series)
        if N < m + 2:
            return 0.0
        r = r_frac * np.std(series)
        if r < 1e-12:
            return 0.0

        def _count_matches(dim: int) -> int:
            templates = np.array([series[i : i + dim] for i in range(N - dim)])
            count = 0
            for i in range(len(templates)):
                for j in range(i + 1, len(templates)):
                    if np.max(np.abs(templates[i] - templates[j])) < r:
                        count += 1
            return count

        B = _count_matches(m)
        A = _count_matches(m + 1)

        if B == 0 or A == 0:
            return 0.0
        return float(-np.log(A / B))

    @staticmethod
    def multiscale_entropy(
        series: np.ndarray, scales: list[int] = None, m: int = 2, r_frac: float = 0.2
    ) -> dict[int, float]:
        """
        Multiscale sample entropy: coarse-grain at different timescales τ.

        Key prediction:
            Daemon: SampEn DECREASES with scale (deterministic dynamics emerge)
            Control: SampEn FLAT or INCREASES (no structure at any scale)
        """
        if scales is None:
            scales = [1, 2, 5, 10, 20]

        result = {}
        for tau in scales:
            if len(series) < tau * 10:
                continue
            n_coarse = len(series) // tau
            coarsened = np.array(
                [np.mean(series[i * tau : (i + 1) * tau]) for i in range(n_coarse)]
            )
            se = StatisticalAnalyzer.sample_entropy(coarsened, m=m, r_frac=r_frac)
            result[tau] = se

        return result

    @staticmethod
    def causal_injection_test(
        injection_flags: np.ndarray,
        entropy_series: np.ndarray,
        lag: int = 5,
    ) -> dict:
        """
        Test whether injection events predict subsequent entropy decrease.
        """
        ds = np.diff(entropy_series)
        n = min(len(injection_flags), len(ds))

        ds_after_inj = []
        ds_after_non_inj = []

        for t in range(n - lag):
            mean_ds = float(np.mean(ds[t : t + lag]))
            if injection_flags[t]:
                ds_after_inj.append(mean_ds)
            else:
                ds_after_non_inj.append(mean_ds)

        if len(ds_after_inj) < 5 or len(ds_after_non_inj) < 5:
            return {"status": "insufficient data"}

        a_inj = np.array(ds_after_inj)
        a_non_inj = np.array(ds_after_non_inj)

        t_stat, p_value = scipy_stats.ttest_ind(a_inj, a_non_inj, equal_var=False)
        d = StatisticalAnalyzer.cohens_d(a_inj, a_non_inj)

        return {
            "mean_ds_after_injection": float(np.mean(a_inj)),
            "mean_ds_after_non_injection": float(np.mean(a_non_inj)),
            "t_statistic": float(t_stat),
            "p_value": float(p_value),
            "cohens_d": d,
            "n_injection_events": len(ds_after_inj),
            "n_non_injection_events": len(ds_after_non_inj),
            "causal": p_value < 0.05 and np.mean(a_inj) < np.mean(a_non_inj),
        }

    @classmethod
    def full_comparison(
        cls,
        daemon_data: list[DataPoint],
        control_data: list[DataPoint],
    ) -> dict:
        """
        Complete statistical comparison between daemon and control.
        This generates the numbers for Table 1 of the paper.
        """
        d_fids = np.array([d.fidelity for d in daemon_data])
        c_fids = np.array([d.fidelity for d in control_data])
        d_entrs = np.array([d.entropy for d in daemon_data])
        c_entrs = np.array([d.entropy for d in control_data])
        d_inj = np.array([d.injection_approved for d in daemon_data])

        print("\n" + "═" * 65)
        print("  STATISTICAL ANALYSIS — DAEMON vs. CONTROL")
        print("═" * 65)

        # 1. Fidelity comparison
        d_eff = cls.cohens_d(d_fids, c_fids)
        t_fid, p_fid = scipy_stats.ttest_ind(d_fids, c_fids, equal_var=False)
        print("\n  Fidelity:")
        print(f"    Daemon mean:  {np.mean(d_fids):.6f}")
        print(f"    Control mean: {np.mean(c_fids):.6f}")
        print(f"    Cohen's d:    {d_eff:.4f}")
        print(f"    t-test p:     {p_fid:.2e}")

        # 2. Wald-Wolfowitz on daemon entropy
        ww_d = cls.wald_wolfowitz_runs_test(d_entrs)
        ww_c = cls.wald_wolfowitz_runs_test(c_entrs)
        print("\n  Wald-Wolfowitz Runs Test (entropy):")
        print(
            f"    Daemon:  Z={ww_d['Z']:.3f}  p={ww_d['p_value']:.4f}  → {ww_d['interpretation']}"
        )
        print(
            f"    Control: Z={ww_c['Z']:.3f}  p={ww_c['p_value']:.4f}  → {ww_c['interpretation']}"
        )

        # 3. Multiscale entropy
        mse_d = cls.multiscale_entropy(d_entrs, scales=[1, 2, 5, 10])
        mse_c = cls.multiscale_entropy(c_entrs, scales=[1, 2, 5, 10])
        print("\n  Multiscale Sample Entropy:")
        print("    Scale | Daemon  | Control | Δ")
        for scale in sorted(set(list(mse_d.keys()) + list(mse_c.keys()))):
            sd = mse_d.get(scale, float("nan"))
            sc = mse_c.get(scale, float("nan"))
            print(f"    τ={scale:3d} | {sd:.4f}  | {sc:.4f}  | {sd - sc:+.4f}")

        # 4. Causal injection test
        causal = cls.causal_injection_test(d_inj, d_entrs)
        print("\n  Causal Injection Analysis:")
        if "status" in causal:
            print(f"    {causal['status']}")
        else:
            print(
                f"    Mean ΔS after injection:     {causal['mean_ds_after_injection']:.6f}"
            )
            print(
                f"    Mean ΔS after non-injection: {causal['mean_ds_after_non_injection']:.6f}"
            )
            print(
                f"    t={causal['t_statistic']:.3f}  p={causal['p_value']:.4f}  d={causal['cohens_d']:.3f}"
            )
            print(f"    Causal: {causal['causal']}")

        print("═" * 65 + "\n")

        return {
            "fidelity_cohens_d": d_eff,
            "fidelity_p_value": float(p_fid),
            "wald_wolfowitz_daemon": ww_d,
            "wald_wolfowitz_control": ww_c,
            "multiscale_entropy_daemon": mse_d,
            "multiscale_entropy_control": mse_c,
            "causal_analysis": causal,
        }


class BlochTrajectoryPlotter:
    """
    Publication-quality Bloch sphere trajectory plots.

    Daemon should show: attractor structure, orbital motion, bounded region.
    Control should show: monotonic inward spiral toward origin (I/2).
    """

    @staticmethod
    def plot_comparison(
        daemon_bloch: list[tuple[float, float, float]],
        control_bloch: list[tuple[float, float, float]],
        save_path: Optional[Path] = None,
    ) -> None:
        if not _MATPLOTLIB:
            log.warning("matplotlib not available for Bloch trajectory plot")
            return

        fig = plt.figure(figsize=(16, 7), facecolor="#07080f")
        fig.suptitle(
            "Bloch Sphere Trajectories: Daemon vs Control", color="white", fontsize=14
        )

        for idx, (data, label, color) in enumerate(
            [
                (daemon_bloch, "Mirror Daemon (feedback)", "#FFD700"),
                (control_bloch, "Standard QEC (control)", "#00E5FF"),
            ]
        ):
            ax = fig.add_subplot(1, 2, idx + 1, projection="3d", facecolor="#0d0f1e")
            ax.set_title(label, color="white", fontsize=11)

            # Wireframe Bloch sphere
            u = np.linspace(0, 2 * np.pi, 30)
            v = np.linspace(0, np.pi, 20)
            xs = np.outer(np.cos(u), np.sin(v))
            ys = np.outer(np.sin(u), np.sin(v))
            zs = np.outer(np.ones_like(u), np.cos(v))
            ax.plot_wireframe(xs, ys, zs, color="white", alpha=0.05, linewidth=0.3)

            # Trajectory
            if data:
                coords = np.array(data)
                n = len(coords)
                colors = plt.cm.plasma(np.linspace(0.2, 1.0, n))
                for i in range(n - 1):
                    ax.plot(
                        coords[i : i + 2, 0],
                        coords[i : i + 2, 1],
                        coords[i : i + 2, 2],
                        color=colors[i],
                        alpha=0.6,
                        linewidth=0.5,
                    )
                ax.scatter(*coords[0], color="#00FF41", s=50, zorder=10, label="Start")
                ax.scatter(*coords[-1], color="#FF4136", s=50, zorder=10, label="End")
                ax.scatter(0, 0, 0, color="white", s=30, alpha=0.5, marker="x")

            ax.set_xlim([-1.1, 1.1])
            ax.set_ylim([-1.1, 1.1])
            ax.set_zlim([-1.1, 1.1])
            ax.set_xlabel("X", color="white", fontsize=8)
            ax.set_ylabel("Y", color="white", fontsize=8)
            ax.set_zlabel("Z", color="white", fontsize=8)
            ax.tick_params(colors="white", labelsize=6)
            ax.legend(fontsize=7, loc="upper left")

        plt.tight_layout()
        if save_path:
            fig.savefig(
                save_path, dpi=200, facecolor=fig.get_facecolor(), bbox_inches="tight"
            )
            log.info(f"Bloch trajectory saved: {save_path}")
        plt.close(fig)
