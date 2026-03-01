"""
SIMULATING YOUR QUANTUM DICE CODE
(Without needing to install cirq)
"""

import random
import numpy as np

print("=" * 80)
print("RUNNING YOUR QUANTUM DICE CODE")
print("=" * 80)
print()

# Simulate what your code would output
print("--- QUANTUM CIRCUIT ---")
print("(0, 0): ───H───M('dice_roll')───")
print("-----------------------")
print()

# Simulate quantum measurements
# A single qubit with Hadamard gate gives 50/50 chance of 0 or 1
sides = 10
results = [random.randint(0, 1) for _ in range(sides)]

print(f"Quantum Bitstream: {results}")
print(f"Total 'On' states: {sum(results)}")
print()

print("=" * 80)
print("THE PROBLEM WITH YOUR CODE:")
print("=" * 80)
print()
print("✗ You're using 1 qubit, which can only give you 0 or 1")
print("✗ No matter how many times you run it (sides=10), you only get 0s and 1s")
print("✗ To get a 10-sided dice, you need MORE QUBITS")
print()
print("Math:")
print("  1 qubit  = 2 possible outcomes (0, 1)")
print("  2 qubits = 4 possible outcomes (00, 01, 10, 11)")
print("  3 qubits = 8 possible outcomes (000, 001, 010, ..., 111)")
print("  4 qubits = 16 possible outcomes")
print()
print("For a 10-sided dice, you need at least 4 qubits (gives you 0-15)")
print()

print("=" * 80)
print("HERE'S THE FIXED VERSION:")
print("=" * 80)
print()

def quantum_dice_fixed(sides=10):
    """
    Proper quantum dice using multiple qubits
    """
    import math
    
    # Calculate how many qubits we need
    # For 10 sides, we need log2(10) ≈ 3.32, so round up to 4 qubits
    num_qubits = math.ceil(math.log2(sides))
    max_value = 2 ** num_qubits  # 4 qubits = 16 possible values
    
    print(f"Target: {sides}-sided dice")
    print(f"Qubits needed: {num_qubits}")
    print(f"Possible outcomes: 0 to {max_value - 1}")
    print()
    
    print("CODE:")
    print("-" * 80)
    print(f"""
import cirq
import math

def quantum_dice(sides={sides}):
    # Calculate number of qubits needed
    num_qubits = math.ceil(math.log2(sides))
    
    # Create multiple qubits
    qubits = [cirq.GridQubit(0, i) for i in range(num_qubits)]
    
    circuit = cirq.Circuit()
    
    # Apply Hadamard to ALL qubits (creates superposition on each)
    for qubit in qubits:
        circuit.append(cirq.H(qubit))
    
    # Measure all qubits
    circuit.append(cirq.measure(*qubits, key='dice_roll'))
    
    # Run it
    simulator = cirq.Simulator()
    result = simulator.run(circuit, repetitions=1)
    
    # Convert binary result to decimal
    bits = result.measurements['dice_roll'][0]
    value = sum(bit * (2**i) for i, bit in enumerate(bits))
    
    # If value >= sides, re-roll (rejection sampling)
    while value >= sides:
        result = simulator.run(circuit, repetitions=1)
        bits = result.measurements['dice_roll'][0]
        value = sum(bit * (2**i) for i, bit in enumerate(bits))
    
    return value + 1  # Add 1 so we get 1-10 instead of 0-9

# Roll the quantum dice!
roll = quantum_dice({sides})
print(f"You rolled: {{roll}}")
    """)
    print("-" * 80)
    print()
    
    # Simulate what this would output
    print("CIRCUIT WOULD LOOK LIKE:")
    print("-" * 80)
    for i in range(num_qubits):
        print(f"(0, {i}): ───H───M('dice_roll')───")
    print("-" * 80)
    print()
    
    # Simulate a roll
    simulated_roll = random.randint(1, sides)
    print(f"Example output: You rolled: {simulated_roll}")
    print()
    
    return num_qubits

num_qubits = quantum_dice_fixed(10)

print()
print("=" * 80)
print("WHY THIS VERSION WORKS:")
print("=" * 80)
print()
print(f"✓ Uses {num_qubits} qubits in PARALLEL superposition")
print("✓ Each measurement gives a binary number (e.g., 1010 = 10 in decimal)")
print("✓ You get all values from 0 to 15")
print("✓ Reject values >= 10 and re-roll (rejection sampling)")
print("✓ Final result: Fair 1-10 dice roll")
print()

print("=" * 80)
print("COMPARE:")
print("=" * 80)
print()
print("YOUR VERSION:")
print("  1 qubit, 10 repetitions → [0,1,0,1,1,0,1,1,0,1]")
print("  This is like flipping a coin 10 times, not rolling a 10-sided dice")
print()
print("FIXED VERSION:")
print(f"  {num_qubits} qubits, 1 measurement → Random number 0-15, keep if < 10")
print("  This gives you a true random number in your desired range")
print()

print("=" * 80)
print("THE QUANTUM ADVANTAGE:")
print("=" * 80)
print()
print("Regular computer: Uses pseudorandom algorithm (deterministic)")
print("Quantum computer: Uses ACTUAL quantum randomness (true randomness)")
print()
print("For a dice app? No real advantage.")
print("For cryptographic keys? HUGE advantage - unpredictable randomness!")
print()
