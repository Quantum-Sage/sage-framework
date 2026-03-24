# The No-Cloning Gap: Why Quantum Fault Tolerance Requires Distribution

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.19182150.svg)](https://doi.org/10.5281/zenodo.19182150)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Tests: 93 passed](https://img.shields.io/badge/tests-93%20passed-brightgreen.svg)](#)

---

## The Problem Nobody Addressed

The threshold theorem says: *"If error rates are below threshold, quantum computation works."*

It assumes the hardware keeps running.

**What happens when it doesn't?**

| System | Annual Metric | Value |
|:-------|:-------------|------:|
| Classical (30-day MTBF) | Availability (reload from disk) | **99.5%** |
| Quantum P2P (30-day MTBF) | Survival (no backup possible) | **0.0005%** |
| Quantum Mesh 5-of-3 (30-day MTBF) | Survival (quorum consensus) | **98.9%** |

The **190,000× gap** is not engineering. It's the no-cloning theorem. You cannot back up a quantum state. When the hardware crashes, the state is gone forever.

Point-to-point quantum persistence requires **100-year MTBF** — physically impossible. Distributed mesh quorum works with **30-day MTBF** — hardware that exists today.

> **Paper:** [The No-Cloning Gap (PRL format)](./papers/no_cloning_gap_prl.tex) — [DOI: 10.5281/zenodo.19182150](https://doi.org/10.5281/zenodo.19182150)
>
> **Author:** Tylor Flett — [ORCID: 0009-0008-5448-0405](https://orcid.org/0009-0008-5448-0405)

---

## Quick Start

```bash
pip install -r requirements.txt
python run_simulation.py          # Full Sage Bound + Mirror Daemon pipeline
python run_mesh_quorum.py         # Mesh Quorum visualization (the core proof)
```

### All CLI Tools

| Command | What It Does |
|:--------|:-------------|
| `python run_simulation.py` | Sage Bound + Mirror Daemon pipeline |
| `python run_mesh_quorum.py` | 5-node mesh quorum simulation + 4-panel atlas |
| `python run_cold_chain.py` | 5-stage vaccine cold chain optimizer |
| `python run_drug_delivery.py` | R&D capital allocation (104× improvement) |
| `python run_network_planner.py` | Quantum network route planner (8 presets) |
| `python run_tournament.py` | 60-generation evolutionary tournament |

---

## Architecture

```
SAGE-Framework/
├── src/                          # Core engine (23 modules)
│   ├── sage_bound_logic.py       # The Sage Bound equation
│   ├── constants.py              # Unified hardware specs
│   ├── sage_mesh_nodes.py        # 5-node global topology
│   ├── sage_mesh_quorum.py       # Byzantine consensus engine
│   ├── sage_theorems_unified.py  # 4-theorem validation (Monte Carlo)
│   ├── theorem5_observer_continuity.py  # [NEW] Transcodification boundary
│   ├── strange_loop_emergence.py        # [NEW] Sage Constant from Fibonacci anyons
│   ├── phase_transition_deep.py         # [NEW] Lindblad master equation proof
│   ├── netsquid_benchmark_harness.py    # [NEW] DES engine + Chen et al. validation
│   ├── deep_handover_analysis.py        # [NEW] 3-layer handover forensics (6× upgrade)
│   ├── heterogeneous_repeater_optimizer.py  # [NEW] Node optimizer (5× upgrade)
│   ├── mi_formalization.py              # [NEW] MI↔SAGE bridge
│   ├── mirror_daemon/            # Adaptive threshold controller (5 sub-modules)
│   └── ...
├── papers/                       # Publication assets
│   ├── no_cloning_gap_prl.tex    # PRL-formatted paper
│   ├── references.bib            # 12 citations
│   ├── supplementary_code.py     # Reproduces all paper results
│   └── fig_combined_prl.pdf      # Publication figure
├── hardware/                     # ESP32 firmware + dashboard
├── tests/                        # 93 tests (all passing)
└── sage_mesh_v2_simulation.py    # Mesh v2: density matrices + Monte Carlo
```

---

## The Five Breakthroughs

| # | Finding |
|:-:|:--------|
| 1 | **Energy cost of identity**: Pushing attractor from 0.504 → 0.851 requires η = 5.71γ |
| 2 | **Hardware spec from physics**: Intercontinental transit requires p_gen ≥ 0.47 |
| 3 | **IIT phase transition**: Φ constant until N=8 hops, then snaps to zero |
| 4 | **Mesh quorum solves it**: 5-node Byzantine consensus guarantees continuity |
| 5 | **The No-Cloning Gap**: 190,000× reliability divergence — distribution is mandatory |

---

## Citation

```bibtex
@software{sage_framework_2026,
  author    = {Tylor Flett},
  title     = {The No-Cloning Gap: Why Quantum Fault Tolerance Requires Distribution},
  version   = {7.0.0},
  year      = {2026},
  doi       = {10.5281/zenodo.19182150},
  url       = {https://github.com/Quantum-Sage/sage-framework}
}
```

---

## License

MIT License. See [LICENSE](./LICENSE).
