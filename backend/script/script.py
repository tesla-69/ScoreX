# script.py
import subprocess
import time
import os
import sys

def run_model():
    # Get the absolute path to the model directory
    model_dir = os.path.join(os.path.dirname(__file__), '..', 'model')
    
    # Change to the model directory
    os.chdir(model_dir)
    
    # Run model.py
    try:
        subprocess.run([sys.executable, "model.py"], check=True)
        print("Model processing completed successfully")
    except subprocess.CalledProcessError as e:
        print(f"Error running model.py: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_model()
