import os
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, transpile
from qiskit_ibm_runtime import QiskitRuntimeService, Sampler, Session
from qiskit.visualization import plot_histogram
import matplotlib.pyplot as plt
from qiskit.circuit.library import RYGate
from qiskit.quantum_info import random_statevector, Statevector

# Get API token from environment variable
API_TOKEN = os.environ.get('IBM_QUANTUM_TOKEN')

if not API_TOKEN:
    raise ValueError("IBM_QUANTUM_TOKEN environment variable is not set. Please set it with your API token.")

# Save and load the IBM Quantum account
QiskitRuntimeService.save_account(channel="ibm_quantum", token=API_TOKEN, overwrite=True)

# Initialize the QiskitRuntimeService
service = QiskitRuntimeService(channel="ibm_quantum")

def create_bell_pair(qc, a, b):
    """Create a Bell pair in qubits a and b."""
    qc.h(a)
    qc.cx(a, b)

def alice_gates(qc, psi, a):
    """Apply Alice's gates."""
    qc.cx(psi, a)
    qc.h(psi)

def measure_and_send(qc, a, psi, crz, crx):
    """Measure qubits and store results in classical registers."""
    qc.measure(a, crz)
    qc.measure(psi, crx)

def bob_gates(qc, b, crz, crx):
    """Apply Bob's corrective gates."""
    with qc.if_test((crx, 1)):
        qc.x(b)
    with qc.if_test((crz, 1)):
        qc.z(b)

def quantum_teleportation_circuit():
    """Create a quantum teleportation circuit."""
    qr = QuantumRegister(3, 'q')
    crz = ClassicalRegister(1, 'crz')
    crx = ClassicalRegister(1, 'crx')
    qc = QuantumCircuit(qr, crz, crx)

    # Create a random state to teleport
    random_state = random_statevector(2)
    qc.initialize(random_state, 0)
    print(f"Initial state to teleport: {random_state}")

    create_bell_pair(qc, 1, 2)
    alice_gates(qc, 0, 1)
    measure_and_send(qc, 1, 0, crz, crx)
    bob_gates(qc, 2, crz, crx)

    # Measure the final state
    qc.measure(2, crz)

    return qc

# Create the quantum teleportation circuit
qc = quantum_teleportation_circuit()

print("Quantum Teleportation Circuit:")
print(qc)

# Save the circuit diagram
qc.draw(output='mpl', filename='teleportation_circuit.png')
print("Circuit diagram saved as 'teleportation_circuit.png'")

# Get the least busy backend
backend = service.least_busy(operational=True, simulator=False)
print(f"\nUsing backend: {backend}")

# Transpile the circuit for the specific backend
transpiled_circuit = transpile(qc, backend)

# Create a session and sampler
with Session(backend=backend) as session:
    sampler = Sampler(session=session)
    
    # Run the job
    job = sampler.run(transpiled_circuit, shots=1000)
    print(f"Job ID: {job.job_id()}")
    
    # Wait for the job to complete and get the result
    result = job.result()
    print("\nJob completed. Results obtained.")

    # Extract counts from the result
    counts = result.quasi_dists[0]

    # Convert quasi-distribution to regular counts
    regular_counts = {format(k, '0b'): int(v * 1000) for k, v in counts.items()}

    print("\nMeasurement Results:")
    for outcome, count in regular_counts.items():
        print(f"Outcome {outcome}: {count} times")

    # Plot the results
    plot_histogram(regular_counts)
    plt.title("Quantum Teleportation Results")
    plt.savefig('teleportation_results.png')
    plt.show()

print("\nExplanation of results:")
print("This circuit implements quantum teleportation:")
print("1. We create a random quantum state.")
print("2. This state is teleported from the first qubit to the third qubit.")
print("3. The measurement result should approximate the initial random state.")
print("4. Any deviation is due to quantum noise and hardware imperfections.")
print("\nResults interpretation:")
print("- '0' indicates the teleported state is close to the initial state.")
print("- '1' indicates a phase flip occurred during teleportation.")
print("The distribution of 0s and 1s depends on the initial random state.")
