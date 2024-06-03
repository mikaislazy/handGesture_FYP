
import os
import cv2
import mediapipe as mp
import numpy as np
import json
# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
# Function to normalize the given keypoints
def normalize_keypoints(keypoints):
    if len( keypoints ) == 0:
        return keypoints
    
    keypoints = np.array(keypoints)  # Convert keypoints to a numpy array
    center_x = np.mean(keypoints[:, 0])  # Calculate the mean of the x-coordinates
    center_y = np.mean(keypoints[:, 1])  # Calculate the mean of the y-coordinates
    
    # Calculate the Euclidean distance from each point to the center
    distances = np.sqrt(np.sum((keypoints[:, :2] - [center_x, center_y])**2, axis=1))
    
    l = np.max(distances)  # Find the maximum distance
    # Normalize the keypoints by centering and scaling with the max distance
    normalized_keypoints = (keypoints - [center_x, center_y, 0]) / l
    
    return normalized_keypoints.tolist() 

# Function to extract hand keypoints from an image
def extract_hand_keypoints(image):
    # Convert the BGR image to RGB
    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Process the image with MediaPipe Hands
    results = hands.process(rgb_image)

    hand_keypoints = {
        'left_hand_pts': None,
        'right_hand_pts': None,
        'is_left': False,
        'is_right': False
    }

    # Check if hand landmarks are detected
    if results.multi_hand_landmarks:
        for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
            hand_label = handedness.classification[0].label
            keypoints = [[landmark.x, landmark.y, landmark.z] for landmark in hand_landmarks.landmark]

            if hand_label == 'Left':
                hand_keypoints['left_hand_pts'] = keypoints
                hand_keypoints['is_left'] = True
            elif hand_label == 'Right':
                hand_keypoints['right_hand_pts'] = keypoints
                hand_keypoints['is_right'] = True
    
    return hand_keypoints

# Function to load and normalize the template keypoints from JSON file
def load_and_normalize_json(json_path):
    json_path = os.path.join(os.path.dirname(__file__), json_path)
    with open(json_path, 'r') as file:
        data = json.load(file)
    
    left_hand_points = []
    right_hand_points = []
    
    for _, points in data.items():
        if points['is_left']:
            left_hand_points.append(np.array(points['left_hand_pts']))
        if points['is_right']:
            right_hand_points.append(np.array(points['right_hand_pts']))
    
    if left_hand_points:
        left_hand_points = np.mean(left_hand_points, axis=0)
        left_normalized= normalize_keypoints(left_hand_points)
    else:
        left_normalized = []

    if right_hand_points:
        right_hand_points = np.mean(right_hand_points, axis=0)
        right_normalized= normalize_keypoints(right_hand_points)
    else:
        right_normalized = []

    return {'left_hand_pts': left_normalized, 'right_hand_pts': right_normalized, 
            'is_left': bool(left_normalized), 'is_right': bool(right_normalized)}
            
def get_normalized_mean_multiple_normalized_keypoints(gestures):
    output_json = "mean_of_normalized_keypoints.json"
    for gesture in gestures:
        data = {}
        #mean of multiple sets of normalized keypoints
        data[gesture] = load_and_normalize_json( f'normalized_keypoints_data/{gesture}_normalized.json')
        with open(output_json, 'a') as outfile:
            json.dump(data , outfile, indent=4)
    