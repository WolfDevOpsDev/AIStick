from fastapi import FastAPI, UploadFile, File, HTTPException
from typing import List
import os
import subprocess
import shutil

app = FastAPI()

# Directory to store uploaded images and training configurations
TRAINING_DIR = "training_data"
CONFIG_PATH = "config.yaml"
MODEL_OUTPUT_DIR = "output_model"


@app.post("/train")
async def train_model(images: List[UploadFile] = File(...), epochs: int = 5, learning_rate: float = 1e-4):
    # Prepare training data directory
    if os.path.exists(TRAINING_DIR):
        shutil.rmtree(TRAINING_DIR)
    os.makedirs(TRAINING_DIR, exist_ok=True)

    # Save uploaded images
    for image in images:
        file_path = os.path.join(TRAINING_DIR, image.filename)
        with open(file_path, "wb") as f:
            f.write(await image.read())

    # Generate a training configuration file
    generate_config_file(epochs, learning_rate)

    # Start the training process using FluxGym
    try:
        # Assuming FluxGym is set up to use 'app.py' as the entry point
        subprocess.run(["python", "fluxgym/app.py", "--config", CONFIG_PATH], check=True)
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Training failed: {e}")

    return {"message": "Training started successfully!", "model_output": MODEL_OUTPUT_DIR}


def generate_config_file(epochs, learning_rate):
    """
    Generates a YAML configuration file for the training process.
    """
    config_content = f"""
    model:
      base_model: flux1-dev
      epochs: {epochs}
      learning_rate: {learning_rate}
      output_dir: {MODEL_OUTPUT_DIR}
      training_data: {TRAINING_DIR}
    """
    with open(CONFIG_PATH, "w") as f:
        f.write(config_content)
