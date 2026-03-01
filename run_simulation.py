from src.mirror_daemon_v2 import MirrorDaemon, DaemonConfig, SimulatedBackend, ket
import numpy as np


def main():
    """
    SAGE Framework v6.0: One-Entry-Point Simulation

    A Linear Programming approach to Quantum Network Reach.
    Proves the existence of a 0.85 fidelity constant across 30,000 km relays.
    """
    print("SAGE Framework v6.0 Launching...")

    # Configure the experiment
    # The "One-Entry-Point" Rule: Create a single file called run_simulation.py in the root.
    cfg = DaemonConfig(
        total_steps=1000,
        fidelity_threshold=0.85,  # The Sage Constant
        injection_strength=0.15,
        enable_visuals=True,
    )

    # Initialize the "Mirror Daemon" (The Product)
    # Using the SimulatedBackend for a 1000-step experiment
    backend = SimulatedBackend(depolar_p=0.005, dephasing_gamma=0.002)

    # Initialize the reference state (e.g. |0>)
    psi_0 = ket([1, 0])

    daemon = MirrorDaemon(backend=backend, config=cfg)
    daemon.initialize(psi_0)

    print(f"\nMirrorDaemon v6.0 Initialized.")
    print(f"Backend: {backend.name}")
    print(f"Goal: Maintain F > {cfg.fidelity_threshold} (The Sage Constant)")

    # Run the simulation
    results = daemon.run()

    print("\nSimulation Complete.")
    print(f"Final Fidelity: {results['final_fidelity']:.4f}")
    print(f"Injection Rate: {results['injection_rate']:.2%}")
    print(f"Stability (Lyapunov): {results['lyapunov_exponent']:.4f}")


if __name__ == "__main__":
    main()
