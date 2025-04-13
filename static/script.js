// script.js

// Elementos do DOM
const fileInput = document.getElementById('fileInput');
const outputImage = document.getElementById('outputImage');
const noImageText = document.getElementById('noImageText');
const imageContainer = document.getElementById('imageContainer');
const detectResult = document.getElementById('detect-result');
const classResult = document.getElementById('class-result');

// Sliders
const detectorIouSlider = document.getElementById('rangeIoU');
const detectorConfidenceSlider = document.getElementById('rangeConfidenceDetector');
const classifierConfidenceSlider = document.getElementById('rangeConfidenceClassifier');

// Carregar configurações ao iniciar
window.onload = async function() {
    await loadDetectorConfig();
    await loadClassifierConfig();
    checkImage();
};

async function loadDetectorConfig() {
    try {
        const response = await fetch('/detector/config', { method: 'GET' });
        if (!response.ok) throw new Error('Erro ao carregar as configurações');
        const config = await response.json();
        detectorIouSlider.value = config.iou * 100;  
        detectorConfidenceSlider.value = config.confidence * 100;  
        document.getElementById('rangeValueConfidenceDetector').textContent = config.confidence * 100;
        document.getElementById('rangeValueIoU').textContent = config.iou * 100;
    } catch (error) {
        console.error(error);
        alert('Erro ao tentar carregar as configurações.');
    }
}

async function loadClassifierConfig() {
    try {
        const response = await fetch('/classifier/config', { method: 'GET' });
        if (!response.ok) throw new Error('Erro ao carregar as configurações');
        const config = await response.json();
        classifierConfidenceSlider.value = config.confidence * 100;
        document.getElementById('rangeValueConfidenceClassifier').textContent = config.confidence * 100;
    } catch (error) {
        console.error(error);
        alert('Erro ao tentar carregar as configurações.');
    }
}

// Verificar a visibilidade da imagem
function checkImage() {
    if (!outputImage.src) {
        outputImage.style.display = 'none';
        imageContainer.style.backgroundColor = 'black';
        noImageText.style.display = 'block';
    } else {
        imageContainer.style.backgroundColor = '';
        noImageText.style.display = 'none';
        outputImage.style.display = 'block';
    }
}

// Atualizar a imagem com o resultado da detecção
function updateImage(base64Image) {
    outputImage.src = `data:image/jpeg;base64,${base64Image}`;
    checkImage();
}

// Enviar configurações do detector
async function updateConfig(iou, confidence) {
    const configData = { iou: iou / 100, confidence: confidence / 100 };
    try {
        await fetch('/detector/config', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(configData)
        });
    } catch (error) {
        alert('Erro ao atualizar as configurações.');
    }
}

// Enviar configurações do classificador
async function updateClassifierConfig(confidence) {
    const configData = { confidence: confidence / 100 };
    try {
        await fetch('/classifier/config', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(configData)
        });
    } catch (error) {
        alert('Erro ao atualizar as configurações.');
    }
}

// Atualizar valores dos sliders
function updateSliderValue(type, value) {
    let valueElement;
    switch (type) {
        case 'detector-confidence': valueElement = document.getElementById('rangeValueConfidenceDetector'); break;
        case 'classifier-confidence': valueElement = document.getElementById('rangeValueConfidenceClassifier'); break;
        case 'detector-iou': valueElement = document.getElementById('rangeValueIoU'); break;
        default: break;
    }

    if (valueElement) valueElement.textContent = value;

    if (type === 'detector-confidence') {
        updateConfig(detectorIouSlider.value, value);
    } else if (type === 'detector-iou') {
        updateConfig(value, detectorConfidenceSlider.value);
    } else if (type === 'classifier-confidence') {
        updateClassifierConfig(classifierConfidenceSlider.value);
    }
}

// Upload e processamento do arquivo
async function handleFileUpload(event) {
    const file = event.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    const isVideo = file.type.startsWith('video');
    const endpoint = isVideo ? '/detect-video' : '/detect-image';

    try {
        const response = await fetch(endpoint, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            alert('Erro ao processar o arquivo.');
            return;
        }

        if (isVideo) {
            // Remover conteúdo antigo
            imageContainer.innerHTML = '';
            imageContainer.appendChild(outputImage); // Reinsere o <img> se tiver sido removido
            outputImage.style.display = 'block';
            noImageText.style.display = 'none';

            const reader = response.body.getReader();
            const decoder = new TextDecoder('utf-8');
            let buffer = '';

            async function processStream() {
                while (true) {
                    const { value, done } = await reader.read();
                    if (done) break;

                    buffer += decoder.decode(value, { stream: true });
                    const parts = buffer.split('\n');

                    for (let i = 0; i < parts.length - 1; i++) {
                        try {
                            const frameData = JSON.parse(parts[i]);
                            updateImage(frameData.frame_base64);
                            detectResult.textContent = JSON.stringify(frameData.detections, null, 2);
                            classResult.textContent = JSON.stringify(frameData.classifications, null, 2);
                        } catch (err) {
                            console.error("Erro ao processar frame:", err);
                        }
                    }

                    buffer = parts[parts.length - 1];
                    await new Promise(resolve => setTimeout(resolve, 100)); // Simula ~10 FPS
                }
            }

            processStream();

        } else {
            const json = await response.json();
            updateImage(json.detections.image_base64);
            detectResult.textContent = JSON.stringify(json.detections.detections, null, 2);
            classResult.textContent = JSON.stringify(json.detections.classifications, null, 2);
        }

    } catch (error) {
        alert('Erro ao enviar o arquivo.');
        console.error(error);
    }
}

// Evento para captura do arquivo
fileInput.addEventListener('change', handleFileUpload);
