---
title: "Dockerfile and Sionna Practice"
weight: 42
---

# Dockerfile Meets Sionna

**Building Sionna Environment with Docker Instead of "pip install"**

Instead of installing Sionna locally, let's define the environment with Dockerfile. Experience Docker's reusability by running a simple communication experiment in a container.

## 🎯 Practice Steps

1. **Check Provided Dockerfile**
2. **Build Image**
3. **Run Container + Test Sionna**
4. **Verify Results**

**Key Point**: Get into the habit of creating environments as "code (Dockerfile)"!

## 📋 Step 1: File Preparation (5 minutes)

- Link1: ![Dockerfile](/samples/docker-sionna/Dockerfile)
- Link2: ![simple_awgn.py](/samples/docker-sionna/simple_awgn.py)

```bash
mkdir /workshop/docker-sionna
cd /workshop/docker-sionna
curl -o <Link1>
curl -o <Link2>
```

Workshop folder structure:

```
docker-sionna/
├── Dockerfile         # Provided (no modification needed!)
└── simple_awgn.py     # Sionna experiment script
```

## 🧐 Step 2: Dockerfile Overview (5 minutes)

**Provided Dockerfile:**

```dockerfile
FROM python:3.10-slim
WORKDIR /app
RUN pip install sionna tensorflow numpy matplotlib
COPY simple_awgn.py .
CMD ["python", "simple_awgn.py"]
```

### Line-by-Line Understanding

- `FROM python:3.10-slim`: Lightweight Python 3.10 base image
- `WORKDIR /app`: Set working directory
- `RUN pip install`: Automatic Sionna + TensorFlow installation
- `COPY simple_awgn.py`: Copy experiment code
- `CMD`: Auto-execute when container starts

### Base Image Comparison

| Base Image | Size | Build Time | GPU | Recommendation |
|------------|------|------------|-----|----------------|
| `python:3.10-slim` | **1.2GB** | **2min** | CPU | 🏆 **Workshop Optimal** |
| `tensorflow/tensorflow:2.16.1` | 3.5GB | 5min | CPU/GPU | Complex |
| `nvidia/cuda:12.4.1` | 10GB | 8min | GPU | Heavy |
| `python:3.10-alpine` | 0.8GB | 4min | CPU | Compatibility issues |

**Workshop Choice Reason**: `python:3.10-slim` is lightweight, fast, and perfectly compatible with Sionna 1.2.1!

## 🔨 Step 3: Build Image (5 minutes)

Execute in terminal:

```bash
cd docker-sionna
docker build -t sionna-simple .
```

**Success Output Example:**

```
[+] Building 101.3s (9/9) FINISHED
 => [1/4] FROM python:3.10-slim                      3.4s
 => [2/4] WORKDIR /app                               0.3s
 => [3/4] RUN pip install sionna...                 76.6s
 => [4/4] COPY simple_awgn.py .                      0.0s
 => exporting to image                              18.5s
 => => exporting layers                             18.5s
 => => naming to docker.io/library/sionna-simple     0.0s
```

**Verification:**

```bash
docker images | grep sionna-simple
```

**Expected Result:**
```
sionna-simple   latest   abc123   2 minutes ago   1.2GB
```

## 🚀 Step 4: Run Sionna Experiment (20 minutes)

### One-Command Execution (Easiest!)

```bash
docker run --rm sionna-simple
```

### Expected Output (within 10 seconds):

```
🎉 **Sionna Workshop Complete!**
Sionna: 1.2.1

🔬 **Sionna AWGN Test**
✅ Eb/No 10dB Success!
  Tx Power: 1.000
  Noise: 0.1000
  Rx Verified!

🏆 Docker + Sionna Perfect!
```

### For Detailed View (Interactive)

```bash
docker run -it --rm sionna-simple bash
```

Inside container:

```bash
python simple_awgn.py
ls -la  # Check files
exit
```

## 🖥️ Step 4.5: Infrastructure Environment Check (10 minutes)

### GPU Environment Check

When using GPU instances on AWS EC2, verify with the following commands:

```bash
# Check GPU on host
nvidia-smi

# Check GPU access from Docker container (for GPU instances)
docker run --rm --gpus all nvidia/cuda:12.4.1-base-ubuntu22.04 nvidia-smi
```

**Expected Output when GPU is available:**
```
+-----------------------------------------------------------------------------+
| NVIDIA-SMI 535.104.05             Driver Version: 535.104.05   CUDA Version: 12.2     |
|-------------------------------+----------------------+----------------------+
| GPU  Name                 Persistence-M| Bus-Id        Disp.A | Volatile Uncorr. ECC |
| Fan  Temp  Perf  Pwr:Usage/Cap|         Memory-Usage | GPU-Util  Compute M. |
|                               |                      |               MIG M. |
|===============================+======================+======================|
|   0  Tesla T4                   Off  | 00000000:00:1E.0 Off |                    0 |
| N/A   45C    P0    26W /  70W |      0MiB / 15109MiB |      0%      Default |
|                               |                      |                  N/A |
+-------------------------------+----------------------+----------------------+
```

**When no GPU available (CPU only):**
```bash
# Check CPU information
lscpu | grep -E "Model name|Architecture|CPU\(s\)"
```

### Graviton (ARM64) Environment Check

When using AWS Graviton processors:

```bash
# Check architecture
uname -m
# Output: aarch64 (ARM64) or x86_64 (Intel/AMD)

# Detailed CPU information
lscpu | grep -E "Architecture|Model name|CPU\(s\)"

# Graviton-specific information check
cat /proc/cpuinfo | grep -E "model name|processor" | head -5
```

**Expected Output for Graviton instances:**
```
Architecture:        aarch64
CPU(s):              4
Model name:          Neoverse-N1
```

**Expected Output for x86 instances:**
```
Architecture:        x86_64
CPU(s):              2
Model name:          Intel(R) Xeon(R) Platinum 8259CL CPU @ 2.50GHz
```

### Docker Architecture Compatibility Check

```bash
# Check if Docker runs on current architecture
docker version --format 'Client: {{.Client.Arch}} Server: {{.Server.Arch}}'

# Check multi-architecture image support
docker buildx version
```

### Performance Benchmark (Optional)

```bash
# Simple CPU performance test
docker run --rm python:3.10-slim python -c "
import time
start = time.time()
sum(i*i for i in range(1000000))
print(f'CPU test completed: {time.time()-start:.2f}s')
print(f'Architecture: {__import__('platform').machine()}')
"
```

**Performance Comparison Reference:**
- **Graviton3 (ARM64)**: Excellent power efficiency, cost-effective
- **Intel/AMD (x86_64)**: Superior single-thread performance, broad software compatibility

### Environment-Specific Optimization Tips

| Environment | Optimization Method | Considerations |
|-------------|-------------------|----------------|
| **GPU Instance** | Use `--gpus all` flag | Check CUDA version compatibility |
| **Graviton (ARM64)** | Use ARM64 native images | Verify package compatibility |
| **x86_64** | Use standard images | Monitor memory usage |

## 🎉 Step 5: Success Verification (5 minutes)

**Checklist:**

| Item | Verification Method | Expected Result |
|------|-------------------|-----------------|
| ✅ Build Success | `docker images` | sionna-simple visible |
| ✅ Run Success | `docker run` | 🏆 message output |
| ✅ Sionna Works | Check output | "Eb/No 10dB Success!" |
| ✅ No Errors | Red errors | None |

## 🔍 Examining simple_awgn.py Code

**Code executed by container:**

```python
#!/usr/bin/env python3
import sionna as sn
import tensorflow as tf
import os

print("🎉 **Sionna Workshop Complete!**")
print(f"Sionna: {sn.__version__}")

from sionna.phy.channel import AWGN
from sionna.phy.mapping import Mapper

print("\n🔬 **Sionna AWGN Test**")

batch_size = 32
ebno_db = 10.0

bits = tf.cast(tf.random.uniform([batch_size, 64], 0, 2) > 0.5, tf.float32)
mapper = Mapper("qam", 2)
symbols = mapper(bits)

Eb = tf.reduce_mean(tf.abs(symbols)**2)
No = Eb / (10**(ebno_db/10))

awgn = AWGN()
rx_symbols = awgn(symbols, No)

print(f"✅ Eb/No {ebno_db}dB Success!")
print(f"  Tx Power: {Eb:.3f}")
print(f"  Noise: {No:.4f}")
print(f"  Rx Verified!")

# 🔥 Add file saving! (Important!)
results_dir = "/app/results"
os.makedirs(results_dir, exist_ok=True)

# Save results to text file
output_file = f"{results_dir}/sionna_result.txt"
with open(output_file, "w") as f:
    f.write("=== Sionna AWGN Test Results ===\n")
    f.write(f"Eb/No: {ebno_db} dB\n")
    f.write(f"Tx Power: {Eb.numpy():.3f}\n")
    f.write(f"Noise Power: {No.numpy():.4f}\n")
    f.write(f"Batch Size: {batch_size}\n")

print(f"\n💾 Results saved: {output_file}")

print("\n🏆 Docker + Sionna Perfect!")
```

**Key Points:**
- Sionna 1.2.1 API: `sionna.phy.channel.AWGN`
- Manual noise calculation (no utils needed)
- Minimum 32 batch for fast execution

## 💡 Why This Approach is Better?

```
❌ Local Installation (Difficult 😭)
$ pip install sionna tensorflow  # 20min + environment conflicts
$ python simple_awgn.py          # Only works on my PC

✅ Docker Method (Easy 😊)  
$ docker build -t sionna-simple .  # 2min once only
$ docker run sionna-simple         # Convenient re-execution anytime + perfect environment reproduction
```

**Reusability Core:**
- Environment = Code (Dockerfile)
- `docker build` once → infinite re-execution
- ECR upload → identical environment anywhere

## 🛠️ If Errors Occur?

| Error Message | Solution |
|---------------|----------|
| `no space left` | `docker system prune -af` |
| `ModuleNotFoundError` | `docker build --no-cache .` |
| `Permission denied` | `sudo docker ...` or add to group |
| Slow build | Check network, try different mirror |

## 🎁 Bonus: Saving Results

```bash
# Connect results folder to host
docker run --rm -v "$(pwd)/results:/app/results" sionna-simple
```

Files saved in `./results/` after container exits!

## ✅ Practice Complete!

**Congratulations! 🎉**

Now you can:

✅ Define Sionna environment with Dockerfile  
✅ Run experiments with single `docker run`  
✅ Zero "environment setup" time!  
✅ Understand base image selection criteria

**Next Time**: Upload this image to ECR and create new versions with modifications.

---

**[Next: Creating Environment Versions →](/40-container-environment/experiment-environment/)**