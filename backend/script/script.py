# script.py
import subprocess
import time

# Start model.py first
model_process = subprocess.Popen(["python3", "../model/model.py"])
print("Started model.py...")

# Optional: wait a bit or check if model.py is ready
time.sleep(5)  # Adjust this delay as needed

# Now start app.py
app_process = subprocess.Popen(["python3", "../app/app.py"])
print("Started app.py...")

# Optional: keep script running while both processes are alive
model_process.wait()
app_process.wait()
