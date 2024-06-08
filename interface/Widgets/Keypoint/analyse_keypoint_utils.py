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

# Load the template keypoints for all gestures
curr_dir = os.path.dirname(os.path.realpath(__file__))
json_filename = os.path.join(curr_dir, "mean_of_normalized_keypoints.json")

with open(json_filename, 'r') as file:
    all_template_keypoints = json.load(file)

def compare_keypoints(current_keypoints, template_keypoints):
    feedback = []

    if not current_keypoints:
        return "No keypoints detected"
    if not template_keypoints:
        return "No template keypoints found"

    keypoint_groups = {
        'thumb': [1, 2, 3, 4],
        'index': [5, 6, 7, 8],
        'middle': [9, 10, 11, 12],
        'ring': [13, 14, 15, 16],
        'little': [17, 18, 19, 20]
    }

    def get_finger_adjustment(current_pts, template_pts, finger_name):
        deltas = template_pts - current_pts
        delta_x = deltas[:, 0]
        delta_y = deltas[:, 1]

        direction_x = 'left' if np.mean(delta_x) < 0 else 'right'
        direction_y = 'up' if np.mean(delta_y) < 0 else 'down'
        
        return (finger_name, direction_y, direction_x)

    def aggregate_finger_directions(current_hand_pts, template_hand_pts):
        finger_adjustments = []
        for finger_name, indices in keypoint_groups.items():
            current_pts = np.array([current_hand_pts[i] for i in indices])
            template_pts = np.array([template_hand_pts[i] for i in indices])
            adjustment = get_finger_adjustment(current_pts, template_pts, finger_name)
            if adjustment:
                finger_adjustments.append(adjustment)
        return finger_adjustments

    if current_keypoints['is_left'] and template_keypoints['is_left']:
        left_finger_adjustments = aggregate_finger_directions(current_keypoints['left_hand_pts'], template_keypoints['left_hand_pts'])
        feedback.extend(left_finger_adjustments)
    
    if current_keypoints['is_right'] and template_keypoints['is_right']:
        right_finger_adjustments = aggregate_finger_directions(current_keypoints['right_hand_pts'], template_keypoints['right_hand_pts'])
        feedback.extend(right_finger_adjustments)
    
    return feedback

def draw_adjustments(image, adjustments, current_keypoints):
    keypoint_groups = {
        'thumb': 4,
        'index': 8,
        'middle': 12,
        'ring': 16,
        'little': 20
    }

    for adjustment in adjustments:
        finger_name, direction_y, direction_x = adjustment
        if finger_name in keypoint_groups:
            keypoint_index = keypoint_groups[finger_name]
            # Draw feedback for the left hand if detected
            if current_keypoints['is_left'] and keypoint_index < len(current_keypoints['left_hand_pts']):
                keypoint = (np.array(current_keypoints['left_hand_pts'][keypoint_index][:2]) * np.array([image.shape[1], image.shape[0]])).astype(int)
                # Draw a circle at the keypoint
                cv2.circle(image, tuple(keypoint), 5, (0, 0, 255), -1)
                # Draw text indicating the direction
                text_position = (keypoint[0] + 10, keypoint[1] + 10)
                cv2.putText(image, f"{direction_y} {direction_x}", text_position, cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2, cv2.LINE_AA)
            # Draw feedback for the right hand if detected
            if current_keypoints['is_right'] and keypoint_index < len(current_keypoints['right_hand_pts']):
                keypoint = (np.array(current_keypoints['right_hand_pts'][keypoint_index][:2]) * np.array([image.shape[1], image.shape[0]])).astype(int)
                # Draw a circle at the keypoint
                cv2.circle(image, tuple(keypoint), 5, (0, 0, 255), -1)
                # Draw text indicating the direction
                text_position = (keypoint[0] + 10, keypoint[1] + 10)
                cv2.putText(image, f"{direction_y} {direction_x}", text_position, cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2, cv2.LINE_AA)

def analyse_keypoints(frame, gesture_name):
    """
    Process a single frame to detect hand gestures and provide feedback.

    Parameters:
    - frame: The input frame from the webcam or video source.
    - gesture_name: The name of the gesture to recognize.

    Returns:
    - processed_frame: The frame with feedback drawn on it.
    """
    # frame = frame.copy()
    
    # Check if the gesture template is available
    if gesture_name not in all_template_keypoints:
        cv2.putText(frame, "Gesture template not found.", (100, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2, cv2.LINE_AA)
        return frame

    template_keypoints = all_template_keypoints[gesture_name]
    
    # Extract hand keypoints
    current_keypoints = common_utils.extract_hand_keypoints(frame)
    if current_keypoints['is_left'] == False and  current_keypoints['is_right'] == False:
        cv2.putText(frame, "No hand detected. Please attempt the task again in a well-lit area or put your hand closer.", (100,150), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2, cv2.LINE_AA)
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
