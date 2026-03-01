import random
import math

def entangled_quantum_dice(sides=10):
    num_qubits = math.ceil(math.log2(sides))
    
    print(f"🌌 CREATING ENTANGLED SYSTEM ({num_qubits} Qubits per Die)")
    
    # Simulate the quantum entanglement process
    # In a real circuit, we would apply H and CNOT gates
    def generate_entangled_value():
        # We only generate the randomness ONCE for both dice
        # This simulates the 'collapse' of a shared wave function
        bits = [random.randint(0, 1) for _ in range(num_qubits)]
        val = sum(bit * (2**i) for i, bit in enumerate(bits))
        
        while val >= sides: # Rejection sampling
            bits = [random.randint(0, 1) for _ in range(num_qubits)]
            val = sum(bit * (2**i) for i, bit in enumerate(bits))
        return val + 1

    # The moment of measurement
    shared_result = generate_entangled_value()
    
    dice_1 = shared_result
    dice_2 = shared_result # Instantly the same due to entanglement
    
    print(f"Die 1 (Measured in New York): {dice_1}")
    print(f"Die 2 (Measured on Mars):     {dice_2}")
    print("✨ Results match perfectly due to quantum correlation.")

print("=" * 60)
print("RUNNING YOUR ENTANGLED DICE CODE")
print("=" * 60)
print()

# Run it 5 times to show they always match
for i in range(5):
    print(f"--- Roll {i+1} ---")
    entangled_quantum_dice(10)
    print()
