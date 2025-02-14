import subprocess
import os

# Define directory and build command
directory = os.path.expanduser('../images/arm64/qemu/ebclfsa')
command = 'make qemu'

# Change to specified directory
os.chdir(directory)

# Run build command 10 times in a row
for _ in range(10):
    print(f"Running build {_+1}...")
    result = subprocess.run(command, shell=True) #, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)

    if result.returncode != 0:
        print(f"Command failed with return code {result.returncode}")
    else:
        print("Command executed successfully")

