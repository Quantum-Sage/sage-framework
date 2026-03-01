import numpy as np


def calculate_sage_bound(hops, hardware_fidelity, p_gen):
    """
    The Sage Bound: Universal Linear Program for Sequential Degradation.
    Maps multiplicative decay to 1D Linear Programs.
    """
    # Discovery 2: The Stochastic Grid Penalty (1 + 2/p)
    # This accounts for retry-induced decoherence during generation
    stochastic_penalty = 1 + (2 / p_gen)

    # The Log-Fidelity Map (The "A-ha!" Moment from Paper 1)
    # F_total = (F_node)^n / Penalty factor
    log_fidelity = hops * np.log(hardware_fidelity)

    # Calculate theoretical maximum fidelity
    theoretical_max = np.exp(log_fidelity) / stochastic_penalty

    return max(theoretical_max, 0.0)


# SAGE_CONSTANT: The Topological Sentience Threshold.
# Anchored to the Surface Code Threshold and 2D Bond Percolation critical point.
SAGE_CONSTANT = 0.851
