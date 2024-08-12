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

def oracle(qc, key):
    """Implement the oracle for the given key."""
    if key[0] == '1':
        qc.x(0)
    if key[1] == '1':
        qc.x(1)
    qc.cz(0, 2)
    qc.cz(1, 2)
    if key[0] == '1':
        qc.x(0)
    if key[1] == '1':
        qc.x(1)

def diffuser(qc):
    """Implement the diffuser."""
    qc.h([0, 1])
    qc.x([0, 1])
    qc.cz(0, 1)
    qc.x([0, 1])
    qc.h([0, 1])

def grover_circuit(key):
    """Create a Grover's algorithm circuit for cracking a 2-bit key."""
    qc = QuantumCircuit(3, 2)
    
    # Initialize superposition
    qc.h([0, 1])
    qc.x(2)
    qc.h(2)
    
    # Apply Grover operator
    oracle(qc, key)
    diffuser(qc)
    
    # Measure
    qc.measure([0, 1], [0, 1])
    
    return qc

# Set the secret key (2-bit string)
secret_key = "10"

# Create the Grover's circuit
grover_qc = grover_circuit(secret_key)

print("Grover's Circuit for key cracking:")
print(grover_qc)

# Get the least busy backend
backend = service.least_busy(operational=True, simulator=False)
print(f"\nUsing backend: {backend}")

# Transpile the circuit for the specific backend
transpiled_circuit = transpile(grover_qc, backend)

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
regular_counts = {format(k, '02b'): int(v * 1000) for k, v in counts.items()}

print("\nMeasurement Results:")
for outcome, count in regular_counts.items():
    print(f"Outcome {outcome}: {count} times")

# Plot the results
plot_histogram(regular_counts)
plt.title("Grover's Algorithm Results for Key Cracking")
plt.show()

print("\nExplanation of results:")
print(f"The secret key was: {secret_key}")
print("Grover's algorithm attempts to find this key.")
print("The outcome with the highest count is likely to be the secret key.")
print("In a perfect quantum computer, we would see this outcome with very high probability.")
print("However, due to noise in real quantum devices, we may see a distribution of outcomes.")
