"""
Data & Logging
===============
DataPoint dataclass, ExperimentLogger (CSV + HDF5), and DaemonConfig.

Extracted from mirror_daemon_v2.py (Sections 5-6 config).
"""

from __future__ import annotations

import csv
import logging
import warnings
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

# Optional live plotting
try:
    import matplotlib.pyplot as plt

    _MATPLOTLIB = True
except ImportError:
    _MATPLOTLIB = False

# Optional HDF5 logging
try:
    import h5py

    _H5PY = True
except ImportError:
    _H5PY = False
    warnings.warn("h5py not found — HDF5 logging disabled, CSV only")


log = logging.getLogger("mirror_daemon_v2")


@dataclass
class DataPoint:
    """One row of experimental data."""

    step_id: int
    timestamp_ns: int
    fidelity: float
    entropy: float
    logical_error_rate: float
    injection_magnitude: float
    injection_approved: bool
    correction_applied: bool
    noise_level: float
    backend: str
    # NEW v2 fields
    threshold_current: float = 0.85
    bloch_x: float = 0.0
    bloch_y: float = 0.0
    bloch_z: float = 0.0
    lyapunov_estimate: float = 0.0


class ExperimentLogger:
    """Writes experimental data to CSV + optionally HDF5."""

    CSV_FIELDS = [
        "step_id",
        "timestamp_ns",
        "fidelity",
        "entropy",
        "logical_error_rate",
        "injection_magnitude",
        "injection_approved",
        "correction_applied",
        "noise_level",
        "backend",
        "threshold_current",
        "bloch_x",
        "bloch_y",
        "bloch_z",
        "lyapunov_estimate",
    ]

    def __init__(
        self,
        experiment_id: str,
        output_dir: Path = Path("./mirror_daemon_data"),
        live_plot: bool = False,
    ):
        self.experiment_id = experiment_id
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.live_plot = live_plot and _MATPLOTLIB

        self._data: list[DataPoint] = []
        self._csv_path = self.output_dir / f"{experiment_id}.csv"
        self._h5_path = self.output_dir / f"{experiment_id}.h5"

        self._csv_file = open(self._csv_path, "w", newline="", encoding="utf-8")
        self._writer = csv.writer(self._csv_file)
        self._writer.writerow(self.CSV_FIELDS)
        log.info(f"ExperimentLogger: writing to {self._csv_path}")

        if self.live_plot:
            self._setup_plot()

    def record(self, dp: DataPoint) -> None:
        self._data.append(dp)
        self._writer.writerow(
            [
                dp.step_id,
                dp.timestamp_ns,
                f"{dp.fidelity:.8f}",
                f"{dp.entropy:.8f}",
                f"{dp.logical_error_rate:.8f}",
                f"{dp.injection_magnitude:.8f}",
                int(dp.injection_approved),
                int(dp.correction_applied),
                f"{dp.noise_level:.6f}",
                dp.backend,
                f"{dp.threshold_current:.6f}",
                f"{dp.bloch_x:.6f}",
                f"{dp.bloch_y:.6f}",
                f"{dp.bloch_z:.6f}",
                f"{dp.lyapunov_estimate:.8f}",
            ]
        )
        self._csv_file.flush()

        if self.live_plot and len(self._data) % 10 == 0:
            self._update_plot()

    def _setup_plot(self):
        plt.ion()
        self._fig, self._axes = plt.subplots(4, 1, figsize=(12, 10), tight_layout=True)
        self._fig.suptitle(f"Mirror Daemon v2 — {self.experiment_id}", fontsize=12)
        self._axes[0].set_ylabel("Fidelity F")
        self._axes[1].set_ylabel("Entropy S (nats)")
        self._axes[2].set_ylabel("Logical Error Rate λ")
        self._axes[3].set_ylabel("Lyapunov λ_L")
        self._axes[3].set_xlabel("Step")
        for ax in self._axes:
            ax.grid(True, alpha=0.3)
        self._axes[0].axhline(0.85, color="red", ls="--", alpha=0.7, label="τ_base")
        self._axes[0].legend(fontsize=8)
        plt.show(block=False)

    def _update_plot(self):
        if len(self._data) < 2:
            return
        steps = [d.step_id for d in self._data]
        fids = [d.fidelity for d in self._data]
        entrs = [d.entropy for d in self._data]
        lers = [d.logical_error_rate for d in self._data]
        lyaps = [d.lyapunov_estimate for d in self._data]
        thrs = [d.threshold_current for d in self._data]

        inj_steps = [d.step_id for d in self._data if d.injection_approved]
        inj_fids = [d.fidelity for d in self._data if d.injection_approved]

        ax0, ax1, ax2, ax3 = self._axes
        for ax in self._axes:
            ax.cla()
            ax.grid(True, alpha=0.3)

        ax0.set_ylabel("Fidelity F")
        ax0.plot(steps, thrs, "r--", linewidth=0.8, alpha=0.5, label="τ(t)")
        ax0.plot(steps, fids, "b-", linewidth=0.8, alpha=0.8, label="F(t)")
        if inj_steps:
            ax0.scatter(
                inj_steps,
                inj_fids,
                c="orange",
                s=10,
                zorder=5,
                label="Injection",
                marker="^",
            )
        ax0.legend(fontsize=7)

        ax1.set_ylabel("Entropy S")
        ax1.plot(steps, entrs, "g-", linewidth=0.8, alpha=0.8)

        ax2.set_ylabel("λ(t)")
        ax2.plot(steps, lers, "r-", linewidth=0.8, alpha=0.8)

        ax3.set_ylabel("Lyapunov λ_L")
        ax3.set_xlabel("Step")
        ax3.plot(steps, lyaps, "m-", linewidth=0.8, alpha=0.8)
        ax3.axhline(0, color="white", ls="-", alpha=0.3)

        n = len(steps)
        for ax in self._axes:
            ax.set_xlim(max(0, n - 500), n + 10)

        self._fig.canvas.draw()
        self._fig.canvas.flush_events()

    def flush_h5(self) -> None:
        if not _H5PY or not self._data:
            return
        with h5py.File(self._h5_path, "w") as f:
            f.attrs["experiment_id"] = self.experiment_id
            f.attrs["n_steps"] = len(self._data)
            f.attrs["timestamp"] = datetime.now(timezone.utc).isoformat()
            ds = f.create_group("timeseries")
            for fname in self.CSV_FIELDS:
                if fname == "backend":
                    continue
                arr = np.array([getattr(d, fname) for d in self._data])
                ds.create_dataset(fname, data=arr, compression="gzip")
        log.info(f"HDF5 written: {self._h5_path}")

    def close(self) -> None:
        self._csv_file.close()
        self.flush_h5()
        if self.live_plot and _MATPLOTLIB:
            plt.ioff()


@dataclass
class DaemonConfig:
    """All tunable parameters."""

    fidelity_threshold: float = 0.85
    warmup_steps: int = 20
    code_distance: int = 3
    max_steps: int = 10_000
    max_injection_norm: float = 0.30
    max_consecutive_reject: int = 5
    # Adaptive threshold parameters
    adaptive_threshold: bool = True
    threshold_sensitivity: float = 0.05
    # Logging
    experiment_id: str = field(
        default_factory=lambda: datetime.now(timezone.utc).strftime("exp_%Y%m%d_%H%M%S")
    )
    output_dir: Path = Path("./mirror_daemon_data")
    live_plot: bool = False
