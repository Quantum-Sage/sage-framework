"""
QUANTUM ARMS RACE: THE GHOST PROTOCOL  v2
─────────────────────────────────────────
Two populations co-evolve simultaneously:

  PREY  — quantum signals trying to survive noise AND avoid interception
  HUNTERS — interceptors that evolve detection skill through natural selection

The forced tradeoffs (v1 had none):
  • High Repair+Redundancy → loud EM signature → easier to detect
  • High Stealth → quiet → survives hunters, but repair is SUPPRESSED by stealth
    (you can't run active QEC and stay invisible — it's thermodynamically loud)
  • Battery constraint from v2 still applies

Hunter co-evolution (v1 was a ratchet, not a race):
  • Hunters breed. High-kill hunters produce offspring.
  • Low-kill hunters die out, even if skilled — skill without captures = no fitness.
  • Hunters also have a FALSE-POSITIVE gene: over-eager hunters waste shots on
    low-signal targets and burn their 'interception budget', lowering total kills.
  • This creates an arms race oscillation — not just a one-way ratchet.

Red Queen Dynamics: Neither side can rest.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.colors import LinearSegmentedColormap
from collections import defaultdict

# ─── CONFIGURATION ──────────────────────────────────────────────────────────
POP_PREY       = 250
POP_HUNT       = 60
GENERATIONS    = 120
BASE_NOISE     = 0.028
MUTATION_PREY  = 0.045
MUTATION_HUNT  = 0.04
ELITE_FRAC     = 0.18

# ── Battery (from v2) ────────────────────────────────────────────────────────
BATTERY        = 0.65
REPAIR_COST    = 0.07   # quadratic per step
REDUND_COST    = 0.03   # linear per step

# ── Hunter budget ────────────────────────────────────────────────────────────
# Each hunter gets N interception shots per generation.
# False-positive shots (mis-targeting low-signal prey) waste the budget.
SHOTS_PER_HUNT = 8

PREY_GENES  = ["Caution", "Agility", "Redundancy", "Repair", "Stealth"]
HUNT_GENES  = ["Sensitivity", "Precision"]  # Sensitivity=detect threshold, Precision=false-pos rate


# ─── PREY ───────────────────────────────────────────────────────────────────
class Prey:
    ALIVE       = "alive"
    DECOHERED   = "decohered"
    CAPTURED    = "captured"
    EXHAUSTED   = "exhausted"

    def __init__(self, dna=None):
        self.dna = np.clip(
            dna if dna is not None else np.random.rand(len(PREY_GENES)), 0, 1
        )
        self.reset()

    def reset(self):
        self.fidelity       = 1.0
        self.alive          = True
        self.status         = self.ALIVE
        self.battery        = BATTERY
        self.battery_at_end = BATTERY
        self.em_signature   = 0.0   # average EM signal emitted during run

    @property
    def caution(self):    return self.dna[0]
    @property
    def agility(self):    return self.dna[1]
    @property
    def redundancy(self): return self.dna[2]
    @property
    def repair(self):     return self.dna[3]
    @property
    def stealth(self):    return self.dna[4]

    def effective_repair(self) -> float:
        """
        Stealth suppresses repair. Running active QEC is thermodynamically loud.
        Max repair is scaled down by stealth level — you can't have both.
        """
        return self.repair * (1.0 - self.stealth * 0.75)

    def run_gauntlet(self) -> float:
        """Run the quantum channel. Returns EM signature emitted (for hunters)."""
        self.reset()

        steps          = int(8 / (self.agility * 0.9 + 0.1))
        noise_per_step = BASE_NOISE * (1.0 - self.caution * 0.75)
        eff_repair     = self.effective_repair()
        repair_bonus   = eff_repair * 0.013
        redund_buf     = self.redundancy * 0.18
        death_thresh   = 0.50 - redund_buf

        battery_dead   = False
        total_signal   = 0.0

        for _ in range(steps):
            # ── Battery ───────────────────────────────────────────────────
            if not battery_dead:
                cost = REPAIR_COST * (eff_repair ** 2) + REDUND_COST * self.redundancy
                self.battery -= cost
                if self.battery <= 0:
                    self.battery  = 0
                    battery_dead  = True
                    death_thresh  = 0.50   # buffer collapses

            # ── Noise ─────────────────────────────────────────────────────
            damage = noise_per_step * np.random.lognormal(0.0, 0.4)
            self.fidelity -= damage

            # ── Repair ────────────────────────────────────────────────────
            if not battery_dead:
                self.fidelity += repair_bonus

            self.fidelity = np.clip(self.fidelity, 0, 1.0)

            # ── EM signature: loud = QEC activity minus stealth cloaking ──
            raw_signal = (self.redundancy * 0.4 + eff_repair * 0.6)
            step_signal = raw_signal * (1.0 - self.stealth * 0.85)
            total_signal += step_signal

            # ── Death ─────────────────────────────────────────────────────
            if self.fidelity < death_thresh:
                self.alive  = False
                self.status = self.EXHAUSTED if battery_dead else self.DECOHERED
                self.fidelity = 0.0
                break

        self.battery_at_end = self.battery
        self.em_signature   = total_signal / max(1, self.dna[1] * 8 + 1)   # normalise
        return self.em_signature

    def fitness(self) -> float:
        if not self.alive:
            return 0.0
        return self.fidelity * (1.0 - self.battery_at_end * 0.12)

    def reproduce(self, partner):
        mask      = np.random.rand(len(PREY_GENES)) > 0.5
        child_dna = np.where(mask, self.dna, partner.dna)
        child_dna += np.random.normal(0, MUTATION_PREY, len(PREY_GENES))
        return Prey(np.clip(child_dna, 0, 1))


# ─── HUNTERS ────────────────────────────────────────────────────────────────
class Hunter:
    def __init__(self, dna=None):
        # DNA: [Sensitivity, Precision]
        # Sensitivity: lower detection threshold → catches stealthier prey
        #              but also fires on lower-signal targets (wastes shots)
        # Precision:   reduces false-positive rate (fires only on real signals)
        #              costs effort — high Precision = slower scan
        self.dna = np.clip(
            dna if dna is not None else np.random.rand(len(HUNT_GENES)), 0, 1
        )
        self.kills         = 0
        self.shots_fired   = 0
        self.shots_wasted  = 0   # false positives

    @property
    def sensitivity(self): return self.dna[0]
    @property
    def precision(self):   return self.dna[1]

    def detection_threshold(self) -> float:
        """Signal level above which this hunter fires."""
        # High sensitivity → lower threshold (catches more, including false positives)
        # High precision   → raises threshold back up selectively
        base_thresh = 1.0 - self.sensitivity * 0.9
        precision_correction = self.precision * 0.3
        return np.clip(base_thresh + precision_correction, 0.05, 0.95)

    def attempt_intercept(self, prey_em: float) -> bool:
        """
        Returns True if hunter fires at this prey signal.
        Whether it's a true kill depends on whether the prey is actually there.
        """
        return prey_em > self.detection_threshold()

    def fitness(self) -> float:
        """Hunters are selected on kills per shot fired (efficiency)."""
        if self.shots_fired == 0:
            return 0.0
        accuracy = self.kills / self.shots_fired
        # Also reward absolute kills (a picky hunter with 0 shots is useless)
        kill_volume = np.tanh(self.kills / 3.0)   # saturates at ~3 kills
        return accuracy * 0.6 + kill_volume * 0.4

    def reproduce(self, partner):
        mask      = np.random.rand(len(HUNT_GENES)) > 0.5
        child_dna = np.where(mask, self.dna, partner.dna)
        child_dna += np.random.normal(0, MUTATION_HUNT, len(HUNT_GENES))
        return Hunter(np.clip(child_dna, 0, 1))


# ─── ARMS RACE ENGINE ───────────────────────────────────────────────────────
def run_arms_race(seed: int = 42):
    rng = np.random.default_rng(seed)
    np.random.seed(seed)

    prey_pop = [Prey()    for _ in range(POP_PREY)]
    hunt_pop = [Hunter()  for _ in range(POP_HUNT)]

    history = {
        # Prey
        "survival_rate":   [],
        "capture_rate":    [],
        "decohere_rate":   [],
        "exhaust_rate":    [],
        "prey_gene_means": defaultdict(list),
        "prey_gene_stds":  defaultdict(list),
        "mean_em_signal":  [],
        "prey_fitness":    [],
        # Hunters
        "hunter_sens":     [],
        "hunter_prec":     [],
        "hunter_kill_eff": [],
        "kill_rate":       [],
        # Arms race trace (stealth vs sensitivity)
        "stealth_vs_sens": [],
    }

    for gen in range(GENERATIONS):

        # ── Phase 1: Prey run the gauntlet → emit EM signatures ───────────
        em_signals = {}
        for prey in prey_pop:
            sig = prey.run_gauntlet()
            em_signals[id(prey)] = sig

        # ── Phase 2: Hunters intercept ────────────────────────────────────
        # Each hunter gets SHOTS_PER_HUNT interception attempts.
        # Hunt order is randomised each gen — no hunter has priority.
        for h in hunt_pop:
            h.kills = 0
            h.shots_fired = 0

        # Build a random scan order: each hunter scans a random subset of alive prey
        alive_prey = [p for p in prey_pop if p.alive]
        rng.shuffle(alive_prey)

        for h in hunt_pop:
            targets = rng.choice(alive_prey,
                                 size=min(SHOTS_PER_HUNT, len(alive_prey)),
                                 replace=False)
            for prey in targets:
                sig = em_signals[id(prey)]
                if h.attempt_intercept(sig):
                    h.shots_fired += 1
                    if prey.alive:   # hasn't been caught by another hunter yet
                        prey.alive  = False
                        prey.status = Prey.CAPTURED
                        h.kills    += 1
                    else:
                        h.shots_wasted += 1  # wasted on already-dead prey

        # ── Phase 3: Record stats ─────────────────────────────────────────
        n      = POP_PREY
        surv   = [p for p in prey_pop if p.alive]
        capt   = [p for p in prey_pop if p.status == Prey.CAPTURED]
        deco   = [p for p in prey_pop if p.status == Prey.DECOHERED]
        exh    = [p for p in prey_pop if p.status == Prey.EXHAUSTED]

        history["survival_rate"].append(len(surv) / n)
        history["capture_rate"].append(len(capt) / n)
        history["decohere_rate"].append(len(deco) / n)
        history["exhaust_rate"].append(len(exh) / n)

        all_prey_dna = np.array([p.dna for p in prey_pop])
        for i, gene in enumerate(PREY_GENES):
            history["prey_gene_means"][gene].append(np.mean(all_prey_dna[:, i]))
            history["prey_gene_stds"][gene].append(np.std(all_prey_dna[:, i]))

        all_em = [em_signals[id(p)] for p in prey_pop]
        history["mean_em_signal"].append(np.mean(all_em))

        hunt_dna = np.array([h.dna for h in hunt_pop])
        history["hunter_sens"].append(np.mean(hunt_dna[:, 0]))
        history["hunter_prec"].append(np.mean(hunt_dna[:, 1]))

        total_kills = sum(h.kills for h in hunt_pop)
        total_shots = sum(h.shots_fired for h in hunt_pop)
        kill_eff    = total_kills / max(total_shots, 1)
        history["hunter_kill_eff"].append(kill_eff)
        history["kill_rate"].append(total_kills / n)

        # Stealth-vs-Sensitivity: the arms race core metric
        prey_stealth  = np.mean(all_prey_dna[:, 4])
        hunt_sens_val = np.mean(hunt_dna[:, 0])
        history["stealth_vs_sens"].append((prey_stealth, hunt_sens_val))

        mean_fit = np.mean([p.fitness() for p in surv]) if surv else 0
        history["prey_fitness"].append(mean_fit)

        print(
            f"Gen {gen:3d}: surv={len(surv):3d}  capt={len(capt):3d}  "
            f"deco={len(deco):3d}  exh={len(exh):3d}  |  "
            f"h_sens={hunt_sens_val:.3f}  h_prec={np.mean(hunt_dna[:,1]):.3f}  "
            f"kill_eff={kill_eff:.2f}  |  "
            f"stealth={prey_stealth:.3f}  em={np.mean(all_em):.3f}"
        )

        if not surv:
            print("EXTINCTION — all prey eliminated")
            break

        # ── Phase 4: Breed prey ───────────────────────────────────────────
        surv.sort(key=lambda p: p.fitness(), reverse=True)
        prey_parents = surv[:max(2, int(POP_PREY * ELITE_FRAC))]
        new_prey     = list(prey_parents[:int(POP_PREY * 0.04)])   # elite carry-over
        while len(new_prey) < POP_PREY:
            p1, p2 = rng.choice(prey_parents, 2, replace=True)
            new_prey.append(p1.reproduce(p2))
        prey_pop = new_prey[:POP_PREY]

        # ── Phase 5: Breed hunters ────────────────────────────────────────
        hunt_pop.sort(key=lambda h: h.fitness(), reverse=True)
        # Kill off the bottom 30% — low-fitness hunters don't survive the gen
        hunt_parents = hunt_pop[:max(2, int(POP_HUNT * 0.70))]
        new_hunt     = list(hunt_parents[:int(POP_HUNT * 0.05)])   # elite carry-over
        while len(new_hunt) < POP_HUNT:
            h1, h2 = rng.choice(hunt_parents, 2, replace=True)
            new_hunt.append(h1.reproduce(h2))
        hunt_pop = new_hunt[:POP_HUNT]

    return history


# ─── PLOTTING ───────────────────────────────────────────────────────────────
def plot(history):
    DARK = "#080810"
    MID  = "#0d0d1a"
    GRID = "#1a1a33"

    PREY_COLORS = {
        "Caution":    "#e74c3c",
        "Agility":    "#3498db",
        "Redundancy": "#00e5ff",
        "Repair":     "#f1c40f",
        "Stealth":    "#9b59b6",
    }

    gens = range(len(history["survival_rate"]))

    fig = plt.figure(figsize=(22, 20), facecolor=DARK)
    fig.suptitle(
        "QUANTUM ARMS RACE: THE GHOST PROTOCOL  v2\n"
        "Co-evolving Prey and Hunters — The Red Queen Never Rests",
        fontsize=16, fontweight="bold", color="white", y=0.995
    )

    gs = gridspec.GridSpec(4, 3, figure=fig,
                           hspace=0.48, wspace=0.34,
                           left=0.07, right=0.97,
                           top=0.957, bottom=0.05)

    ax_death  = fig.add_subplot(gs[0, :2])   # stacked cause-of-death
    ax_race   = fig.add_subplot(gs[0, 2])    # arms race: stealth vs sensitivity
    ax_genes  = fig.add_subplot(gs[1, :2])   # prey gene evolution
    ax_hunt   = fig.add_subplot(gs[1, 2])    # hunter gene evolution
    ax_em     = fig.add_subplot(gs[2, :2])   # EM signal + hunter kill efficiency
    ax_phase  = fig.add_subplot(gs[2, 2])    # phase portrait: stealth vs sens
    ax_trap   = fig.add_subplot(gs[3, :2])   # the stealth-repair trap
    ax_info   = fig.add_subplot(gs[3, 2])    # explanatory text panel

    all_ax = [ax_death, ax_race, ax_genes, ax_hunt, ax_em, ax_phase, ax_trap, ax_info]
    for ax in all_ax:
        ax.set_facecolor(MID)
        for spine in ax.spines.values():
            spine.set_color(GRID)

    def style(ax, title, xlabel="Generation", ylabel=""):
        ax.set_title(title, color="white", fontsize=10, pad=7)
        ax.set_xlabel(xlabel, color="#aaaacc", fontsize=9)
        ax.set_ylabel(ylabel, color="#aaaacc", fontsize=9)
        ax.tick_params(colors="#aaaacc", labelsize=8)
        ax.grid(True, alpha=0.15, color=GRID)

    # ── Panel 1: Stacked Cause-of-Death ───────────────────────────────────
    surv  = history["survival_rate"]
    capt  = history["capture_rate"]
    deco  = history["decohere_rate"]
    exh   = history["exhaust_rate"]

    ax_death.stackplot(
        gens, exh, deco, capt, surv,
        labels=["Battery exhaustion", "Decoherence", "Captured by hunter", "Survived"],
        colors=["#e67e22", "#c0392b", "#8e44ad", "#27ae60"],
        alpha=0.75
    )
    ax_death.set_xlim(0, len(gens) - 1); ax_death.set_ylim(0, 1.02)
    ax_death.legend(fontsize=8.5, facecolor="#111128", labelcolor="white",
                     edgecolor=GRID, loc="center right")
    style(ax_death,
          "Population Fate per Generation\n"
          "Three ways to die: decoherence, battery, or hunters",
          ylabel="Fraction of population")

    # ── Panel 2: Arms Race — stealth vs sensitivity over time ─────────────
    stealth_trace = [sv[0] for sv in history["stealth_vs_sens"]]
    sens_trace    = [sv[1] for sv in history["stealth_vs_sens"]]

    ax_race.plot(gens, stealth_trace, color="#9b59b6", lw=2.2, label="Prey Stealth")
    ax_race.plot(gens, sens_trace,    color="#e74c3c",  lw=2.2, label="Hunter Sensitivity",
                 ls="--")
    ax_race.fill_between(gens,
                         np.array(stealth_trace) - np.array(sens_trace),
                         0, alpha=0.12, color="#9b59b6",
                         label="Prey advantage")
    ax_race.fill_between(gens,
                         0,
                         np.array(stealth_trace) - np.array(sens_trace),
                         alpha=0.12, color="#e74c3c",
                         label="Hunter advantage")
    ax_race.axhline(0.5, color="white", lw=0.6, ls=":", alpha=0.3)
    ax_race.set_xlim(0, len(gens) - 1); ax_race.set_ylim(-0.05, 1.05)
    ax_race.legend(fontsize=7.5, facecolor="#111128", labelcolor="white",
                    edgecolor=GRID, loc="lower right")
    style(ax_race, "The Arms Race\nPrey Stealth vs Hunter Sensitivity",
          ylabel="Gene value")

    # ── Panel 3: Prey Gene Evolution ──────────────────────────────────────
    for gene, color in PREY_COLORS.items():
        arr = np.array(history["prey_gene_means"][gene])
        std = np.array(history["prey_gene_stds"][gene])
        ax_genes.plot(gens, arr, color=color, lw=2.0, label=gene)
        ax_genes.fill_between(gens, arr - std, arr + std, alpha=0.08, color=color)

    ax_genes.axhline(0.5, color="white", lw=0.7, ls=":", alpha=0.25)
    ax_genes.set_xlim(0, len(gens) - 1); ax_genes.set_ylim(-0.05, 1.05)
    ax_genes.legend(fontsize=8.5, facecolor="#111128", labelcolor="white",
                     edgecolor=GRID, loc="upper left", ncol=2)
    style(ax_genes,
          "Prey Gene Evolution  (5 genes — band = std dev)\n"
          "Stealth suppresses effective Repair — watch them trade off",
          ylabel="Gene value")

    # ── Panel 4: Hunter Gene Evolution ────────────────────────────────────
    ax_hunt.plot(gens, history["hunter_sens"], color="#e74c3c", lw=2.2,
                 label="Sensitivity (lower threshold)")
    ax_hunt.plot(gens, history["hunter_prec"], color="#f39c12", lw=2.2,
                 label="Precision (reduces false positives)", ls="--")
    ax_hunt.plot(gens, history["hunter_kill_eff"], color="#2ecc71", lw=1.5,
                 label="Kill efficiency (kills/shots)", ls=":")
    ax_hunt.set_xlim(0, len(gens) - 1); ax_hunt.set_ylim(-0.05, 1.05)
    ax_hunt.legend(fontsize=7.5, facecolor="#111128", labelcolor="white",
                    edgecolor=GRID)
    style(ax_hunt, "Hunter Gene Evolution\n(hunters breed too — low-kill hunters die out)",
          ylabel="Value")

    # ── Panel 5: EM Signal vs Kill Rate ───────────────────────────────────
    ax_em.plot(gens, history["mean_em_signal"], color="#00e5ff", lw=2.0,
               label="Mean prey EM signal")
    ax_em.plot(gens, history["kill_rate"],      color="#e74c3c", lw=2.0,
               label="Kill rate (per gen)", ls="--")
    ax_em.set_xlim(0, len(gens) - 1)
    ax_em.legend(fontsize=8.5, facecolor="#111128", labelcolor="white",
                  edgecolor=GRID, loc="upper right")
    style(ax_em,
          "EM Signal vs Kill Rate\n"
          "As stealth rises, signal drops — hunters must evolve to compensate",
          ylabel="Value")

    # ── Panel 6: Phase Portrait (stealth vs sensitivity) ──────────────────
    # Colour by generation (early=dark, late=bright)
    cmap_phase = plt.cm.plasma
    n_gens = len(stealth_trace)
    for i in range(n_gens - 1):
        t  = i / n_gens
        ax_phase.plot(stealth_trace[i:i+2], sens_trace[i:i+2],
                      color=cmap_phase(t), lw=1.5, alpha=0.8)

    # Start and end markers
    ax_phase.scatter(stealth_trace[0],  sens_trace[0],  c="white", s=60, zorder=5,
                     marker="o", label="Gen 0")
    ax_phase.scatter(stealth_trace[-1], sens_trace[-1], c="#00e5ff", s=80, zorder=5,
                     marker="*", label=f"Gen {n_gens-1}")

    # Diagonal: arms race parity line
    ax_phase.plot([0, 1], [0, 1], color="white", lw=0.7, ls=":", alpha=0.3)
    ax_phase.text(0.72, 0.62, "Parity", color="#555577", fontsize=7.5, rotation=38)

    ax_phase.set_xlim(-0.02, 1.02); ax_phase.set_ylim(-0.02, 1.02)
    ax_phase.set_xlabel("Prey Stealth", color="#aaaacc", fontsize=9)
    ax_phase.set_ylabel("Hunter Sensitivity", color="#aaaacc", fontsize=9)
    ax_phase.tick_params(colors="#aaaacc", labelsize=8)
    ax_phase.grid(True, alpha=0.15, color=GRID)
    ax_phase.legend(fontsize=8, facecolor="#111128", labelcolor="white", edgecolor=GRID)
    sm = plt.cm.ScalarMappable(cmap=cmap_phase, norm=plt.Normalize(0, n_gens))
    cb = plt.colorbar(sm, ax=ax_phase, fraction=0.06, pad=0.02)
    cb.set_label("Generation", color="white", fontsize=8)
    cb.ax.yaxis.set_tick_params(labelcolor="white")
    ax_phase.set_title("Phase Portrait: Arms Race Trajectory\n(colour = time, * = final state)",
                        color="white", fontsize=10, pad=7)

    # ── Panel 7: The Stealth-Repair Trap ─────────────────────────────────
    # Show that effective repair = repair * (1 - stealth * 0.75)
    # As stealth rises, the repair that actually runs drops
    stealth_arr  = np.array(history["prey_gene_means"]["Stealth"])
    repair_arr   = np.array(history["prey_gene_means"]["Repair"])
    eff_repair   = repair_arr * (1.0 - stealth_arr * 0.75)

    ax_trap.plot(gens, repair_arr,  color="#f1c40f", lw=2.0, label="Repair gene (raw)")
    ax_trap.plot(gens, stealth_arr, color="#9b59b6", lw=2.0, label="Stealth gene")
    ax_trap.plot(gens, eff_repair,  color="#ff6b35", lw=2.5, ls="--",
                 label="Effective repair (what actually runs)")
    ax_trap.fill_between(gens, repair_arr, eff_repair, alpha=0.15, color="#e74c3c",
                         label="Repair suppressed by stealth")

    ax_trap.axhline(0.5, color="white", lw=0.6, ls=":", alpha=0.25)
    ax_trap.set_xlim(0, len(gens) - 1); ax_trap.set_ylim(-0.02, 1.05)
    ax_trap.legend(fontsize=8.5, facecolor="#111128", labelcolor="white",
                    edgecolor=GRID, loc="lower left")
    style(ax_trap,
          "The Stealth-Repair Trap\n"
          "Higher stealth suppresses effective QEC — you can hide or you can fix, not both",
          ylabel="Gene / Repair value")

    # ── Panel 8: Explanatory text ─────────────────────────────────────────
    ax_info.axis("off")
    final_stealth = stealth_arr[-1]
    final_sens    = sens_trace[-1]
    final_eff_rep = eff_repair[-1]
    final_surv    = surv[-1]
    advantage     = "PREY" if final_stealth > final_sens else "HUNTERS"

    info = (
        "ARMS RACE SUMMARY\n"
        "─────────────────────────────────\n\n"
        f"Final survival rate:  {final_surv:.0%}\n"
        f"Final stealth:        {final_stealth:.3f}\n"
        f"Final hunter sens:    {final_sens:.3f}\n"
        f"Current advantage:    {advantage}\n\n"
        f"Effective repair:     {final_eff_rep:.3f}\n"
        f"(Stealth cost: -{(repair_arr[-1]-final_eff_rep):.3f})\n\n"
        "─────────────────────────────────\n"
        "THE CORE TRAP:\n\n"
        "To survive hunters,\n"
        "prey raise Stealth.\n\n"
        "But Stealth suppresses\n"
        "active QEC repair.\n\n"
        "So stealthy prey are\n"
        "more vulnerable to\n"
        "decoherence.\n\n"
        "Evolution is forced\n"
        "to choose: hide from\n"
        "the hunter or fight\n"
        "the noise.\n\n"
        "─────────────────────────────────\n"
        "This is the same\n"
        "tradeoff quantum\n"
        "networks face in\n"
        "adversarial channels."
    )
    ax_info.text(0.06, 0.96, info, transform=ax_info.transAxes,
                 va="top", ha="left", fontsize=8.5, color="white",
                 fontfamily="monospace", linespacing=1.6,
                 bbox=dict(facecolor="#0a0a18", edgecolor="#9b59b6",
                           linewidth=1.5, boxstyle="round,pad=0.55", alpha=0.95))

    fig.text(0.5, 0.008,
             "Stealth suppresses effective QEC  |  Hunters breed on kill efficiency  |  "
             "Three death modes compete  |  Phase portrait shows Red Queen dynamics",
             ha="center", color="#2a2a4a", fontsize=7.5, style="italic")

    out = r"C:\Users\tylor\Desktop\quantum_arms_race.png"
    plt.savefig(out, dpi=150, bbox_inches="tight", facecolor=DARK)
    plt.close()
    print(f"\nSaved -> {out}")
    return out


# ─── MAIN ───────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("QUANTUM ARMS RACE: THE GHOST PROTOCOL  v2")
    print("=" * 65)
    print(f"  Prey:     {POP_PREY}  |  Hunters: {POP_HUNT}")
    print(f"  Stealth suppresses repair by up to {0.75:.0%}")
    print(f"  Hunters breed — low-kill hunters die out")
    print(f"  Battery: {BATTERY} per agent")
    print("=" * 65)

    history = run_arms_race(seed=7)
    plot(history)

    # ── Console summary ───────────────────────────────────────────────────
    print("\nPREY GENE EVOLUTION")
    print(f"  {'Gene':<12} {'Start':>8} {'Final':>8} {'Delta':>8}")
    print("  " + "-" * 44)
    for i, gene in enumerate(PREY_GENES):
        start = history["prey_gene_means"][gene][0]
        final = history["prey_gene_means"][gene][-1]
        print(f"  {gene:<12} {start:>8.3f} {final:>8.3f} {final-start:>+8.3f}")

    print("\nHUNTER GENE EVOLUTION")
    for i, gene in enumerate(HUNT_GENES):
        h_arr = {"Sensitivity": history["hunter_sens"],
                 "Precision":   history["hunter_prec"]}[gene]
        print(f"  {gene:<14} {h_arr[0]:>8.3f} -> {h_arr[-1]:>8.3f}  "
              f"({h_arr[-1]-h_arr[0]:>+.3f})")

    stealth_f = history["prey_gene_means"]["Stealth"][-1]
    sens_f    = history["hunter_sens"][-1]
    print(f"\n  Arms race final state: prey stealth={stealth_f:.3f}  "
          f"hunter sensitivity={sens_f:.3f}")
    print(f"  {'PREY winning' if stealth_f > sens_f else 'HUNTERS winning'} "
          f"(gap: {abs(stealth_f - sens_f):.3f})")
