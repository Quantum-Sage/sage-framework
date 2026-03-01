"""
NAKED QUANTUM REALITY CHECK
The Slapstick Solution: Why Even Willow Can't Do It Alone

MODEL NOTES:
  Simplified educational model using "virtual hops":
  - One decoherence event per 100km (one gate operation equivalent)
  - Chip fidelity = probability of surviving each such event
  - Quantum repeaters allow entanglement swapping at each node
  - Without QEC: errors accumulate multiplicatively
  - With QEC: effective per-event error is squared (threshold theorem)

  Same mathematics as the identity persistence simulator —
  just at a different scale (km instead of teleportation hops).
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import warnings
warnings.filterwarnings('ignore')

# ─── CONSTANTS ─────────────────────────────────────────────────────────────
TOTAL_KM          = 11_000
KM_PER_HOP        = 100      # one decoherence event per 100 km
TOTAL_HOPS        = TOTAL_KM // KM_PER_HOP   # 110 hops
PER_SEG_TARGET    = 0.9990
COST_PER_REPEATER = 10_000_000

# ─── CHIPS ─────────────────────────────────────────────────────────────────
CHIPS = {
    "Prototype\n(95%/op)":      {"fidelity": 0.9500, "color": "#e74c3c", "ls": "-"},
    "IBMQ\n(99.0%/op)":         {"fidelity": 0.9900, "color": "#e67e22", "ls": "-"},
    "Willow\n(99.6%/op)":       {"fidelity": 0.9960, "color": "#f39c12", "ls": "-"},
    "Helios\n(99.9%/op)":       {"fidelity": 0.9990, "color": "#8e44ad", "ls": "-"},
    "Willow+QEC\n(99.99%/op)":  {"fidelity": 0.9999, "color": "#00e5ff", "ls": "--"},
}

# ─── MODEL ─────────────────────────────────────────────────────────────────
def max_seg_hops(chip_fidelity, target=PER_SEG_TARGET):
    if chip_fidelity <= 0 or chip_fidelity >= 1.0:
        return TOTAL_HOPS if chip_fidelity >= 1.0 else 0
    n = np.log(target) / np.log(chip_fidelity)
    return max(1, int(np.floor(n)))

def network_stats(chip_fidelity):
    seg_h  = max_seg_hops(chip_fidelity)
    n_segs = int(np.ceil(TOTAL_HOPS / seg_h))
    n_reps = n_segs - 1
    last_h = TOTAL_HOPS - (n_segs - 1) * seg_h
    if last_h <= 0: last_h = seg_h
    fidelity = (chip_fidelity ** seg_h) ** (n_segs - 1) * (chip_fidelity ** last_h)
    cost     = n_reps * COST_PER_REPEATER
    return seg_h * KM_PER_HOP, n_reps, float(fidelity), cost

results = {}
for name, spec in CHIPS.items():
    spacing, n_reps, fid, cost = network_stats(spec["fidelity"])
    results[name] = {"spacing": spacing, "repeaters": n_reps,
                     "fidelity": fid, "cost": cost,
                     "color": spec["color"], "ls": spec["ls"]}

# ─── FIDELITY CURVES ───────────────────────────────────────────────────────
distances = np.linspace(0, TOTAL_KM, 1100)

def fidelity_curve(chip_fidelity, spacing_km):
    seg_h   = max_seg_hops(chip_fidelity)
    spacing = seg_h * KM_PER_HOP
    curve   = np.zeros(len(distances))
    for i, d in enumerate(distances):
        seg_idx   = int(d // spacing) if spacing > 0 else 0
        d_in_seg  = d % spacing if spacing > 0 else d
        if d_in_seg == 0 and d > 0:
            seg_idx -= 1; d_in_seg = spacing
        hops_in   = d_in_seg / KM_PER_HOP
        curve[i]  = (chip_fidelity ** seg_h) ** seg_idx * (chip_fidelity ** hops_in)
    return curve

# ─── PLOT ──────────────────────────────────────────────────────────────────
fig = plt.figure(figsize=(20, 15), facecolor="#080810")
fig.suptitle(
    "THE NAKED QUANTUM REALITY CHECK\n"
    "Why Even Google's Willow Can't Do It Without Error Correction",
    fontsize=17, fontweight="bold", color="white", y=0.99
)

gs = GridSpec(2, 3, figure=fig,
              hspace=0.42, wspace=0.35,
              left=0.07, right=0.97, top=0.92, bottom=0.07)

ax_fid  = fig.add_subplot(gs[0, :2])
ax_cost = fig.add_subplot(gs[0, 2])
ax_rep  = fig.add_subplot(gs[1, 0])
ax_fid2 = fig.add_subplot(gs[1, 1])
ax_txt  = fig.add_subplot(gs[1, 2])

BG = "#0d0d1a"
for ax in [ax_fid, ax_cost, ax_rep, ax_fid2, ax_txt]:
    ax.set_facecolor(BG)
    for spine in ax.spines.values():
        spine.set_color("#2a2a4a")

# Panel 1: Fidelity vs Distance
for name, spec in CHIPS.items():
    r = results[name]
    curve = fidelity_curve(spec["fidelity"], r["spacing"])
    ax_fid.plot(distances, curve * 100, color=r["color"], lw=2.0,
                ls=r["ls"], label=name.replace("\n", " "), alpha=0.9)

ax_fid.axhline(99.9, color="#ffffff", lw=1, ls=":", alpha=0.35, label="99.9% threshold")
ax_fid.axvline(TOTAL_KM, color="#555588", lw=1.2, ls="--", alpha=0.5)
ax_fid.text(10_380, 5, "New York", color="#888899", fontsize=8, rotation=90)
ax_fid.text(150, 5, "Beijing", color="#888899", fontsize=8)
for city, km in [("Moscow", 5_800), ("London", 9_100)]:
    ax_fid.axvline(km, color="#1a1a33", lw=0.8)
    ax_fid.text(km + 80, 30, city, color="#555577", fontsize=7.5, rotation=90)

ax_fid.set_xlim(0, TOTAL_KM); ax_fid.set_ylim(0, 105)
ax_fid.set_xlabel("Distance (km)", color="#aaaacc", fontsize=10)
ax_fid.set_ylabel("Fidelity (%)", color="#aaaacc", fontsize=10)
ax_fid.set_title(
    f"Cumulative Fidelity vs Distance   (Beijing → New York, {TOTAL_KM:,} km)\n"
    f"[1 decoherence event per {KM_PER_HOP} km · fidelity resets at each repeater]",
    color="white", fontsize=11, pad=8)
ax_fid.tick_params(colors="#aaaacc")
ax_fid.legend(fontsize=8.5, facecolor="#111128", labelcolor="white",
               edgecolor="#333355", loc="upper right", ncol=2)

# Helper bar chart
def dark_bars(ax, values, title, ylabel, fmt="{:.0f}"):
    names  = list(results.keys())
    colors = [results[n]["color"] for n in names]
    labels = [n.replace("\n", "\n") for n in names]
    x = np.arange(len(names))
    bars = ax.bar(x, values, color=colors, edgecolor="#1a1a33", lw=0.8, alpha=0.88, width=0.6)
    ax.set_xticks(x); ax.set_xticklabels(labels, fontsize=7.5, color="#ccccee")
    ax.tick_params(colors="#aaaacc", labelsize=8)
    ax.set_title(title, color="white", fontsize=10, pad=6)
    ax.set_ylabel(ylabel, color="#aaaacc", fontsize=8)
    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height()*1.025,
                fmt.format(val), ha="center", va="bottom",
                color="white", fontsize=8.5, fontweight="bold")

names  = list(results.keys())
costs_m = [results[n]["cost"]/1e6 for n in names]
reps    = [results[n]["repeaters"] for n in names]
fids    = [results[n]["fidelity"]*100 for n in names]

# Panel 2: Cost
dark_bars(ax_cost, costs_m, "Network Cost  ($ millions)\n@$10M per Repeater", "$ millions", "${:.0f}M")
ax_cost.set_ylim(0, max(costs_m)*1.35)
# QEC annotation
w_idx = names.index("Willow\n(99.6%/op)")
q_idx = names.index("Willow+QEC\n(99.99%/op)")
factor = round(costs_m[w_idx] / max(costs_m[q_idx], 0.001))
ax_cost.annotate(f"{factor}× cheaper\nwith QEC",
    xy=(q_idx, costs_m[q_idx]),
    xytext=(q_idx - 1.5, costs_m[q_idx] + max(costs_m)*0.3),
    color="#00e5ff", fontsize=8.5, fontweight="bold",
    arrowprops=dict(arrowstyle="->", color="#00e5ff", lw=1.3))

# Panel 3: Repeaters
dark_bars(ax_rep, reps, "Repeaters Required\nBeijing → New York", "Repeater nodes", "{:.0f}")
ax_rep.set_ylim(0, max(reps)*1.3)

# Panel 4: End-to-End Fidelity
dark_bars(ax_fid2, fids, "End-to-End Fidelity  (%)\nBeijing → New York", "Fidelity (%)", "{:.1f}%")
ax_fid2.set_ylim(0, 110)
ax_fid2.axhline(99.9, color="white", lw=1, ls="--", alpha=0.3)

# Panel 5: Verdict
ax_txt.axis("off")
willow     = results["Willow\n(99.6%/op)"]
willow_qec = results["Willow+QEC\n(99.99%/op)"]
helios     = results["Helios\n(99.9%/op)"]
cost_x     = willow["cost"] / max(willow_qec["cost"], 1)
rep_x      = willow["repeaters"] / max(willow_qec["repeaters"], 1)

verdict = (
    "THE VERDICT\n"
    "───────────────────────────────\n\n"
    "Willow  WITHOUT QEC\n"
    f"  Spacing:    {willow['spacing']:,} km\n"
    f"  Repeaters:  {willow['repeaters']}\n"
    f"  Cost:       ${willow['cost']/1e6:.0f}M\n"
    f"  Fidelity:   {willow['fidelity']*100:.1f}%\n\n"
    "Willow  WITH QEC\n"
    f"  Spacing:    {willow_qec['spacing']:,} km\n"
    f"  Repeaters:  {willow_qec['repeaters']}\n"
    f"  Cost:       ${willow_qec['cost']/1e6:.0f}M\n"
    f"  Fidelity:   {willow_qec['fidelity']*100:.2f}%\n\n"
    f"  → {cost_x:.0f}× cheaper\n"
    f"  → {rep_x:.0f}× fewer repeaters\n\n"
    "───────────────────────────────\n"
    "THE PARADOX:\n"
    f"Helios (best hardware):\n"
    f"  ${helios['cost']/1e6:.0f}M · {helios['fidelity']*100:.1f}% fidelity\n\n"
    f"Willow + QEC:\n"
    f"  ${willow_qec['cost']/1e6:.0f}M · {willow_qec['fidelity']*100:.2f}% fidelity\n\n"
    f"QEC beats best hardware\n"
    f"by {helios['cost']//max(willow_qec['cost'],1):.0f}× in cost\n"
    f"AND fidelity.\n\n"
    "───────────────────────────────\n"
    "QEC is not an upgrade.\n"
    "It is the FOUNDATION."
)

ax_txt.text(0.05, 0.98, verdict, transform=ax_txt.transAxes,
            va="top", ha="left", fontsize=8.8, color="white",
            fontfamily="monospace", linespacing=1.55,
            bbox=dict(facecolor="#0a0a18", edgecolor="#00e5ff",
                      linewidth=1.8, boxstyle="round,pad=0.55", alpha=0.95))

fig.text(0.5, 0.003,
    "Pedagogical model: 1 decoherence event per 100km · fidelity resets at each repeater · "
    "same mathematics as identity persistence simulator",
    ha="center", color="#2a2a4a", fontsize=7.5, style="italic")

out = "/mnt/user-data/outputs/naked_quantum_reality.png"
plt.savefig(out, dpi=180, bbox_inches="tight", facecolor="#080810")
plt.close()
print(f"✅  Saved → {out}")

# ─── CONSOLE REPORT ────────────────────────────────────────────────────────
sep = "═" * 76
print()
print(sep)
print("  NAKED QUANTUM REALITY — FULL REPORT")
print(f"  Route: Beijing → New York  ({TOTAL_KM:,} km)  ·  {TOTAL_HOPS} virtual hops")
print(sep)
print(f"  {'Chip':<28} {'Spacing':>9} {'Repeaters':>11} {'Fidelity':>10} {'Cost':>11}")
print("  " + "─" * 72)
for name, r in results.items():
    label = name.replace("\n", " ")
    print(f"  {label:<28} {r['spacing']:>7}km  {r['repeaters']:>11}  "
          f"{r['fidelity']*100:>9.2f}%  ${r['cost']/1e6:>8.0f}M")
print()
print(f"  Willow  w/o QEC → ${willow['cost']/1e6:.0f}M,  {willow['fidelity']*100:.1f}% fidelity")
print(f"  Helios  (best)  → ${helios['cost']/1e6:.0f}M,  {helios['fidelity']*100:.1f}% fidelity")
print(f"  Willow  w/  QEC → ${willow_qec['cost']/1e6:.0f}M,  {willow_qec['fidelity']*100:.2f}% fidelity")
print(f"\n  QEC beats best hardware by {helios['cost']//max(willow_qec['cost'],1):.0f}× in cost AND fidelity.")
print(sep)
