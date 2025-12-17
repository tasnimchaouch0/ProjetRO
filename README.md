# 🏥 VRP Santé - Healthcare Route Optimization System

A professional vehicle routing problem (VRP) solver for healthcare workforce scheduling with nurse skill matching, developed using Python, Gurobi optimization, and PyQt5.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![Gurobi](https://img.shields.io/badge/Gurobi-13.0-green)

## 📋 Table of Contents

- [Features](#features)
- [System Architecture](#system-architecture)
- [Requirements](#requirements)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Customization Guide](#customization-guide)
- [Optimization Model](#optimization-model)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

---

## ✨ Features

- **🎯 Skill-Based Matching**: Automatic assignment of nurses to patients based on required medical skills
- **📊 Real-Time Optimization**: Gurobi-powered mixed-integer programming solver
- **🖥️ Modern GUI**: Beautiful PyQt5 interface with interactive visualization
- **🗺️ Route Visualization**: Matplotlib-based route mapping with color-coded circuits
- **✏️ Live Editing**: Click-to-edit patient parameters with automatic re-optimization
- **🏗️ Object-Oriented Design**: Clean POO architecture with reusable domain models
- **🔄 Multi-Constraint Support**: 7 types of VRP constraints (capacity, time windows, skills, etc.)
- **📈 Scalable**: Handles up to 10 patients and 10 nurses (limited by Gurobi license)

### Supported Skills

- 💉 **Nursing** - General nursing care
- 🩹 **WoundCare** - Wound treatment and management
- 👶 **Pediatrics** - Child healthcare
- 🍬 **Diabetes** - Diabetes management
- 🏃 **Physio** - Physiotherapy services

---

## 🏛️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     GUI Layer (PyQt5)                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ MainWindow   │  │ PlotWidget   │  │ InfoDialog   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└────────────────────────────┬────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────┐
│                   Business Logic Layer                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ VRPThread    │  │ Solver       │  │ DataGenerator│      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└────────────────────────────┬────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────┐
│                     Domain Model (POO)                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Patient      │  │ Agent        │  │ VRPInstance  │      │
│  │ Depot        │  │              │  │              │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└────────────────────────────┬────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────┐
│              Optimization Engine (Gurobi)                   │
│                   Mixed-Integer Programming                 │
└─────────────────────────────────────────────────────────────┘
```

---

## 📦 Requirements

### System Requirements

- **Operating System**: Windows 10/11, macOS 10.14+, or Linux
- **Python**: 3.8 or higher
- **RAM**: Minimum 4GB (8GB recommended)
- **Disk Space**: 500MB free space

### Software Dependencies

```plaintext
Python 3.8+
Gurobi 13.0+ (with valid license)
PyQt5 5.15+
matplotlib 3.10+
numpy 2.3+
```

---

## 🚀 Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/tasnimchaouch0/health_gui.git
cd health_gui
```

### Step 2: Create Virtual Environment

**Windows (PowerShell):**
```powershell
python -m venv env
.\env\Scripts\Activate.ps1
```

**macOS/Linux:**
```bash
python3 -m venv env
source env/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Install Gurobi

#### Option A: Academic License (Free)
1. Register at [Gurobi Academic Program](https://www.gurobi.com/academia/academic-program-and-licenses/)
2. Download Gurobi Optimizer
3. Install and activate license:
```bash
grbgetkey YOUR-LICENSE-KEY
```

#### Option B: Commercial License
Contact [Gurobi Sales](https://www.gurobi.com/company/contact/) for licensing

### Step 5: Verify Installation

```bash
python -c "import gurobipy; print(gurobipy.gurobi.version())"
```

Should output: `(13, 0, 0)`

---

## ⚙️ Configuration

### 1. Environment Variables

Create a `.env` file in the project root:

```env
# Gurobi Configuration
GUROBI_HOME=/path/to/gurobi130
GRB_LICENSE_FILE=/path/to/gurobi.lic

# Application Settings
MAX_PATIENTS=10
MAX_NURSES=10
DEFAULT_SEED=42
```

### 2. Application Settings

Edit `app/config.py` (create if needed):

```python
# Model Configuration
MAX_PATIENTS = 10
MAX_NURSES = 10
SHIFT_DURATION = 300  # minutes
MAX_CAPACITY_PER_NURSE = 8

# Skill Types
SKILL_TYPES = [
    "Nursing",
    "WoundCare", 
    "Pediatrics",
    "Diabetes",
    "Physio"
]

# GUI Settings
WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 800
GRAPH_SIZE = (4, 3)  # inches

# Optimization Settings
OPTIMIZATION_TIMEOUT = 300  # seconds
MIP_GAP = 0.01  # 1% optimality gap
```

### 3. Gurobi Parameters

Modify `app/core/model_builder.py`:

```python
def build_vrp_model(patients, coords, s, skills_req, agents):
    m = Model("VRP_Model")
    
    # Gurobi Parameters
    m.setParam('TimeLimit', 300)        # Max solve time
    m.setParam('MIPGap', 0.01)          # 1% gap
    m.setParam('Threads', 4)            # CPU threads
    m.setParam('OutputFlag', 0)         # Silence output
    m.setParam('MIPFocus', 1)           # Focus on feasibility
    
    # ... rest of model
```

---

## 🎮 Usage

### Quick Start

```bash
python main.py
```

### GUI Operations

1. **Set Parameters**: Choose number of patients and nurses (max 10 each)
2. **Launch Optimization**: Click "🚀 Lancer l'optimisation"
3. **View Results**: 
   - Total distance in "📊 Résultat"
   - Nurse assignments in "👥 Équipe d'infirmiers"
   - Patient needs in "👤 Besoins des patients"
   - Route circuits in "🗺️ Circuits détaillés"
   - Visual map in graph area
4. **Edit Patient**: Click on any patient point to modify coordinates, duration, or skill
5. **Re-optimize**: Changes trigger automatic re-optimization

### Command Line Interface

```bash
# Run with custom parameters
python -c "
from app.gui.data_generator import generate_instance
from app.core.solver import solve_instance

instance = generate_instance(num_patients=5, num_agents=2, seed=42)
result, coords = solve_instance(data=instance)
print(result)
"
```

### Running Tests

```bash
# All tests
pytest app/tests/

# Specific test file
pytest app/tests/test_small_instances.py

# With coverage
pytest --cov=app app/tests/
```

---

## 📁 Project Structure

```
Projet RO/
├── main.py                      # Application entry point
├── README.md                    # This file
├── requirements.txt             # Python dependencies
├── .gitignore                  # Git ignore rules
│
├── app/
│   ├── __init__.py
│   │
│   ├── models/                  # Domain models (POO)
│   │   ├── __init__.py
│   │   └── domain.py           # Patient, Agent, Depot, VRPInstance classes
│   │
│   ├── core/                    # Optimization engine
│   │   ├── __init__.py
│   │   ├── model_builder.py    # Gurobi model construction
│   │   └── solver.py           # VRP solver logic
│   │
│   ├── gui/                     # User interface
│   │   ├── __init__.py
│   │   ├── main_window.py      # Main PyQt5 window
│   │   ├── plot_widget.py      # Matplotlib graph widget
│   │   └── data_generator.py   # Instance generation
│   │
│   ├── threads/                 # Async operations
│   │   ├── __init__.py
│   │   └── vrp_thread.py       # Background solver thread
│   │
│   ├── tests/                   # Unit tests
│   │   ├── __init__.py
│   │   ├── test_small_instances.py
│   │   ├── test_medium_instances.py
│   │   ├── test_skills_constraints.py
│   │   └── test_infeasible_cases.py
│   │
│   └── utils/                   # Utilities
│       ├── __init__.py
│       └── distance.py         # Distance calculations
│
└── env/                        # Virtual environment (not in git)
```

---

## 🔧 Customization Guide

### Adding New Skills

**1. Update skill list** in `app/gui/data_generator.py`:
```python
SKILL_TYPES = [
    "Nursing",
    "WoundCare",
    "Pediatrics",
    "Diabetes",
    "Physio",
    "Cardiology",      # NEW
    "Psychiatry",      # NEW
]
```

**2. Add emojis** in `app/gui/main_window.py` and `app/gui/plot_widget.py`:
```python
skill_emojis = {
    "Nursing": "💉",
    "WoundCare": "🩹",
    "Pediatrics": "👶",
    "Diabetes": "🍬",
    "Physio": "🏃",
    "Cardiology": "❤️",    # NEW
    "Psychiatry": "🧠",    # NEW
}
```

### Modifying Constraints

Edit `app/core/model_builder.py`:

```python
# Example: Add maximum distance constraint
MAX_ROUTE_DISTANCE = 50  # km

for k in agents:
    m.addConstr(
        quicksum(d[i, j] * x[i, j, k] for i, j in d) <= MAX_ROUTE_DISTANCE,
        name=f"max_distance_{k}"
    )
```

### Changing GUI Theme

Modify stylesheet in `app/gui/main_window.py`:

```python
self.setStyleSheet("""
    QMainWindow {
        background-color: #ffffff;  /* Change background */
    }
    QPushButton {
        background-color: #2ecc71;  /* Change button color */
        color: white;
    }
    /* ... more styles ... */
""")
```

### Using Custom Data

**Option 1: JSON Import**
```python
import json
from app.models.domain import VRPInstance

with open('my_data.json', 'r') as f:
    data = json.load(f)
    
instance = VRPInstance.from_dict(data)
result, coords = solve_instance(data=instance)
```

**Option 2: CSV Import**
```python
import pandas as pd
from app.models.domain import Patient, Agent, Depot, VRPInstance

# Load patients
df_patients = pd.read_csv('patients.csv')
patients = [Patient(**row.to_dict()) for _, row in df_patients.iterrows()]

# Load agents
df_agents = pd.read_csv('agents.csv')
df_agents['skills'] = df_agents['skills'].str.split(',')
agents = [Agent(**row.to_dict()) for _, row in df_agents.iterrows()]

# Create instance
depot = Depot(id=0, lat=0.0, lon=0.0)
instance = VRPInstance(depot=depot, agents=agents, patients=patients)
```

### Scaling Beyond 10x10

**For larger instances, you need:**

1. **Full Gurobi License** (commercial or academic unrestricted)
2. **Update validation** in `app/core/solver.py`:
```python
def solve_instance(...):
    # Remove or adjust these checks
    if len(instance.patients) > 50:  # NEW LIMIT
        raise ValueError(f"Too many patients")
```

3. **Optimize model performance**:
```python
m.setParam('Presolve', 2)      # Aggressive presolve
m.setParam('Cuts', 2)          # Aggressive cuts
m.setParam('Heuristics', 0.05) # 5% time on heuristics
```

---

## 🧮 Optimization Model

### Decision Variables

- **x[i,j,k]**: Binary variable, 1 if agent k travels from node i to node j
- **t[i,k]**: Continuous variable, arrival time of agent k at node i

### Objective Function

```
Minimize: Σ(i,j,k) distance[i,j] × x[i,j,k]
```

### Constraints

1. **Assignment**: Each patient visited exactly once by eligible agent
   ```
   Σ(i,k∈eligible) x[i,j,k] = 1  ∀j∈patients
   ```

2. **Flow Conservation**: What enters must exit
   ```
   Σ(i) x[i,j,k] = Σ(i) x[j,i,k]  ∀j∈patients, ∀k∈agents
   ```

3. **Depot Flow**: Agents start and return to depot
   ```
   Σ(j) x[0,j,k] = Σ(j) x[j,0,k]  ∀k∈agents
   ```

4. **MTZ Subtour Elimination**: Prevent disconnected routes
   ```
   t[j,k] ≥ t[i,k] + s[i] + d[i,j] - M(1 - x[i,j,k])  ∀i,j,k
   ```

5. **Time Windows**: Service within allowed times
   ```
   t[i,k] ≤ max_time  ∀i,k
   ```

6. **Capacity**: Respect maximum patients per agent
   ```
   Σ(i,j) x[i,j,k] ≤ capacity[k]  ∀k∈agents
   ```

7. **Shift Duration**: Total time within shift limits
   ```
   t[0,k] ≤ shift_duration[k]  ∀k∈agents
   ```

---

## 🧪 Testing

### Test Suite Structure

```
app/tests/
├── test_small_instances.py      # 5 patients, 2 agents
├── test_medium_instances.py     # 10 patients, 5 agents
├── test_skills_constraints.py   # Skill matching validation
├── test_infeasible_cases.py    # Error handling
└── test_performance.py          # Execution speed benchmarks
```

### Running Specific Tests

```bash
# Test skill constraints
pytest app/tests/test_skills_constraints.py -v

# Test with print output
pytest app/tests/test_small_instances.py -s

# Test with coverage report
pytest --cov=app --cov-report=html app/tests/
```

### Writing Custom Tests

```python
# app/tests/test_custom.py
from app.gui.data_generator import generate_instance
from app.core.solver import solve_instance

def test_custom_scenario():
    instance = generate_instance(num_patients=3, num_agents=2, seed=100)
    
    # Modify instance as needed
    instance.patients[0].required_skill = "Nursing"
    instance.agents[0].skills = ["Nursing", "WoundCare"]
    
    result, coords = solve_instance(data=instance)
    
    assert result, "Should find feasible solution"
    assert len(result) > 0, "Should have at least one route"
```

---

## 🐛 Troubleshooting

### Common Issues

#### 1. Gurobi License Error
```
Error: Model too large for size-limited license
```

**Solution**: 
- Reduce to max 10 patients and 10 nurses
- Or obtain full Gurobi license

#### 2. Import Error
```
ModuleNotFoundError: No module named 'PyQt5'
```

**Solution**:
```bash
pip install PyQt5
# or
pip install -r requirements.txt
```

#### 3. Infeasible Model
```
Status: INFEASIBLE
```

**Solution**:
- Ensure at least one agent has each required skill
- Check time window feasibility
- Verify capacity constraints are reasonable

#### 4. GUI Doesn't Open
```
QXcbConnection: Could not connect to display
```

**Solution** (Linux):
```bash
export DISPLAY=:0
python main.py
```

#### 5. Slow Optimization

**Solutions**:
- Reduce problem size
- Adjust Gurobi parameters:
```python
m.setParam('TimeLimit', 60)
m.setParam('MIPGap', 0.05)  # Accept 5% gap
```

---

## 🤝 Contributing

We welcome contributions! Please follow these guidelines:

### Development Setup

```bash
# Fork and clone
git clone https://github.com/YOUR-USERNAME/health_gui.git
cd health_gui

# Create branch
git checkout -b feature/your-feature-name

# Make changes and test
pytest app/tests/

# Commit with clear message
git commit -m "Add: Description of feature"

# Push and create PR
git push origin feature/your-feature-name
```

### Code Style

- **Python**: Follow PEP 8
- **Docstrings**: Use Google style
- **Type Hints**: Preferred for new code
- **Comments**: French or English accepted

### Pull Request Checklist

- [ ] Tests pass (`pytest app/tests/`)
- [ ] Code follows style guidelines
- [ ] Documentation updated
- [ ] Commit messages are clear
- [ ] No merge conflicts

---

## 📄 License

This project is licensed under the MIT License.

```
MIT License

Copyright (c) 2025 Tasnim Chaouch

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/tasnimchaouch0/health_gui/issues)
- **Email**: [Your contact email]
- **Documentation**: This README and inline code comments

---

## 🙏 Acknowledgments

- **Gurobi Optimization** - For the powerful MIP solver
- **PyQt5** - For the modern GUI framework
- **Matplotlib** - For visualization capabilities
- **NumPy** - For numerical computations

---

## 📊 Project Status

![Status](https://img.shields.io/badge/status-active-success.svg)
![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Maintained](https://img.shields.io/badge/maintained-yes-green.svg)

**Current Version**: 1.0.0  
**Last Updated**: December 2025  
**Production Ready**: Yes ✅

---

