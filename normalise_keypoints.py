import json
import numpy as np

def normalize_keypoints(keypoints):
    if not keypoints:
        return keypoints
    keypoints = np.array(keypoints)
    center_x = np.mean(keypoints[:, 0])
    center_y = np.mean(keypoints[:, 1])
    distances = np.sqrt(np.sum((keypoints[:, :2] - [center_x, center_y])**2, axis=1))
    l = np.max(distances)
    normalized_keypoints = (keypoints - [center_x, center_y, 0]) / l
    return normalized_keypoints.tolist()

def normalize_and_save_keypoints(input_json, output_json):
    with open(input_json, 'r') as infile:
        data = json.load(infile)
    
    normalized_data = {}
    for gesture_name, keypoints in data.items():
        normalized_data[gesture_name] = {
            'left_hand_pts': normalize_keypoints(keypoints['left_hand_pts']) if 'left_hand_pts' in keypoints else [],
            'right_hand_pts': normalize_keypoints(keypoints['right_hand_pts']) if 'right_hand_pts' in keypoints else [],
            'is_left': keypoints.get('is_left', False),
            'is_right': keypoints.get('is_right', False)
        }
    
    with open(output_json, 'w') as outfile:
        json.dump(normalized_data, outfile, indent=4)

# Normalize keypoints and save to new JSON file
normalize_and_save_keypoints('keypoint/ChanDingYin.json', 'keypoint/ChanDingYin_normalized.json')
