---
title: "Creating Experiment Environment Versions"
weight: 43
---

# Creating Experiment Environment Versions

**Adding Packages to baseline to Create extras**

Add a few packages to the previously created image to make a new version. Then upload to Amazon ECR to share with team members.

## 🎯 Module Structure

1. **Add baseline Tag** - Just rename
2. **Create extras Version** - Add 3 packages
3. **Compare Two Versions** - See what's different
4. **ECR Upload** - Store in cloud
5. **Download Test** - Verify sharing works

## 📋 Step 1: Add Name Tags

### Check Current Images

```bash
docker images | grep sionna
```

**Result:**
```
sionna-simple   latest   abc123   1.2GB
```

### Add baseline Tag (Not a copy!)

```bash
docker tag sionna-simple:latest sionna-simple:baseline
docker images | grep sionna
```

**Result:**
```
sionna-simple   baseline   abc123   1.2GB
sionna-simple   latest     abc123   1.2GB
```

**Explanation**: Same image with 2 name tags attached!

## 🔨 Step 2: Create extras Version

### Create Dockerfile.extras

**New file: `Dockerfile.extras`**

```dockerfile
FROM python:3.10-slim
WORKDIR /app

# baseline packages + 3 additional!
RUN pip install sionna==1.2.1 tensorflow numpy matplotlib \
    pandas plotly tqdm

COPY simple_awgn.py .
CMD ["python", "simple_awgn.py"]
```

**Added Packages:**
- `pandas`: Data analysis
- `plotly`: Beautiful graphs
- `tqdm`: Progress bars

### Build It

```bash
docker build -f Dockerfile.extras -t sionna-simple:extras .
```

**Wait 3 minutes...**

### Verify

```bash
docker images | grep sionna
```

**Result:**
```
sionna-simple   extras     def456   1.4GB   just now
sionna-simple   baseline   abc123   1.2GB   30 min ago
sionna-simple   latest     abc123   1.2GB   30 min ago
```

## 🔍 Step 3: Compare Differences

### Size Comparison

| Version | Size | Difference |
|---------|------|------------|
| baseline | 1.2GB | Base |
| extras | 1.4GB | +200MB (3 packages) |

### Execution Comparison

```bash
# Run baseline
docker run --rm sionna-simple:baseline
# 🏆 Docker + Sionna Perfect!

# Run extras
docker run --rm sionna-simple:extras
# 🏆 Docker + Sionna Perfect! (Same)
```

**Difference**: Same execution result, but extras can use pandas/plotly!

### Package Verification

```bash
# Does extras have pandas?
docker run --rm sionna-simple:extras python -c "import pandas; print('pandas OK!')"
# pandas OK!

# What about baseline?
docker run --rm sionna-simple:baseline python -c "import pandas"
# ModuleNotFoundError (Normal!)
```

## ☁️ Step 4: Upload to ECR

### Create ECR Repository (First time only)

```bash
aws ecr create-repository \
    --repository-name sionna-workshop \
    --region ap-northeast-2
```

**Success Message:**
```json
{
    "repository": {
        "repositoryName": "sionna-workshop",
        "repositoryUri": "<ACCOUNT_ID>.dkr.ecr.ap-northeast-2.amazonaws.com/sionna-workshop"
    }
}
```

### AWS Login

```bash
# Get account ID automatically
export ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

aws ecr get-login-password --region ap-northeast-2 | \
    docker login --username AWS --password-stdin \
    $ACCOUNT_ID.dkr.ecr.ap-northeast-2.amazonaws.com
```

**Success:**
```
Login Succeeded
```

### Change Tags (Add ECR Address)

```bash
# Save variable for convenience
export ECR=$ACCOUNT_ID.dkr.ecr.ap-northeast-2.amazonaws.com/sionna-workshop

# Tag baseline
docker tag sionna-simple:baseline $ECR:baseline

# Tag extras
docker tag sionna-simple:extras $ECR:extras
```

### Upload!

```bash
# Upload baseline (5 minutes)
docker push $ECR:baseline

# Upload extras (6 minutes)
docker push $ECR:extras
```

**During Upload:**
```
baseline: digest: sha256:abc123... size: 1234
```

### Check AWS Console

1. Login to AWS Console
2. ECR → Repositories → sionna-workshop
3. Verify image tags:
   - `baseline` ✅
   - `extras` ✅

## 🧪 Step 5: Download Test (10 minutes)

### Delete Local Images

```bash
docker rmi sionna-simple:baseline sionna-simple:extras
docker images | grep sionna
# (None - Clean!)
```

### Pull from ECR

```bash
# Download baseline
docker pull $ECR:baseline

# Run it
docker run --rm $ECR:baseline
```

**Success:**
```
🎉 **Sionna Workshop Complete!**
...
```

## 🎁 Team Sharing Method

**Tell team members:**

```bash
# 1. Get account ID
export ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

# 2. AWS login (once only)
aws ecr get-login-password --region ap-northeast-2 | \
    docker login --username AWS --password-stdin $ACCOUNT_ID.dkr.ecr.ap-northeast-2.amazonaws.com

# 3. Download
docker pull $ACCOUNT_ID.dkr.ecr.ap-northeast-2.amazonaws.com/sionna-workshop:baseline

# 4. Run
docker run --rm $ACCOUNT_ID.dkr.ecr.ap-northeast-2.amazonaws.com/sionna-workshop:baseline
```

**Done! Team members run in identical environment!** 🎉

## ✅ Practice Checklist

| Task | Verification |
|------|-------------|
| ✅ baseline tag | Check `docker images` |
| ✅ extras build | Use Dockerfile.extras |
| ✅ Size difference | 200MB increase |
| ✅ ECR upload | Visible in AWS console |
| ✅ Download success | pull → run success |

## 🛠️ Error Solutions

| Problem | Solution |
|---------|----------|
| ECR login fails | Check `aws configure` settings |
| No push permission | Request ECR permissions from AWS admin |
| Image too large | `docker system prune -a` |

## 🎉 Complete!

**Congratulations!**

What you can now do:

✅ Add packages to environment (modify Dockerfile)  
✅ Version tags (baseline, extras)  
✅ ECR upload (team sharing)  
✅ Run identical environment anywhere

**Key Points:**
- Dockerfile modification = Environment change
- Tags = Version names
- ECR = Cloud storage

---

**[Continue to Git Version Management →](/50-git-management/)**