// script.js

// Elementos do DOM
const fileInput = document.getElementById('fileInput');
const outputImage = document.getElementById('outputImage');
const noImageText = document.getElementById('noImageText');
const imageContainer = document.getElementById('imageContainer');
const detectResult = document.getElementById('detect-result');
const classResult = document.getElementById('class-result');

// Elementos dos sliders
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

// Enviar as configurações de 'iou' e 'confidence' para o backend
async function updateConfig(iou, confidence) {
    const configData = { iou: iou / 100, confidence: confidence / 100 };
    try {
        await fetch('/detector/config', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(configData) });
    } catch (error) {
        alert('Erro ao atualizar as configurações.');
    }
}

// Enviar configurações de 'confidence' para o backend
async function updateClassifierConfig(confidence) {
    const configData = { confidence: confidence / 100 };
    try {
        await fetch('/classifier/config', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(configData) });
    } catch (error) {
        alert('Erro ao atualizar as configurações.');
    }
}

// Atualizar valores dos sliders e enviar configurações
function updateSliderValue(type, value) {
    var valueElement; 
    switch (type) {
        case 'detector-confidence': valueElement = document.getElementById('rangeValueConfidenceDetector'); break;
        case 'classifier-confidence': valueElement = document.getElementById('rangeValueConfidenceClassifier'); break;
        case 'detector-iou': valueElement = document.getElementById('rangeValueIoU'); break;
        default: break;
    }

    if (valueElement) { valueElement.textContent = value; }
    if (type === 'detector-confidence') { updateConfig(detectorIouSlider.value, value); }
    else if (type === 'detector-iou') { updateConfig(value, detectorConfidenceSlider.value); }
    else if (type === 'classifier-confidence') { updateClassifierConfig(classifierConfidenceSlider.value); }
}

// Tratar o upload do arquivo
async function handleFileUpload(event) {
    const file = event.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch('/detect', { method: 'POST', body: formData });
        const json = await response.json();
        if (response.ok) {
            updateImage(json.detections.image_base64);
            detectResult.textContent = JSON.stringify(json.detections.detections, null, 2);
            classResult.textContent = JSON.stringify(json.detections.classifications, null, 2);
        } else {
            alert('Erro ao processar a imagem.');
        }
    } catch (error) {
        alert('Erro ao enviar a imagem.');
    }
}

// Evento para capturar o arquivo selecionado
fileInput.addEventListener('change', handleFileUpload);