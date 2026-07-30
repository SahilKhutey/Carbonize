import React, { useState, createContext, useContext } from 'react';

interface ExportContextType {
  openExport: (config: any) => void;
  closeExport: () => void;
  isOpen: boolean;
  config: any;
}

const ExportContext = createContext<ExportContextType | undefined>(undefined);

export function ExportProvider({ children }: { children: React.ReactNode }) {
  const [isOpen, setIsOpen] = useState(false);
  const [config, setConfig] = useState<any>(null);
  
  const openExport = (cfg: any) => {
    setConfig(cfg);
    setIsOpen(true);
  };
  const closeExport = () => {
    setIsOpen(false);
    setConfig(null);
  };
  
  return (
    <ExportContext.Provider value={{ openExport, closeExport, isOpen, config }}>
      {children}
    </ExportContext.Provider>
  );
}

export function useExport() {
  const ctx = useContext(ExportContext);
  if (!ctx) throw new Error('useExport must be used within ExportProvider');
  return ctx;
}
