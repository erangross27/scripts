# Directory Scripts Documentation


## Available Scripts


### __init__.py

**Path:** `network monitor\models\__init__.py`

**Description:**
This script handles   init  .


**File Info:**
- Last modified: 2025-04-15 20:20:08
- Size: 0.2 KB
- Lines of code: 5 (of 7 total)

**Dependencies:**
- persistent_anomaly_detector
- deep_packet_analyzer

### persistent_anomaly_detector.py

**Path:** `network monitor\models\persistent_anomaly_detector.py`

**Description:**
This script handles persistent anomaly detector that processes data.


**File Info:**
- Last modified: 2025-04-15 20:20:08
- Size: 3.1 KB
- Lines of code: 70 (of 84 total)

**Classes:**
- `PersistentAnomalyDetector`: Represents a persistent anomaly detector
  - Methods:
    - `__init__`: Special method __init__
    - `partial_fit`: Partially fit the model with new data
    - `predict`: Make predictions using the fitted model
    - `save_model`: Save the fitted model to a file
    - `load_model`: Load a previously saved model

**Dependencies:**
- joblib
- pandas
- sklearn

### deep_packet_analyzer.py

**Path:** `network monitor\models\deep_packet_analyzer.py`

**Description:**
This script implements deep learning models for advanced packet analysis and anomaly detection.


**File Info:**
- Last modified: 2025-04-15 20:20:08
- Size: 0 KB
- Lines of code: 0 (of 0 total)

**Classes:**
- `DeepPacketAnalyzer`: Deep learning-based packet analyzer with multiple model options
  - Methods:
    - `__init__`: Initialize with model type (Random Forest, Neural Network, or Deep NN)
    - `fit`: Train the model with provided data
    - `predict`: Predict anomalies in data
    - `predict_proba`: Predict probabilities of anomalies

- `DeepNeuralNetwork`: PyTorch-based deep neural network for packet analysis
  - Methods:
    - `__init__`: Initialize the neural network
    - `train_model`: Train the neural network
    - `predict`: Make predictions using the trained model
    - `predict_proba`: Predict probabilities using the trained model

- `SequenceAnomalyDetector`: Sequence-based anomaly detector for temporal pattern analysis
  - Methods:
    - `__init__`: Initialize with sequence length
    - `fit`: Train the sequence-based model
    - `predict`: Predict anomalies in sequences

**Dependencies:**
- sklearn
- torch (optional)
- pandas
- numpy