from pathlib import Path
import shutil
import imageio
from PIL import Image
import numpy as np
import math
import json
import os
import cv2
import mediapipe as mp
        
def get_frames_from_video(videoPath, ctg, skip_fps, target_size, videoName, imgPath):
    """ 
    imgPath: the directory to save the images
    videoPath: the path to the video
    ctg: number of classes of hand gestures
    fps: the number of frames to skip
    target_size: the size of the image
    videoName: name of the video
    """
    # check if video exists
    if not Path(videoPath).exists():
        print('Video {} not exists'.format(videoPath))
        return
    
    # process the video
    cap = cv2.VideoCapture(videoPath)
    i = 0
    # variable to set number of frames to skip
    frame_skip = skip_fps
    # variable to keep track of the frame to be saved
    frame_count = 0
    # make directory for categories in data folder if folder not exists
    cwd = os.getcwd()
    print("current dir: {}".format(cwd))
    mkdir( Path(imgPath))
    mkdir(Path(imgPath+ctg))

    # a while loop to extract frames
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        if i > frame_skip - 1:
            processed_frame = image_processing(target_size, frame, True)
            if processed_frame is None:
                continue
            frame_count += 1
            #frame name
            frame_name = '{}_{}.jpg'.format(videoName, frame_count)
            #frame path
            frame_path = imgPath+ ctg + "/" + frame_name
            cv2.imwrite(frame_path, processed_frame)
            i = 0
            continue
        i += 1

    cap.release()


def process_videos(fps, target_size, imgPath):
    '''
    fps: int
    target_size: tuple(width, height)
    '''

    # video folder directory 
    base_dir = Path('./data')
    print(base_dir)
    video_dir = base_dir / 'video' / 'selectedGesture'
    print(video_dir)
    categories = get_sub_dir(video_dir)
    print('Total number of gesture classes: {}, which are {}'.format(len(categories), categories))

    # convert the frames in video to jpg
    # process videos in each category
    for ctg in categories:
        # get all the path of  all video in a category
        videos = [
            path for path in (video_dir / ctg).iterdir() if path.is_file()
        ]
        for video in videos:
          try:
              # print("video_dir:{}".format(video_dir))
              # print("ctg:{}".format(ctg))
              # print("video:{}".format(video))
              videoName = str(video).split("/")[-1].replace(".mp4", "")
              print('Processing video{} at path: {}'.format(videoName, "./"+ str(video)))
              # process video 
              get_frames_from_video( "./"+ str(video) , ctg ,fps, target_size, videoName, imgPath)
          except:
              print("get into trouble in {}".format(video))
              continue

    # split_dataset("splited_dataset", imgPath)
    print('videos process completed.')

def split_dataset(image_folder, org_img_dir, video_folder, splited_dataset_folder):
    """
    Args:
        image_folder (string): destination folder to save the splited dataset
        org_img_dir (path): the path to the original images
        video_folder (string): the name of the videos folder stored the
        splited_dataset_folder (string): the name of the splited dataset
    """
    
    base_dir = Path('./data')
    video_dir = base_dir / 'video' / video_folder
    categories = get_child_dir_names(video_dir)
    print('The {} number of classes are: {}'.format(len(categories), categories))
    mkdir(base_dir/splited_dataset_folder)
    data_dir = Path(base_dir/splited_dataset_folder) # data_dir is the directory to save the splited dataset
    org_img_dir = Path(org_img_dir)
    
    
    # create directory for training, validation and testing set
    train_dir = data_dir / 'train'
    val_dir = data_dir / 'val'
    test_dir = data_dir / 'test'
    for dir in [train_dir, val_dir, test_dir]:
        mkdir(dir)
        for ctg in categories:
            mkdir(dir / ctg) #create folder for each gesture

    # random split the images
    for ctg in categories:
        cur_dir = org_img_dir / ctg
        jpgs = np.array([image for image in cur_dir.iterdir() if image.match('*.jpg')])#turn the image in the category into array
        train, val, test = random_split(jpgs) #split the array into train, val, test    
        move_paths(train, train_dir / ctg)
        move_paths(val, val_dir / ctg)
        move_paths(test, test_dir / ctg)

def get_sub_dir(path):
    """
    return list of the child directory names 
    """
    return [dir.name for dir in path.iterdir() if dir.is_dir()]

def count_jpgs(path):
    return len(list(path.rglob('*.jpg')))


def move_paths(paths, dst_dir):
    # move the file to the destination directory
    for path in paths:
        dst = dst_dir / path.name
        shutil.move(path, dst)
        print('{} is moved to {}'.format(path, dst))


def random_split(x, train_ratio, val_ratio):
    """
    Args:
    x: the np.array of the images
    train_ratio: the ratio of the training set
    val_ratio: the ratio of the validation set
    """
    random.seed(99)
    np.random.shuffle(x)
    n = len(x)
    train = math.ceil(n * train_ratio)
    val = math.ceil(n * val_ratio) 
    test = train+val
    train, val, test = x[:train],  x[train:test], x[test:]
    return train, val, test


def mkdir(path):
    if not path.exists():
        path.mkdir()
        print('{} created'.format(path))
    else:
        print('{} already exists'.format(path))


def show_predict(y, class_indices_reverse):
    '''
    Arguments
    y - ndarray(1, n)
    class_indices_reverse: a list of class indices of gestures
    '''
    for i in range(len(y)):
        print('The prediction of hand gesture is {:.2f}% {}'.format(y[i]*100, class_indices_reverse[i]))
    
    

def save_confg(indices, input_size, fp):
    '''
    Arguments
    indic - dict
    fp - file path
    '''
    config = {
        'indices': indices,
        'input_size': input_size
    }
    with open(fp, 'w', encoding='UTF-8') as f:
        json.dump(config, f,ensure_ascii=False)
        
def show_pred_max_toString(y, class_indices_reverse):
    """_summary_

    Args:
        y : prediction result
        class_indices_reverse: the dictionary of class indices

    Returns:
        string of result 
    """
    max = y.argmax()
    return f"{class_indices_reverse[max]}: {y[max]*100}%"

def image_processing(target_size, img, hand_area_only):
    """ image processing - resize the image to 224 * 224 , then apply median filter and gaussian filter. Finally, apply auto contrast adjustment to the images

    Args:
        target_size (int, int): input =( width, height)
        img (np_array): input image
        hand_area_only ( boolean ): True/False - determine whether to crop the hand area only or not
    """
    # crap the hand regions
    if hand_area_only:
        getFlag, img= crop_hand_area(img)
        if not getFlag:
            return None
    # image processing
    # apply median filter to image
    filteredImg = cv2.medianBlur(img, ksize=3)
    # apply gaussian filter to image
    gaussBlurImg = cv2.GaussianBlur(filteredImg,(3,3),0)
    # automatic contrast adjustment
    adjustedImg = auto_contrast_adjustment(gaussBlurImg, 255, 0)
    # convert image to grayscale
    grayImg = cv2.cvtColor(adjustedImg, cv2.COLOR_BGR2GRAY)
    # apply binary thresholding to image
    ret, threshImg = cv2.threshold(grayImg,160,255,cv2.THRESH_BINARY)
    # apply canny edge detection to image
    cannyImg = cv2.Canny(threshImg,10,100)
    # resize the image to target size
    resizedImg = cv2.resize(cannyImg, target_size)
    return resizedImg

def auto_contrast_adjustment(img, max_val, min_val):
    image = img.copy()

    low, high = image.min(), image.max()

    image = min_val + (image - low) * ((max_val - min_val) / (high - low))

    return image.astype(np.uint8) # for canny edge detection

def crop_hand_area(img, adj_x = 0, adj_y = 0, adj_w = 0, adj_h = 0):
    """ crop the hand area only

    Args:
        img (np_array): input image
        adj_x (int): number of pixel to shift horizontally
        ady_y (int): number of pixel to shift vertically
    Returns:
        img (np_array): output image
    """
    b, g, r = cv2.split(img)
    # Create a binary mask based on the skin rgb color 
    skin_mask = np.logical_and.reduce((r > 85, r - b > 10, r - g > 10)).astype(np.uint8) * 255
    
    # Find the largest skin part ( i.e. hand region)
    contours, _ = cv2.findContours(skin_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) # find contours
    if len(contours) > 0:
        # Find the largest contour (hand)
        largest_contour = max(contours, key=cv2.contourArea)

        # Calculate the bounding rectangle of the largest contour
        x, y, w, h = cv2.boundingRect(largest_contour)
        #adjust cropped hand region
        w += adj_w
        h += adj_h
        x += adj_x
        y += adj_y
        cropped_image = img[y:y+h, x:x+w]
        return True, cropped_image
    
    return False, None
def find_hand_region(img, adj_x = 0, adj_y = 0, adj_w = 0, adj_h = 0):
    """ crop the hand area only

    Args:
        img (np_array): input image
        adj_x (int): number of pixel to shift horizontally
        ady_y (int): number of pixel to shift vertically
    Returns:
        img (np_array): output image
    """
    b, g, r = cv2.split(img)
    # Create a binary mask based on the skin rgb color 
    skin_mask = np.logical_and.reduce((r > 85, r - b > 10, r - g > 10)).astype(np.uint8) * 255
    
    # Find the largest skin part ( i.e. hand region)
    contours, _ = cv2.findContours(skin_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) # find contours
    if len(contours) > 0:
        # Find the largest contour (hand)
        largest_contour = max(contours, key=cv2.contourArea)

        # Calculate the bounding rectangle of the largest contour
        x, y, w, h = cv2.boundingRect(largest_contour)
        #adjust cropped hand region
        w += adj_w
        h +=adj_h
        x += adj_x
        y += adj_y
        return True, [x, y, w, h]
    
    return False, None