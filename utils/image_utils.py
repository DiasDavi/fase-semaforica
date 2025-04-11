import cv2
import numpy as np

def resize_img(image, target_size):
    return cv2.resize(image, target_size)

def crop_and_preprocess(image, target_size):
    image = cv2.resize(image, target_size)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image = image.astype('float32') / 255.0
    image = np.expand_dims(image, axis=0)
    return image

def draw_traffic_lights(img_path, detections):
    image = cv2.imread(img_path)
    for det in detections:
        x1, y1, x2, y2 = det["bbox"]
        label = f"{det['classification']} ({det['classification_confidence']*100:.1f}%)"
        cv2.rectangle(image, (x1, y1), (x2, y2), (0, 0, 0), 2)
        cv2.putText(image, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
    return image
