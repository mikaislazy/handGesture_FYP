import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, '../Widgets')

# add the src directory to the system path
sys.path.insert(0, src_dir)