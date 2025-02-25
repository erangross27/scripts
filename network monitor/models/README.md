# Directory Scripts Documentation

## Available Scripts


### __init__.py

**Path:** `network monitor\models\__init__.py`

**Description:**
This script handles   init  .

**File Info:**
- Last modified: 2025-02-25 08:16:29
- Size: 0.2 KB
- Lines of code: 5 (of 7 total)

**Dependencies:**
- persistent_anomaly_detector

### persistent_anomaly_detector.py

**Path:** `network monitor\models\persistent_anomaly_detector.py`

**Description:**
This script handles persistent anomaly detector that processes data.

**File Info:**
- Last modified: 2025-02-25 08:16:29
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