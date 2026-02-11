#!/bin/bash
set -e # Exit immediately if a command exits with a non-zero status.

# --- Configuration ---
# Determine the absolute path of the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Define directories relative to the script's location
SERVER_DIR="${SCRIPT_DIR}/server"
CLIENT_DIR="${SCRIPT_DIR}/client"
VENV_DIR="${SERVER_DIR}/venv"
REPO_DIR="${SERVER_DIR}/AngelinaReader"
REPO_URL="https://github.com/IlyaOvodov/AngelinaReader.git"
MODEL_WEIGHTS_DIR="${REPO_DIR}/weights"
MODEL_FILE="${MODEL_WEIGHTS_DIR}/model.t7"
MODEL_URL="http://ovdv.ru/files/retina_chars_eced60.clr.008"
LIBLOUIS_VERSION="3.33.0"
LIBLOUIS_ARCHIVE="liblouis-${LIBLOUIS_VERSION}.tar.gz"
LIBLOUIS_URL="https://github.com/liblouis/liblouis/releases/download/v${LIBLOUIS_VERSION}/${LIBLOUIS_ARCHIVE}"
LIBLOUIS_DIR="/usr/local/liblouis-${LIBLOUIS_VERSION}"

# --- Main Script ---

# # Check if script is run with sudo
# if [ "$EUID" -ne 0 ]; then 
#     echo "Please run as root or with sudo privileges"
#     exit 1
# fi

echo "Starting setup..."
echo "Script directory: ${SCRIPT_DIR}"
echo "Server directory: ${SERVER_DIR}"

# 1. Create virtual environment
echo ""
echo "Step 1: Creating Python virtual environment in '${VENV_DIR}'..."
if [ ! -d "${VENV_DIR}" ]; then
    # Create the server directory if it doesn't exist, needed for venv creation
    mkdir -p "${SERVER_DIR}"
    python3 -m venv "${VENV_DIR}"
    echo "Virtual environment created."
else
    echo "Virtual environment already exists in '${VENV_DIR}'. Skipping creation."
fi
# Define python and pip executables from venv for use in this script
VENV_PYTHON="${VENV_DIR}/bin/python3"
VENV_PIP="${VENV_DIR}/bin/pip3"

# 2. Clone AngelinaReader repository
echo ""
echo "Step 2: Cloning AngelinaReader repository into '${REPO_DIR}'..."
if [ ! -d "${REPO_DIR}" ]; then
    # Ensure server directory exists before cloning into it
    mkdir -p "${SERVER_DIR}"
    git clone --recursive "${REPO_URL}" "${REPO_DIR}"
    echo "Repository cloned."
else
    echo "Repository already exists in '${REPO_DIR}'. Skipping clone."
    echo "If you need to update, please pull changes manually from within '${REPO_DIR}'."
fi

# 3. Install Python dependencies
echo ""
echo "Step 3: Installing Python dependencies using pip from virtual environment..."

# Install from server/requirements.txt
SERVER_REQS_FILE="${SERVER_DIR}/requirements.txt"
if [ -f "${SERVER_REQS_FILE}" ]; then
    echo "Installing requirements from '${SERVER_REQS_FILE}'..."
    "${VENV_PIP}" install -r "${SERVER_REQS_FILE}"
else
    echo "Warning: Main requirements file '${SERVER_REQS_FILE}' not found. Skipping."
fi

# Install from server/AngelinaReader/requirements.txt
REPO_REQS_FILE="${REPO_DIR}/requirements.txt"
if [ -f "${REPO_REQS_FILE}" ]; then
    echo "Installing requirements from '${REPO_REQS_FILE}'..."
    "${VENV_PIP}" install -r "${REPO_REQS_FILE}"
    echo "Downgrading NumPy to < 2.0.0 for compatibility"
    "${VENV_PIP}" install "numpy<2.0.0"
else
    echo "Warning: AngelinaReader requirements file '${REPO_REQS_FILE}' not found. Skipping."
fi
echo "Dependency installation attempt finished."

# 4. Download model weights
echo ""
echo "Step 4: Downloading model weights..."
# Ensure weights directory exists
mkdir -p "${MODEL_WEIGHTS_DIR}"
echo "Downloading model to '${MODEL_FILE}' from '${MODEL_URL}'..."
wget -O "${MODEL_FILE}" "${MODEL_URL}"
echo "Model weights downloaded."

# 5. Install liblouis
echo ""
echo "Step 5: Installing liblouis..."

# Install m4 if not present
if ! command -v m4 &> /dev/null; then
    echo "Installing m4..."
    apt-get update
    apt-get install -y m4
fi

# Download and extract liblouis
echo "Downloading liblouis ${LIBLOUIS_VERSION}..."
cd /usr/local
wget "${LIBLOUIS_URL}"
tar xzf "${LIBLOUIS_ARCHIVE}"
rm "${LIBLOUIS_ARCHIVE}"

# Configure and install liblouis
echo "Configuring and installing liblouis..."
cd "${LIBLOUIS_DIR}"
./configure --enable-ucs4
make
make install
ldconfig

# Install Python bindings
echo "Installing Python bindings for liblouis..."
cd "${LIBLOUIS_DIR}/python"
"${VENV_PIP}" install setuptools
"${VENV_PYTHON}" setup.py install

# Run tests
echo "Running liblouis tests..."
"${VENV_PYTHON}" tests/test_louis.py

echo "liblouis installation completed."

# 6. Build the client


echo ""
echo "Step 6: Building the client..."
if ! command -v npm &> /dev/null; then
    echo "npm is not installed. Skipping client build step."
else
    if [ -d "${CLIENT_DIR}" ]; then
        echo "Building client in '${CLIENT_DIR}'..."
        cd "${CLIENT_DIR}"
        npm install
        npm run build
        echo "Client build completed."
    else
        echo "Client directory '${CLIENT_DIR}' does not exist. Skipping client build step."
    fi
fi

echo ""
echo "--------------------------------------------------------------------"
echo "Setup script finished"
echo ""
echo "IMPORTANT"
echo "===================================================================="
echo "In \'server/AngelinaReader/model/infer_retinanet.py\',"
echo "    Change line 12 from"
echo "        import local_config"
echo "    to"
echo "        from .. import local_config"
echo ""
echo "To start the server:"
echo "1. Make sure you are in the server directory"
echo "    cd ${SERVER_DIR}"
echo "2. Activate the Python virtual environment"
echo "    source venv/bin/activate"
echo "3. Start the server"
echo "    uvicorn app.main:app --host 0.0.0.0 --port 1897"
echo "--------------------------------------------------------------------"
