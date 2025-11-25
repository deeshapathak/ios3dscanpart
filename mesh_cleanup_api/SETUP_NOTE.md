# Setup Note: Python Version Requirement

## Issue
Open3D (required for mesh processing) does not support Python 3.13 yet. It requires Python 3.10 or 3.11.

## Solutions

### Option 1: Install Python 3.11 (Recommended for local development)

**macOS:**
```bash
brew install python@3.11
python3.11 -m pip install -r requirements.txt
python3.11 main.py
```

**Or use pyenv:**
```bash
pyenv install 3.11.0
pyenv local 3.11.0
pip install -r requirements.txt
python main.py
```

### Option 2: Use Docker (Recommended for production)

```bash
docker build -t mesh-cleanup-api .
docker run -p 8000:8000 mesh-cleanup-api
```

### Option 3: Use a Virtual Environment with Python 3.11

```bash
# Create venv with Python 3.11
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

## Current Status
- ✅ FastAPI and other dependencies installed
- ❌ Open3D cannot be installed (Python 3.13 not supported)

Once you have Python 3.11 or use Docker, the server will run successfully.

