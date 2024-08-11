import os
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, transpile
from qiskit_ibm_runtime import QiskitRuntimeService, Sampler, Session
from qiskit.visualization import plot_histogram, plot_gate_map, plot_circuit_layout
from qiskit.transpiler import PassManager, InstructionDurations
from qiskit.transpiler.passes import Unroller, Optimize1qGates, CXCancellation, Depth, FixedPoint
from qiskit.transpiler.preset_passmanagers import level_3_pass_manager
from qiskit.circuit.library import GroverOperator
import matplotlib.pyplot as plt
import numpy
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
    num_iterations = int(numpy.pi/4 * numpy.sqrt(2**n_qubits / len(marked_states)))
    for _ in range(num_iterations):
        qc.append(grover_op, qr)

    # Measure
    qc.measure(qr, cr)

    return qc

# Create Grover's algorithm circuit
n_qubits = 4
marked_states = ['1011', '1100']
grover_circuit = create_grover_circuit(n_qubits, marked_states)

print("Original Grover's Algorithm Circuit:")
print(grover_circuit)

# Get the least busy backend
backend = service.least_busy(operational=True, simulator=False)
print(f"\nUsing backend: {backend}")

# Visualize the backend's gate map
gate_map = plot_gate_map(backend)
gate_map.savefig('backend_gate_map.png')
print("Backend gate map saved as 'backend_gate_map.png'")

# Create a custom pass manager
def create_custom_pm(backend):
    pass_manager = PassManager()
    pass_manager.append(Unroller(['u', 'cx']))
    pass_manager.append(Optimize1qGates())
    pass_manager.append(CXCancellation())
    
    # Use FixedPoint to repeat optimization until the circuit doesn't change
    depth_pass = Depth()
    fix_point = FixedPoint('depth')
    fix_point.append(depth_pass)
    pass_manager.append(fix_point)

    return pass_manager

custom_pm = create_custom_pm(backend)

# Transpile with custom pass manager
custom_transpiled = transpile(grover_circuit, backend, pass_manager=custom_pm)

print("\nCircuit after custom transpilation:")
print(custom_transpiled)

# Transpile with preset level 3 pass manager
preset_transpiled = transpile(grover_circuit, backend, optimization_level=3)

print("\nCircuit after preset level 3 transpilation:")
print(preset_transpiled)

# Visualize circuits
grover_circuit.draw(output='mpl', filename='original_circuit.png')
custom_transpiled.draw(output='mpl', filename='custom_transpiled_circuit.png')
preset_transpiled.draw(output='mpl', filename='preset_transpiled_circuit.png')

# Visualize circuit layout on the device
layout_plot = plot_circuit_layout(preset_transpiled, backend)
layout_plot.savefig('circuit_layout.png')

print("\nCircuit visualizations saved as PNG files.")

# Run the transpiled circuit
with Session(backend=backend) as session:
    sampler = Sampler(session=session)
    
    job = sampler.run(preset_transpiled, shots=1000)
    print(f"Job ID: {job.job_id()}")
    
    result = job.result()
    print("\nJob completed. Results obtained.")

    counts = result.quasi_dists[0]
    regular_counts = {format(k, f'0{n_qubits}b'): int(v * 1000) for k, v in counts.items()}

    print("\nMeasurement Results:")
    for outcome, count in regular_counts.items():
        print(f"Outcome {outcome}: {count} times")

    plot_histogram(regular_counts)
    plt.title("Grover's Algorithm Results")
    plt.savefig('grover_results.png')
    plt.show()

print("\nExplanation of results:")
print(f"This circuit implements Grover's algorithm to search for {len(marked_states)} marked states out of {2**n_qubits} possibilities.")
print(f"The marked states are: {', '.join(marked_states)}")
print("The algorithm amplifies the probability of measuring these states.")
print("Any deviation from perfect amplification is due to quantum noise and hardware imperfections.")
