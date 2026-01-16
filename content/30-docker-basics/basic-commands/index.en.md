---
title: "Basic Commands and Practice"
weight: 32
---

# Basic Commands and Practice

Let's learn Docker's basic commands through hands-on practice and master container lifecycle management methods.

## 🛠️ Docker Basic Commands Practice

### Environment Check

```bash
# Check Docker version
docker --version

# Check Docker system information
docker info

# Check Docker disk usage
docker system df
```

### Practice 1: Hello World Container

Let's run the most basic Docker command.

```bash
# Run Hello World container
docker run hello-world
```

**Expected Output:**
```
Unable to find image 'hello-world:latest' locally
latest: Pulling from library/hello-world
...
Hello from Docker!
This message shows that your installation appears to be working correctly.
```

**Process Flow:**
```
docker run hello-world
        │
        ▼
┌─────────────────────────────────┐
│ 1. Search for image locally     │
│    → Not found                  │
└───────────────┬─────────────────┘
                ▼
┌─────────────────────────────────┐
│ 2. Download image from Docker   │
│    Hub                          │
└───────────────┬─────────────────┘
                ▼
┌─────────────────────────────────┐
│ 3. Create container from image  │
└───────────────┬─────────────────┘
                ▼
┌─────────────────────────────────┐
│ 4. Run container (print message)│
└───────────────┬─────────────────┘
                ▼
┌─────────────────────────────────┐
│ 5. Container exits              │
└─────────────────────────────────┘
```

### Practice 2: Interactive Ubuntu Container Execution

```bash
# Run Ubuntu container in interactive mode
docker run -it ubuntu:22.04 /bin/bash
```

**Execute inside container:**
```bash
# Check system information
cat /etc/os-release

# Update packages
apt update

# Install simple package
apt install -y curl

# Exit container
exit
```

**Command Option Explanation:**

| Option | Meaning |
|--------|---------|
| `-i` | Interactive (keep standard input open) |
| `-t` | TTY (allocate terminal) |
| `-it` | Interactive terminal mode |

### Practice 3: Container Lifecycle Management

```bash
# Run nginx container in background
docker run -d --name my-nginx -p 5000:80 nginx

# Check running containers
docker ps

# Check all containers (including stopped)
docker ps -a

# Check container logs
docker logs my-nginx

# Stream logs in real-time
docker logs -f my-nginx

# Access running container
docker exec -it my-nginx /bin/bash

# Stop container
docker stop my-nginx

# Start container
docker start my-nginx

# Restart container
docker restart my-nginx

# Remove container (after stopping)
docker stop my-nginx
docker rm my-nginx

# Force remove
docker rm -f my-nginx
```

**Command Option Explanation:**

| Option | Meaning |
|--------|---------|
| `-d` | Detached (run in background) |
| `--name` | Assign container name |
| `-p 8080:80` | Map host:container port |
| `-f` | Follow (real-time output) |

### Practice 4: Image Management

```bash
# Search images on Docker Hub
docker search python

# Download image
docker pull python:3.11-slim

# List local images
docker images

# Check image details
docker inspect python:3.11-slim

# Remove image
docker rmi python:3.11-slim

# Clean unused images
docker image prune

# Clean all unused resources
docker system prune -a
```

## 🐍 Python Environment Configuration Practice

### Practice 5: Python Development Environment

Let's configure a development environment using Python containers.

```bash
# Run Python 3.11 container
docker run -it python:3.11 python

# Execute in Python interpreter
>>> import sys
>>> print(f"Python version: {sys.version}")
>>> print("Hello from containerized Python!")
>>> exit()
```

### Practice 6: Package Installation and Testing

```bash
# Test package installation in Python container
docker run -it python:3.11 /bin/bash

# Execute inside container
pip install numpy matplotlib
python -c "import numpy as np; print(f'NumPy version: {np.__version__}')"
python -c "import matplotlib; print(f'Matplotlib version: {matplotlib.__version__}')"
exit
```

### Practice 7: Running Simple Python Scripts

**1. Create working directory:**

```bash
mkdir -p ~/docker-lab/python-demo
cd ~/docker-lab/python-demo
```

**2. Write Python script:**

```bash
cat > hello.py << 'EOF'
import datetime

def main():
    now = datetime.datetime.now()
    print(f"Hello from Docker! Current time: {now}")
    
    # Simple calculation
    numbers = [1, 2, 3, 4, 5]
    total = sum(numbers)
    print(f"Sum of {numbers} = {total}")

if __name__ == "__main__":
    main()
EOF
```

**3. Execute script in container:**

```bash
# Mount current directory to container and execute script
docker run --rm -v $(pwd):/app -w /app python:3.11 python hello.py
```

## 📊 matplotlib Installation Practice

### Practice 8: Visualization Environment Setup

Let's set up a visualization environment using matplotlib.

**1. Write visualization script:**

```bash
cat > plot_demo.py << 'EOF'
import matplotlib
matplotlib.use('Agg')  # Use in GUI-less environment
import matplotlib.pyplot as plt
import numpy as np

# Generate data
x = np.linspace(0, 10, 100)
y = np.sin(x)

# Create plot
plt.figure(figsize=(10, 6))
plt.plot(x, y, 'b-', linewidth=2, label='sin(x)')
plt.xlabel('x')
plt.ylabel('y')
plt.title('Sine Wave')
plt.legend()
plt.grid(True)

# Save to file
plt.savefig('/app/sine_wave.png', dpi=300, bbox_inches='tight')
print("Plot saved as sine_wave.png")
EOF
```

**2. Execute with required packages:**

```bash
# Install matplotlib and execute script
docker run --rm -v $(pwd):/app -w /app python:3.11 bash -c "
pip install matplotlib numpy && 
python plot_demo.py
"

# Check generated file
ls -la sine_wave.png
```

## 🔧 Practice Exercises

### Exercise 1: Run Web Server Container

Run a web server that meets the following requirements:

1. Use nginx image
2. Accessible on port 8080
3. Container name should be "my-webserver"
4. Run in background

**Solution:**
```bash
docker run -d --name my-webserver -p 8080:80 nginx
```

### Exercise 2: Execute Data Analysis Script

Write and execute a script that performs simple data analysis using pandas.

**Script Example:**
```python
import pandas as pd
import numpy as np

# Generate sample data
data = {
    'name': ['Alice', 'Bob', 'Charlie', 'Diana'],
    'age': [25, 30, 35, 28],
    'score': [85, 92, 78, 88]
}

df = pd.DataFrame(data)
print("Data:")
print(df)
print(f"\nAverage age: {df['age'].mean()}")
print(f"Average score: {df['score'].mean()}")
```

## 📝 Summary

### Learning Checklist

✅ **Basic Commands**
- `docker run`, `docker ps`, `docker logs`
- `docker exec`, `docker stop`, `docker rm`
- `docker images`, `docker pull`, `docker rmi`

✅ **Container Lifecycle**
- Container creation, start, stop, deletion
- Interactive mode and background execution
- Port mapping and volume mounting

✅ **Python Environment Utilization**
- Using Python base images
- Package installation and script execution
- Development environment configuration

### Useful Command Collection

```bash
# Container management
docker ps -a                    # Check all containers
docker rm $(docker ps -aq)      # Remove all containers
docker logs -f <container>      # Real-time logs

# Image management
docker images                   # Image list
docker rmi $(docker images -q)  # Remove all images
docker image prune -a           # Clean unused images

# System management
docker system df                # Disk usage
docker system prune -a          # Complete cleanup

# Debugging
docker inspect <container>      # Detailed information
docker stats                    # Resource usage
docker top <container>          # Process list
```

## 🚀 Next Steps

Now that you've mastered the basic commands, let's learn advanced features like Dockerfile writing, Volume management, and Multi-stage builds.

---

**[Continue to Practical Application and Optimization →](/30-docker-basics/practical-application/)**