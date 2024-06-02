from pathlib import Path
import shutil
import numpy as np
import math
import json
import os
import cv2
import mediapipe as mp

def count_jpgs(path):
    return len(list(path.rglob('*.jpg')))

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
    # grayImg = cv2.cvtColor(adjustedImg, cv2.COLOR_BGR2GRAY)
    # apply binary thresholding to image
    # ret, threshImg = cv2.threshold(grayImg,160,255,cv2.THRESH_BINARY)
    # apply canny edge detection to image
    # cannyImg = cv2.Canny(threshImg,10,100)
    # resize the image to target size
    resizedImg = cv2.resize(adjustedImg, target_size)
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