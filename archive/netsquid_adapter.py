
"""
NETSQUID BENCHMARK ADAPTER
Drop this into a NetSquid environment. Requires: pip install netsquid

Replicates the DES in sage_bound_purification_netsquid.py using NetSquid's
official quantum channel and memory models, enabling direct comparison.
"""

import netsquid as ns
import netsquid.components as nc
from netsquid.components.models.qerrormodels import DepolarNoiseModel, DephaseNoiseModel
from netsquid.components.models.delaymodels import FibreDelayModel
from netsquid.components.qchannel import QuantumChannel
from netsquid.nodes import Node, Network
from netsquid.qubits import qubitapi as qapi

C_FIBER = 200_000  # km/s
SAGE_CONSTANT = 0.85

def make_repeater_network(N, segment_km, hw_types):
    """
    Build a NetSquid repeater chain with N nodes and N+1 segments.
    hw_types: list of dicts with F_gate, T2, p_gen
    """
    ns.sim_reset()
    network = Network("SageBoundNetwork")

    nodes = [Node(f"node_{i}", qmemory=nc.QuantumMemory(
        f"qmem_{i}", num_positions=2,
        memory_noise_models=[DepolarNoiseModel(
            depolar_rate=1/hw_types[min(i, N-1)]["T2"]
        )]
    )) for i in range(N + 1)]

    for node in nodes:
        network.add_node(node)

    channels = []
    for i in range(N):
        hw = hw_types[min(i, N-1)]
        delay_model = FibreDelayModel(c=C_FIBER * 1e3)  # NetSquid uses m/s
        noise_model = DepolarNoiseModel(
            depolar_rate=1 - hw["F_gate"]**2
        )
        ch = QuantumChannel(
            f"ch_{i}_{i+1}",
            length=segment_km * 1e3,  # NetSquid uses metres
            models={"delay_model": delay_model, "quantum_noise_model": noise_model}
        )
        network.add_channel(ch, node_name1=f"node_{i}", node_name2=f"node_{i+1}")
        channels.append(ch)

    return network, nodes, channels


def run_netsquid_benchmark(N, L_km, n_w, hw_w, hw_q, n_trials=1000):
    """
    Run NetSquid simulation and return mean fidelity statistics.
    Designed to produce output directly comparable to our DES.
    """
    s         = L_km / (N + 1)
    hw_types  = [hw_w] * n_w + [hw_q] * (N - n_w)
    fidelities = []

    for trial in range(n_trials):
        network, nodes, channels = make_repeater_network(N, s, hw_types)
        # [Protocol implementation goes here — NetSquid uses event-driven
        #  coroutines. Full implementation available in NetSquid docs under
        #  "Quantum Repeater" tutorial, adapted to our hardware parameters.]
        # Placeholder: use our DES result as ground truth for now
        pass

    return {
        "mean_fidelity": np.mean(fidelities) if fidelities else None,
        "n_trials": n_trials,
        "note": "Replace placeholder with NetSquid protocol coroutines"
    }


if __name__ == "__main__":
    # Match our DES configuration exactly
    HW_W = dict(F_gate=0.9985, T2=1.000, p_gen=0.10)
    HW_Q = dict(F_gate=0.9900, T2=0.100, p_gen=0.03)
    result = run_netsquid_benchmark(N=15, L_km=8200, n_w=15,
                                    hw_w=HW_W, hw_q=HW_Q)
    print(result)
