# Directory Scripts Documentation

## Available Scripts


### __init__.py

**Path:** `network monitor\models\__init__.py`

**Description:**
No description available

**File Info:**
- Last modified: 2025-02-18 10:38:35
- Size: 0.1 KB
- Lines of code: 2 (of 3 total)

**Dependencies:**
- persistent_anomaly_detector

### persistent_anomaly_detector.py

**Path:** `network monitor\models\persistent_anomaly_detector.py`

**Description:**
No description available

**File Info:**
- Last modified: 2025-02-18 10:38:35
- Size: 2.9 KB
- Lines of code: 61 (of 74 total)

**Classes:**
- `PersistentAnomalyDetector`: No documentation
  - Methods:
    - `__init__`: No documentation
    - `partial_fit`: Partially fit the model with new data
    - `predict`: Make predictions using the fitted model
    - `save_model`: Save the fitted model to a file
    - `load_model`: Load a previously saved model

**Dependencies:**
- joblib
- pandas
- sklearn