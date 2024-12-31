const ROBOFLOW_API_KEY = "0r4klCQmalPo9Xw2xkj6";
const ROBOFLOW_MODEL_ENDPOINT = "https://detect.roboflow.com/recyclableitems/2";

let currentStream = null;
let camera = document.getElementById('camera');
let overlay = document.getElementById('overlay');
let captureBtn = document.getElementById('captureBtn');
let switchCameraBtn = document.getElementById('switchCameraBtn');
let facingMode = 'environment';

const wasteInfo = {
    'Valuable Waste - Cans': {
        label: 'Latas',
        binColor: '#9E9E9E',
        icon: 'https://s3-srd-project.s3.us-east-2.amazonaws.com/img/setUp_metal.png',
        disposalInstructions: 'Depositar en contenedor de metal/latas',
        recyclable: 'Sí - 100% reciclable',
        decompositionTime: '80-100 años',
    },
    'Valuable Waste - Cardboard': {
        label: 'Carton',
        binColor: '#2196F3',
        icon: 'https://s3-srd-project.s3.us-east-2.amazonaws.com/img/setUp_carton.png',
        disposalInstructions: 'Depositar en contenedor de papel/cartón',
        recyclable: 'Sí - 100% reciclable',
        decompositionTime: '1 año',
    },
    'Valuable Waste - Glass': {
        label: 'Vidrio',
        binColor: '#4CAF50',
        icon: 'https://s3-srd-project.s3.us-east-2.amazonaws.com/img/setUp_vidrio.png',
        disposalInstructions: 'Depositar en contenedor de vidrio',
        recyclable: 'Sí - 100% reciclable',
        decompositionTime: '4000 años',
    },
    'Valuable Waste - Metal': {
        label: 'Metal',
        binColor: '#9E9E9E',
        icon: 'https://s3-srd-project.s3.us-east-2.amazonaws.com/img/setUp_metal.png',
        disposalInstructions: 'Depositar en contenedor de metal',
        recyclable: 'Sí - 100% reciclable',
        decompositionTime: '500 años',
    },
    'Valuable Waste - Paper': {
        label: 'Papel',
        binColor: '#2196F3',
        icon: 'https://s3-srd-project.s3.us-east-2.amazonaws.com/img/setUp_plastico.png',
        disposalInstructions: 'Depositar en contenedor de papel',
        recyclable: 'Sí - 100% reciclable',
        decompositionTime: '1 año',
    },
    'Valuable Waste - Plastic': {
        label: 'Plastico',
        binColor: '#FFC107',
        icon: 'https://s3-srd-project.s3.us-east-2.amazonaws.com/img/setUp_plastico.png',
        disposalInstructions: 'Depositar en contenedor de plástico',
        recyclable: 'Sí - Reciclable según el tipo',
        decompositionTime: '500 años',
    },
    'Valuable Waste - Plastic bottles': {
        label: 'Botella',
        binColor: '#FFC107',
        icon: 'https://s3-srd-project.s3.us-east-2.amazonaws.com/img/setUp_plastico.png',
        disposalInstructions: 'Depositar en contenedor de plástico',
        recyclable: 'Sí - 100% reciclable',
        decompositionTime: '450 años',
    }
};

// Tab switching logic
const cameraTab = document.getElementById('cameraTab');
const uploadTab = document.getElementById('uploadTab');
const cameraSection = document.getElementById('cameraSection');
const uploadSection = document.getElementById('uploadSection');
const dropZone = document.getElementById('dropZone');
const fileInput = document.getElementById('fileInput');

// Function to process image through Roboflow API
async function processImageWithRoboflow(imageFile) {
    try {
        // Show loading state
        Swal.fire({
            title: 'Procesando imagen...',
            html: 'Por favor espera mientras analizamos la imagen.',
            allowOutsideClick: false,
            didOpen: () => {
                Swal.showLoading();
            }
        });

        // Convert image file to base64
        const base64Image = await convertToBase64(imageFile);
        const base64Data = base64Image.split(',')[1];

        // Make API request to Roboflow
        const response = await axios({
            method: "POST",
            url: ROBOFLOW_MODEL_ENDPOINT,
            params: {
                api_key: ROBOFLOW_API_KEY
            },
            data: base64Data,
            headers: {
                "Content-Type": "application/x-www-form-urlencoded"
            }
        });

        // Close loading dialog
        Swal.close();

        // Process and display results
        if (response.data && response.data.predictions) {
            const formattedDetections = formatDetections(response.data.predictions);
            displayDetections(formattedDetections);
        } else {
            throw new Error('No se detectaron objetos en la imagen');
        }
    } catch (error) {
        console.error('Error processing image:', error);
        Swal.fire({
            icon: 'error',
            title: 'Error',
            text: error.message || 'No se pudo procesar la imagen. Por favor, intenta de nuevo.',
        });
    }
}

// Helper function to convert file to base64
function convertToBase64(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.readAsDataURL(file);
        reader.onload = () => resolve(reader.result);
        reader.onerror = error => reject(error);
    });
}

// Format detections to match our application's structure
function formatDetections(predictions) {
    return predictions.map(prediction => ({
        label: prediction.class,
        confidence: prediction.confidence,
        coordinates: {
            x: prediction.x,
            y: prediction.y,
            width: prediction.width,
            height: prediction.height
        }
    }));
}

function createResultElement(info, detection) {
    const resultElement = document.createElement('div');
    resultElement.className = 'waste-result-card';
    
    // Determine waste type class for styling
    const wasteTypeClass = `waste-type-${info.label.toLowerCase()}`;
    
    resultElement.innerHTML = `
        <div class="waste-header ${wasteTypeClass}">
            <div class="waste-icon-container">
                <img src="${info.icon}" alt="${info.label}" class="waste-icon">
            </div>
            <div class="flex-1">
                <h3 class="text-black text-2xl font-bold mb-2">${info.label}</h3>
                <div class="inline-block px-3 py-1 rounded-full bg-white bg-opacity-25">
                    <span class="text-black font-medium">
                        ${(detection.confidence * 100).toFixed(1)}% de confianza
                    </span>
                </div>
            </div>
        </div>
        <div class="waste-info">
            <div class="waste-stat">
                <i class="fas fa-recycle text-green-500"></i>
                <div>
                    <h4 class="font-medium">Estado de Reciclaje</h4>
                    <p class="text-gray-600">${info.recyclable}</p>
                </div>
            </div>
            <div class="waste-stat">
                <i class="fas fa-trash-alt text-blue-500"></i>
                <div>
                    <h4 class="font-medium">Instrucciones</h4>
                    <p class="text-gray-600">${info.disposalInstructions}</p>
                </div>
            </div>
            <div class="waste-stat">
                <i class="fas fa-hourglass-half text-yellow-500"></i>
                <div>
                    <h4 class="font-medium">Tiempo de Descomposición</h4>
                    <p class="text-gray-600">${info.decompositionTime}</p>
                </div>
            </div>
        </div>
    `;
    
    return resultElement;
}

function displayDetections(detections) {
    const resultsDiv = document.getElementById('results');
    const detectionResults = document.getElementById('detectionResults');
    
    if (!resultsDiv || !detectionResults) {
        console.error('Required DOM elements not found');
        return;
    }
    
    resultsDiv.classList.remove('hidden');
    detectionResults.innerHTML = '';
    
    if (!detections || detections.length === 0) {
        detectionResults.innerHTML = '<p class="text-center text-gray-500">No se detectaron objetos</p>';
        return;
    }
    
    detections.forEach(detection => {
        const info = wasteInfo[detection.label];
        
        if (!info) {
            console.log('No waste info found for label:', detection.label);
            return;
        }
        
        const resultElement = createResultElement(info, detection);
        detectionResults.appendChild(resultElement);
    });

    resultsDiv.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

async function processFrame() {
    const canvas = document.createElement('canvas');
    canvas.width = camera.videoWidth;
    canvas.height = camera.videoHeight;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(camera, 0, 0);
    
    canvas.toBlob(async (blob) => {
        await processImageWithRoboflow(blob);
    }, 'image/jpeg', 0.8); // Added quality parameter for better performance
}

async function initCamera() {
    try {
        if (currentStream) {
            currentStream.getTracks().forEach(track => track.stop());
        }
        
        const constraints = {
            video: {
                facingMode: facingMode,
                width: { ideal: 1280 },
                height: { ideal: 720 }
            }
        };
        
        currentStream = await navigator.mediaDevices.getUserMedia(constraints);
        camera.srcObject = currentStream;
    } catch (error) {
        console.error('Error accessing camera:', error);
        Swal.fire({
            icon: 'error',
            title: 'Error de Cámara',
            text: 'No se pudo acceder a la cámara. Por favor, verifica los permisos.',
        });
    }
}

// Event Listeners
cameraTab.addEventListener('click', () => {
    cameraTab.classList.add('border-green-500');
    uploadTab.classList.remove('border-green-500');
    cameraSection.classList.remove('hidden');
    uploadSection.classList.add('hidden');
    initCamera();
});

uploadTab.addEventListener('click', () => {
    uploadTab.classList.add('border-green-500');
    cameraTab.classList.remove('border-green-500');
    uploadSection.classList.remove('hidden');
    cameraSection.classList.add('hidden');
    if (currentStream) {
        currentStream.getTracks().forEach(track => track.stop());
    }
});

dropZone.addEventListener('click', () => fileInput.click());

dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('border-blue-500');
});

dropZone.addEventListener('dragleave', () => {
    dropZone.classList.remove('border-blue-500');
});

dropZone.addEventListener('drop', async (e) => {
    e.preventDefault();
    dropZone.classList.remove('border-blue-500');
    const file = e.dataTransfer.files[0];
    if (file && file.type.startsWith('image/')) {
        await processImageWithRoboflow(file);
    }
});

fileInput.addEventListener('change', async (e) => {
    const file = e.target.files[0];
    if (file) {
        await processImageWithRoboflow(file);
        e.target.value = ''; // Reset file input
    }
});

captureBtn.addEventListener('click', async () => {
    await processFrame();
    // Add capture feedback animation
    captureBtn.classList.add('scale-95', 'opacity-75');
    setTimeout(() => {
        captureBtn.classList.remove('scale-95', 'opacity-75');
    }, 200);
});

switchCameraBtn.addEventListener('click', () => {
    facingMode = facingMode === 'environment' ? 'user' : 'environment';
    initCamera();
});

// Error handling for camera initialization
camera.addEventListener('loadedmetadata', () => {
    console.log('Camera initialized successfully');
});

camera.addEventListener('error', (error) => {
    console.error('Camera error:', error);
    Swal.fire({
        icon: 'error',
        title: 'Error de Cámara',
        text: 'Hubo un problema al inicializar la cámara. Por favor, verifica los permisos y vuelve a intentarlo.',
        confirmButtonText: 'Reintentar',
    }).then((result) => {
        if (result.isConfirmed) {
            initCamera();
        }
    });
});

// Handle page visibility changes
document.addEventListener('visibilitychange', () => {
    if (document.hidden && currentStream) {
        currentStream.getTracks().forEach(track => track.stop());
    } else if (!document.hidden && !currentStream && !uploadSection.classList.contains('hidden')) {
        initCamera();
    }
});

// Initialize camera when page loads
document.addEventListener('DOMContentLoaded', () => {
    // Check if the browser supports the required APIs
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        Swal.fire({
            icon: 'warning',
            title: 'Navegador no compatible',
            text: 'Tu navegador no soporta el acceso a la cámara. Por favor, utiliza un navegador moderno.',
        });
        // Automatically switch to upload tab
        uploadTab.click();
        return;
    }
    
    initCamera();
});