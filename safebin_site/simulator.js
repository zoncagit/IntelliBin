/**
 * IntelliBin AI Simulator
 * Waste-specific material classification using Hugging Face model
 */

// ============================================
// CONFIGURATION
// ============================================

const API_URL = "http://localhost:8000";
const CONFIDENCE_THRESHOLD = 0.5;

// ============================================
// MATERIAL CONTAINERS (5 Categories Only)
// ============================================

const CONTAINERS = {
  paper: {
    id: "BIN-001",
    name: "Paper",
    material: "paper",
    capacity: 500,
    current_fill: 0,
    color: "#4A90D9",
    icon: "P"
  },
  plastic: {
    id: "BIN-002",
    name: "Plastic",
    material: "plastic",
    capacity: 500,
    current_fill: 0,
    color: "#E6A23C",
    icon: "PL"
  },
  glass: {
    id: "BIN-003",
    name: "Glass",
    material: "glass",
    capacity: 300,
    current_fill: 0,
    color: "#67C23A",
    icon: "G"
  },
  metal: {
    id: "BIN-004",
    name: "Metal",
    material: "metal",
    capacity: 400,
    current_fill: 0,
    color: "#909399",
    icon: "M"
  },
  other: {
    id: "BIN-005",
    name: "Other Materials",
    material: "other",
    capacity: 500,
    current_fill: 0,
    color: "#F56C6C",
    icon: "O"
  }
};

// ============================================
// STATE
// ============================================

let disposalLog = [];
let currentDetection = null;
let cameraStream = null;
let isScanning = false;

// DOM Elements
let elements = {};

// ============================================
// INITIALIZATION
// ============================================

document.addEventListener("DOMContentLoaded", () => {
  cacheElements();
  renderContainers();
  renderLog();
  setupEventListeners();
  checkAPIHealth();
});

function cacheElements() {
  elements = {
    // Scanner
    cameraFeed: document.getElementById("camera-feed"),
    captureCanvas: document.getElementById("capture-canvas"),
    previewImage: document.getElementById("preview-image"),
    scanOverlay: document.getElementById("scan-overlay"),
    scannerPlaceholder: document.getElementById("scanner-placeholder"),
    scannerStatus: document.getElementById("scanner-status"),
    
    // Buttons
    scanBtn: document.getElementById("scan-btn"),
    cameraBtn: document.getElementById("camera-btn"),
    uploadInput: document.getElementById("upload-input"),
    confirmDisposeBtn: document.getElementById("confirm-dispose-btn"),
    rescanBtn: document.getElementById("rescan-btn"),
    retryBtn: document.getElementById("retry-btn"),
    
    // Result displays
    detectionResult: document.getElementById("detection-result"),
    detectionError: document.getElementById("detection-error"),
    resultMaterial: document.getElementById("result-material"),
    resultObject: document.getElementById("result-object"),
    resultConfidence: document.getElementById("result-confidence"),
    errorText: document.getElementById("error-text"),
    
    // Containers & Log
    materialContainers: document.getElementById("material-containers"),
    disposalLog: document.getElementById("disposal-log"),
    logCount: document.getElementById("log-count"),
    
    // Modals
    disposalModal: document.getElementById("disposal-modal"),
    errorModal: document.getElementById("error-modal")
  };
}

function setupEventListeners() {
  // Scan button
  elements.scanBtn.addEventListener("click", handleScan);
  
  // Camera toggle
  elements.cameraBtn.addEventListener("click", toggleCamera);
  
  // File upload
  elements.uploadInput.addEventListener("change", handleFileUpload);
  
  // Confirm disposal
  elements.confirmDisposeBtn.addEventListener("click", handleDispose);
  
  // Rescan buttons
  elements.rescanBtn.addEventListener("click", resetScanner);
  elements.retryBtn.addEventListener("click", resetScanner);
  
  // Modal close buttons
  document.getElementById("close-disposal-modal").addEventListener("click", closeDisposalModal);
  document.getElementById("popup-close-btn").addEventListener("click", closeDisposalModal);
  document.getElementById("close-error-modal").addEventListener("click", closeErrorModal);
  document.getElementById("error-close-btn").addEventListener("click", closeErrorModal);
  
  // Close modals on overlay click
  elements.disposalModal.addEventListener("click", (e) => {
    if (e.target.id === "disposal-modal") closeDisposalModal();
  });
  elements.errorModal.addEventListener("click", (e) => {
    if (e.target.id === "error-modal") closeErrorModal();
  });
}

// ============================================
// API COMMUNICATION
// ============================================

async function checkAPIHealth() {
  try {
    const response = await fetch(`${API_URL}/health`);
    if (response.ok) {
      console.log("[Simulator] API connected");
      updateScannerStatus("READY", true);
    } else {
      throw new Error("API not responding");
    }
  } catch (error) {
    console.warn("[Simulator] API not available:", error.message);
    updateScannerStatus("API_OFFLINE", false);
  }
}

async function detectMaterial(imageBlob) {
  const formData = new FormData();
  formData.append("image", imageBlob, "scan.jpg");
  
  try {
    const response = await fetch(`${API_URL}/detect`, {
      method: "POST",
      body: formData
    });
    
    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error("[Simulator] Detection failed:", error);
    throw error;
  }
}

// ============================================
// CAMERA HANDLING
// ============================================

async function toggleCamera() {
  if (cameraStream) {
    stopCamera();
  } else {
    await startCamera();
  }
}

async function startCamera() {
  try {
    cameraStream = await navigator.mediaDevices.getUserMedia({
      video: {
        facingMode: "environment",
        width: { ideal: 640 },
        height: { ideal: 480 }
      }
    });
    
    elements.cameraFeed.srcObject = cameraStream;
    elements.cameraFeed.style.display = "block";
    elements.scannerPlaceholder.style.display = "none";
    elements.previewImage.style.display = "none";
    
    updateScannerStatus("CAMERA_ACTIVE", true);
    console.log("[Simulator] Camera started");
    
  } catch (error) {
    console.error("[Simulator] Camera error:", error);
    showError("Camera access denied or unavailable");
  }
}

function stopCamera() {
  if (cameraStream) {
    cameraStream.getTracks().forEach(track => track.stop());
    cameraStream = null;
  }
  
  elements.cameraFeed.srcObject = null;
  elements.cameraFeed.style.display = "none";
  elements.scannerPlaceholder.style.display = "flex";
  
  updateScannerStatus("READY", true);
}

function captureFrame() {
  const video = elements.cameraFeed;
  const canvas = elements.captureCanvas;
  
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  
  const ctx = canvas.getContext("2d");
  ctx.drawImage(video, 0, 0);
  
  return new Promise(resolve => {
    canvas.toBlob(resolve, "image/jpeg", 0.9);
  });
}

// ============================================
// FILE UPLOAD HANDLING
// ============================================

function handleFileUpload(event) {
  const file = event.target.files[0];
  if (!file) return;
  
  // Stop camera if running
  stopCamera();
  
  // Show preview
  const reader = new FileReader();
  reader.onload = (e) => {
    elements.previewImage.src = e.target.result;
    elements.previewImage.style.display = "block";
    elements.scannerPlaceholder.style.display = "none";
  };
  reader.readAsDataURL(file);
  
  // Process the file
  processImage(file);
  
  // Reset input for re-uploads
  event.target.value = "";
}

// ============================================
// SCANNING LOGIC
// ============================================

async function handleScan() {
  if (isScanning) return;
  
  // Determine image source
  let imageBlob;
  
  if (cameraStream) {
    // Capture from camera
    imageBlob = await captureFrame();
    
    // Show captured frame
    elements.cameraFeed.style.display = "none";
    elements.previewImage.src = elements.captureCanvas.toDataURL();
    elements.previewImage.style.display = "block";
    
  } else if (elements.previewImage.src && elements.previewImage.style.display !== "none") {
    // Use existing preview (from upload)
    const response = await fetch(elements.previewImage.src);
    imageBlob = await response.blob();
    
  } else {
    showError("Please start camera or upload an image first");
    return;
  }
  
  await processImage(imageBlob);
}

async function processImage(imageBlob) {
  isScanning = true;
  updateScannerStatus("SCANNING", true);
  elements.scanOverlay.classList.add("scanning");
  
  // Hide previous results
  elements.detectionResult.style.display = "none";
  elements.detectionError.style.display = "none";
  
  try {
    const result = await detectMaterial(imageBlob);
    console.log("[Simulator] Detection result:", result);
    
    // Check confidence threshold
    if (result.confidence < CONFIDENCE_THRESHOLD) {
      showDetectionError("Unable to classify item. Confidence too low. Please try again.");
      return;
    }
    
    // Store result and show
    currentDetection = result;
    showDetectionResult(result);
    
  } catch (error) {
    showDetectionError("Detection failed. Please check if the API is running.");
  } finally {
    isScanning = false;
    elements.scanOverlay.classList.remove("scanning");
    updateScannerStatus("SCAN_COMPLETE", true);
  }
}

function showDetectionResult(result) {
  const materialName = result.material.toUpperCase();
  const confidence = Math.round(result.confidence * 100);
  const detectedObject = result.detected_object || "unknown";
  
  elements.resultMaterial.textContent = materialName;
  elements.resultMaterial.className = `result-material material-${result.material}`;
  elements.resultConfidence.textContent = `${confidence}%`;
  
  // Show detected object name
  if (elements.resultObject) {
    elements.resultObject.textContent = detectedObject;
  }
  
  elements.detectionResult.style.display = "block";
  elements.detectionError.style.display = "none";
}

function showDetectionError(message) {
  elements.errorText.textContent = message;
  elements.detectionError.style.display = "block";
  elements.detectionResult.style.display = "none";
}

function resetScanner() {
  currentDetection = null;
  
  // Hide results
  elements.detectionResult.style.display = "none";
  elements.detectionError.style.display = "none";
  
  // Reset preview
  elements.previewImage.style.display = "none";
  elements.previewImage.src = "";
  
  // Show camera or placeholder
  if (cameraStream) {
    elements.cameraFeed.style.display = "block";
  } else {
    elements.scannerPlaceholder.style.display = "flex";
  }
  
  updateScannerStatus("READY", true);
}

function updateScannerStatus(status, online) {
  elements.scannerStatus.textContent = `[ ${status} ]`;
  elements.scannerStatus.className = `header-tag ${online ? "" : "offline"}`;
}

// ============================================
// DISPOSAL LOGIC
// ============================================

function handleDispose() {
  if (!currentDetection) return;
  
  const material = currentDetection.material;
  const container = CONTAINERS[material];
  
  if (!container) {
    showErrorModal("Unknown material category");
    return;
  }
  
  // Check capacity
  const fillAmount = 50;
  if (container.current_fill + fillAmount > container.capacity) {
    showErrorModal(`Container ${container.id} is full!`);
    return;
  }
  
  // Update container
  container.current_fill += fillAmount;
  
  // Log entry
  const timestamp = new Date().toLocaleTimeString("en-US", {
    hour12: false,
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit"
  });
  
  const logEntry = {
    time: timestamp,
    material: material,
    confidence: currentDetection.confidence,
    container: container.id,
    detected_object: currentDetection.detected_object
  };
  
  disposalLog.unshift(logEntry);
  
  // Update UI
  renderContainers();
  renderLog();
  
  // Show confirmation
  showDisposalModal(currentDetection, container, timestamp);
  
  // Reset scanner
  resetScanner();
}

// ============================================
// RENDERING
// ============================================

function renderContainers() {
  const containerDiv = elements.materialContainers;
  containerDiv.innerHTML = "";
  
  Object.entries(CONTAINERS).forEach(([key, container]) => {
    const widget = createContainerWidget(container);
    containerDiv.appendChild(widget);
  });
}

function createContainerWidget(container) {
  const fillPercent = (container.current_fill / container.capacity) * 100;
  const isFull = fillPercent >= 100;
  const isWarning = fillPercent >= 70 && fillPercent < 100;
  
  const widget = document.createElement("div");
  widget.className = `material-widget ${isFull ? "full" : ""} material-${container.material}`;
  widget.innerHTML = `
    <div class="material-icon" style="background: ${container.color}">
      ${container.icon}
    </div>
    <div class="material-info">
      <div class="material-header">
        <span class="material-name">${container.name}</span>
        <span class="material-status ${isFull ? "full" : isWarning ? "warning" : ""}"></span>
      </div>
      <div class="material-id">${container.id}</div>
      <div class="material-bar">
        <div class="material-bar-fill ${isFull ? "full" : isWarning ? "high" : ""}" 
             style="width: ${Math.min(fillPercent, 100)}%; background: ${container.color}"></div>
      </div>
      <div class="material-fill-text">${container.current_fill}/${container.capacity}</div>
    </div>
  `;
  
  return widget;
}

function renderLog() {
  const logContainer = elements.disposalLog;
  const logCount = elements.logCount;
  
  logCount.textContent = `[ ${disposalLog.length} ENTRIES ]`;
  
  if (disposalLog.length === 0) {
    logContainer.innerHTML = `
      <div class="log-empty">
        <span class="log-comment">// No disposals yet</span>
        <span class="log-comment">// Scan an item to begin</span>
      </div>
    `;
    return;
  }
  
  logContainer.innerHTML = disposalLog.slice(0, 20).map(entry => `
    <div class="log-entry">
      <span class="log-time">[${entry.time}]</span>
      <span class="log-object">${entry.detected_object || "item"}</span>
      <span class="log-material material-${entry.material}">${entry.material.toUpperCase()}</span>
      <span class="log-confidence">${Math.round(entry.confidence * 100)}%</span>
      <span class="log-container">${entry.container}</span>
    </div>
  `).join("");
}

// ============================================
// MODALS
// ============================================

function showDisposalModal(detection, container, timestamp) {
  document.getElementById("popup-object").textContent = detection.detected_object || "item";
  document.getElementById("popup-material").textContent = detection.material.toUpperCase();
  document.getElementById("popup-confidence").textContent = `${Math.round(detection.confidence * 100)}%`;
  document.getElementById("popup-container").textContent = `${container.id} (${container.name})`;
  document.getElementById("popup-time").textContent = timestamp;
  
  elements.disposalModal.classList.add("active");
}

function closeDisposalModal() {
  elements.disposalModal.classList.remove("active");
}

function showErrorModal(message) {
  document.getElementById("error-message").textContent = message;
  elements.errorModal.classList.add("active");
}

function closeErrorModal() {
  elements.errorModal.classList.remove("active");
}

function showError(message) {
  showDetectionError(message);
}

// ============================================
// RESET
// ============================================

function resetSimulator() {
  // Reset containers
  Object.values(CONTAINERS).forEach(container => {
    container.current_fill = 0;
  });
  
  // Clear log
  disposalLog = [];
  
  // Reset scanner
  resetScanner();
  stopCamera();
  
  // Re-render
  renderContainers();
  renderLog();
  
  // Show toast
  showToast("SYSTEM_RESET");
}

// ============================================
// UTILITIES
// ============================================

function showToast(message) {
  const toast = document.createElement("div");
  toast.style.cssText = `
    position: fixed;
    bottom: 2rem;
    left: 50%;
    transform: translateX(-50%);
    background: rgba(10, 10, 10, 0.9);
    color: #db835c;
    padding: 1rem 2rem;
    border: 1px solid rgba(219, 131, 92, 0.4);
    border-radius: 4px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.8rem;
    z-index: 3000;
    backdrop-filter: blur(10px);
    box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    pointer-events: none;
    opacity: 0;
    transition: all 0.3s ease;
  `;
  toast.textContent = `[ STATUS ]: ${message}`;
  document.body.appendChild(toast);
  
  setTimeout(() => {
    toast.style.opacity = "1";
    toast.style.transform = "translateX(-50%) translateY(-10px)";
  }, 10);
  
  setTimeout(() => {
    toast.style.opacity = "0";
    setTimeout(() => toast.remove(), 300);
  }, 3000);
}

// Expose reset function globally
window.resetSimulator = resetSimulator;
