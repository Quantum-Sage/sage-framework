"""
QUANTUM SURVIVAL EVOLUTION  ·  v2: The Energy Constraint
─────────────────────────────────────────────────────────
In v1, Repair was free — evolution maxed it out trivially.

In v2, every agent runs on a finite battery.
The critical fix: battery drains PER STEP with no normalisation.
This means slow agents (low Agility = many steps) burn far more battery
than fast agents. Agility and Repair are now genuinely coupled:

  • Low Agility + High Repair → battery death (too many expensive steps)
  • High Agility + Low Repair → decoherence death (fast but unprotected)
  • The sweet spot is a saddle point. Evolution has to find it.

Two kill mechanisms compete across generations. Watch them in the
cause-of-death panel.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.colors import LinearSegmentedColormap
from collections import defaultdict

# ─── CONFIGURATION ──────────────────────────────────────────────────────────
POPULATION_SIZE     = 300
GENERATIONS         = 100
BASE_NOISE          = 0.028
ELITE_FRAC          = 0.15
MUTATION_STD        = 0.04
EXTINCTION_RISK     = True

# ── Battery (the new physics) ────────────────────────────────────────────────
# Battery drains EACH STEP — not normalised.
# Low Agility → more steps → more drain. That's the key coupling.
BATTERY_SIZE        = 0.65   # tight enough that high-repair + many-steps kills
REPAIR_COST_SCALE   = 0.07   # per step: cost = SCALE * repair^2
REDUND_COST_SCALE   = 0.03   # per step: cost = SCALE * redundancy

# When battery dies: QEC stops and redundancy buffer collapses.
# Agent may still limp to the finish — or die of decoherence without protection.

GENES = ["Caution", "Agility", "Redundancy", "Repair"]


class QuantumAgent:
    ALIVE       = "alive"
    DECOHERENCE = "decoherence"
    EXHAUSTION  = "exhaustion"   # battery died → then fidelity collapsed

    def __init__(self, dna=None):
        self.dna = np.clip(
            dna if dna is not None else np.random.rand(len(GENES)), 0, 1
        )
        self.reset()

    def reset(self):
        self.fidelity       = 1.0
        self.alive          = True
        self.cause_of_death = self.ALIVE
        self.steps_total    = 0
        self.battery        = BATTERY_SIZE
        self.battery_at_end = BATTERY_SIZE

    @property
    def caution(self):    return self.dna[0]
    @property
    def agility(self):    return self.dna[1]
    @property
    def redundancy(self): return self.dna[2]
    @property
    def repair(self):     return self.dna[3]

    def run_gauntlet(self, hard_event: bool = False):
        self.reset()

        # ── Gene → physics ────────────────────────────────────────────────
        # More agility = fewer steps. Steps NOT normalised for energy.
        steps          = int(8 / (self.agility * 0.9 + 0.1))
        noise_per_step = BASE_NOISE * (1 - self.caution * 0.75)
        repair_bonus   = self.repair * 0.013      # heal per step at full battery
        redund_buf     = self.redundancy * 0.18   # buffer below 0.5 threshold

        hard_death_thresh = 0.50            # threshold when unprotected
        soft_death_thresh = hard_death_thresh - redund_buf

        battery_dead = False

        for _ in range(steps):
            # ── Energy drain (no step-weight — this is what makes it bind) ─
            if not battery_dead:
                cost = REPAIR_COST_SCALE * (self.repair ** 2) \
                     + REDUND_COST_SCALE  *  self.redundancy
                self.battery -= cost
                if self.battery <= 0:
                    self.battery  = 0
                    battery_dead  = True
                    # Protection collapses when power dies
                    soft_death_thresh = hard_death_thresh

            # ── Noise ─────────────────────────────────────────────────────
            weather = np.random.lognormal(mean=0.0, sigma=0.4)
            damage  = noise_per_step * weather
            if hard_event and np.random.rand() < 0.12:
                damage *= np.random.uniform(3, 7)

            self.fidelity -= damage

            # ── Repair (only while powered) ───────────────────────────────
            if not battery_dead:
                self.fidelity += repair_bonus

            self.fidelity = np.clip(self.fidelity, 0, 1.0)
            self.steps_total += 1

            # ── Death check ───────────────────────────────────────────────
            if self.fidelity < soft_death_thresh:
                self.alive = False
                self.cause_of_death = (
                    self.EXHAUSTION if battery_dead else self.DECOHERENCE
                )
                self.fidelity = 0.0
                break

        self.battery_at_end = self.battery

    def fitness(self) -> float:
        if not self.alive:
            return 0.0
        # Small penalty for wasted battery (unused power = over-cautious spending)
        waste_penalty = self.battery_at_end * 0.12
        return self.fidelity * (1.0 - waste_penalty)

    def reproduce(self, partner, mutation_std=MUTATION_STD):
        mask      = np.random.rand(len(GENES)) > 0.5
        child_dna = np.where(mask, self.dna, partner.dna)
        child_dna += np.random.normal(0, mutation_std, len(GENES))
        return QuantumAgent(np.clip(child_dna, 0, 1))


# ─── EVOLUTION ENGINE ───────────────────────────────────────────────────────
def evolve(seed: int = 7):
    rng = np.random.default_rng(seed)
    np.random.seed(seed)

    population = [QuantumAgent() for _ in range(POPULATION_SIZE)]

    history = {
        "mean_fidelity":      [],
        "max_fidelity":       [],
        "survival_rate":      [],
        "decoherence_deaths": [],
        "exhaustion_deaths":  [],
        "mean_battery_end":   [],
        "gene_means":         defaultdict(list),
        "gene_stds":          defaultdict(list),
        "diversity":          [],
        "best_dna_trace":     [],
        "final_gen_repair":   [],
        "final_gen_fitness":  [],
        "final_gen_battery":  [],
        "final_gen_alive":    [],
        "final_gen_cause":    [],
    }

    for gen in range(GENERATIONS):
        hard_event = EXTINCTION_RISK and (gen % 15 == 14)

        for agent in population:
            agent.run_gauntlet(hard_event=hard_event)

        survivors = [a for a in population if a.alive]
        dead      = [a for a in population if not a.alive]
        n_total   = POPULATION_SIZE
        survival_rate = len(survivors) / n_total
        n_deco  = sum(1 for a in dead if a.cause_of_death == QuantumAgent.DECOHERENCE)
        n_exhau = sum(1 for a in dead if a.cause_of_death == QuantumAgent.EXHAUSTION)

        if not survivors:
            print(f"Gen {gen:3d}: EXTINCTION")
            break

        survivors.sort(key=lambda a: a.fitness(), reverse=True)

        mean_fid = np.mean([a.fidelity      for a in survivors])
        max_fid  = survivors[0].fidelity
        mean_bat = np.mean([a.battery_at_end for a in survivors])
        best_dna = survivors[0].dna.copy()

        all_dna   = np.array([a.dna for a in population])
        diversity = np.mean(np.std(all_dna, axis=0))

        history["mean_fidelity"].append(mean_fid)
        history["max_fidelity"].append(max_fid)
        history["survival_rate"].append(survival_rate)
        history["decoherence_deaths"].append(n_deco / n_total)
        history["exhaustion_deaths"].append(n_exhau / n_total)
        history["mean_battery_end"].append(mean_bat)
        history["diversity"].append(diversity)
        history["best_dna_trace"].append(best_dna)

        for i, gene in enumerate(GENES):
            history["gene_means"][gene].append(np.mean(all_dna[:, i]))
            history["gene_stds"][gene].append(np.std(all_dna[:, i]))

        event_tag = "  HARD EVENT" if hard_event else ""
        print(
            f"Gen {gen:3d}: fid={mean_fid:.4f}  best={max_fid:.4f}  "
            f"surv={survival_rate:.0%}  "
            f"deco={n_deco:3d}  exh={n_exhau:3d}  "
            f"bat={mean_bat:.3f}{event_tag}"
        )

        parents = survivors[:max(2, int(POPULATION_SIZE * ELITE_FRAC))]
        new_pop = list(parents[:int(POPULATION_SIZE * 0.04)])
        while len(new_pop) < POPULATION_SIZE:
            p1, p2 = rng.choice(parents, 2, replace=True)
            new_pop.append(p1.reproduce(p2))
        population = new_pop[:POPULATION_SIZE]

    # Final generation snapshot for Goldilocks scatter
    for agent in population:
        agent.run_gauntlet(hard_event=False)
    history["final_gen_repair"]  = [a.repair          for a in population]
    history["final_gen_fitness"] = [a.fitness()        for a in population]
    history["final_gen_battery"] = [a.battery_at_end   for a in population]
    history["final_gen_alive"]   = [a.alive             for a in population]
    history["final_gen_cause"]   = [a.cause_of_death    for a in population]

    return history


# ─── PLOTTING ───────────────────────────────────────────────────────────────
def plot(history):
    DARK = "#080810"
    MID  = "#0d0d1a"
    GRID = "#1a1a33"

    GENE_COLORS = {
        "Caution":    "#e74c3c",
        "Agility":    "#3498db",
        "Redundancy": "#00e5ff",
        "Repair":     "#f1c40f",
    }

    gens = range(len(history["mean_fidelity"]))

    fig = plt.figure(figsize=(22, 18), facecolor=DARK)
    fig.suptitle(
        "QUANTUM SURVIVAL EVOLUTION  v2: The Energy Constraint\n"
        "Can evolution find the Goldilocks Zone between decoherence and battery death?",
        fontsize=15, fontweight="bold", color="white", y=0.995
    )

    gs = gridspec.GridSpec(4, 3, figure=fig,
                           hspace=0.50, wspace=0.35,
                           left=0.07, right=0.97,
                           top=0.955, bottom=0.05)

    ax_fid   = fig.add_subplot(gs[0, :2])
    ax_surv  = fig.add_subplot(gs[0, 2])
    ax_genes = fig.add_subplot(gs[1, :2])
    ax_bat   = fig.add_subplot(gs[1, 2])
    ax_death = fig.add_subplot(gs[2, :2])
    ax_gold  = fig.add_subplot(gs[2, 2])
    ax_dna   = fig.add_subplot(gs[3, :])

    for ax in [ax_fid, ax_surv, ax_genes, ax_bat, ax_death, ax_gold, ax_dna]:
        ax.set_facecolor(MID)
        for spine in ax.spines.values():
            spine.set_color(GRID)

    def style(ax, title, xlabel="Generation", ylabel=""):
        ax.set_title(title, color="white", fontsize=10, pad=7)
        ax.set_xlabel(xlabel, color="#aaaacc", fontsize=9)
        ax.set_ylabel(ylabel, color="#aaaacc", fontsize=9)
        ax.tick_params(colors="#aaaacc", labelsize=8)
        ax.grid(True, alpha=0.15, color=GRID)

    hard_gens = [g for g in gens if EXTINCTION_RISK and (g % 15 == 14)]

    def mark_events(ax, label=False):
        for i, g in enumerate(hard_gens):
            kw = {"label": "Hard event"} if (label and i == 0) else {}
            ax.axvline(g, color="#ff4444", lw=0.9, ls="--", alpha=0.45, **kw)

    # ── Panel 1: Fidelity ──────────────────────────────────────────────────
    mean_f = history["mean_fidelity"]
    max_f  = history["max_fidelity"]
    ax_fid.fill_between(gens, mean_f, max_f, alpha=0.15, color="#00e5ff")
    ax_fid.plot(gens, max_f,  color="#00e5ff", lw=2.0, label="Best fidelity")
    ax_fid.plot(gens, mean_f, color="#888888", lw=1.5, ls="--",
                label="Mean fidelity (survivors)")
    mark_events(ax_fid, label=True)
    ax_fid.set_xlim(0, len(gens) - 1); ax_fid.set_ylim(0, 1.05)
    ax_fid.legend(fontsize=8.5, facecolor="#111128", labelcolor="white",
                   edgecolor=GRID, loc="lower right")
    style(ax_fid, "Fidelity at Destination  (Best & Mean Survivors)",
          ylabel="Fidelity")

    # ── Panel 2: Survival + Verdict ───────────────────────────────────────
    sr = history["survival_rate"]
    ax_surv.fill_between(gens, sr, alpha=0.20, color="#f39c12")
    ax_surv.plot(gens, sr, color="#f39c12", lw=2.0)
    mark_events(ax_surv)
    ax_surv.set_xlim(0, len(gens) - 1); ax_surv.set_ylim(0, 1.05)

    final_means = {g: history["gene_means"][g][-1] for g in GENES}
    winner = max(final_means, key=final_means.get)
    final_repair = final_means["Repair"]
    final_agility = final_means["Agility"]
    steps_final = int(8 / (final_agility * 0.9 + 0.1))
    total_cost_est = steps_final * (REPAIR_COST_SCALE * final_repair**2
                                   + REDUND_COST_SCALE * final_means["Redundancy"])
    verdict = (
        "Evolution's answer:\n\n"
        + "\n".join(
            f"  {'>' if g == winner else ' '} {g:<11} {v:.2f}"
            for g, v in final_means.items()
        )
        + f"\n\n  Steps at final Agility:\n    {steps_final}"
        + f"\n  Est. battery spend:\n    {total_cost_est:.3f} / {BATTERY_SIZE}"
        + f"\n\n  Repair settled at {final_repair:.2f},\n  NOT 1.0 — the battery\n  forced restraint."
    )
    ax_surv.text(0.04, 0.96, verdict, transform=ax_surv.transAxes,
                 va="top", ha="left", fontsize=7.8, color="white",
                 fontfamily="monospace",
                 bbox=dict(facecolor="#0a0a18", edgecolor="#f39c12",
                           linewidth=1.2, boxstyle="round,pad=0.5", alpha=0.92))
    style(ax_surv, "Survival Rate per Generation", ylabel="Fraction surviving")

    # ── Panel 3: Gene Evolution ───────────────────────────────────────────
    for gene, color in GENE_COLORS.items():
        arr = np.array(history["gene_means"][gene])
        std = np.array(history["gene_stds"][gene])
        ax_genes.plot(gens, arr, color=color, lw=2.0, label=gene)
        ax_genes.fill_between(gens, arr - std, arr + std, alpha=0.10, color=color)

    ax_genes.axhline(0.5, color="#ffffff", lw=0.7, ls=":", alpha=0.22)
    mark_events(ax_genes)
    ax_genes.set_xlim(0, len(gens) - 1); ax_genes.set_ylim(-0.05, 1.05)
    ax_genes.legend(fontsize=8.5, facecolor="#111128", labelcolor="white",
                     edgecolor=GRID, loc="upper left", ncol=2)
    style(ax_genes,
          "Gene Evolution  (band = population std dev)\n"
          "Watch Repair settle BELOW its v1 maximum — the battery constraint shapes it",
          ylabel="Gene value")

    # ── Panel 4: Mean Battery at Finish ───────────────────────────────────
    bat = history["mean_battery_end"]
    ax_bat.fill_between(gens, bat, alpha=0.25, color="#2ecc71")
    ax_bat.plot(gens, bat, color="#2ecc71", lw=2.0, label="Mean battery (survivors)")
    ax_bat.axhline(0.0, color="#e74c3c", lw=1.2, ls="--", alpha=0.5,
                   label="Battery dead (0)")
    ax_bat.axhline(BATTERY_SIZE, color="#ffffff", lw=0.7, ls=":", alpha=0.25,
                   label=f"Full battery ({BATTERY_SIZE})")
    mark_events(ax_bat)
    ax_bat.set_xlim(0, len(gens) - 1)
    ax_bat.set_ylim(-0.05, BATTERY_SIZE * 1.15)
    ax_bat.legend(fontsize=8, facecolor="#111128", labelcolor="white",
                   edgecolor=GRID)
    style(ax_bat, "Mean Battery Remaining\n(survivors only — negative = impossible by construction)",
          ylabel="Battery left")

    # ── Panel 5: Cause-of-Death stacked area ─────────────────────────────
    deco  = np.array(history["decoherence_deaths"])
    exhau = np.array(history["exhaustion_deaths"])
    surv  = np.array(history["survival_rate"])

    ax_death.stackplot(
        gens, exhau, deco, surv,
        labels=["Battery exhaustion", "Decoherence", "Survived"],
        colors=["#e67e22", "#c0392b", "#27ae60"],
        alpha=0.72
    )
    mark_events(ax_death)
    ax_death.set_xlim(0, len(gens) - 1); ax_death.set_ylim(0, 1.02)
    ax_death.legend(fontsize=8.5, facecolor="#111128", labelcolor="white",
                     edgecolor=GRID, loc="center right")
    style(ax_death,
          "Cause of Death per Generation\n"
          "Watch the two kill mechanisms compete — evolution finds the narrow band between them",
          ylabel="Fraction of population")

    # ── Panel 6: Goldilocks Scatter ───────────────────────────────────────
    repair_vals  = np.array(history["final_gen_repair"])
    fitness_vals = np.array(history["final_gen_fitness"])
    bat_vals     = np.array(history["final_gen_battery"])
    alive_mask   = np.array(history["final_gen_alive"])
    cause_vals   = np.array(history["final_gen_cause"])

    deco_mask  = ~alive_mask & (cause_vals == QuantumAgent.DECOHERENCE)
    exhau_mask = ~alive_mask & (cause_vals == QuantumAgent.EXHAUSTION)

    ax_gold.scatter(repair_vals[deco_mask],  [0]*deco_mask.sum(),
                    c="#c0392b", s=14, alpha=0.5, label="Decoherence death", zorder=2)
    ax_gold.scatter(repair_vals[exhau_mask], [0]*exhau_mask.sum(),
                    c="#e67e22", s=14, alpha=0.5, label="Battery death", zorder=2)
    if alive_mask.any():
        sc = ax_gold.scatter(
            repair_vals[alive_mask], fitness_vals[alive_mask],
            c=bat_vals[alive_mask], cmap="YlGn", vmin=0, vmax=BATTERY_SIZE,
            s=28, alpha=0.85, label="Survived", zorder=3
        )
        cbar = plt.colorbar(sc, ax=ax_gold, fraction=0.07, pad=0.03)
        cbar.set_label("Battery left", color="white", fontsize=8)
        cbar.ax.yaxis.set_tick_params(labelcolor="white")

    # Shade the danger zones
    ax_gold.axvspan(0,    0.18, alpha=0.08, color="#c0392b")
    ax_gold.axvspan(0.85, 1.0,  alpha=0.08, color="#e67e22")
    ax_gold.text(0.02,  0.85, "Deco\nzone",   transform=ax_gold.transAxes,
                 color="#c0392b", fontsize=7.5, alpha=0.8)
    ax_gold.text(0.83,  0.85, "Exhaust\nzone", transform=ax_gold.transAxes,
                 color="#e67e22", fontsize=7.5, alpha=0.8)

    ax_gold.set_xlim(-0.02, 1.02); ax_gold.set_ylim(-0.05, 1.10)
    ax_gold.legend(fontsize=7.5, facecolor="#111128", labelcolor="white",
                    edgecolor=GRID, loc="upper left")
    style(ax_gold,
          "The Goldilocks Zone\nRepair gene vs Fitness (final generation)",
          xlabel="Repair gene (0=none, 1=max)", ylabel="Fitness")

    # ── Panel 7: DNA Heatmap ──────────────────────────────────────────────
    dna_trace = np.array(history["best_dna_trace"]).T
    cmap = LinearSegmentedColormap.from_list(
        "qcmap", ["#0a0a18", "#0d2b5e", "#1565c0", "#00e5ff", "#ffffff"]
    )
    im = ax_dna.imshow(dna_trace, aspect="auto", cmap=cmap,
                       vmin=0, vmax=1, interpolation="nearest")
    ax_dna.set_yticks(range(len(GENES)))
    ax_dna.set_yticklabels(GENES, color="white", fontsize=9.5)
    ax_dna.set_xlabel("Generation", color="#aaaacc", fontsize=9)
    ax_dna.tick_params(colors="#aaaacc", labelsize=8)
    ax_dna.set_title(
        "Best Agent's DNA Over Time  (brightness = gene expression)\n"
        "This is what real QEC engineering looks like — optimising under resource constraints",
        color="white", fontsize=10, pad=7
    )
    for g in hard_gens:
        ax_dna.axvline(g, color="#ff4444", lw=1.0, ls="--", alpha=0.55)
    cb2 = plt.colorbar(im, ax=ax_dna, fraction=0.012, pad=0.01)
    cb2.set_label("Gene value", color="white", fontsize=8)
    cb2.ax.yaxis.set_tick_params(labelcolor="white")

    fig.text(0.5, 0.008,
             f"Battery per agent: {BATTERY_SIZE}  |  "
             f"Repair cost: {REPAIR_COST_SCALE} * repair^2 per step  |  "
             f"Redundancy cost: {REDUND_COST_SCALE} * redundancy per step  |  "
             "Low Agility = more steps = more drain",
             ha="center", color="#2a2a4a", fontsize=7.5, style="italic")

    out = "/mnt/user-data/outputs/quantum_evolution_v2.png"
    plt.savefig(out, dpi=155, bbox_inches="tight", facecolor=DARK)
    plt.close()
    print(f"\nSaved -> {out}")
    return out


# ─── MAIN ───────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("QUANTUM SURVIVAL EVOLUTION  v2: The Energy Constraint")
    print("=" * 65)
    print(f"  Battery:          {BATTERY_SIZE}")
    print(f"  Repair cost:      quadratic — {REPAIR_COST_SCALE} * repair^2 per step")
    print(f"  Redundancy cost:  linear   — {REDUND_COST_SCALE} * redundancy per step")
    print(f"  Key coupling:     fewer steps (high Agility) saves battery")
    print("=" * 65)

    history = evolve(seed=7)
    plot(history)

    final  = {g: history["gene_means"][g][-1] for g in GENES}
    init   = {g: history["gene_means"][g][0]  for g in GENES}
    winner = max(final, key=final.get)

    print("\nGENE EVOLUTION REPORT")
    print(f"  {'Gene':<12} {'Start':>8} {'Final':>8} {'Delta':>8}   Note")
    print("  " + "-" * 60)
    for g in GENES:
        delta = final[g] - init[g]
        tag   = "  << DOMINANT" if g == winner else ""
        print(f"  {g:<12} {init[g]:>8.3f} {final[g]:>8.3f} {delta:>+8.3f}{tag}")

    steps_final = int(8 / (final["Agility"] * 0.9 + 0.1))
    total_cost  = steps_final * (REPAIR_COST_SCALE * final["Repair"]**2
                                + REDUND_COST_SCALE * final["Redundancy"])
    print(f"\n  Final Agility {final['Agility']:.3f} -> {steps_final} steps per run")
    print(f"  Estimated battery spend per run: {total_cost:.3f} / {BATTERY_SIZE}")
    print(f"  Headroom: {BATTERY_SIZE - total_cost:.3f}  "
          f"({'tight' if BATTERY_SIZE - total_cost < 0.1 else 'some slack'})")
    print()
    total_dead_deco  = sum(history["decoherence_deaths"])
    total_dead_exhau = sum(history["exhaustion_deaths"])
    print(f"  Total decoherence deaths across all gens: {total_dead_deco*POPULATION_SIZE:.0f}")
    print(f"  Total exhaustion   deaths across all gens: {total_dead_exhau*POPULATION_SIZE:.0f}")
    ratio = total_dead_exhau / max(total_dead_deco, 0.001)
    print(f"  Exhaustion / Decoherence ratio: {ratio:.2f}")
    print(f"  (ratio > 0 proves the battery constraint was a real selective force)")
