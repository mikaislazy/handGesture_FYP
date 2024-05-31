import os
import cv2
import mediapipe as mp
import numpy as np
import json

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()

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

def get_hand_landmarks_keypoints_dataset(category, main_dataset_folder, sub_dataset_folder):
    for gesture in category:
        gesture_keypoints = {}

        for sub in sub_dataset_folder:
            gesture_sub_path = os.path.join(main_dataset_folder, sub, gesture)
            print(gesture_sub_path)
            if os.path.exists(gesture_sub_path):
                for image_filename in os.listdir(gesture_sub_path):
                    image_path = os.path.join(gesture_sub_path, image_filename)

                    # Load the image
                    image = cv2.imread(image_path)

                    # Extract hand keypoints from the image
                    hand_keypoints = extract_hand_keypoints(image)

                    # Save the keypoints in the dictionary
                    img_name = os.path.splitext(image_filename)[0]
                    gesture_keypoints[img_name] = hand_keypoints
            else:
                print(f"Path not found: {gesture_sub_path}")

        # Save all keypoints for the current gesture in a separate JSON file
        json_filename = f'{gesture}.json'
        with open(json_filename, 'w', encoding='UTF-8') as f:
            json.dump(gesture_keypoints, f, ensure_ascii=False, indent=4)
        
        print(f"Finished processing hand keypoints for gesture: {gesture}")

if __name__ == '__main__':
    # Process the dataset
    main_dataset_folder = 'data/color_fps4_hand_splited_dataset'
    sub_dataset_folder = ['train', 'test', 'val']
    category = [
        "ChanDingYin",
        "HuoYanYin",
        "MiTuoDingYin",
        "Retsu",
        "Rin",
        "TaiJiYin",
        "Zai",
        "Zen",
        "ZhiJiXiangYin"
    ]
    get_hand_landmarks_keypoints_dataset(category, main_dataset_folder, sub_dataset_folder)
