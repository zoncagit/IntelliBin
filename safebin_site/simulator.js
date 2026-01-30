/**
 * IntelliBin Web Simulator
 * Waste disposal simulation system
 */

// ============================================
// DATA DEFINITIONS
// ============================================

const DISPOSABLES = [
  // Non-dangerous items
  { name: "Plastic Bottle", dangerous: false, category: "plastic" },
  { name: "Plastic Wrapper", dangerous: false, category: "plastic" },
  { name: "Paper Sheet", dangerous: false, category: "paper" },
  { name: "Cardboard Box", dangerous: false, category: "paper" },
  { name: "Newspaper", dangerous: false, category: "paper" },
  
  // Dangerous items
  { name: "Glass Vial", dangerous: true, category: "glass" },
  { name: "Broken Beaker", dangerous: true, category: "glass" },
  { name: "Petri Dish (Used)", dangerous: true, category: "microbio" },
  { name: "Culture Sample", dangerous: true, category: "microbio" },
  { name: "Contaminated Swab", dangerous: true, category: "microbio" },
  { name: "Aluminium Can", dangerous: true, category: "aluminium" },
  { name: "Foil Wrapper", dangerous: true, category: "aluminium" },
  { name: "Metal Scrap", dangerous: true, category: "metals" },
  { name: "Wire Fragments", dangerous: true, category: "metals" },
  { name: "Used Syringe", dangerous: true, category: "sharps" },
  { name: "Scalpel Blade", dangerous: true, category: "sharps" },
];

const CONTAINERS = {
  "NON-DANGEROUS": {
    id: "BIN-001",
    name: "General Waste",
    capacity: 500,
    current_fill: 0,
    dangerous: false,
  },
  "GLASS": {
    id: "BIN-002",
    name: "Glass Container",
    capacity: 300,
    current_fill: 0,
    dangerous: true,
  },
  "MICROBIO": {
    id: "BIN-003",
    name: "Biohazard",
    capacity: 200,
    current_fill: 0,
    dangerous: true,
  },
  "ALUMINIUM": {
    id: "BIN-004",
    name: "Aluminium",
    capacity: 300,
    current_fill: 0,
    dangerous: true,
  },
  "METALS": {
    id: "BIN-005",
    name: "Metal Waste",
    capacity: 300,
    current_fill: 0,
    dangerous: true,
  },
  "SHARPS": {
    id: "BIN-006",
    name: "Sharps Disposal",
    capacity: 150,
    current_fill: 0,
    dangerous: true,
  },
};

// Category to container mapping
const CATEGORY_MAP = {
  plastic: "NON-DANGEROUS",
  paper: "NON-DANGEROUS",
  glass: "GLASS",
  microbio: "MICROBIO",
  aluminium: "ALUMINIUM",
  metals: "METALS",
  sharps: "SHARPS",
};

// State
let disposalLog = [];

// ============================================
// INITIALIZATION
// ============================================

document.addEventListener("DOMContentLoaded", () => {
  initializeDropdown();
  renderContainers();
  renderLog();
  setupEventListeners();
});

function initializeDropdown() {
  const select = document.getElementById("item-select");
  select.innerHTML = "";
  
  DISPOSABLES.forEach((item, index) => {
    const option = document.createElement("option");
    option.value = index;
    option.textContent = item.name;
    select.appendChild(option);
  });
}

function setupEventListeners() {
  // Dispose button
  document.getElementById("dispose-btn").addEventListener("click", handleDispose);
  
  // Modal close buttons
  document.getElementById("close-disposal-modal").addEventListener("click", closeDisposalModal);
  document.getElementById("popup-close-btn").addEventListener("click", closeDisposalModal);
  document.getElementById("close-error-modal").addEventListener("click", closeErrorModal);
  document.getElementById("error-close-btn").addEventListener("click", closeErrorModal);
  
  // Close modals on overlay click
  document.getElementById("disposal-modal").addEventListener("click", (e) => {
    if (e.target.id === "disposal-modal") closeDisposalModal();
  });
  document.getElementById("error-modal").addEventListener("click", (e) => {
    if (e.target.id === "error-modal") closeErrorModal();
  });
}

// ============================================
// RENDERING
// ============================================

function renderContainers() {
  const safeContainer = document.getElementById("safe-containers");
  const dangerContainer = document.getElementById("danger-containers");
  
  safeContainer.innerHTML = "";
  dangerContainer.innerHTML = "";
  
  Object.entries(CONTAINERS).forEach(([key, container]) => {
    const widget = createContainerWidget(key, container);
    
    if (container.dangerous) {
      dangerContainer.appendChild(widget);
    } else {
      safeContainer.appendChild(widget);
    }
  });
}

function createContainerWidget(key, container) {
  const fillPercent = (container.current_fill / container.capacity) * 100;
  const isFull = fillPercent >= 100;
  const isWarning = fillPercent >= 70 && fillPercent < 100;
  
  const widget = document.createElement("div");
  widget.className = `container-widget ${isFull ? "full" : ""}`;
  widget.innerHTML = `
    <div class="container-header">
      <span class="container-id">${container.id}</span>
      <span class="container-status ${isFull ? "full" : isWarning ? "warning" : ""}"></span>
    </div>
    <div class="container-name">${container.name}</div>
    <div class="container-bar">
      <div class="container-bar-fill ${isFull ? "full" : isWarning ? "high" : ""}" 
           style="width: ${Math.min(fillPercent, 100)}%"></div>
    </div>
    <div class="container-fill-text">${container.current_fill}/${container.capacity}</div>
  `;
  
  return widget;
}

function renderLog() {
  const logContainer = document.getElementById("disposal-log");
  const logCount = document.getElementById("log-count");
  
  logCount.textContent = `[ ${disposalLog.length} ENTRIES ]`;
  
  if (disposalLog.length === 0) {
    logContainer.innerHTML = `
      <div class="log-empty">
        <span class="log-comment">// No disposals yet</span>
        <span class="log-comment">// Select an item and click DISPOSE</span>
      </div>
    `;
    return;
  }
  
  logContainer.innerHTML = disposalLog.slice(0, 20).map(entry => `
    <div class="log-entry">
      <span class="log-time">[${entry.time}]</span>
      <span class="log-icon ${entry.dangerous ? "danger" : "safe"}">${entry.dangerous ? "⚠" : "✓"}</span>
      <span class="log-item">${entry.item}</span>
      <span class="log-container">→ ${entry.container}</span>
    </div>
  `).join("");
}

// ============================================
// DISPOSAL LOGIC
// ============================================

function handleDispose() {
  const select = document.getElementById("item-select");
  const itemIndex = parseInt(select.value);
  const item = DISPOSABLES[itemIndex];
  
  if (!item) return;
  
  // Find target container
  const containerKey = CATEGORY_MAP[item.category];
  const container = CONTAINERS[containerKey];
  
  if (!container) return;
  
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
    item: item.name,
    dangerous: item.dangerous,
    container: container.id,
  };
  
  disposalLog.unshift(logEntry);
  
  // Update UI
  renderContainers();
  renderLog();
  
  // Show confirmation popup
  showDisposalModal(item, container, timestamp);
}

// ============================================
// MODALS
// ============================================

function showDisposalModal(item, container, timestamp) {
  const modal = document.getElementById("disposal-modal");
  
  document.getElementById("popup-item").textContent = item.name;
  
  const typeValue = document.getElementById("popup-type");
  typeValue.textContent = item.dangerous ? "⚠ DANGEROUS" : "✓ SAFE";
  typeValue.className = `detail-value ${item.dangerous ? "danger" : "safe"}`;
  
  document.getElementById("popup-container").textContent = `${container.id} (${container.name})`;
  document.getElementById("popup-time").textContent = timestamp;
  
  modal.classList.add("active");
}

function closeDisposalModal() {
  document.getElementById("disposal-modal").classList.remove("active");
}

function showErrorModal(message) {
  document.getElementById("error-message").textContent = message;
  document.getElementById("error-modal").classList.add("active");
}

function closeErrorModal() {
  document.getElementById("error-modal").classList.remove("active");
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
  
  // Re-render
  renderContainers();
  renderLog();
  
  // Show toast
  showToast("SIMULATOR_RESET");
}

// Toast notification (reuse from main.js if available)
function showToast(message) {
  // Check if showToast exists from main.js
  if (window.showToast && window.showToast !== showToast) {
    window.showToast(message);
    return;
  }
  
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
