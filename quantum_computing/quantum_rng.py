"""
Quantum Random Number Generator

This script demonstrates the generation of random numbers using a quantum circuit
implemented with IBM Quantum services. It showcases the following functionality:

1. Setting up an IBM Quantum account using an API token.
2. Creating a quantum circuit to generate random numbers.
3. Executing the circuit on the least busy IBM Quantum backend.
4. Retrieving and interpreting the results as random numbers.
5. Providing an explanation of the quantum random number generation process.
6. Suggesting potential cybersecurity applications for the generated random numbers.

The script uses Qiskit and the IBM Quantum Runtime to interact with real quantum hardware.
It generates 4-bit random numbers (0-15) and displays them in both decimal and binary formats.

Requirements:
- IBM Quantum account and API token (set as IBM_QUANTUM_TOKEN environment variable)
- Qiskit and qiskit_ibm_runtime libraries

Note: This script is for educational purposes and demonstrates basic quantum computing concepts.
For production-level cryptographic applications, consult with cryptography experts and use
established cryptographic libraries and protocols.
"""

# Import necessary libraries
import os
from qiskit import QuantumCircuit, transpile
from qiskit_ibm_runtime import QiskitRuntimeService, Sampler, Options

# Setup IBM Quantum account
API_TOKEN = os.environ.get('IBM_QUANTUM_TOKEN')
if not API_TOKEN:
    raise ValueError("IBM_QUANTUM_TOKEN environment variable is not set.")

# Save the IBM Quantum account credentials
QiskitRuntimeService.save_account(channel="ibm_quantum", token=API_TOKEN, overwrite=True)
service = QiskitRuntimeService(channel="ibm_quantum")

def quantum_random_number(num_bits=4):
    """Generate a random number using quantum circuit."""
    # Create a quantum circuit with specified number of qubits and classical bits
    qc = QuantumCircuit(num_bits, num_bits)
    
    # Apply Hadamard gates to create superposition
    for qubit in range(num_bits):
        qc.h(qubit)
    
    # Measure all qubits
    qc.measure(range(num_bits), range(num_bits))
    
    return qc

# Create a quantum circuit for 4-bit random number
qc = quantum_random_number(4)

# Get the least busy backend from IBM Quantum
backend = service.least_busy(operational=True, simulator=False)
print(f"Using backend: {backend}")

# Transpile the circuit for the chosen backend
transpiled_circuit = transpile(qc, backend)

# Set up the Sampler options
options = Options()
options.optimization_level = 1
options.resilience_level = 1
sampler = Sampler(backend=backend, options=options)

# Run the circuit using the Sampler
job = sampler.run(transpiled_circuit, shots=10)
result = job.result()

# Print the generated quantum random numbers
print("\nQuantum Random Numbers:")
for i, counts in enumerate(result.quasi_dists):
    # Convert quasi-distribution to binary string and then to integer
    binary_string = format(max(counts, key=counts.get), '04b')
    random_number = int(binary_string, 2)
    print(f"Random Number {i+1}: {random_number} (Binary: {binary_string})")

# Provide explanation about the generated numbers
print("\nThese numbers are generated using quantum superposition and measurement,")
print("providing true randomness based on quantum mechanics.")
print("The numbers range from 0 to 15, representing all possible 4-bit values.")

# Cybersecurity application example
print("\nCybersecurity Application Example:")
print("These random numbers could be used for:")
print("1. Generating encryption keys (e.g., for simple XOR cipher)")
print("2. Creating initialization vectors for block ciphers")
print("3. Producing nonces for cryptographic protocols")
print("4. Seeding classical pseudo-random number generators")
