// script.js

// Elementos do DOM
const fileInput = document.getElementById('fileInput');
const outputImage = document.getElementById('outputImage');
const noImageText = document.getElementById('noImageText');
const imageContainer = document.getElementById('imageContainer');
const detectResult = document.getElementById('detect-result');
const classResult = document.getElementById('class-result');

// Elementos dos sliders
const iouSlider = document.getElementById('rangeIoU');
const confidenceSlider = document.getElementById('rangeConfidenceDetector');

// Verifique se a imagem foi carregada corretamente ao carregar a página
window.onload = async function() {
    await loadConfig();
    checkImage();
};

async function loadConfig() {
    try {
        const response = await fetch('/detect/config', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            throw new Error('Erro ao carregar as configurações');
        }

        const config = await response.json();

        
        iouSlider.value = config.iou * 100;  
        confidenceSlider.value = config.confidence * 100;  

        document.getElementById('rangeValueConfidenceDetector').textContent = config.confidence * 100;
        document.getElementById('rangeValueIoU').textContent = config.iou * 100;

    } catch (error) {
        console.error(error);
        alert('Erro ao tentar carregar as configurações.');
    }
}



// Função para verificar a visibilidade da imagem
function checkImage() {
    if (!outputImage.src) {
        // Caso não haja uma imagem carregada, exibir mensagem e fundo preto
        outputImage.style.display = 'none';
        imageContainer.style.backgroundColor = 'black';
        noImageText.style.display = 'block';
    } else {
        // Se houver imagem carregada, exibir a imagem e ocultar a mensagem
        imageContainer.style.backgroundColor = '';
        noImageText.style.display = 'none';
        outputImage.style.display = 'block';
    }
}

// Função para atualizar a imagem com base no retorno do backend
function updateImage(base64Image) {
    outputImage.src = `data:image/jpeg;base64,${base64Image}`;
    checkImage(); // Verifique se a imagem foi carregada corretamente
}

// Função para enviar as configurações de 'iou' e 'confidence' para o backend
async function updateConfig(iou, confidence) {
    const configData = {
        // Divida por 100 para enviar os valores reais (decimais)
        iou: iou / 100,
        confidence: confidence / 100
    };

    try {
        // Envio das configurações para o backend
        const response = await fetch('/detect/config', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(configData)
        });

        const result = await response.json();
    } catch (error) {
        alert('Erro ao atualizar as configurações.');
    }
}

// Função para atualizar os valores dos sliders e enviar as configurações
function updateSliderValue(type, value) {
    const valueElement = type === 'confidence' 
        ? document.getElementById('rangeValueConfidenceDetector') 
        : document.getElementById('rangeValueIoU');

    valueElement.textContent = value;

    
    if (type === 'confidence') {
        updateConfig(iouSlider.value, value);
    } else if (type === 'iou') {
        updateConfig(value, confidenceSlider.value);
    }
}

// Função para tratar o upload do arquivo
async function handleFileUpload(event) {
    const file = event.target.files[0];  // Obtém o arquivo selecionado
    if (!file) return;  // Se nenhum arquivo for selecionado, não faz nada

    const formData = new FormData();
    formData.append('file', file);  // Adiciona o arquivo ao FormData

    try {
        // Envio assíncrono do arquivo para o backend
        const response = await fetch('/detect', {
            method: 'POST',
            body: formData
        });

        const json = await response.json();

        if (response.ok) {
            // Atualiza a imagem com o resultado da detecção
            updateImage(json.detections.image_base64);
            // Exibe resultados de detecção e classificação
            detectResult.textContent = JSON.stringify(json.detections.detections, null, 2);
            classResult.textContent = JSON.stringify(json.detections.classifications, null, 2);
        } else {
            alert('Erro ao processar a imagem.');
        }
    } catch (error) {
        alert('Erro ao enviar a imagem.');
    }
}

// Evento para capturar a seleção do arquivo
fileInput.addEventListener('change', handleFileUpload);
