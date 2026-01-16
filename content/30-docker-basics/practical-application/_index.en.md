---
title: "Practical Application and Optimization"
weight: 33
---

# Practical Application and Optimization

Let's learn Docker's practical application features including Dockerfile writing, Volume management, and Multi-stage builds to create efficient container environments.

## 📝 Writing Dockerfiles

### Basic Dockerfile Structure

```dockerfile
# Specify base image
FROM python:3.11-slim

# Add metadata
LABEL maintainer="your-email@example.com"
LABEL description="Python development environment"

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV APP_HOME=/app

# Set working directory
WORKDIR $APP_HOME

# Install system packages
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Set execution command
CMD ["python", "app.py"]
```

### Key Dockerfile Commands

| Command | Description | Example |
|---------|-------------|---------|
| `FROM` | Specify base image | `FROM python:3.11-slim` |
| `WORKDIR` | Set working directory | `WORKDIR /app` |
| `COPY` | Copy files/directories | `COPY . /app` |
| `ADD` | Copy files (supports URL, tar) | `ADD app.tar.gz /app` |
| `RUN` | Execute command during build | `RUN pip install flask` |
| `ENV` | Set environment variable | `ENV PORT=8000` |
| `EXPOSE` | Document port | `EXPOSE 8000` |
| `CMD` | Container startup command | `CMD ["python", "app.py"]` |
| `ENTRYPOINT` | Fixed execution command | `ENTRYPOINT ["python"]` |

### Practice 1: Containerizing Python Web Application

**1. Create project directory structure:**

```bash
mkdir -p ~/docker-lab/python-app
cd ~/docker-lab/python-app
```

**2. Write simple Flask application:**

```bash
cat > app.py << 'EOF'
from flask import Flask, jsonify
import os

app = Flask(__name__)

@app.route('/')
def hello():
    return jsonify({
        "message": "Hello from Docker!",
        "hostname": os.uname().nodename
    })

@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
EOF
```

**3. Write requirements.txt:**

```bash
cat > requirements.txt << 'EOF'
flask==3.0.0
EOF
```

**4. Write Dockerfile:**

```bash
cat > Dockerfile << 'EOF'
FROM python:3.11-slim

WORKDIR /app

# Copy dependencies first (for caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app.py .

EXPOSE 5000

CMD ["python", "app.py"]
EOF
```

**5. Build and run image:**

```bash
# Build image
docker build -t my-flask-app:v1 .

# Check build process
docker images my-flask-app

# Run container
docker run -d --name flask-app -p 5000:5000 my-flask-app:v1

# Test application
curl http://localhost:5000
curl http://localhost:5000/health

# Check logs
docker logs flask-app

# Clean up
docker rm -f flask-app
```

## 💾 Docker Volume

### Why Volumes are Needed

```
┌─────────────────────────────────────────────────────────┐
│                    When Container is Deleted             │
│                                                         │
│  ┌─────────────────┐          ┌─────────────────┐      │
│  │    Container    │  Delete  │     Data        │      │
│  │                 │ ───────▶ │     Lost!       │      │
│  │  (Container     │          │                 │      │
│  │   Layer R/W)    │          │                 │      │
│  └─────────────────┘          └─────────────────┘      │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│                    When Using Volume                     │
│                                                         │
│  ┌─────────────────┐          ┌─────────────────┐      │
│  │    Container    │  Delete  │    Container    │      │
│  │                 │ ───────▶ │     Deleted     │      │
│  └────────┬────────┘          └─────────────────┘      │
│           │                                             │
│           ▼                                             │
│  ┌─────────────────┐          ┌─────────────────┐      │
│  │     Volume      │ ───────▶ │  Data Preserved!│      │
│  │  (Host Storage) │          │                 │      │
│  └─────────────────┘          └─────────────────┘      │
└─────────────────────────────────────────────────────────┘
```

### Volume Types

| Type | Description | Use Case |
|------|-------------|----------|
| **Named Volume** | Docker-managed volume | Data persistence |
| **Bind Mount** | Direct host path mount | Development environment |
| **tmpfs Mount** | Memory storage | Temporary data |

### Practice 2: Using Volumes

**Using Named Volume:**

```bash
# Create volume
docker volume create my-data

# List volumes
docker volume ls

# Volume details
docker volume inspect my-data

# Run container with volume
docker run -d \
  --name db-container \
  -v my-data:/var/lib/data \
  ubuntu:22.04 \
  sleep infinity

# Create data in container
docker exec db-container bash -c "echo 'Hello Volume' > /var/lib/data/test.txt"

# Check data
docker exec db-container cat /var/lib/data/test.txt

# Remove container
docker rm -f db-container

# Check data in new container (data preserved!)
docker run --rm \
  -v my-data:/var/lib/data \
  ubuntu:22.04 \
  cat /var/lib/data/test.txt

# Remove volume
docker volume rm my-data
```

**Using Bind Mount (Development Environment):**

```bash
# Create working directory
mkdir -p ~/docker-lab/bind-mount-demo
cd ~/docker-lab/bind-mount-demo

# Create test file
echo "Hello from host!" > hello.txt

# Run container with bind mount
docker run --rm \
  -v $(pwd):/workspace \
  -w /workspace \
  ubuntu:22.04 \
  cat hello.txt

# Check real-time file synchronization
docker run -it --rm \
  -v $(pwd):/workspace \
  -w /workspace \
  ubuntu:22.04 \
  /bin/bash

# Inside container
# ls -la
# echo "Modified in container" >> hello.txt
# exit

# Check changes on host
cat hello.txt
```

## 🚀 Multi-stage Build

### Benefits of Multi-stage Build

```
┌─────────────────────────────────────────────────────────────────┐
│                     Regular Build                               │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ Final Image                                             │   │
│  │ - Includes build tools                                  │   │
│  │ - Includes source code                                  │   │
│  │ - Unnecessary files                                     │   │
│  │                                                         │   │
│  │ Size: Hundreds of MB ~ Several GB                       │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                   Multi-stage Build                             │
│                                                                 │
│  Stage 1: Builder                  Stage 2: Final              │
│  ┌────────────────────┐           ┌────────────────────┐       │
│  │ - Build tools      │  COPY     │ - Runtime only     │       │
│  │ - Source code      │ ────────▶ │ - Build artifacts  │       │
│  │ - Compilation      │  Only     │   only             │       │
│  │                    │  needed   │                    │       │
│  │ Size: Hundreds MB  │  parts    │ Size: Tens of MB   │       │
│  └────────────────────┘           └────────────────────┘       │
│         (Discarded)                    (Final Image)           │
└─────────────────────────────────────────────────────────────────┘
```

### Practice 3: Multi-stage Build

```bash
mkdir -p ~/docker-lab/multistage
cd ~/docker-lab/multistage
```

**Write Go application:**

```bash
cat > main.go << 'EOF'
package main

import (
    "fmt"
    "net/http"
)

func main() {
    http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
        fmt.Fprintf(w, "Hello from Multi-stage Build!")
    })
    fmt.Println("Server starting on :8080")
    http.ListenAndServe(":8080", nil)
}
EOF
```

**Compare Regular Dockerfile vs Multi-stage Dockerfile:**

```bash
# Regular Dockerfile
cat > Dockerfile.single << 'EOF'
FROM golang:1.21

WORKDIR /app
COPY main.go .
RUN go build -o server main.go

EXPOSE 8080
CMD ["./server"]
EOF

# Multi-stage Dockerfile
cat > Dockerfile.multi << 'EOF'
# Stage 1: Build environment
FROM golang:1.21 AS builder

WORKDIR /app
COPY main.go .
RUN CGO_ENABLED=0 GOOS=linux go build -o server main.go

# Stage 2: Runtime environment
FROM alpine:latest

WORKDIR /app
COPY --from=builder /app/server .

EXPOSE 8080
CMD ["./server"]
EOF
```

**Compare image sizes:**

```bash
# Regular build
docker build -f Dockerfile.single -t go-app:single .

# Multi-stage build
docker build -f Dockerfile.multi -t go-app:multi .

# Compare sizes
docker images | grep go-app
```

**Expected Result:**
```
go-app    single    xxx    xxx    ~800MB
go-app    multi     xxx    xxx    ~15MB
```

## 🧪 Practice Exercises

### Exercise 1: Build Data Analysis Environment

Write a Dockerfile that meets the following requirements:

**Requirements:**
- Use Python 3.11 base image
- Install numpy, pandas, matplotlib, seaborn
- Install and configure Jupyter Notebook
- Set working directory to `/workspace`
- Expose port 8888

**Example Solution:**

```dockerfile
FROM python:3.11-slim

# Install system packages
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /workspace

# Install Python packages
RUN pip install --no-cache-dir \
    numpy \
    pandas \
    matplotlib \
    seaborn \
    jupyter

# Configure Jupyter
RUN jupyter notebook --generate-config && \
    echo "c.NotebookApp.ip = '0.0.0.0'" >> ~/.jupyter/jupyter_notebook_config.py && \
    echo "c.NotebookApp.allow_root = True" >> ~/.jupyter/jupyter_notebook_config.py && \
    echo "c.NotebookApp.open_browser = False" >> ~/.jupyter/jupyter_notebook_config.py

# Expose port
EXPOSE 8888

# Startup command
CMD ["jupyter", "notebook", "--port=8888", "--no-browser", "--allow-root"]
```

### Exercise 2: Separate Development-Production Environments

Write two Dockerfiles for development and production environments:

**Development Environment (Dockerfile.dev):**
```dockerfile
FROM python:3.11

WORKDIR /app

# Install development tools
RUN pip install --no-cache-dir \
    flask \
    flask-debugtoolbar \
    pytest \
    black \
    flake8

# Development settings
ENV FLASK_ENV=development
ENV FLASK_DEBUG=1

EXPOSE 5000

CMD ["flask", "run", "--host=0.0.0.0"]
```

**Production Environment (Dockerfile.prod):**
```dockerfile
# Stage 1: Build environment
FROM python:3.11 AS builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Runtime environment
FROM python:3.11-slim

# Create non-root user
RUN useradd --create-home --shell /bin/bash app

WORKDIR /app
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

COPY app.py .
RUN chown -R app:app /app

USER app

EXPOSE 5000

CMD ["python", "app.py"]
```

## 📝 Summary

### Learning Checklist

✅ **Dockerfile Writing**
- Understanding basic structure and commands
- Optimizing image build process
- Utilizing layer caching

✅ **Volume Management**
- Differences between Named Volume and Bind Mount
- Methods to ensure data persistence
- Usage in development environments

✅ **Multi-stage Build**
- Image size optimization techniques
- Separating build and runtime environments
- Security enhancement methods

### Best Practices

```dockerfile
# 1. Choose appropriate base image
FROM python:3.11-slim  # Use slim version

# 2. Optimize layer caching
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .  # Copy code last

# 3. Remove unnecessary files
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 4. Use non-root user
RUN useradd --create-home app
USER app

# 5. Explicit port exposure
EXPOSE 8000
```

## 🚀 Next Steps

You've completely mastered Docker basics! Now let's learn how to configure professional telecommunications simulation environments using the NVIDIA Sionna library as containers.

---

**[Continue to Sionna Environment Setup →](/40-container-environment/)**