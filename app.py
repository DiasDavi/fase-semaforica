import cv2
import numpy as np
from flask import Flask, render_template, request, jsonify
import functions

# Inicializar a aplicação Flask
app = Flask(__name__)

# Rota principal para renderizar a página HTML
@app.route('/')
def index():
    return render_template('index.html')

# Rota POST para receber e processar imagem
@app.route('/detect', methods=['POST'])
def detect_route():
    if 'file' not in request.files:
        return jsonify({"error": "Nenhuma imagem enviada"}), 400
    
    # Receber a imagem
    file = request.files['file']
    img = np.frombuffer(file.read(), np.uint8)
    img = cv2.imdecode(img, cv2.IMREAD_COLOR)
    img = cv2.resize(img, (640, 640))
    
    # Realizar a detecção usando a função detect importada
    detections = functions.run(img)
    
    # Retornar os resultados
    return jsonify({"detections": detections})

# Rota GET para obter as configurações do detector
@app.route('/detect/config', methods=['GET'])
def get_config():
    # Carregar as configurações do arquivo YAML
    config = functions.load_detector_config()

    # Retornar as configurações como um JSON
    return jsonify({
        'iou': config.get('iou', 50),  # Valor padrão 50 caso não exista
        'confidence': config.get('confidence', 50)  # Valor padrão 50 caso não exista
    })

# Rota POST para atualizar as configurações do detector
@app.route('/detect/config', methods=['POST'])
def config_route():
    # Verifica se o conteúdo da requisição é JSON
    if not request.is_json:
        return jsonify({"error": "Formato de dados não é JSON"}), 400

    # Receber o JSON com as novas configurações
    config_updates = request.get_json()
    
    # Validar a presença de "iou" e "confidence" no JSON
    if 'iou' not in config_updates or 'confidence' not in config_updates:
        return jsonify({"error": "'iou' e 'confidence' são obrigatórios"}), 400

    # Atualizar as configurações no YAML
    functions.config_detect(config_updates)

    return jsonify({"message": "Configurações atualizadas com sucesso", "iou": config_updates['iou'], "confidence": config_updates['confidence']}), 200



# Rodar a aplicação Flask
if __name__ == "__main__":
    app.run(debug=True)