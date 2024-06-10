import tensorflow as tf
from gesture_constants import GESTURES_INDICS
import cv2
import os
# Assuming you have a trained model that can classify gestures
class VGGModel:
    def __init__(self):
        self.target_size = (224, 224)
        
        model_file = os.path.join(os.path.dirname(__file__), 'overall_dataset.h5')
        self.model = tf.keras.models.load_model(model_file)

    
    def get_max_prediction(self, frame):
        """Get the maximum prediction result for a given frame.

        Args:
            frame (numpy.ndarray): The input frame for prediction.

        Returns:
            tuple: A tuple containing the predicted class and its corresponding percentage.
                The predicted class is a string and the percentage is a float.
        """
          # Resize the frame to the target size
        processed_image = cv2.resize(frame, self.target_size)
        # Expand the dimensions of the processed image
        x = tf.expand_dims(processed_image, 0)
        # Make the prediction using the model
        pred = self.model.predict(x)[0]
        max_class_idx = pred.argmax()
        return pred, GESTURES_INDICS[max_class_idx], pred[max_class_idx]*100
