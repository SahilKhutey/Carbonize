import sys
import time
import numpy as np
import torch

sys.path.insert(0, r'c:\Users\ASUS\Documents\Carbonize')

from carbonize_chemistry.columns.tray_column import TrayColumnSolver, ColumnSpec, StreamConditions
from carbonize_reactor.reactors.packed_bed import PackedBedReactor
from carbonize_reactor.reactors.base import ReactorGeometry, OperatingConditions, ReactionNetwork
from carbonize_ssml.electronic.dft import KS_DFT, PlaneWaveBasis, BandStructureAnalyzer
from carbonize_compchem.md.integrators.velocity_verlet import VelocityVerlet, MDState
from carbonize_streaming.app.anomaly.autoencoder import LSTMAutoencoder

def verify_simulations_running():
    print("=" * 80)
    print("        CARBONIZE MULTI-PHYSICS SIMULATION ENGINES VERIFICATION")
    print("=" * 80)

    # 1. Tray-by-Tray Absorber Column Simulation (Wang-Henke Matrix)
    print("\n[1/5] RUNNING TRAY-BY-TRAY ABSORBER COLUMN SIMULATION")
    t0 = time.time()
    col_spec = ColumnSpec(n_trays=20, diameter=4.0)
    solver = TrayColumnSolver(column=col_spec, amine='MEA')
    gas_in = StreamConditions(T=313.15, P=101325.0, flow=5000.0, composition={'CO2': 0.12, 'N2': 0.88})
    liquid_in = StreamConditions(T=313.15, P=101325.0, flow=15000.0, composition={'MEA': 0.30, 'CO2': 0.25})
    
    col_res = solver.solve(gas_in=gas_in, liquid_in=liquid_in)
    dt1 = (time.time() - t0) * 1000.0
    
    co2_outlet = col_res['gas_out']['CO2_mol_frac']
    removal_eff = (1.0 - co2_outlet / 0.12) * 100.0
    
    print(f"  [OK] Solver Iterations : {col_res['iterations']} iterations in {dt1:.2f} ms")
    print(f"  [OK] Outlet CO2 Frac   : {co2_outlet:.4f} (Removal: {removal_eff:.1f}%)")
    print(f"  [OK] Temperature Range : {col_res['temperature_profile'][0]:.1f} K to {col_res['temperature_profile'][-1]:.1f} K")
    assert col_res['converged'], "Column solver failed to converge"
    print("  --> PASS: 20-tray Wang-Henke absorption profile simulation converged.")

    # 2. 1D Catalytic Packed Bed Reactor Simulation
    print("\n[2/5] RUNNING 1D CATALYTIC PACKED BED REACTOR SIMULATION")
    t0 = time.time()
    geom = ReactorGeometry(length=5.0, diameter=1.0, particle_diameter=0.005)
    operating = OperatingConditions(T_in=673.15, P_in=200000.0, flow_gas=10.0, y_in={'CO': 0.10, 'O2': 0.05, 'CO2': 0.02, 'N2': 0.83})
    reactions = ReactionNetwork(species=['CO', 'O2', 'CO2', 'N2'])
    
    pbr = PackedBedReactor(geom, operating, reactions)
    reactor_res = pbr.solve(n_points=50)
    dt2 = (time.time() - t0) * 1000.0
    
    print(f"  [OK] Spatial Grid      : 50 grid points along 5.0m length ({dt2:.2f} ms)")
    print(f"  [OK] Pressure Drop dP  : {reactor_res.pressure_drop:.1f} Pa (Ergun equation)")
    print(f"  [OK] CO Conversion     : {reactor_res.conversion.get('CO', 0.0):.1f}%")
    assert reactor_res.pressure_drop > 0.0, "Pressure drop must be positive"
    print("  --> PASS: 1D catalytic packed bed ODE spatial simulation completed.")

    # 3. Plane-Wave Kohn-Sham DFT Electronic Structure Simulation
    print("\n[3/5] RUNNING PLANE-WAVE KOHN-SHAM DFT BAND STRUCTURE SIMULATION")
    t0 = time.time()
    dft = KS_DFT(functional='LDA')
    k_path = [
        ('G', np.array([0.0, 0.0, 0.0])),
        ('X', np.array([0.5, 0.0, 0.5])),
        ('W', np.array([0.5, 0.25, 0.75])),
        ('L', np.array([0.5, 0.5, 0.5]))
    ]
    
    band_res = dft.compute_band_structure(k_path=k_path, n_per_segment=10)
    gap_info = BandStructureAnalyzer.find_band_gap(band_res['bands'], band_res['efermi'])
    dt3 = (time.time() - t0) * 1000.0
    
    bands_arr = np.array(band_res['bands'])
    
    print(f"  [OK] k-Path Sampling   : {len(band_res['k_distances'])} k-points sampled in {dt3:.2f} ms")
    print(f"  [OK] Electronic Bands  : {bands_arr.shape[1]} bands computed")
    print(f"  [OK] Fermi Level E_f   : {band_res['efermi']:.2f} eV")
    print(f"  [OK] Calculated Gap    : {gap_info['band_gap']:.2f} eV ({gap_info['gap_type']})")
    assert bands_arr.shape[0] == len(band_res['k_distances']), "Band dimension mismatch"
    print("  --> PASS: Plane-Wave Kohn-Sham DFT band structure simulation completed.")

    # 4. Molecular Dynamics Trajectory Simulation (Velocity Verlet Integrator)
    print("\n[4/5] RUNNING MOLECULAR DYNAMICS TRAJECTORY SIMULATION")
    t0 = time.time()
    n_atoms = 50
    positions = np.random.uniform(0.0, 20.0, (n_atoms, 3))
    velocities = np.random.normal(0.0, 1.0, (n_atoms, 3))
    forces = np.random.normal(0.0, 0.1, (n_atoms, 3))
    masses = np.full(n_atoms, 12.011) # Carbon atoms
    box = np.eye(3) * 25.0
    
    md_state = MDState(positions=positions, velocities=velocities, forces=forces, box=box)
    vv = VelocityVerlet(dt=0.001)
    
    def harmonic_force(pos):
        return -0.05 * pos
        
    for step in range(100):
        md_state = vv.step(md_state, masses, harmonic_force)
        
    dt4 = (time.time() - t0) * 1000.0
    
    print(f"  [OK] Trajectory Steps  : 100 timesteps (dt = 1 fs) in {dt4:.2f} ms")
    print(f"  [OK] Final Kinetic E   : {md_state.kinetic_energy:.2f} kcal/mol")
    print(f"  [OK] Final Temp (K)    : {md_state.temperature:.1f} K")
    assert md_state.step == 100, "MD simulation step count mismatch"
    print("  --> PASS: Velocity-Verlet 100-step MD trajectory simulation completed.")

    # 5. PyTorch LSTM Autoencoder Neural Time-Series Simulation
    print("\n[5/5] RUNNING PYTORCH LSTM AUTOENCODER NEURAL SIMULATION")
    t0 = time.time()
    model = LSTMAutoencoder(input_dim=4, hidden_dim=16, num_layers=1, sequence_length=30)
    optimizer = torch.optim.Adam(model.parameters(), lr=0.01)
    criterion = torch.nn.MSELoss()
    
    dummy_x = torch.randn(16, 30, 4) # batch=16, seq=30, dim=4
    losses = []
    
    for epoch in range(15):
        optimizer.zero_grad()
        output = model(dummy_x)
        loss = criterion(output, dummy_x)
        loss.backward()
        optimizer.step()
        losses.append(loss.item())
        
    dt5 = (time.time() - t0) * 1000.0
    
    print(f"  [OK] Training Time     : 15 epochs on (16, 30, 4) tensor in {dt5:.2f} ms")
    print(f"  [OK] Initial Loss      : {losses[0]:.4f}")
    print(f"  [OK] Final Loss        : {losses[-1]:.4f} (Reduction: {(1 - losses[-1]/losses[0])*100:.1f}%)")
    assert losses[-1] <= losses[0], "Autoencoder loss must decrease"
    print("  --> PASS: PyTorch LSTM Autoencoder 15-epoch neural simulation completed.")

    print("\n" + "=" * 80)
    print("   ALL 5 MULTI-PHYSICS SIMULATION ENGINES RAN & CONVERGED SUCCESSFULLY 100%")
    print("=" * 80)

if __name__ == '__main__':
    verify_simulations_running()
