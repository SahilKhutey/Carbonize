import React from 'react';
import { X } from 'lucide-react';

interface ModalProps {
  open: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
}

export function Modal({ open, onClose, title, children }: ModalProps) {
  if (!open) return null;
  
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm animate-fade-in">
      <div className="bg-surface-elevated border border-border rounded-theme-lg p-6 w-full max-w-xl max-h-[90vh] overflow-y-auto shadow-theme-xl">
        <div className="flex items-center justify-between mb-4 border-b border-border pb-3">
          <h3 className="font-bold text-lg text-text">{title}</h3>
          <button onClick={onClose} className="p-1 rounded text-text-tertiary hover:text-text hover:bg-surface-hover">
            <X className="w-5 h-5" />
          </button>
        </div>
        <div>{children}</div>
      </div>
    </div>
  );
}
