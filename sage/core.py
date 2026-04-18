import math
from typing import List, Dict, Union

class SageResult:
    """Result object for a SAGE feasibility check."""
    def __init__(self, is_feasible: bool, f_total: float, bottleneck_index: int = -1):
        self.is_feasible = is_feasible
        self.f_total = f_total
        self.bottleneck_index = bottleneck_index

class SageSolver:
    """
    SAGE (Synthetic Adaptive Generation Engine) Core Solver.
    
    Implements the O(1) Sage Bound feasibility test for sequential
    degradation systems (Quantum networks, cold chains, etc.).
    """
    
    def __init__(self, threshold: float = 0.851, confirmation_k: int = 2):
        """
        Args:
            threshold: Minimum end-to-end fidelity required (Sage Constant).
            confirmation_k: Topology invariant (k=1: one-way, k=2: round-trip).
        """
        self.threshold = threshold
        self.k = confirmation_k
        self.log_threshold = math.log(threshold)
        self.c = 2.0e5  # Speed of signal in fiber (km/s)

    def calculate_hop_cost(self, hop_data: Dict[str, float]) -> float:
        """
        Calculate the log-fidelity cost of a single hop.
        
        Args:
            hop_data: Dict with 'fidelity', 't2' (ms), 'p_succ', 'length' (km).
        """
        # 1. Base fidelity (gate error)
        cost = math.log(hop_data.get('fidelity', 1.0))
        
        # 2. Stochastic penalty (decoherence due to retries)
        # alpha = -s / (c * t2) * (1 + k/p)
        s = hop_data.get('length', 0.0)
        t2 = hop_data.get('t2', 1e9) / 1000.0  # Convert ms to s
        p = hop_data.get('p_succ', 1.0)
        
        penalty = (s / (self.c * t2)) * (1 + (self.k / p))
        return cost - penalty

    def check_feasibility(self, path_data: List[Dict[str, float]]) -> SageResult:
        """
        Perform O(N) feasibility check for a multi-hop path.
        
        Returns:
            SageResult object with feasibility flag and end-to-end fidelity.
        """
        if not path_data:
            return SageResult(True, 1.0, -1)

        total_log_f = 0.0
        # Fix: Initialize to infinity so first hop correctly sets min_cost
        min_cost = float('inf')
        bottleneck = 0
        
        required_keys = {'fidelity', 't2', 'p_succ', 'length'}
        
        for i, hop in enumerate(path_data):
            # Input validation
            missing = required_keys - set(hop.keys())
            if missing:
                raise KeyError(f"Hop {i} is missing required SAGE parameters: {missing}")

            cost = self.calculate_hop_cost(hop)
            total_log_f += cost
            
            # Identify path bottleneck (most negative cost = highest loss)
            if cost < min_cost:
                min_cost = cost
                bottleneck = i
        
        f_total = math.exp(total_log_f)
        is_feasible = total_log_f >= self.log_threshold
        
        return SageResult(is_feasible, f_total, bottleneck)

# --- Example Usage ---
if __name__ == "__main__":
    # Example: 3-hop metropolitan quantum network
    path = [
        {"fidelity": 0.999, "t2": 100, "p_succ": 0.10, "length": 20},
        {"fidelity": 0.999, "t2": 100, "p_succ": 0.05, "length": 25},
        {"fidelity": 0.999, "t2": 100, "p_succ": 0.08, "length": 15},
    ]
    
    solver = SageSolver(threshold=0.851)
    res = solver.check_feasibility(path)
    
    print("-" * 40)
    print(f"SAGE Feasibility Result: {'GO' if res.is_feasible else 'NO-GO'}")
    print(f"End-to-End Fidelity:     {res.f_total:.4f}")
    if not res.is_feasible:
        print(f"Bottleneck identified:   Hop {res.bottleneck_index}")
    print("-" * 40)
