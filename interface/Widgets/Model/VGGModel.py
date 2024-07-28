import tensorflow as tf
from gesture_constants import GESTURES_INDICS
import cv2
import os

class VGGModel:
    def __init__(self):
        self.target_size = (224, 224)
        
        model_file = os.path.join(os.path.dirname(__file__), 'overall_dataset.h5')
        self.model = tf.keras.models.load_model(model_file)

    
    def get_max_prediction(self, frame):
        # Resize the frame to the target size
        processed_image = cv2.resize(frame, self.target_size)
        # Expand the dimensions of the processed image
        x = tf.expand_dims(processed_image, 0)
        # Make the prediction using the model
        pred = self.model.predict(x)[0]
        max_class_idx = pred.argmax()
        return pred, GESTURES_INDICS[max_class_idx], pred[max_class_idx]*100
