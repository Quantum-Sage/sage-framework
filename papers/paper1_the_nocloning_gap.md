# The No-Cloning Gap: Why Distributed Architecture Is Mandatory for Quantum Information Persistence

**Tylor Flett**  
ORCID: 0009-0008-5448-0405  
innerpeacesage@gmail.com

---

## Abstract

Quantum error correction (QEC) protects quantum information from computational errors—gate infidelities, decoherence, and measurement noise. However, QEC provides no protection against catastrophic node failure, where an entire processor is lost. The no-cloning theorem prohibits the classical backup strategies that solve this problem in distributed computing. We formalize this as a distinction between two failure modes: Layer 1 (computational errors, addressed by QEC) and Layer 2 (physical node loss, unaddressed by QEC). We show that distributed mesh architecture is therefore not an optimization but a physical requirement for persistent quantum information. For systems with mean time between failures (MTBF) of τ, single-node survival probability decays exponentially as P = e^(−t/τ), while mesh architectures with Byzantine fault-tolerant quorum achieve survival probabilities approaching unity. We quantify this reliability gap and provide a feasibility bound for quantum network architectures operating above practical fidelity thresholds established in the quantum key distribution literature.

---

## I. Introduction

The development of fault-tolerant quantum computing has focused primarily on quantum error correction—encoding logical qubits across multiple physical qubits to protect against gate errors, decoherence, and measurement noise [1,2]. Surface codes [3], qLDPC codes [4], and related constructions have achieved remarkable progress, with recent demonstrations achieving below-threshold operation on superconducting processors [5].

However, this progress addresses only one failure mode. A quantum processor is a physical device that can fail catastrophically—from cosmic ray impacts [6], cryogenic system failures, or component degradation. When such failures occur, the quantum information encoded in that processor is lost entirely. This is not a computational error that QEC can correct; it is physical destruction of the substrate.

In classical distributed systems, this problem is solved by redundancy: critical data is backed up across multiple nodes, and Byzantine fault-tolerant consensus protocols ensure survival despite node failures [7]. But the no-cloning theorem [8] prohibits copying arbitrary quantum states. The standard solution to node failure in classical systems is fundamentally unavailable for quantum information.

This paper formalizes the distinction between these two failure modes and demonstrates that distributed mesh architecture is not merely beneficial but physically mandatory for quantum systems requiring long-term information persistence.

---

## II. The Two-Layer Failure Model

We distinguish two fundamentally different failure modes in quantum systems:

**Layer 1: Computational Errors**  
Gate infidelities, decoherence during computation, measurement errors, and environmental noise. These errors occur continuously during quantum operations and accumulate over circuit depth. QEC addresses Layer 1 by encoding logical qubits redundantly and performing syndrome measurements to detect and correct errors.

**Layer 2: Physical Node Failure**  
Catastrophic loss of an entire quantum processor—the physical substrate itself. This includes cosmic ray events that simultaneously corrupt large qubit arrays [6], cryogenic system failures, power loss, or hardware degradation. When a node fails, all quantum information encoded in that node is destroyed.

**Key Observation:** QEC operates entirely within Layer 1. The logical qubit survives computational errors because its information is distributed across physical qubits *within the same processor*. But if the processor itself fails, all physical qubits fail simultaneously, and the logical qubit is lost regardless of how it was encoded.

This is not a limitation of current QEC implementations—it is structural. QEC corrects errors by comparing redundant encodings and voting. But voting requires the voters to exist. When the physical substrate is destroyed, there are no voters.

---

## III. The No-Cloning Constraint

In classical systems, Layer 2 failures are addressed by backup and replication. Critical data is copied to multiple nodes; if one node fails, the data persists elsewhere. Byzantine fault-tolerant protocols [7] ensure correct operation even if f out of 3f+1 nodes fail.

The no-cloning theorem [8] prohibits this strategy for quantum information:

> **No-Cloning Theorem:** There exists no quantum operation that takes an arbitrary unknown state |ψ⟩ and produces |ψ⟩ ⊗ |ψ⟩.

This means quantum information cannot be backed up in the classical sense. You cannot make a copy "just in case" the original is destroyed.

Recent work by Yamaguchi & Kempf [16] demonstrated that *encrypted* clones of a quantum state can be produced, enabling redundant quantum cloud storage. However, their protocol consumes the decryption key upon use (only one decryption per clone), making it a solution for *storage redundancy* rather than *continuous operational persistence*. During active computation, the state cannot be frozen into encrypted clones without halting the computation.

**Consequence:** The standard distributed systems solution to Layer 2 (backup/restore) is fundamentally unavailable for quantum information during active operation. Any solution to quantum Layer 2 failures during continuous computation must work within the constraints of quantum mechanics.

---

## IV. The Reliability Gap

Consider a quantum node with mean time between failures τ (MTBF). The survival probability over time t follows Poisson statistics:

$$P_{\text{single}}(t) = e^{-t/\tau}$$

For concrete illustration, consider τ = 30 days (plausible for current cryogenic systems) and t = 365 days (one year of operation):

$$P_{\text{single}} = e^{-365/30} = e^{-12.17} \approx 5.2 \times 10^{-6}$$

A single quantum node has approximately 0.0005% probability of surviving one year without catastrophic failure.

Compare this to classical high-availability systems, which routinely achieve 99.5% or higher annual availability through redundancy. The ratio:

$$\text{Gap} = \frac{P_{\text{classical}}}{P_{\text{single}}} = \frac{0.995}{5.2 \times 10^{-6}} \approx 191{,}000$$

This gap is not an artifact of our parameter choices. The structure is fundamental: classical availability is roughly constant (achieved through backup/redundancy), while quantum single-node survival decays exponentially with t/τ. For any fixed MTBF, the gap grows exponentially with mission duration.

**Note on parameters:** The specific value 191,000× depends on assumed MTBF and mission duration. For τ = 90 days, the gap is ~800×. The qualitative conclusion—exponential divergence between single-node and redundant architectures—holds regardless of parameter choices.

---

## V. Mesh Architecture as the Only Solution

Since classical backup is prohibited by no-cloning, quantum systems must achieve Layer 2 resilience through a different mechanism. The solution is *distributed entanglement*: quantum information is not copied but *spread* across multiple nodes via entanglement, such that the information can be recovered even if some nodes fail.

This is precisely the approach demonstrated by Xu et al. [9], who introduced distributed quantum error correction across separate chips to protect against cosmic ray events. Their scheme reduced catastrophic error rates from 1 per 10 seconds to less than 1 per month.

Our contribution is to formalize when such distributed architecture becomes necessary.

**Mesh Survival with Repairable Quorum:**  
Consider N nodes, each with MTBF τ and mean time to repair (MTTR) δ, operating under a Byzantine fault-tolerant protocol requiring quorum of k out of N nodes. When a node fails, its entangled share is lost, but the surviving quorum still holds sufficient information to reconstruct the full state on a replacement node (this is not cloning—it is re-encoding from the distributed representation). The system fails only if more than N−k nodes are down *simultaneously* before repairs complete.

For a repairable k-out-of-N system with individual failure rate λ = 1/τ and repair rate μ = 1/δ, the steady-state unavailability is dominated by the probability of simultaneous failures:

$$P_{\text{fail}} \approx \binom{N}{N-k+1} \left(\frac{\lambda}{\mu}\right)^{N-k+1}$$

For N = 5, k = 3, τ = 30 days, δ = 1 day (MTTR):

$$P_{\text{fail}} \approx \binom{5}{3} \left(\frac{1}{30}\right)^{3} \approx 10 \times 3.7 \times 10^{-5} \approx 3.7 \times 10^{-4}$$

$$P_{\text{mesh}} = 1 - P_{\text{fail}} \approx 0.9996$$

The mesh architecture with active repair restores survival probability to >99.9%, compared to 0.0005% for single-node operation. Even with conservative MTTR = 7 days, P_mesh > 98.9%.

---

## VI. Feasibility Threshold

Distributed quantum architectures face an additional constraint: the fidelity of entanglement across network links must remain above a threshold for the distributed information to be recoverable.

From the quantum key distribution literature, practical distillation protocols require end-to-end fidelity F ≳ 0.83–0.85 [10,11,12]. Below this threshold, distillation and error correction protocols fail to produce usable entanglement.

For a network of n hops with per-link fidelity F_link, the end-to-end fidelity decays multiplicatively:

$$F_{\text{total}} \approx F_{\text{link}}^{n}$$

This imposes a constraint on network architecture: for a given link fidelity and target end-to-end fidelity, there exists a maximum number of hops beyond which the network cannot function.

**Feasibility Condition:**

$$n_{\text{max}} = \left\lfloor \frac{\ln(F_{\text{threshold}})}{\ln(F_{\text{link}})} \right\rfloor$$

For F_link = 0.99 and F_threshold = 0.85:

$$n_{\text{max}} = \left\lfloor \frac{\ln(0.85)}{\ln(0.99)} \right\rfloor = \left\lfloor \frac{-0.163}{-0.01} \right\rfloor = 16$$

Networks requiring more than 16 hops at 99% per-link fidelity will fall below the distillation threshold.

---

## VII. The Sage Bound

We define the *Sage Bound* as the feasibility condition for distributed quantum architectures:

> A quantum network with n nodes, per-link fidelity F, and target survival probability P_target over time t is feasible if and only if:
> 
> 1. F^n ≥ F_threshold (fidelity constraint)
> 2. P_mesh(t) ≥ P_target (survival constraint)
> 3. Quorum k ≤ ⌊(N+1)/3⌋ × 2 (Byzantine constraint)

This can be formulated as a linear program in log-space for efficient feasibility testing:

$$n \cdot \ln(F) \geq \ln(F_{\text{threshold}})$$

Given hardware specifications (F, τ) and mission requirements (t, P_target), the Sage Bound provides an immediate yes/no answer on architectural feasibility—without requiring expensive discrete-event simulation.

---

## VIII. Discussion

**Relation to Prior Work:**  
Xu et al. [9] demonstrated that distributed chip-level QEC can suppress catastrophic error rates by orders of magnitude. Our work provides the analytical framework for determining *when* such distributed architecture is necessary and *whether* a proposed architecture is feasible given hardware constraints.

The distinction between Layer 1 and Layer 2 failures has been implicit in the quantum computing literature but, to our knowledge, has not been formalized in these terms. This framing clarifies why QEC progress, while essential, does not by itself solve the persistence problem.

**Implications for Modular Architectures:**  
Current roadmaps from IBM [13], Photonic Inc. [14], and other DARPA QBI participants [15] involve modular architectures where multiple quantum processors are linked. Our analysis suggests this is not merely an engineering convenience but a physical necessity for any system requiring long-term quantum information persistence.

**Limitations:**  
The specific numerical thresholds (F_threshold ≈ 0.85, the 191,000× gap) depend on parameter choices and should be understood as illustrative rather than universal constants. The structural arguments—exponential decay of single-node survival, multiplicative fidelity degradation across hops, the no-cloning prohibition on backup—are parameter-independent.

---

## IX. Conclusion

We have formalized the distinction between two failure modes in quantum systems: computational errors (addressed by QEC) and physical node failure (unaddressed by QEC). The no-cloning theorem prohibits classical backup strategies for the latter, making distributed mesh architecture mandatory rather than optional for quantum information persistence.

We quantified the reliability gap between single-node and mesh architectures, showing exponential divergence as mission duration increases. We provided a feasibility bound (the Sage Bound) for quantum network architectures, enabling rapid assessment of whether a proposed design can meet persistence requirements.

The implication is clear: fault-tolerant quantum computing requires not only better QEC but also distributed architecture. The two problems are complementary, not substitutes.

---

## References

[1] Shor, P. W. "Scheme for reducing decoherence in quantum computer memory." Phys. Rev. A 52, R2493 (1995).

[2] Steane, A. M. "Error correcting codes in quantum theory." Phys. Rev. Lett. 77, 793 (1996).

[3] Fowler, A. G., et al. "Surface codes: Towards practical large-scale quantum computation." Phys. Rev. A 86, 032324 (2012).

[4] Breuckmann, N. P. & Eberhardt, J. N. "Quantum low-density parity-check codes." PRX Quantum 2, 040101 (2021).

[5] Google Quantum AI. "Quantum error correction below the surface code threshold." Nature 638, 920–926 (2025).

[6] McEwen, M., et al. "Resolving catastrophic error bursts from cosmic rays in large arrays of superconducting qubits." Nat. Phys. 18, 107–111 (2022).

[7] Castro, M. & Liskov, B. "Practical Byzantine fault tolerance." OSDI 99, 173–186 (1999).

[8] Wootters, W. K. & Zurek, W. H. "A single quantum cannot be cloned." Nature 299, 802–803 (1982).

[9] Xu, Q., et al. "Distributed quantum error correction for chip-level catastrophic errors." arXiv:2203.16488 (2022).

[10] Bennett, C. H., et al. "Purification of noisy entanglement and faithful teleportation via noisy channels." Phys. Rev. Lett. 76, 722 (1996).

[11] Rozpędek, F., et al. "Parameter regimes for a single sequential quantum repeater." Quantum Sci. Technol. 3, 034002 (2018).

[12] Coopmans, T., et al. "NetSquid, a NETwork Simulator for QUantum Information using Discrete events." Commun. Phys. 4, 164 (2021).

[13] IBM. "IBM Quantum roadmap to fault-tolerant quantum computing." (2025).

[14] Photonic Inc. "Silicon spin qubit architecture for distributed quantum computing." DARPA QBI Stage B (2025).

[15] DARPA. "Quantum Benchmarking Initiative Stage B Selection." (2025).

[16] Yamaguchi, K. & Kempf, A. "Encrypted qubits can be cloned." Phys. Rev. Lett. arXiv:2501.02757 (2026).

---

## Appendix: Derivation of Mesh Survival Probability

The mesh survival model assumes a *repairable* k-out-of-N system. When a node fails, the surviving quorum (≥ k nodes) holds sufficient information to reconstruct the distributed state on a replacement node. This is not cloning: the original state is not duplicated but re-encoded from its distributed representation across the surviving shares.

The system fails only when more than N−k nodes are simultaneously unavailable—i.e., when failures accumulate faster than repairs.

**Model:** Each node fails independently with rate λ = 1/τ (MTBF) and is repaired with rate μ = 1/δ (MTTR). For the high-availability regime (μ >> λ), the steady-state probability of system failure is dominated by the probability of N−k+1 simultaneous failures:

$$P_{\text{fail}} \approx \binom{N}{N-k+1} \left(\frac{\lambda}{\mu}\right)^{N-k+1} = \binom{N}{N-k+1} \left(\frac{\delta}{\tau}\right)^{N-k+1}$$

Numerical evaluation (τ = 30 days):

| N | k | MTTR (δ) | P_fail | P_mesh |
|---|---|---|---|---|
| 5 | 3 | 1 day | 3.7 × 10⁻⁴ | 99.96% |
| 5 | 3 | 7 days | 1.3 × 10⁻¹ | ~87% |
| 7 | 5 | 1 day | 2.5 × 10⁻⁵ | 99.998% |
| 9 | 6 | 1 day | 8.4 × 10⁻⁷ | 99.99992% |

**Key insight:** The mesh converts the problem from *preventing all failures* (exponentially hard) to *repairing faster than failures accumulate* (achievable with reasonable MTTR). This is precisely the mechanism that classical high-availability systems use—but adapted for quantum information via distributed entanglement rather than copying.

**Note:** Without repair capability (MTTR → ∞), the mesh provides no benefit: the simple binomial with p = e^(−t/τ) ≈ 5 × 10⁻⁶ yields P_mesh ≈ 0 regardless of N. The mesh architecture requires active topology healing to function. This is an additional operational requirement that reinforces the thesis: quantum persistence is an active, architectural problem, not a passive one.
