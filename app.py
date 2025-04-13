import os
import tempfile
import warnings
import logging

# Oculta logs do TensorFlow C++
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

# Oculta todos os warnings do Python
warnings.filterwarnings('ignore')

# Oculta logs do logger do TensorFlow (Python)
logging.getLogger('tensorflow').setLevel(logging.ERROR)

import cv2
import numpy as np
import base64
from flask import Flask, Response, json, render_template, request, jsonify, stream_with_context
from utils.detection import detect_bboxes, load_detector_config, update_detector_config
from utils.classification import classify_traffic_light, load_classifier_config, update_classifier_config
from utils.traffic_light_tracker import SimpleTracker

# Inicializar a aplicação Flask
app = Flask(__name__)

# Rota principal para renderizar a página HTML
@app.route('/')
def index():
    return render_template('index.html')

# Rota GET para obter as configurações do detector
@app.route('/detector/config', methods=['GET'])
def get_detector_config_route():
    detector_config = load_detector_config()
    return detector_config

# Rota POST para atualizar as configurações do detector
@app.route('/detector/config', methods=['POST'])
def update_detector_config_route():
    if not request.is_json:
        return jsonify({"error": "Formato de dados não é JSON"}, 400)
    
    config_updates = request.get_json()
    update_detector_config(config_updates)
    
    return jsonify({"message": "Configurações atualizadas com sucesso", "confidence": config_updates['confidence'], "iou": config_updates["iou"]}), 200

# Rota GET para obter a configuração de confiança do classificador
@app.route('/classifier/config', methods=['GET'])
def get_classifier_config_route():
    classifier_config = load_classifier_config()
    return classifier_config

# Rota POST para atualizar as configurações do classificador
@app.route('/classifier/config', methods=['POST'])
def update_classifier_config_route():
    if not request.is_json:
        return jsonify({"error": "Formato de dados não é JSON"}), 400

    config_updates = request.get_json()
    update_classifier_config(config_updates)

    return jsonify({"message": "Configurações atualizadas com sucesso", "confidence": config_updates['confidence']}), 200

# Rota POST para receber e processar imagem
@app.route('/detect-image', methods=['POST'])
def traffic_light_ia_route():
    if 'file' not in request.files:
        return jsonify({"error": "Nenhuma imagem enviada"}), 400

    file = request.files['file']
    npimg = np.frombuffer(file.read(), np.uint8)
    img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)

    detections_raw = detect_bboxes(img)

    traffic_lights = []
    for idx, det in enumerate(detections_raw):
        x1, y1, x2, y2 = det["bbox"]
        crop = img[y1:y2, x1:x2]
        class_name, class_conf = classify_traffic_light(crop)

        traffic_lights.append({
            **det,
            "classification": class_name,
            "classification_confidence": class_conf
        })

    classifier_config = load_classifier_config()
    confidence_threshold = classifier_config['confidence']

    color_map = {'verde': (0, 255, 0), 'amarelo': (0, 255, 255), 'vermelho': (0, 0, 255)}
    detections = []
    classifications = []

    for light in traffic_lights:
        x1, y1, x2, y2 = light["bbox"]
        class_name = light["classification"]
        class_conf = light["classification_confidence"]
        det_conf = light["confidence"]

        if class_conf >= confidence_threshold:
            color = color_map.get(class_name, (255, 255, 255))
            cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
            cv2.putText(img, class_name, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)

            detections.append({
                "bbox": [x1, y1, x2, y2],
                "confidence": round(det_conf,2)
            })
            classifications.append({
                "classification": class_name,
                "confidence": round(float(class_conf), 2)
            })

    final_image = cv2.resize(img, (888, 640))
    _, buffer = cv2.imencode('.jpg', final_image)
    image_base64 = base64.b64encode(buffer).decode('utf-8')

    return jsonify({
        "detections": {
            "detections": detections,
            "classifications": classifications,
            "image_base64": image_base64
        }
    })
    
# Rota POST para receber e processar vídeo
@app.route('/detect-video', methods=['POST'])
def traffic_light_video_route():
    if 'file' not in request.files:
        return jsonify({"error": "Nenhum vídeo enviado"}), 400

    file = request.files['file']

    # Salva o vídeo temporariamente
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp_file:
        tmp_file.write(file.read())
        tmp_path = tmp_file.name

    def generate_frames():
        cap = cv2.VideoCapture(tmp_path)
        tracker = SimpleTracker(max_distance=150, max_age=50)

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            detections = detect_bboxes(frame)
            boxes_for_tracker = []
            classes_for_tracker = []

            for det in detections:
                x1, y1, x2, y2 = det['bbox']
                conf = det['confidence']
                crop = frame[y1:y2, x1:x2]
                class_name, _ = classify_traffic_light(crop)

                boxes_for_tracker.append([x1, y1, x2, y2, conf])
                classes_for_tracker.append(class_name)

            tracked = tracker.update(boxes_for_tracker, classes_for_tracker)

            frame_data = {
                "detections": [],
                "classifications": []
            }

            for track_id, x1, y1, x2, y2, class_name in tracked:
                color = (0, 255, 0) if class_name == "verde" else (0, 255, 255) if class_name == "amarelo" else (0, 0, 255)
                cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)
                cv2.putText(frame, f"{class_name} ID {track_id}", (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

                frame_data["detections"].append({
                    "id": track_id,
                    "bbox": [int(x1), int(y1), int(x2), int(y2)]
                })
                frame_data["classifications"].append({
                    "id": track_id,
                    "classification": class_name
                })

            # Codifica frame
            _, buffer = cv2.imencode('.jpg', frame)
            frame_base64 = base64.b64encode(buffer).decode('utf-8')
            frame_data["frame_base64"] = frame_base64

            yield json.dumps(frame_data) + "\n"

        cap.release()

    return Response(stream_with_context(generate_frames()), mimetype='application/x-ndjson')


# Rodar a aplicação Flask
if __name__ == "__main__":
        app.run(host="0.0.0.0", port=5000, debug=True)
