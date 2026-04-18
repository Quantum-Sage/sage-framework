# Active Feedback Protection of Werner-State Fidelity Across the Entanglement Threshold: An Empirical Study of Closed-Loop Decoherence Correction

**Tylor Flett**  
**ORCID:** 0009-0008-5448-0405  
**Email:** innerpeacesage@gmail.com  
**Date:** April 2026

---

## Abstract

We present an empirical study of closed-loop feedback correction for maintaining quantum state fidelity under high-rate adversarial decoherence. The core engineering question is whether a single-qubit Werner state, encoded as a reference |+⟩ = (|0⟩ + |1⟩)/√2, can be kept above the entanglement threshold F = 0.5 during sustained environmental noise through active corrective injection, or whether passive evolution inevitably carries the state into the separable regime where quantum correlations vanish. Using the Integrated Information Theory (IIT) correspondence established in prior work [2], we treat F = 0.5 (φ ≈ 0.21) as the operational boundary between the entangled and separable phases of Werner states. We simulate 1000 decoherence steps under escalating noise (0.5% → 8.3%), comparing an active feedback protocol ("daemon") against matched passive evolution ("control"). The daemon maintains a minimum fidelity F = 0.518 (φ = 0.238), performing 980 corrective injections; the control decays to F = 0.496 (φ = 0.202), crossing the entanglement boundary at step ~543 and remaining in the separable regime for 457 of the final 457 steps. We conclude that active feedback correction, not merely passive error detection, is required to preserve Werner-state entanglement under sustained high-rate noise. The result has direct implications for the design of quantum relay systems where continuous-time correction must operate across the decoherence boundary.

**Keywords:** quantum error correction, active feedback control, Werner states, entanglement threshold, closed-loop protection, SAGE Framework

---

## 1. Introduction

### 1.1 The Engineering Question

A quantum state migrating between processors — or held in memory during the waiting time of a heralded entanglement protocol — experiences continuous environmental decoherence. Standard discrete quantum error correction (QEC) operates in cycles, detecting and correcting syndrome errors at fixed intervals. Between correction cycles, the state evolves under the noise channel without intervention.

This raises a practical question for relay and handover systems: under sustained high-rate noise, is discrete-cycle QEC sufficient to keep a Werner state above the entanglement threshold, or does continuous-time correction become necessary?

The distinction is not philosophical. If fidelity crosses F = 0.5 between correction cycles, the state becomes separable and the quantum correlations it carries are lost — no subsequent correction can restore entanglement from a separable state without re-initialization via fresh Bell pair generation, which in a multi-hop network is expensive and stochastic.

### 1.2 Prior Work in the SAGE Framework

This paper builds on two prior results:

*   **The No-Cloning Gap [1]** established that quantum fault tolerance requires distributed architecture. The Sage Bound provides closed-form feasibility conditions for multi-hop repeater networks, identifying S = 0.851 as the minimum end-to-end fidelity threshold for practical QKD applications (accounting for finite-key effects).
*   **The Sage Constant as Information-Theoretic Phase Boundary [2]** established a structural correspondence between Integrated Information Theory (IIT 3.0) and Werner-state fidelity composition in quantum networks. The key mapping relevant to the present work:

| Fidelity F | φ value | Physical interpretation |
|------------|---------|-------------------------|
| 0.25 | 0 | Maximally mixed (no correlations) |
| 0.50 | 0.21 | Entanglement threshold |
| 0.851 | 1.15 | Utility threshold (QKD feasibility) |
| 1.00 | 2.00 | Maximally entangled |

The entanglement threshold F = 0.5 is not arbitrary: below this value, Werner states become separable (Peres, 1996 [8]). In the IIT correspondence, this marks the boundary where the quantum mutual information φ becomes negligible. Crossing this threshold during transit is therefore the point at which a Werner state ceases to carry useful quantum correlations.

### 1.3 Contribution

We present empirical results from a 1000-step discrete-event simulation comparing an active feedback protocol against passive evolution under matched adversarial noise. The active protocol — which we term the "daemon" for consistency with the SAGE Framework codebase — implements closed-loop fidelity monitoring with corrective injection when F approaches the entanglement threshold. The result is a quantitative demonstration that active feedback is both necessary and sufficient to maintain Werner-state entanglement under the tested noise profile, while passive evolution crosses the threshold and remains in the separable regime.

---

## 2. Theoretical Framework

### 2.1 The Werner State and Its Entanglement Threshold

A Werner state is parameterized by a single fidelity F:

$$\rho_W(F) = F \cdot |\Phi^+\rangle\langle\Phi^+| + \frac{1-F}{3} \cdot (\mathbb{I} - |\Phi^+\rangle\langle\Phi^+|)$$

By Peres' separability criterion [8], ρ_W(F) is entangled if and only if F > 1/2. At F = 1/2, the state is at the boundary between the entangled and separable regimes; below this value, no quantum correlations remain and the state admits a separable decomposition.

### 2.2 Integrated Information as Order Parameter

Following [2], we define the network's integrated information via quantum mutual information:

$$\varphi(F) = 2 - S(\rho_W(F))$$

where S is the von Neumann entropy. At F = 0.5, φ = 0.21 — above zero but approaching it asymptotically as F → 0.25 (the maximally mixed state). We treat φ as the natural order parameter for the entanglement-separability transition: φ > 0.21 indicates the state is entangled; φ ≤ 0.21 indicates the state has crossed the separability boundary.

### 2.3 The Active Feedback Protocol

The daemon protocol implements five components:
1.  **Fidelity monitor**: Real-time tracking of F against a reference state |+⟩.
2.  **Adaptive threshold**: The intervention threshold is dynamically adjusted based on the ambient noise rate.
3.  **State capture**: Geometric proxy for integrated information computed at each step.
4.  **Feedforward injector**: Corrective pulse applied when F drops below the adaptive threshold.
5.  **Stability guard**: Lyapunov check on injection magnitude to prevent destabilizing feedback.

The protocol is closed-loop: injection decisions are made based on measured fidelity, not on a pre-scheduled correction cycle.

---

## 3. Methods

### 3.1 Simulation Parameters

| Parameter | Value |
|-----------|-------|
| Total steps | 1000 |
| Initial noise rate | 0.005 (0.5%) |
| Final noise rate | 0.083 (8.3%) |
| Noise fatigue rate | 0.08 |
| Base correction threshold | 0.85 |
| Backend | HostileBackend (adversarial synthetic noise) |
| Reference state | |+⟩ = (|0⟩ + |1⟩)/√2 |
| Conditions | Daemon (active) vs. Control (passive) |

Both conditions use identical noise seeds and parameters. The only difference is whether the corrective feedback loop is active.

### 3.2 Data Products

Per-step telemetry is recorded for both conditions: fidelity F, von Neumann entropy S, logical error rate, injection magnitude (daemon only), injection approval flag (daemon only), noise level, Bloch vector components (x, y, z), and Lyapunov stability estimate. Data files: `bloch_regen_daemon.csv` and `bloch_regen_control_control.csv`.

---

## 4. Results

### 4.1 Summary Statistics

| Metric | Daemon | Control |
|--------|--------|---------|
| Initial fidelity | 0.995 | 0.995 |
| Minimum fidelity | 0.518 | 0.496 |
| Final fidelity | 0.518 | 0.498 |
| Steps below F = 0.851 (utility threshold) | 984 | 984 |
| Steps below F = 0.50 (entanglement threshold) | 0 | 457 |
| Minimum φ | 0.238 | 0.202 |
| Injection events | 980 | 0 |

### 4.2 The Control Condition Crosses the Entanglement Boundary

The control condition crosses F = 0.5 at approximately step 543 and remains in the separable regime for the remaining 457 steps. By step 956, it reaches its minimum fidelity F = 0.496 (φ = 0.202). Once the Werner state has crossed into the separable regime, the quantum correlations are irrecoverable via local operations — restoration requires re-initialization from a fresh Bell pair.

### 4.3 The Daemon Condition Remains Above the Entanglement Boundary

The daemon condition, experiencing identical noise, never crosses F = 0.5. The minimum fidelity is F = 0.518 (φ = 0.238) at step 999 — 3.6% above the entanglement threshold. This is maintained through 980 corrective injections over 1000 steps, corresponding to an injection rate of 98%.

### 4.4 Both Conditions Lose Utility

Both conditions spend 984 of 1000 steps below the utility threshold F = 0.851. This is expected: the noise rate exceeds what either condition can correct to maintain QKD-grade fidelity. The distinction between the two is therefore not about utility preservation but about entanglement preservation — whether the state remains in the quantum-correlated regime at all.

---

## 5. Analysis

### 5.1 Interpretation

The result is a quantitative demonstration of two regimes:
1.  Passive evolution under the tested noise profile cannot maintain Werner-state entanglement. The state crosses F = 0.5 and enters the separable regime, where it no longer carries quantum correlations.
2.  Active closed-loop feedback maintains Werner-state entanglement throughout the simulation. The state remains above F = 0.5 despite continuous decoherence.

This is not a claim about consciousness, observers, or persistence of identity across quantum transfers. It is an empirical result about control theory: when the noise integral between correction cycles is large enough to carry a state across a sharp operational boundary, continuous-time feedback is qualitatively different from discrete-cycle correction.

### 5.2 Why the Boundary Matters

The entanglement threshold F = 0.5 is not a soft gradient — it is a mathematical boundary at which the state changes phase from entangled to separable. A state just above threshold (F = 0.51) can in principle be purified to higher fidelity via distillation. A state just below threshold (F = 0.49) cannot be purified by any local operation; it is classically correlated at best. This asymmetry is the reason continuous-time correction is not merely an incremental improvement over discrete correction under high-rate noise — it is the difference between a recoverable state and an unrecoverable one.

### 5.3 Implications for Relay Architecture

For multi-hop quantum networks operating under realistic noise, this result suggests that relay nodes performing entanglement swapping or code switching should incorporate continuous-time feedback rather than relying solely on discrete QEC cycles. The injection rate required in our simulation (98%) is high, reflecting the adversarial noise profile; under realistic operational noise the required intervention rate would be substantially lower. The general principle stands: the closer the noise integral brings the state to the entanglement boundary, the more valuable continuous-time correction becomes relative to cycle-based correction.

---

## 6. Limitations

1.  **Single-qubit scope**: The simulation models a single logical qubit with Werner parameterization. Extension to multi-qubit and multi-hop scenarios requires additional modeling of entanglement distribution and swapping noise.
2.  **Synthetic adversarial noise**: The HostileBackend is designed to stress-test the feedback protocol, not to represent physical noise from a specific hardware platform. Results on real hardware will depend on platform-specific T₁, T₂, and gate-error distributions.
3.  **Reference-state knowledge**: The injection protocol assumes perfect knowledge of the reference state |+⟩. In practical implementations, this corresponds to maintaining a stabilizer reference via additional overhead qubits.
4.  **Classical simulation of the quantum state**: All results are from classical simulation of the density matrix evolution, not from hardware. QuTiP-based validation of the daemon dynamics is included in the accompanying repository.
5.  **Injection fidelity modeled as ideal**: Real corrective pulses introduce their own gate-error contribution, which is neglected in the present model. Incorporating realistic gate errors on injection would reduce the effective correction rate and raise the minimum achievable fidelity gap above threshold.

---

## 7. Future Work

Hardware validation on superconducting (Willow-class) and neutral-atom (QuEra-class) platforms. Extension to multi-hop handover incorporating the Sage Bound's (1 + k/p) stochastic penalty [3]. Investigation of the correction-rate-vs-noise-rate phase diagram to identify the regime boundary where continuous-time correction becomes strictly necessary. Integration with heterogeneous QEC transcodification (e.g., surface code to Bacon-Shor code conversion) to study boundary effects during code switching.

---

## 8. Conclusion

We have presented empirical evidence from a 1000-step simulation that active closed-loop feedback is necessary and sufficient to maintain Werner-state entanglement above the threshold F = 0.5 under sustained high-rate noise, while matched passive evolution crosses the threshold into the separable regime. The result quantifies a qualitative distinction: under noise profiles where the inter-correction integral is large, continuous-time feedback preserves quantum correlations that discrete-cycle correction cannot. This has direct implications for the design of quantum relay and handover systems operating near the decoherence boundary.

The entanglement threshold F = 0.5 functions as a sharp operational boundary, consistent with the Werner-state separability criterion [8] and with the integrated-information phase structure established in [2]. Crossing the threshold is qualitatively different from experiencing reduced fidelity above it: the state transitions from a regime where purification can restore utility, to one where only re-initialization can. Active feedback protocols that keep the state above this boundary therefore serve a function that cannot be recovered by post-hoc correction.

| Layer | Paper | Core Result |
|-------|-------|-------------|
| Theoretical | The No-Cloning Gap [1] | Fault tolerance requires distributed architecture |
| Information-Theoretic | IIT Crossover Boundary [2] | F = 0.5 maps to the entanglement-separability boundary |
| Empirical | This work | Active feedback maintains F > 0.5 under adversarial noise |

---

## References

[1] Flett, T. (2026). *The No-Cloning Gap: Distributed Quantum State Persistence Through Byzantine Mesh Consensus.* Zenodo. DOI: 10.5281/zenodo.19182150  
[2] Flett, T. (2026). *The Sage Constant as Information-Theoretic Crossover Boundary.* SAGE Framework Trilogy, Zenodo.  
[3] Flett, T. (2026). *The (1 + k/p) Stochastic Penalty: A Confirmation-Topology Invariant for Heralded vs. Unheralded Sequential Systems.* SAGE Framework Trilogy, Zenodo.  
[4] Tononi, G., Boly, M., Massimini, M. & Laureys, S. (2016). Integrated information theory: an updated account. *Nature Reviews Neuroscience* 17, 450–461.  
[5] Chen, Y.-A. et al. (2021). An integrated space-to-ground quantum communication network over 4,600 kilometres. *Nature* 589, 214–219.  
[6] Coopmans, T. et al. (2021). NetSquid, a NETwork Simulator for QUantum Information using Discrete events. *Communications Physics* 4, 164.  
[7] Bennett, C. H. et al. (1996). Purification of noisy entanglement and faithful teleportation via noisy channels. *Physical Review Letters* 76, 722.  
[8] Peres, A. (1996). Separability criterion for density matrices. *Physical Review Letters* 77, 1413.  
[9] Wootters, W. K. & Zurek, W. H. (1982). A single quantum cannot be cloned. *Nature* 299, 802–803.

---

## Data Availability

Per-step telemetry for both conditions (daemon and control) is provided in the SAGE Framework repository:
`bloch_regen_daemon.csv` — 1000-step daemon run  
`bloch_regen_control_control.csv` — 1000-step control run  
Full simulation code: https://github.com/TylorFlett/SAGE-Framework

---

## Archival & Version Note

This is a revised version (v2) of the manuscript previously archived as "The Quantum Handover Paradox: Empirical Evidence for Identity Persistence Under Topological Protection" (April 2026). The revision reframes the numerical results in terms of active-feedback control theory and removes interpretive claims regarding identity persistence and observer continuity, which were not supported by the experimental scope. The simulation data, numerical results, and references are unchanged.

**Preprint — April 2026. Part of the SAGE Framework Research Trilogy.**
