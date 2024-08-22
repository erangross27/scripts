import torch
import torch.nn as nn
import torch.optim as optim
import torchvision
import torchvision.transforms as transforms
import time
import psutil
import GPUtil

# Check if CUDA is available
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

# Print GPU information if available
if torch.cuda.is_available():
    print(f"GPU: {torch.cuda.get_device_name(0)}")
    print(f"Number of GPUs: {torch.cuda.device_count()}")
    print(f"CUDA Version: {torch.version.cuda}")

# Define a simple CNN
class Net(nn.Module):
    def __init__(self):
        super(Net, self).__init__()
        self.conv1 = nn.Conv2d(1, 32, 3, 1)
        self.conv2 = nn.Conv2d(32, 64, 3, 1)
        self.dropout1 = nn.Dropout2d(0.25)
        self.dropout2 = nn.Dropout2d(0.5)
        self.fc1 = nn.Linear(9216, 128)
        self.fc2 = nn.Linear(128, 10)

    def forward(self, x):
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

train_dataset = torchvision.datasets.MNIST(root='./data', train=True, download=True, transform=transform)
test_dataset = torchvision.datasets.MNIST(root='./data', train=False, download=True, transform=transform)

train_loader = torch.utils.data.DataLoader(train_dataset, batch_size=64, shuffle=True)
test_loader = torch.utils.data.DataLoader(test_dataset, batch_size=1000, shuffle=False)

def train_and_test(device, num_epochs=5):
    model = Net().to(device)
    optimizer = optim.Adam(model.parameters())
    criterion = nn.CrossEntropyLoss()

    for epoch in range(num_epochs):
        model.train()
        start_time = time.time()
        for batch_idx, (data, target) in enumerate(train_loader):
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
    if torch.cuda.is_available():
        GPUs = GPUtil.getGPUs()
        gpu = GPUs[0]
        print(f"GPU Memory Usage: {gpu.memoryUsed}MB / {gpu.memoryTotal}MB")

# Function to print CPU memory usage
def print_cpu_memory():
    print(f"CPU Memory Usage: {psutil.virtual_memory().percent}%")

# Train on CPU
print("\nTraining on CPU:")
cpu_start_time = time.time()
print_cpu_memory()
train_and_test(torch.device("cpu"))
cpu_end_time = time.time()
print(f"Total CPU training time: {cpu_end_time - cpu_start_time:.2f} seconds")
print_cpu_memory()

# Train on GPU
if torch.cuda.is_available():
    print("\nTraining on GPU:")
    gpu_start_time = time.time()
    print_gpu_memory()
    train_and_test(torch.device("cuda"))
    gpu_end_time = time.time()
    print(f"Total GPU training time: {gpu_end_time - gpu_start_time:.2f} seconds")
    print_gpu_memory()

    # Calculate speedup
    speedup = (cpu_end_time - cpu_start_time) / (gpu_end_time - gpu_start_time)
    print(f"\nGPU speedup over CPU: {speedup:.2f}x")
