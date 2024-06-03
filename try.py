import cv2
import numpy as np

# Open the webcam
cap = cv2.VideoCapture(0)

while True:
    # Capture frame-by-frame
    ret, img = cap.read()

    # If the frame was successfully captured
    if ret:
        # Applying Bilateral Filter
        img = cv2.bilateralFilter(img, d=9, sigmaColor=75, sigmaSpace=75)
        
        # Converting from BGR to HSV color space
        img_HSV = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        HSV_mask = cv2.inRange(img_HSV, (0, 30, 60), (20, 150, 255))
        HSV_mask = cv2.medianBlur(HSV_mask, 5)

        # Converting from BGR to YCbCr color space
        img_YCrCb = cv2.cvtColor(img, cv2.COLOR_BGR2YCrCb)
        YCrCb_mask = cv2.inRange(img_YCrCb, (0, 133, 77), (235, 173, 127))
        YCrCb_mask = cv2.medianBlur(YCrCb_mask, 5)

        # Merge skin detection (YCbCr and HSV)
        global_mask = cv2.bitwise_and(YCrCb_mask, HSV_mask)
        global_mask = cv2.medianBlur(global_mask, 5)
        global_mask = cv2.morphologyEx(global_mask, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))

        global_result = cv2.bitwise_and(img, img, mask=global_mask)

        # Display the resulting frame
        cv2.imshow('Webcam', global_result)

    # If 'q' is pressed on the keyboard, exit the loop
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture and destroy the windows
cap.release()
cv2.destroyAllWindows()
