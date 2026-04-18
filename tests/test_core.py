import pytest
import math
from sage.core import SageSolver

def test_empty_path():
    solver = SageSolver()
    res = solver.check_feasibility([])
    assert res.is_feasible is True
    assert res.f_total == 1.0
    assert res.bottleneck_index == -1

def test_single_hop_feasible():
    solver = SageSolver(threshold=0.851)
    # F=0.99, length=0 -> alpha = ln(0.99)
    hop = {"fidelity": 0.99, "t2": 1000, "p_succ": 1.0, "length": 0}
    res = solver.check_feasibility([hop])
    assert res.is_feasible is True
    assert pytest.approx(res.f_total, 0.001) == 0.99

def test_theorem_3_stochastic_penalty():
    solver = SageSolver(confirmation_k=2)
    # N=1, length=200, t2=72ms, p=0.10
    # Expected alpha = ln(F) - (s/(c*t2)) * (1 + 2/p)
    # alpha = ln(0.99) - (200 / (2e5 * 0.072)) * (1 + 2/0.10)
    # alpha = ln(0.99) - (200 / 14400) * (21)
    # alpha = -0.010 - (0.0138) * 21 = -0.010 - 0.291 = -0.301
    hop = {"fidelity": 0.99, "t2": 72, "p_succ": 0.10, "length": 200}
    res = solver.check_feasibility([hop])
    expected_f = math.exp(math.log(0.99) - (200 / (2e5 * 0.072)) * 21)
    assert pytest.approx(res.f_total, 0.001) == expected_f

def test_bottleneck_detection_fixed():
    solver = SageSolver()
    # Hop 1: -0.1 cost
    # Hop 2: -0.5 cost (Bottleneck)
    # Hop 3: -0.2 cost
    path = [
        {"fidelity": math.exp(-0.1), "t2": 1000, "p_succ": 1.0, "length": 0},
        {"fidelity": math.exp(-0.5), "t2": 1000, "p_succ": 1.0, "length": 0},
        {"fidelity": math.exp(-0.2), "t2": 1000, "p_succ": 1.0, "length": 0},
    ]
    res = solver.check_feasibility(path)
    assert res.bottleneck_index == 1

def test_input_validation():
    solver = SageSolver()
    # Missing 'length'
    bad_hop = {"fidelity": 0.99, "t2": 100, "p_succ": 1.0}
    with pytest.raises(KeyError) as excinfo:
        solver.check_feasibility([bad_hop])
    assert "missing required SAGE parameters" in str(excinfo.value)
    assert "length" in str(excinfo.value)

def test_infeasible_path():
    # Set threshold very high
    solver = SageSolver(threshold=0.999)
    hop = {"fidelity": 0.90, "t2": 100, "p_succ": 1.0, "length": 0}
    res = solver.check_feasibility([hop])
    assert res.is_feasible is False
