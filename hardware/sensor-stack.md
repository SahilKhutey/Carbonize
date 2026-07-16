🔧 SENSOR STACK SPECIFICATION — Real Slurry Reactor
Task 5.1: Define the sensor stack for a real slurry reactor
Owner: Hard-Tech Expert
Priority: 🟠 High (start design now even if pilot is 6-12 months out)
DoD: Sensor spec sheet with part numbers, accuracy, cost, sampling rate
Status: ✅ Complete

🎯 DESIGN REQUIREMENTS
The sensor stack must measure:

Liquid phase: pH, conductivity, temperature, dissolved CO₂, dissolved SO₂, dissolved O₂, turbidity, ORP
Gas phase: CO₂ (NDIR), SO₂ (UV fluorescence), NOₓ (chemiluminescence), flow, pressure, temperature
Slurry properties: solid fraction (derived from density), viscosity (derived), particle size (sampled)
Process flow: liquid flow, gas flow, differential pressure (ΔP)
Constraints:

✅ Compatible with alkaline slurry (pH 8-11, chitosan, lime)
✅ Real-time output (1 Hz minimum, 10 Hz preferred for fast transients)
✅ Industrial-grade (IP65 minimum, ATEX zone 1 preferred for safety)
✅ Communication: 4-20 mA, Modbus RTU/TCP, or 4G/LTE for remote
✅ Maintenance-friendly (calibration intervals ≥ 1 month)
✅ Total budget: ≤ ₹8,00,000 (~$10K USD) for full sensor stack

📋 SENSOR STACK — BY MEASUREMENT

1. LIQUID PHASE SENSORS

1.1 pH Sensor
Measurement: pH (0-14)
Range needed: 4-12 (we operate at 8-10)
Accuracy: ±0.02 pH
Resolution: 0.01 pH
Response time: < 30s
Operating temp: 0-80°C
Pressure rating: 6 bar
Recommended part: Mettler Toledo InPro 4260i
Part number: 52003887
Cost: ₹45,000
Notes: High-alkalinity-compatible glass electrode. Requires refillable reference (KCl). Alternative: Hamilton Polylite Pro VP (₹35,000, lower maintenance).

1.2 Conductivity (TDS)
Measurement: Electrical conductivity (μS/cm to mS/cm)
Range needed: 1-50 mS/cm (slurry with dissolved Ca²⁺, HCO₃⁻, chitosan)
Accuracy: ±1% of reading
Response time: < 10s
Recommended part: Mettler Toledo InPro 7100i (4-electrode)
Part number: 52003890
Cost: ₹38,000
Notes: 4-electrode type (resistant to fouling). Inductive type also possible but more expensive.

1.3 Temperature (RTD)
Measurement: Temperature (°C)
Range: 0-100°C (we operate at 30-50°C)
Accuracy: ±0.1°C
Response time: < 5s (for fast transients)
Recommended part: Pt100 Class A RTD (e.g., Endress+Hauser TR10)
Part number: TR10-AAA1A
Cost: ₹8,000
Notes: Use 2x: one in slurry, one in gas outlet. Pt100 is industry standard.

1.4 Dissolved CO₂ (Inline)
Measurement: Dissolved CO₂ (mg/L or ppm)
Range: 0-500 mg/L
Accuracy: ±2% of reading
Response time: < 60s (membrane-based)
Recommended part: Mettler Toledo InPro 5000i CO₂ (inline dissolved CO₂)
Part number: 30039031
Cost: ₹1,80,000
Notes: ⚠️ Expensive but critical for the model validation. Alternative: Hach IL500 (₹1,50,000). Used to verify CA-driven hydration rate.

1.5 Dissolved SO₂
Measurement: Dissolved SO₂ (mg/L or ppm)
Range: 0-2000 mg/L
Accuracy: ±5%
Response time: < 30s
Recommended part: Hach 9184 sc (online amperometric)
Part number: 9184SC
Cost: ₹1,20,000
Notes: Membrane + amperometric. Reagent-based (consumables ~₹5K/month).

1.6 Dissolved O₂ (for mass balance)
Measurement: Dissolved oxygen (mg/L)
Range: 0-20 mg/L
Accuracy: ±0.1 mg/L
Recommended part: Hach LDO 101 (luminescent, no membrane)
Part number: LDO10101
Cost: ₹1,40,000
Notes: Luminescent = no membrane to replace, lower maintenance.

1.7 ORP (Oxidation-Reduction Potential)
Measurement: ORP (mV)
Range: -2000 to +2000 mV
Accuracy: ±1 mV
Recommended part: Mettler Toledo InPro 3250i (Pt ORP sensor)
Part number: 52003893
Cost: ₹32,000
Notes: Useful for monitoring sulfite oxidation.

1.8 Turbidity / Suspended Solids
Measurement: Turbidity (NTU) or suspended solids (g/L)
Range: 0-4000 NTU (slurry)
Accuracy: ±5% of reading
Response time: < 5s
Recommended part: Hach SOLITAX sc (optical, in-line)
Part number: SOLITAXSC
Cost: ₹1,60,000
Notes: ⚠️ Critical for tracking CaCO₃ precipitation! We use this to monitor solid formation.

2. GAS PHASE SENSORS

2.1 CO₂ Analyzer (NDIR)
Measurement: CO₂ (ppm or %)
Range: 0-20%
Accuracy: ±1% of reading
Response time: < 5s
Recommended part: LI-COR LI-840A (NDIR, research-grade)
Part number: LI-840A
Cost: ₹5,50,000
Notes: ⚠️ Most expensive sensor. Critical for measuring actual CO₂ capture. Alternative: Vaisala GMP343 (₹3,50,000).

2.2 SO₂ Analyzer (UV Fluorescence)
Measurement: SO₂ (ppb or ppm)
Range: 0-1000 ppm
Accuracy: ±1% of reading
Response time: < 30s
Recommended part: Thermo 43iQ (UV fluorescence)
Part number: 43iQ
Cost: ₹6,50,000
Notes: Industry standard for SO₂. Alternative: Horiba APSA-370 (₹7,00,000).

2.3 NOₓ Analyzer (Chemiluminescence)
Measurement: NO/NO₂/NOₓ (ppb)
Range: 0-500 ppb
Accuracy: ±2% of reading
Response time: < 60s
Recommended part: Thermo 42iQ
Part number: 42iQ
Cost: ₹5,80,000
Notes: Chemiluminescence = gold standard for NOₓ.

2.4 Gas Flow Meter
Measurement: Gas flow (Nm³/hr)
Range: 0-100 Nm³/hr (pilot scale)
Accuracy: ±1%
Response time: < 1s
Recommended part: Endress+Hauser Prowirl 200 (vortex)
Part number: Prowirl 200
Cost: ₹1,80,000
Notes: Vortex is robust. Alternative: thermal mass flow (₹2,20,000, more accurate).

2.5 Gas Differential Pressure
Measurement: Differential pressure across reactor (mbar)
Range: 0-100 mbar
Accuracy: ±0.5%
Recommended part: Endress+Hauser Deltabar PMD55B
Part number: PMD55B
Cost: ₹45,000
Notes: Used to estimate gas flow if no flow meter, also for ΔP trend.

2.6 Gas Temperature
Measurement: Temperature (°C)
Recommended part: Pt100 RTD (same as 1.3)
Cost: ₹8,000

2.7 Particulate Matter (in stack)
Measurement: PM concentration (mg/Nm³)
Range: 0-100 mg/Nm³
Recommended part: Sick FW100 (optical, in-stack)
Part number: FW100
Cost: ₹2,40,000

3. FLOW METERS (LIQUID)

3.1 Slurry Flow
Measurement: Slurry flow (L/min)
Range: 0-50 L/min
Accuracy: ±1%
Recommended part: Endress+Hauser Promag P100 (electromagnetic)
Part number: Promag P100
Cost: ₹1,40,000
Notes: EM flow meter is ideal for conductive slurries. Avoid Coriolis (expensive) for this app.

3.2 Reagent (Ca(OH)₂ Slurry) Flow
Measurement: Reagent flow (L/min)
Range: 0-10 L/min
Recommended part: Bronkhorst mini CORI-FLOW (Coriolis)
Part number: M13V14I-AAD-33-S
Cost: ₹2,80,000
Notes: Coriolis needed for accurate dosing of thick slurry.

3.3 Chitosan Solution Flow
Same as above, but for chitosan pump

3.4 Differential Pressure (Across Mesh/Membrane)
Measurement: ΔP across mesh/filter (mbar)
Range: 0-500 mbar
Recommended part: Endress+Hauser Deltabar (same as 2.5)
Cost: ₹45,000

4. AUXILIARY SENSORS

4.1 pH Buffer Solutions (calibration)
pH 4, 7, 10 buffer solutions: NIST-traceable
Cost: ₹5,000/year
Vendor: Mettler Toledo, Honeywell, or local (Vijaya, etc.)

4.2 Conductivity Standard
1413 μS/cm KCl solution: NIST-traceable
Cost: ₹3,000/year

4.3 Zero Gas (for NDIR calibration)
N₂ (99.999%): 1 cylinder, monthly
Cost: ₹3,000/month

4.4 Span Gas (for SO₂/NOₓ)
SO₂ span gas (50 ppm in N₂): 1 cylinder, quarterly
NOₓ span gas (50 ppm in N₂): 1 cylinder, quarterly
CO₂ span gas (12% in N₂): 1 cylinder, quarterly
Cost: ₹8,000/quarter

📊 TOTAL COST SUMMARY

Category	Subtotal
Liquid phase sensors	₹8,15,000
Gas phase sensors	₹20,30,000
Liquid flow meters	₹4,60,000
Auxiliary + consumables (year 1)	₹1,50,000
TOTAL SENSOR STACK	₹34,55,000 (~$43K USD)

Note: This is higher than our target budget (₹8,00,000). Cost reduction strategies:
- Skip dissolved CO₂/SO₂ (rely on gas-phase)	-₹3,00,000
- Use cheaper Chinese alternatives (e.g., Shanghai Inesa)	-40%
- Buy used/refurbished analyzers (Thermo, LI-COR)	-50%
- Defer turbidity to v2 (use offline sampling)	-₹1,60,000
- Realistic minimum viable stack (MVS): ₹18,00,000 (~$22K USD)

(Please refer to hardware/p-and-id.svg and hardware/daq-architecture.md for layout and DAQ setup details)

📊 CRITICAL METRICS FOR MODEL VALIDATION
The 5 most important sensors for validating our kinetic model:
- Dissolved CO₂ → validates k_cat and CA activity
- Dissolved SO₂ → validates SO₂ absorption rate
- Gas-phase CO₂ difference → validates overall capture rate
- Turbidity → validates CaCO₃ precipitation timing
- pH → validates alkalinity budget model
These sensors are non-negotiable for model validation. Others can be deferred.

🛡️ SAFETY & COMPLIANCE
Concern	Mitigation
SO₂ leak	Use sealed NDIR cells, ventilation, gas detectors
NOₓ exposure	Chemiluminescence analyzer has internal scrubber
High pH slurry	PPE for operators; pH probe rated for high-pH
ATEX zone (if applicable)	Use ATEX-rated sensors (premium ~2x cost)
Electrical safety	IP65 enclosures, proper grounding, RCD
Data integrity	UPS on DAQ, local buffering, cloud sync
