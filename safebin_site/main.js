import * as THREE from 'three';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

// Register Plugin
gsap.registerPlugin(ScrollTrigger);

// --- SCENE SETUP ---
const scene = new THREE.Scene();
scene.background = null; // Let CSS grid show through

// Camera - positioned to see the FULL bin
const camera = new THREE.PerspectiveCamera(35, window.innerWidth / window.innerHeight, 0.1, 100);
camera.position.set(0, 0, 8); // Pulled back to see full model
camera.lookAt(0, 0, 0);

const renderer = new THREE.WebGLRenderer({
    antialias: true,
    alpha: true,
    powerPreference: "high-performance",
    precision: "mediump"
});
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1.5)); // Capped at 1.5 for performance
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.2;
document.getElementById('canvas-container').appendChild(renderer.domElement);

// --- LIGHTING ---
const ambientLight = new THREE.AmbientLight(0xffffff, 1.2);
scene.add(ambientLight);

const keyLight = new THREE.DirectionalLight(0xffffff, 2.5);
keyLight.position.set(5, 5, 5);
scene.add(keyLight);

const fillLight = new THREE.DirectionalLight(0xddeeff, 1.0);
fillLight.position.set(-5, 0, 5);
scene.add(fillLight);

const backLight = new THREE.DirectionalLight(0xffffff, 1.5);
backLight.position.set(0, 5, -5);
scene.add(backLight);

// --- MODEL LOADING ---
const loader = new GLTFLoader();
let model;

// Placeholder Geometry
const geometry = new THREE.BoxGeometry(1, 1.5, 1);
const material = new THREE.MeshStandardMaterial({
    color: 0xcccccc,
    roughness: 0.3,
    metalness: 0.7
});
const placeholderMesh = new THREE.Mesh(geometry, material);

loader.load(
    '/model.glb',
    (gltf) => {
        model = gltf.scene;
        scene.add(model);

        // Auto-center
        const box = new THREE.Box3().setFromObject(model);
        const center = box.getCenter(new THREE.Vector3());
        const size = box.getSize(new THREE.Vector3());

        model.position.sub(center);

        // Scale to fit nicely - normalize based on largest dimension
        const maxDim = Math.max(size.x, size.y, size.z);
        const scale = 2.5 / maxDim; // Target size of 2.5 units
        model.scale.set(scale, scale, scale);

        // Position below the title
        model.position.y = -1.2;

        // Rotate to face the FRONT initially
        model.rotation.y = Math.PI; // 180 degrees to show front

        initInteractions();
        initScrollAnimations();
    },
    undefined,
    (error) => {
        console.error('Model load error:', error);
        scene.add(placeholderMesh);
        model = placeholderMesh;
        model.position.y = -1.2;
        initInteractions();
        initScrollAnimations();
    }
);

// --- MOUSE DRAG ROTATION ---
let isDragging = false;
let previousMousePosition = { x: 0, y: 0 };

function initInteractions() {
    const canvas = renderer.domElement;

    canvas.addEventListener('mousedown', (e) => {
        isDragging = true;
        previousMousePosition = { x: e.clientX, y: e.clientY };
    });

    canvas.addEventListener('mousemove', (e) => {
        if (!isDragging || !model) return;

        const deltaX = e.clientX - previousMousePosition.x;
        const deltaY = e.clientY - previousMousePosition.y;

        // Rotate model based on mouse movement
        model.rotation.y += deltaX * 0.01;
        model.rotation.x += deltaY * 0.01;

        previousMousePosition = { x: e.clientX, y: e.clientY };
    });

    canvas.addEventListener('mouseup', () => {
        isDragging = false;
    });

    canvas.addEventListener('mouseleave', () => {
        isDragging = false;
    });
}

// --- MOUSE PARALLAX (PEPS) ---
function initParallax() {
    document.addEventListener('mousemove', (e) => {
        const x = (e.clientX - window.innerWidth / 2) / 50;
        const y = (e.clientY - window.innerHeight / 2) / 50;

        // Move floating cards
        const floatingCards = document.querySelector('.floating-cards');
        if (floatingCards) {
            gsap.to(floatingCards, {
                x: x * 1.5,
                y: y * 1.5,
                duration: 1,
                ease: "power2.out"
            });
        }

        // Move hero content slightly for depth
        const heroContent = document.querySelector('.hero-content');
        if (heroContent) {
            gsap.to(heroContent, {
                x: x * -0.5,
                y: y * -0.5,
                duration: 1,
                ease: "power2.out"
            });
        }
    });
}

// --- GLASS CARD SPOTLIGHT EFFECT ---
function initCardEffects() {
    // Select all types of glass cards
    const cardSelectors = ['.glass-card', '.stat-glass-card', '.service-glass-card', '.hud-card'];
    const cards = document.querySelectorAll(cardSelectors.join(','));

    cards.forEach(card => {
        const spotlight = card.querySelector('.card-spotlight');
        if (!spotlight) return;

        card.addEventListener('mousemove', (e) => {
            const rect = card.getBoundingClientRect();
            const mouseX = e.clientX - rect.left;
            const mouseY = e.clientY - rect.top;

            spotlight.style.left = `${mouseX}px`;
            spotlight.style.top = `${mouseY}px`;
        });
    });
}

// --- SCROLL ANIMATION (REFACTORED: SECTION-BASED) ---
// --- SCROLL ANIMATION (THE PERFECT PATH: MASTER TIMELINE) ---
function initScrollAnimations() {
    if (!model) return;

    // THE MASTER TRAJECTORY (Unified Control)
    const tl = gsap.timeline({
        scrollTrigger: {
            trigger: "main",
            start: "top top",
            endTrigger: ".solution-section", // FIX: Lock end to the Solution section
            end: "bottom bottom",
            scrub: 1, // Reduced for better responsiveness
        }
    });

    // PHASE 1: GLIDE TO RIGHT + SPIN (Start -> Problem)
    tl.to(model.position, {
        x: 2.5,
        y: 0,
        ease: "power2.inOut",
        duration: 20
    }, 0);

    tl.to(model.rotation, {
        y: "+=" + (Math.PI * 2), // Spin only during move
        ease: "power2.inOut",
        duration: 20
    }, 0);

    // PHASE 2: STASIS RIGHT (During Problem)
    tl.to(model.position, {
        x: 2.5,
        y: 0,
        duration: 20
    }, 20);

    // PHASE 3: CROSS TO LEFT + SPIN (Problem -> Costs)
    tl.to(model.position, {
        x: -2.5,
        y: -0.5,
        ease: "power2.inOut",
        duration: 20
    }, 40);

    tl.to(model.rotation, {
        y: "+=" + (Math.PI * 2), // Spin only during move
        ease: "power2.inOut",
        duration: 20
    }, 40);

    // PHASE 4: STASIS LEFT (During High Costs)
    tl.to(model.position, {
        x: -2.5,
        y: -0.5,
        duration: 20
    }, 60);

    // PHASE 5: RETURN TO CENTER + SPIN (Costs -> Solution)
    tl.to(model.position, {
        x: 0,
        y: 0,
        ease: "power2.inOut",
        duration: 20
    }, 80);

    tl.to(model.rotation, {
        y: "+=" + (Math.PI * 2), // Spin only during move
        ease: "power2.inOut",
        duration: 20
    }, 80);

    // --- SCALE CONTROL ---
    tl.to(model.scale, {
        x: model.scale.x * 0.8,
        y: model.scale.y * 0.8,
        z: model.scale.z * 0.8,
        ease: "power2.inOut",
        duration: 50
    }, 0);

    tl.to(model.scale, {
        x: model.scale.x * 1,
        y: model.scale.y * 1,
        z: model.scale.z * 1,
        ease: "power2.out",
        duration: 50
    }, 50);

    // 6️⃣ EXIT STRATEGY: Anchor to Solution
    // Moves the entire canvas container up as the user scrolls into the next section
    gsap.to("#canvas-container", {
        y: "-100vh",
        ease: "none",
        scrollTrigger: {
            trigger: ".how-section",
            start: "top bottom", // When the section after solution enters
            end: "top top",      // When it occupies the whole screen
            scrub: true
        }
    });
}

// --- TOAST SYSTEM ---
function showToast(message) {
    const toast = document.createElement('div');
    toast.style.cssText = `
        position: fixed;
        bottom: 2rem;
        left: 50%;
        transform: translateX(-50%);
        background: rgba(10, 10, 10, 0.9);
        color: var(--accent-orange);
        padding: 1rem 2rem;
        border: 1px solid var(--accent-glow);
        border-radius: 4px;
        font-family: var(--font-mono);
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
        toast.style.opacity = '1';
        toast.style.transform = 'translateX(-50%) translateY(-10px)';
    }, 10);

    setTimeout(() => {
        toast.style.opacity = '0';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// --- MODAL CONTROLLER ---
function initModal() {
    const modal = document.getElementById('reservation-modal');
    if (!modal) return;

    const openBtns = document.querySelectorAll('.header-cta, .reserve-btn, .cta-button, .reserve-btn-glitch');
    const closeBtn = document.getElementById('close-modal');
    const toStep2 = document.getElementById('to-step-2');
    const step1 = document.getElementById('modal-step-1');
    const step2 = document.getElementById('modal-step-2');
    const form = modal.querySelector('.reservation-form');

    openBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            modal.classList.add('active');
            showToast('PROTOCOL_INITIATED');
        });
    });

    if (closeBtn) {
        closeBtn.addEventListener('click', () => {
            modal.classList.remove('active');
            setTimeout(() => {
                step1.classList.remove('hidden');
                step2.classList.add('hidden');
            }, 500);
        });
    }

    if (toStep2) {
        toStep2.addEventListener('click', () => {
            step1.classList.add('hidden');
            step2.classList.remove('hidden');
            showToast('AUTH_SEQUENCE_READY');
        });
    }

    if (form) {
        form.addEventListener('submit', (e) => {
            e.preventDefault();
            showToast('AUTHORIZING...');
            setTimeout(() => {
                showToast('RESERVATION_SUCCESS');
                modal.classList.remove('active');
                setTimeout(() => {
                    step1.classList.remove('hidden');
                    step2.classList.add('hidden');
                }, 500);
            }, 2000);
        });
    }
}

// --- HEADER SCROLL EFFECT ---
function initHeader() {
    const header = document.querySelector('.tactical-header');
    if (!header) return;

    window.addEventListener('scroll', () => {
        if (window.scrollY > 50) {
            header.classList.add('header-scrolled');
        } else {
            header.classList.remove('header-scrolled');
        }
    });
}

// --- RESIZE ---
function onWindowResize() {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
}
window.addEventListener('resize', onWindowResize);

// --- LIVE UTC CLOCK ---
function initClock() {
    const clockElement = document.querySelector('.utc-clock');
    if (!clockElement) return;

    setInterval(() => {
        const now = new Date();
        const utcStr = now.toISOString().split('T')[1].split('.')[0];
        clockElement.textContent = `UTC ${utcStr}`;
    }, 1000);
}

// --- RENDER LOOP ---
// Use GSAP Ticker for smoother frame synchronization
gsap.ticker.add(() => {
    renderer.render(scene, camera);
});

// Remove manual animate loop
// function animate() {
//     requestAnimationFrame(animate);
//     renderer.render(scene, camera);
// }
// animate();

// --- INITIALIZE ALL ---
initCardEffects();
initParallax();
initClock();
initHeader();
initModal();

// Expose to global for onclick handlers
window.showToast = showToast;

// Global Smooth Scroll Behavior
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});
