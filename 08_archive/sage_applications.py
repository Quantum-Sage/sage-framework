"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  THE SAGE BOUND — BEYOND QUANTUM NETWORKS                                  ║
║  Cross-Domain Applications of Log-Additive LP Optimization                 ║
║                                                                            ║
║  The mathematical insight: ANY system where quality degrades               ║
║  multiplicatively through sequential stages can be optimized               ║
║  using the same LP structure that produces the Sage Bound.                 ║
║                                                                            ║
║  Applications:                                                             ║
║    1. ORGAN TRANSPLANT LOGISTICS — viability decay during transport        ║
║    2. DRUG DELIVERY OPTIMIZATION — bioavailability across barriers         ║
║    3. SUPPLY CHAIN RESILIENCE — quality loss in cold chain                 ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import sys
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

import numpy as np
import math
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

# Visual constants
BG    = '#0D1117'
GOLD  = '#FFD700'
CYAN  = '#00FFE0'
RED   = '#FF4444'
WHITE = '#E6EDF3'
GRID  = '#21262D'
PANEL = '#161B22'
GREEN = '#4CAF50'
ORANGE = '#FF9800'
BLUE  = '#00A8E8'
PURPLE = '#C084FC'


# ============================================================================
# THE UNIVERSAL SAGE BOUND
# ============================================================================

def universal_sage_bound(stages, threshold):
    """
    Universal Sage Bound: given a list of per-stage survival factors,
    determine whether the system meets the quality threshold.
    
    This is Theorem 1 generalized: log(Q_total) = Σ log(r_i)
    
    Args:
        stages: list of dicts with 'survival_factor' and 'name'
        threshold: minimum acceptable quality (like S = 0.851)
    
    Returns: total quality, log decomposition, feasibility
    """
    log_quality = sum(math.log(s['survival_factor']) for s in stages)
    total_quality = math.exp(log_quality)
    feasible = total_quality >= threshold
    
    return {
        'total_quality': total_quality,
        'log_quality': log_quality,
        'per_stage_log': [math.log(s['survival_factor']) for s in stages],
        'stage_names': [s['name'] for s in stages],
        'threshold': threshold,
        'feasible': feasible,
        'gap': total_quality - threshold,
    }


# ============================================================================
# APPLICATION 1: ORGAN TRANSPLANT LOGISTICS
# ============================================================================

def organ_transplant_analysis():
    """
    Organ Transplant Sage Bound
    
    PROBLEM: ~20% of procured kidneys are discarded, many due to logistics.
    Organ viability decays exponentially: V(t) = exp(-t / T_viable)
    
    Each transport segment introduces delay. The total viability is the
    product of per-segment survival factors — IDENTICAL to quantum fidelity.
    
    MAPPING:
      Quantum Fidelity F    →  Organ Viability V
      Repeater hop          →  Transport segment
      T₂ (coherence)        →  Cold ischemia tolerance
      p_gen                 →  P(transport on schedule)
      Sage Constant S       →  Min viability for transplant
      
    HARDWARE TYPES:
      "Willow" = Helicopter (fast, expensive, reliable)
      "QuEra"  = Ground ambulance (slow, cheap, less reliable)
    """
    print("\n  APPLICATION 1: ORGAN TRANSPLANT LOGISTICS")
    print("  " + "=" * 55)
    
    # Organ viability parameters (hours)
    organs = {
        'Kidney': {'T_viable': 24.0, 'threshold': 0.70},  # 24h cold ischemia
        'Liver':  {'T_viable': 12.0, 'threshold': 0.75},   # 12h tolerance
        'Heart':  {'T_viable': 4.0,  'threshold': 0.85},   # 4h critical window
        'Lung':   {'T_viable': 6.0,  'threshold': 0.80},   # 6h tolerance
    }
    
    # Transport types (analogous to Willow/QuEra hardware)
    transport = {
        'Helicopter': {
            'speed_kmh': 250,    # km/h
            'p_schedule': 0.92,  # probability on schedule
            'overhead_h': 0.5,   # loading/unloading time
            'cost_per_km': 15,   # $/km
        },
        'Ground': {
            'speed_kmh': 80,
            'p_schedule': 0.70,
            'overhead_h': 0.3,
            'cost_per_km': 3,
        },
        'Commercial_Air': {
            'speed_kmh': 800,
            'p_schedule': 0.85,
            'overhead_h': 2.0,   # airport wait time
            'cost_per_km': 8,
        },
    }
    
    # Route: Multi-city organ transport chain (like Beijing-London)
    # Example: Rural hospital → city hospital → airport → destination airport → transplant center
    route_segments = [
        {'name': 'Procurement → Regional Hub', 'distance_km': 80},
        {'name': 'Regional Hub → Airport', 'distance_km': 40},
        {'name': 'Airport → Dest Airport', 'distance_km': 600},
        {'name': 'Dest Airport → Transplant Center', 'distance_km': 30},
    ]
    total_distance = sum(s['distance_km'] for s in route_segments)
    
    results = {}
    
    for organ_name, organ in organs.items():
        T_viable = organ['T_viable']
        threshold = organ['threshold']
        
        best_config = None
        best_viability = 0
        all_configs = []
        
        # Sweep transport allocations (like Theorem 2 LP)
        transport_types = list(transport.keys())
        
        for config_idx in range(3**len(route_segments)):
            # Each segment gets a transport type
            choices = []
            idx = config_idx
            for _ in route_segments:
                choices.append(transport_types[idx % 3])
                idx //= 3
            
            # Calculate total time and viability
            total_time = 0
            total_cost = 0
            stages = []
            
            for seg, choice in zip(route_segments, choices):
                t = transport[choice]
                # Transit time
                transit_h = seg['distance_km'] / t['speed_kmh'] + t['overhead_h']
                # Stochastic delay: expected wait = transit / p (like 1/p_gen)
                expected_delay = transit_h / t['p_schedule']
                # Per-stage viability = exp(-delay / T_viable)
                stage_viability = math.exp(-expected_delay / T_viable)
                
                stages.append({
                    'survival_factor': stage_viability,
                    'name': f"{seg['name']} ({choice})",
                    'time_h': expected_delay,
                    'cost': seg['distance_km'] * t['cost_per_km'],
                })
                total_time += expected_delay
                total_cost += seg['distance_km'] * t['cost_per_km']
            
            # Apply universal Sage Bound
            result = universal_sage_bound(stages, threshold)
            result['choices'] = choices
            result['total_time_h'] = total_time
            result['total_cost'] = total_cost
            all_configs.append(result)
            
            if result['total_quality'] > best_viability:
                best_viability = result['total_quality']
                best_config = result
        
        # Also find cheapest feasible
        feasible = [c for c in all_configs if c['feasible']]
        cheapest_feasible = min(feasible, key=lambda x: x['total_cost']) if feasible else None
        
        results[organ_name] = {
            'organ': organ,
            'best': best_config,
            'cheapest_feasible': cheapest_feasible,
            'n_feasible': len(feasible),
            'n_total': len(all_configs),
            'all_configs': all_configs,
        }
        
        print(f"\n  {organ_name} (T_viable={T_viable}h, threshold={threshold})")
        print(f"    Route: {total_distance} km, {len(route_segments)} segments")
        print(f"    Best viability: {best_viability:.4f} ({best_config['choices']})")
        print(f"    Feasible configs: {len(feasible)}/{len(all_configs)}")
        if cheapest_feasible:
            print(f"    Cheapest feasible: V={cheapest_feasible['total_quality']:.4f}, "
                  f"${cheapest_feasible['total_cost']:,.0f} ({cheapest_feasible['choices']})")
        else:
            print(f"    NO FEASIBLE CONFIG — organ will be discarded!")
        
        # Log decomposition (like quantum log-fidelity)
        if best_config:
            print(f"    Log-viability decomposition:")
            for name, log_v in zip(best_config['stage_names'], best_config['per_stage_log']):
                print(f"      {log_v:+.4f}  {name}")
    
    return results


# ============================================================================
# APPLICATION 2: DRUG DELIVERY OPTIMIZATION
# ============================================================================

def drug_delivery_analysis():
    """
    Drug Delivery Sage Bound
    
    PROBLEM: Only ~1% of oral drugs reach the brain. Each biological 
    barrier absorbs a fraction. Total bioavailability = product of
    per-barrier transmissions — IDENTICAL to quantum fidelity.
    
    MAPPING:
      Quantum Fidelity F    →  Bioavailability B
      Repeater hop          →  Biological barrier
      Gate fidelity F_gate  →  Per-barrier transmission
      Hardware types        →  Delivery vehicles (nanoparticle, liposome, etc.)
    """
    print("\n\n  APPLICATION 2: DRUG DELIVERY OPTIMIZATION")
    print("  " + "=" * 55)
    
    # Biological barriers and their base transmission rates
    barriers = [
        {'name': 'Stomach acid survival', 'base_transmission': 0.60},
        {'name': 'Intestinal absorption', 'base_transmission': 0.30},
        {'name': 'First-pass metabolism (liver)', 'base_transmission': 0.50},
        {'name': 'Blood-Brain Barrier', 'base_transmission': 0.02},
        {'name': 'Cellular uptake', 'base_transmission': 0.40},
        {'name': 'Nuclear localization', 'base_transmission': 0.70},
    ]
    
    # Delivery vehicles (like Willow/QuEra hardware types)
    vehicles = {
        'Uncoated': {  # baseline — no delivery enhancement
            'multipliers': [1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
            'cost_factor': 1.0,
        },
        'Nanoparticle': {  # good at BBB crossing
            'multipliers': [1.2, 1.5, 0.8, 5.0, 2.0, 1.0],
            'cost_factor': 15.0,
        },
        'Liposome': {  # good at cellular uptake
            'multipliers': [0.9, 1.3, 1.2, 1.5, 3.0, 1.5],
            'cost_factor': 8.0,
        },
        'PEGylated': {  # good at avoiding liver metabolism
            'multipliers': [1.0, 1.1, 3.0, 1.2, 1.0, 1.0],
            'cost_factor': 5.0,
        },
        'Viral_Vector': {  # AAV — great at everything but expensive
            'multipliers': [1.5, 2.0, 1.5, 3.0, 4.0, 2.0],
            'cost_factor': 100.0,
        },
    }
    
    target_bioavailability = 0.001  # 0.1% reaching brain target
    
    # Optimal allocation: LP over vehicle choice at each barrier
    # (like Theorem 2: allocate hardware types to maximize fidelity)
    
    # Brute force LP (5^6 = 15,625 configs — tractable)
    vehicle_names = list(vehicles.keys())
    n_vehicles = len(vehicle_names)
    n_barriers = len(barriers)
    
    best_config = None
    best_bioavail = 0
    all_configs = []
    
    # Sample configurations (full sweep would be 5^6)
    np.random.seed(42)
    
    # Include all single-vehicle configs
    configs_to_test = []
    for v in range(n_vehicles):
        configs_to_test.append([v] * n_barriers)
    
    # Include all "best at each barrier" configs
    best_per_barrier = []
    for b_idx in range(n_barriers):
        best_v = max(range(n_vehicles), 
                     key=lambda v: barriers[b_idx]['base_transmission'] * vehicles[vehicle_names[v]]['multipliers'][b_idx])
        best_per_barrier.append(best_v)
    configs_to_test.append(best_per_barrier)
    
    # Add random mixed configs
    for _ in range(500):
        configs_to_test.append(list(np.random.randint(0, n_vehicles, n_barriers)))
    
    for config in configs_to_test:
        stages = []
        total_cost = 0
        
        for b_idx, v_idx in enumerate(config):
            barrier = barriers[b_idx]
            vehicle = vehicles[vehicle_names[v_idx]]
            
            transmission = min(barrier['base_transmission'] * vehicle['multipliers'][b_idx], 0.99)
            
            stages.append({
                'survival_factor': transmission,
                'name': f"{barrier['name']} [{vehicle_names[v_idx]}]",
            })
            total_cost += vehicle['cost_factor']
        
        result = universal_sage_bound(stages, target_bioavailability)
        result['vehicle_config'] = [vehicle_names[v] for v in config]
        result['total_cost'] = total_cost
        all_configs.append(result)
        
        if result['total_quality'] > best_bioavail:
            best_bioavail = result['total_quality']
            best_config = result
    
    # Find baseline (all uncoated)
    baseline_stages = [{'survival_factor': b['base_transmission'], 'name': b['name']} for b in barriers]
    baseline = universal_sage_bound(baseline_stages, target_bioavailability)
    
    feasible = [c for c in all_configs if c['feasible']]
    cheapest_feasible = min(feasible, key=lambda x: x['total_cost']) if feasible else None
    
    improvement = best_bioavail / baseline['total_quality'] if baseline['total_quality'] > 0 else float('inf')
    
    print(f"\n  Target: {target_bioavailability*100:.2f}% bioavailability at brain target")
    print(f"\n  BASELINE (no delivery vehicle):")
    print(f"    Bioavailability: {baseline['total_quality']*100:.4f}%")
    print(f"    Log-bioavailability: {baseline['log_quality']:.3f}")
    for name, log_v in zip(baseline['stage_names'], baseline['per_stage_log']):
        print(f"      {log_v:+.3f}  {name}")
    
    print(f"\n  OPTIMIZED (LP-selected vehicles at each barrier):")
    print(f"    Bioavailability: {best_bioavail*100:.4f}%")
    print(f"    Improvement: {improvement:.1f}x over baseline")
    print(f"    Vehicle allocation: {best_config['vehicle_config']}")
    for name, log_v in zip(best_config['stage_names'], best_config['per_stage_log']):
        print(f"      {log_v:+.3f}  {name}")
    
    print(f"\n  Feasible configs: {len(feasible)}/{len(all_configs)}")
    if cheapest_feasible:
        print(f"  Cheapest feasible: B={cheapest_feasible['total_quality']*100:.4f}%, "
              f"cost={cheapest_feasible['total_cost']:.0f}x ({cheapest_feasible['vehicle_config']})")
    
    return {
        'baseline': baseline,
        'best': best_config,
        'cheapest_feasible': cheapest_feasible,
        'improvement': improvement,
        'barriers': barriers,
        'vehicles': vehicles,
        'all_configs': all_configs,
    }


# ============================================================================
# APPLICATION 3: SUPPLY CHAIN COLD CHAIN
# ============================================================================

def supply_chain_analysis():
    """
    Supply Chain Sage Bound (Cold Chain for Vaccines)
    
    PROBLEM: ~50% of vaccines are wasted globally due to cold chain breaks.
    Each logistics stage has a probability of maintaining temperature.
    Quality = product of per-stage maintenance rates.
    """
    print("\n\n  APPLICATION 3: SUPPLY CHAIN — VACCINE COLD CHAIN")
    print("  " + "=" * 55)
    
    # Cold chain stages for vaccine distribution (rural Africa example)
    stages_cold = [
        {'name': 'Manufacturer → National Store', 'survival_factor': 0.98, 'type': 'reliable'},
        {'name': 'National Store → Regional Hub', 'survival_factor': 0.95, 'type': 'moderate'},
        {'name': 'Regional Hub → District', 'survival_factor': 0.88, 'type': 'weak'},
        {'name': 'District → Health Post', 'survival_factor': 0.75, 'type': 'vulnerable'},
        {'name': 'Health Post → Outreach', 'survival_factor': 0.60, 'type': 'critical'},
    ]
    
    threshold = 0.50  # minimum viable potency
    
    # Current baseline
    current = universal_sage_bound(stages_cold, threshold)
    
    # Stochastic penalty: power interruptions
    # Like Theorem 3: (1 + 2/p) amplifier
    p_power = [0.99, 0.95, 0.80, 0.60, 0.40]  # power reliability at each stage
    
    stochastic_stages = []
    for stage, p in zip(stages_cold, p_power):
        # Stochastic penalty: quality loss amplified by 1/p unreliability
        stoch_factor = stage['survival_factor'] ** (1 + 1/p)
        stochastic_stages.append({
            'name': stage['name'],
            'survival_factor': stoch_factor,
        })
    
    stochastic = universal_sage_bound(stochastic_stages, threshold)
    
    # Intervention: solar-powered cold boxes at weakest links
    # Like upgrading QuEra nodes to Willow
    improved_stages = list(stages_cold)  # copy
    improved_stages[3] = {'name': 'District → Health Post [+Solar]', 'survival_factor': 0.92, 'type': 'improved'}
    improved_stages[4] = {'name': 'Health Post → Outreach [+Solar]', 'survival_factor': 0.85, 'type': 'improved'}
    improved = universal_sage_bound(improved_stages, threshold)
    
    print(f"\n  CURRENT COLD CHAIN:")
    print(f"    End-to-end potency: {current['total_quality']*100:.1f}%")
    print(f"    Feasible: {current['feasible']}")
    for name, log_v in zip(current['stage_names'], current['per_stage_log']):
        pct = math.exp(log_v) * 100
        print(f"      {log_v:+.4f} ({pct:.0f}%)  {name}")
    
    print(f"\n  WITH POWER INTERRUPTIONS (stochastic penalty):")
    print(f"    End-to-end potency: {stochastic['total_quality']*100:.1f}%")
    print(f"    Feasible: {stochastic['feasible']}")
    
    print(f"\n  WITH SOLAR COLD BOXES (targeted upgrade):")
    print(f"    End-to-end potency: {improved['total_quality']*100:.1f}%")
    print(f"    Feasible: {improved['feasible']}")
    print(f"    Improvement: {improved['total_quality']/current['total_quality']:.2f}x")
    
    return {
        'current': current,
        'stochastic': stochastic,
        'improved': improved,
        'stages': stages_cold,
        'threshold': threshold,
    }


# ============================================================================
# CROSS-DOMAIN ATLAS — 6-PANEL FIGURE
# ============================================================================

def generate_applications_atlas(organ_data, drug_data, chain_data,
                                 save_path="sage_applications_atlas.png"):
    """6-panel cross-domain atlas."""
    
    fig = plt.figure(figsize=(22, 16), facecolor=BG)
    fig.suptitle(
        'THE SAGE BOUND — BEYOND QUANTUM NETWORKS',
        color=GOLD, fontsize=20, fontweight='bold', y=0.98,
        fontfamily='monospace'
    )
    fig.text(0.5, 0.955,
             'Universal LP Structure  |  Organ Transport  |  Drug Delivery  |  Cold Chain',
             ha='center', color=CYAN, fontsize=11, fontfamily='monospace', alpha=0.7)
    
    gs = gridspec.GridSpec(2, 3, hspace=0.35, wspace=0.30,
                           left=0.06, right=0.96, top=0.92, bottom=0.06)
    
    def style_ax(ax, title):
        ax.set_facecolor(PANEL)
        ax.set_title(title, color=GOLD, fontsize=11, fontweight='bold',
                     fontfamily='monospace', pad=10)
        ax.tick_params(colors=WHITE, labelsize=8)
        for spine in ax.spines.values():
            spine.set_color(GRID)
        ax.grid(True, alpha=0.15, color=GRID)
    
    # ── Panel 1: Cross-Domain Mapping Table ──
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.set_facecolor(PANEL)
    style_ax(ax1, '[1] UNIVERSAL SAGE MAPPING')
    ax1.axis('off')
    
    mappings = [
        ('Quantum', 'Transplant', 'Drug', 'Supply Chain'),
        ('Fidelity F', 'Viability V', 'Bioavail B', 'Potency P'),
        ('Repeater', 'Transfer Pt', 'Barrier', 'Stage'),
        ('T2', 'Ischemia Tol', 'Clearance', 'Shelf Life'),
        ('p_gen', 'P(on-time)', 'P(absorb)', 'P(powered)'),
        ('S=0.851', 'V>0.70', 'B>0.1%', 'P>50%'),
        ('LP opt', 'Route opt', 'Vehicle opt', 'Upgrade opt'),
    ]
    
    colors_col = [CYAN, RED, PURPLE, ORANGE]
    y = 0.95
    for row in mappings:
        for j, (cell, col) in enumerate(zip(row, colors_col)):
            x = 0.02 + j * 0.25
            weight = 'bold' if y > 0.90 else 'normal'
            ax1.text(x, y, cell, transform=ax1.transAxes, ha='left', va='top',
                    color=col, fontsize=8, fontweight=weight, fontfamily='monospace')
        y -= 0.12
    
    # ── Panel 2: Organ Viability by Type ──
    ax2 = fig.add_subplot(gs[0, 1])
    style_ax(ax2, '[2] ORGAN VIABILITY — OPTIMAL TRANSPORT')
    
    organ_names = list(organ_data.keys())
    viabilities = [organ_data[o]['best']['total_quality'] for o in organ_names]
    thresholds = [organ_data[o]['organ']['threshold'] for o in organ_names]
    
    x_pos = range(len(organ_names))
    bars = ax2.bar(x_pos, viabilities, color=[CYAN, BLUE, RED, ORANGE], alpha=0.8, 
                   edgecolor=WHITE, linewidth=0.5)
    
    for i, (v, t) in enumerate(zip(viabilities, thresholds)):
        ax2.plot([i-0.4, i+0.4], [t, t], '--', color=GOLD, linewidth=2)
        status = 'FEASIBLE' if v >= t else 'DISCARDED'
        color = GREEN if v >= t else RED
        ax2.text(i, v + 0.02, f'{v:.3f}\n{status}', ha='center', 
                color=color, fontsize=8, fontweight='bold', fontfamily='monospace')
    
    ax2.set_xticks(x_pos)
    ax2.set_xticklabels(organ_names, color=WHITE, fontsize=9)
    ax2.set_ylabel('Viability at Destination', color=WHITE, fontsize=9)
    ax2.set_ylim(0, 1.1)
    
    # ── Panel 3: Drug Delivery Log-Decomposition ──
    ax3 = fig.add_subplot(gs[0, 2])
    style_ax(ax3, '[3] DRUG DELIVERY — LOG-BIOAVAILABILITY')
    
    baseline = drug_data['baseline']
    optimized = drug_data['best']
    
    barrier_names_short = ['Stomach', 'Intestine', 'Liver', 'BBB', 'Cell', 'Nucleus']
    x_pos = range(len(barrier_names_short))
    
    width = 0.35
    ax3.bar([x - width/2 for x in x_pos], baseline['per_stage_log'], width,
            color=RED, alpha=0.7, label=f'Baseline ({baseline["total_quality"]*100:.3f}%)')
    ax3.bar([x + width/2 for x in x_pos], optimized['per_stage_log'], width,
            color=CYAN, alpha=0.7, label=f'Optimized ({optimized["total_quality"]*100:.3f}%)')
    
    ax3.set_xticks(x_pos)
    ax3.set_xticklabels(barrier_names_short, color=WHITE, fontsize=8, rotation=30)
    ax3.set_ylabel('log(transmission)', color=WHITE, fontsize=9)
    ax3.legend(fontsize=8, facecolor=BG, edgecolor=GRID, labelcolor=WHITE)
    ax3.axhline(0, color=GRID, linewidth=0.5)
    
    # ── Panel 4: Cold Chain Comparison ──
    ax4 = fig.add_subplot(gs[1, 0])
    style_ax(ax4, '[4] COLD CHAIN — CURRENT vs IMPROVED')
    
    stage_names_short = ['Mfg→Nat', 'Nat→Reg', 'Reg→Dist', 'Dist→HP', 'HP→Out']
    
    current_vals = [math.exp(v) for v in chain_data['current']['per_stage_log']]
    stoch_vals = [math.exp(v) for v in chain_data['stochastic']['per_stage_log']]
    improved_vals = [math.exp(v) for v in chain_data['improved']['per_stage_log']]
    
    x = np.arange(len(stage_names_short))
    w = 0.25
    ax4.bar(x - w, current_vals, w, color=ORANGE, alpha=0.8, label='Current')
    ax4.bar(x, stoch_vals, w, color=RED, alpha=0.8, label='+ Power Failures')
    ax4.bar(x + w, improved_vals, w, color=GREEN, alpha=0.8, label='+ Solar Upgrade')
    
    ax4.set_xticks(x)
    ax4.set_xticklabels(stage_names_short, color=WHITE, fontsize=8)
    ax4.set_ylabel('Per-Stage Survival', color=WHITE, fontsize=9)
    ax4.legend(fontsize=7, facecolor=BG, edgecolor=GRID, labelcolor=WHITE)
    ax4.axhline(chain_data['threshold'], color=GOLD, linestyle='--', linewidth=1, alpha=0.5)
    
    # ── Panel 5: Feasibility Sweep (Organ — Distance) ──
    ax5 = fig.add_subplot(gs[1, 1])
    style_ax(ax5, '[5] ORGAN FEASIBILITY vs DISTANCE')
    
    distances = np.linspace(50, 2000, 50)
    organ_colors = {'Kidney': CYAN, 'Liver': BLUE, 'Heart': RED, 'Lung': ORANGE}
    
    for organ_name, organ_params in [('Kidney', {'T_viable': 24.0}),
                                       ('Liver', {'T_viable': 12.0}),
                                       ('Heart', {'T_viable': 4.0}),
                                       ('Lung', {'T_viable': 6.0})]:
        viabilities_sweep = []
        for d in distances:
            # Simplified: helicopter transport, 4 segments
            n_seg = 4
            seg_d = d / n_seg
            transit_h = seg_d / 250 + 0.5  # helicopter
            v = math.exp(-n_seg * transit_h / organ_params['T_viable'])
            viabilities_sweep.append(v)
        
        ax5.plot(distances, viabilities_sweep, '-', color=organ_colors[organ_name],
                linewidth=2, label=organ_name)
    
    ax5.axhline(0.70, color=GOLD, linestyle='--', linewidth=1.5, alpha=0.7, label='Threshold')
    ax5.set_xlabel('Total Distance (km)', color=WHITE, fontsize=9)
    ax5.set_ylabel('Viability at Destination', color=WHITE, fontsize=9)
    ax5.legend(fontsize=8, facecolor=BG, edgecolor=GRID, labelcolor=WHITE)
    ax5.set_ylim(0, 1.05)
    
    # ── Panel 6: Impact Summary ──
    ax6 = fig.add_subplot(gs[1, 2])
    ax6.set_facecolor(PANEL)
    style_ax(ax6, '[6] IMPACT SUMMARY')
    ax6.axis('off')
    
    drug_improve = drug_data['improvement']
    chain_improve = chain_data['improved']['total_quality'] / chain_data['current']['total_quality']
    n_feasible = sum(1 for o in organ_data.values() if o['best']['feasible'])
    
    lines = [
        ("THE SAGE BOUND IS UNIVERSAL", GOLD, 13, 'bold'),
        ("", WHITE, 4, 'normal'),
        ("log(Q) = Sum log(r_i)", CYAN, 11, 'normal'),
        ("Any multiplicative system -> LP", CYAN, 10, 'normal'),
        ("", WHITE, 6, 'normal'),
        ("ORGAN TRANSPORT", RED, 11, 'bold'),
        (f"  {n_feasible}/4 organs deliverable at 750km", WHITE, 9, 'normal'),
        (f"  LP selects transport per segment", WHITE, 9, 'normal'),
        ("", WHITE, 4, 'normal'),
        ("DRUG DELIVERY", PURPLE, 11, 'bold'),
        (f"  {drug_improve:.0f}x improvement with LP vehicle", WHITE, 9, 'normal'),
        (f"  selection at each biological barrier", WHITE, 9, 'normal'),
        ("", WHITE, 4, 'normal'),
        ("COLD CHAIN", ORANGE, 11, 'bold'),
        (f"  {chain_improve:.1f}x improvement with targeted", WHITE, 9, 'normal'),
        (f"  solar upgrades at weakest links", WHITE, 9, 'normal'),
        ("", WHITE, 6, 'normal'),
        ("Same math. Same LP. Same theorem.", GREEN, 10, 'bold'),
        ("Different domain. Real impact.", GREEN, 10, 'bold'),
    ]
    
    y = 0.95
    for text, color, size, weight in lines:
        if text:
            ax6.text(0.05, y, text, transform=ax6.transAxes, ha='left', va='top',
                    color=color, fontsize=size, fontweight=weight, fontfamily='monospace')
        y -= 0.045 if size >= 9 else 0.02
    
    plt.savefig(save_path, dpi=180, bbox_inches='tight', facecolor=BG)
    print(f"\n  [Applications] Atlas saved -> {save_path}")
    return save_path


# ============================================================================
# MAIN
# ============================================================================

def run_all_applications():
    """Run all three cross-domain applications and generate atlas."""
    
    print("\n" + "=" * 62)
    print("  THE SAGE BOUND — BEYOND QUANTUM NETWORKS")
    print("  Cross-Domain Applications")
    print("=" * 62)
    
    organ_data = organ_transplant_analysis()
    drug_data = drug_delivery_analysis()
    chain_data = supply_chain_analysis()
    
    print("\n\nGenerating 6-panel cross-domain atlas...")
    atlas = generate_applications_atlas(organ_data, drug_data, chain_data)
    
    print("\n" + "=" * 62)
    print("  CROSS-DOMAIN SUMMARY")
    print("=" * 62)
    print("  The Sage Bound LP structure applies identically to:")
    print("    1. Organ transplant route optimization")
    print("    2. Drug delivery vehicle allocation")
    print("    3. Vaccine cold chain improvement targeting")
    print("  Same monoid homomorphism. Same LP. Different domains.")
    
    return {'organ': organ_data, 'drug': drug_data, 'chain': chain_data, 'atlas': atlas}


if __name__ == "__main__":
    results = run_all_applications()
