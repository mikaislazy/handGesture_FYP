import os
import cv2
import mediapipe as mp
import numpy as np
import json
from . import common_utils
from constants import GESTURES

# Function to extract the hand landmarks keypoints from the frames
def get_hand_landmarks_keypoints_dataset(category, main_dataset_folder):
    for gesture in category:
        gesture_keypoints = {}

        gesture_path = os.path.join(main_dataset_folder, gesture)
        print(f"Processing gesture: {gesture}")

        if os.path.exists(gesture_path):
            for image_filename in os.listdir(gesture_path):
                image_path = os.path.join(gesture_path, image_filename)

                # Load the image
                image = cv2.imread(image_path)

                # Extract hand keypoints from the image
                hand_keypoints = common_utils.extract_hand_keypoints(image)

                # Save the keypoints in the dictionary
                img_name = os.path.splitext(image_filename)[0]
                gesture_keypoints[img_name] = hand_keypoints
        else:
            print(f"Path not found: {gesture_path}")

        # Save all keypoints for the current gesture in a separate JSON file
        json_filename = f'{gesture}.json'
        with open(json_filename, 'w', encoding='UTF-8') as f:
            json.dump(gesture_keypoints, f, ensure_ascii=False, indent=4)
        
        print(f"Finished processing hand keypoints for gesture: {gesture}")

if __name__ == "__main__":
    main_dataset_folder = '../data/frame_fps4'
    get_hand_landmarks_keypoints_dataset(GESTURES, main_dataset_folder)
