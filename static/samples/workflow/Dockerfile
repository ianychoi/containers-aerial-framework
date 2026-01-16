FROM python:3.10-slim
WORKDIR /app
RUN pip install sionna tensorflow numpy matplotlib pyyaml

# Copy source code (only experiment parameters change)
COPY configs/ ./configs/
COPY scripts/ ./scripts/
COPY README.md .

# Execution permissions
RUN chmod +x scripts/*.py

# Default volume mount (for saving results)
VOLUME ["/app/results"]

# Practice entrypoint
ENTRYPOINT ["python", "scripts/run_phy_abs.py"]
