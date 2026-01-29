import React, { Suspense, useRef } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, useGLTF, Stage, ContactShadows, Html, PerspectiveCamera } from '@react-three/drei';

const LabUnit = () => {
    // Explicit root-relative path for public assets in Vite
    const { scene } = useGLTF('/model.glb');
    const group = useRef();

    useFrame((state) => {
        if (group.current) {
            group.current.rotation.y += 0.005;
        }
    });

    return <primitive ref={group} object={scene} scale={0.5} position={[0, -0.8, 0]} />;
};

const LuxuryLoader = () => (
    <Html center>
        <div className="glass-v3" style={{ padding: '2rem', border: '1px solid var(--border-ambre)', textAlign: 'center', minWidth: '220px' }}>
            <div className="mono-tag" style={{ animation: 'pulse 1.5s infinite', color: '#fff' }}>[ PROTOCOL_LINKING ]</div>
            <div style={{ marginTop: '1.5rem', height: '2px', background: 'rgba(219, 131, 92, 0.1)', overflow: 'hidden' }}>
                <div style={{ width: '100%', height: '100%', background: 'var(--accent-ambre)', boxShadow: '0 0 15px var(--accent-ambre)', animation: 'shimmer 2s infinite linear' }} />
            </div>
        </div>
        <style>{`
            @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.4; } }
            @keyframes shimmer { 0% { transform: translateX(-100%); } 100% { transform: translateX(100%); } }
        `}</style>
    </Html>
);

const ModelView = () => {
    return (
        <div style={{ width: '100%', height: '100%', position: 'relative' }}>
            <div className="mono-tag" style={{ position: 'absolute', top: '1.5rem', left: '1.5rem', zIndex: 5, opacity: 0.4, pointerEvents: 'none' }}>
                [ TELEMETRY_CORE // LINK_ACTIVE ]
            </div>

            <Canvas dpr={[1, 2]} gl={{ antialias: true, alpha: true }}>
                <PerspectiveCamera makeDefault position={[0, 0, 5]} fov={33} />
                <ambientLight intensity={0.8} />
                <spotLight position={[10, 20, 10]} intensity={2.5} color="#DB835C" angle={0.2} penumbra={1} />

                <Suspense fallback={<LuxuryLoader />}>
                    <Stage environment="studio" intensity={0.5} contactShadow={{ opacity: 0.4, blur: 3 }}>
                        <LabUnit />
                    </Stage>
                    <ContactShadows position={[0, -1.8, 0]} opacity={0.5} scale={10} blur={3} far={10} color="#DB835C" />
                </Suspense>

                <OrbitControls enableZoom={false} enablePan={false} makeDefault />
            </Canvas>
        </div>
    );
};

export default ModelView;
// Preload for instant access
useGLTF.preload('/model.glb');
