from config._config import DETECT_MODEL_PATH, CLASSIFIER_MODEL_PATH, CLASS_NAMES
from utils.detection import detect_bboxes
from utils.classification import classify_traffic_light
from utils.image_utils import draw_traffic_lights
import cv2

IMAGE_PATH = "images/test/exemplo4.jpg"

# Detecta os semáforos
detections = detect_bboxes(IMAGE_PATH)

# Classifica cada detecção
traffic_lights = []
for det in detections:
    class_name, class_conf = classify_traffic_light(IMAGE_PATH, det["bbox"])
    traffic_lights.append({
        **det,
        "classification": class_name,
        "classification_confidence": class_conf
    })

# Carrega e desenha a imagem com anotações
image = draw_traffic_lights(IMAGE_PATH, traffic_lights)

# Exibe
cv2.imshow("Semáforos Classificados", image)
cv2.waitKey(0)
cv2.destroyAllWindows()
