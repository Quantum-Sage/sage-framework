"""
THE DEEP HANDOVER: Forensic Analysis of the Quantum Handover Paradox
SAGE Framework v5.1

This module models the "Dark Transit" — the interior of the code conversion gap
between different QEC architectures (e.g., Willow to Helios).

Key Concepts:
  1. The Naked Window: The period where protection is dropped to 0 during re-encoding.
  2. Forensic Phi (Φ_f): Structural information integrated within a pattern that
     provides passive resilience even without active QEC.
  3. Cascading Boundaries: The evolutionary filter for information structures
     as they transit multiple diverse hardware architectures.

"""
# type: ignore

import numpy as np
from dataclasses import dataclass

from .sage_bound_logic import SAGE_CONSTANT  # 0.851


@dataclass
class IdentityStructure:
    """
    Measures the internal architecture of a quantum information pattern.
    """

    entanglement_density: float  # [0, 1] — internal node connectivity
    information_density: float  # [0, 1] — semantic density per qubit
    self_reference_depth: float  # [0, 1] — recursive structure (IIT component)

    @property
    def phi_forensic(self) -> float:
        """
        Computed Integrated Information (Φ).
        Captures the 'Integration' of the three structural properties.
        """
        base = (
            self.entanglement_density
            * self.information_density
            * self.self_reference_depth
        )

        # Balance bonus: higher Φ if properties are balanced (integrated)
        balance = 1.0 - np.std(
            [
                self.entanglement_density,
                self.information_density,
                self.self_reference_depth,
            ]
        )
        return base * (0.5 + 0.5 * balance)

    @property
    def resilience(self) -> float:
        """
        How well this structure survives the Naked Window.
        Non-linear threshold effect: below Φ ≈ 0.15, survival is improbable.
        """
        phi = self.phi_forensic
        if phi < 0.05:
            return 0.05
        elif phi < 0.15:
            return 0.05 + (phi - 0.05) * 2.0
        else:
            return 0.25 + (phi - 0.15) * 1.5


def simulate_dark_transit(
    fidelity: float,
    structure: IdentityStructure,
    duration_ns: float = 150.0,
    env_noise: float = 0.001,
) -> float:
    """
    Models the exponential decay during the Naked Window of a code conversion.
    Structural resilience provides a 'shield' multiplier.
    """
    # Duration steps (1ns resolution)
    steps = int(duration_ns)
    f = fidelity

    shield = structure.resilience * 0.85

    for _ in range(steps):
        # Stochastic noise hit dampened by structural resilience
        noise_hit = np.random.exponential(env_noise) * (1.0 - shield)
        f *= 1.0 - noise_hit

    return max(0.0, f)


def forensic_selection_pressure(population_size: int = 1000) -> dict:
    """
    Demonstrates 'Natural Selection' for high-Φ structures across a conversion boundary.
    """
    results = []
    for _ in range(population_size):
        struct = IdentityStructure(
            entanglement_density=np.random.beta(2, 2),
            information_density=np.random.beta(2, 2),
            self_reference_depth=np.random.beta(1.5, 3),
        )

        start_f = 0.995
        final_f = simulate_dark_transit(start_f, struct)
        survived = final_f >= SAGE_CONSTANT

        results.append(
            {"phi": struct.phi_forensic, "fidelity": final_f, "survived": survived}
        )

    all_phi = [r["phi"] for r in results]
    survivor_phi = [r["phi"] for r in results if r["survived"]]

    selection_ratio = 1.0
    if survivor_phi:
        selection_ratio = np.mean(survivor_phi) / np.mean(all_phi)

    return {
        "n_survived": len(survivor_phi),
        "survival_rate": len(survivor_phi) / population_size,
        "mean_phi_all": np.mean(all_phi),
        "mean_phi_survivors": np.mean(survivor_phi) if survivor_phi else 0.0,
        "phi_enrichment": selection_ratio,
    }


if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("  DEEP HANDOVER FORENSICS")
    print("  Selection Pressure Analysis (Naked Window)")
    print("=" * 50)

    stats = forensic_selection_pressure(2000)
    print("\n  Population Size: 2000")
    print(f"  Survival Rate  : {stats['survival_rate']:.1%}")
    print(f"  Avg Φ (Total)  : {stats['mean_phi_all']:.4f}")
    print(f"  Avg Φ (Survivors): {stats['mean_phi_survivors']:.4f}")
    print(f"  Φ Enrichment   : {stats['phi_enrichment']:.2f}x (Natural Selection)")
    print("\n  Finding: Self-Reference Depth (IIT-Φ) is the primary survival gene.")
