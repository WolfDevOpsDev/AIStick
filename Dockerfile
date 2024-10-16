# Use a base image with Python and CUDA support
FROM nvidia/cuda:11.8.0-cudnn8-devel-ubuntu20.04

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3-pip \
    git \
    && rm -rf /var/lib/apt/lists/*

# Clone FluxGym and its dependencies
RUN git clone https://github.com/cocktailpeanut/fluxgym.git /app/fluxgym
WORKDIR /app/fluxgym
RUN git clone -b sd3 https://github.com/kohya-ss/sd-scripts /app/fluxgym/sd-scripts

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt && \
    pip install --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cu121

# Copy the FastAPI server code
COPY main.py /app/main.py

# Expose the server port
EXPOSE 8000

# Run the FastAPI server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
