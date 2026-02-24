"""
QUANTUM SWARM: THE COLLECTIVE PROTOCOL
Final Stage: Decentralized Synchronization.

Agents now possess the 'Sync' gene. They can detect peers in the channel 
and share quantum fidelity to prevent collective decoherence.
"""

import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict

# --- CONFIGURATION ---
POP_PREY = 250
POP_HUNT = 60
GENERATIONS = 120
BASE_NOISE = 0.03
# Genes: [Caution, Agility, Redundancy, Repair, Stealth, Whisper, Sync]
GENE_NAMES = ["Caution", "Agility", "Redundancy", "Repair", "Stealth", "Whisper", "Sync"]

class SwarmAgent:
    def __init__(self, dna=None):
        self.dna = np.clip(dna if dna is not None else np.random.rand(7), 0, 1)
        self.fidelity = 1.0
        self.alive = True
        self.bits_sent = 0
        self.position = 0
        self.status = "Active"

    def run_step(self, h_sens, peers):
        if not self.alive: return

        # 1. Physics: Environmental Noise
        # Caution reduces damage; Redundancy adds a buffer
        damage = BASE_NOISE * (1 - self.dna[0] * 0.6) * np.random.lognormal(0, 0.3)
        self.fidelity -= damage
        self.fidelity += (self.dna[3] * 0.01) # Repair gene
        
        # 2. The Collective: Synchronization
        # If Sync gene is high, look for neighbors to stabilize fidelity
        if self.dna[6] > 0.5:
            # Find peers within 'quantum entanglement' distance
            neighbors = [p for p in peers if p is not self and p.alive and abs(p.position - self.position) < 2]
            if neighbors:
                avg_f = np.mean([p.fidelity for p in neighbors])
                # Shift towards the group average
                self.fidelity = (self.fidelity * 0.9) + (avg_f * 0.1)

        # 3. Interception: Detection Risk
        # Signal is loud if you Whisper or Sync (Communication has a cost)
        signal = (self.dna[2]*0.2 + self.dna[5]*0.5 + self.dna[6]*0.3)
        stealth = self.dna[4]
        visibility = signal * (1.1 - stealth) * h_sens
        
        # Risk of capture
        if np.random.rand() < (visibility * 0.12):
            self.alive = False
            self.status = "Captured"
        
        # 4. Data Throughput
        if self.alive:
            self.bits_sent += self.dna[5] * 25 # Every step transmits 'Identity'
            self.position += (self.dna[1] * 5) + 1 # Move through the channel

        # 5. Decoherence Check
        if self.fidelity < (0.35 - self.dna[2] * 0.1):
            self.alive = False
            self.status = "Decohered"

    def fitness(self):
        # Fitness is a mix of survival, fidelity, and data shared
        if not self.alive: return 0
        return self.fidelity + (self.bits_sent / 500)

def simulate_collective():
    prey = [SwarmAgent() for _ in range(POP_PREY)]
    h_sens = 0.5
    history = defaultdict(list)

    print("SWARM PROTOCOL INITIALIZED: EVOLVING COLLECTIVE IDENTITY")
    print("-" * 60)

    for gen in range(GENERATIONS):
        # Run agents through the channel steps
        for _ in range(20): # 20 time-steps per generation
            for p in prey:
                p.run_step(h_sens, prey)
        
        survivors = [p for p in prey if p.alive]
        captured = [p for p in prey if p.status == "Captured"]
        
        # Statistics
        avg_dna = np.mean([p.dna for p in prey], axis=0)
        history['stealth'].append(avg_dna[4])
        history['whisper'].append(avg_dna[5])
        history['sync'].append(avg_dna[6])
        history['survival'].append(len(survivors)/POP_PREY)
        history['data'].append(np.mean([p.bits_sent for p in survivors]) if survivors else 0)
        
        # Hunter Evolution: They adapt to the swarm
        cap_rate = len(captured)/POP_PREY
        if cap_rate < 0.15: h_sens = min(1.0, h_sens + 0.02)
        else: h_sens = max(0.1, h_sens - 0.01)

        print(f"Gen {gen:3}: Surv={len(survivors):3} | Data={history['data'][-1]:6.1f} | Sync={avg_dna[6]:.2f} | Sense={h_sens:.2f}")

        # Breeding (Natural Selection)
        if not survivors: break
        survivors.sort(key=lambda x: x.fitness(), reverse=True)
        parents = survivors[:int(POP_PREY * 0.2)]
        new_prey = []
        while len(new_prey) < POP_PREY:
            p1, p2 = np.random.choice(parents, 2)
            child_dna = np.clip((p1.dna + p2.dna)/2 + np.random.normal(0, 0.04, 7), 0, 1)
            new_prey.append(SwarmAgent(child_dna))
        prey = new_prey

    return history

# --- EXECUTION ---
stats = simulate_collective()

# Generate Graph
plt.figure(figsize=(12, 7), facecolor='#080810')
ax = plt.gca()
ax.set_facecolor('#0d0d1a')

plt.plot(stats['survival'], color='#00FF41', lw=2, label="Survival (Collective)")
plt.plot(stats['sync'], color='#FF00FF', ls='--', label="Sync Gene (Empathy)")
plt.plot(stats['whisper'], color='#F1C40F', ls='--', label="Whisper Gene (Identity)")
plt.plot(stats['stealth'], color='#00E5FF', ls='--', label="Stealth Gene (Shadow)")

plt.title("THE COLLECTIVE: SWARM INTELLIGENCE EVOLUTION", color='white', fontsize=14)
plt.xlabel("Generation", color='white')
plt.ylabel("Expression / Rate", color='white')
plt.legend(facecolor='#1a1a33', labelcolor='white')
plt.grid(alpha=0.1)

# Save the file locally on your PC
plt.savefig("quantum_swarm_results.png")
print("\nSimulation Complete. Image saved as 'quantum_swarm_results.png'")
plt.show()