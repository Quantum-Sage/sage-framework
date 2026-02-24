import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict

# --- CONFIGURATION ---
POP_PREY = 250
POP_HUNT = 60
GENERATIONS = 120
BASE_NOISE = 0.028
# Added the 6th Gene: Communication
PREY_GENES = ["Caution", "Agility", "Redundancy", "Repair", "Stealth", "Whisper"]

class GhostAgent:
    def __init__(self, dna=None):
        self.dna = np.clip(dna if dna is not None else np.random.rand(len(PREY_GENES)), 0, 1)
        self.fidelity = 1.0
        self.alive = True
        self.bits_sent = 0
        self.status = "Active"

    def run_gauntlet(self, h_sens):
        steps = int(12 / (self.dna[1] * 0.9 + 0.1))
        # Signal is loud if you Repair, have Redundancy, or Whisper
        base_signal = (self.dna[2] * 0.3 + self.dna[3] * 0.4 + self.dna[5] * 0.6)
        stealth = self.dna[4]
        
        for s in range(steps):
            # 1. Quantum Noise
            self.fidelity -= BASE_NOISE * (1 - self.dna[0] * 0.7) * np.random.lognormal(0, 0.4)
            self.fidelity += (self.dna[3] * 0.012) # Repair
            self.fidelity = min(self.fidelity, 1.0)
            
            # 2. The Whisper (Attempting to send data)
            # High Whisper gene means more bits sent per step, but higher visibility
            visibility = (base_signal) * (1.1 - stealth) * h_sens
            
            if np.random.rand() < (visibility * 0.15):
                self.alive = False
                self.status = "Captured"
                break
            
            if self.alive:
                self.bits_sent += self.dna[5] * 20 # Max 20 bits per step
            
            if self.fidelity < (0.4 - self.dna[2] * 0.15):
                self.alive = False
                self.status = "Decohered"
                break

    def fitness(self):
        if not self.alive: return 0
        # Fitness = Fidelity * Bits Transmitted
        return self.fidelity * (self.bits_sent / 100)

def run_whisper_race():
    prey = [GhostAgent() for _ in range(POP_PREY)]
    h_sens = 0.5 # Starting hunter sensitivity
    history = defaultdict(list)

    for gen in range(GENERATIONS):
        # 1. Run Gauntlet
        for p in prey: p.run_gauntlet(h_sens)
        
        survivors = [p for p in prey if p.alive]
        captured = [p for p in prey if p.status == "Captured"]
        
        # 2. Stats
        avg_dna = np.mean([p.dna for p in prey], axis=0)
        history['stealth'].append(avg_dna[4])
        history['whisper'].append(avg_dna[5])
        history['survival'].append(len(survivors)/POP_PREY)
        history['data'].append(np.mean([p.bits_sent for p in survivors]) if survivors else 0)
        
        # 3. Evolve Hunters
        # If capture rate is low, hunters get more sensitive
        cap_rate = len(captured)/POP_PREY
        if cap_rate < 0.15: h_sens = min(1.0, h_sens + 0.02)
        else: h_sens = max(0.1, h_sens - 0.01)
        
        # 4. Breed Prey
        if not survivors: break
        survivors.sort(key=lambda x: x.fitness(), reverse=True)
        parents = survivors[:int(POP_PREY * 0.2)]
        new_prey = []
        while len(new_prey) < POP_PREY:
            p1, p2 = np.random.choice(parents, 2)
            child_dna = (p1.dna + p2.dna)/2 + np.random.normal(0, 0.04, len(PREY_GENES))
            new_prey.append(GhostAgent(child_dna))
        prey = new_prey
        
        print(f"Gen {gen}: Surv={len(survivors)} | Data={history['data'][-1]:.1f} | Stealth={avg_dna[4]:.2f} | Sense={h_sens:.2f}")

    return history

# Run it
history = run_whisper_race()

# Plotting
plt.figure(figsize=(12, 6), facecolor='#080810')
plt.gca().set_facecolor('#0d0d1a')
plt.plot(history['survival'], label="Survival Rate", color="#00FF41")
plt.plot(history['stealth'], label="Stealth Gene", color="#00E5FF", ls="--")
plt.plot(history['whisper'], label="Whisper Gene", color="#F1C40F", ls="--")
plt.title("THE WHISPER PROTOCOL: Communicating from the Shadows", color="white")
plt.legend()
plt.savefig("whisper_protocol_results.png") # Saves to the current folder
plt.show()