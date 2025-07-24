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

        try:
            if not self.is_fitted or self.feature_names is None or set(X.columns) != set(self.feature_names):
                self.model = IsolationForest(contamination=self.contamination, random_state=42)
                self.model.fit(X)
                self.is_fitted = True
                self.feature_names = X.columns.tolist()
            else:
                self.model.fit(X)
            
            self.save_model()
        except Exception as e:
            # Handle any errors during model fitting
            print(f"Warning: Error during model fitting: {e}")

    def update_model(self, features):
        """
        Update the model with new features.
        This method provides compatibility with the original interface.
        """
        if isinstance(features, list):
            # Convert list to DataFrame if needed
            if len(features) > 0 and isinstance(features[0], list):
                # Assuming features is a list of feature vectors
                try:
                    df = pd.DataFrame(features, columns=getattr(self, 'feature_names', None))
                    self.partial_fit(df)
                except Exception as e:
                    print(f"Warning: Error converting features to DataFrame: {e}")
            else:
                print("Warning: Unexpected features format for model update")
        elif isinstance(features, pd.DataFrame):
            self.partial_fit(features)
        else:
            print("Warning: Unsupported features format for model update")

    def predict(self, X):
        """Make predictions using the fitted model."""
        if not self.is_fitted:
            raise ValueError("Model is not fitted yet. Call 'partial_fit' first.")
        return self.model.predict(X)

    def score_samples(self, X):
        """Calculate anomaly scores for samples."""
        if not self.is_fitted:
            raise ValueError("Model is not fitted yet. Call 'partial_fit' first.")
        return self.model.score_samples(X)

    def save_model(self):
        """Save the fitted model to a file."""
        try:
            if self.is_fitted:
                joblib.dump({
                    'model': self.model, 
                    'feature_names': self.feature_names,
                    'contamination': self.contamination
                }, self.model_path)
        except Exception as e:
            print(f"Warning: Error saving model: {e}")

    def load_model(self):
        """Load a previously saved model."""
        try:
            if os.path.exists(self.model_path):
                with warnings.catch_warnings():
                    warnings.filterwarnings("ignore", category=InconsistentVersionWarning)
                    loaded_data = joblib.load(self.model_path)
                
                if isinstance(loaded_data, dict):
                    self.model = loaded_data['model']
                    self.feature_names = loaded_data.get('feature_names', None)
                    # Update contamination if it was saved
                    if 'contamination' in loaded_data:
                        self.contamination = loaded_data['contamination']
                else:
                    self.model = loaded_data
                    self.feature_names = None
                
                self.is_fitted = True
                
                if not isinstance(self.model, IsolationForest):
                    raise ValueError("Loaded model is not an IsolationForest")
                
                if not hasattr(self.model, 'contamination') or not hasattr(self.model, 'random_state'):
                    raise ValueError("Loaded model is missing expected attributes")
        except Exception as e:
            print(f"Warning: Error loading model: {e}")
            self.model = IsolationForest(contamination=self.contamination, random_state=42)
            self.is_fitted = False
            self.feature_names = None