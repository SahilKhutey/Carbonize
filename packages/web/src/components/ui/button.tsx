/**
 * packages/web/src/components/ui/button.tsx
 */
import React from "react";

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "default" | "outline" | "ghost";
  size?: "default" | "sm" | "lg";
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className = "", variant = "default", size = "default", ...props }, ref) => {
    let baseStyle = "inline-flex items-center justify-center rounded-md font-medium transition-colors focus-visible:outline-none disabled:opacity-50 disabled:pointer-events-none";
    let variantStyle = "";
    let sizeStyle = "";

    if (variant === "outline") variantStyle = "border border-slate-200 bg-transparent hover:bg-slate-100 text-slate-900";
    else if (variant === "ghost") variantStyle = "bg-transparent hover:bg-slate-100 text-slate-900";
    else variantStyle = "bg-slate-900 text-white hover:bg-slate-800";

    if (size === "sm") sizeStyle = "h-9 px-3 text-xs";
    else if (size === "lg") sizeStyle = "h-11 px-8 text-base";
    else sizeStyle = "h-10 px-4 py-2 text-sm";

    return (
      <button
        ref={ref}
        className={`${baseStyle} ${variantStyle} ${sizeStyle} ${className}`}
        {...props}
      />
    );
  }
);

Button.displayName = "Button";
