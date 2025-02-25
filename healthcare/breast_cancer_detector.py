"""
This script handles breast cancer detector that processes data, performs numerical operations.
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import joblib

class BreastCancerDetector:
    """
    Represents a breast cancer detector.
    """
    def __init__(self):
        """
        Special method __init__.
        """
        self.model = None
        self.scaler = StandardScaler()
        
    def load_and_prepare_data(self, data_path):
        """Load and prepare the breast cancer dataset"""
        try:
            # Load the dataset
            data = pd.read_csv(data_path)
            
            # Separate features and target
            X = data.drop('diagnosis', axis=1)
            y = data['diagnosis'].map({'M': 1, 'B': 0})
            
            return X, y
            
        except Exception as e:
            print(f"Error loading data: {str(e)}")
            return None, None
    
    def train_model(self, X, y):
        """Train the machine learning model"""
        try:
            # Split the data into training and testing sets
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # Scale the features
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Initialize and train the model
            self.model = RandomForestClassifier(
                n_estimators=100,
                random_state=42
            )
            self.model.fit(X_train_scaled, y_train)
            
            # Make predictions and evaluate the model
            y_pred = self.model.predict(X_test_scaled)
            accuracy = accuracy_score(y_test, y_pred)
            report = classification_report(y_test, y_pred)
            
            return accuracy, report, X_test, y_test
            
        except Exception as e:
            print(f"Error training model: {str(e)}")
            return None, None, None, None
    
    def predict_single_case(self, features):
        """Predict for a single case"""
        try:
            # Scale the features
            features_scaled = self.scaler.transform([features])
            
            # Make prediction
            prediction = self.model.predict(features_scaled)
            probability = self.model.predict_proba(features_scaled)
            
            return prediction[0], probability[0]
            
        except Exception as e:
            print(f"Error making prediction: {str(e)}")
            return None, None
    
    def save_model(self, model_path):
        """Save the trained model"""
        try:
            joblib.dump((self.model, self.scaler), model_path)
            print("Model saved successfully")
        except Exception as e:
            print(f"Error saving model: {str(e)}")
    
    def load_model(self, model_path):
        """Load a trained model"""
        try:
            self.model, self.scaler = joblib.load(model_path)
            print("Model loaded successfully")
        except Exception as e:
            print(f"Error loading model: {str(e)}")

def main():
    """
    Main.
    """
    # Initialize the detector
    detector = BreastCancerDetector()
    
    # Load and prepare data
    data_path = "breast_cancer_data.csv"  # You would need the actual dataset
    X, y = detector.load_and_prepare_data(data_path)
    
    if X is not None and y is not None:
        # Train the model
        accuracy, report, X_test, y_test = detector.train_model(X, y)
        
        if accuracy is not None:
            print(f"\nModel Accuracy: {accuracy:.2f}")
            print("\nClassification Report:")
            print(report)
            
            # Save the model
            detector.save_model("breast_cancer_model.pkl")
            
            # Example of predicting a single case
            sample_features = X_test.iloc[0].values
            prediction, probability = detector.predict_single_case(sample_features)
            
            if prediction is not None:
                result = "Malignant" if prediction == 1 else "Benign"
                print(f"\nSample Prediction: {result}")
                print(f"Probability: Benign: {probability[0]:.2f}, "
                      f"Malignant: {probability[1]:.2f}")

if __name__ == "__main__":
    main()