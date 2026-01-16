FROM python:3.10-slim
WORKDIR /app
RUN pip install sionna tensorflow numpy matplotlib
COPY simple_awgn.py .
CMD ["python", "simple_awgn.py"]