import torch
import yaml
import cv2
import base64
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing import image as keras_image
from PIL import Image

# Caminhos para os modelos e configurações
detector_model_path = 'models/detector/best.pt'  # Caminho para o modelo
detector_config_path = 'models/detector/config.yaml'  # Caminho para o YAML de configuração
classifier_model_path = 'models/classifier/classifier.h5'  # Caminho para o modelo de classificação
classes_path = 'models/classifier/classes.txt'  # Caminho para o arquivo de classes

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
    # Carregar as configurações
    config = load_config(detector_config_path)

    # Configurar IOU e confiança
    detector_model.iou = config['iou']  
    detector_model.conf = config['confidence'] 

    # Redimensionar a imagem para 640x640
    resized_image = cv2.resize(image, (640, 640))

    # Fazer inferência com o modelo YOLOv5 usando a imagem redimensionada
    results = detector_model(resized_image)

    detections = []
    classifications = []

    # Carregar as classes do arquivo
    classification_labels = load_classes(classes_path)

    for *box, conf, cls in results.xyxy[0].cpu().numpy():
        x1, y1, x2, y2 = map(int, box)
        detection_label = detector_model.names[int(cls)]
        detection_confidence = float(conf)
    
        # Recortar a imagem com base na bounding box
        cropped_image = resized_image[y1:y2, x1:x2]

        # Converter de BGR para RGB para evitar distorção de cores
        cropped_image_rgb = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2RGB)

        # Usar PIL para redimensionar a imagem
        pil_image = Image.fromarray(cropped_image_rgb)  
        pil_image = pil_image.resize((224, 224), Image.Resampling.LANCZOS) 
        pil_image.save("cropped_image.jpg", 'JPEG')

        # Preparar a imagem para classificação
        cropped_image_resized = keras_image.img_to_array(pil_image)  
        cropped_image_resized = np.expand_dims(cropped_image_resized, axis=0) 

        # Fazer a classificação
        classification = classifier_model.predict(cropped_image_resized)
        classification_label = classification_labels[np.argmax(classification)]
        classification_confidence = float(np.max(classification))

        # Determinar cor do bbox com base na classificação
        color_map = {'verde': (0, 255, 0), 'amarelo': (0, 255, 255), 'vermelho': (0, 0, 255)}
        bbox_color = color_map[classification_label]

        # Desenhar o bounding box e a classificação na imagem original redimensionada
        cv2.rectangle(resized_image, (x1, y1), (x2, y2), bbox_color, 2)
        cv2.putText(resized_image, classification_label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, bbox_color, 2)

        # Adicionar os dados ao resultado final
        detections.append({
            "label": detection_label,
            "bbox": [x1, y1, x2, y2],
            "confidence": detection_confidence,  # Garantir que é um float nativo
        })

        classifications.append({
            "classification": classification_label,
            "confidence": classification_confidence,  # Garantir que é um float nativo
        })

    # Redimensionar a imagem final para 888x640
    final_image = cv2.resize(resized_image, (888, 640))

    # Converter a imagem para base64
    _, buffer = cv2.imencode('.jpg', final_image)
    image_base64 = base64.b64encode(buffer).decode('utf-8')

    # Retornar as detecções, classificações, e a imagem processada
    return {
        "detections": detections,
        "classifications": classifications,
        "image_base64": image_base64
    }

def load_detector_config():
    with open(detector_config_path, 'r') as file:
        return yaml.safe_load(file)

# Função para sobrescrever as configurações no arquivo YAML
def config_detect(updates):
    # Carregar o arquivo de configuração existente
    config = load_config(detector_config_path)
    # Atualizar as configurações com os valores recebidos no JSON
    config['iou'] = updates.get('iou', config['iou'])
    config['confidence'] = updates.get('confidence', config['confidence'])

    # Sobrescrever o arquivo YAML com as novas configurações
    with open(detector_config_path, 'w') as file:
        yaml.safe_dump(config, file)

    print(f"Configurações atualizadas: IOU={config['iou']}, Confiança={config['confidence']}")
