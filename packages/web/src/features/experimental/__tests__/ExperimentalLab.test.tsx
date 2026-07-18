import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import { ExperimentalLab } from '../pages/ExperimentalLab.tsx';

// Mock fetch global object
global.fetch = vi.fn();

const mockSimResponse = {
  success: true,
  message: "Success",
  efficiencies: {
    CO2: 85.5,
    SO2: 95.0,
    NOx: 62.0,
    PM: 99.0,
    Metal: 75.0
  },
  block_strength_mpa: 28.5,
  block_grade: "M25 (Premium)",
  final_state: {
    CaCO3_s: 15.0,
    MgCO3_s: 8.0,
    CaNO3_s: 4.5,
    Metal_chelated: 0.35
  },
  sizing: {
    vessel_diameter_m: 2.34,
    vessel_height_m: 54.0,
    circulating_liquid_flow_m3_hr: 85.0,
    pump_power_kw: 15.2,
    descaling_interval_days: 12.5,
    annual_downtime_hours: 108.0,
    adjusted_operating_hours: 8652.0,
    total_scaling_rate_kg_hr: 16.7
  }
};

describe('ExperimentalLab Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    (global.fetch as any).mockResolvedValue({
      ok: true,
      json: async () => mockSimResponse
    });
  });

  it('renders slider titles, simulation metrics, and sizing results', async () => {
    render(
      <MemoryRouter>
        <ExperimentalLab />
      </MemoryRouter>
    );

    // Verify title elements render
    expect(screen.getByText(/Material Science Lab/i)).toBeInTheDocument();
    expect(screen.getByText(/Chitosan Crosslinking/i)).toBeInTheDocument();
    expect(screen.getByText(/Mg²⁺ Substitution Ratio/i)).toBeInTheDocument();
    expect(screen.getByText(/Liquid-to-Gas Ratio/i)).toBeInTheDocument();

    // Verify results show up after fetch resolves
    await waitFor(() => {
      expect(screen.getByText("85.5%")).toBeInTheDocument();
      expect(screen.getByText("62.0%")).toBeInTheDocument();
      expect(screen.getByText("28.5 MPa")).toBeInTheDocument();
      // Sizing asserts
      expect(screen.getByText(/Ø 2.34m × 54.0m/i)).toBeInTheDocument();
      expect(screen.getByText(/85 m³\/hr/i)).toBeInTheDocument();
      expect(screen.getByText(/8652 hrs \/ yr/i)).toBeInTheDocument();
    });
  });
});
