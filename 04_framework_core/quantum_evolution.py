"""
QUANTUM SURVIVAL EVOLUTION
Evolving Optimal Strategies for Quantum Decoherence Resistance

What emerges when you subject a population to the brutal physics of
quantum noise across 1000 km? Do they evolve toward Caution or Agility?
Does the answer change when you add error correction?

Connects to the identity persistence framework:
  The genome IS the quantum error correction strategy.
  Evolution rediscovers QEC from scratch.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.colors import LinearSegmentedColormap
from collections import defaultdict

# ─── CONFIGURATION ──────────────────────────────────────────────────────────
POPULATION_SIZE = 200
GENERATIONS     = 80
BASE_NOISE      = 0.025
ELITE_FRAC      = 0.15    # top 15% breed
MUTATION_STD    = 0.04
EXTINCTION_RISK = True    # periodic hard events

# DNA GENES (each 0–1)
GENES = ["Caution", "Agility", "Redundancy", "Repair"]
# Caution    → reduces noise per step (slower, safer)
# Agility    → fewer steps (faster, noisier)
# Redundancy → copies of state (QEC-like — costly but protective)
# Repair     → active error correction per step (expensive energy)


class QuantumAgent:
    def __init__(self, dna=None):
        self.dna = np.clip(
            dna if dna is not None else np.random.rand(len(GENES)),
            0, 1
        )
        self.fidelity = 1.0
        self.alive    = True
        self.steps_survived = 0

    @property
    def caution(self):    return self.dna[0]
    @property
    def agility(self):    return self.dna[1]
    @property
    def redundancy(self): return self.dna[2]
    @property
    def repair(self):     return self.dna[3]

    def run_gauntlet(self, hard_event=False):
        """
        Simulate the quantum channel.
        Returns True if survived.
        """
        self.fidelity = 1.0
        self.alive    = True
        self.steps_survived = 0

        # Gene trade-offs
        steps          = int(8 / (self.agility * 0.9 + 0.1))   # agility → fewer steps
        noise_per_step = BASE_NOISE * (1 - self.caution * 0.75) # caution → less noise
        repair_bonus   = self.repair * 0.012                    # active repair per step
        redundancy_buf = self.redundancy * 0.18                 # buffer above threshold

        death_threshold = 0.50 - redundancy_buf  # redundancy raises point of no return

        for _ in range(steps):
            # Quantum weather: lognormal bursts (heavier tails than Gaussian)
            weather = np.random.lognormal(mean=0.0, sigma=0.4)
            damage  = noise_per_step * weather

            # Optional hard event (gamma-ray burst, etc.)
            if hard_event and np.random.rand() < 0.12:
                damage *= np.random.uniform(3, 7)

            self.fidelity -= damage
            self.fidelity += repair_bonus      # active error correction
            self.fidelity  = min(self.fidelity, 1.0)  # can't exceed perfect
            self.steps_survived += 1

            if self.fidelity < death_threshold:
                self.alive = False
                self.fidelity = 0.0
                break

        self.fidelity = max(0, self.fidelity)

    def fitness(self):
        """Composite fitness: fidelity AND survival bonus AND efficiency."""
        if not self.alive:
            return 0.0
        steps_bonus = 1.0 - (self.steps_survived / 100) * 0.1   # fewer steps = bonus
        return self.fidelity * steps_bonus

    def reproduce(self, partner, mutation_std=MUTATION_STD):
        """Crossover + mutation → child agent."""
        # Uniform crossover
        mask     = np.random.rand(len(GENES)) > 0.5
        child_dna = np.where(mask, self.dna, partner.dna)
        child_dna += np.random.normal(0, mutation_std, len(GENES))
        return QuantumAgent(np.clip(child_dna, 0, 1))


# ─── EVOLUTION ENGINE ───────────────────────────────────────────────────────
def evolve(seed=42):
    rng = np.random.default_rng(seed)
    np.random.seed(seed)

    population = [QuantumAgent() for _ in range(POPULATION_SIZE)]

    history = {
        "mean_fidelity":    [],
        "max_fidelity":     [],
        "survival_rate":    [],
        "gene_means":       defaultdict(list),   # per gene
        "gene_stds":        defaultdict(list),
        "diversity":        [],                  # population std across all genes
        "best_dna_trace":   [],
    }

    for gen in range(GENERATIONS):

        # Periodic extinction event (every 15 gens)
        hard_event = EXTINCTION_RISK and (gen % 15 == 14)

        # Run gauntlet
        for agent in population:
            agent.run_gauntlet(hard_event=hard_event)

        survivors = [a for a in population if a.alive]
        survival_rate = len(survivors) / POPULATION_SIZE

        if not survivors:
            print(f"Gen {gen:3d}: ☠  EXTINCTION — population wiped out")
            break

        survivors.sort(key=lambda a: a.fitness(), reverse=True)

        mean_fid = np.mean([a.fidelity for a in survivors])
        max_fid  = survivors[0].fidelity
        best_dna = survivors[0].dna.copy()

        # Record gene stats across WHOLE population (including dead)
        all_dna = np.array([a.dna for a in population])
        diversity = np.mean(np.std(all_dna, axis=0))

        history["mean_fidelity"].append(mean_fid)
        history["max_fidelity"].append(max_fid)
        history["survival_rate"].append(survival_rate)
        history["diversity"].append(diversity)
        history["best_dna_trace"].append(best_dna)

        for i, gene in enumerate(GENES):
            history["gene_means"][gene].append(np.mean(all_dna[:, i]))
            history["gene_stds"][gene].append(np.std(all_dna[:, i]))

        event_tag = "  ⚡ HARD EVENT" if hard_event else ""
        print(f"Gen {gen:3d}: fid={mean_fid:.4f}  best={max_fid:.4f}  "
              f"survived={survival_rate:.0%}  diversity={diversity:.3f}{event_tag}")

        # Breed next generation
        parents = survivors[:max(2, int(POPULATION_SIZE * ELITE_FRAC))]
        new_pop = list(parents[:int(POPULATION_SIZE * 0.05)])  # elites survive unchanged

        while len(new_pop) < POPULATION_SIZE:
            p1, p2 = rng.choice(parents, 2, replace=True)
            new_pop.append(p1.reproduce(p2))

        population = new_pop[:POPULATION_SIZE]

    return history


# ─── PLOTTING ───────────────────────────────────────────────────────────────
def plot(history):
    gens = range(len(history["mean_fidelity"]))

    DARK = "#080810"
    MID  = "#0d0d1a"
    GRID = "#1a1a33"

    GENE_COLORS = {
        "Caution":    "#e74c3c",
        "Agility":    "#3498db",
        "Redundancy": "#00e5ff",
        "Repair":     "#2ecc71",
    }

    fig = plt.figure(figsize=(20, 14), facecolor=DARK)
    fig.suptitle(
        "QUANTUM SURVIVAL EVOLUTION\n"
        "What Strategy Does Nature Select for Surviving Quantum Decoherence?",
        fontsize=16, fontweight="bold", color="white", y=0.99
    )

    gs = gridspec.GridSpec(3, 3, figure=fig,
                           hspace=0.52, wspace=0.35,
                           left=0.07, right=0.97,
                           top=0.93, bottom=0.06)

    ax_fit    = fig.add_subplot(gs[0, :2])   # main fidelity trace
    ax_surv   = fig.add_subplot(gs[0, 2])    # survival rate
    ax_genes  = fig.add_subplot(gs[1, :2])   # all 4 genes over time
    ax_div    = fig.add_subplot(gs[1, 2])    # diversity
    ax_dna    = fig.add_subplot(gs[2, :])    # heatmap of best-agent DNA trace

    for ax in [ax_fit, ax_surv, ax_genes, ax_div, ax_dna]:
        ax.set_facecolor(MID)
        for spine in ax.spines.values():
            spine.set_color(GRID)

    def style(ax, title, xlabel="Generation", ylabel=""):
        ax.set_title(title, color="white", fontsize=10, pad=7)
        ax.set_xlabel(xlabel, color="#aaaacc", fontsize=9)
        ax.set_ylabel(ylabel, color="#aaaacc", fontsize=9)
        ax.tick_params(colors="#aaaacc", labelsize=8)
        ax.grid(True, alpha=0.15, color=GRID)

    # Mark hard events
    hard_events = [g for g in gens if EXTINCTION_RISK and (g % 15 == 14)]

    def mark_events(ax):
        for g in hard_events:
            ax.axvline(g, color="#ff4444", lw=0.8, ls="--", alpha=0.5)
        if hard_events:
            ax.axvline(hard_events[0], color="#ff4444", lw=0.8, ls="--",
                       alpha=0.5, label="⚡ Hard event")

    # ── Panel 1: Fidelity ──────────────────────────────────────────────────
    mean_f = history["mean_fidelity"]
    max_f  = history["max_fidelity"]

    ax_fit.fill_between(gens, mean_f, max_f, alpha=0.15, color="#00e5ff")
    ax_fit.plot(gens, max_f,  color="#00e5ff", lw=2.0, label="Best fidelity")
    ax_fit.plot(gens, mean_f, color="#888888", lw=1.5, ls="--", label="Mean fidelity")
    mark_events(ax_fit)
    ax_fit.set_xlim(0, len(gens) - 1)
    ax_fit.set_ylim(0, 1.05)
    ax_fit.legend(fontsize=8.5, facecolor="#111128", labelcolor="white",
                   edgecolor=GRID, loc="lower right")
    style(ax_fit, "Fidelity at Destination  (Best & Mean Survivors)", ylabel="Fidelity")

    # ── Panel 2: Survival Rate ────────────────────────────────────────────
    sr = history["survival_rate"]
    ax_surv.fill_between(gens, sr, alpha=0.2, color="#f39c12")
    ax_surv.plot(gens, sr, color="#f39c12", lw=2.0)
    mark_events(ax_surv)
    ax_surv.set_xlim(0, len(gens) - 1)
    ax_surv.set_ylim(0, 1.05)
    style(ax_surv, "Survival Rate per Generation", ylabel="Fraction surviving")

    # ── Panel 3: Gene Evolution ───────────────────────────────────────────
    for gene, color in GENE_COLORS.items():
        means = history["gene_means"][gene]
        stds  = history["gene_stds"][gene]
        arr   = np.array(means)
        std   = np.array(stds)
        ax_genes.plot(gens, arr, color=color, lw=2.0, label=gene)
        ax_genes.fill_between(gens, arr - std, arr + std, alpha=0.10, color=color)

    ax_genes.axhline(0.5, color="#ffffff", lw=0.8, ls=":", alpha=0.3)
    mark_events(ax_genes)
    ax_genes.set_xlim(0, len(gens) - 1)
    ax_genes.set_ylim(-0.05, 1.05)
    ax_genes.legend(fontsize=8.5, facecolor="#111128", labelcolor="white",
                     edgecolor=GRID, loc="upper left", ncol=2)
    style(ax_genes, "Gene Evolution  (shading = population std dev)", ylabel="Gene value")

    # ── Panel 4: Diversity ────────────────────────────────────────────────
    divs = history["diversity"]
    ax_div.fill_between(gens, divs, alpha=0.25, color="#8e44ad")
    ax_div.plot(gens, divs, color="#8e44ad", lw=2.0)
    mark_events(ax_div)
    ax_div.set_xlim(0, len(gens) - 1)
    style(ax_div, "Population Genetic Diversity\n(mean std dev across genes)",
          ylabel="Diversity index")

    # ── Panel 5: DNA Heatmap of Best Agent over Time ──────────────────────
    dna_trace = np.array(history["best_dna_trace"]).T   # shape: (4 genes, generations)
    cmap = LinearSegmentedColormap.from_list(
        "quantumcmap",
        ["#0a0a18", "#0d2b5e", "#1565c0", "#00e5ff", "#ffffff"]
    )
    im = ax_dna.imshow(dna_trace, aspect="auto", cmap=cmap,
                       vmin=0, vmax=1, interpolation="nearest")
    ax_dna.set_yticks(range(len(GENES)))
    ax_dna.set_yticklabels(GENES, color="white", fontsize=9)
    ax_dna.set_xlabel("Generation", color="#aaaacc", fontsize=9)
    ax_dna.tick_params(colors="#aaaacc", labelsize=8)
    ax_dna.set_title(
        "Best Agent DNA Over Time  (brightness = gene expression level)\n"
        "Watch which genes get selected — this IS evolution discovering QEC",
        color="white", fontsize=10, pad=7
    )

    for g in hard_events:
        ax_dna.axvline(g, color="#ff4444", lw=1.0, ls="--", alpha=0.6)

    plt.colorbar(im, ax=ax_dna, fraction=0.015, pad=0.01,
                 label="Gene value (0=off, 1=max)").ax.yaxis.label.set_color("white")

    # ── Final gene verdict annotation ─────────────────────────────────────
    final_means = {g: history["gene_means"][g][-1] for g in GENES}
    winner = max(final_means, key=final_means.get)
    verdict = (
        f"Evolution's answer:\n"
        f"  {winner} dominates  ({final_means[winner]:.2f}/1.0)\n\n"
        + "\n".join(f"  {g}: {v:.2f}" for g, v in final_means.items())
        + f"\n\nInsight: the winning gene\n"
          f"is the one closest to\na real QEC strategy."
    )
    ax_surv.text(0.04, 0.04, verdict,
                 transform=ax_surv.transAxes,
                 va="bottom", ha="left",
                 fontsize=7.5, color="white",
                 fontfamily="monospace",
                 bbox=dict(facecolor="#0a0a18", edgecolor="#f39c12",
                           linewidth=1.2, boxstyle="round,pad=0.5", alpha=0.9))

    fig.text(0.5, 0.005,
             "Each agent carries 4 genes: Caution · Agility · Redundancy · Repair  "
             "— evolution selects the strategy that survives quantum noise over 1000 km",
             ha="center", color="#2a2a4a", fontsize=7.5, style="italic")

    out = "/mnt/user-data/outputs/quantum_evolution.png"
    plt.savefig(out, dpi=170, bbox_inches="tight", facecolor=DARK)
    plt.close()
    print(f"\n✅  Saved → {out}")
    return out


# ─── MAIN ───────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("QUANTUM SURVIVAL EVOLUTION")
    print("=" * 60)
    history = evolve(seed=7)
    plot(history)

    # Summary
    final = {g: history["gene_means"][g][-1] for g in GENES}
    init  = {g: history["gene_means"][g][0]  for g in GENES}
    print("\nGENE EVOLUTION SUMMARY")
    print(f"{'Gene':<12} {'Start':>8} {'Final':>8} {'Δ':>8}  {'Winner?'}")
    print("─" * 52)
    winner = max(final, key=final.get)
    for g in GENES:
        delta = final[g] - init[g]
        tag   = " ◄ SELECTED" if g == winner else ""
        print(f"  {g:<10} {init[g]:>8.3f} {final[g]:>8.3f} {delta:>+8.3f}{tag}")
    print()
    print(f"Evolution discovered: '{winner}' maximizes quantum survival.")
    print(f"This maps directly to real QEC: active {'repair' if winner=='Repair' else 'redundancy'}.")
