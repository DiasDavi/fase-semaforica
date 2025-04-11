from ultralytics import YOLO
import yaml
from config._config import DETECT_MODEL_PATH, DETECTION_IMG_SIZE, DETECTOR_CONFIG_YAML

MODEL = YOLO(DETECT_MODEL_PATH)

def load_detector_config():
    with open(DETECTOR_CONFIG_YAML, "r") as file:
        return yaml.safe_load(file)
    
def detect_bboxes(image):
    config = load_detector_config()
    
    results = MODEL.predict(source=image, 
                            imgsz=DETECTION_IMG_SIZE[0], 
                            conf=config['confidence'], 
                            iou=config['iou'],
                            verbose=False)
    boxes = results[0].boxes

    return [ 
        {
            "bbox": tuple(map(int, box.xyxy[0])),
            "confidence": float(box.conf[0])
        } for box in boxes
    ]


    
def update_detector_config(update):
    config = load_detector_config()
    config['confidence'] = update.get('confidence', config['confidence'])
    config['iou'] = update.get('iou', config['iou'])
    
    with open(DETECTOR_CONFIG_YAML, 'w') as file:
        yaml.safe_dump(config, file)