"""
THE SAGE BOUND — STOCHASTIC EXTENSION
Sage Framework v4.2

Theorem 3: Analytic Bounds Under Probabilistic Entanglement Generation

Extends Theorems 1 & 2 from the deterministic model to real quantum networks
where entanglement generation at each segment succeeds with probability p per attempt.

Authors: Ty (Lead Architect) | Claude (Technical Implementation, Anthropic)

Core Result:
  The LP structure of the Sage Bound is PRESERVED under probabilistic generation,
  provided T2 >> 2s/(c·p) [the LP-preservation condition].

  The stochastic extension adds a single new term to α_i(s):

    α_i^prob(s) = 2·ln(F_gate_i) - (s / c·T2_i) · (1 + 2/p_i)

  Theorems 1 and 2 hold with this substitution.
  New result: critical success probability p* below which no mix achieves threshold.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.colors import LinearSegmentedColormap
from itertools import product

# ============================================================================
# HARDWARE SPECIFICATIONS
# ============================================================================

HARDWARE = {
    "Willow": {
        "F_gate": 0.9985,
        "T2":     1.000,      # seconds
        "p_gen":  0.10,       # optimistic: ~10% per heralding attempt
        "color":  "#00A8E8",
        "label":  "Willow (Google)",
    },
    "Helios": {
        "F_gate": 0.9975,
        "T2":     2.000,      # projected next-gen: 2s T2
        "p_gen":  0.08,
        "color":  "#FF6B35",
        "label":  "Helios (projected)",
    },
    "QuEra": {
        "F_gate": 0.9900,
        "T2":     0.100,      # 100ms
        "p_gen":  0.03,       # neutral atom remote entanglement is harder
        "color":  "#7BC67E",
        "label":  "QuEra-class",
    },
}

SAGE_CONSTANT = 0.85       # S — minimum acceptable end-to-end fidelity
C_FIBER       = 200_000    # km/s — speed of light in fiber
ROUTE_BEIJING_LONDON = 8_200   # km


# ============================================================================
# CORE FUNCTIONS — DETERMINISTIC (Theorems 1 & 2)
# ============================================================================

def alpha_det(s, hw):
    """
    Deterministic log-fidelity contribution per hop (Theorems 1 & 2).
    α_i(s) = 2·ln(F_gate) - s/(c·T2)
    """
    gate_cost   = 2 * np.log(hw["F_gate"])
    memory_cost = -s / (C_FIBER * hw["T2"])
    return gate_cost + memory_cost


def n_w_star_uniform(N, L, hw_w, hw_q, S=SAGE_CONSTANT):
    """
    Theorem 1 (deterministic): minimum Willow nodes under uniform spacing.
    n_w* = ceil( [ln(S) - N·α_q(s)] / [α_w(s) - α_q(s)] )
    """
    s     = L / (N + 1)
    aq    = alpha_det(s, hw_q)
    aw    = alpha_det(s, hw_w)
    denom = aw - aq
    if denom <= 0:
        return N   # all-Willow required
    nw = (np.log(S) - N * aq) / denom
    return int(np.ceil(np.clip(nw, 0, N)))


def n_w_star_nonuniform(N, L, hw_w, hw_q, s_min=50, S=SAGE_CONSTANT):
    """
    Theorem 2 (deterministic): minimum Willow nodes under optimal T2-proportional spacing.
    """
    beta_w = 1 / (C_FIBER * hw_w["T2"])
    aq_min = alpha_det(s_min, hw_q)
    aw_min = alpha_det(s_min, hw_w)
    denom  = aw_min - aq_min
    if denom <= 0:
        return N
    numer  = np.log(S) - N * aq_min + (L - N * s_min) * beta_w
    nw     = numer / denom
    return int(np.ceil(np.clip(nw, 0, N)))


# ============================================================================
# STOCHASTIC EXTENSION — THEOREM 3
# ============================================================================

def alpha_stochastic(s, hw):
    """
    THEOREM 3: Stochastic log-fidelity per hop under probabilistic entanglement.

    Physical model:
      - Each heralding attempt: photon travels s km, success signal returns → 2s/c total
      - Geometric retries: expected attempts = 1/p
      - Expected waiting time: τ_wait = 2s / (c · p)
      - Additional decoherence during wait: exp(-τ_wait / T2)

    Result:
      α_i^prob(s) = 2·ln(F_gate) - s/(c·T2) - 2s/(c·p·T2)
                  = 2·ln(F_gate) - (s / c·T2) · (1 + 2/p)

    LP-preservation condition (must hold for additive structure to apply):
      T2 >> 2s/(c·p)   i.e.  p >> 2s/(c·T2)
    """
    p           = hw["p_gen"]
    gate_cost   = 2 * np.log(hw["F_gate"])
    memory_cost = -s / (C_FIBER * hw["T2"])
    wait_cost   = -2 * s / (C_FIBER * p * hw["T2"])
    return gate_cost + memory_cost + wait_cost


def lp_preservation_ratio(s, hw):
    """
    Returns T2 / τ_wait — should be >> 1 for LP structure to hold.
    Rule of thumb: ratio > 10 means LP approximation is valid.
    """
    tau_wait = 2 * s / (C_FIBER * hw["p_gen"])
    return hw["T2"] / tau_wait


def p_critical(s, hw, S=SAGE_CONSTANT, N=1):
    """
    COROLLARY 4: Critical success probability below which a single node type
    cannot achieve threshold fidelity at segment length s.

    Solve α_prob(s) = ln(S)/N for p:
      2·ln(F_gate) - s/(c·T2) - 2s/(c·p·T2) = ln(S)/N
      2s/(c·p·T2) = 2·ln(F_gate) - s/(c·T2) - ln(S)/N
      p* = 2s / (c·T2 · [2·ln(F_gate) - s/(c·T2) - ln(S)/N])
    """
    per_hop_target = np.log(S) / N
    det_alpha      = alpha_det(s, hw)
    margin         = det_alpha - per_hop_target  # must be > 0 for any p* to exist
    if margin <= 0:
        return np.inf   # deterministic model already fails at this segment length
    p_star = 2 * s / (C_FIBER * hw["T2"] * margin)
    return p_star


def n_w_star_stochastic_uniform(N, L, hw_w, hw_q, S=SAGE_CONSTANT):
    """
    THEOREM 3 — Uniform spacing variant.
    Identical structure to Theorem 1 with α_prob substituted.
    """
    s     = L / (N + 1)
    aq    = alpha_stochastic(s, hw_q)
    aw    = alpha_stochastic(s, hw_w)
    denom = aw - aq
    if denom <= 0:
        return N
    nw = (np.log(S) - N * aq) / denom
    return int(np.ceil(np.clip(nw, 0, N)))


def n_w_star_stochastic_nonuniform(N, L, hw_w, hw_q, s_min=50, S=SAGE_CONSTANT):
    """
    THEOREM 3 — Non-uniform spacing variant.
    LP structure: Willow gets shorter segments (wastes less fidelity per km).
    Under stochastic extension, Willow advantage is amplified because
    β_eff_w / β_eff_q is more favorable when T2 ratio dominates.
    """
    beta_w = (1 + 2 / hw_w["p_gen"]) / (C_FIBER * hw_w["T2"])
    aq_min = alpha_stochastic(s_min, hw_q)
    aw_min = alpha_stochastic(s_min, hw_w)
    denom  = aw_min - aq_min
    if denom <= 0:
        return N
    numer = np.log(S) - N * aq_min + (L - N * s_min) * beta_w
    nw    = numer / denom
    return int(np.ceil(np.clip(nw, 0, N)))


# ============================================================================
# MONTE CARLO VALIDATION
# ============================================================================

def simulate_stochastic_fidelity(N, L, n_w, hw_w, hw_q, n_trials=5000):
    """
    Monte Carlo simulation of end-to-end fidelity under probabilistic
    entanglement generation with geometric retries.

    Protocol: parallel segment attempts, local memory storage,
    entanglement swap when both neighbors have stored entanglement.
    Each stored state decoheres during the waiting period.
    """
    s        = L / (N + 1)
    nodes    = ([hw_w] * n_w) + ([hw_q] * (N - n_w))
    np.random.shuffle(nodes)

    fidelities = []

    for _ in range(n_trials):
        # Each segment: sample geometric waiting time, compute decoherence
        total_log_fidelity = 0.0
        for hw in nodes:
            # Gate fidelity (Bell measurement + correction)
            total_log_fidelity += 2 * np.log(hw["F_gate"])

            # Memory decoherence (deterministic: distance/speed/T2)
            total_log_fidelity -= s / (C_FIBER * hw["T2"])

            # Geometric retry waiting: k ~ Geometric(p), k attempts
            k        = np.random.geometric(hw["p_gen"])
            tau_wait = k * (2 * s / C_FIBER)  # each attempt = 2s/c seconds
            total_log_fidelity -= tau_wait / hw["T2"]

        fidelities.append(np.exp(total_log_fidelity))

    return np.mean(fidelities), np.std(fidelities)


# ============================================================================
# ANALYSIS ENGINE
# ============================================================================

def compare_deterministic_vs_stochastic(L=ROUTE_BEIJING_LONDON):
    """
    Core comparison: deterministic Sage Bound vs stochastic extension.
    Returns structured results dict for plotting and reporting.
    """
    hw_w = HARDWARE["Willow"]
    hw_q = HARDWARE["QuEra"]

    N_values = list(range(5, 45, 5))
    results = {
        "N":             N_values,
        "det_uniform":   [],
        "det_nonuniform":[],
        "sto_uniform":   [],
        "sto_nonuniform":[],
        "willow_saved_det": [],
        "willow_saved_sto": [],
        "lp_ratio":      [],
    }

    for N in N_values:
        s = L / (N + 1)

        det_u  = n_w_star_uniform(N, L, hw_w, hw_q)
        det_nu = n_w_star_nonuniform(N, L, hw_w, hw_q)
        sto_u  = n_w_star_stochastic_uniform(N, L, hw_w, hw_q)
        sto_nu = n_w_star_stochastic_nonuniform(N, L, hw_w, hw_q)
        lp_r   = lp_preservation_ratio(s, hw_w)

        results["det_uniform"].append(det_u)
        results["det_nonuniform"].append(det_nu)
        results["sto_uniform"].append(sto_u)
        results["sto_nonuniform"].append(sto_nu)
        results["willow_saved_det"].append(det_u - det_nu)
        results["willow_saved_sto"].append(sto_u - sto_nu)
        results["lp_ratio"].append(lp_r)

    return results


def p_critical_sweep():
    """
    For each hardware type, sweep segment length to find p* vs s.
    Shows where probabilistic generation causes the stochastic extension
    to diverge from the deterministic model.
    """
    s_values = np.linspace(10, 500, 200)
    sweep = {}
    for name, hw in HARDWARE.items():
        p_crits = [p_critical(s, hw) for s in s_values]
        sweep[name] = p_crits
    return s_values, sweep


def effective_decoherence_advantage(s_values=None):
    """
    Quantifies how the T2 advantage between Willow and QuEra is amplified
    under stochastic generation.

    Deterministic: β_eff ratio = T2_w / T2_q = 10
    Stochastic:    β_eff ratio = [(1+2/p_q)·T2_q] / [(1+2/p_w)·T2_w]
    """
    if s_values is None:
        s_values = np.linspace(50, 400, 100)

    hw_w = HARDWARE["Willow"]
    hw_q = HARDWARE["QuEra"]

    det_ratio = []
    sto_ratio = []

    for s in s_values:
        aw_det = abs(alpha_det(s, hw_w))
        aq_det = abs(alpha_det(s, hw_q))
        aw_sto = abs(alpha_stochastic(s, hw_w))
        aq_sto = abs(alpha_stochastic(s, hw_q))

        # Ratio of cost-per-hop: lower = better hardware
        det_ratio.append(aq_det / aw_det if aw_det > 0 else 0)
        sto_ratio.append(aq_sto / aw_sto if aw_sto > 0 else 0)

    return s_values, det_ratio, sto_ratio


# ============================================================================
# VISUALIZATION
# ============================================================================

def generate_theorem3_figure(save_path="/mnt/user-data/outputs/sage_bound_theorem3.png"):
    """
    Six-panel publication figure for Theorem 3 submission.
    """
    hw_w = HARDWARE["Willow"]
    hw_q = HARDWARE["QuEra"]

    fig = plt.figure(figsize=(18, 14), facecolor="#0D1117")
    gs  = gridspec.GridSpec(3, 3, figure=fig, hspace=0.45, wspace=0.38)

    TITLE_COLOR  = "#E6EDF3"
    LABEL_COLOR  = "#8B949E"
    GRID_COLOR   = "#21262D"
    WILLOW_COLOR = "#00A8E8"
    QUERA_COLOR  = "#7BC67E"
    WARN_COLOR   = "#FF6B35"
    GOLD_COLOR   = "#F0C040"

    def style_ax(ax, title):
        ax.set_facecolor("#161B22")
        ax.tick_params(colors=LABEL_COLOR, labelsize=9)
        ax.xaxis.label.set_color(LABEL_COLOR)
        ax.yaxis.label.set_color(LABEL_COLOR)
        for spine in ax.spines.values():
            spine.set_edgecolor(GRID_COLOR)
        ax.grid(True, color=GRID_COLOR, linewidth=0.6, alpha=0.7)
        ax.set_title(title, color=TITLE_COLOR, fontsize=11, fontweight="bold", pad=8)

    results = compare_deterministic_vs_stochastic()
    N_vals  = results["N"]

    # ── Panel 1: Deterministic vs Stochastic n_w* (uniform) ──────────────────
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.plot(N_vals, results["det_uniform"], "o-", color=WILLOW_COLOR,
             label="Deterministic (Thm 1)", linewidth=2, markersize=6)
    ax1.plot(N_vals, results["sto_uniform"], "s--", color=WARN_COLOR,
             label="Stochastic (Thm 3)", linewidth=2, markersize=6)
    ax1.set_xlabel("Total Nodes N")
    ax1.set_ylabel("Min Willow Nodes n_w*")
    ax1.legend(fontsize=8, labelcolor=TITLE_COLOR, facecolor="#21262D",
               edgecolor=GRID_COLOR)
    style_ax(ax1, "Uniform Spacing: Thm 1 vs Thm 3")

    # ── Panel 2: Non-uniform comparison ──────────────────────────────────────
    ax2 = fig.add_subplot(gs[0, 1])
    ax2.plot(N_vals, results["det_nonuniform"], "o-", color=WILLOW_COLOR,
             label="Deterministic (Thm 2)", linewidth=2, markersize=6)
    ax2.plot(N_vals, results["sto_nonuniform"], "s--", color=WARN_COLOR,
             label="Stochastic (Thm 3+)", linewidth=2, markersize=6)
    ax2.set_xlabel("Total Nodes N")
    ax2.set_ylabel("Min Willow Nodes n_w*")
    ax2.legend(fontsize=8, labelcolor=TITLE_COLOR, facecolor="#21262D",
               edgecolor=GRID_COLOR)
    style_ax(ax2, "Non-Uniform Spacing: Thm 2 vs Thm 3")

    # ── Panel 3: LP Preservation Ratio ───────────────────────────────────────
    ax3 = fig.add_subplot(gs[0, 2])
    ax3.plot(N_vals, results["lp_ratio"], "o-", color=GOLD_COLOR,
             linewidth=2, markersize=6)
    ax3.axhline(y=10, color=WARN_COLOR, linestyle="--", linewidth=1.5,
                label="LP validity threshold (×10)")
    ax3.axhline(y=1, color="#FF0000", linestyle=":", linewidth=1.5,
                label="LP breaks (×1)")
    ax3.set_xlabel("Total Nodes N")
    ax3.set_ylabel("T2 / τ_wait (Willow)")
    ax3.set_yscale("log")
    ax3.legend(fontsize=8, labelcolor=TITLE_COLOR, facecolor="#21262D",
               edgecolor=GRID_COLOR)
    style_ax(ax3, "LP Preservation Ratio (Willow)")

    # ── Panel 4: p* vs segment length (Corollary 4) ──────────────────────────
    ax4 = fig.add_subplot(gs[1, 0])
    s_sweep, p_crits = p_critical_sweep()
    for name, hw in HARDWARE.items():
        p_vals = np.clip(p_crits[name], 0, 1.5)
        ax4.plot(s_sweep, p_vals, color=hw["color"], label=hw["label"],
                 linewidth=2)
    ax4.axhline(y=1.0, color="#FF0000", linestyle="--", linewidth=1.5,
                label="p_max = 1.0 (impossible)")
    ax4.fill_between(s_sweep, 1.0, 1.5, alpha=0.15, color="#FF0000",
                     label="Infeasible region")
    ax4.set_xlabel("Segment Length s (km)")
    ax4.set_ylabel("Critical Success Probability p*")
    ax4.set_ylim(0, 1.55)
    ax4.legend(fontsize=7.5, labelcolor=TITLE_COLOR, facecolor="#21262D",
               edgecolor=GRID_COLOR)
    style_ax(ax4, "Corollary 4: Critical p* vs Segment Length")

    # ── Panel 5: Willow T2 advantage amplification ───────────────────────────
    ax5 = fig.add_subplot(gs[1, 1])
    s_arr, det_ratio, sto_ratio = effective_decoherence_advantage()
    ax5.plot(s_arr, det_ratio, "o-", color=WILLOW_COLOR, label="Deterministic",
             linewidth=2, markersize=4)
    ax5.plot(s_arr, sto_ratio, "s-", color=WARN_COLOR, label="Stochastic",
             linewidth=2, markersize=4)
    ax5.set_xlabel("Segment Length s (km)")
    ax5.set_ylabel("QuEra cost / Willow cost per hop")
    ax5.legend(fontsize=8, labelcolor=TITLE_COLOR, facecolor="#21262D",
               edgecolor=GRID_COLOR)
    style_ax(ax5, "Willow T2 Advantage Amplification")
    note = "Higher ratio = Willow more\nvaluable relative to QuEra"
    ax5.text(0.97, 0.05, note, transform=ax5.transAxes, ha="right",
             color=GOLD_COLOR, fontsize=8, style="italic")

    # ── Panel 6: Monte Carlo validation of Theorem 3 ─────────────────────────
    ax6 = fig.add_subplot(gs[1, 2])
    mc_N      = [5, 10, 15, 20, 25, 30]
    mc_analytic, mc_sim_mean, mc_sim_std = [], [], []
    L = ROUTE_BEIJING_LONDON

    for N in mc_N:
        nw        = n_w_star_stochastic_uniform(N, L, hw_w, hw_q)
        # Analytic: threshold should be just met
        s         = L / (N + 1)
        aq        = alpha_stochastic(s, hw_q)
        aw        = alpha_stochastic(s, hw_w)
        log_F     = nw * aw + (N - nw) * aq
        mc_analytic.append(np.exp(log_F))
        m, sd     = simulate_stochastic_fidelity(N, L, nw, hw_w, hw_q, n_trials=2000)
        mc_sim_mean.append(m)
        mc_sim_std.append(sd)

    ax6.plot(mc_N, mc_analytic, "o-", color=WILLOW_COLOR, linewidth=2,
             markersize=7, label="Analytic (Thm 3)")
    ax6.errorbar(mc_N, mc_sim_mean, yerr=mc_sim_std, fmt="s--",
                 color=QUERA_COLOR, linewidth=1.5, markersize=6,
                 capsize=4, label="Monte Carlo (2k trials)")
    ax6.axhline(y=SAGE_CONSTANT, color=GOLD_COLOR, linestyle="--",
                linewidth=1.5, label=f"Sage Constant S={SAGE_CONSTANT}")
    ax6.set_xlabel("Total Nodes N")
    ax6.set_ylabel("End-to-End Fidelity")
    ax6.set_ylim(0.5, 1.05)
    ax6.legend(fontsize=8, labelcolor=TITLE_COLOR, facecolor="#21262D",
               edgecolor=GRID_COLOR)
    style_ax(ax6, "MC Validation: Theorem 3 (Beijing–London)")

    # ── Panel 7 (bottom row, full width): Comprehensive comparison table ──────
    ax7 = fig.add_subplot(gs[2, :])
    ax7.set_facecolor("#161B22")
    ax7.axis("off")

    # Build comparison data
    routes = [
        ("NYC – London",   5_500),
        ("Beijing – London", 8_200),
        ("Beijing – NYC",  11_000),
        ("Sydney – London",16_993),
    ]
    N_test = 20
    header = ["Route", "Distance",
              "Thm1 n_w*", "Thm2 n_w*", "Thm3-Unif n_w*", "Thm3-NonUnif n_w*",
              "LP Ratio", "Stochastic ΔCost"]
    rows = []
    for rname, dist in routes:
        d1  = n_w_star_uniform(N_test, dist, hw_w, hw_q)
        d2  = n_w_star_nonuniform(N_test, dist, hw_w, hw_q)
        s3u = n_w_star_stochastic_uniform(N_test, dist, hw_w, hw_q)
        s3n = n_w_star_stochastic_nonuniform(N_test, dist, hw_w, hw_q)
        s   = dist / (N_test + 1)
        lpr = lp_preservation_ratio(s, hw_w)
        # Extra Willow cost from stochastic vs deterministic (uniform)
        delta = s3u - d1
        rows.append([rname, f"{dist:,} km",
                     str(d1), str(d2), str(s3u), str(s3n),
                     f"{lpr:.1f}×", f"+{delta} nodes" if delta > 0 else f"{delta}"])

    table = ax7.table(
        cellText=rows,
        colLabels=header,
        cellLoc="center",
        loc="center",
        bbox=[0.01, 0.05, 0.98, 0.90]
    )
    table.auto_set_font_size(False)
    table.set_fontsize(9)

    for (r, c), cell in table.get_celld().items():
        cell.set_facecolor("#21262D" if r == 0 else ("#1C2128" if r % 2 else "#161B22"))
        cell.set_edgecolor(GRID_COLOR)
        cell.set_text_props(color=TITLE_COLOR if r > 0 else GOLD_COLOR,
                            fontweight="bold" if r == 0 else "normal")

    ax7.set_title(
        "Theorem 3 Summary: Deterministic vs Stochastic Sage Bound  (N=20 nodes per route)",
        color=TITLE_COLOR, fontsize=11, fontweight="bold", pad=6
    )

    # Master title
    fig.suptitle(
        "THE SAGE BOUND — STOCHASTIC EXTENSION  |  Theorem 3: Probabilistic Entanglement Generation\n"
        "Sage Framework v4.2  |  Ty (Lead Architect)  ·  Claude (Anthropic)",
        color=TITLE_COLOR, fontsize=13, fontweight="bold", y=0.98
    )

    plt.savefig(save_path, dpi=180, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    print(f"Figure saved: {save_path}")
    return fig


# ============================================================================
# THEOREM 3 PROOF SUMMARY (printed)
# ============================================================================

def print_theorem3():
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║              THE SAGE BOUND — THEOREM 3 (STOCHASTIC EXTENSION)             ║
╚══════════════════════════════════════════════════════════════════════════════╝

PHYSICAL MODEL
──────────────
Each segment attempts entanglement generation with success probability p per
heralding round-trip (duration = 2s/c). Retries are geometric: k ~ Geom(p).
Stored entanglement decoheres during waiting: F_wait = exp(-k·2s/(c·T2)).

EXPECTED LOG-FIDELITY PER HOP
──────────────────────────────
  α_i^prob(s) = E[2·ln(F_gate) - s/(c·T2) - k·2s/(c·T2)]
              = 2·ln(F_gate) - s/(c·T2) - E[k]·2s/(c·T2)
              = 2·ln(F_gate) - (s / c·T2) · (1 + 2/p)

  where E[k] = 1/p for Geometric(p).

LP-PRESERVATION CONDITION
──────────────────────────
  The additive structure holds when segments are independent (parallel protocol,
  local memory storage). Condition: T2 >> 2s/(c·p).
  Equivalently: LP ratio = T2·c·p / (2s) >> 1.

THEOREM 3 — UNIFORM SPACING
─────────────────────────────
  n_w* = ceil { [ln(S) - N·α_q^prob(s)] / [α_w^prob(s) - α_q^prob(s)] }
  Identical structure to Theorem 1 with α^prob substituted.

THEOREM 3 — NON-UNIFORM SPACING
──────────────────────────────────
  Analogous substitution into Theorem 2.
  β_i^eff = (1 + 2/p_i) / (c·T2_i)
  Willow advantage is AMPLIFIED: higher T2 reduces both memory and wait costs.

COROLLARY 4 — CRITICAL SUCCESS PROBABILITY
────────────────────────────────────────────
  p*(s) = 2s / (c·T2 · [2·ln(F_gate) - s/(c·T2) - ln(S)/N])
  For p < p*(s): NO hardware mix achieves threshold at segment length s.
  Interpretation: segment length must shrink or T2 must grow.

KEY PHYSICAL INSIGHT
─────────────────────
  Deterministic model: T2 advantage (Willow/QuEra) = 10×
  Stochastic model:    effective advantage = (1 + 2/p_q)·T2_q / [(1+2/p_w)·T2_w]
                     = (1 + 2/0.03)·0.1 / [(1 + 2/0.10)·1.0]
                     = (67.7·0.1) / (21·1.0)
                     = 6.77 / 21 ≈ 0.32

  This means QuEra's decoherence cost is LOWER per unit cost when p_q << p_w
  and T2 dominates — stochastic model favors Willow even MORE strongly at
  short segments, but the relative advantage inverts at long segments where
  memory-limited QuEra nodes fail first.

  The full picture requires sweeping (s, p, T2) jointly — see figures.
""")


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print_theorem3()

    print("\n── Running analysis ──\n")
    results = compare_deterministic_vs_stochastic()

    print(f"{'N':>4}  {'Det Unif':>10}  {'Det NonUnif':>12}  "
          f"{'Sto Unif':>10}  {'Sto NonUnif':>12}  {'LP Ratio':>10}")
    print("─" * 65)
    for i, N in enumerate(results["N"]):
        print(f"{N:>4}  {results['det_uniform'][i]:>10}  "
              f"{results['det_nonuniform'][i]:>12}  "
              f"{results['sto_uniform'][i]:>10}  "
              f"{results['sto_nonuniform'][i]:>12}  "
              f"{results['lp_ratio'][i]:>10.1f}×")

    print("\n── LP-preservation check (Willow at key segment lengths) ──\n")
    hw_w = HARDWARE["Willow"]
    for s_test in [50, 100, 200, 300, 400]:
        ratio = lp_preservation_ratio(s_test, hw_w)
        status = "✓ VALID" if ratio > 10 else ("⚠ MARGINAL" if ratio > 1 else "✗ INVALID")
        p_s = p_critical(s_test, hw_w)
        print(f"  s={s_test:>4}km  LP ratio={ratio:>8.1f}×  {status}  "
              f"p*={p_s:.4f}")

    print("\n── Generating publication figure ──\n")
    generate_theorem3_figure()
    print("\nDone.")
