import React, { createContext, useContext, useState } from 'react';

const WasteContext = createContext();

export const WasteProvider = ({ children }) => {
    const [containers, setContainers] = useState([
        { id: 'ACID-001', location: 'Fume Hood A', type: 'Acidic', fill: 45, capacity: 100, deadline: 5 },
        { id: 'BASE-022', location: 'Safety Cabinet 1', type: 'Basic', fill: 88, capacity: 100, deadline: 2 },
        { id: 'SOLV-009', location: 'Fume Hood B', type: 'Solvent', fill: 12, capacity: 100, deadline: 14 },
        { id: 'TOX-004', location: 'Lab 204', type: 'Toxic', fill: 65, capacity: 100, deadline: 7 },
    ]);

    const [history, setHistory] = useState([
        { id: 1, chemical: 'Sulphuric Acid', qty: '500mL', container: 'ACID-001', time: '2026-01-28 14:30' },
        { id: 2, chemical: 'Acetone', qty: '200mL', container: 'SOLV-009', time: '2026-01-29 09:15' },
    ]);

    const addDisposal = (disposal) => {
        const newEntry = {
            ...disposal,
            id: Date.now(),
            time: new Date().toLocaleString(),
        };
        setHistory([newEntry, ...history]);

        // Update container fill level
        setContainers(prev => prev.map(c =>
            c.id === disposal.container ? { ...c, fill: Math.min(c.fill + 10, 100) } : c
        ));
    };

    return (
        <WasteContext.Provider value={{ containers, history, addDisposal }}>
            {children}
        </WasteContext.Provider>
    );
};

export const useWaste = () => useContext(WasteContext);
