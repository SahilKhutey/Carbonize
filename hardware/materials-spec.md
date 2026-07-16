🔌 MATERIALS & ENCLOSURE SPECIFICATION — Reactor Internals
Task 5.3: Materials/enclosure considerations for reactor internals exposed to CO₂/SO₂/NOx-laden slurry
Owner: Hard-Tech Expert
Priority: 🟠 Medium (pilot is 6-12 months out, but materials decisions are long-lead)
DoD: Materials shortlist with cost/durability tradeoffs
Status: ✅ Complete

🎯 ENVIRONMENT SPECIFICATION
The reactor internals are exposed to:

Parameter	Range	Notes
pH	8-11	Alkaline, aggressive to aluminum, mild steel
Temperature	30-55°C	Moderate, but CA enzyme denatures >60°C
Slurry composition	Chitosan (1-5%), Ca(OH)₂ (1-3%), water, dissolved CO₂/SO₂/NOₓ	Abrasive + corrosive
Gas phase	CO₂, SO₂, NOₓ, water vapor	Acidic, condensing moisture
Velocity	0.1-0.3 m/s in slurry, 0.05-0.2 m/s in gas	Erosion risk
Solids content	5-15 wt%	Abrasive
Pressure	Atmospheric to +0.5 bar gauge	Low pressure
Temperature cycling	30→55→30°C daily, 100+ cycles	Thermal fatigue
Key challenge: Combine alkaline + acidic + abrasive environment.

🧪 MATERIALS SHORTLIST
1. REACTOR VESSEL
Material	Grade	Cost (₹/m²)	Corrosion Resistance	Durability (yr)	Recommended?
PP (Polypropylene)	Homopolymer, 10mm	₹2,800	🟢 Excellent (pH 1-14)	10-15	✅ PRIMARY
PPH (PP-H)	Natural, 12mm	₹3,200	🟢 Excellent	15-20	✅ Premium
PVDF (Polyvinylidene fluoride)	10mm	₹8,500	🟢 Outstanding (pH 0-14)	20-25	✅ Premium alternative
HDPE (High-density PE)	PE100, 10mm	₹3,800	🟢 Excellent	15-20	✅ For secondary vessels
PP-R (Random copolymer PP)	8mm	₹2,400	🟢 Excellent	8-12	✅ Budget option
316L Stainless Steel	-	₹18,000	🟡 Adequate (but pitting risk)	5-10	❌ Pitting at welds
Hastelloy C-276	-	₹85,000	🟢 Outstanding	25+	❌ Overkill + expensive
FRP (Fiberglass)	Vinyl ester	₹6,500	🟢 Excellent	15-20	✅ For large vessels
PVC-U	Class 1	₹2,200	🟢 Excellent (pH 1-14)	8-12	✅ Budget, but limited temp
RECOMMENDATION: PP-H (Polypropylene Homopolymer), 12mm wall

Reason	Details
Cost-effective	₹3,200/m² (vs ₹85K for Hastelloy)
Corrosion-proof	Inert to pH 1-14, SO₂, NOₓ, CO₂
Temperature range	-10°C to +100°C (covers our 30-55°C operating range)
Weldable	Hot gas welding is reliable and field-repairable
Food/pharma grade available	Important if pilot produces marketable blocks
Lifecycle	15-20 years in similar service
Fabrication method: CNC-cut pieces, hot-gas welded with extrusion welder.

2. IMPELLER / MIXER
Material	Cost (₹)	Suitability	Recommended?
PP coated 316L SS	₹8,500	🟢 Standard, well-proven	✅ PRIMARY
316L SS bare	₹6,000	🟡 Adequate (pitting risk)	❌ Pitting at welds
Hastelloy C-22	₹45,000	🟢 Outstanding	❌ Overkill
PVDF solid	₹12,000	🟢 Corrosion-proof	✅ For fully plastic
Titanium Gr.2	₹28,000	🟢 Excellent	❌ Overkill
Glass-lined steel	₹35,000	🟢 Outstanding	❌ Too expensive
RECOMMENDATION: PP-coated 316L SS impeller

Reason	Details
Standard marine-style impeller	Well-known geometry (e.g., A310, PBT4)
PP coating (3-5mm)	Protects SS from pitting
Magnetic coupling	Allows easy removal for cleaning
Speed: 100-200 RPM	Sufficient for 100L tank without shearing enzymes
Coupling: Magnetic drive (no shaft seal to leak)

3. MESH / MEMBRANE SUPPORT
Material	Form	Cost (₹/m²)	Chemical Resistance	Biofouling Risk	Recommended?
PP mesh	200 micron	₹3,500	🟢 Excellent	Medium (anti-fouling coating)	✅ PRIMARY
SS 316L mesh	100 micron	₹8,000	🟡 Good (pitting)	High	❌
PTFE mesh	100 micron	₹18,500	🟢 Outstanding	Low	✅ Premium
Nylon mesh	200 micron	₹2,800	🟡 Good (alkaline)	High	❌
PVDF mesh	100 micron	₹12,500	🟢 Excellent	Low	✅ Alternative
RECOMMENDATION: PP mesh, 200 micron opening, anti-fouling coated

Specification	Value
Material	Polypropylene (PP)
Opening	200 μm
Wire diameter	100 μm
Open area	~45%
Anti-fouling	Hydrophilic coating (e.g., hydrophilic PU coating)
Form	Wound cylindrical or pleated cartridge
Diameter	150 mm (for 100L tank)
Height	400 mm
Cost estimate: ₹4,200 for 6 mesh elements (annual replacement)

4. ENZYME IMMOBILIZATION SUBSTRATE
CRITICAL DECISION — affects enzyme stability and operating cost

Substrate	Form	CA Loading (mg/g)	Stability (°C)	pH Range	Reusability	Cost (₹/g)	Recommended?
Calcium alginate beads	2-3mm beads	5-10	<40°C	5-9	❌ 1-2 uses only	₹0.5	❌ Dissolves at pH>9
Chitosan beads (cross-linked)	2-3mm beads	15-30	<50°C	3-11	✅ 10-20 uses	₹1.2	✅ PRIMARY
Glutaraldehyde-cross-linked chitosan	2-3mm beads	20-40	<55°C	3-11	✅ 20-50 uses	₹1.5	✅ Best stability
Magnetic chitosan nanoparticles	100nm	30-50	<55°C	3-11	✅ 30+ uses	₹8.0	❌ Too expensive
Mesoporous silica (SBA-15)	Powder	10-20	<60°C	4-9	✅ 10-30 uses	₹5.0	❌ Brittle
Activated carbon (immobilized)	Granular	5-15	<45°C	5-9	❌ Fouling	₹0.3	❌
Sepabeads (commercial)	Beads	20-40	<55°C	4-10	✅ 20+ uses	₹25	❌ Very expensive
Chitosan-PVA cryogel	Sponge	15-25	<55°C	3-11	✅ 20+ uses	₹2.0	✅ GOOD ALTERNATIVE
RECOMMENDATION: Glutaraldehyde-cross-linked chitosan beads

Reason	Details
Excellent stability at pH 8-10	Covalent crosslinking resists alkaline dissolution
Survives 50°C for hours	Sufficient for our 40-50°C operation
Easy to manufacture	Lab-scale fabrication well-established
20-50 reuse cycles	Dramatically reduces operating cost
Cost-effective	₹1.5/g, scaleable
Fabrication recipe (1 kg batch):

Dissolve 20g chitosan in 1L 2% acetic acid
Add 10g CA powder, stir 1h
Extrude through 23G needle into 1M NaOH (forms beads)
Cross-link in 0.5% glutaraldehyde, 2h
Wash, sieve (2-3 mm), store at 4°C
Reactor bed: 1-2 kg beads in mesh basket inside reactor

Estimated enzyme cost: ₹1,500 initial + ₹500/month for replacement/replenishment

5. PIPING & VALVES
Component	Material	Size	Cost (₹)	Recommended?
Pipes (process)	PP-H	DN25-DN50	₹200/m	✅ PRIMARY
Pipes (gas)	PP-H	DN50-DN100	₹300/m	✅
Ball valves	PP	DN25	₹800	✅
Butterfly valves	PP	DN50-100	₹1,500	✅
Diaphragm valves	PP diaphragm, PTFE body	DN25	₹2,500	✅ For clean service
Check valves	PP	DN25	₹1,200	✅
Pressure gauges	SS316L diaphragm, PP case	0-1 bar	₹3,500	✅
Sight glasses	PP frame, glass	DN50	₹2,800	✅ For visual inspection
Total piping estimate: ₹35,000 for pilot

6. SEALING & GASKETS
Seal Type	Material	Application	Cost (₹)	Recommended?
O-rings	EPDM or FKM (Viton)	Vessel lid, instrument ports	₹200/each	✅ EPDM for our pH range
PTFE envelope gaskets	PTFE envelope with EPDM filler	Flanged connections	₹400/each	✅ For higher-pressure
Pure PTFE gaskets	Virgin PTFE	Critical joints	₹1,200/each	✅ For sensor mountings
Graphite gaskets	Flexible graphite	High-temp service	₹600/each	❌ Too brittle
Rubber gaskets	Natural rubber	Low pressure, low temp	₹100/each	❌ Not chemically resistant
Material choice: EPDM for general use (pH 8-11 OK, -50 to +150°C), FKM (Viton) for gas side (better SO₂ resistance).

7. INSTRUMENT CONNECTIONS
Connection	Type	Material	Cost (₹)	Recommended?
Sensor ports	Tri-clamp (sanitary)	PP/316L	₹1,200/each	✅ Easy sensor swap
Threaded	NPT/BSP	PP	₹300/each	✅ For permanent
Compression fittings	Swagelok-type	PP	₹1,500/each	✅ For easy removal
Flanged	ANSI/DIN	PP	₹1,800/each	✅ For DN50+
RECOMMENDATION: Tri-clamp connections for sensors (easy removal for cleaning/calibration)

🏗️ ENCLOSURE & SUPPORT STRUCTURE
8. PILOT SKID FRAME
Component	Material	Cost (₹)	Recommended?
Frame	Galvanized steel (powder-coated)	₹45,000	✅ PRIMARY
Frame	Stainless steel 304	₹1,20,000	❌ Overkill
Frame	Aluminum 6061	₹55,000	🟡 Lighter but less rigid
Panels	PP sheet, 6mm	₹12,000	✅ Splash guards
Enclosure (electrical)	SS304, IP65, 600x800x250mm	₹18,000	✅ For DAQ + PLC
Enclosure (control)	Polycarbonate, IP65	₹8,500	✅ For HMI
Total skid cost: ₹90,000

Dimensions: 1.5m × 0.8m × 1.8m (W × D × H), compact skid

💰 TOTAL MATERIALS COST SUMMARY
Category	Cost (₹)
Reactor vessel (PP-H, 100L)	25,000
Impeller (PP-coated 316L)	8,500
Mesh cartridges (PP, 6 pcs/yr)	4,200
Enzyme beads (chitosan cross-linked)	1,500 (initial) + 500/month
Piping + valves	35,000
Seals + fittings	8,000
Tri-clamp connections	6,000
Skid frame + enclosure	90,000
TOTAL ONE-TIME	₹1,78,700
Annual consumables	₹30,000 (beads + mesh)

🔬 CORROSION TESTING PROTOCOL
Before committing to PP, we should run a 30-day immersion test:

Sample	Material	Test Conditions	Duration	Pass Criteria
PP-H specimen	As specified	pH 9.5, 50°C, slurry	30 days	<2% mass loss, no cracking
PP-H welded joint	Hot gas welded	pH 9.5, 50°C	30 days	No delamination
316L SS	Bare	pH 9.5, 50°C, slurry + 500 ppm SO₂	30 days	No pitting visible
316L SS	PP coated (3mm)	pH 9.5, 50°C	30 days	No coating failure
EPDM O-ring	As specified	pH 9.5, 55°C	30 days	<10% compression set
Test plan: Place samples in operating reactor for 30 days, then inspect. Critical: validate before committing full budget.

🌡️ THERMAL CONSIDERATIONS
Concern	Mitigation
Enzyme denaturation > 55°C	Use water bath (PID-controlled, ±0.5°C)
Heat loss in winter	Insulate vessel with 50mm mineral wool
Local hot spots near mesh	Continuous agitation, baffles
Condensation in gas lines	Heat trace gas outlet to 5°C above dew point
Heating/Cooling System:

Heating: 1kW electric immersion heater (PID-controlled)
Cooling: Chilled water coil (chiller or cooling tower)
Operating window: 30-50°C
Control accuracy: ±0.5°C
Estimated cost: ₹85,000 (heater + chiller + control)

✅ TASK 5.3 DEFINITION OF DONE — VERIFICATION
 All material categories specified (vessel, impeller, mesh, enzyme, pipes, seals) ✓
 Part numbers or specs for each ✓
 Cost estimates for each component ✓
 Corrosion considerations documented ✓
 Recommended choices for each (with justification) ✓
 Tradeoff analysis (cost vs durability) ✓
 30-day corrosion test plan defined ✓
 Thermal management plan ✓
 Total cost summary ✓
 Manufacturability and serviceability addressed ✓

📊 DECISION MATRIX
Decision	Choice	Rationale
Vessel material	PP-H 12mm	Best cost/corrosion balance; proven in FGD service
Impeller	PP-coated 316L	Magnetic drive + PP coating; reliable
Mesh	PP 200μm with anti-fouling	Cost-effective; replaceable
Enzyme substrate	Glutaraldehyde-cross-linked chitosan	Best stability vs cost
Piping	PP-H	Same as vessel; consistency
Connections	Tri-clamp for sensors	Serviceability
Frame	Galvanized steel	Cost-effective, durable
Heating	Electric + chiller	Precise control
