import subprocess
import os
# Set the working directory to the project root directory
project_root = os.path.dirname(os.path.abspath(__file__))

# Specify the directory of the test cases
test_dir = "Test"

# Run pytest on the test cases
subprocess.run(["pytest", test_dir])