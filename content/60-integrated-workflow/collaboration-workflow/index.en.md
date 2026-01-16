---
title: "Collaboration Workflow Implementation"
weight: 62
---

# Collaboration Workflow Implementation

**Experiment Sharing and Reproducibility Verification through Git + ECR**

Now let's implement a complete collaboration workflow by managing the Sionna experiment environment built in the previous step with Git version control and sharing it with teams through ECR. Practice the entire process from tracking experiment changes to reproducing results among team members.

## 🎯 Practice Objectives

1. **Git Version Control** - Systematic tracking of experiment changes
2. **ECR Image Sharing** - Team sharing of experiment environments
3. **Collaboration Reproducibility Verification** - Confirming identical results among team members
4. **Version-based Result Comparison** - Performance analysis according to experiment changes

## 📋 Step 1: Initialize Git Repository (10 minutes)

### Create Git Repository

```bash
cd sionna-experiments

# Initialize Git repository
git init
git config user.name "Workshop Participant"
git config user.email "participant@example.com"
```

### Initial Commit

```bash
# Add all files (.gitignore applied)
git add .

# Initial commit
git commit -m "init: Build Sionna PHY Abstraction experiment environment

- Docker-based Sionna experiment environment
- PHY Abstraction baseline configuration
- Reproducible experiment script composition"
```

### Check Commit

```bash
git log --oneline
```

**Expected Output:**
```
a1b2c3d (HEAD -> main) init: Build Sionna PHY Abstraction experiment environment
```

## 🔄 Step 2: Track Experiment Changes (15 minutes)

### Modify extras Experiment Configuration

Modify existing `configs/extras.yaml` to more challenging settings:

```yaml
experiment_id: "phy-abs-extras-v2"
num_ut: 12             # Significantly increased number of users
num_sym: 14            # Number of OFDM symbols
num_sc: 48             # Significantly increased number of subcarriers
bler_target: 0.01      # Very strict target BLER
mcs_table_index: 2     # High-order MCS table
mcs_category: 1        # downlink
sinr_range: [-15, 40]  # Very wide SINR range
num_experiments: 30    # More experiment repetitions
```

### Run Experiment and Check Results

```bash
# Run experiment with new configuration
docker run --rm -v $(pwd)/results:/app/results sionna-phy configs/extras.yaml
```

**Expected Output:**
```
🔬 Sionna 1.2.1 experiment started
=== phy-abs-extras-v2 Experiment ===
📊 Running 30 experiments...
  Progress: 5/30
  Progress: 10/30
  Progress: 15/30
  Progress: 20/30
  Progress: 25/30
  Progress: 30/30

📈 Experiment Results:
  TBLER: 0.009 ± 0.003
  Throughput: 2847.6 kbit
  HARQ NACK Rate: 0.008

📊 Graph saved: results/phy-abs-extras-v2.png
🏆 Experiment completed!
```

### Commit Changes

```bash
# Check changed files
git status

# Check configuration file changes
git diff configs/extras.yaml

# Commit changes
git add configs/extras.yaml
git commit -m "feat: [extras-v2] Add large-scale multi-user scenario

- Number of users: 8 → 12
- Subcarriers: 24 → 48  
- Target BLER: 0.05 → 0.01 (stricter)
- Experiments: 20 → 30 repetitions
- Expected throughput improvement and HARQ performance enhancement"
```

### Update README

Add new experiment configuration to README.md like below:

```markdown
# Sionna PHY Abstraction Experiment Environment

## 📋 Experiment Reproduction Method

### 1. Environment Preparation
```bash
git clone <repository-url>
cd sionna-experiments
git checkout <commit-hash>  # For specific version reproduction
```

### 2. Build Docker Image
```bash
docker build -t sionna-phy .
```

### 3. Run Experiments
```bash
# Basic experiment (baseline)
docker run --rm -v $(pwd)/results:/app/results sionna-phy configs/baseline.yaml

# Extended experiment v1 (extras)
docker run --rm -v $(pwd)/results:/app/results sionna-phy configs/extras.yaml
```

## 🔬 Experiment Configuration Comparison

| Configuration | baseline | extras-v2 |
|---------------|----------|-----------|
| Number of users | 5 | 12 |
| Subcarriers | 12 | 48 |
| Target BLER | 0.1 | 0.01 |
| Experiments | 10 | 30 |
| Expected throughput | ~1.2 Mbit | ~2.8 Mbit |

## 📊 Reproducibility Verification

Expected results when running from the same commit:
- baseline: TBLER ~0.098, throughput ~1247 kbit
- extras-v2: TBLER ~0.009, throughput ~2847 kbit
```

### Commit README Changes

```bash
git add README.md
git commit -m "docs: Add extras-v2 experiment configuration and reproduction guide"
```

## ☁️ Step 3: ECR Image Sharing (15 minutes)

### Create ECR Repository

```bash
# Create ECR repository
aws ecr create-repository \
    --repository-name sionna-experiments \
    --region ap-northeast-2
```

### Tag and Push Docker Image

```bash
# Get account ID
export ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

# ECR login
aws ecr get-login-password --region ap-northeast-2 | \
    docker login --username AWS --password-stdin \
    $ACCOUNT_ID.dkr.ecr.ap-northeast-2.amazonaws.com

# Get current commit hash
COMMIT=$(git rev-parse --short HEAD)
echo "Current commit: $COMMIT"

# Tag image
docker tag sionna-phy:latest \
    $ACCOUNT_ID.dkr.ecr.ap-northeast-2.amazonaws.com/sionna-experiments:$COMMIT

docker tag sionna-phy:latest \
    $ACCOUNT_ID.dkr.ecr.ap-northeast-2.amazonaws.com/sionna-experiments:latest

# Push to ECR
docker push $ACCOUNT_ID.dkr.ecr.ap-northeast-2.amazonaws.com/sionna-experiments:$COMMIT
docker push $ACCOUNT_ID.dkr.ecr.ap-northeast-2.amazonaws.com/sionna-experiments:latest
```

**Expected Output:**
```
The push refers to repository [123456789012.dkr.ecr.ap-northeast-2.amazonaws.com/sionna-experiments]
a1b2c3d: Pushed
latest: digest: sha256:abc123... size: 1234
```

### Record Image Sharing Information

```bash
# Add sharing information to README
cat >> README.md << EOF

## 🐳 Docker Image Sharing

### Pull Image from ECR
\`\`\`bash
# ECR login
aws ecr get-login-password --region ap-northeast-2 | \\
    docker login --username AWS --password-stdin \\
    $ACCOUNT_ID.dkr.ecr.ap-northeast-2.amazonaws.com

# Pull specific version
docker pull $ACCOUNT_ID.dkr.ecr.ap-northeast-2.amazonaws.com/sionna-experiments:$COMMIT

# Pull latest version
docker pull $ACCOUNT_ID.dkr.ecr.ap-northeast-2.amazonaws.com/sionna-experiments:latest
\`\`\`

### Run by Version
\`\`\`bash
# Run with specific commit version
docker run --rm -v \$(pwd)/results:/app/results \\
    $ACCOUNT_ID.dkr.ecr.ap-northeast-2.amazonaws.com/sionna-experiments:$COMMIT \\
    configs/baseline.yaml
\`\`\`
EOF

# Commit changes
git add README.md
git commit -m "docs: Add ECR image sharing guide

- Commit-based image tagging strategy
- ECR image pull/run commands
- Version-based experiment reproduction method"
```

## 🤝 Step 4: Collaboration Reproducibility Verification (20 minutes)

### Rollback to Previous Version Test

```bash
# Check commit history
git log --oneline

# Rollback to first commit
FIRST_COMMIT=$(git rev-list --max-parents=0 HEAD)
git checkout $FIRST_COMMIT

# Build image with previous version
docker build -t sionna-phy-old .

# Run experiment with previous configuration
mkdir -p results-old
docker run --rm -v $(pwd)/results-old:/app/results sionna-phy-old configs/baseline.yaml
```

### Compare Results

```bash
# Return to latest version
git checkout main

# Compare result files
echo "=== Previous Version Results ==="
ls -la results-old/

echo "=== Current Version Results ==="
ls -la results/

# Compare numerical results with Python
python3 << EOF
import numpy as np

# Load previous version results
try:
    old_data = np.load('results-old/phy-abs-baseline.npz')
    print("Previous version TBLER:", old_data['tbler_mean'])
    print("Previous version throughput:", old_data['throughput_mean']/1024, "kbit")
except:
    print("No previous version results")

# Load current version results
try:
    new_data = np.load('results/phy-abs-baseline.npz')
    print("Current version TBLER:", new_data['tbler_mean'])
    print("Current version throughput:", new_data['throughput_mean']/1024, "kbit")
    
    # extras-v2 results
    extras_data = np.load('results/phy-abs-extras-v2.npz')
    print("extras-v2 TBLER:", extras_data['tbler_mean'])
    print("extras-v2 throughput:", extras_data['throughput_mean']/1024, "kbit")
except:
    print("No current version results")
EOF
```

### Team Collaboration Simulation

```bash
# Simulate team member perspective in new directory
cd ..
mkdir team-member-test
cd team-member-test

# Pull image from ECR
aws ecr get-login-password --region ap-northeast-2 | \
    docker login --username AWS --password-stdin \
    $ACCOUNT_ID.dkr.ecr.ap-northeast-2.amazonaws.com

docker pull $ACCOUNT_ID.dkr.ecr.ap-northeast-2.amazonaws.com/sionna-experiments:latest

# Clone Git repository (in practice from GitHub/GitLab)
cp -r ../sionna-experiments .
cd sionna-experiments

# Team member runs same experiment
mkdir -p team-results
docker run --rm -v $(pwd)/team-results:/app/results \
    $ACCOUNT_ID.dkr.ecr.ap-northeast-2.amazonaws.com/sionna-experiments:latest \
    configs/baseline.yaml

echo "=== Team Member Reproduction Results ==="
ls -la team-results/
```

## 📊 Step 5: Version-based Performance Analysis (10 minutes)

### Create Performance Comparison Script

```bash
cd ../sionna-experiments

# Create performance analysis script
cat > scripts/compare_results.py << 'EOF'
#!/usr/bin/env python3
import numpy as np
import matplotlib.pyplot as plt
import glob
import os

def compare_experiments():
    """Compare experiment results analysis"""
    results_files = glob.glob('results/*.npz')
    
    if not results_files:
        print("❌ No result files found.")
        return
    
    experiments = {}
    
    # Load all result files
    for file in results_files:
        exp_name = os.path.basename(file).replace('.npz', '')
        data = np.load(file)
        experiments[exp_name] = {
            'tbler': data['tbler_mean'],
            'throughput': data['throughput_mean'] / 1024,  # kbit
            'tbler_std': data['tbler_std'],
            'nack_rate': data['harq_nack_rate']
        }
    
    # Print results
    print("📊 Experiment Results Comparison")
    print("=" * 60)
    print(f"{'Experiment':<20} {'TBLER':<10} {'Throughput(kbit)':<12} {'NACK Rate':<8}")
    print("-" * 60)
    
    for exp_name, data in experiments.items():
        print(f"{exp_name:<20} {data['tbler']:.3f}     {data['throughput']:.1f}        {data['nack_rate']:.3f}")
    
    # Visualization
    if len(experiments) > 1:
        create_comparison_plot(experiments)

def create_comparison_plot(experiments):
    """Create comparison visualization"""
    exp_names = list(experiments.keys())
    tbler_values = [experiments[name]['tbler'] for name in exp_names]
    throughput_values = [experiments[name]['throughput'] for name in exp_names]
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    # TBLER comparison
    bars1 = ax1.bar(exp_names, tbler_values, color='lightcoral', alpha=0.7)
    ax1.set_ylabel('TBLER')
    ax1.set_title('TBLER Comparison by Experiment')
    ax1.tick_params(axis='x', rotation=45)
    
    # Display values on bars
    for bar, value in zip(bars1, tbler_values):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.001,
                f'{value:.3f}', ha='center', va='bottom')
    
    # Throughput comparison
    bars2 = ax2.bar(exp_names, throughput_values, color='lightgreen', alpha=0.7)
    ax2.set_ylabel('Throughput (kbit)')
    ax2.set_title('Throughput Comparison by Experiment')
    ax2.tick_params(axis='x', rotation=45)
    
    # Display values on bars
    for bar, value in zip(bars2, throughput_values):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 50,
                f'{value:.1f}', ha='center', va='bottom')
    
    plt.tight_layout()
    plt.savefig('results/experiment_comparison.png', dpi=150, bbox_inches='tight')
    plt.close()
    
    print("📊 Comparison graph saved: results/experiment_comparison.png")

if __name__ == "__main__":
    compare_experiments()
EOF

chmod +x scripts/compare_results.py
```

### Run Performance Comparison

```bash
python scripts/compare_results.py
```

**Expected Output:**
```
📊 Experiment Results Comparison
============================================================
Experiment           TBLER      Throughput(kbit)   NACK Rate
------------------------------------------------------------
phy-abs-baseline     0.098      1247.3       0.089
phy-abs-extras-v2    0.009      2847.6       0.008
📊 Comparison graph saved: results/experiment_comparison.png
```

## ✅ Practice Checklist

| Step | Verification | Status |
|------|-------------|--------|
| ✅ Git Initialization | Repository creation and initial commit | |
| ✅ Experiment Change Tracking | extras-v2 configuration change and commit | |
| ✅ ECR Image Sharing | Commit-based tagging and push success | |
| ✅ Reproducibility Verification | Previous version rollback and execution | |
| ✅ Team Collaboration Test | Identical result reproduction with ECR image | |
| ✅ Performance Comparison | Version-based result analysis completed | |

## 🎯 Core Workflow Summary

### 1. Development Workflow
```bash
# Change experiment configuration
vim configs/new_experiment.yaml

# Run and verify experiment
docker run --rm -v $(pwd)/results:/app/results sionna-phy configs/new_experiment.yaml

# Commit changes
git add configs/new_experiment.yaml
git commit -m "feat: Add new experiment configuration"

# Push to ECR
COMMIT=$(git rev-parse --short HEAD)
docker tag sionna-phy:latest $ACCOUNT_ID.dkr.ecr.ap-northeast-2.amazonaws.com/sionna-experiments:$COMMIT
docker push $ACCOUNT_ID.dkr.ecr.ap-northeast-2.amazonaws.com/sionna-experiments:$COMMIT
```

### 2. Collaboration Workflow
```bash
# Team member: Clone repository
git clone <repository-url>
cd sionna-experiments

# Checkout specific version
git checkout <commit-hash>

# Pull corresponding version image from ECR
docker pull $ACCOUNT_ID.dkr.ecr.ap-northeast-2.amazonaws.com/sionna-experiments:<commit-hash>

# Reproduce same experiment
docker run --rm -v $(pwd)/results:/app/results \
    $ACCOUNT_ID.dkr.ecr.ap-northeast-2.amazonaws.com/sionna-experiments:<commit-hash> \
    configs/baseline.yaml
```

## 🛠️ Troubleshooting

| Problem | Solution |
|---------|----------|
| Git commit failure | Check user information settings |
| ECR push failure | Check AWS credentials and permissions |
| Result inconsistency | Check Sionna seed settings |
| Image tag error | Check commit hash accuracy |

## 🎉 Complete!

**Congratulations!** 

You have implemented a complete collaboration workflow:

✅ Systematic tracking of experiment changes through Git  
✅ Experiment environment image sharing through ECR  
✅ Commit-based version management and reproducibility guarantee  
✅ Standardized workflow for team collaboration  
✅ Experiment result comparison and performance analysis

**Core Value**: Now any team member can reproduce 100% identical experiments from specific commits!

---

**[Continue to Workshop Summary →](/80-summary/)**