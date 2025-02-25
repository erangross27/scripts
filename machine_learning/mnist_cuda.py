"""
MNIST Digit Classification using Convolutional Neural Network

This script implements a Convolutional Neural Network (CNN) to classify handwritten digits
from the MNIST dataset using PyTorch. It includes the following main components:

1. Data loading and preprocessing using torchvision
2. Definition of a CNN architecture (Net class)
3. Training and testing functions
4. Model training loop with performance evaluation

The script uses CUDA if available, otherwise falls back to CPU computation.
It trains the model for 10 epochs and prints training progress, test set accuracy,
and total training time.

Dependencies:
- torch
- torchvision
- time

Usage:
Run the script to train and evaluate the model on the MNIST dataset.
The script will automatically download the dataset if not already present.

Note: Adjust hyperparameters like batch size, learning rate, and number of epochs as needed.
"""
import torch
import torch.nn as nn
import torch.optim as optim
import torchvision
import torchvision.transforms as transforms
import time

# Check if CUDA is available and set the device accordingly
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

# Define a simple neural network
class Net(nn.Module):
    """
    Represents a net.
    """
    def __init__(self):
        """
        Special method __init__.
        """
        super(Net, self).__init__()
        # Define the layers of the network
        self.conv1 = nn.Conv2d(1, 32, 3, 1)  # First convolutional layer
        self.conv2 = nn.Conv2d(32, 64, 3, 1)  # Second convolutional layer
        self.dropout1 = nn.Dropout2d(0.25)  # Dropout layer to prevent overfitting
        self.dropout2 = nn.Dropout2d(0.5)  # Another dropout layer
        self.fc1 = nn.Linear(9216, 128)  # First fully connected layer
        self.fc2 = nn.Linear(128, 10)  # Output layer (10 classes for MNIST)
    def forward(self, x):
        """
        Forward based on x.
        """
        # Define the forward pass of the network
        x = self.conv1(x)
        x = nn.functional.relu(x)  # Apply ReLU activation
        x = self.conv2(x)
        x = nn.functional.relu(x)
        x = nn.functional.max_pool2d(x, 2)  # Apply max pooling
        x = self.dropout1(x)
        x = torch.flatten(x, 1)  # Flatten the tensor
        x = self.fc1(x)
        x = nn.functional.relu(x)
        x = self.dropout2(x)
        x = self.fc2(x)
        output = nn.functional.log_softmax(x, dim=1)  # Apply log softmax
        return output

# Load and preprocess the MNIST dataset
transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize((0.1307,), (0.3081,))  # Normalize with mean and std dev of MNIST
])

# Load training and test datasets
train_dataset = torchvision.datasets.MNIST(root='./data', train=True, download=True, transform=transform)
test_dataset = torchvision.datasets.MNIST(root='./data', train=False, download=True, transform=transform)

# Create data loaders
train_loader = torch.utils.data.DataLoader(train_dataset, batch_size=64, shuffle=True)
test_loader = torch.utils.data.DataLoader(test_dataset, batch_size=1000, shuffle=False)

# Initialize the model, loss function, and optimizer
model = Net().to(device)  # Move model to GPU if available
criterion = nn.CrossEntropyLoss()  # Use Cross Entropy Loss
optimizer = optim.Adam(model.parameters())  # Use Adam optimizer

# Training function
def train(model, device, train_loader, optimizer, epoch):
    """
    Train based on model, device, train loader, optimizer, epoch.
    """
    model.train()  # Set model to training mode
    for batch_idx, (data, target) in enumerate(train_loader):
        data, target = data.to(device), target.to(device)  # Move data to device
        optimizer.zero_grad()  # Zero the gradient buffers
        output = model(data)  # Forward pass
        loss = criterion(output, target)  # Compute loss
        loss.backward()  # Backpropagation
        optimizer.step()  # Update weights
        if batch_idx % 100 == 0:  # Print progress every 100 batches
            print(f'Train Epoch: {epoch} [{batch_idx * len(data)}/{len(train_loader.dataset)} '
                  f'({100. * batch_idx / len(train_loader):.0f}%)]\tLoss: {loss.item():.6f}')

# Testing function
def test(model, device, test_loader):
    """
    Test based on model, device, test loader.
    """
    model.eval()  # Set model to evaluation mode
    test_loss = 0
    correct = 0
    with torch.no_grad():  # Disable gradient calculation
        for data, target in test_loader:
            data, target = data.to(device), target.to(device)
            output = model(data)  # Forward pass
            test_loss += criterion(output, target).item()  # Sum up batch loss
            pred = output.argmax(dim=1, keepdim=True)  # Get the index of the max log-probability
            correct += pred.eq(target.view_as(pred)).sum().item()  # Compute number of correct predictions

    test_loss /= len(test_loader.dataset)
    print(f'\nTest set: Average loss: {test_loss:.4f}, '
          f'Accuracy: {correct}/{len(test_loader.dataset)} '
          f'({100. * correct / len(test_loader.dataset):.2f}%)\n')

# Train and test the model
start_time = time.time()

for epoch in range(1, 11):  # Train for 10 epochs
    train(model, device, train_loader, optimizer, epoch)
    test(model, device, test_loader)

end_time = time.time()
print(f"Total training time: {end_time - start_time:.2f} seconds")
