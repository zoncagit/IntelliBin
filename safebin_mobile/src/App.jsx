import React, { useState, useEffect, Suspense } from 'react';
import {
    LayoutGrid, Plus, History, AlertTriangle, ShieldCheck,
    MapPin, Zap, Database, Download, ArrowUpRight,
    CheckCircle2, FlaskConical, Activity, Info, Bell, X, Cpu, Layout
} from 'lucide-react';
import { WasteProvider, useWaste } from './WasteContext';
import ModelView from './ModelView';
import './App.css';

// --- SOPHISTICATED TOAST (AURORA) ---
const Toast = ({ message, type, onClear }) => {
    useEffect(() => {
        const timer = setTimeout(onClear, 4000);
        return () => clearTimeout(timer);
    }, [onClear]);

    return (
        <div className="glass-v3 fade-in" style={{
            position: 'fixed', top: '2.5rem', left: '1.25rem', right: '1.25rem',
            padding: '1.4rem', display: 'flex', alignItems: 'center', gap: '15px',
            zIndex: 10000, border: `1px solid ${type === 'alert' ? '#FF3B30' : 'var(--border-ambre)'}`,
            background: 'rgba(10, 10, 12, 0.98)',
            borderRadius: '24px'
        }}>
            <div style={{ color: type === 'alert' ? '#FF3B30' : '#DB835C' }}><Bell size={24} /></div>
            <div style={{ flex: 1 }}>
                <div className="mono-tag" style={{ fontSize: '0.6rem', opacity: 0.5, marginBottom: '2px' }}>SYSTEM_ALERT</div>
                <div style={{ fontSize: '0.9rem', fontWeight: 800, color: '#fff' }}>{message}</div>
            </div>
            <X size={18} onClick={onClear} style={{ opacity: 0.3, cursor: 'pointer' }} />
        </div>
    );
};

// --- LUXURY SECTIONS ---

const Dashboard = () => {
    const { containers } = useWaste();
    return (
        <div className="fade-in">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '2rem' }}>
                <div>
                    <div className="live-badge" style={{ background: 'rgba(219, 131, 92, 0.15)' }}>
                        <div className="live-dot" /> LIVE_DATASTREAM
                    </div>
                    <h1 className="luxury-text" style={{ marginTop: '0.8rem' }}>DASHBOARD</h1>
                </div>
                <div className="glass-v3" style={{ width: '3.5rem', height: '3.5rem', display: 'flex', alignItems: 'center', justifyContent: 'center', borderRadius: '18px' }}>
                    <Activity color="#DB835C" size={24} />
                </div>
            </div>

            <div className="bento-grid">
                <div className="glass-v3 bento-item bento-wide" style={{ padding: '0', height: '23rem', overflow: 'hidden', borderRadius: '32px' }}>
                    <ModelView />
                </div>

                {containers.map((c, i) => (
                    <div key={c.id} className={`glass-v3 bento-item ${i === 1 ? 'bento-tall' : ''}`} style={{
                        padding: '1.8rem',
                        background: c.fill > 85 ? 'rgba(255, 59, 48, 0.05)' : '',
                        border: c.fill > 85 ? '1px solid rgba(255, 59, 48, 0.4)' : '',
                        borderRadius: '28px'
                    }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', width: '100%', marginBottom: '1.5rem' }}>
                            <span className="mono-tag" style={{ opacity: 0.4 }}>{c.id}</span>
                            <Cpu size={14} style={{ opacity: 0.2 }} />
                        </div>
                        <div style={{ flex: 1 }}>
                            <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '4px' }}>{c.type}</div>
                            <div style={{ fontSize: '2.6rem', fontWeight: 900 }}>{c.fill}%</div>
                        </div>
                        <div style={{ height: '6px', background: 'rgba(255,255,255,0.05)', borderRadius: '100px', overflow: 'hidden', marginTop: '1.2rem' }}>
                            <div style={{
                                width: `${c.fill}%`, height: '100%',
                                background: c.fill > 85 ? '#FF3B30' : 'var(--accent-ambre)',
                                boxShadow: c.fill > 85 ? '0 0 20px #FF3B30' : '0 0 15px var(--accent-ambre-glow)'
                            }} />
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

const Protocol = ({ onNotify }) => {
    const { addDisposal } = useWaste();
    const [formData, setFormData] = useState({ name: '', qty: '', conc: '' });
    const [result, setResult] = useState(null);

    const handleSubmit = (e) => {
        e.preventDefault();
        const isDanger = formData.name.toLowerCase().includes('cyanide');
        if (isDanger) {
            setResult({ status: 'DANGER', title: 'BLOCKING_CMD_INT', node: 'SECURED_VALVE', loc: 'ZONE_04_S' });
            onNotify('CRITICAL_THREAT_REJECTED', 'alert');
        } else {
            setResult({ status: 'SUCCESS', title: 'ROUTE_RESOLVED', node: 'ACID-001_P', loc: 'CORE_UNIT_01' });
            onNotify('ACCESS_GRANTED_PROTOCOL_READY', 'info');
        }
    };

    return (
        <div className="fade-in">
            <div className="live-badge" style={{ background: 'rgba(219, 131, 92, 0.15)' }}><div className="live-dot" /> DISPOSAL_ENGINE</div>
            <h1 className="luxury-text" style={{ marginTop: '0.8rem', marginBottom: '2.5rem' }}>PROTOCOL</h1>

            {!result ? (
                <form className="glass-v3" style={{ padding: '2.5rem', display: 'flex', flexDirection: 'column', gap: '2.5rem', borderRadius: '32px' }} onSubmit={handleSubmit}>
                    <div>
                        <label className="mono-tag" style={{ marginBottom: '1rem', display: 'block' }}>[ CHEMICAL_ENTITY ]</label>
                        <input type="text" className="premium-input" placeholder="e.g. SULPHURIC ACID" value={formData.name} onChange={e => setFormData({ ...formData, name: e.target.value })} required />
                    </div>
                    <div style={{ display: 'flex', gap: '1.2rem' }}>
                        <div style={{ flex: 1 }}>
                            <label className="mono-tag" style={{ marginBottom: '1rem', display: 'block' }}>[ VOLUME ]</label>
                            <input type="text" className="premium-input" placeholder="1000 mL" value={formData.qty} onChange={e => setFormData({ ...formData, qty: e.target.value })} required />
                        </div>
                        <div style={{ flex: 1 }}>
                            <label className="mono-tag" style={{ marginBottom: '1rem', display: 'block' }}>[ CONC_% ]</label>
                            <input type="text" className="premium-input" placeholder="37%" value={formData.conc} onChange={e => setFormData({ ...formData, conc: e.target.value })} required />
                        </div>
                    </div>
                    <button type="submit" className="aurora-btn" style={{ height: '4.8rem', fontSize: '1.2rem', fontWeight: 900 }}>EXECUTE_ROUTING</button>
                </form>
            ) : (
                <div className="glass-v3" style={{ padding: '3.5rem', textAlign: 'center', borderRadius: '40px' }}>
                    {result.status === 'DANGER' ? <AlertTriangle size={80} color="#FF3B30" style={{ marginBottom: '2rem', filter: 'drop-shadow(0 0 25px rgba(255, 59, 48, 0.5))' }} /> : <CheckCircle2 size={80} color="#DB835C" style={{ marginBottom: '2rem', filter: 'drop-shadow(0 0 25px rgba(219, 131, 92, 0.5))' }} />}
                    <div className="mono-tag" style={{ color: result.status === 'DANGER' ? '#FF3B30' : '#DB835C', fontSize: '1.2rem' }}>{result.title}</div>

                    <div className="glass-v3" style={{ padding: '2.5rem', margin: '2.5rem 0', borderRadius: '28px', background: 'rgba(255,255,255,0.03)' }}>
                        <div className="mono-tag" style={{ fontSize: '0.65rem', marginBottom: '8px', opacity: 0.5 }}>IDENTIFIED_DESTINATION</div>
                        <div style={{ fontSize: '3.8rem', fontWeight: 950 }}>{result.node}</div>
                        <div className="mono-tag" style={{ marginTop: '5px', opacity: 0.4 }}>[ {result.loc} ]</div>
                    </div>

                    <button onClick={() => { if (result.status !== 'DANGER') addDisposal({ chemical: formData.name, qty: formData.qty, container: result.node }); setResult(null); setFormData({ name: '', qty: '', conc: '' }); }} className="aurora-btn" style={{ width: '100%', height: '4.5rem' }}>
                        {result.status === 'DANGER' ? 'RESTART_PROTOCOL' : 'COMPLETE_SEQUENCE'}
                    </button>
                </div>
            )}
        </div>
    );
};

const Archives = () => {
    const { history } = useWaste();
    return (
        <div className="fade-in">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', marginBottom: '2.5rem' }}>
                <div>
                    <div className="live-badge" style={{ background: 'rgba(219, 131, 92, 0.15)' }}><div className="live-dot" /> SECURE_DATA_FEED</div>
                    <h1 className="luxury-text" style={{ marginTop: '0.8rem' }}>ARCHIVES</h1>
                </div>
                <button className="glass-v3" style={{ width: '4rem', height: '4rem', borderRadius: '20px', border: 'none', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    <Download size={24} color="#fff" />
                </button>
            </div>

            <div className="glass-v3" style={{ borderRadius: '35px', padding: '0.6rem' }}>
                {history.length > 0 ? history.map(item => (
                    <div key={item.id} style={{ padding: '2rem', borderBottom: '1px solid rgba(255,255,255,0.05)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <div>
                            <div style={{ fontSize: '1.2rem', fontWeight: 800, marginBottom: '5px' }}>{item.chemical.toUpperCase()}</div>
                            <div className="mono-tag" style={{ fontSize: '0.7rem', opacity: 0.5 }}>{item.qty} • {item.container}</div>
                        </div>
                        <div className="mono-tag" style={{ opacity: 0.3 }}>{item.time.split(',')[1]}</div>
                    </div>
                )) : (
                    <div style={{ padding: '6rem 2rem', textAlign: 'center', opacity: 0.2 }} className="mono-tag">NO_TELEMETRY_FOUND</div>
                )}
            </div>
        </div>
    );
};

// --- LUXURY HUB FRAME ---

function App() {
    const [activeTab, setActiveTab] = useState('dashboard');
    const [toast, setToast] = useState(null);

    useEffect(() => {
        console.log("SAFEBINHUB_V4_MOUNTED");
        // Ensure root visibility
        if (document.getElementById('root')) {
            document.getElementById('root').style.opacity = '1';
            document.getElementById('root').style.visibility = 'visible';
        }
    }, []);

    return (
        <WasteProvider>
            <div className="app-container">
                {/* CINEMATIC AURORA SYSTEM */}
                <div className="aurora-bg">
                    <div className="mesh-flow"></div>
                    <div className="hud-overlay"></div>
                </div>

                {toast && <Toast message={toast.message} type={toast.type} onClear={() => setToast(null)} />}

                <main className="main-viewport" style={{ zIndex: 10, position: 'relative', padding: '2rem 1.5rem', paddingBottom: '8rem' }}>
                    {activeTab === 'dashboard' && <Dashboard />}
                    {activeTab === 'entry' && <Protocol onNotify={(m, t) => setToast({ message: m, type: t })} />}
                    {activeTab === 'log' && <Archives />}
                </main>

                <nav className="glass-v3" style={{
                    position: 'fixed', bottom: '1.5rem', left: '1.2rem', right: '1.2rem',
                    padding: '0.6rem', display: 'flex', gap: '0.6rem', zIndex: 1000,
                    borderRadius: '28px'
                }}>
                    <button className={`dock-button ${activeTab === 'dashboard' ? 'active' : ''}`} onClick={() => setActiveTab('dashboard')} style={{
                        flex: 1, height: '3.8rem', borderRadius: '22px', border: 'none', background: activeTab === 'dashboard' ? '#fff' : 'transparent', color: activeTab === 'dashboard' ? '#000' : '#fff', transition: 'all 0.4s cubic-bezier(0.23, 1, 0.32, 1)', display: 'flex', alignItems: 'center', justifyContent: 'center'
                    }}>
                        <LayoutGrid size={24} />
                    </button>
                    <button className={`dock-button ${activeTab === 'entry' ? 'active' : ''}`} onClick={() => setActiveTab('entry')} style={{
                        flex: 1, height: '3.8rem', borderRadius: '22px', border: 'none', background: activeTab === 'entry' ? '#fff' : 'transparent', color: activeTab === 'entry' ? '#000' : '#fff', transition: 'all 0.4s cubic-bezier(0.23, 1, 0.32, 1)', display: 'flex', alignItems: 'center', justifyContent: 'center'
                    }}>
                        <FlaskConical size={24} />
                    </button>
                    <button className={`dock-button ${activeTab === 'log' ? 'active' : ''}`} onClick={() => setActiveTab('log')} style={{
                        flex: 1, height: '3.8rem', borderRadius: '22px', border: 'none', background: activeTab === 'log' ? '#fff' : 'transparent', color: activeTab === 'log' ? '#000' : '#fff', transition: 'all 0.4s cubic-bezier(0.23, 1, 0.32, 1)', display: 'flex', alignItems: 'center', justifyContent: 'center'
                    }}>
                        <Database size={24} />
                    </button>
                </nav>
            </div>
        </WasteProvider>
    );
}

export default App;
