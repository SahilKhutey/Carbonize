/**
 * Tests for graceful degradation.
 */

import React from "react";
import { render, screen, act } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { DataFreshnessOverlay } from "../DataFreshnessOverlay";
import { ConnectionStateIndicator } from "../ConnectionStateIndicator";

describe("DataFreshnessOverlay", () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });
  
  it("shows full opacity when data is fresh", () => {
    const recentDate = new Date();
    render(
      <DataFreshnessOverlay lastUpdateAt={recentDate}>
        <div data-testid="content">Content</div>
      </DataFreshnessOverlay>
    );
    
    const content = screen.getByTestId("content").parentElement!;
    expect(content.className).toContain("opacity-100");
  });
  
  it("dims content and shows stale banner when data is stale", () => {
    const oldDate = new Date(Date.now() - 30000); // 30s ago
    render(
      <DataFreshnessOverlay lastUpdateAt={oldDate} staleThresholdSeconds={10}>
        <div data-testid="content">Content</div>
      </DataFreshnessOverlay>
    );
    
    expect(screen.getByText(/STALE DATA/)).toBeInTheDocument();
    const content = screen.getByTestId("content").parentElement!;
    expect(content.className).toContain("opacity-70");
  });
  
  it("shows empty state when no data ever received", () => {
    render(
      <DataFreshnessOverlay lastUpdateAt={null}>
        <div data-testid="content">Content</div>
      </DataFreshnessOverlay>
    );
    
    expect(screen.getByText(/No data received yet/)).toBeInTheDocument();
  });
  
  it("escalates to VERY STALE after long time", () => {
    const veryOld = new Date(Date.now() - 120000); // 2 min ago
    render(
      <DataFreshnessOverlay
        lastUpdateAt={veryOld}
        staleThresholdSeconds={10}
        veryStaleThresholdSeconds={60}
      >
        <div data-testid="content">Content</div>
      </DataFreshnessOverlay>
    );
    
    expect(screen.getByText(/VERY STALE/)).toBeInTheDocument();
  });
});

describe("ConnectionStateIndicator", () => {
  it("shows LIVE when connected", () => {
    render(<ConnectionStateIndicator state="connected" />);
    expect(screen.getByText("LIVE")).toBeInTheDocument();
    expect(screen.getByText("LIVE").closest("button")?.className).toContain("emerald");
  });
  
  it("shows Reconnecting with attempt number", () => {
    render(<ConnectionStateIndicator state="reconnecting" reconnectAttempt={5} />);
    expect(screen.getByText(/attempt 5/)).toBeInTheDocument();
  });
  
  it("shows Disconnected in red", () => {
    render(<ConnectionStateIndicator state="disconnected" />);
    expect(screen.getByText("Disconnected")).toBeInTheDocument();
    expect(screen.getByText("Disconnected").closest("button")?.className).toContain("red");
  });
  
  it("shows age when connected and stale", () => {
    const oldDate = new Date(Date.now() - 15000);
    render(
      <ConnectionStateIndicator 
        state="connected" 
        lastUpdateAt={oldDate}
      />
    );
    expect(screen.getByText(/15s/)).toBeInTheDocument();
  });
});
