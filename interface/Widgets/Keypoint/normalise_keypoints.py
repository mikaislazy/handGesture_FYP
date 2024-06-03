import json  
import numpy as np  
from constants import GESTURES
from . import common_utils

# Function to normalize keypoints from input JSON and save to output JSON
def get_normalized__keypoints_dataset(input_json, output_json):
    print(f"Start normalising {input_json}")
    with open(input_json, 'r') as infile:
        data = json.load(infile)  # Load data from input JSON file
    
    normalized_data = {}
    for gesture_name, keypoints in data.items():
        # Normalize the keypoints for each gesture
        normalized_data[gesture_name] = {
            'left_hand_pts': common_utils.normalize_keypoints(keypoints['left_hand_pts']) if 'left_hand_pts' in keypoints else [],
            'right_hand_pts': common_utils.normalize_keypoints(keypoints['right_hand_pts']) if 'right_hand_pts' in keypoints else [],
            'is_left': keypoints.get('is_left', False), 
            'is_right': keypoints.get('is_right', False)
        }
    
    with open(output_json, 'w') as outfile:
        json.dump(normalized_data, outfile, indent=4)
    print(f"The normalized data is stored in {output_json}.")

if __name__ == "__main__":
    for gesture in GESTURES.values():
        get_normalized__keypoints_dataset(f'keypoints_data/{gesture}.json', f'normalized_keypoints_data/{gesture}_normalized.json')