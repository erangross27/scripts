# Directory Scripts Documentation

## Available Scripts


### deutsch_jozsa_algorithm.py

**Path:** `quantum_computing\deutsch_jozsa_algorithm.py`

**Description:**
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

**File Info:**
- Last modified: 2025-02-18 10:38:35
- Size: 3.8 KB
- Lines of code: 75 (of 124 total)

**Functions:**
- `deutsch_jozsa_circuit`: Create a Deutsch-Jozsa circuit
- `balanced_oracle`: No documentation

**Dependencies:**
- matplotlib
- qiskit
- qiskit_ibm_runtime

### quantum_key_cracking.py

**Path:** `quantum_computing\quantum_key_cracking.py`

**Description:**
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

**File Info:**
- Last modified: 2025-02-18 10:38:35
- Size: 4.3 KB
- Lines of code: 95 (of 142 total)

**Functions:**
- `oracle`: Implement a more complex oracle for the given 3-bit key
- `diffuser`: Implement the diffuser for 3 qubits
- `grover_circuit`: Create a Grover's algorithm circuit for cracking a 3-bit key

**Dependencies:**
- matplotlib
- qiskit
- qiskit_ibm_runtime

### quantum_rng.py

**Path:** `quantum_computing\quantum_rng.py`

**Description:**
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

**File Info:**
- Last modified: 2025-02-18 10:38:35
- Size: 3.8 KB
- Lines of code: 58 (of 93 total)

**Functions:**
- `quantum_random_number`: Generate a random number using quantum circuit

**Dependencies:**
- qiskit
- qiskit_ibm_runtime