# The No-Cloning Gap

**Why Distributed Architecture Is Mandatory for Quantum Information Persistence**

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.19182150.svg)](https://doi.org/10.5281/zenodo.19182150)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

---

## The Problem

Quantum error correction (QEC) protects against **computational errors** — gate infidelities, decoherence, measurement noise.

QEC provides **no protection** against catastrophic node failure — when an entire processor is lost.

The **no-cloning theorem** prohibits classical backup strategies. You cannot copy a quantum state "just in case."

This creates a fundamental reliability gap:

| Architecture | Annual Survival (30-day MTBF) |
|---|---|
| Classical (backup/restore) | **99.5%** |
| Single quantum node | **0.0005%** |
| Quantum mesh (5-of-3 quorum) | **99.96%** |

The **190,000× gap** is not engineering — it's physics.

---

## The Two-Layer Failure Model

| Layer | Failure Mode | Protection | Status |
|---|---|---|---|
| **Layer 1** | Computational errors | QEC (surface codes, qLDPC) | ✅ Extensive research |
| **Layer 2** | Physical node failure | ??? | ❌ **Unaddressed by QEC** |

QEC operates entirely within Layer 1. When the physical substrate is destroyed, there are no qubits left to vote on error correction.

**Distributed mesh architecture** is the only solution for Layer 2 that works within quantum constraints.

---

## The Sage Bound

A quantum network is **feasible** if and only if:

1. **Fidelity constraint:** `F^n ≥ F_threshold` (~0.85 from QKD literature)
2. **Survival constraint:** `P_mesh(t) ≥ P_target`
3. **Byzantine constraint:** `k ≤ ⌊(N+1)/3⌋ × 2`

This can be evaluated in **constant time** — no expensive discrete-event simulation required.

---

## Quick Start

```bash
pip install -r requirements.txt
python run_simulation.py          # Full Sage Bound pipeline
python run_mesh_quorum.py         # Mesh quorum survival simulation
```

---

## Key Files

| File | Purpose |
|---|---|
| `src/sage_bound_logic.py` | Core feasibility test |
| `src/sage_mesh_quorum.py` | Byzantine consensus engine |
| `src/sage_mesh_nodes.py` | Network topology |
| `src/constants.py` | Hardware parameters (Willow, Helios, QuEra) |
| `papers/no_cloning_gap_prl.tex` | Paper (PRL format) |

---

## Citation

```bibtex
@software{sage_framework_2026,
  author    = {Tylor Flett},
  title     = {The No-Cloning Gap: Why Distributed Architecture Is Mandatory for Quantum Information Persistence},
  version   = {7.1.0},
  year      = {2026},
  doi       = {10.5281/zenodo.19182150},
  url       = {https://github.com/Quantum-Sage/sage-framework}
}
```

---

## Related Work

- Xu et al. (2022) — Distributed QEC for chip-level catastrophic errors ([arXiv:2203.16488](https://arxiv.org/abs/2203.16488))
- Yamaguchi & Kempf (2026) — Encrypted qubits can be cloned ([arXiv:2501.02757](https://arxiv.org/abs/2501.02757))

---

## Author

**Tylor Flett**
ORCID: [0009-0008-5448-0405](https://orcid.org/0009-0008-5448-0405)

---

## License

MIT License. See [LICENSE](LICENSE).
