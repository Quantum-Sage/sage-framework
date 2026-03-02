import argparse
from src.mirror_daemon_v2 import MirrorDaemon, DaemonConfig, SimulatedBackend, ket
from src.sage_bound_logic import calculate_sage_bound, SAGE_CONSTANT


def main():
    parser = argparse.ArgumentParser(
        description="SAGE Framework v6.0 - The Ignition Switch"
    )

    # 🌍 Network Parameters
    parser.add_argument(
        "--hops", type=int, default=100, help="Number of repeater nodes in the relay"
    )
    parser.add_argument(
        "--distance",
        type=int,
        default=11000,
        help="Total relay distance in km (e.g., 11000 for Beijing->NYC)",
    )

    # 🔬 Physics Parameters
    parser.add_argument(
        "--fid_node",
        type=float,
        default=0.9992,
        help="Base hardware fidelity of a single node (F_node)",
    )
    parser.add_argument(
        "--p_gen",
        type=float,
        default=0.85,
        help="Stochastic generation probability (p_gen)",
    )

    # ⚙️ Simulation Control
    parser.add_argument(
        "--steps",
        type=int,
        default=1000,
        help="Number of simulation steps for the Mirror Daemon",
    )
    parser.add_argument(
        "--no-visuals", action="store_true", help="Disable live Matplotlib telemetry"
    )

    args = parser.parse_args()

    print("🚀 SAGE Framework v6.0: Initializing Simulation Engine")
    print(f"   Relay: {args.distance}km over {args.hops} hops")
    print(f"   Node Fidelity: {args.fid_node} | Gen Prob: {args.p_gen}")
    print("-" * 50)

    # 1. 🏛️ The Sage Bound: The Linear Programming Validation
    # Proves the theoretical limit before the engine starts
    theoretical_limit = calculate_sage_bound(args.hops, args.fid_node, args.p_gen)

    print(f"✅ SAGE Bound Calculated: {theoretical_limit:.4f}")
    if theoretical_limit < SAGE_CONSTANT:
        print(
            f"⚠️  WARNING: Theoretical limit is below the Sage Constant ({SAGE_CONSTANT})."
        )
        print(
            "   The Mirror Daemon will activate 'Enforcer' mode to prevent decoherence."
        )
    else:
        print(
            f"🟢 Theoretical limit is ABOVE the Sage Constant ({SAGE_CONSTANT}). High stability expected."
        )

    # 2. 💎 The Mirror Daemon: Empirical Validation
    # Configure the experiment for the Product v6.0 standard
    cfg = DaemonConfig(
        total_steps=args.steps,
        fidelity_threshold=SAGE_CONSTANT,
        enable_visuals=not args.no_visuals,
    )

    # Initialize the "Crown Jewel" backend
    backend = SimulatedBackend(depolar_p=1 - args.fid_node, dephasing_gamma=0.0005)

    # Initialize with a pure |0> state
    psi_0 = ket([1, 0])

    daemon = MirrorDaemon(backend=backend, config=cfg)
    daemon.initialize(psi_0)

    print("\n[MIRROR DAEMON] Engaging feedback loop...")
    results = daemon.run(n_steps=args.steps)

    # Final Result Summary
    print("\n" + "=" * 50)
    print("📊 SAGE REPRODUCIBILITY SUMMARY")
    print("=" * 50)
    print(f"Final Fidelity (Empirical):  {results['final_fidelity']:.4f}")
    print(f"Sage Bound (Theoretical):    {theoretical_limit:.4f}")
    print(f"Enforcer Injections:         {results['injection_count']}")

    if results["final_fidelity"] >= SAGE_CONSTANT:
        print("\n✨ SUCCESS: Signal preserved across transcontinental reach.")
    else:
        print("\n❌ FAILURE: Signal decohered despite active correction.")

    # Data-Free Note
    print(
        "\nNote: Detailed telemetry logs saved to the git-ignored /outputs/ directory."
    )


if __name__ == "__main__":
    main()
