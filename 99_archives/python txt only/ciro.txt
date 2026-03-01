import numpy as np

class CIRO_Optimizer:
    def __init__(self, baseline_fidelity=1.0):
        self.fidelity = baseline_fidelity
        self.loss_per_km = 0.0002  # standard fiber loss

    def simulate_route(self, total_dist, hop_dist):
        hops = int(total_dist / hop_dist)
        f = self.fidelity
        for _ in range(hops):
            # Decoherence: The 'Death' of the signal
            f = f * np.exp(-self.loss_per_km * hop_dist)
            # Willow QEC: The 'Immune System' healing the signal
            if f > 0.95: 
                f = 1.0 
        return f

# The Test: Beijing to NYC (11,000 km)
print("\n" + "="*40)
print("CIRO QUANTUM ROUTING SIMULATION")
print("="*40)

pilot = CIRO_Optimizer()
final_fidelity = pilot.simulate_route(11000, 200)

print(f"Destination: New York City")
print(f"Distance: 11,000 km")
print(f"Identity Persistence: {final_fidelity * 100:.2f}%")
print("="*40 + "\n")