"""
This script handles persistent anomaly detector that processes data.
"""

import os
import warnings
import joblib
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.exceptions import InconsistentVersionWarning

class PersistentAnomalyDetector:
    """
    Represents a persistent anomaly detector.
    """
    def __init__(self, model_path='anomaly_model.joblib', contamination=0.01):
        """
        Special method __init__.
        """
        self.model_path = model_path
        self.contamination = contamination
        self.model = IsolationForest(contamination=contamination, random_state=42)
        self.is_fitted = False
        self.feature_names = None

    def partial_fit(self, X):
        """Partially fit the model with new data."""
        if not isinstance(X, pd.DataFrame):
            return

        if X.empty:
            return

        if not self.is_fitted or self.feature_names is None or set(X.columns) != set(self.feature_names):
            self.model = IsolationForest(contamination=self.contamination, random_state=42)
            self.model.fit(X)
            self.is_fitted = True
            self.feature_names = X.columns.tolist()
        else:
            self.model.fit(X)
        
        self.save_model()

    def predict(self, X):
        """Make predictions using the fitted model."""
        if not self.is_fitted:
            raise ValueError("Model is not fitted yet. Call 'partial_fit' first.")
        return self.model.predict(X)

    def save_model(self):
        """Save the fitted model to a file."""
        if self.is_fitted:
            joblib.dump({
                'model': self.model, 
                'feature_names': self.feature_names
            }, self.model_path)

    def load_model(self):
        """Load a previously saved model."""
        if os.path.exists(self.model_path):
            try:
                with warnings.catch_warnings():
                    warnings.filterwarnings("ignore", category=InconsistentVersionWarning)
                    loaded_data = joblib.load(self.model_path)
                
                if isinstance(loaded_data, dict):
                    self.model = loaded_data['model']
                    self.feature_names = loaded_data['feature_names']
                else:
                    self.model = loaded_data
                    self.feature_names = None
                
                self.is_fitted = True
                
                if not isinstance(self.model, IsolationForest):
                    raise ValueError("Loaded model is not an IsolationForest")
                
                if not hasattr(self.model, 'contamination') or not hasattr(self.model, 'random_state'):
                    raise ValueError("Loaded model is missing expected attributes")
                
            except Exception as e:
                self.model = IsolationForest(contamination=self.contamination, random_state=42)
                self.is_fitted = False
                self.feature_names = None
