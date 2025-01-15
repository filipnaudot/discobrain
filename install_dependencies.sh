#!/bin/bash

# Script to set up a Python virtual environment and install dependencies.

set -e  # Exit immediately if a command exits with a non-zero status.
set -o pipefail  # Fail if any part of a pipe command fails.

INSTALL_LOCAL=false

# Parse command-line arguments
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --local)
            INSTALL_LOCAL=true
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
    shift
done

echo "Starting the installation process..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python3 is not installed. Please install it first."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "pip3 is not installed. Please install it first."
    exit 1
fi

CUDA_VERSION="cpu"

if $INSTALL_LOCAL; then
    # Check if NVIDIA GPU is present
    if command -v nvidia-smi &> /dev/null; then
        echo "NVIDIA GPU detected. Fetching CUDA version..."
        CUDA_VERSION=$(nvidia-smi | grep -oP 'CUDA Version: \K[0-9]+\.[0-9]+')
        if [[ -z "$CUDA_VERSION" ]]; then
            echo "Failed to detect CUDA version from nvidia-smi."
            CUDA_VERSION="cpu"  # Fallback to CPU
        else
            echo "Detected CUDA version: $CUDA_VERSION"
        fi
    else
        echo "No NVIDIA GPU detected. Falling back to CPU installation."
    fi
else
    echo "--local not provided. Skipping CUDA and PyTorch specific installations."
fi

# Create a virtual environment (if not already created)
VENV_DIR="env"
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating a Python virtual environment in $VENV_DIR..."
    python3 -m venv "$VENV_DIR"
fi

# Activate the virtual environment
source "$VENV_DIR/bin/activate"


echo "Installing dependencies..."
pip install --upgrade pip

if $INSTALL_LOCAL; then
    # Install PyTorch with appropriate CUDA or CPU version
    if [[ "$CUDA_VERSION" == "cpu" ]]; then
        echo "Installing CPU version of PyTorch..."
        pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
    else
        # Determine closest compatible CUDA version for PyTorch
        case $CUDA_VERSION in
            12.*) TORCH_CUDA="cu121" ;;  # Assume CUDA 12.1
            11.[8-9]*) TORCH_CUDA="cu118" ;;  # CUDA 11.8
            11.[0-7]*) TORCH_CUDA="cu117" ;;  # CUDA 11.7
            10.*) TORCH_CUDA="cu102" ;;  # Assume CUDA 10.2
            *) TORCH_CUDA="cpu" ;;  # Fallback to CPU
        esac
        echo "Installing PyTorch with CUDA support ($TORCH_CUDA)..."
        pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/$TORCH_CUDA
    fi
    
    # Install packages needed to run local LLM
    pip install transformers
    pip install bitsandbytes
    pip install 'accelerate>=0.26.0'
    pip install nvidia-ml-py
    pip install mistral
fi
# Install packages
pip install python-dotenv
pip install mistralai
pip install discord.py
pip install requests


echo "All dependencies have been installed successfully."

# Deactivate the virtual environment
deactivate

echo "Installation complete. To activate the virtual environment, run:"
echo "source $VENV_DIR/bin/activate"