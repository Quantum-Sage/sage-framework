"""
QUANTUM TELEPORTATION MASTERCLASS
The most mind-bending protocol in quantum mechanics

This is NOT Star Trek teleportation - it's even weirder!
- The original state is DESTROYED (No-Cloning Theorem)
- Nothing travels faster than light (classical bits needed)
- But quantum information is perfectly transferred
"""

import random
import math

def show_teleportation_circuit():
    """
    Shows the famous quantum teleportation circuit
    """
    print("=" * 80)
    print("📊 QUANTUM TELEPORTATION CIRCUIT (Bennett et al., 1993)")
    print("=" * 80)
    print()
    print("Alice's side                      Bob's side (far away)")
    print("-" * 80)
    print("|ψ⟩ (the state)  ──────┬───────M──── (bit 1) ──→ classical channel")
    print("                       │        │")
    print("                     CNOT       │")
    print("                       │        │")
    print("|0⟩ (Alice's half) ───X────H───M──── (bit 2) ──→ classical channel")
    print("                                         ↓")
    print("|0⟩ (Bob's half)   ────────────────────[Apply corrections]───→ |ψ⟩")
    print("-" * 80)
    print()
    print("KEY STEPS:")
    print("  1. Create entangled pair (Alice & Bob each get one qubit)")
    print("  2. Alice does Bell measurement on her state + her half of pair")
    print("  3. Alice gets 2 classical bits (00, 01, 10, or 11)")
    print("  4. Alice sends bits to Bob via normal communication")
    print("  5. Bob applies corrections based on bits")
    print("  6. Bob now has the original state!")
    print()
    print("⚠️  CRITICAL: Alice's original state is DESTROYED in step 2")
    print("    This preserves the No-Cloning Theorem")
    print()

def show_correction_table():
    """
    Shows all possible measurement outcomes and Bob's corrections
    """
    print("=" * 80)
    print("📋 CORRECTION TABLE - All 4 Possible Outcomes")
    print("=" * 80)
    print()
    print("Alice's Measurement  │  Bob's Corrections  │  Gate Operations")
    print("─────────────────────┼────────────────────┼──────────────────")
    print("    00 (25%)         │  Do nothing        │  I (Identity)")
    print("    01 (25%)         │  Flip bit          │  X (NOT gate)")
    print("    10 (25%)         │  Flip phase        │  Z (Phase flip)")
    print("    11 (25%)         │  Both              │  X then Z")
    print()
    print("All outcomes are equally likely and RANDOM!")
    print("But Bob can always reconstruct the state perfectly.")
    print()

def quantum_teleportation_detailed(state_description="secret thought"):
    """
    Step-by-step quantum teleportation with full state tracking
    """
    print("=" * 80)
    print(f"🚀 TELEPORTING: '{state_description}'")
    print("=" * 80)
    print()
    
    # Randomly generate the quantum state Alice wants to send
    # In reality this would be a superposition like α|0⟩ + β|1⟩
    alpha = random.uniform(0, 1)
    beta = math.sqrt(1 - alpha**2)
    
    print("STEP 1: Alice's Original State")
    print("-" * 80)
    print(f"|ψ⟩ = {alpha:.3f}|0⟩ + {beta:.3f}|1⟩")
    print(f"This is a quantum superposition - Alice doesn't know which it will be!")
    print()
    
    print("STEP 2: Create Entangled Pair (The Bridge)")
    print("-" * 80)
    print("Generate Bell pair: (|00⟩ + |11⟩)/√2")
    print("Alice gets qubit A, Bob gets qubit B")
    print("They are now entangled - perfectly correlated!")
    print()
    
    print("STEP 3: Alice's Bell Measurement")
    print("-" * 80)
    print("Alice entangles her state |ψ⟩ with her half of the Bell pair")
    print("Then measures both qubits in the Bell basis...")
    print()
    
    # Simulate the measurement - get 2 random bits
    bit1 = random.randint(0, 1)
    bit2 = random.randint(0, 1)
    
    print(f"💥 MEASUREMENT RESULT: {bit1}{bit2}")
    print()
    print("⚠️  CRITICAL MOMENT:")
    print("   • Alice's original state |ψ⟩ is now DESTROYED")
    print("   • This is required by the No-Cloning Theorem")
    print("   • We can't copy quantum information!")
    print()
    
    print("STEP 4: Classical Communication")
    print("-" * 80)
    print(f"Alice calls Bob (or emails, or mails a letter): '{bit1}{bit2}'")
    print("⏱️  This step is LIMITED by speed of light!")
    print("   (No faster-than-light communication possible)")
    print()
    
    print("STEP 5: Bob's Correction")
    print("-" * 80)
    print(f"Bob receives: {bit1}{bit2}")
    print("Bob's qubit is currently in a 'scrambled' version of |ψ⟩")
    print()
    
    # Determine what Bob needs to do
    if bit1 == 0 and bit2 == 0:
        print("→ Bob does: NOTHING (Identity gate)")
        correction = "I"
    elif bit1 == 0 and bit2 == 1:
        print("→ Bob applies: X gate (bit flip)")
        correction = "X"
    elif bit1 == 1 and bit2 == 0:
        print("→ Bob applies: Z gate (phase flip)")
        correction = "Z"
    else:
        print("→ Bob applies: X then Z gates")
        correction = "XZ"
    
    print()
    print("STEP 6: Success!")
    print("-" * 80)
    print(f"✨ Bob's final state: |ψ⟩ = {alpha:.3f}|0⟩ + {beta:.3f}|1⟩")
    print(f"   This is EXACTLY what Alice started with!")
    print()
    print("🎯 TELEPORTATION COMPLETE")
    print(f"   State traveled from Alice → Bob without passing through space")
    print(f"   Classical bits sent: {bit1}{bit2}")
    print(f"   Correction applied: {correction}")
    print()
    
    return bit1, bit2, correction

def no_cloning_theorem_explanation():
    """
    Explains why quantum teleportation doesn't violate no-cloning
    """
    print("=" * 80)
    print("🚫 THE NO-CLONING THEOREM")
    print("=" * 80)
    print()
    print("THEOREM: You cannot create an identical copy of an unknown quantum state")
    print()
    print("WHY IT MATTERS:")
    print("  • In teleportation, Alice's state is DESTROYED when measured")
    print("  • At no point do two copies exist simultaneously")
    print("  • The state is MOVED, not COPIED")
    print()
    print("CONSEQUENCES:")
    print("  ✓ Makes quantum cryptography secure (can't copy keys)")
    print("  ✓ Makes teleportation possible (state moves, not copied)")
    print("  ✗ Can't backup quantum computers (can't copy states)")
    print()
    print("ANALOGY:")
    print("  It's like cutting and pasting (not copy and paste)")
    print("  The original is deleted, the copy appears elsewhere")
    print()

def faster_than_light_explanation():
    """
    Explains why this doesn't allow faster-than-light communication
    """
    print("=" * 80)
    print("⚡ FASTER THAN LIGHT? NOPE!")
    print("=" * 80)
    print()
    print("COMMON MISCONCEPTION:")
    print("  'Bob gets the state instantly, so information traveled FTL!'")
    print()
    print("REALITY:")
    print("  • After Alice measures, Bob's qubit IS in a scrambled state")
    print("  • But Bob doesn't know WHICH scrambled state")
    print("  • Without Alice's classical bits, Bob has random noise")
    print("  • The classical bits travel at normal speeds (light or slower)")
    print()
    print("TIMELINE:")
    print("  t=0:   Alice performs measurement")
    print("  t=0:   Bob's qubit changes (entanglement)")
    print("  t=0:   But Bob can't extract any information yet!")
    print("  t=Δt:  Classical bits arrive (light-speed delay)")
    print("  t=Δt:  Bob applies corrections and gets the state")
    print()
    print("✓ No faster-than-light COMMUNICATION")
    print("✓ But quantum CORRELATION is instantaneous")
    print()

def star_trek_vs_quantum():
    """
    Compare to Star Trek teleportation
    """
    print("=" * 80)
    print("🖖 STAR TREK vs QUANTUM TELEPORTATION")
    print("=" * 80)
    print()
    print("┌────────────────────────────────────────────────────────────────┐")
    print("│ STAR TREK TELEPORTATION                                        │")
    print("├────────────────────────────────────────────────────────────────┤")
    print("│ • Teleports matter (atoms, molecules)                          │")
    print("│ • Person is scanned, transmitted, reconstructed                │")
    print("│ • Original is destroyed ('dematerialized')                     │")
    print("│ • Creates philosophical questions about identity               │")
    print("│ • Completely fictional with current physics                    │")
    print("└────────────────────────────────────────────────────────────────┘")
    print()
    print("┌────────────────────────────────────────────────────────────────┐")
    print("│ QUANTUM TELEPORTATION                                          │")
    print("├────────────────────────────────────────────────────────────────┤")
    print("│ • Teleports quantum INFORMATION (not matter)                   │")
    print("│ • State is measured, classical bits sent, state reconstructed  │")
    print("│ • Original state is destroyed (no-cloning theorem)             │")
    print("│ • No philosophical issues (just information transfer)          │")
    print("│ • ACTUALLY REAL - done in labs since 1997!                     │")
    print("└────────────────────────────────────────────────────────────────┘")
    print()
    print("🎯 KEY DIFFERENCE:")
    print("   Quantum teleportation moves INFORMATION, not physical objects")
    print("   You can't teleport yourself, but you can teleport qubit states!")
    print()

def real_world_applications():
    """
    Show where quantum teleportation is used
    """
    print("=" * 80)
    print("🌍 REAL-WORLD APPLICATIONS")
    print("=" * 80)
    print()
    print("1. QUANTUM INTERNET")
    print("   • Securely transfer quantum information between nodes")
    print("   • China teleported photon states to satellite (2017)")
    print("   • Distance record: 1,400 km (2022)")
    print()
    print("2. QUANTUM COMPUTING")
    print("   • Transfer quantum states between processors")
    print("   • Google's Willow uses teleportation for error correction!")
    print("   • Enables distributed quantum computers")
    print()
    print("3. QUANTUM CRYPTOGRAPHY")
    print("   • Secure key distribution")
    print("   • Unhackable communication channels")
    print("   • Already used by banks and governments")
    print()
    print("4. QUANTUM REPEATERS")
    print("   • Extend range of quantum communication")
    print("   • Overcome photon loss in fiber optics")
    print("   • Essential for long-distance quantum networks")
    print()

# ============================================================================
# MAIN DEMONSTRATION
# ============================================================================

print("\n")
print("╔" + "=" * 78 + "╗")
print("║" + " " * 22 + "QUANTUM TELEPORTATION LAB" + " " * 31 + "║")
print("║" + " " * 15 + "\"Beam me up, Scotty!\" - But make it quantum" + " " * 18 + "║")
print("╚" + "=" * 78 + "╝")
print()

# Show the circuit
show_teleportation_circuit()

# Show correction table
show_correction_table()

# Run detailed teleportation
input("Press ENTER to teleport a quantum state...")
print()

results = []
for i in range(3):
    print(f"\n{'▼' * 40} TELEPORTATION #{i+1} {'▼' * 40}\n")
    bit1, bit2, correction = quantum_teleportation_detailed(
        f"Quantum Secret #{i+1}"
    )
    results.append((bit1, bit2, correction))
    if i < 2:
        input("\nPress ENTER for next teleportation...")

# Statistics
print()
print("=" * 80)
print("📊 TELEPORTATION STATISTICS")
print("=" * 80)
print()
print("Classical bits sent:")
for i, (b1, b2, corr) in enumerate(results, 1):
    print(f"  Trial {i}: {b1}{b2} → Correction: {corr}")
print()
print("Notice: The measurement outcomes are completely random!")
print("But Bob can ALWAYS reconstruct the state perfectly.")
print()

# Explanations
input("Press ENTER to understand the No-Cloning Theorem...")
print()
no_cloning_theorem_explanation()

input("Press ENTER to see why this isn't faster than light...")
print()
faster_than_light_explanation()

input("Press ENTER for Star Trek comparison...")
print()
star_trek_vs_quantum()

input("Press ENTER for real-world applications...")
print()
real_world_applications()

# Final thoughts
print()
print("=" * 80)
print("💡 MIND-BLOWING FACTS")
print("=" * 80)
print()
print("1. Quantum teleportation has been demonstrated in labs since 1997")
print()
print("2. China teleported photon states 1,400 km to a satellite in orbit")
print()
print("3. Google's Willow chip uses teleportation protocols internally")
print()
print("4. The quantum internet will rely heavily on teleportation")
print()
print("5. You can't teleport yourself (sorry!), but you can teleport")
print("   the quantum state of individual photons or atoms")
print()
print("6. This is one of the most experimentally verified predictions")
print("   of quantum mechanics - it's 100% real!")
print()
print("=" * 80)
print("🎓 CONGRATULATIONS!")
print("=" * 80)
print()
print("You now understand one of the most profound protocols")
print("in quantum information theory!")
print()
print("Next steps: Learn about quantum error correction, quantum")
print("cryptography, and how companies like Google and IBM are")
print("building the quantum computers of tomorrow.")
print()
print("=" * 80)
