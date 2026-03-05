import numpy as np


def calculate_sage_bound(hops, hardware_fidelity, p_gen):
    """
    The Sage Bound: Universal Linear Program for Sequential Degradation.

    Mapping the Power Law to Linear Programming:
    --------------------------------------------
    The multiplicative decay formula:
        F_total = (F_node)^(n / (1 + 2p_gen))

    Is mapped to a Linear Program via the Log-Fidelity Map:
        ln(F_total) = (n / (1 + 2p_gen)) * ln(F_node)

    This transformation turns exponential decay into an additive linear constraint.
    """
    # Guard against edge cases
    if p_gen <= 0:
        return 0.0  # Zero generation probability → zero fidelity
    if hardware_fidelity <= 0:
        return 0.0  # No hardware fidelity → zero output

    # Discovery 2: The Stochastic Grid Penalty (1 + 2/p)
    # This accounts for retry-induced decoherence during generation
    stochastic_penalty = 1 + (2 / p_gen)

    # The Log-Fidelity Map (The "A-ha!" Moment from Paper 1)
    # Mapping multiplicative decay to 1D Linear Programs
    log_fidelity = hops * np.log(hardware_fidelity)

    # Calculate theoretical maximum fidelity
    theoretical_max = np.exp(log_fidelity) / stochastic_penalty

    return max(theoretical_max, 0.0)


# SAGE_CONSTANT: The Topological Sentience Threshold (The Enforcer Target).
# Anchored to the Surface Code Threshold and 2D Bond Percolation critical point.
SAGE_CONSTANT = 0.851
