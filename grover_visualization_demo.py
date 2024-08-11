import os
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, transpile
from qiskit_ibm_runtime import QiskitRuntimeService, Sampler, Session
from qiskit.visualization import plot_histogram, plot_state_qsphere, plot_state_paulivec, plot_bloch_multivector
from qiskit.circuit.library import GroverOperator
from qiskit.quantum_info import Statevector
import matplotlib.pyplot as plt
import numpy as np

# Get API token from environment variable
API_TOKEN = os.environ.get('IBM_QUANTUM_TOKEN')

if not API_TOKEN:
    raise ValueError("IBM_QUANTUM_TOKEN environment variable is not set. Please set it with your API token.")

# Save and load the IBM Quantum account
QiskitRuntimeService.save_account(channel="ibm_quantum", token=API_TOKEN, overwrite=True)

# Initialize the QiskitRuntimeService
service = QiskitRuntimeService(channel="ibm_quantum")

def create_grover_circuit(n_qubits, marked_states):
    """Create a Grover's algorithm circuit."""
    qr = QuantumRegister(n_qubits, 'q')
    cr = ClassicalRegister(n_qubits, 'c')
    qc = QuantumCircuit(qr, cr)

    # Initialize superposition
    qc.h(qr)

    # Create Grover operator
    grover_op = GroverOperator(n_qubits, marked_states)
    
    # Apply Grover operator optimal number of times
    num_iterations = int(np.pi/4 * np.sqrt(2**n_qubits / len(marked_states)))
    for _ in range(num_iterations):
        qc.append(grover_op, qr)

    # Measure
    qc.measure(qr, cr)

    return qc

# Create Grover's algorithm circuit
n_qubits = 3
marked_states = ['101', '110']
grover_circuit = create_grover_circuit(n_qubits, marked_states)

print("Grover's Algorithm Circuit:")
print(grover_circuit)

# Get the least busy backend
backend = service.least_busy(operational=True, simulator=False)
print(f"\nUsing backend: {backend}")

# Transpile the circuit
transpiled_circuit = transpile(grover_circuit, backend, optimization_level=3)

# Run the transpiled circuit
with Session(backend=backend) as session:
    sampler = Sampler(session=session)
    
    job = sampler.run(transpiled_circuit, shots=1000)
    print(f"Job ID: {job.job_id()}")
    
    result = job.result()
    print("\nJob completed. Results obtained.")

    counts = result.quasi_dists[0]
    regular_counts = {format(k, f'0{n_qubits}b'): int(v * 1000) for k, v in counts.items()}

# Visualize results

# 1. Histogram
plt.figure(figsize=(10, 6))
plot_histogram(regular_counts)
plt.title("Grover's Algorithm Results - Histogram")
plt.savefig('grover_histogram.png')
plt.close()

# 2. Q-sphere representation
# For Q-sphere, we need the statevector, which we'll simulate
statevector = Statevector.from_instruction(transpiled_circuit)
plt.figure(figsize=(10, 10))
plot_state_qsphere(statevector)
plt.title("Q-sphere Representation of Final State")
plt.savefig('grover_qsphere.png')
plt.close()

# 3. Pauli vector representation
plt.figure(figsize=(10, 10))
plot_state_paulivec(statevector)
plt.title("Pauli Vector Representation of Final State")
plt.savefig('grover_paulivec.png')
plt.close()

# 4. Bloch multivector
plt.figure(figsize=(15, 5))
plot_bloch_multivector(statevector)
plt.title("Bloch Multivector Representation of Final State")
plt.savefig('grover_bloch_multivector.png')
plt.close()

# 5. City plot (using histogram data)
from qiskit.visualization import plot_state_city
plt.figure(figsize=(10, 10))
plot_state_city(regular_counts)
plt.title("City Plot of Measurement Outcomes")
plt.savefig('grover_city_plot.png')
plt.close()

print("\nVisualization Results:")
print("1. Histogram saved as 'grover_histogram.png'")
print("2. Q-sphere representation saved as 'grover_qsphere.png'")
print("3. Pauli vector representation saved as 'grover_paulivec.png'")
print("4. Bloch multivector representation saved as 'grover_bloch_multivector.png'")
print("5. City plot saved as 'grover_city_plot.png'")

print("\nExplanation of results:")
print(f"This circuit implements Grover's algorithm to search for {len(marked_states)} marked states out of {2**n_qubits} possibilities.")
print(f"The marked states are: {', '.join(marked_states)}")
print("The algorithm amplifies the probability of measuring these states.")
print("The various visualizations provide different perspectives on the final quantum state and measurement outcomes:")
print("- Histogram: Shows the distribution of measurement outcomes.")
print("- Q-sphere: Represents the quantum state on a sphere, where amplitude and phase are encoded.")
print("- Pauli vector: Shows the expectation values of Pauli operators for the state.")
print("- Bloch multivector: Displays individual qubit states on Bloch spheres.")
print("- City plot: Provides a 3D representation of the measurement probabilities.")
print("These visualizations help in understanding the quantum state produced by the algorithm and the effectiveness of the search.")
