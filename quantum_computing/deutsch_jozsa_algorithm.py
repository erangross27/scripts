"""
Deutsch-Jozsa Algorithm Implementation using IBM Quantum

This script implements the Deutsch-Jozsa algorithm using IBM Quantum's cloud-based quantum computers.
The Deutsch-Jozsa algorithm is designed to determine whether a given function is constant or balanced.

The script performs the following main steps:
1. Sets up the connection to IBM Quantum using an API token.
2. Defines the Deutsch-Jozsa circuit and a balanced oracle.
3. Creates and transpiles the circuit for the selected backend.
4. Runs the circuit on the least busy available quantum computer.
5. Retrieves and processes the results.
6. Visualizes the results using a histogram.

The script requires the IBM_QUANTUM_TOKEN environment variable to be set with a valid API token.

Dependencies:
- qiskit
- qiskit_ibm_runtime
- matplotlib
- os

Note: This script is designed for educational and demonstrative purposes.
"""

import os
from qiskit import QuantumCircuit, transpile
from qiskit_ibm_runtime import QiskitRuntimeService, Sampler, Options
import matplotlib.pyplot as plt
from qiskit.visualization import plot_histogram

# Get API token from environment variable
API_TOKEN = os.environ.get('IBM_QUANTUM_TOKEN')
if not API_TOKEN:
    raise ValueError("IBM_QUANTUM_TOKEN environment variable is not set. Please set it with your API token.")

# Save and load the IBM Quantum account
QiskitRuntimeService.save_account(channel="ibm_quantum", token=API_TOKEN, overwrite=True)

# Initialize the QiskitRuntimeService
service = QiskitRuntimeService(channel="ibm_quantum")

def deutsch_jozsa_circuit(n, oracle):
    """Create a Deutsch-Jozsa circuit."""
    qc = QuantumCircuit(n + 1, n)
    
    # Apply H-gates to the first n qubits
    for qubit in range(n):
        qc.h(qubit)
    
    # Apply X-gate and H-gate to the last qubit
    qc.x(n)
    qc.h(n)
    
    # Apply the oracle
    qc.append(oracle, range(n + 1))
    
    # Apply H-gates to the first n qubits
    for qubit in range(n):
        qc.h(qubit)
    
    # Measure the first n qubits
    qc.measure(range(n), range(n))
    
    return qc

# Define a balanced oracle for 3 qubits
def balanced_oracle():
    qc = QuantumCircuit(4)
    qc.cx(0, 3)
    qc.cx(1, 3)
    return qc

# Create the Deutsch-Jozsa circuit
n = 3  # number of qubits
dj_circuit = deutsch_jozsa_circuit(n, balanced_oracle())

print("Deutsch-Jozsa Circuit:")
print(dj_circuit)

# Get the least busy backend
backend = service.least_busy(operational=True, simulator=False)
print(f"\nUsing backend: {backend}")

# Transpile the circuit for the specific backend
transpiled_circuit = transpile(dj_circuit, backend)

# Create options for the Sampler
options = Options()
options.optimization_level = 1
options.resilience_level = 1

# Create a sampler
sampler = Sampler(backend=backend, options=options)

# Run the job
job = sampler.run([transpiled_circuit], shots=1000)
print(f"Job ID: {job.job_id()}")

# Wait for the job to complete and get the result
result = job.result()
print("\nJob completed. Results obtained.")

# Extract counts from the result
quasi_dists = result.quasi_dists
counts = quasi_dists[0]

# Convert quasi-distribution to regular counts
regular_counts = {format(k, '0' + str(n) + 'b'): int(v * 1000) for k, v in counts.items()}

print("\nMeasurement Results:")
for outcome, count in regular_counts.items():
    print(f"Outcome {outcome}: {count} times")

# Plot the results
plot_histogram(regular_counts)
plt.title("Deutsch-Jozsa Algorithm Results")
plt.show()

print("\nExplanation of results:")
print("In the Deutsch-Jozsa algorithm:")
print("- If we measure all zeros (000), the function is constant.")
print("- If we measure any other result, the function is balanced.")
print("Our oracle was designed to be balanced, so we expect to see non-zero results.")
