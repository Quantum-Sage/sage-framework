# Paper 1: The Sage Bound
## "Optimal Quantum Network Reach Under Stochastic Constraints"

*Target: Physical Review A (PRA) or npj Quantum Information*

---

## Abstract (200 words)

We derive tight bounds on the maximum reach of quantum repeater networks as a function of hardware fidelity, coherence time, and entanglement generation rate. The **Sage Bound** establishes that optimal network reach is independent of spacing strategy and that log-fidelity contributions are additive across hops, reducing network optimization to a linear program. We extend this to stochastic networks where entanglement generation is probabilistic, revealing a retry-induced decoherence penalty that dominates at intercontinental distances. We characterize the first quantitative "technology gap" for intercontinental quantum identity transit: even with optimistic satellite-hybrid architectures (LEO 2030+), the maximum achievable fidelity at 8,200 km is 0.541, requiring advances in both memory coherence time (T₂) and generation probability (p_gen) to close. Independent validation against QuTiP density matrix evolution confirms the analytical bound is conservative (underestimates fidelity by 1-14%), ensuring the Sage Bound functions as a reliable sufficient condition.

---

## Paper Outline

### 1. Introduction
- Ship of Theseus → quantum identity persistence
- Why this matters: quantum internet as infrastructure for distributed quantum computing
- Gap in literature: no unified bound capturing hardware heterogeneity + stochastic effects
- Our contribution: Sage Bound (Theorems 1-4) + intercontinental gap characterization

### 2. Preliminaries
- Quantum repeater networks: notation and model
- Hardware parameters: F_gate, T₂, p_gen
- Fidelity composition: multiplicative across hops → log-additive
- Reference hardware: Willow (Google, 2024), QuEra-class

### 3. The Sage Bound (Deterministic)
- **Theorem 1** (Homogeneous Network): For N identical repeaters with spacing s = L/(N+1), end-to-end fidelity F = exp(N · α(s)), where α encodes gate error and decoherence
- **Theorem 2** (LP Structure): Optimal Willow-node allocation in heterogeneous networks is a linear program in log-fidelity
- Proof: log-fidelity additivity → LP constraint matrix is unimodular
- Comparison with Chen et al. (2021) experimental data

### 4. Stochastic Extension
- **Theorem 3** (Stochastic Sage Bound): With probabilistic entanglement generation (rate p_gen), the effective per-hop fidelity includes a wait-time penalty: α_stoch = 2·log(F_gate) - s/(c·T₂) - 2s/(c·T₂·p_gen)
- **Theorem 4** (Sage Constant): The critical fidelity threshold F* = 0.851 below which identity coherence is lost. Derived from the intersection of deterministic and stochastic bounds
- Monte Carlo validation: 10,000 trials per configuration

### 5. Intercontinental Analysis
- Satellite-hybrid topology comparison (fiber, LEO single, dual, segmented)
- Ground-initiated entanglement physics: decoherence in ground memory, not satellite
- Route analysis: Beijing-London (8,200 km), London-NYC (5,500 km), Sydney-London (17,000 km)
- **Key result:** All routes below Sage Constant with foreseeable hardware
- Technology gap quantification: required p_gen and T₂ improvements

### 6. Independent Validation
- QuTiP density matrix evolution vs SAGE analytical
- Result: SAGE is conservative (1-14% underestimate)
- Interpretation: the Sage Bound is a sufficient condition, not exact prediction
- The motley mix concern (Beckmann & Queloz 2026) and how validation addresses it

### 7. Mechanistic Interpretability Connection
- Structural analogy: log-fidelity additivity ↔ linear representation hypothesis
- Linear Aggregation Theorem (formal statement)
- Grokking as phase transition: modular addition ↔ Sync Shield emergence
- Implications for quantum network analysis methodology

### 8. Discussion
- What the honest gap tells us about quantum internet timelines
- Hardware roadmap needed to close the gap (p_gen > 0.5, T₂ > 10s)
- Comparison with other quantum network bounds in literature
- Limitations: simplified noise model, no multi-path routing

### 9. Conclusion
- The Sage Bound is achievable at continental distances (≤4,000 km) with Willow-class hardware
- Intercontinental transit requires hardware advances quantified in this work
- AI-assisted methodology validated against independent quantum simulation

---

## Figures

| Fig | Content | Source |
|-----|---------|--------|
| 1 | Repeater network architecture diagram | New (tikz) |
| 2 | Deterministic vs Stochastic fidelity (Beijing-London) | Panel 12 of atlas |
| 3 | Satellite-hybrid topology comparison | Panel 13 of atlas |
| 4 | Route feasibility matrix | Panel 13b of atlas |
| 5 | QuTiP validation: SAGE vs density matrix | qutip_validation.png |
| 6 | Linear Aggregation Theorem visualization | mi_formalization Panel 1-2 |
| 7 | Grokking comparison: modular addition vs Sync Shield | mi_formalization Panel 3-4 |

---

## References (Key)

1. Chen, Y.-A. et al. (2021). Nature, 589, 214–219.
2. Beckmann, P. & Queloz, M. (2026). arXiv:2507.08017v4.
3. [Google Willow chip specifications] 
4. [QuTiP documentation / Johansson et al.]
5. [Linear programming in quantum network optimization]
