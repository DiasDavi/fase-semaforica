import torch
import yaml
import cv2
import base64
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing import image as keras_image
from PIL import Image

# Caminhos para os modelos e configurações
detector_model_path = 'models/detector/detector.pt'  
detector_config_path = 'models/detector/config.yaml'  
classifier_model_path = 'models/classifier/classifier.h5'  
classes_path = 'models/classifier/classes.txt'  
classifier_config_path = 'models/classifier/config.yaml'  

# Carregar o modelo YOLOv5 e o classificador
detector_model = torch.hub.load('ultralytics/yolov5', 'custom', path=detector_model_path)
classifier_model = tf.keras.models.load_model(classifier_model_path)

# Função para carregar as classes do arquivo classes.txt
def load_classes(classes_path):
    with open(classes_path, 'r') as file:
        classes = [line.strip() for line in file.readlines()]
    return classes

# Função para carregar configurações do YAML
def load_config(config_path):
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
    return config

# Função de detecção utilizando o modelo e as configurações carregadas
def run(image):
    # Carregar as configurações do detector e classificador
    detector_config = load_config(detector_config_path)
    classifier_config = load_config(classifier_config_path)

    # Configurar IOU e confiança para o detector
    detector_model.iou = detector_config['iou']  
    detector_model.conf = detector_config['confidence'] 

    # Configurar o limite de confiança para o classificador
    classifier_confidence_threshold = classifier_config['confidence']

    # Fazer inferência com o modelo YOLOv5
    results = detector_model(image)

    detections = []
    classifications = []

    # Carregar as classes do arquivo
    classification_labels = load_classes(classes_path)

    for *box, conf, cls in results.xyxy[0].cpu().numpy():
        x1, y1, x2, y2 = map(int, box)
        detection_label = detector_model.names[int(cls)]
        detection_confidence = float(conf)
    
        # Recortar a imagem para a classificação
        cropped_image = image[y1:y2, x1:x2]
        cropped_image_rgb = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(cropped_image_rgb).resize((224, 224), Image.Resampling.LANCZOS)
        
        # Preparar a imagem para classificação
        cropped_image_resized = keras_image.img_to_array(pil_image)  
        cropped_image_resized = np.expand_dims(cropped_image_resized, axis=0) 

        # Fazer a classificação
        classification = classifier_model.predict(cropped_image_resized)
        classification_label = classification_labels[np.argmax(classification)]
        classification_confidence = float(np.max(classification))

        if classification_confidence >= classifier_confidence_threshold:
            # Definir a cor do bounding box com base na classificação
            color_map = {'verde': (0, 255, 0), 'amarelo': (0, 255, 255), 'vermelho': (0, 0, 255)}
            bbox_color = color_map[classification_label]

            # Desenhar o bounding box e a classificação na imagem original
            cv2.rectangle(image, (x1, y1), (x2, y2), bbox_color, 2)
            cv2.putText(image, classification_label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, bbox_color, 2)

            # Adicionar aos resultados
            detections.append({
                "label": detection_label,
                "bbox": [x1, y1, x2, y2],
                "confidence": detection_confidence,
            })

            classifications.append({
                "classification": classification_label,
                "confidence": classification_confidence,
            })

    # Redimensionar a imagem final
    final_image = cv2.resize(image, (888, 640))

    # Converter a imagem para base64
    _, buffer = cv2.imencode('.jpg', final_image)
    image_base64 = base64.b64encode(buffer).decode('utf-8')

    # Retornar as detecções, classificações, e a imagem processada
    return {
        "detections": detections,
        "classifications": classifications,
        "image_base64": image_base64
    }

# Função para carregar configurações do detector YAML
def load_detector_config():
    with open(detector_config_path, 'r') as file:
        return yaml.safe_load(file)

# Função para sobrescrever as configurações no arquivo YAML
def config_detect(updates):
    config = load_config(detector_config_path)
    config['iou'] = updates.get('iou', config['iou'])
    config['confidence'] = updates.get('confidence', config['confidence'])

    with open(detector_config_path, 'w') as file:
        yaml.safe_dump(config, file)

# Função para carregar configurações do classificador YAML
def load_classifier_config():
    with open(classifier_config_path, 'r') as file:
        return yaml.safe_load(file)

# Função para sobrescrever as configurações no arquivo YAML
def config_classifier(updates):
    config = load_config(classifier_config_path)
    config['confidence'] = updates.get('confidence', config['confidence'])

    with open(classifier_config_path, 'w') as file:
        yaml.safe_dump(config, file)
