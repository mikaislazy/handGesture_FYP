import os
import cv2
import mediapipe as mp
import numpy as np
import pandas as pd
import csv

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()

# Function to extract hand keypoints from an image
def extract_hand_keypoints(image):
    # Convert the BGR image to RGB
    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Process the image with MediaPipe Hands
    results = hands.process(rgb_image)

    hand_keypoints = []

    # Check if hand landmarks are detected
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            # Extract hand landmark coordinates
            landmarks = np.array([[landmark.x, landmark.y, landmark.z] for landmark in hand_landmarks.landmark])
            hand_keypoints.append(landmarks.flatten())  # Flatten the 2D array to a 1D array
            

    return hand_keypoints

def get_hand_landmarks_keypoints_dataset(category, main_dataset_folder, sub_dataset_folder, csv_path):
    for gesture in category:
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

                    # Save hand keypoints and label to the dataset
                    
                    with open(csv_path, 'a', newline="") as f:
                        writer = csv.writer(f)
                        for h in hand_keypoints:
                            writer.writerow([gesture, list(h)])
        else:
            print("{} not exist".format(gesture_sub_path))
        print("Finish processing hand keypoints Dataset")

if __name__ == '__main__':
    # Process the dataset
    main_dataset_folder = 'data/color_fps4_hand_splited_dataset'
    sub_dataset_folder = ['train', 'test', 'val']
    dataset = {'keypoint_data': [], 'labels': []}
    category = [
            "ChanDingYin",
            "HuoYanYin",
            "MiTuoDingYin",
            "Retsu",
            "Rin",
            "TaiJiYin",
            "Zai",
            "Zen",
            "ZhiJiXiangYin"]
    csv_path = 'keypoints.csv'
    get_hand_landmarks_keypoints_dataset(category, main_dataset_folder, sub_dataset_folder, csv_path)