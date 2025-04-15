# Directory Scripts Documentation


## Available Scripts


### breast_cancer_detector.py

**Path:** `healthcare\breast_cancer_detector.py`

**Description:**
This script handles breast cancer detector that processes data, performs numerical operations.


**File Info:**
- Last modified: 2025-04-15 20:20:08
- Size: 4.6 KB
- Lines of code: 97 (of 136 total)

**Functions:**
- `main`: Main

**Classes:**
- `BreastCancerDetector`: Represents a breast cancer detector
  - Methods:
    - `__init__`: Special method __init__
    - `load_and_prepare_data`: Load and prepare the breast cancer dataset
    - `train_model`: Train the machine learning model
    - `predict_single_case`: Predict for a single case
    - `save_model`: Save the trained model
    - `load_model`: Load a trained model

**Dependencies:**
- joblib
- numpy
- pandas
- sklearn