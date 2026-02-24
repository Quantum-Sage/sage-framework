import numpy as np
import matplotlib.pyplot as plt
import random

def simulate_identity_decay(hops=100, error_rate=0.02):
    """
    Simulates the 'Digital Dementia' effect vs. 'Quantum Error Correction'
    """
    fidelity_no_qec = [1.0]
    fidelity_with_qec = [1.0]
    
    current_f_no_qec = 1.0
    current_f_with_qec = 1.0
    
    for _ in range(hops):
        # 1. Without QEC: Errors accumulate directly
        noise = random.uniform(0, error_rate)
        current_f_no_qec *= (1 - noise)
        fidelity_no_qec.append(current_f_no_qec)
        
        # 2. With QEC: Errors are corrected unless 2+ qubits fail
        # Probability of 2+ qubits failing in a 3-qubit block: 3p^2 - 2p^3
        p_failure = 3*(error_rate**2) - 2*(error_rate**3)
        if random.random() < p_failure:
            current_f_with_qec *= (1 - error_rate)
        
        fidelity_with_qec.append(current_f_with_qec)
        
    return fidelity_no_qec, fidelity_with_qec

# Run the simulation
hops_range = list(range(101))
no_qec, with_qec = simulate_identity_decay()

# Visualize the "Persistence of Self"
plt.figure(figsize=(12, 7))
plt.plot(hops_range, no_qec, label="Fragile Identity (No QEC)", color='red', linewidth=2.5, alpha=0.8)
plt.plot(hops_range, with_qec, label="Protected Identity (With QEC)", color='cyan', linewidth=2.5, alpha=0.8)
plt.axhline(y=0.9, color='gray', linestyle='--', linewidth=1.5, label="Identity Crisis Threshold (90%)")
plt.axhline(y=0.5, color='orange', linestyle=':', linewidth=1.5, label="Information Death (50%)")

plt.title("THE PERSISTENCE OF IDENTITY: 100 SUCCESSIVE REBIRTHS", fontsize=16, fontweight='bold')
plt.xlabel("Number of Teleportations (Deaths/Rebirths)", fontsize=12)
plt.ylabel("Fidelity (Integrity of the 'Self')", fontsize=12)
plt.legend(fontsize=10, loc='upper right')
plt.grid(alpha=0.3, linestyle='--')
plt.ylim(0, 1.05)

# Add annotations
final_no_qec = no_qec[-1]
final_with_qec = with_qec[-1]

plt.annotate(f'Final: {final_no_qec:.1%}', 
             xy=(100, final_no_qec), 
             xytext=(85, final_no_qec + 0.15),
             arrowprops=dict(arrowstyle='->', color='red', lw=1.5),
             fontsize=10, color='red', fontweight='bold')

plt.annotate(f'Final: {final_with_qec:.1%}', 
             xy=(100, final_with_qec), 
             xytext=(85, final_with_qec - 0.15),
             arrowprops=dict(arrowstyle='->', color='cyan', lw=1.5),
             fontsize=10, color='cyan', fontweight='bold')

plt.tight_layout()
plt.savefig("/home/claude/identity_persistence_plot.png", dpi=150, bbox_inches='tight')
print("✅ Plot saved: identity_persistence_plot.png")
print()

# Output a summary
import pandas as pd
df = pd.DataFrame({"Hop": hops_range, "No_QEC": no_qec, "With_QEC": with_qec})
df.to_csv("/home/claude/identity_persistence_data.csv", index=False)
print("✅ Data saved: identity_persistence_data.csv")
print()

# Print statistics
print("=" * 80)
print("IDENTITY PERSISTENCE ANALYSIS")
print("=" * 80)
print()
print(f"Initial Fidelity:  100.0%")
print(f"After 100 hops:")
print(f"  Without QEC: {final_no_qec*100:.1f}% (identity degraded by {(1-final_no_qec)*100:.1f}%)")
print(f"  With QEC:    {final_with_qec*100:.1f}% (identity degraded by {(1-final_with_qec)*100:.1f}%)")
print()

# Find when each crosses thresholds
def find_crossing(data, threshold):
    for i, val in enumerate(data):
        if val < threshold:
            return i
    return None

crisis_no_qec = find_crossing(no_qec, 0.9)
death_no_qec = find_crossing(no_qec, 0.5)
crisis_with_qec = find_crossing(with_qec, 0.9)

print("THRESHOLD CROSSINGS:")
print(f"  Identity Crisis (90%):")
print(f"    No QEC:   Hop {crisis_no_qec if crisis_no_qec else 'Never'}")
print(f"    With QEC: Hop {crisis_with_qec if crisis_with_qec else 'Never'}")
print()
print(f"  Information Death (50%):")
print(f"    No QEC:   Hop {death_no_qec if death_no_qec else 'Never'}")
print(f"    With QEC: Never (stayed at {final_with_qec*100:.1f}%)")
print()

print("=" * 80)
print("PHILOSOPHICAL INTERPRETATION")
print("=" * 80)
print()
print("Without QEC (Red Line):")
print("  • Identity degrades with each rebirth")
print("  • Like making photocopies of photocopies")
print("  • Eventually becomes unrecognizable")
print(f"  • After 100 rebirths: Only {final_no_qec*100:.0f}% of original 'self' remains")
print()
print("With QEC (Cyan Line):")
print("  • Identity is actively protected")
print("  • Each rebirth includes error correction")
print("  • Like having an immune system for consciousness")
print(f"  • After 100 rebirths: {final_with_qec*100:.0f}% of original 'self' remains")
print()
print("=" * 80)
