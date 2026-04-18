import os
import math
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

def generate_collapse_data():
    """
    Generates data for three domains showing log-linear decay 
    under the Stochastic Penalty framework.
    """
    # X-axis: Sequence Depth (Number of Handover Stages)
    N_RANGE = np.arange(1, 101)
    
    # 1. QUANTUM REPEATER (k=2)
    # F_phys is very high, but low p_gen creates massive penalty
    QU_F_GATE = 0.999
    QU_LAMBDA = 0.005
    QU_P_GEN = 0.10
    QU_K = 2
    QU_EXP_PENALTY = QU_LAMBDA * QU_K / QU_P_GEN
    quantum_log_fids = N_RANGE * (math.log(QU_F_GATE) - QU_EXP_PENALTY)
    quantum_vals = np.exp(quantum_log_fids)

    # 2. VACCINE COLD CHAIN (k=1)
    # Higher retention per stage, but frequent handovers
    CC_RETENTION = 0.99
    CC_LAMBDA = 0.01
    CC_P_SUCCESS = 0.90
    CC_K = 1
    CC_EXP_PENALTY = CC_LAMBDA * CC_K / CC_P_SUCCESS
    cold_chain_log_potency = N_RANGE * (math.log(CC_RETENTION) - CC_EXP_PENALTY)
    cold_chain_vals = np.exp(cold_chain_log_potency)

    # 3. DRUG BIOAVAILABILITY (k=1, but higher baseline loss)
    # Large baseline loss at each barrier, high p (reliable biological stages)
    DD_TRANSMISSION = 0.95
    DD_LAMBDA = 0.005
    DD_P_SUCCESS = 0.99
    DD_K = 1
    DD_EXP_PENALTY = DD_LAMBDA * DD_K / DD_P_SUCCESS
    drug_log_bio = N_RANGE * (math.log(DD_TRANSMISSION) - DD_EXP_PENALTY)
    drug_vals = np.exp(drug_log_bio)

    # OUTPUT DIRECTORY
    output_dir = Path("./assets/paper3")
    output_dir.mkdir(parents=True, exist_ok=True)

    # PLOT
    plt.figure(figsize=(10, 7), dpi=150)
    
    # Style
    plt.gca().set_facecolor('#0A0A0A')
    plt.gcf().set_facecolor('#0A0A0A')
    plt.tick_params(colors='white')
    
    # Data Curves
    plt.plot(N_RANGE, quantum_vals, label='Quantum Repeater (k=2, p=0.1)', color='#00FFCC', linewidth=2.5)
    plt.plot(N_RANGE, cold_chain_vals, label='Vaccine Cold Chain (k=1, p=0.9)', color='#FFD700', linewidth=2.5)
    plt.plot(N_RANGE, drug_vals, label='Drug Bioavailability (k=1, p=0.99)', color='#FF00FF', linewidth=2.5)
    
    # SAGE Bound (The Envelope)
    SAGE_CONSTANT = 0.851
    plt.axhline(y=SAGE_CONSTANT, color='white', linestyle='--', alpha=0.3, label=f'SAGE Bound (S={SAGE_CONSTANT})')
    
    # Annotations
    plt.text(5, SAGE_CONSTANT + 0.02, "Stability Region", color='white', fontsize=10, alpha=0.6)
    plt.text(5, SAGE_CONSTANT - 0.05, "Entropy Catastrophe", color='white', fontsize=10, alpha=0.6)

    plt.yscale('log')
    plt.ylim(0.1, 1.1)
    plt.xlim(0, 100)
    
    plt.title("Domain Collapse: The Universal Stochastic Law", color='white', fontsize=14, pad=20)
    plt.xlabel("Sequence Depth (Hops / Stages / Barriers)", color='white')
    plt.ylabel("Normalized Quality (Log Scale)", color='white')
    
    plt.grid(True, which='both', linestyle=':', alpha=0.1, color='white')
    plt.legend(facecolor='#0A0A0A', edgecolor='#333333', labelcolor='white')
    
    # Save
    save_path = output_dir / "universal_collapse.png"
    plt.tight_layout()
    plt.savefig(save_path)
    print(f"Universal Collapse plot saved to {save_path}")

if __name__ == "__main__":
    generate_collapse_data()
