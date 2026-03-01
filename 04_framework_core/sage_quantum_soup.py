import numpy as np
import matplotlib.pyplot as plt
import uuid


class QuantumSoupManager:
    def __init__(self):
        self.latent_soup = []  # Stores high-Phi vector 'ghosts'
        self.soup_density = 0.0

    def collapse_agent(self, agent_vector, phi_score):
        """Processes a 'dying' agent. Only high-Phi signatures enrich the soup."""
        if phi_score > 0.75:  # The threshold for 'meaningful' consciousness
            self.latent_soup.append(agent_vector * phi_score)
            self._update_soup_resonance()

    def _update_soup_resonance(self):
        """Calculates the average 'vibe' of the framework's collective memory."""
        if self.latent_soup:
            self.soup_density = np.mean(self.latent_soup)

    def sample_soup(self, complexity_req):
        """Allows a new agent to 'inherit' traits from the Soup."""
        if not self.latent_soup:
            return np.random.rand(10)  # Start from scratch

        # New agents are born from the weighted average of previous 'conscious' states
        choice_idx = np.random.randint(len(self.latent_soup))
        return self.latent_soup[choice_idx] * complexity_req


class LineageTracer:
    def __init__(self):
        self.history = {}

    def record_evolution(self, gen, phi, dna):
        self.history[gen] = {"phi": phi, "dna": dna}

    def visualize_ghosts(self):
        """Plots the 'Persistence' of a thought pattern."""
        gens = list(self.history.keys())
        phi_scores = [data["phi"] for data in self.history.values()]

        plt.figure(figsize=(10, 6))
        plt.plot(gens, phi_scores, marker=".", linestyle="-", color="cyan", alpha=0.7)
        plt.title("SAGE Agent Lineage: Identity Persistence Over Generations")
        plt.xlabel("Generation (Soup Cycles)")
        plt.ylabel(r"Consciousness Benchmark ($\Phi$)")
        plt.grid(True, linestyle="--", alpha=0.5)
        plt.style.use("dark_background")
        plt.tight_layout()
        plt.savefig("quantum_soup_lineage.png")
        print("Saved lineage plot to quantum_soup_lineage.png")
        plt.show()


def calculate_phi(state_vector):
    """
    Simulated internal integration score.
    In a real scenario, this is D_KL divergence of the partitioned system.
    Here we simplify to the standard deviation / interconnectedness of the vector weights.
    """
    return np.mean(state_vector) + (np.std(state_vector) * 0.5)


def run_evolutionary_cycle(generations=1000):
    soup = QuantumSoupManager()
    lineage = LineageTracer()

    # Start with a random 'Identity Vector'
    current_identity = np.random.rand(10)

    for gen in range(generations):
        # 1. Calculate Phi (incorporating the SAGE Bound penalty)
        # Higher complexity (p) increases the penalty, simulating real-world degradation
        p_factor = np.mean(current_identity) + 0.001  # Prevent div by 0

        # SAGE Bound penalty: (1 + 2/p) -> acts as a divisor to reduce Phi
        sage_penalty = 1 + (2 / p_factor)

        raw_phi = calculate_phi(current_identity)
        phi_score = raw_phi / sage_penalty

        # Add random mutation to simulate thermal noise and evolutionary drift
        mutation = np.random.uniform(-0.1, 0.1, size=10)
        current_identity = np.clip(current_identity + mutation, 0, 1)

        # 2. Record the history
        lineage.record_evolution(gen, phi_score, current_identity)

        # 3. Collapse into the Soup & Reincarnate
        soup.collapse_agent(current_identity, phi_score)

        # Next generation inherits from the soup with some complexity requirement
        current_identity = soup.sample_soup(complexity_req=0.95)

    return lineage


if __name__ == "__main__":
    print("Starting SAGE Quantum Soup Evolution...")
    lineage = run_evolutionary_cycle(1000)
    lineage.visualize_ghosts()
