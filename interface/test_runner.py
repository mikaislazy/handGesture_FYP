import subprocess
import os
import Widgets.UserData.db_utils as db_utils

"""
Please run this file in interface directory.
"""

# Set the working directory to the  root directory
project_root = os.path.dirname(os.path.abspath(__file__))

# Specify the directory of the test cases
test_dir = "Test"

# Run pytest on the test cases
subprocess.run(["pytest", test_dir])
db_utils.clear_db() # clear the database