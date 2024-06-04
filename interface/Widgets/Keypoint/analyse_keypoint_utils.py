import os
import cv2
import mediapipe as mp
import numpy as np
import json
from collections import deque
import tensorflow as tf
from . import  common_utils
# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()

# Buffer to store recent predictions
buffer_size = 15  # Number of frames to consider for temporal smoothing
prediction_buffer = deque(maxlen=buffer_size)

# load the template keypoints for all gestures
# Get the directory of the current script
curr_dir = os.path.dirname(os.path.realpath(__file__))
json_filename = os.path.join(curr_dir, "mean_of_normalized_keypoints.json")

with open(json_filename, 'r') as file:
    all_template_keypoints = json.load(file)


# Compare keypoints with the template keypoints and provide feedback
def compare_keypoints(current_keypoints, template_keypoints):
    feedback = []

    if not current_keypoints:
        return "No keypoints detected"
    if not template_keypoints:
        return "No template keypoints found"

    keypoint_mapping = {
        4: 'thumb tip',
        8: 'index finger tip',
        12: 'middle finger tip',
        16: 'ring finger tip',
        20: 'little finger tip'
    }

    def get_adjustment(current_pt, template_pt, part_name, keypoint_index):
        delta_x = template_pt[0] - current_pt[0] # compare x-axis
        delta_y = template_pt[1] - current_pt[1] # compare y-axis
        direction_x = 'left' if delta_x < 0 else 'right' 
        direction_y = 'up' if delta_y < 0 else 'down'
        direction = direction_y if direction_y else direction_x

        if direction:
            return [(keypoint_index, direction, part_name)]
        return []

    if current_keypoints['is_left'] and template_keypoints['is_left']:
        # Compare left hand keypoints
        for i in keypoint_mapping:
            current_pt = np.array(current_keypoints['left_hand_pts'][i])
            template_pt = np.array(template_keypoints['left_hand_pts'][i])
            part_name = keypoint_mapping[i]
            feedback.extend(get_adjustment(current_pt, template_pt, part_name, i))
    
    if current_keypoints['is_right'] and template_keypoints['is_right']:
        # Compare right hand keypoints
        for i in keypoint_mapping:
            current_pt = np.array(current_keypoints['right_hand_pts'][i])
            template_pt = np.array(template_keypoints['right_hand_pts'][i])
            part_name = keypoint_mapping[i]
            feedback.extend(get_adjustment(current_pt, template_pt, part_name, i))
    
    return feedback

# draw the feedback on the image
def draw_adjustments(image, adjustments, current_keypoints):
    for adjustment in adjustments:
        keypoint_index, direction, part_name = adjustment
        if current_keypoints['is_left'] and keypoint_index < len(current_keypoints['left_hand_pts']):
            keypoint = (np.array(current_keypoints['left_hand_pts'][keypoint_index][:2]) * np.array([image.shape[1], image.shape[0]])).astype(int)
        elif current_keypoints['is_right'] and keypoint_index < len(current_keypoints['right_hand_pts']):
            keypoint = (np.array(current_keypoints['right_hand_pts'][keypoint_index][:2]) * np.array([image.shape[1], image.shape[0]])).astype(int)
        else:
            continue

        # Draw a circle at the keypoint
        cv2.circle(image, tuple(keypoint), 5, (0, 0, 255), -1)

        # Draw text indicating the direction
        text_position = (keypoint[0] + 10, keypoint[1] + 10)
        cv2.putText(image, direction, text_position, cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2, cv2.LINE_AA)

def analyse_keypoints(frame, gesture_name):
    """
    Process a single frame to detect hand gestures and provide feedback.

    Parameters:
    - frame: The input frame from the webcam or video source.
    - gesture_name: The name of the gesture to recognize.
    - template_keypoints: The template keypoints for the gesture.
    - prediction_buffer: A list used to store recent predictions.
    - buffer_size: The size of the prediction buffer.

    Returns:
    - processed_frame: The frame with feedback drawn on it.
    - prediction_buffer: Updated prediction buffer.
    """
    frame = frame.copy()
    # json_filename = f"normalized_keypoints_data/{gesture_name}_normalized.json"
    # template_keypoints = common_utils.load_and_normalize_json(json_filename)
    template_keypoints = all_template_keypoints[gesture_name]
    
    # Extract hand keypoints
    current_keypoints = common_utils.extract_hand_keypoints(frame)
    if current_keypoints is None:
        cv2.putText(frame, "No hand detected. Please attempt the task again in a well-lit area or put your hand closer.", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2, cv2.LINE_AA)
        return frame

    # Normalize current keypoints
    normalized_keypoints = {'is_left': False, 'is_right': False}
    if current_keypoints['is_left']:
        normalized_keypoints['left_hand_pts'] = common_utils.normalize_keypoints(current_keypoints['left_hand_pts'])
        normalized_keypoints['is_left'] = True
    if current_keypoints['is_right']:
        normalized_keypoints['right_hand_pts'] = common_utils.normalize_keypoints(current_keypoints['right_hand_pts'])
        normalized_keypoints['is_right'] = True

    
    # Compare keypoints and provide feedback
    adjustments = compare_keypoints(normalized_keypoints, template_keypoints)
    draw_adjustments(frame, adjustments, current_keypoints)

    return frame

# # Load the normalized template keypoints for the specific gesture
# gesture_name = "ChanDingYin"
# json_filename = "normalized_keypoints_data/ChanDingYin_normalized.json"
# template_keypoints = common_utils.load_and_normalize_json(json_filename)

# if __name__ == "__main__":
#     print("current dir", os.path.dirname(__file__))
#     # Load the normalized template keypoints for the specific gesture
#     gesture_name = "ChanDingYin"
#     json_filename = "normalized_keypoints_data/ChanDingYin_normalized.json"
#     template_keypoints = common_utils.load_and_normalize_json(json_filename)

#     # Process the frame
#     frame = cv2.imread("frame.jpg")
#     processed_frame = process_frame(frame, gesture_name, template_keypoints)

#     # Display the processed frame
#     cv2.imwrite("processed_frame.jpg", processed_frame)
#     cv2.waitKey(0)
#     cv2.destroyAllWindows()