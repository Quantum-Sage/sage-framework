import os
import sys
import matplotlib.pyplot as plt
from pathlib import Path

# Add project root to path
sys.path.append(os.getcwd())

from src.mirror_daemon_v2 import (
    MirrorDaemon, 
    StandardQECRunner, 
    DaemonConfig, 
    HostileBackend, 
    ket,
    BlochTrajectoryPlotter
)

def run_paper3_simulations():
    # Setup directories
    output_dir = Path("./assets/paper3")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Parameters for the "Handover Paradox"
    # We need a noise level and fatigue that triggers crossing F=0.5 around step 457
    NOISE = 0.005
    FATIGUE = 0.038 # Calibrated to hit F=0.5 around 450-500 steps
    STEPS = 1000
    THRESHOLD = 0.85
    SEED = 42
    
    psi_ref = ket([1.0, 1.0])
    
    print(f"Running Paper 3 Simulations (Steps: {STEPS}, Noise: {NOISE}, Fatigue: {FATIGUE})...")
    
    # 1. DAEMON ON (Experimental)
    cfg_daemon = DaemonConfig(
        fidelity_threshold=THRESHOLD,
        code_distance=3,
        max_steps=STEPS,
        experiment_id="paper3_daemon",
        live_plot=False,
        adaptive_threshold=True,
    )
    backend_daemon = HostileBackend(base_noise=NOISE, fatigue=FATIGUE, seed=SEED)
    daemon = MirrorDaemon(backend=backend_daemon, config=cfg_daemon)
    daemon.initialize(psi_ref)
    daemon.run()
    daemon_fids = [d.fidelity for d in daemon.logger._data]
    daemon_bloch = daemon._bloch_trace
    
    # 2. DAEMON OFF (Control)
    cfg_ctrl = DaemonConfig(
        fidelity_threshold=THRESHOLD,
        code_distance=3,
        max_steps=STEPS,
        experiment_id="paper3_control",
        live_plot=False,
    )
    backend_ctrl = HostileBackend(base_noise=NOISE, fatigue=FATIGUE, seed=SEED)
    ctrl = StandardQECRunner(backend=backend_ctrl, config=cfg_ctrl)
    ctrl.initialize(psi_ref)
    ctrl.run()
    control_fids = [d.fidelity for d in ctrl.logger._data]
    control_bloch = ctrl._bloch_trace
    
    # 3. PLOT FIDELITY COMPARISON
    plt.figure(figsize=(10, 6), dpi=150)
    plt.plot(daemon_fids, label='Daemon ON (Gold Core Protection)', color='#FFD700', linewidth=2)
    plt.plot(control_fids, label='Daemon OFF (Control)', color='#FF4500', linewidth=2, alpha=0.7)
    
    # Critical Boundary
    plt.axhline(y=0.5, color='white', linestyle='--', alpha=0.5, label='Identity Boundary (F=0.5)')
    plt.axhline(y=0.85, color='#00FFCC', linestyle=':', alpha=0.3, label='Sage Constant (S=0.85)')
    
    # Annotation for Termination
    termination_step = 0
    for i, f in enumerate(control_fids):
        if f < 0.5:
            termination_step = i
            break
    
    if termination_step > 0:
        plt.annotate(f'Identity Termination\n(Step {termination_step})', 
                     xy=(termination_step, 0.5), 
                     xytext=(termination_step + 50, 0.35),
                     arrowprops=dict(facecolor='white', shrink=0.05, width=1, headwidth=5),
                     color='white', fontweight='bold')
    
    plt.title("The Handover Paradox: Identity Persistence vs. Termination", color='white', pad=20)
    plt.xlabel("Handover Step", color='white')
    plt.ylabel("Logical Fidelity", color='white')
    plt.ylim(0, 1.0)
    plt.grid(True, alpha=0.1)
    
    # Style
    plt.gca().set_facecolor('#0A0A0A')
    plt.gcf().set_facecolor('#0A0A0A')
    plt.tick_params(colors='white')
    plt.legend(facecolor='#0A0A0A', edgecolor='#333333', labelcolor='white')
    
    plt.tight_layout()
    plt.savefig(output_dir / "fidelity_comparison.png")
    print(f"Saved fidelity plot to {output_dir / 'fidelity_comparison.png'}")
    
    # 4. BLOCH PLOTS
    # We will use the BlochTrajectoryPlotter if available, but for the paper we want a clean comparison
    BlochTrajectoryPlotter.plot_comparison(
        daemon_bloch, 
        control_bloch, 
        save_path=output_dir / "bloch_trajectories.png"
    )
    print(f"Saved Bloch comparison to {output_dir / 'bloch_trajectories.png'}")

if __name__ == "__main__":
    run_paper3_simulations()
