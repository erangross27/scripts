"""
This script demonstrates the training and testing of a Convolutional Neural Network (CNN) on the MNIST dataset using PyTorch.
It compares the performance of training on CPU versus GPU (if available) and provides metrics on execution time and memory usage.

The script includes the following main components:
1. A simple CNN model definition (Net class)
2. Data loading and preprocessing for the MNIST dataset
3. A training and testing function (train_and_test)
4. Functions to print GPU and CPU memory usage
5. Execution of the training process on both CPU and GPU (if available)
6. Comparison of training times and calculation of GPU speedup over CPU

Requirements:
- PyTorch
- torchvision
- psutil
- GPUtil

The script will automatically use CUDA if available, otherwise it will default to CPU.
"""
import torch
import torch.nn as nn
import torch.optim as optim
import torchvision
import torchvision.transforms as transforms
import time
import psutil
import GPUtil

# Check if CUDA is available and set the device accordingly
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

# Print GPU information if available
if torch.cuda.is_available():
    print(f"GPU: {torch.cuda.get_device_name(0)}")
    print(f"Number of GPUs: {torch.cuda.device_count()}")
    print(f"CUDA Version: {torch.version.cuda}")

# Define a simple Convolutional Neural Network (CNN)
class Net(nn.Module):
    """
    Represents a net.
    """
    def __init__(self):
        """
        Special method __init__.
        """
        super(Net, self).__init__()
        # Define the layers of the CNN
        self.conv1 = nn.Conv2d(1, 32, 3, 1)
        self.conv2 = nn.Conv2d(32, 64, 3, 1)
        self.dropout1 = nn.Dropout2d(0.25)
        self.dropout2 = nn.Dropout2d(0.5)
        self.fc1 = nn.Linear(9216, 128)
        self.fc2 = nn.Linear(128, 10)

    def forward(self, x):
        """
        Forward based on x.
        """
        # Define the forward pass of the network
        x = self.conv1(x)
        x = nn.functional.relu(x)
        x = self.conv2(x)
        x = nn.functional.relu(x)
        x = nn.functional.max_pool2d(x, 2)
        x = self.dropout1(x)
        x = torch.flatten(x, 1)
        x = self.fc1(x)
        x = nn.functional.relu(x)
        x = self.dropout2(x)
        x = self.fc2(x)
        output = nn.functional.log_softmax(x, dim=1)
        return output

# Load and preprocess the MNIST dataset
transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize((0.1307,), (0.3081,))
])

# Load training and test datasets
train_dataset = torchvision.datasets.MNIST(root='./data', train=True, download=True, transform=transform)
test_dataset = torchvision.datasets.MNIST(root='./data', train=False, download=True, transform=transform)

# Create data loaders for batching
train_loader = torch.utils.data.DataLoader(train_dataset, batch_size=64, shuffle=True)
test_loader = torch.utils.data.DataLoader(test_dataset, batch_size=1000, shuffle=False)

def train_and_test(device, num_epochs=5):
    """
    Train and test based on device, num epochs.
    """
    # Initialize the model, optimizer, and loss function
    model = Net().to(device)
    optimizer = optim.Adam(model.parameters())
    criterion = nn.CrossEntropyLoss()

    for epoch in range(num_epochs):
        model.train()
        start_time = time.time()
        for batch_idx, (data, target) in enumerate(train_loader):
            # Move data to the specified device (CPU or GPU)
            data, target = data.to(device), target.to(device)
            optimizer.zero_grad()
            output = model(data)
            loss = criterion(output, target)
            loss.backward()
            optimizer.step()
            if batch_idx % 100 == 0:
                print(f'Train Epoch: {epoch} [{batch_idx * len(data)}/{len(train_loader.dataset)} '
                      f'({100. * batch_idx / len(train_loader):.0f}%)]\tLoss: {loss.item():.6f}')
        
        end_time = time.time()
        print(f"Epoch {epoch + 1} training time: {end_time - start_time:.2f} seconds")

        # Test the model
        model.eval()
        test_loss = 0
        correct = 0
        with torch.no_grad():
            for data, target in test_loader:
                data, target = data.to(device), target.to(device)
                output = model(data)
                test_loss += criterion(output, target).item()
                pred = output.argmax(dim=1, keepdim=True)
                correct += pred.eq(target.view_as(pred)).sum().item()

        test_loss /= len(test_loader.dataset)
        accuracy = 100. * correct / len(test_loader.dataset)
        print(f'Test set: Average loss: {test_loss:.4f}, Accuracy: {correct}/{len(test_loader.dataset)} ({accuracy:.2f}%)')

    return model

# Function to print GPU memory usage
def print_gpu_memory():
    """
    Print gpu memory.
    """
    if torch.cuda.is_available():
        GPUs = GPUtil.getGPUs()
        gpu = GPUs[0]
        print(f"GPU Memory Usage: {gpu.memoryUsed}MB / {gpu.memoryTotal}MB")

# Function to print CPU memory usage
def print_cpu_memory():
    """
    Print cpu memory.
    """
    print(f"CPU Memory Usage: {psutil.virtual_memory().percent}%")

# Train on CPU
print("\nTraining on CPU:")
cpu_start_time = time.time()
print_cpu_memory()
train_and_test(torch.device("cpu"))
cpu_end_time = time.time()
print(f"Total CPU training time: {cpu_end_time - cpu_start_time:.2f} seconds")
print_cpu_memory()

# Train on GPU if available
if torch.cuda.is_available():
    print("\nTraining on GPU:")
    gpu_start_time = time.time()
    print_gpu_memory()
    train_and_test(torch.device("cuda"))
    gpu_end_time = time.time()
    print(f"Total GPU training time: {gpu_end_time - gpu_start_time:.2f} seconds")
    print_gpu_memory()

    # Calculate and print the speedup of GPU over CPU
    speedup = (cpu_end_time - cpu_start_time) / (gpu_end_time - gpu_start_time)
    print(f"\nGPU speedup over CPU: {speedup:.2f}x")
