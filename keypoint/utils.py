
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
    if not keypoints:
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

