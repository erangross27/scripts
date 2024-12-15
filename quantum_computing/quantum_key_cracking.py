"""
Quantum Key Cracking using Grover's Algorithm

This script demonstrates the use of Grover's algorithm to crack a 3-bit secret key
using IBM's Qiskit framework and quantum computing services. It includes the following
main components:

1. Setup of IBM Quantum services using an API token.
2. Implementation of a custom oracle function for the 3-bit key.
3. Implementation of a diffuser function for 3 qubits.
4. Creation of a Grover's algorithm circuit for key cracking.
5. Execution of the quantum circuit on IBM's quantum simulator.
6. Analysis and visualization of the results.

The script uses a more complex oracle implementation to demonstrate a practical
application of Grover's algorithm in cryptography. It also includes error handling
for the API token and provides a detailed explanation of the results.

Requirements:
- Qiskit
- Matplotlib
- IBM Quantum account and API token

Usage:
Set the IBM_QUANTUM_TOKEN environment variable with your API token before running the script.
The secret key is set within the script and can be modified as needed.

Note: This is a demonstration and should not be used for actual cryptographic purposes.
"""

import os
from qiskit import QuantumCircuit
from qiskit_ibm_runtime import QiskitRuntimeService, Sampler, Options
import matplotlib.pyplot as plt

# Get API token from environment variable
API_TOKEN = os.environ.get('IBM_QUANTUM_TOKEN')
if not API_TOKEN:
    raise ValueError("IBM_QUANTUM_TOKEN environment variable is not set. Please set it with your API token.")

# Initialize the QiskitRuntimeService
service = QiskitRuntimeService(channel="ibm_quantum", token=API_TOKEN)

def oracle(qc, key):
    """Implement a more complex oracle for the given 3-bit key."""
    if key[0] == '1':
        qc.x(0)
    if key[1] == '1':
        qc.x(1)
    if key[2] == '1':
        qc.x(2)
    
    # More complex operation
    qc.ccx(0, 1, 3)  # Toffoli gate
    qc.cx(2, 3)
    
    if key[0] == '1':
        qc.x(0)
    if key[1] == '1':
        qc.x(1)
    if key[2] == '1':
        qc.x(2)

def diffuser(qc):
    """Implement the diffuser for 3 qubits."""
    qc.h([0, 1, 2])
    qc.x([0, 1, 2])
    qc.h(2)
    qc.ccx(0, 1, 2)
    qc.h(2)
    qc.x([0, 1, 2])
    qc.h([0, 1, 2])

def grover_circuit(key):
    """Create a Grover's algorithm circuit for cracking a 3-bit key."""
    qc = QuantumCircuit(4, 3)
    
    # Initialize superposition
    qc.h([0, 1, 2])
    qc.x(3)
    qc.h(3)
    
    # Apply Grover operator
    oracle(qc, key)
    diffuser(qc)
    
    # Measure
    qc.measure([0, 1, 2], [0, 1, 2])
    
    return qc

# Set the secret key (3-bit string)
secret_key = "101"  # This is now a more complex key

# Create the Grover's circuit
grover_qc = grover_circuit(secret_key)

print("Grover's Circuit for key cracking:")
print(grover_qc)

# Select the backend
backend = service.backend("ibmq_qasm_simulator")  # You can change this to a real quantum device

# Create options for the Sampler
options = Options()
options.optimization_level = 1
options.resilience_level = 1

# Create a sampler
sampler = Sampler(backend=backend, options=options)

# Run the job
job = sampler.run(circuits=[grover_qc], shots=1000)
print(f"Job ID: {job.job_id()}")

# Wait for the job to complete and get the result
result = job.result()
print("\nJob completed. Results obtained.")

# Extract quasi-probabilities from the result
quasi_dists = result.quasi_dists[0]

# Convert quasi-probabilities to counts
counts = {format(k, '03b'): int(v * 1000) for k, v in quasi_dists.items()}

print("\nMeasurement Results:")
for outcome, count in counts.items():
    print(f"Outcome {outcome}: {count} times")

# Plot the results
plt.bar(counts.keys(), counts.values())
plt.title("Grover's Algorithm Results for Key Cracking")
plt.xlabel("Measured State")
plt.ylabel("Counts")
plt.show()

print("\nExplanation of results:")
print(f"The secret key was: {secret_key}")
print("Grover's algorithm attempts to find this key.")
print("The outcome with the highest count is likely to be the secret key.")
print("In a perfect quantum computer, we would see this outcome with very high probability.")
print("However, due to noise in real quantum devices, we may see a distribution of outcomes.")
