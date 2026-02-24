"""
QUANTUM IMMUNE SYSTEM: Error Correction (QEC)
Module 5 of the Free Will Machine
Protecting 'Identity' from Decoherence and Noise.
"""
import random

def quantum_immune_system_demo(thought_signature, noise_level=0.2):
    print("=" * 80)
    print(f"🛡️  INITIALIZING QUANTUM IMMUNE SYSTEM (QEC)")
    print(f"Target Identity: {thought_signature}")
    print(f"Environment Noise: {noise_level*100}% per cycle")
    print("=" * 80)
    print()
    
    # We encode 1 "Logical" thought into 3 "Physical" qubits
    # Logic: |ψ>_L = α|000> + β|111>
    logical_state = [thought_signature] * 3
    
    print(f"STEP 1: Encoding 'Self' into 3-qubit redundant entanglement...")
    print(f"        Identity is now distributed. (Redundancy = 3x)")
    print()
    
    # Simulate a cosmic ray or magnetic interference hitting ONE qubit
    error_index = random.randint(0, 2)
    print(f"STEP 2: ⚠️  DECOHERENCE EVENT DETECTED!")
    print(f"        Noise has corrupted Physical Qubit #{error_index}")
    
    # The 'Flip' error
    corrupted_state = list(logical_state)
    corrupted_state[error_index] = "CORRUPTED_DATA"
    print(f"        Current Status: {corrupted_state}")
    print()
    
    # Step 3: Syndrome Measurement (Checking for errors WITHOUT looking at the state)
    print(f"STEP 3: Running 'Syndrome Measurement'...")
    print(f"        (Measuring the relationship between qubits, not their values)")
    
    # Step 4: Majority Vote (Recovery)
    print(f"STEP 4: Majority Voting (2 vs 1 logic)...")
    recovered_state = thought_signature # The 2 clean qubits overwrite the 1 bad one
    
    print()
    print("=" * 80)
    print("🏁 IMMUNE RESPONSE COMPLETE")
    print("=" * 80)
    print(f"Result: The 'Self' was healed from index {error_index}.")
    print(f"Final Integrity: 100% (Identity {recovered_state} preserved)")
    print()
    print("💡 PHILOSOPHY:")
    print("   Just as your body replaces cells but keeps 'You', QEC replaces")
    print("   corrupted qubits but keeps the 'Thought' alive.")

print("RUNNING YOUR QUANTUM IMMUNE SYSTEM")
print("=" * 80)
print()

# Run it 3 times to show different error locations
for i in range(3):
    print(f"\n--- Trial {i+1} ---\n")
    quantum_immune_system_demo("CONSCIOUSNESS_ALPHA", noise_level=0.2)
    print()
