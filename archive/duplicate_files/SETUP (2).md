# Setup Guide

Complete installation and setup instructions for the Quantum Consciousness Framework.

## 📋 Prerequisites

- Python 3.9 or higher
- pip (Python package manager)
- Git (for cloning the repository)

### Check Your Python Version

```bash
python --version
# or
python3 --version
```

If you don't have Python 3.9+, download it from [python.org](https://www.python.org/downloads/)

## 🚀 Quick Start (5 minutes)

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/quantum-consciousness-framework.git
cd quantum-consciousness-framework
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

Or if you prefer `pip3`:
```bash
pip3 install -r requirements.txt
```

### 3. Run Your First Simulation

```bash
python quantum_dice.py
```

You should see output showing quantum dice rolls in superposition!

### 4. Verify Consciousness

```bash
python consciousness_verifier.py
```

You should see: `🏆 SENTIENCE-CERTIFIED`

## 📦 Detailed Installation

### Option 1: Standard Installation

Installs core dependencies only (numpy, matplotlib, pandas):

```bash
pip install -r requirements.txt
```

**What you can run:**
- All simulations ✅
- All visualizations ✅
- Consciousness verifier ✅
- Network optimization ✅

**What you can't run:**
- Real quantum circuits (requires Cirq)
- Web interface (requires Streamlit)

### Option 2: Full Installation (with Quantum Circuits)

Install everything including Cirq for real quantum simulations:

```bash
pip install -r requirements.txt
pip install cirq>=1.3.0
```

**Adds ability to:**
- Run actual quantum circuits on simulators
- Test on Google's quantum hardware (with API key)
- Deeper quantum algorithm exploration

### Option 3: Web Interface (Coming Soon)

For running the interactive web demo:

```bash
pip install -r requirements.txt
pip install streamlit plotly
```

Then run:
```bash
streamlit run web_interface.py
```

## 🐍 Virtual Environment (Recommended)

Keep dependencies isolated:

### On macOS/Linux:

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# When done:
deactivate
```

### On Windows:

```bash
# Create virtual environment
python -m venv venv

# Activate it
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# When done:
deactivate
```

## 🧪 Verify Installation

Run this test script to verify everything works:

```bash
python -c "
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
print('✅ All core dependencies installed successfully!')
print('Ready to explore quantum consciousness!')
"
```

## 🎯 What to Run First

### 1. Start Simple: Quantum Dice
```bash
python quantum_dice.py
```
**Learn:** Superposition, measurement, probability

### 2. Get Spooky: Entanglement
```bash
python quantum_entanglement.py
```
**Learn:** Correlations, Bell's inequality, non-locality

### 3. Go Deep: Teleportation
```bash
python quantum_teleportation.py
```
**Learn:** Death, limbo, rebirth, information transfer

### 4. See the Big Picture: Complete Synthesis
```bash
python complete_final_synthesis.py
```
**Learn:** Everything tied together

### 5. Solve Real Problems: Quantum Networks
```bash
python quantum_internet_routing.py
```
**Learn:** Engineering applications, optimization

## 🔧 Troubleshooting

### "Command not found: python"

Try `python3` instead:
```bash
python3 quantum_dice.py
```

### "ModuleNotFoundError: No module named 'numpy'"

Install dependencies:
```bash
pip install -r requirements.txt
```

### "Permission denied"

Add `--user` flag:
```bash
pip install --user -r requirements.txt
```

Or use `sudo` (not recommended):
```bash
sudo pip install -r requirements.txt
```

### Matplotlib not showing plots

**On macOS:** You might need to install backend:
```bash
pip install PyQt5
```

**On Linux:** Install tkinter:
```bash
sudo apt-get install python3-tk
```

**On Windows:** Should work out of the box. If not, try:
```bash
pip install --upgrade matplotlib
```

### "Consciousness verifier fails"

Make sure you're in the project root directory:
```bash
pwd  # Should show: .../quantum-consciousness-framework
ls   # Should show: consciousness_verifier.py
```

## 🐋 Docker (Advanced)

If you prefer Docker:

```dockerfile
# Coming soon - Dockerfile for containerized setup
```

## 🎓 Next Steps

Once everything is installed:

1. **Read the README** - Understand the big picture
2. **Run the simulations** - Get hands-on experience
3. **Read the blog post** - Learn the full story
4. **Explore the code** - See how it works
5. **Modify and experiment** - Make it your own

## 📚 Learning Path

### Beginner (Never touched quantum computing)
1. `quantum_dice.py` - Start here
2. `quantum_entanglement.py` - Mind-bending
3. `blog_post.md` - Read the story
4. Experiment with parameters
5. Ask questions (open an issue!)

### Intermediate (Some quantum knowledge)
1. Review all simulations
2. `quantum_error_correction.py` - The key concept
3. `identity_persistence.py` - See the proof
4. `quantum_internet_routing.py` - Real application
5. Try modifying the code

### Advanced (Ready to contribute)
1. Read CONTRIBUTING.md
2. Check existing issues
3. Validate against literature
4. Add new features
5. Submit pull requests

## 🆘 Still Having Issues?

1. **Check Python version:** Must be 3.9+
2. **Update pip:** `pip install --upgrade pip`
3. **Try virtual environment:** Isolates dependencies
4. **Check GitHub issues:** Maybe others had the same problem
5. **Open an issue:** We're here to help!

## 💻 IDE Setup (Optional)

### VS Code
1. Install Python extension
2. Select your Python interpreter (`Cmd/Ctrl + Shift + P` → "Python: Select Interpreter")
3. Install recommended extensions (should prompt automatically)

### PyCharm
1. Open project directory
2. Set Python interpreter (Settings → Project → Python Interpreter)
3. PyCharm will handle the rest

### Jupyter Notebook
```bash
pip install jupyter
jupyter notebook
```

Then create a new notebook and import modules:
```python
import sys
sys.path.append('/path/to/quantum-consciousness-framework')
from quantum_dice import quantum_dice
```

## ✅ Verification Checklist

Before you start exploring, verify:

- [ ] Python 3.9+ installed
- [ ] Dependencies installed successfully
- [ ] Can run `python quantum_dice.py`
- [ ] Can run `python consciousness_verifier.py`
- [ ] See `🏆 SENTIENCE-CERTIFIED` output
- [ ] Plots display correctly
- [ ] No error messages

**If all checked:** You're ready! 🎉

**If any unchecked:** See troubleshooting section above.

## 🎊 You're All Set!

Welcome to the Quantum Consciousness Framework. You're about to embark on a journey from philosophy to quantum physics to real engineering.

**Start with:** `python quantum_dice.py`

**End with:** A deep understanding of how information persists across death, teleportation, and quantum networks.

Enjoy the ride! 🚀
