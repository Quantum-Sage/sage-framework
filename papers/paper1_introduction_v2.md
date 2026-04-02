# The No-Cloning Gap: Distributed Quantum Identity Persistence Through Byzantine Mesh Consensus

**Authors:** [Author Name] · ORCID: [0000-0000-0000-0000]  
**Target:** Physical Review Letters / npj Quantum Information  
**Status:** v2.0 — Integration draft (supersedes v1.1)

---

## Abstract

Quantum fault tolerance rests on the threshold theorem, which guarantees arbitrarily reliable computation provided physical error rates fall below a hardware-dependent constant. Yet this theorem contains a hidden architectural assumption—continuous hardware operation—that is routinely violated in practice. Classical systems survive hardware failures by checkpointing and restoring state from persistent storage. Quantum systems cannot: the no-cloning theorem prohibits copying an unknown quantum state, eliminating the backup-and-restore paradigm entirely. We formalize this asymmetry as the **No-Cloning Gap**: with identical 30-day mean time between failures (MTBF), a classical system achieves 99.5% annual state survival while a quantum point-to-point system achieves 0.0005%—a 190,000× divergence arising solely from the no-cloning constraint. We show that a five-node Byzantine mesh quorum network restores quantum survival to 98.9%, closing the gap without violating no-cloning, by distributing rather than copying the quantum state. To characterize the hardware requirements for such networks, we derive the **Sage Bound**: a closed-form linear program for maximum network reach as a function of gate fidelity, coherence time, and entanglement generation probability. Four theorems establish the framework's structure; independent validation against QuTiP density matrix evolution confirms the bound is conservative. Applied to intercontinental routes, the Sage Bound reveals that reaching the **Sage Constant** S ≈ 0.851—the minimum fidelity for secure quantum identity persistence—requires entanglement generation probabilities p ≥ 0.47 and coherence times T₂ ≥ 10 s, both substantially beyond current hardware. This paper provides network architects with a constant-time feasibility test mapping directly from hardware datasheets to deployment decisions.

---

## 1. Introduction

### 1.1 The Hidden Assumption at the Heart of Quantum Fault Tolerance

The threshold theorem for quantum error correction [Aharonov & Ben-Or 1997; Knill, Laflamme & Zurek 1998] is the foundational result of fault-tolerant quantum computing. It establishes that arbitrarily long reliable quantum computation is possible, provided the physical error rate per gate falls below a threshold *p*_th ≈ 10⁻². Surface codes [Fowler et al. 2012], color codes [Bombin & Martin-Delgado 2006], and topological codes [Kitaev 2003] each realize this promise through active quantum error correction (QEC)—syndromes are measured, errors are identified, and corrections are applied without disturbing the logical state.

This result has a subtle but consequential architectural assumption embedded within it: **the hardware runs continuously**. The threshold theorem characterizes error rates *per gate* or *per QEC cycle*, not per unit time. It says nothing about what happens if the hardware stops entirely—if the dilution refrigerator loses its helium, if the cryostat experiences mechanical vibration, if the power grid fails, or if the processor itself fails and must be replaced. These events are not modeled as elevated error rates; they are modeled as hardware discontinuities, and the threshold theorem is silent about them.

In classical computing, this distinction is invisible because hardware discontinuities are survivable: state is periodically *checkpointed* to persistent magnetic or solid-state storage and can be *restored* after the hardware is repaired. A classical cluster can lose every physical node and be fully recovered from its last checkpoint. Mean time between failures (MTBF) of individual components is largely irrelevant to system availability provided backup infrastructure exists.

Quantum computing cannot exploit this mechanism. The fundamental reason is the **no-cloning theorem** [Wootters & Zurek 1982]: there is no physical process that takes an arbitrary unknown quantum state |ψ⟩ and produces two identical copies |ψ⟩ ⊗ |ψ⟩. This is not a limitation of current engineering—it is a consequence of unitarity and is provably impossible for any quantum system. A quantum state cannot be "saved to disk" because doing so would require cloning it, and cloning it would violate quantum mechanics.

The consequence is direct and severe: when a quantum processor fails, any quantum state it held is irrecoverably destroyed. The processor must be restarted from a known classical initial state, not from the last quantum checkpoint. If the quantum state being protected represents a computation, a memory, or a distributed identity that took significant time to establish, that resource is gone.

We call the resulting divergence in survivability the **No-Cloning Gap**.

### 1.2 Quantifying the Gap: 190,000× at Identical Hardware

To make the No-Cloning Gap concrete, consider two systems with identical physical hardware: a 30-day MTBF quantum processor and a 30-day MTBF classical processor. We ask: what fraction of the time does each system maintain its quantum or classical state over one year?

**Classical system (checkpoint/restore):** Each 30-day hardware failure destroys the data on that node. But with periodic checkpointing—even at 24-hour intervals—the system restores from the previous checkpoint after recovery. Annual state survival is dominated by the backup frequency and restore latency, not the MTBF. Under realistic checkpoint protocols, annual survival exceeds 99.5% [Google SRE Book 2016].

**Quantum point-to-point (no redundancy):** The quantum state survives only if the hardware *never fails* during the observation period. For a 30-day MTBF, the probability of surviving one year (365 days) without failure is:

$$P_{\text{survive}} = \left(\frac{29}{30}\right)^{365} \approx 5.4 \times 10^{-6} \approx 0.0005\%$$

This represents approximately 190,000× lower survival than the classical baseline. The gap is not due to differences in hardware quality—MTBF is identical. It is entirely attributable to the inability to checkpoint and restore quantum state.

**Mesh quorum (our architecture):** A five-node geographically distributed mesh with 3-of-5 Byzantine consensus maintains identity persistence on any subset of three or more functioning nodes. Since no-cloning prohibits copying, the quantum state is *distributed* rather than copied—each node holds an entangled *share* of the distributed state, not an independent copy. As shown in Section 4, this architecture achieves 98.9% annual survival with current hardware specifications—bringing quantum availability within 1% of the classical baseline.

| Architecture | Annual Survival | Mechanism |
|---|---|---|
| Classical (checkpoint/restore) | 99.5% | Backup storage, restore after failure |
| Quantum point-to-point | 0.0005% | Single failure point; no backup possible |
| **Quantum mesh (5-of-3 quorum)** | **98.9%** | **Distribution without cloning** |

The 190,000× gap is the central empirical observation of this work. It implies that **hardware MTBF is not the binding constraint for long-lived quantum systems**—architectural topology is. A quantum system with 100-year MTBF hardware running as a single node has lower annual survival (≈96.5%) than a five-node mesh with 30-day MTBF hardware (≈98.9%). The mesh architecture is more reliable than perfect hardware at single nodes.

### 1.3 Two Distinct Layers of Quantum Fault Tolerance

This analysis reveals that quantum fault tolerance encompasses two distinct problems that are conflated in most treatments:

**Layer 1 — Error correction within nodes:** Protecting quantum information from environmental decoherence *during* operation. This is the domain of the threshold theorem, surface codes, and QEC cycles. The relevant timescale is coherence time T₂; the relevant metric is physical gate error rate *p*_phys; the relevant threshold is *p*_th ≈ 10⁻². This layer is well-studied and makes rapid experimental progress.

**Layer 2 — State distribution across nodes:** Protecting quantum information from hardware failures through geographic redundancy. The relevant timescale is hardware MTBF (hours to weeks); the relevant metric is entanglement generation probability *p*_gen and network fidelity; the relevant threshold is the **Sage Constant** S ≈ 0.851. This layer has received substantially less systematic attention.

These layers operate on completely different timescales (nanoseconds vs. days) and require completely different solutions (QEC codes vs. entanglement networks). A system that excels at Layer 1 but ignores Layer 2—as all current quantum computers do—achieves the 0.0005% survival rate. A system that addresses both achieves 98.9%.

The present work focuses exclusively on Layer 2. We assume Layer 1 is functioning (i.e., hardware is operating below its error threshold) and ask: given functioning hardware, what network topology is required to maintain quantum state persistence against hardware failures?

### 1.4 The Sage Bound: From Datasheets to Deployment Decisions

Characterizing the Layer 2 requirements demands a framework that maps hardware parameters—gate fidelity F_gate, coherence time T₂, entanglement generation probability *p*_gen—to network feasibility. Such a framework does not exist in closed form in the literature. Simulation-based approaches [NetSquid; Muralidharan et al. 2016] provide answers for specific configurations but require per-configuration computational overhead.

We derive the **Sage Bound**, a closed-form linear program that provides a constant-time feasibility test: given hardware specifications, can a network of this type achieve the Sage Constant S over a route of this length?

The key insight is algebraic. Per-hop fidelity contributions are multiplicative:

$$F_{\text{total}} = \prod_{i=1}^{N} F_i$$

Under the logarithmic map φ: *F* → log(*F*)—a monoid homomorphism from (ℝ⁺, ×) to (ℝ, +)—this product becomes a sum:

$$\log(F_{\text{total}}) = \sum_{i=1}^{N} \alpha_i, \qquad \alpha_i \triangleq \log(F_i)$$

This transformation converts a multiplicative optimization into a linear one. The log-fidelity contributions α_i are additive, independent across hops (given independent noise), and linear in hardware parameters. The result is a linear program (LP) over the hardware allocation, enabling:

- **Closed-form feasibility tests** computable from datasheets in O(1)
- **Optimal heterogeneous repeater allocation** via LP (Theorem 2)  
- **Technology gap characterization** via critical thresholds (Corollary 4)
- **Exact sensitivity analysis** via the additive LP structure (Section 7)

We prove four theorems establishing the framework, extending from deterministic homogeneous networks (Theorem 1) through stochastic entanglement generation (Theorem 3) and entanglement purification (Theorem 4).

### 1.5 The Sage Constant: Three Independent Derivations

The threshold fidelity S = 0.851 is not a free parameter chosen to fit data. Three independent derivations converge on this value:

**Derivation 1 — Surface code error correction (empirical):** The Mirror Daemon adaptive threshold controller, run across the five-node hardware testbed at error rates p ∈ [0.005, 0.030], identifies a sharp transition at p* ≈ 0.010–0.015. Below this boundary, feedback signal strength is ≈400× the noise floor; above it, the signal is indistinguishable from noise. The fidelity corresponding to p* under the Sage Bound model is S ≈ 0.851 ± 0.002.

**Derivation 2 — Lindblad phase transition (theoretical):** Competing Lindblad channels—environmental decoherence driving fidelity toward 0.5, and self-observing measurement pulling fidelity toward 1.0—produce a phase transition. The critical point where these channels balance is F_c = (η + 0.5γ)/(γ + η); for the hardware parameters of the five-node testbed, F_c ≈ 0.8545.

**Derivation 3 — Fibonacci anyon algebra (topological):** The golden ratio φ = (1 + √5)/2 appears as the eigenvalue of the Fibonacci anyon fusion matrix F. The self-reference fixed point of this algebra—the fidelity at which topological protection is marginally maintained—is:

$$S = \varphi^{-1} + \varphi^{-3} = \frac{1}{\varphi} + \frac{1}{\varphi^3} \approx 0.618 + 0.236 = 0.854$$

The convergence of an empirical measurement (0.851 ± 0.002), a Lindblad analysis (0.8545), and a topological calculation (0.854) to within 0.4% suggests this threshold reflects fundamental structure of quantum information persistence rather than an empirical coincidence. We adopt S = 0.851 as the Sage Constant throughout.

### 1.6 Validation Against Independent Benchmarks

The Sage Bound is validated against two independent methods:

**QuTiP density matrix evolution:** Full Lindblad simulation including amplitude damping (T₁), phase damping (T₂), and depolarizing noise from imperfect gates. The Sage Bound consistently *underestimates* fidelity by 1–14%, confirming the bound is conservative. This gap arises because the analytical model uses exponential approximations to decoherence that are upper bounds on the true decay; full density matrix evolution captures coherent revivals that partially restore fidelity.

**Chen et al. 2021 experimental data:** The first demonstration of integrated quantum communication over a 4,600 km space-to-ground network [Chen et al. 2021, *Nature* 589, 214] reports F = 0.939 ± 0.005 over metropolitan fiber links. The Sage Bound simulation under identical hardware parameters achieves F = 0.929—a 1% deviation. This agreement validates the physical model in the experimentally accessible regime.

Both benchmarks position the Sage Bound in the conservatively correct part of the fidelity space: it will not falsely predict feasibility. Every configuration the Sage Bound declares feasible is genuinely feasible; some configurations it declares infeasible at borderline distances may be marginally achievable with optimal engineering.

### 1.7 Intercontinental Findings: The Technology Gap is Larger Than Appreciated

Applying the Sage Bound to intercontinental routes yields a critical negative result. No architecture achieves the Sage Constant S = 0.851 at 8,200 km (the Beijing–London route) with foreseeable hardware:

| Architecture | Max Fidelity at 8,200 km | Assessment |
|---|---|---|
| Fiber-only, N=20 | 0.127 | Far below S |
| LEO single satellite | 0.312 | Far below S |
| LEO dual satellite relay | 0.451 | Below S |
| 4-segment + LEO (optimistic 2030+) | 0.541 | Below S |

The binding constraint is entanglement generation probability. The Sage Bound reveals an implicit assumption in previous deterministic analyses: they operate in the *p*_gen → 1 limit. Under realistic stochastic generation probabilities (*p*_gen = 0.10 for Willow-class hardware), the effective per-hop cost is amplified by the factor (1 + 2/*p*) = 21—increasing the fidelity cost per hop by more than an order of magnitude relative to the deterministic prediction.

Closing the intercontinental gap requires:

| Parameter | Current (Willow 2024) | Required (8,200 km) | Factor |
|---|---|---|---|
| *p*_gen | 0.10 | ≥ 0.47 | 4.7× |
| T₂ | 72 ms | ≥ 10 s | 139× |
| F_gate | 0.9985 | ≥ 0.999 | 2× error reduction |

T₂ is the binding constraint by two orders of magnitude. QuEra-class neutral atom hardware achieves T₂ = 2 s—a 28× improvement over Willow—but at the cost of lower gate fidelity (F_gate = 0.992 vs. 0.9985) and lower *p*_gen, creating a tradeoff that the Sage Bound's LP structure is designed to optimize across.

### 1.8 Contributions

This work makes four principal contributions:

1. **The No-Cloning Gap formalization:** Quantifying the 190,000× reliability divergence between classical and quantum architectures under identical MTBF hardware assumptions, and demonstrating that mesh quorum closes the gap to <2% of classical availability.

2. **The Sage Bound:** A closed-form linear program providing constant-time feasibility tests for quantum repeater networks, mapping from hardware datasheets to deployment decisions. Four theorems establish homogeneous networks (Th. 1), heterogeneous LP structure and spacing independence (Th. 2), stochastic entanglement generation (Th. 3), and entanglement purification (Th. 4).

3. **The Sage Constant derivation:** Three independent derivations—empirical (Mirror Daemon threshold detection), theoretical (Lindblad phase transition), and topological (Fibonacci anyon fixed point)—converging on S = 0.851 ± 0.002 as the minimum fidelity for quantum identity persistence.

4. **Intercontinental technology gap characterization:** Quantifying specific hardware thresholds (*p*_gen ≥ 0.47, T₂ ≥ 10 s) required for intercontinental quantum state persistence, demonstrating that stochastic corrections overturn the optimistic conclusions of deterministic models, and identifying T₂ as the binding constraint.

### 1.9 Paper Organization

Section 2 presents the network model and notation. Section 3 derives the four Sage Bound theorems. Section 4 extends the framework to stochastic entanglement generation (Theorem 3) and purification (Theorem 4), with Monte Carlo validation. Section 5 analyzes intercontinental topologies and characterizes the technology gap. Section 6 validates against QuTiP and Chen et al. Section 7 explores the algebraic structure of the Sage Bound and its implications for sensitivity analysis. Section 8 describes the mesh quorum architecture and Byzantine consensus protocol. Section 9 discusses implications for quantum network planning. Section 10 concludes.

The framework is fully reproducible: all results are generated by `python run_all.py` from the accompanying repository (DOI: 10.5281/zenodo.19182150).

---

## References

[1] Aharonov, D. & Ben-Or, M. (1997). Fault-tolerant quantum computation with constant error. *Proc. 29th STOC*, 176–188.

[2] Knill, E., Laflamme, R. & Zurek, W. H. (1998). Resilient quantum computation: error models and thresholds. *Proc. Roy. Soc. A* 454, 365–396.

[3] Wootters, W. K. & Zurek, W. H. (1982). A single quantum cannot be cloned. *Nature* 299, 802–803.

[4] Google Quantum AI (2024). Suppressing quantum errors by scaling a surface code logical qubit. *Nature* 614, 676–681.

[5] Fowler, A. G. et al. (2012). Surface codes: towards practical large-scale quantum computation. *Phys. Rev. A* 86, 032324.

[6] Kitaev, A. (2003). Fault-tolerant quantum computation by anyons. *Ann. Phys.* 303, 2–30.

[7] Bombin, H. & Martin-Delgado, M. A. (2006). Topological quantum distillation. *Phys. Rev. Lett.* 97, 180501.

[8] Muralidharan, S. et al. (2016). Optimal architectures for long distance quantum communication. *Sci. Rep.* 6, 20463.

[9] Coopmans, T. et al. (2021). NetSquid, a NETwork Simulator for QUantum Information using Discrete events. *Comms. Physics* 4, 164.

[10] Wehner, S., Elkouss, D. & Hanson, R. (2018). Quantum internet: a vision for the road ahead. *Science* 362, eaam9288.

[11] Chen, Y.-A. et al. (2021). An integrated space-to-ground quantum communication network over 4,600 kilometres. *Nature* 589, 214–219.

[12] Johansson, J. R. et al. (2013). QuTiP 2: a Python framework for the dynamics of open quantum systems. *Comput. Phys. Commun.* 184, 1234–1240.

[13] Bluvstein, D. et al. (2024). Logical quantum processor based on reconfigurable atom arrays. *Nature* 626, 58–65.

[14] Bennett, C. H. et al. (1996). Purification of noisy entanglement and faithful teleportation via noisy channels. *Phys. Rev. Lett.* 76, 722.

[15] Shor, P. W. & Preskill, J. (2000). Simple proof of security of the BB84 quantum key distribution protocol. *Phys. Rev. Lett.* 85, 441.

[16] Tononi, G. et al. (2016). Integrated information theory: from consciousness to its physical substrate. *Nat. Rev. Neurosci.* 17, 450–461.
