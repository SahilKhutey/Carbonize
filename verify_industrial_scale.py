import sys
import numpy as np

sys.path.insert(0, r'c:\Users\ASUS\Documents\Carbonize')

from carbonize_chemistry.hardware_twin.plant import CarbonCapturePlant
from carbonize_mvp.roi.calculator import ROICalculator
from carbonize_mvp.architecture.sizing import estimate_compute_hardware

def verify_industrial_scale():
    print("=" * 80)
    print("       CARBONIZE INDUSTRIAL SCALE VERIFICATION & HYDRAULIC VALIDATION")
    print("=" * 80)

    # Industrial Capacity Tiers & Sizing Specifications
    tiers = [
        {
            "name": "Small Industrial (Cement Skid)",
            "capacity_t_yr": 100_000,
            "gas_flow_nm3_h": 150_000,
            "absorber_dia_m": 5.5,
            "n_trains": 1
        },
        {
            "name": "Medium Industrial (Steel Mill)",
            "capacity_t_yr": 500_000,
            "gas_flow_nm3_h": 750_000,
            "absorber_dia_m": 12.0,
            "n_trains": 1
        },
        {
            "name": "Mega Industrial (Power Plant)",
            "capacity_t_yr": 1_000_000,
            "gas_flow_nm3_h": 1_500_000,
            "absorber_dia_m": 12.0,
            "n_trains": 2
        },
    ]

    roi_calc = ROICalculator()

    for idx, t in enumerate(tiers, 1):
        cap = t["capacity_t_yr"]
        flow = t["gas_flow_nm3_h"]
        dia = t["absorber_dia_m"]
        trains = t["n_trains"]
        
        # Calculate ROI metrics
        res = roi_calc.calculate(capacity_t_yr=cap)
        hw = estimate_compute_hardware(capacity_t_yr=cap)
        
        # Compute hydraulic & process parameters
        co2_hourly_ton = cap / 8760.0
        co2_hourly_kmol = co2_hourly_ton * 1000.0 / 44.01
        solvent_recirc_m3_h = co2_hourly_kmol * 61.08 / (1000.0 * 0.30 * (0.45 - 0.15))
        
        # Gas superficial velocity per absorber train
        flow_per_train = flow / trains
        column_area = np.pi * (dia / 2.0)**2
        gas_velocity_m_s = (flow_per_train / 3600.0) / column_area
        
        # Reboiler steam demand (t/h LP steam)
        steam_latent_heat_gj_t = 2.2 # GJ/t steam at 3 bar sat
        reboiler_duty_gj_h = co2_hourly_ton * 2.45 # SOLV-0237 heat duty
        steam_flow_t_h = reboiler_duty_gj_h / steam_latent_heat_gj_t
        
        print(f"\n[{idx}/3] {t['name'].upper()}")
        print(f"      CO2 Capture Capacity   : {cap:,} t/year ({co2_hourly_ton:.1f} t/h CO2)")
        print(f"      Flue Gas Throughput    : {flow:,} Nm3/h ({trains} absorber train{'s' if trains > 1 else ''})")
        print(f"      Absorber Diameter      : {dia:.1f} m per train (Area: {column_area:.1f} m2)")
        print(f"      Gas Superficial Velocity: {gas_velocity_m_s:.2f} m/s (< 2.5 m/s flooding threshold)")
        print(f"      Solvent Recirculation  : {solvent_recirc_m3_h:.1f} m3/h")
        print(f"      Reboiler Steam Demand  : {steam_flow_t_h:.1f} t/h LP steam (Duty: {reboiler_duty_gj_h:.1f} GJ/h)")
        print(f"      Annual OPEX Savings    : ${res['annual_savings_usd']/1e6:.2f}M / year")
        print(f"      Payback Period         : {res['payback_months']:.1f} months")
        print(f"      10-Year Net Present Val: ${res['npv_10yr_usd']/1e6:.1f}M")
        print(f"      Compute Hardware Spec  : Tier '{hw['tier']}', {hw['cpus']} vCPUs, {hw['gpus']} GPUs")
        
        # Hydraulic & physical assertions
        assert gas_velocity_m_s < 2.5, f"Gas velocity exceeds flooding limit: {gas_velocity_m_s}"
        assert res['annual_savings_usd'] > 0.0, "Annual savings must be positive"
        assert res['payback_months'] < 6.0, "Payback period must be under 6 months"
        assert res['energy_savings_pct'] == 31.9, "Energy savings must match 31.9%"

    print("\n" + "=" * 80)
    print("     INDUSTRIAL SCALE THROUGHPUT, HYDRAULICS & ROI VERIFIED 100%")
    print("=" * 80)

if __name__ == '__main__':
    verify_industrial_scale()
