---
title: "Experiment Environment Integration"
weight: 61
---

# Experiment Environment Integration

**Building Sionna PHY Abstraction Experiment Environment with Docker + Git**

Now let's integrate Docker, Git, and actual Sionna experiments to build a reproducible research environment. Experience the workflow used in real research through link-level simulations using PHY Abstraction.

## 🎯 Practice Objectives

1. **Create Integrated Project Structure** - Docker + Git + Sionna experiment environment
2. **Run PHY Abstraction Experiments** - Perform experiments with basic settings
3. **Verify Experiment Results** - Analyze TBLER and throughput
4. **Verify Environment Reproducibility** - Confirm identical result reproduction

## 📋 Step 1: Create Project Structure (10 minutes)

### Create Directory Structure

```bash
mkdir sionna-experiments
cd sionna-experiments

# Create project structure
mkdir -p configs scripts results
touch Dockerfile README.md .gitignore
```

**Final Structure:**
```
sionna-experiments/
├── Dockerfile          # Experiment environment definition
├── README.md           # Reproduction guide
├── .gitignore          # Git exclusion files
├── configs/            # Experiment configuration files
│   ├── baseline.yaml   # Basic experiment settings
│   └── extras.yaml     # Extended experiment settings
├── scripts/            # Experiment scripts
│   └── run_phy_abs.py  # PHY Abstraction experiment
└── results/            # Experiment results (Git excluded)
```

## 🐳 Step 2: Docker Environment Setup (5 minutes)

### Write Dockerfile

```dockerfile
FROM python:3.10-slim
WORKDIR /app

# Install Sionna and required packages
RUN pip install sionna tensorflow numpy matplotlib pyyaml

# Copy source code
COPY configs/ ./configs/
COPY scripts/ ./scripts/
COPY README.md .

# Set execution permissions
RUN chmod +x scripts/*.py

# Volume for result storage
VOLUME ["/app/results"]

# Default execution command
ENTRYPOINT ["python", "scripts/run_phy_abs.py"]
```

### Configure .gitignore

```gitignore
# Experiment results and large files
results/
data/
raw/
*.log
*.h5
*.png
__pycache__/
*.pyc

# AWS credentials
.aws/
*.pem
docker-credential*
.env
*.token

# IDE settings
.vscode/
.idea/
*.swp

# OS files
.DS_Store
Thumbs.db
```

## 🔬 Step 3: Sionna PHY Abstraction Experiment Script (15 minutes)

### Write scripts/run_phy_abs.py

```python
#!/usr/bin/env python3
import os
import sys
import yaml
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import tensorflow as tf

# Create results directory
os.makedirs("/app/results", exist_ok=True)
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

try:
    import sionna
    print(f"🔬 Sionna {sionna.__version__} experiment started")
except ImportError:
    print("❌ Sionna installation required: pip install sionna")
    exit(1)

from sionna.sys import PHYAbstraction, InnerLoopLinkAdaptation
from sionna.phy import config
from sionna.phy.utils import db_to_lin

# Sionna configuration
config.precision = 'single'
config.seed = 42

def load_config(path):
    """Load experiment configuration file"""
    with open(path) as f:
        return yaml.safe_load(f)

def run_phy_experiment(config):
    """Run PHY Abstraction experiment"""
    print(f"=== {config['experiment_id']} Experiment ===")
    
    # Initialize PHY Abstraction and Link Adaptation
    phy_abs = PHYAbstraction()
    illa = InnerLoopLinkAdaptation(phy_abs, config['bler_target'])
    
    # Lists for storing experiment results
    all_tbler = []
    all_throughput = []
    
    print(f"📊 Running {config['num_experiments']} experiments...")
    
    for exp in range(config['num_experiments']):
        # Generate SINR grid (random channel conditions)
        sinr_db = tf.random.uniform(
            [1, 1, config['num_ut'], 1],
            config['sinr_range'][0], 
            config['sinr_range'][1]
        ) + tf.random.normal(
            [config['num_sym'], config['num_sc'], config['num_ut'], 1], 
            stddev=2.0
        )
        sinr = db_to_lin(sinr_db)
        
        # MCS selection (Link Adaptation)
        mcs_index = illa(sinr=sinr, mcs_table_index=config['mcs_table_index'])
        
        # Perform PHY Abstraction
        num_decoded_bits, harq_feedback, sinr_eff, bler, tbler = phy_abs(
            mcs_index, 
            sinr=sinr, 
            mcs_table_index=config['mcs_table_index'],
            mcs_category=config['mcs_category']
        )
        
        # Collect results
        all_tbler.append(tbler.numpy().mean())
        all_throughput.append(num_decoded_bits.numpy().sum())
        
        if (exp + 1) % 5 == 0:
            print(f"  Progress: {exp + 1}/{config['num_experiments']}")
    
    # Calculate statistics
    results = {
        'tbler_mean': np.mean(all_tbler),
        'throughput_mean': np.mean(all_throughput),
        'tbler_std': np.std(all_tbler),
        'harq_nack_rate': 1 - np.mean(harq_feedback.numpy())
    }
    
    # Save results
    np.savez(f"results/{config['experiment_id']}.npz", **results)
    
    # Print results
    print(f"\n📈 Experiment Results:")
    print(f"  TBLER: {results['tbler_mean']:.3f} ± {results['tbler_std']:.3f}")
    print(f"  Throughput: {results['throughput_mean']/1024:.1f} kbit")
    print(f"  HARQ NACK Rate: {results['harq_nack_rate']:.3f}")
    
    # Create visualizations
    create_plots(config, all_tbler, results)
    
    return results

def create_plots(config, all_tbler, results):
    """Visualize experiment results"""
    plt.figure(figsize=(12, 4))
    
    # TBLER distribution histogram
    plt.subplot(121)
    plt.hist(all_tbler, bins=20, alpha=0.7, color='skyblue', edgecolor='black')
    plt.axvline(config['bler_target'], color='red', linestyle='--', 
                label=f'Target BLER: {config["bler_target"]}')
    plt.xlabel('TBLER')
    plt.ylabel('Frequency')
    plt.title('TBLER Distribution')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Summary bar chart
    plt.subplot(122)
    metrics = ['TBLER', 'Throughput(kbit)', 'NACK Rate']
    values = [
        results['tbler_mean'], 
        results['throughput_mean']/1024, 
        results['harq_nack_rate']
    ]
    
    bars = plt.bar(metrics, values, color=['lightcoral', 'lightgreen', 'lightsalmon'])
    plt.title(f'{config["experiment_id"]} Summary')
    plt.xticks(rotation=45)
    
    # Display values on bars
    for bar, value in zip(bars, values):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                f'{value:.3f}', ha='center', va='bottom')
    
    plt.tight_layout()
    plt.savefig(f"results/{config['experiment_id']}.png", 
                dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"📊 Graph saved: results/{config['experiment_id']}.png")

if __name__ == "__main__":
    # Configuration file path (default: baseline.yaml)
    config_file = sys.argv[1] if len(sys.argv) > 1 else "configs/baseline.yaml"
    
    try:
        config = load_config(config_file)
        results = run_phy_experiment(config)
        print("\n🏆 Experiment completed!")
        
    except FileNotFoundError:
        print(f"❌ Configuration file not found: {config_file}")
        exit(1)
    except Exception as e:
        print(f"❌ Error during experiment: {e}")
        exit(1)
```

## ⚙️ Step 4: Create Experiment Configuration Files (5 minutes)

### configs/baseline.yaml

```yaml
experiment_id: "phy-abs-baseline"
num_ut: 5              # Number of users
num_sym: 7             # Number of OFDM symbols
num_sc: 12             # Number of subcarriers
bler_target: 0.1       # Target BLER
mcs_table_index: 1     # MCS table index
mcs_category: 0        # 0: uplink, 1: downlink
sinr_range: [-5, 30]   # SINR range (dB)
num_experiments: 10    # Number of experiment repetitions
```

### configs/extras.yaml

```yaml
experiment_id: "phy-abs-extras"
num_ut: 8              # Increased number of users
num_sym: 14            # Increased number of OFDM symbols
num_sc: 24             # Increased number of subcarriers
bler_target: 0.05      # Stricter target BLER
mcs_table_index: 2     # Different MCS table
mcs_category: 1        # downlink
sinr_range: [-10, 35]  # Wider SINR range
num_experiments: 20    # More experiment repetitions
```

## 📖 Step 5: Write README.md (5 minutes)

Create a `README.md` file in the project root to document the experiment reproduction method:

```bash
cat > README.md << 'EOF'
# Sionna PHY Abstraction Experiment Environment

## 📋 Experiment Reproduction Method

### 1. Environment Preparation

git clone [repository-url]

cd sionna-experiments

### 2. Build Docker Image

docker build -t sionna-phy .

### 3. Run Experiments

- Basic experiment (baseline)

docker run --rm -v $(pwd)/results:/app/results sionna-phy configs/baseline.yaml

- Extended experiment (extras)

docker run --rm -v $(pwd)/results:/app/results sionna-phy configs/extras.yaml

### 4. Check Results

- results/phy-abs-baseline.npz: Numerical results
- results/phy-abs-baseline.png: Visualization results

## 🔬 Experiment Settings

- baseline: Basic 5G link-level simulation
- extras: Extended multi-user scenario

## 📊 Expected Results

- TBLER: Convergence near target value
- Throughput: Adaptive changes according to channel conditions
- HARQ Performance: Retransmission efficiency analysis

EOF
```

## 🚀 Step 6: Run First Experiment (10 minutes)

### Build Docker Image

```bash
docker build -t sionna-phy .
```

**Expected Output:**
```
[+] Building 45.2s (10/10) FINISHED
 => [1/6] FROM python:3.10-slim                    2.1s
 => [2/6] WORKDIR /app                             0.1s
 => [3/6] RUN pip install sionna tensorflow...    38.5s
 => [4/6] COPY configs/ ./configs/                 0.1s
 => [5/6] COPY scripts/ ./scripts/                 0.1s
 => [6/6] COPY README.md .                         0.1s
 => exporting to image                             4.2s
```

### Run Basic Experiment

```bash
docker run --rm -v $(pwd)/results:/app/results sionna-phy configs/baseline.yaml
```

**Expected Output:**
```
🔬 Sionna 1.2.1 experiment started
=== phy-abs-baseline Experiment ===
📊 Running 10 experiments...
  Progress: 5/10
  Progress: 10/10

📈 Experiment Results:
  TBLER: 0.098 ± 0.012
  Throughput: 1247.3 kbit
  HARQ NACK Rate: 0.089

📊 Graph saved: results/phy-abs-baseline.png
🏆 Experiment completed!
```

### Check Results

```bash
ls -la results/
```

**Expected Results:**
```
-rw-r--r-- 1 user user  2048 Jan 11 15:30 phy-abs-baseline.npz
-rw-r--r-- 1 user user 45123 Jan 11 15:30 phy-abs-baseline.png
```

## ✅ Practice Checklist

| Step | Verification | Status |
|------|-------------|--------|
| ✅ Project Structure | Directory and file creation completed | |
| ✅ Docker Build | `sionna-phy` image creation successful | |
| ✅ Experiment Execution | baseline experiment completed normally | |
| ✅ Result Generation | .npz, .png files created confirmed | |
| ✅ TBLER Convergence | Results near target BLER(0.1) | |

## 🛠️ Troubleshooting

| Problem | Solution |
|---------|----------|
| Docker build failure | `docker system prune -f` then retry |
| Sionna installation error | Confirm Python 3.10 image usage |
| No result files | Check volume mount path |
| Abnormal TBLER values | Check configuration file parameters |

## 🎉 Complete!

**Congratulations!** 

Now you can:

✅ Build Docker + Git + Sionna integrated environment  
✅ Run PHY Abstraction experiments  
✅ Analyze and visualize experiment results  
✅ Create reproducible experiment environment

**Next Step**: Learn collaboration workflows for managing this environment with Git and sharing through ECR.

---

**[Next: Collaboration Workflow Implementation →](/60-integrated-workflow/collaboration-workflow/)**