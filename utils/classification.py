import numpy as np
import tensorflow as tf
import yaml
from config._config import CLASSIFIER_MODEL_PATH, CLASSIFICATION_IMG_SIZE, CLASS_NAMES, CLASSIFIER_CONFIG_YAML
from utils.image_utils import crop_and_preprocess

MODEL = tf.keras.models.load_model(CLASSIFIER_MODEL_PATH)

def classify_traffic_light(cropped_img):
    image = crop_and_preprocess(cropped_img, CLASSIFICATION_IMG_SIZE)
    predictions = MODEL.predict(image)
    class_index = np.argmax(predictions)
    confidence = np.max(predictions)    
    return CLASS_NAMES[class_index], confidence

def load_classifier_config():
    with open(CLASSIFIER_CONFIG_YAML, 'r') as file:
        return yaml.safe_load(file)
    
def update_classifier_config(update):
    config = load_classifier_config()
    config['confidence'] = update.get('confidence', config['confidence'])
    
    with open(CLASSIFIER_CONFIG_YAML, 'w') as file:
        yaml.safe_dump(config, file)