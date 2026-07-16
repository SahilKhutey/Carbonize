/**
 * Connection state indicator pill.
 * 
 * Shows the current state of the WebSocket connection with appropriate
 * color, icon, and message. This is the "always visible" indicator.
 */

import React from "react";
import { Wifi, WifiOff, RefreshCw, Loader2 } from "lucide-react";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { ConnectionState } from "@/hooks/useWebSocket";

interface ConnectionStateIndicatorProps {
  state: ConnectionState;
  reconnectAttempt?: number;
  lastUpdateAt?: Date;
  showLabel?: boolean;        // Show text label or just icon
  size?: "sm" | "md";
  onClick?: () => void;        // E.g., retry button
}

const STATE_CONFIG: Record<ConnectionState, {
  color: string;
  bgColor: string;
  borderColor: string;
  icon: React.ReactNode;
  label: string;
  description: string;
}> = {
  connected: {
    color: "text-emerald-700",
    bgColor: "bg-emerald-50",
    borderColor: "border-emerald-200",
    icon: <Wifi className="w-3 h-3" />,
    label: "LIVE",
    description: "Receiving real-time updates",
  },
  connecting: {
    color: "text-amber-700",
    bgColor: "bg-amber-50",
    borderColor: "border-amber-200",
    icon: <Loader2 className="w-3 h-3 animate-spin" />,
    label: "Connecting",
    description: "Establishing WebSocket connection",
  },
  reconnecting: {
    color: "text-amber-700",
    bgColor: "bg-amber-50",
    borderColor: "border-amber-200",
    icon: <RefreshCw className="w-3 h-3 animate-spin" />,
    label: `Reconnecting`,  // dynamic label will be built in component
    description: "Re-establishing WebSocket connection",
  },
  disconnected: {
    color: "text-red-700",
    bgColor: "bg-red-50",
    borderColor: "border-red-200",
    icon: <WifiOff className="w-3 h-3" />,
    label: "Disconnected",
    description: "WebSocket connection lost; data is stale",
  },
  error: {
    color: "text-red-700",
    bgColor: "bg-red-50",
    borderColor: "border-red-200",
    icon: <WifiOff className="w-3 h-3" />,
    label: "Error",
    description: "WebSocket error; data unavailable",
  },
};

export function ConnectionStateIndicator({
  state,
  reconnectAttempt = 0,
  lastUpdateAt,
  showLabel = true,
  size = "md",
  onClick,
}: ConnectionStateIndicatorProps) {
  const config = STATE_CONFIG[state];
  
  // Update reconnecting label with attempt number
  const label = state === "reconnecting" 
    ? `Reconnecting (attempt ${reconnectAttempt})` 
    : config.label;
  
  const staleness = lastUpdateAt 
    ? Math.floor((Date.now() - lastUpdateAt.getTime()) / 1000)
    : null;
  
  const sizeClasses = {
    sm: "text-[10px] px-1.5 py-0.5 gap-0.5",
    md: "text-xs px-2 py-0.5 gap-1",
  };
  
  const iconSize = size === "sm" ? "w-3 h-3" : "w-3.5 h-3.5";
  
  return (
    <TooltipProvider>
      <Tooltip>
        <TooltipTrigger asChild>
          <button
            onClick={onClick}
            className={`
              inline-flex items-center rounded-full font-semibold
              border transition-colors
              ${config.bgColor} ${config.color} ${config.borderColor}
              ${sizeClasses[size]}
              ${onClick ? "cursor-pointer hover:opacity-80" : "cursor-default"}
            `}
          >
            <span className={iconSize}>{config.icon}</span>
            {showLabel && <span>{label}</span>}
            {state === "connected" && staleness !== null && staleness > 5 && (
              <span className="text-[10px] opacity-75">
                · {staleness}s
              </span>
            )}
          </button>
        </TooltipTrigger>
        <TooltipContent>
          <p className="text-xs font-semibold">{label}</p>
          <p className="text-xs text-gray-500">{config.description}</p>
          {state === "connected" && staleness !== null && (
            <p className="text-xs text-gray-500 mt-1">
              Last update: {staleness}s ago
            </p>
          )}
          {state === "reconnecting" && (
            <p className="text-xs text-amber-600 mt-1">
              Showing cached data
            </p>
          )}
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  );
}
