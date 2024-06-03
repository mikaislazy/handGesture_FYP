import os
import sys
# Get the directory of the current script
current_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the path to the src directory
src_dir = os.path.join(current_dir, '../Widgets')

# Add the src directory to the system path
sys.path.insert(0, src_dir)

print(os.getcwd())