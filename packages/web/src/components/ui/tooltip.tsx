/**
 * packages/web/src/components/ui/tooltip.tsx
 */
import React, { useState } from "react";

export function TooltipProvider({ children }: { children: React.ReactNode }) {
  return <>{children}</>;
}

export function Tooltip({ children }: { children: React.ReactNode }) {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div 
      className="relative inline-block" 
      onMouseEnter={() => setIsOpen(true)} 
      onMouseLeave={() => setIsOpen(false)}
    >
      {React.Children.map(children, (child) => {
        if (React.isValidElement(child)) {
          return React.cloneElement(child as React.ReactElement<any>, { isOpen });
        }
        return child;
      })}
    </div>
  );
}

export function TooltipTrigger({ children, asChild }: { children: React.ReactNode, asChild?: boolean }) {
  return <>{children}</>;
}

export function TooltipContent({ children, isOpen }: { children?: React.ReactNode, isOpen?: boolean }) {
  if (!isOpen) return null;
  return (
    <div className="absolute z-50 px-3 py-2 text-sm text-white bg-slate-900 rounded-md shadow-md -top-2 transform -translate-y-full left-1/2 -translate-x-1/2 min-w-max pointer-events-none">
      {children}
    </div>
  );
}
