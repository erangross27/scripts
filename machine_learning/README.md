# Directory Scripts Documentation


## Available Scripts


### mnist_cuda.py

**Path:** `machine_learning\mnist_cuda.py`

**Description:**
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


**File Info:**
- Last modified: 2025-04-15 20:20:08
- Size: 5.5 KB
- Lines of code: 110 (of 139 total)

**Functions:**
- `train`: Train based on model, device, train loader, optimizer, epoch
- `test`: Test based on model, device, test loader

**Classes:**
- `Net`: Represents a net
  - Methods:
    - `__init__`: Special method __init__
    - `forward`: Forward based on x

**Dependencies:**
- torch
- torchvision

### mnist_gpu_comparison.py

**Path:** `machine_learning\mnist_gpu_comparison.py`

**Description:**
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


**File Info:**
- Last modified: 2025-04-15 20:20:08
- Size: 6.1 KB
- Lines of code: 137 (of 174 total)

**Functions:**
- `train_and_test`: Train and test based on device, num epochs
- `print_gpu_memory`: Print gpu memory
- `print_cpu_memory`: Print cpu memory

**Classes:**
- `Net`: Represents a net
  - Methods:
    - `__init__`: Special method __init__
    - `forward`: Forward based on x

**Dependencies:**
- GPUtil
- psutil
- torch
- torchvision

### train_watermark_yolov5.py

**Path:** `machine_learning\train_watermark_yolov5.py`

**Description:**
YOLOv5 Training Script

This script sets up and runs a training process for YOLOv5 object detection model.
It includes the following main components:

1. Importing necessary libraries and YOLOv5 modules
2. Defining hyperparameters for YOLOv5 training
3. Setting up command-line argument parsing for various training options
4. Creating a data.yaml file with dataset information
5. Initializing device and callbacks
6. Running the training process

The script is designed to be run from the command line with various optional arguments
to customize the training process. It uses a pre-defined set of hyperparameters and
allows for further customization through command-line options.

Usage:
    python script_name.py [arguments]

For a full list of available arguments, run:
    python script_name.py --help


**File Info:**
- Last modified: 2025-04-15 20:20:08
- Size: 7.7 KB
- Lines of code: 119 (of 145 total)

**Functions:**
- `main`: Main

**Dependencies:**
- torch
- train
- utils
- yaml