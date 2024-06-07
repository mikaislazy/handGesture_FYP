import cv2
import numpy as np
import matplotlib.pyplot as plt
from utils import auto_contrast_adjustment

# Load the image
image = cv2.imread('hh3jpg.jpg')  # Load in grayscale

# Apply auto contrast adjustment
adjusted_image = auto_contrast_adjustment(image, 255, 0)

# Calculate the difference between the original and adjusted images
difference = cv2.absdiff(image, adjusted_image)

# Normalize the difference image
difference = cv2.normalize(difference, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8U)

# Print statistics of the difference image
print(f"Difference Image - min: {difference.min()}, max: {difference.max()}, mean: {difference.mean()}, std: {difference.std()}")

# Display the original, adjusted, and difference images
# cv2.imshow('Original Image', image)
# cv2.imshow('Adjusted Image', adjusted_image)
cv2.imwrite("adjusted.jpg", adjusted_image)
# cv2.imshow('Difference Image', difference)

# Plot the histogram of the original, adjusted, and difference images
plt.figure(figsize=(18, 6))

plt.subplot(131)
plt.hist(image.ravel(), 256, [0, 256])
plt.title('Original Image Histogram')

plt.subplot(132)
plt.hist(adjusted_image.ravel(), 256, [0, 256])
plt.title('Adjusted Image Histogram')

plt.subplot(133)
plt.hist(difference.ravel(), 256, [0, 256])
plt.title('Difference Image Histogram')

plt.show()

# Wait for a key press and destroy all windows
cv2.waitKey(0)
cv2.destroyAllWindows()
