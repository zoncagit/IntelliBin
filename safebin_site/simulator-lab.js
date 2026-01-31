/**
 * IntelliBin Laboratory Chemical Simulator
 * Chemical disposal system with incompatibility detection
 */

// ============================================
// CHEMICAL DATABASE
// ============================================

const CHEMICAL_CATEGORIES = {
  WEAK_ACID: "weak_acid",
  STRONG_ACID: "strong_acid",
  HALOGENATED_SOLVENT: "halogenated_solvent",
  NON_HALOGENATED_SOLVENT: "non_halogenated_solvent",
  BASE: "base",
  OXIDIZER: "oxidizer"
};

const CHEMICALS = [
  // Weak Acids
  { id: "acetic_acid", name: "Acetic Acid", category: CHEMICAL_CATEGORIES.WEAK_ACID, hazard: "low" },
  { id: "citric_acid", name: "Citric Acid", category: CHEMICAL_CATEGORIES.WEAK_ACID, hazard: "low" },
  { id: "formic_acid", name: "Formic Acid", category: CHEMICAL_CATEGORIES.WEAK_ACID, hazard: "medium" },
  { id: "phosphoric_acid_dilute", name: "Phosphoric Acid (dilute)", category: CHEMICAL_CATEGORIES.WEAK_ACID, hazard: "low" },
  { id: "carbonic_acid", name: "Carbonic Acid", category: CHEMICAL_CATEGORIES.WEAK_ACID, hazard: "low" },
  
  // Strong Acids
  { id: "nitric_acid", name: "Nitric Acid", category: CHEMICAL_CATEGORIES.STRONG_ACID, hazard: "high" },
  { id: "sulfuric_acid", name: "Sulfuric Acid", category: CHEMICAL_CATEGORIES.STRONG_ACID, hazard: "high" },
  { id: "hydrochloric_acid", name: "Hydrochloric Acid", category: CHEMICAL_CATEGORIES.STRONG_ACID, hazard: "high" },
  { id: "perchloric_acid", name: "Perchloric Acid", category: CHEMICAL_CATEGORIES.STRONG_ACID, hazard: "high" },
  { id: "phosphoric_acid_conc", name: "Phosphoric Acid (concentrated)", category: CHEMICAL_CATEGORIES.STRONG_ACID, hazard: "high" },
  
  // Halogenated Solvents
  { id: "chloroform", name: "Chloroform", category: CHEMICAL_CATEGORIES.HALOGENATED_SOLVENT, hazard: "high" },
  { id: "dichloromethane", name: "Dichloromethane (DCM)", category: CHEMICAL_CATEGORIES.HALOGENATED_SOLVENT, hazard: "medium" },
  { id: "carbon_tetrachloride", name: "Carbon Tetrachloride", category: CHEMICAL_CATEGORIES.HALOGENATED_SOLVENT, hazard: "high" },
  { id: "trichloroethylene", name: "Trichloroethylene", category: CHEMICAL_CATEGORIES.HALOGENATED_SOLVENT, hazard: "high" },
  { id: "tetrachloroethylene", name: "Tetrachloroethylene", category: CHEMICAL_CATEGORIES.HALOGENATED_SOLVENT, hazard: "high" },
  
  // Non-Halogenated Solvents
  { id: "acetone", name: "Acetone", category: CHEMICAL_CATEGORIES.NON_HALOGENATED_SOLVENT, hazard: "medium" },
  { id: "ethanol", name: "Ethanol", category: CHEMICAL_CATEGORIES.NON_HALOGENATED_SOLVENT, hazard: "low" },
  { id: "methanol", name: "Methanol", category: CHEMICAL_CATEGORIES.NON_HALOGENATED_SOLVENT, hazard: "medium" },
  { id: "diethyl_ether", name: "Diethyl Ether", category: CHEMICAL_CATEGORIES.NON_HALOGENATED_SOLVENT, hazard: "high" },
  { id: "toluene", name: "Toluene", category: CHEMICAL_CATEGORIES.NON_HALOGENATED_SOLVENT, hazard: "medium" },
  { id: "hexane", name: "Hexane", category: CHEMICAL_CATEGORIES.NON_HALOGENATED_SOLVENT, hazard: "medium" },
  { id: "xylene", name: "Xylene", category: CHEMICAL_CATEGORIES.NON_HALOGENATED_SOLVENT, hazard: "medium" },
  { id: "isopropanol", name: "Isopropanol", category: CHEMICAL_CATEGORIES.NON_HALOGENATED_SOLVENT, hazard: "low" },
  
  // Bases
  { id: "sodium_hydroxide", name: "Sodium Hydroxide (NaOH)", category: CHEMICAL_CATEGORIES.BASE, hazard: "high" },
  { id: "potassium_hydroxide", name: "Potassium Hydroxide (KOH)", category: CHEMICAL_CATEGORIES.BASE, hazard: "high" },
  { id: "ammonia", name: "Ammonia Solution", category: CHEMICAL_CATEGORIES.BASE, hazard: "medium" },
  { id: "sodium_carbonate", name: "Sodium Carbonate", category: CHEMICAL_CATEGORIES.BASE, hazard: "low" },
  { id: "calcium_hydroxide", name: "Calcium Hydroxide", category: CHEMICAL_CATEGORIES.BASE, hazard: "medium" },
  { id: "lithium_aluminum_hydride", name: "Lithium Aluminum Hydride (LAH)", category: CHEMICAL_CATEGORIES.BASE, hazard: "high" },
  { id: "sodium_metal", name: "Sodium Metal", category: CHEMICAL_CATEGORIES.BASE, hazard: "high" },
  
  // Oxidizers
  { id: "hydrogen_peroxide", name: "Hydrogen Peroxide (30%)", category: CHEMICAL_CATEGORIES.OXIDIZER, hazard: "high" },
  { id: "potassium_permanganate", name: "Potassium Permanganate", category: CHEMICAL_CATEGORIES.OXIDIZER, hazard: "high" },
  { id: "sodium_hypochlorite", name: "Sodium Hypochlorite (Bleach)", category: CHEMICAL_CATEGORIES.OXIDIZER, hazard: "medium" },
  { id: "nitric_acid_oxidizer", name: "Nitric Acid (as oxidizer)", category: CHEMICAL_CATEGORIES.OXIDIZER, hazard: "high" },
  { id: "chromic_acid", name: "Chromic Acid", category: CHEMICAL_CATEGORIES.OXIDIZER, hazard: "high" },
  { id: "perchloric_acid_oxidizer", name: "Perchloric Acid (as oxidizer)", category: CHEMICAL_CATEGORIES.OXIDIZER, hazard: "high" },
];

// ============================================
// INCOMPATIBILITY RULES
// ============================================

const INCOMPATIBILITY_RULES = [
  // Nitric acid + acetic acid -> violent oxidation
  {
    chemical1: ["nitric_acid"],
    chemical2: ["acetic_acid"],
    reaction: "Violent oxidation reaction",
    consequence: "Heat generation, toxic nitrogen oxides release",
    severity: "danger"
  },
  // Strong acids + weak organic acids with nitric acid
  {
    chemical1: ["nitric_acid"],
    chemical2: ["formic_acid", "citric_acid"],
    reaction: "Oxidation of organic acids",
    consequence: "Toxic gas evolution, heat generation",
    severity: "danger"
  },
  // Sodium hydroxide + aluminum (simulated by other reactive metals)
  {
    chemical1: ["sodium_hydroxide", "potassium_hydroxide"],
    chemical2: ["lithium_aluminum_hydride"],
    reaction: "Hydrogen gas generation",
    consequence: "Explosion risk from hydrogen accumulation",
    severity: "danger"
  },
  // Hydrogen peroxide + potassium permanganate
  {
    chemical1: ["hydrogen_peroxide"],
    chemical2: ["potassium_permanganate"],
    reaction: "Explosive decomposition",
    consequence: "Fire or explosion, rapid oxygen release",
    severity: "danger"
  },
  // Acetone + hydrogen peroxide
  {
    chemical1: ["acetone"],
    chemical2: ["hydrogen_peroxide"],
    reaction: "Organic peroxide formation",
    consequence: "Extremely explosive acetone peroxide (TATP) risk",
    severity: "danger"
  },
  // Chloroform + acetone (with base)
  {
    chemical1: ["chloroform"],
    chemical2: ["acetone"],
    reaction: "Phosgene gas formation (with base contamination)",
    consequence: "Highly toxic phosgene gas release",
    severity: "danger"
  },
  // Chloroform + bases
  {
    chemical1: ["chloroform", "carbon_tetrachloride"],
    chemical2: ["sodium_hydroxide", "potassium_hydroxide", "ammonia"],
    reaction: "Haloform reaction / Phosgene formation",
    consequence: "Toxic gas generation, potential explosion",
    severity: "danger"
  },
  // Bleach + ammonia
  {
    chemical1: ["sodium_hypochlorite"],
    chemical2: ["ammonia"],
    reaction: "Chloramine gas formation",
    consequence: "Highly toxic chloramine gas release",
    severity: "danger"
  },
  // Bleach + acids
  {
    chemical1: ["sodium_hypochlorite"],
    chemical2: ["hydrochloric_acid", "sulfuric_acid", "nitric_acid", "acetic_acid"],
    reaction: "Chlorine gas liberation",
    consequence: "Toxic chlorine gas release",
    severity: "danger"
  },
  // Sodium metal + lithium aluminum hydride
  {
    chemical1: ["sodium_metal"],
    chemical2: ["lithium_aluminum_hydride"],
    reaction: "Violent reaction with moisture",
    consequence: "Fire or explosion on moisture exposure",
    severity: "danger"
  },
  // Sodium/potassium metal + water/alcohols
  {
    chemical1: ["sodium_metal"],
    chemical2: ["ethanol", "methanol", "isopropanol"],
    reaction: "Violent hydrogen evolution",
    consequence: "Fire and explosion risk",
    severity: "danger"
  },
  // Ether + oxidizers
  {
    chemical1: ["diethyl_ether"],
    chemical2: ["hydrogen_peroxide", "potassium_permanganate", "chromic_acid"],
    reaction: "Peroxide formation / Fire",
    consequence: "Explosive peroxide crystals, spontaneous ignition",
    severity: "danger"
  },
  // Strong acids + bases (neutralization heat)
  {
    chemical1: ["sulfuric_acid", "hydrochloric_acid", "nitric_acid"],
    chemical2: ["sodium_hydroxide", "potassium_hydroxide"],
    reaction: "Violent exothermic neutralization",
    consequence: "Splashing, boiling, heat release",
    severity: "warning"
  },
  // Oxidizers + flammable solvents
  {
    chemical1: ["hydrogen_peroxide", "potassium_permanganate", "chromic_acid"],
    chemical2: ["ethanol", "methanol", "toluene", "hexane", "xylene"],
    reaction: "Oxidation / Fire risk",
    consequence: "Spontaneous ignition possible",
    severity: "danger"
  },
  // Perchloric acid + organic materials
  {
    chemical1: ["perchloric_acid", "perchloric_acid_oxidizer"],
    chemical2: ["acetone", "ethanol", "methanol", "diethyl_ether", "toluene"],
    reaction: "Explosive reaction",
    consequence: "Violent explosion risk with organics",
    severity: "danger"
  },
  // Chromic acid + organics
  {
    chemical1: ["chromic_acid"],
    chemical2: ["acetone", "ethanol", "methanol", "isopropanol"],
    reaction: "Violent oxidation",
    consequence: "Fire, toxic chromium compounds",
    severity: "danger"
  }
];

// ============================================
// CONTAINERS
// ============================================

const CONTAINERS = {
  weak_acid: {
    id: "ACID-W01",
    name: "Weak Acids",
    category: CHEMICAL_CATEGORIES.WEAK_ACID,
    capacity: 2000,
    current_fill: 0,
    contents: [],
    color: "#F59E0B",
    icon: "WA"
  },
  strong_acid: {
    id: "ACID-S01",
    name: "Strong Acids",
    category: CHEMICAL_CATEGORIES.STRONG_ACID,
    capacity: 1500,
    current_fill: 0,
    contents: [],
    color: "#EF4444",
    icon: "SA"
  },
  halogenated_solvent: {
    id: "SOLV-H01",
    name: "Halogenated Solvents",
    category: CHEMICAL_CATEGORIES.HALOGENATED_SOLVENT,
    capacity: 2000,
    current_fill: 0,
    contents: [],
    color: "#8B5CF6",
    icon: "HS"
  },
  non_halogenated_solvent: {
    id: "SOLV-N01",
    name: "Non-Halogenated Solvents",
    category: CHEMICAL_CATEGORIES.NON_HALOGENATED_SOLVENT,
    capacity: 2500,
    current_fill: 0,
    contents: [],
    color: "#3B82F6",
    icon: "NS"
  },
  base: {
    id: "BASE-01",
    name: "Bases",
    category: CHEMICAL_CATEGORIES.BASE,
    capacity: 2000,
    current_fill: 0,
    contents: [],
    color: "#10B981",
    icon: "BA"
  },
  oxidizer: {
    id: "OXID-01",
    name: "Oxidizers",
    category: CHEMICAL_CATEGORIES.OXIDIZER,
    capacity: 1000,
    current_fill: 0,
    contents: [],
    color: "#F97316",
    icon: "OX"
  }
};

// ============================================
// STATE
// ============================================

let disposalLog = [];
let pendingDisposal = null;

// DOM Elements
let elements = {};

// ============================================
// INITIALIZATION
// ============================================

document.addEventListener("DOMContentLoaded", () => {
  cacheElements();
  initializeDropdown();
  renderContainers();
  renderLog();
  setupEventListeners();
  updateChemicalInfo();
});

function cacheElements() {
  elements = {
    chemicalSelect: document.getElementById("chemical-select"),
    quantitySelect: document.getElementById("quantity-select"),
    disposeBtn: document.getElementById("dispose-btn"),
    
    infoCategory: document.getElementById("info-category"),
    infoHazard: document.getElementById("info-hazard"),
    infoContainer: document.getElementById("info-container"),
    
    safetyDot: document.getElementById("safety-dot"),
    safetyTag: document.getElementById("safety-tag"),
    safetyDisplay: document.getElementById("safety-display"),
    
    chemicalContainers: document.getElementById("chemical-containers"),
    disposalLog: document.getElementById("disposal-log"),
    logCount: document.getElementById("log-count"),
    
    disposalModal: document.getElementById("disposal-modal"),
    dangerModal: document.getElementById("danger-modal"),
    errorModal: document.getElementById("error-modal")
  };
}

function initializeDropdown() {
  const select = elements.chemicalSelect;
  select.innerHTML = "";
  
  // Group chemicals by category
  const grouped = {};
  CHEMICALS.forEach(chem => {
    if (!grouped[chem.category]) {
      grouped[chem.category] = [];
    }
    grouped[chem.category].push(chem);
  });
  
  // Create optgroups
  const categoryNames = {
    [CHEMICAL_CATEGORIES.WEAK_ACID]: "Weak Acids",
    [CHEMICAL_CATEGORIES.STRONG_ACID]: "Strong Acids",
    [CHEMICAL_CATEGORIES.HALOGENATED_SOLVENT]: "Halogenated Solvents",
    [CHEMICAL_CATEGORIES.NON_HALOGENATED_SOLVENT]: "Non-Halogenated Solvents",
    [CHEMICAL_CATEGORIES.BASE]: "Bases",
    [CHEMICAL_CATEGORIES.OXIDIZER]: "Oxidizers"
  };
  
  Object.entries(grouped).forEach(([category, chemicals]) => {
    const optgroup = document.createElement("optgroup");
    optgroup.label = categoryNames[category];
    
    chemicals.forEach(chem => {
      const option = document.createElement("option");
      option.value = chem.id;
      option.textContent = chem.name;
      optgroup.appendChild(option);
    });
    
    select.appendChild(optgroup);
  });
}

function setupEventListeners() {
  // Chemical selection change
  elements.chemicalSelect.addEventListener("change", updateChemicalInfo);
  
  // Dispose button
  elements.disposeBtn.addEventListener("click", handleDispose);
  
  // Modal close buttons
  document.getElementById("close-disposal-modal").addEventListener("click", closeDisposalModal);
  document.getElementById("popup-close-btn").addEventListener("click", closeDisposalModal);
  document.getElementById("close-danger-modal").addEventListener("click", closeDangerModal);
  document.getElementById("danger-cancel-btn").addEventListener("click", closeDangerModal);
  document.getElementById("danger-force-btn").addEventListener("click", forceDisposal);
  document.getElementById("close-error-modal").addEventListener("click", closeErrorModal);
  document.getElementById("error-close-btn").addEventListener("click", closeErrorModal);
  
  // Close modals on overlay click
  elements.disposalModal.addEventListener("click", (e) => {
    if (e.target.id === "disposal-modal") closeDisposalModal();
  });
  elements.dangerModal.addEventListener("click", (e) => {
    if (e.target.id === "danger-modal") closeDangerModal();
  });
  elements.errorModal.addEventListener("click", (e) => {
    if (e.target.id === "error-modal") closeErrorModal();
  });
}

// ============================================
// CHEMICAL INFO DISPLAY
// ============================================

function updateChemicalInfo() {
  const chemicalId = elements.chemicalSelect.value;
  const chemical = CHEMICALS.find(c => c.id === chemicalId);
  
  if (!chemical) return;
  
  const categoryNames = {
    [CHEMICAL_CATEGORIES.WEAK_ACID]: "Weak Acid",
    [CHEMICAL_CATEGORIES.STRONG_ACID]: "Strong Acid",
    [CHEMICAL_CATEGORIES.HALOGENATED_SOLVENT]: "Halogenated Solvent",
    [CHEMICAL_CATEGORIES.NON_HALOGENATED_SOLVENT]: "Non-Halogenated Solvent",
    [CHEMICAL_CATEGORIES.BASE]: "Base",
    [CHEMICAL_CATEGORIES.OXIDIZER]: "Oxidizer"
  };
  
  const container = CONTAINERS[chemical.category];
  
  elements.infoCategory.textContent = categoryNames[chemical.category];
  elements.infoCategory.className = `info-value category-${chemical.category}`;
  
  elements.infoHazard.textContent = chemical.hazard.toUpperCase();
  elements.infoHazard.className = `info-value hazard-${chemical.hazard}`;
  
  elements.infoContainer.textContent = container ? container.id : "N/A";
  
  // Check for potential hazards
  checkPotentialHazards(chemical);
}

function checkPotentialHazards(newChemical) {
  const container = CONTAINERS[newChemical.category];
  if (!container || container.contents.length === 0) {
    showSafeStatus();
    return;
  }
  
  const hazards = findIncompatibilities(newChemical.id, container.contents);
  
  if (hazards.length > 0) {
    showWarningStatus(hazards);
  } else {
    showSafeStatus();
  }
}

function showSafeStatus() {
  elements.safetyDot.className = "status-dot-green";
  elements.safetyTag.textContent = "[ SYSTEM_CLEAR ]";
  elements.safetyDisplay.innerHTML = `
    <div class="safety-indicator safe">
      <div class="indicator-icon">OK</div>
      <div class="indicator-text">No hazardous combinations detected</div>
    </div>
  `;
}

function showWarningStatus(hazards) {
  const severity = hazards.some(h => h.severity === "danger") ? "danger" : "warning";
  
  elements.safetyDot.className = severity === "danger" ? "status-dot-danger" : "status-dot-warning";
  elements.safetyTag.textContent = severity === "danger" ? "[ DANGER ]" : "[ CAUTION ]";
  
  elements.safetyDisplay.innerHTML = hazards.map(h => `
    <div class="safety-indicator ${h.severity}">
      <div class="indicator-icon">${severity === "danger" ? "!" : "?"}</div>
      <div class="indicator-text">
        <strong>${h.reaction}</strong><br>
        ${h.consequence}
      </div>
    </div>
  `).join("");
}

// ============================================
// INCOMPATIBILITY CHECKING
// ============================================

function findIncompatibilities(newChemicalId, containerContents) {
  const hazards = [];
  
  // Get all chemical IDs in container
  const existingChemicalIds = containerContents.map(c => c.chemicalId);
  
  // Check each rule
  INCOMPATIBILITY_RULES.forEach(rule => {
    const newMatchesFirst = rule.chemical1.includes(newChemicalId);
    const newMatchesSecond = rule.chemical2.includes(newChemicalId);
    
    if (newMatchesFirst) {
      // Check if any existing chemical matches second group
      const conflicts = existingChemicalIds.filter(id => rule.chemical2.includes(id));
      if (conflicts.length > 0) {
        hazards.push({
          ...rule,
          conflictingChemicals: conflicts.map(id => CHEMICALS.find(c => c.id === id)?.name || id)
        });
      }
    }
    
    if (newMatchesSecond) {
      // Check if any existing chemical matches first group
      const conflicts = existingChemicalIds.filter(id => rule.chemical1.includes(id));
      if (conflicts.length > 0) {
        hazards.push({
          ...rule,
          conflictingChemicals: conflicts.map(id => CHEMICALS.find(c => c.id === id)?.name || id)
        });
      }
    }
  });
  
  return hazards;
}

// ============================================
// DISPOSAL LOGIC
// ============================================

function handleDispose() {
  const chemicalId = elements.chemicalSelect.value;
  const quantity = parseInt(elements.quantitySelect.value);
  const chemical = CHEMICALS.find(c => c.id === chemicalId);
  
  if (!chemical) return;
  
  const container = CONTAINERS[chemical.category];
  
  if (!container) {
    showErrorModal("No container available for this chemical category");
    return;
  }
  
  // Check capacity
  if (container.current_fill + quantity > container.capacity) {
    showErrorModal(`Container ${container.id} is full! (${container.current_fill}/${container.capacity} mL)`);
    return;
  }
  
  // Check for incompatibilities
  const hazards = findIncompatibilities(chemicalId, container.contents);
  
  if (hazards.length > 0 && hazards.some(h => h.severity === "danger")) {
    // Show danger modal
    pendingDisposal = { chemical, quantity, container, hazards };
    showDangerModal(chemical, hazards);
    return;
  }
  
  // Safe to dispose
  executeDisposal(chemical, quantity, container);
}

function executeDisposal(chemical, quantity, container) {
  // Update container
  container.current_fill += quantity;
  container.contents.push({
    chemicalId: chemical.id,
    name: chemical.name,
    quantity: quantity,
    timestamp: new Date().toISOString()
  });
  
  // Log entry
  const timestamp = new Date().toLocaleTimeString("en-US", {
    hour12: false,
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit"
  });
  
  const logEntry = {
    time: timestamp,
    chemical: chemical.name,
    chemicalId: chemical.id,
    category: chemical.category,
    quantity: quantity,
    container: container.id,
    hazard: chemical.hazard
  };
  
  disposalLog.unshift(logEntry);
  
  // Update UI
  renderContainers();
  renderLog();
  updateChemicalInfo();
  
  // Show confirmation
  showDisposalModal(chemical, container, quantity, timestamp);
}

function forceDisposal() {
  if (!pendingDisposal) return;
  
  const { chemical, quantity, container } = pendingDisposal;
  
  closeDangerModal();
  executeDisposal(chemical, quantity, container);
  
  pendingDisposal = null;
}

// ============================================
// RENDERING
// ============================================

function renderContainers() {
  const containerDiv = elements.chemicalContainers;
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
  widget.className = `chemical-widget ${isFull ? "full" : ""} ${isWarning ? "warning" : ""}`;
  
  // Get recent contents (last 3)
  const recentContents = container.contents.slice(-3).map(c => c.name).join(", ") || "Empty";
  
  widget.innerHTML = `
    <div class="chemical-icon" style="background: ${container.color}">
      ${container.icon}
    </div>
    <div class="chemical-info">
      <div class="chemical-header">
        <span class="chemical-name">${container.name}</span>
        <span class="chemical-status ${isFull ? "full" : isWarning ? "warning" : ""}"></span>
      </div>
      <div class="chemical-id">${container.id}</div>
      <div class="chemical-bar">
        <div class="chemical-bar-fill ${isFull ? "full" : isWarning ? "high" : ""}" 
             style="width: ${Math.min(fillPercent, 100)}%; background: ${container.color}"></div>
      </div>
      <div class="chemical-fill-text">${container.current_fill}/${container.capacity} mL</div>
      <div class="chemical-contents" title="${recentContents}">
        ${container.contents.length > 0 ? `Contains: ${recentContents.substring(0, 30)}${recentContents.length > 30 ? '...' : ''}` : 'Empty'}
      </div>
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
        <span class="log-comment">// Select a chemical and click DISPOSE</span>
      </div>
    `;
    return;
  }
  
  const categoryShort = {
    [CHEMICAL_CATEGORIES.WEAK_ACID]: "WA",
    [CHEMICAL_CATEGORIES.STRONG_ACID]: "SA",
    [CHEMICAL_CATEGORIES.HALOGENATED_SOLVENT]: "HS",
    [CHEMICAL_CATEGORIES.NON_HALOGENATED_SOLVENT]: "NS",
    [CHEMICAL_CATEGORIES.BASE]: "BA",
    [CHEMICAL_CATEGORIES.OXIDIZER]: "OX"
  };
  
  logContainer.innerHTML = disposalLog.slice(0, 20).map(entry => `
    <div class="log-entry">
      <span class="log-time">[${entry.time}]</span>
      <span class="log-category cat-${entry.category}">${categoryShort[entry.category]}</span>
      <span class="log-chemical">${entry.chemical}</span>
      <span class="log-quantity">${entry.quantity}mL</span>
      <span class="log-container">${entry.container}</span>
    </div>
  `).join("");
}

// ============================================
// MODALS
// ============================================

function showDisposalModal(chemical, container, quantity, timestamp) {
  const categoryNames = {
    [CHEMICAL_CATEGORIES.WEAK_ACID]: "Weak Acid",
    [CHEMICAL_CATEGORIES.STRONG_ACID]: "Strong Acid",
    [CHEMICAL_CATEGORIES.HALOGENATED_SOLVENT]: "Halogenated Solvent",
    [CHEMICAL_CATEGORIES.NON_HALOGENATED_SOLVENT]: "Non-Halogenated Solvent",
    [CHEMICAL_CATEGORIES.BASE]: "Base",
    [CHEMICAL_CATEGORIES.OXIDIZER]: "Oxidizer"
  };
  
  document.getElementById("popup-chemical").textContent = chemical.name;
  document.getElementById("popup-category").textContent = categoryNames[chemical.category];
  document.getElementById("popup-quantity").textContent = `${quantity} mL`;
  document.getElementById("popup-container").textContent = `${container.id} (${container.name})`;
  document.getElementById("popup-time").textContent = timestamp;
  
  elements.disposalModal.classList.add("active");
}

function closeDisposalModal() {
  elements.disposalModal.classList.remove("active");
}

function showDangerModal(chemical, hazards) {
  const primaryHazard = hazards[0];
  
  document.getElementById("danger-chemical").textContent = `Attempting to dispose: ${chemical.name}`;
  document.getElementById("danger-reaction").textContent = primaryHazard.reaction;
  document.getElementById("danger-consequence").textContent = primaryHazard.consequence;
  
  const existingDiv = document.getElementById("existing-chemicals");
  existingDiv.innerHTML = hazards.flatMap(h => h.conflictingChemicals || [])
    .filter((v, i, a) => a.indexOf(v) === i)
    .map(name => `<span class="existing-chem">${name}</span>`)
    .join("");
  
  elements.dangerModal.classList.add("active");
}

function closeDangerModal() {
  elements.dangerModal.classList.remove("active");
  pendingDisposal = null;
}

function showErrorModal(message) {
  document.getElementById("error-message").textContent = message;
  elements.errorModal.classList.add("active");
}

function closeErrorModal() {
  elements.errorModal.classList.remove("active");
}

// ============================================
// RESET
// ============================================

function resetSimulator() {
  // Reset containers
  Object.values(CONTAINERS).forEach(container => {
    container.current_fill = 0;
    container.contents = [];
  });
  
  // Clear log
  disposalLog = [];
  
  // Re-render
  renderContainers();
  renderLog();
  updateChemicalInfo();
  
  // Show toast
  showToast("LAB_SIMULATOR_RESET");
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
    color: #10B981;
    padding: 1rem 2rem;
    border: 1px solid rgba(16, 185, 129, 0.4);
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
