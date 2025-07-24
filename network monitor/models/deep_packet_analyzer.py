"""
Deep Learning-based Packet Analyzer for Network Traffic Analysis
"""

import numpy as np
import pandas as pd
try:
    from sklearn.preprocessing import StandardScaler
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.neural_network import MLPClassifier
except ImportError:
    print("Warning: scikit-learn not available. Some functionality will be limited.")

try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    from torch.utils.data import DataLoader, TensorDataset
except ImportError:
    print("Warning: PyTorch not available. Deep learning functionality will be limited.")
    torch = None
    nn = None

class DeepPacketAnalyzer:
    """
    A deep learning-based packet analyzer that can detect various types of network anomalies
    and malicious activities with higher accuracy than traditional methods.
    """
    
    def __init__(self, model_type='random_forest'):
        """
        Initialize the DeepPacketAnalyzer.
        
        Args:
            model_type (str): Type of model to use ('random_forest', 'neural_network', 'deep_nn')
        """
        self.model_type = model_type
        self.model = None
        self.scaler = StandardScaler()
        self.is_fitted = False
        self.feature_names = None
        
        # Initialize the appropriate model
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize the model based on the specified type."""
        try:
            if self.model_type == 'random_forest':
                self.model = RandomForestClassifier(
                    n_estimators=100,
                    max_depth=10,
                    random_state=42,
                    n_jobs=-1
                )
            elif self.model_type == 'neural_network':
                self.model = MLPClassifier(
                    hidden_layer_sizes=(100, 50),
                    activation='relu',
                    solver='adam',
                    max_iter=500,
                    random_state=42
                )
            elif self.model_type == 'deep_nn' and torch is not None:
                self.model = DeepNeuralNetwork(input_size=19)  # Based on FEATURE_NAMES count
            else:
                # Fallback to Random Forest if deep learning is not available
                self.model = RandomForestClassifier(
                    n_estimators=100,
                    max_depth=10,
                    random_state=42,
                    n_jobs=-1
                )
        except Exception as e:
            print(f"Error initializing model: {e}")
            # Fallback to a simple model
            self.model = RandomForestClassifier(n_estimators=10, max_depth=5, random_state=42)
    
    def fit(self, X, y):
        """
        Train the model with the provided data.
        
        Args:
            X (DataFrame or array): Feature data
            y (array): Labels (0 for normal, 1 for anomaly)
        """
        try:
            # Convert DataFrame to numpy array if needed
            if isinstance(X, pd.DataFrame):
                # Store feature names for later validation
                self.feature_names = X.columns.tolist()
                X_values = X.values.astype(np.float32)
            else:
                X_values = np.asarray(X, dtype=np.float32)
            
            # Scale the features
            X_scaled = self.scaler.fit_transform(X_values)
            
            # Train the model
            if self.model_type == 'deep_nn' and isinstance(self.model, DeepNeuralNetwork):
                self.model.train_model(X_scaled, y)
            else:
                # Ensure y is numpy array
                y_values = y.values if isinstance(y, pd.Series) else y
                y_values = y_values.astype(np.int64)
                self.model.fit(X_scaled, y_values)
            
            self.is_fitted = True
        except Exception as e:
            print(f"Error training model: {e}")
    
    def predict(self, X):
        """
        Predict anomalies in the provided data.
        
        Args:
            X (DataFrame or array): Feature data
            
        Returns:
            array: Predictions (0 for normal, 1 for anomaly)
        """
        try:
            if not self.is_fitted:
                raise ValueError("Model is not fitted yet. Call 'fit' first.")
            
            # Convert DataFrame to numpy array if needed
            if isinstance(X, pd.DataFrame):
                # Validate feature names if available
                if self.feature_names is not None and list(X.columns) != self.feature_names:
                    print("Warning: Feature names do not match training data")
                X_values = X.values.astype(np.float32)
            else:
                X_values = np.asarray(X, dtype=np.float32)
            
            # Scale the features
            X_scaled = self.scaler.transform(X_values)
            
            # Make predictions
            if self.model_type == 'deep_nn' and isinstance(self.model, DeepNeuralNetwork):
                return self.model.predict(X_scaled)
            else:
                return self.model.predict(X_scaled)
        except Exception as e:
            print(f"Error making predictions: {e}")
            return np.zeros(len(X)) if hasattr(X, '__len__') else np.array([0])
    
    def predict_proba(self, X):
        """
        Predict probabilities of anomalies in the provided data.
        
        Args:
            X (DataFrame or array): Feature data
            
        Returns:
            array: Prediction probabilities
        """
        try:
            if not self.is_fitted:
                raise ValueError("Model is not fitted yet. Call 'fit' first.")
            
            # Convert DataFrame to numpy array if needed
            if isinstance(X, pd.DataFrame):
                # Validate feature names if available
                if self.feature_names is not None and list(X.columns) != self.feature_names:
                    print("Warning: Feature names do not match training data")
                X_values = X.values.astype(np.float32)
            else:
                X_values = np.asarray(X, dtype=np.float32)
            
            # Scale the features
            X_scaled = self.scaler.transform(X_values)
            
            # Make probability predictions
            if self.model_type == 'deep_nn' and isinstance(self.model, DeepNeuralNetwork):
                return self.model.predict_proba(X_scaled)
            elif hasattr(self.model, 'predict_proba'):
                return self.model.predict_proba(X_scaled)
            else:
                # If predict_proba is not available, return binary predictions
                predictions = self.model.predict(X_scaled)
                # Convert to probability-like format
                proba = np.zeros((len(predictions), 2))
                proba[:, 0] = 1 - predictions  # Probability of normal
                proba[:, 1] = predictions       # Probability of anomaly
                return proba
        except Exception as e:
            print(f"Error making probability predictions: {e}")
            # Return default probabilities
            size = len(X) if hasattr(X, '__len__') else 1
            return np.zeros((size, 2))

class DeepNeuralNetwork:
    """
    A deep neural network implementation for packet analysis using PyTorch.
    """
    
    def __init__(self, input_size, hidden_sizes=[128, 64, 32], num_classes=2):
        """
        Initialize the deep neural network.
        
        Args:
            input_size (int): Number of input features
            hidden_sizes (list): Sizes of hidden layers
            num_classes (int): Number of output classes
        """
        if torch is None:
            raise ImportError("PyTorch is required for DeepNeuralNetwork")
        
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = self._build_network(input_size, hidden_sizes, num_classes).to(self.device)
        self.criterion = nn.CrossEntropyLoss()
        self.optimizer = optim.Adam(self.model.parameters(), lr=0.001)
        self.is_trained = False
    
    def _build_network(self, input_size, hidden_sizes, num_classes):
        """Build the neural network architecture."""
        layers = []
        prev_size = input_size
        
        # Add hidden layers
        for hidden_size in hidden_sizes:
            layers.append(nn.Linear(prev_size, hidden_size))
            layers.append(nn.ReLU())
            layers.append(nn.Dropout(0.2))
            prev_size = hidden_size
        
        # Add output layer
        layers.append(nn.Linear(prev_size, num_classes))
        
        return nn.Sequential(*layers)
    
    def train_model(self, X, y, epochs=100, batch_size=64):
        """
        Train the neural network.
        
        Args:
            X (array): Feature data
            y (array): Labels
            epochs (int): Number of training epochs
            batch_size (int): Batch size for training
        """
        try:
            # Convert to PyTorch tensors
            X_tensor = torch.FloatTensor(X).to(self.device)
            y_tensor = torch.LongTensor(y).to(self.device)
            
            # Create data loader
            dataset = TensorDataset(X_tensor, y_tensor)
            dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)
            
            # Training loop
            self.model.train()
            for epoch in range(epochs):
                total_loss = 0
                for batch_X, batch_y in dataloader:
                    # Forward pass
                    outputs = self.model(batch_X)
                    loss = self.criterion(outputs, batch_y)
                    
                    # Backward pass and optimization
                    self.optimizer.zero_grad()
                    loss.backward()
                    self.optimizer.step()
                    
                    total_loss += loss.item()
                
                # Print progress every 20 epochs
                if (epoch + 1) % 20 == 0:
                    print(f'Epoch [{epoch+1}/{epochs}], Loss: {total_loss/len(dataloader):.4f}')
            
            self.is_trained = True
        except Exception as e:
            print(f"Error training neural network: {e}")
    
    def predict(self, X):
        """
        Make predictions using the trained model.
        
        Args:
            X (array): Feature data
            
        Returns:
            array: Predictions
        """
        try:
            if not self.is_trained:
                raise ValueError("Model is not trained yet. Call 'train_model' first.")
            
            self.model.eval()
            with torch.no_grad():
                X_tensor = torch.FloatTensor(X).to(self.device)
                outputs = self.model(X_tensor)
                _, predicted = torch.max(outputs.data, 1)
                return predicted.cpu().numpy()
        except Exception as e:
            print(f"Error making predictions with neural network: {e}")
            return np.zeros(len(X))
    
    def predict_proba(self, X):
        """
        Predict probabilities using the trained model.
        
        Args:
            X (array): Feature data
            
        Returns:
            array: Prediction probabilities
        """
        try:
            if not self.is_trained:
                raise ValueError("Model is not trained yet. Call 'train_model' first.")
            
            self.model.eval()
            with torch.no_grad():
                X_tensor = torch.FloatTensor(X).to(self.device)
                outputs = self.model(X_tensor)
                probabilities = torch.softmax(outputs, dim=1)
                return probabilities.cpu().numpy()
        except Exception as e:
            print(f"Error making probability predictions with neural network: {e}")
            # Return default probabilities
            size = len(X)
            return np.zeros((size, 2))

# Sequence-based anomaly detector for temporal pattern analysis
class SequenceAnomalyDetector:
    """
    A sequence-based anomaly detector that analyzes temporal patterns in network traffic.
    """
    
    def __init__(self, sequence_length=10):
        """
        Initialize the sequence-based anomaly detector.
        
        Args:
            sequence_length (int): Length of sequences to analyze
        """
        self.sequence_length = sequence_length
        self.model = None
        self.scaler = StandardScaler()
        self.is_fitted = False
    
    def _create_sequences(self, data):
        """
        Create sequences from the data for temporal analysis.
        
        Args:
            data (array): Input data
            
        Returns:
            tuple: (sequences, targets)
        """
        try:
            sequences = []
            targets = []
            
            for i in range(len(data) - self.sequence_length):
                sequences.append(data[i:(i + self.sequence_length)])
                targets.append(data[i + self.sequence_length])
            
            return np.array(sequences), np.array(targets)
        except Exception as e:
            print(f"Error creating sequences: {e}")
            return np.array([]), np.array([])
    
    def fit(self, X):
        """
        Train the sequence-based anomaly detector.
        
        Args:
            X (DataFrame or array): Feature data
        """
        try:
            if isinstance(X, pd.DataFrame):
                X_values = X.values
            else:
                X_values = X
            
            # Scale the features
            X_scaled = self.scaler.fit_transform(X_values)
            
            # Create sequences
            sequences, targets = self._create_sequences(X_scaled)
            
            if len(sequences) == 0:
                print("Not enough data to create sequences")
                return
            
            # Reshape sequences for sklearn
            sequences_reshaped = sequences.reshape(sequences.shape[0], -1)
            
            # Train a Random Forest model
            self.model = RandomForestClassifier(n_estimators=50, random_state=42)
            self.model.fit(sequences_reshaped, targets.argmax(axis=1) if targets.ndim > 1 else targets)
            
            self.is_fitted = True
        except Exception as e:
            print(f"Error training sequence model: {e}")
    
    def predict(self, X):
        """
        Predict anomalies in sequences.
        
        Args:
            X (DataFrame or array): Feature data
            
        Returns:
            array: Predictions
        """
        try:
            if not self.is_fitted:
                raise ValueError("Model is not fitted yet. Call 'fit' first.")
            
            if isinstance(X, pd.DataFrame):
                X_values = X.values
            else:
                X_values = X
            
            # Scale the features
            X_scaled = self.scaler.transform(X_values)
            
            # Create sequences
            sequences, _ = self._create_sequences(X_scaled)
            
            if len(sequences) == 0:
                return np.array([])
            
            # Reshape sequences for sklearn
            sequences_reshaped = sequences.reshape(sequences.shape[0], -1)
            
            # Make predictions
            return self.model.predict(sequences_reshaped)
        except Exception as e:
            print(f"Error making sequence predictions: {e}")
            return np.array([])