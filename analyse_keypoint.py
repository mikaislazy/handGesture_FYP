import os
import cv2
import mediapipe as mp
import numpy as np
import json
from collections import deque
import tensorflow as tf

GESTURES_INDICS = {0: 'ChanDingYin', 
                   1: 'HuoYanYin', 
                   2: 'MiTuoDingYin', 
                   3: 'Retsu', 
                   4: 'Rin', 
                   5: 'TaiJiYin', 
                   6: 'Zai', 
                   7: 'Zen', 
                   8: 'ZhiJiXiangYin'}

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()

# Buffer to store recent predictions
buffer_size = 15  # Number of frames to consider for temporal smoothing
prediction_buffer = deque(maxlen=buffer_size)

# Function to normalize keypoints 
def normalize_keypoints(keypoints):
    if len(keypoints) == 0:
        return keypoints, 0, 0, 1
    keypoints = np.array(keypoints)
    center_x = np.mean(keypoints[:, 0])
    center_y = np.mean(keypoints[:, 1])
    distances = np.sqrt(np.sum((keypoints[:, :2] - [center_x, center_y])**2, axis=1))
    l = np.max(distances)
    normalized_keypoints = (keypoints - [center_x, center_y, 0]) / l
    return normalized_keypoints.tolist(), center_x, center_y, l

# Function to extract hand keypoints from an image
def extract_hand_keypoints(image):
    # Convert the BGR image to RGB
    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Process the image with MediaPipe Hands
    results = hands.process(rgb_image)

    hand_keypoints = {'left_hand_pts': [], 'right_hand_pts': [], 'is_left': False, 'is_right': False}

    # Check if hand landmarks are detected
    if results.multi_hand_landmarks:
        for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
            # Extract hand landmark coordinates
            landmarks = np.array([[landmark.x, landmark.y, landmark.z] for landmark in hand_landmarks.landmark])
            # Determine if it's left or right hand
            if handedness.classification[0].label == 'Left':
                hand_keypoints['left_hand_pts'] = landmarks.tolist()
                hand_keypoints['is_left'] = True
            else:
                hand_keypoints['right_hand_pts'] = landmarks.tolist()
                hand_keypoints['is_right'] = True

    # Return None if no landmarks are found
    if not hand_keypoints['is_left'] and not hand_keypoints['is_right']:
        return None

    return hand_keypoints

# Function to load and normalize the template keypoints from JSON file
def load_and_normalize_json(json_path):
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
        left_normalized, _, _, _ = normalize_keypoints(left_hand_points)
    else:
        left_normalized = []

    if right_hand_points:
        right_hand_points = np.mean(right_hand_points, axis=0)
        right_normalized, _, _, _ = normalize_keypoints(right_hand_points)
    else:
        right_normalized = []

    return {'left_hand_pts': left_normalized, 'right_hand_pts': right_normalized, 
            'is_left': bool(left_normalized), 'is_right': bool(right_normalized)}

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
        direction_x = 'left' if delta_x > 0 else 'right' if delta_x < 0 else ''
        direction_y = 'up' if delta_y > 0 else 'down' if delta_y < 0 else ''
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

def process_webcam(model, gesture_name, template_keypoints, buffer_size=4):
    cap = cv2.VideoCapture(0)

    while cap.isOpened():
        success, image = cap.read()
        if not success:
            print("Ignoring empty camera frame.")
            continue

        # Extract hand keypoints
        current_keypoints = extract_hand_keypoints(image)
        if current_keypoints is None:
            cv2.putText(image, "No hand detected", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
            cv2.imshow('Hand Gesture Recognition', image)
            if cv2.waitKey(5) & 0xFF == 27:
                break
            continue

        # Normalize current keypoints
        normalized_keypoints = {'is_left': False, 'is_right': False}
        if current_keypoints['is_left']:
            normalized_keypoints['left_hand_pts'], _, _, _ = normalize_keypoints(current_keypoints['left_hand_pts'])
            normalized_keypoints['is_left'] = True
        if current_keypoints['is_right']:
            normalized_keypoints['right_hand_pts'], _, _, _ = normalize_keypoints(current_keypoints['right_hand_pts'])
            normalized_keypoints['is_right'] = True

        # Predict gesture using the model (assuming the model has a predict function that returns gesture class)
        gesture_class = model.predict(image)  # Pass the raw image to the model for prediction

        # Update the prediction buffer
        prediction_buffer.append(gesture_class)
        buffer_text = f"Buffer: {prediction_buffer}"
        cv2.putText(image, buffer_text, (10,50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2, cv2.LINE_AA)
        # Check if buffer is full and filled with other predictions
        if len(prediction_buffer) == buffer_size:
            # Compare keypoints and provide feedback
            adjustments = compare_keypoints(normalized_keypoints, template_keypoints)
            draw_adjustments(image, adjustments, current_keypoints)
            prediction_buffer.clear()  # Clear the buffer after processing

        # Display the image
        cv2.imshow('Hand Gesture Recognition', image)
        if cv2.waitKey(5) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()

# Load the normalized template keypoints for the specific gesture
gesture_name = "ChanDingYin"
json_filename = "keypoint/ChanDingYin_normalized.json"
template_keypoints = load_and_normalize_json(json_filename)

# Assuming you have a trained model that can classify gestures
class TrainedModel:
    def __init__(self):
        self.target_size = (224, 224)
        self.model = tf.keras.models.load_model("interface/Model/color_fps4_splited_dataset.h5")

    def predict(self, frame):
        processed_image = cv2.resize(frame, self.target_size)
        x = tf.expand_dims(processed_image, 0)
        pred = self.model.predict(x)[0]
        prediction = GESTURES_INDICS[pred.argmax()]
        return prediction

model = TrainedModel()

# Process webcam input and provide feedback
process_webcam(model, gesture_name, template_keypoints)
# print(template_keypoints)