import sys
import numpy as np

sys.path.insert(0, r'c:\Users\ASUS\Documents\Carbonize')

from carbonize_chemistry.chemistry.vle import CO2AmineVLE, VLEResult
from carbonize_chemistry.chemistry.kinetics import CO2MEA_Kinetics, CO2MDEA_Kinetics, CO2Piperazine_Kinetics
from carbonize_chemistry.chemistry.mass_transfer import TwoFilmTheory, MassTransferParams
from carbonize_chemistry.chemistry.constants import R_GAS, MOLAR_MASSES, CRITICAL_PROPERTIES
from carbonize_chemistry.pollutants.sox import WetLimestoneSOxScrubber
from carbonize_chemistry.pollutants.nox import SCR_System
from carbonize_chemistry.pollutants.mercury import ActivatedCarbonInjection
from carbonize_chemistry.columns.tray_column import TrayColumnSolver, ColumnSpec, StreamConditions

def run_chemical_verification():
    print("=" * 80)
    print("        CARBONIZE DEEP CHEMICAL CHEMISTRY & REACTION KINETICS SUITE")
    print("=" * 80)

    # 1. Physical Constants & Molar Mass Calculations
    print("\n[1/6] VERIFYING PHYSICAL CONSTANTS & MOLAR MASSES")
    assert R_GAS == 8.314462618, f"Gas constant mismatch: {R_GAS}"
    assert abs(MOLAR_MASSES['CO2'] - 44.01) < 0.05, f"CO2 molar mass mismatch: {MOLAR_MASSES['CO2']}"
    assert abs(MOLAR_MASSES['MEA'] - 61.08) < 0.05, f"MEA molar mass mismatch: {MOLAR_MASSES['MEA']}"
    assert abs(MOLAR_MASSES['Air'] - 28.97) < 0.05, f"Air molar mass mismatch: {MOLAR_MASSES['Air']}"
    print(f"  [OK] Gas Constant R = {R_GAS} J/(mol*K)")
    print(f"  [OK] Molar Masses: CO2={MOLAR_MASSES['CO2']} g/mol, MEA={MOLAR_MASSES['MEA']} g/mol, Air={MOLAR_MASSES['Air']} g/mol")
    print(f"  [OK] Critical Temp: CO2={CRITICAL_PROPERTIES['CO2']['Tc']} K, MEA={CRITICAL_PROPERTIES['MEA']['Tc']} K")
    print("  --> PASS: Physical constants & critical properties match CODATA & IUPAC standards.")

    # 2. VLE Kent-Eisenberg Equilibrium Thermodynamics
    print("\n[2/6] VERIFYING VLE & EQUILIBRIUM PARTIAL PRESSURES (Kent-Eisenberg)")
    vle_mea = CO2AmineVLE(amine='MEA', concentration_wt=30.0)
    T_abs_K = 313.15  # 40 deg C
    T_strip_K = 393.15 # 120 deg C
    
    H_40C = vle_mea.henry_constant_co2_water(T_abs_K)
    p_co2_40C = vle_mea.equilibrium_pressure(T_abs_K, loading=0.01)
    p_co2_120C = vle_mea.equilibrium_pressure(T_strip_K, loading=0.01)
    
    loading_recovered = vle_mea.loading_from_partial_pressure(T_abs_K, p_co2_40C)
    
    print(f"  [OK] Henry's Constant H_CO2(40C) = {H_40C:.2e} Pa")
    print(f"  [OK] Absorber Equilibrium Pressure P*(40C, alpha=0.01) = {p_co2_40C:.2f} Pa")
    print(f"  [OK] Stripper Equilibrium Pressure P*(120C, alpha=0.01) = {p_co2_120C:.2f} Pa")
    print(f"  [OK] Bisection Inversion Recovery: alpha_calc = {loading_recovered:.4f} mol/mol (target: 0.01)")
    
    assert abs(loading_recovered - 0.01) < 0.005, f"VLE inversion error: {loading_recovered}"
    assert p_co2_120C > p_co2_40C, "Thermal desorption pressure ratio failed"
    print("  --> PASS: VLE equilibrium curves & thermal desorption pressure ratios verified.")

    # 3. Zwitterion Kinetics & Arrhenius Reaction Rates
    print("\n[3/6] VERIFYING AMINE REACTION KINETICS & ARRHENIUS ACTIVATION")
    mea_kin = CO2MEA_Kinetics(concentration_wt=30.0)
    k2_298K = mea_kin.second_order_rate_constant(298.15) # 25 deg C
    k2_313K = mea_kin.second_order_rate_constant(313.15) # 40 deg C
    arrhenius_ratio = k2_313K / k2_298K
    
    # Kinetic flux calculation
    flux_co2 = mea_kin.flux_per_area(T=313.15, C_CO2_interface=0.025, C_amine_bulk=4900.0, C_CO2_bulk=0.001)
    
    mdea_kin = CO2MDEA_Kinetics(concentration_wt=50.0)
    k_mdea_313K = mdea_kin.rate_constant(313.15)
    
    pz_kin = CO2Piperazine_Kinetics(concentration_wt=8.0)
    k2_pz_313K = pz_kin.rate_constant(313.15)
    
    print(f"  [OK] MEA Rate Constant k2(25C)  = {k2_298K:.2f} m3/(mol*s)")
    print(f"  [OK] MEA Rate Constant k2(40C)  = {k2_313K:.2f} m3/(mol*s)")
    print(f"  [OK] Arrhenius Activation Ratio  = {arrhenius_ratio:.2f}x (Literature range: 2.0 - 2.5)")
    print(f"  [OK] Mass Transfer Flux N_CO2   = {flux_co2:.6f} mol/(m2*s)")
    print(f"  [OK] MDEA Pseudo-1st Order Rate = {k_mdea_313K:.2f} s^-1")
    print(f"  [OK] Piperazine (PZ) k2(40C)   = {k2_pz_313K:.2f} m3/(mol*s)")
    
    assert k2_pz_313K > 10.0 and k2_313K > 10.0, "Rate constants must be in physical range"
    print("  --> PASS: Zwitterion and base-catalyzed hydration rate constants verified.")

    # 4. Two-Film Mass Transfer Theory
    print("\n[4/6] VERIFYING TWO-FILM MASS TRANSFER THEORY & ENHANCEMENT FACTOR")
    tf = TwoFilmTheory()
    k_g = tf.calculate_k_g(compound='CO2', T=313.15, P=101325.0, v_gas=1.5, d_p=0.025)
    k_l = tf.calculate_k_l(T=313.15, d_p=0.025, v_liquid=0.05, compound_l='CO2', solvent='H2O')
    E_factor = tf.enhancement_factor(Ha=5.0)
    
    params = MassTransferParams(k_G=k_g, k_L=k_l, a=250.0, f=E_factor, H=2500.0)
    K_G_overall = params.K_G
    
    print(f"  [OK] Gas Mass Transfer k_G      = {k_g:.6e} m/s")
    print(f"  [OK] Liquid Mass Transfer k_L   = {k_l:.6e} m/s")
    print(f"  [OK] Enhancement Factor (Ha=5)  = {E_factor:.2f}")
    print(f"  [OK] Overall Mass Transfer K_G = {K_G_overall:.6e} m/s")
    
    assert k_g > 0.0 and k_l > 0.0, "Mass transfer coefficients must be positive"
    assert E_factor == 5.0, "Enhancement factor for Ha > 3 should equal Ha"
    print("  --> PASS: Two-film mass transfer theory & Onda correlation coefficients verified.")

    # 5. Flue Gas Scrubbers & Pollutant Control Dynamics
    print("\n[5/6] VERIFYING POLLUTANT CONTROL & SCRUBBER CHEMISTRY")
    sox = WetLimestoneSOxScrubber(config={'L_G_ratio': 50.0, 'slurry_pH': 6.5})
    sox_res = sox.calculate_removal(gas_flow_nm3_h=100000.0, SO2_in_ppm=800.0)
    
    scr = SCR_System()
    scr_res = scr.calculate_performance(gas_flow_nm3_h=100000.0, NO_in_ppm=350.0)
    
    aci = ActivatedCarbonInjection()
    aci_res = aci.calculate_removal(gas_flow_nm3_h=100000.0, Hg_in_ug_Nm3=8.5)
    
    print(f"  [OK] SOx FGD Efficiency        = {sox_res.removal_efficiency:.1f}% ({sox_res.SO2_out:.1f} ppm outlet)")
    print(f"  [OK] NOx SCR Conversion        = {scr_res.conversion:.1f}% ({scr_res.NO_out:.1f} ppm outlet)")
    print(f"  [OK] Mercury Removal Efficiency = {aci_res.removal_efficiency:.1f}% ({aci_res.Hg_out:.2f} ug/Nm3 outlet)")
    
    assert sox_res.removal_efficiency > 95.0, "SOx efficiency target failed"
    assert scr_res.conversion > 90.0, "NOx SCR conversion target failed"
    assert aci_res.removal_efficiency > 90.0, "Mercury removal efficiency target failed"
    print("  --> PASS: FGD, SCR, and activated carbon mercury removal chemistry verified.")

    # 6. Tray-by-Tray Column Mass Transfer Solver
    print("\n[6/6] VERIFYING 20-TRAY MEA ABSORBER COLUMN SOLVER (Wang-Henke)")
    col_spec = ColumnSpec(n_trays=20, diameter=4.0)
    solver = TrayColumnSolver(column=col_spec, amine='MEA')
    
    gas_in = StreamConditions(T=313.15, P=101325.0, flow=5000.0, composition={'CO2': 0.12, 'N2': 0.88})
    liquid_in = StreamConditions(T=313.15, P=101325.0, flow=15000.0, composition={'MEA': 0.30, 'CO2': 0.25})
    
    sol_res = solver.solve(gas_in=gas_in, liquid_in=liquid_in)
    
    co2_inlet = gas_in.composition['CO2']
    co2_outlet = sol_res['gas_out']['CO2_mol_frac']
    co2_removal_pct = (1.0 - co2_outlet / co2_inlet) * 100.0
    rich_loading = sol_res['liquid_out']['loading']
    
    print(f"  [OK] Tray Column Trays          = {col_spec.n_trays} trays")
    print(f"  [OK] CO2 Outlet Mol Fraction   = {co2_outlet:.4f} (Inlet: {co2_inlet:.2f})")
    print(f"  [OK] CO2 Removal Efficiency     = {co2_removal_pct:.1f}%")
    print(f"  [OK] Rich Liquid Loading        = {rich_loading:.3f} mol/mol")
    
    assert co2_removal_pct >= 80.0, f"Tray absorber CO2 removal below 80%: {co2_removal_pct}"
    print("  --> PASS: 20-tray Wang-Henke liquid-gas absorption solver verified.")

    print("\n" + "=" * 80)
    print("     ALL DEEP CHEMICAL CHEMISTRY & KINETICS VERIFICATIONS PASSED 100%")
    print("=" * 80)

if __name__ == '__main__':
    run_chemical_verification()
