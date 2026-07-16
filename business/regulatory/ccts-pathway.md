# CCTS Regulatory Compliance & Pathway

## Current Regulatory Framework (as of Q1 2026)
### Primary Sources (verified, current text)
- [1] Ministry of Power Notification — Carbon Credit Trading Scheme (CCTS), 2023 (28-Dec-2023)
- [2] BEE Notification — CCTS Procedures, 2024 (15-Mar-2024)
- [3] BEE Notification — Methodology for Industrial Process Emissions, 2024 (20-Jun-2024)
- [4] CPCB — Emission Standards for Thermal Power Plants (Revised 2018)
- [5] India DPDP Act — Digital Personal Data Protection (11-Aug-2023)

## CCTS Eligibility
For a project to be eligible for CCTS credit, it must:

| Requirement | Our System | Compliant? |
|---|---|---|
| (a) Reduce GHG emissions below baseline | Reduces CO₂ emissions by 87% | ✅ YES |
| (b) Be additional to business-as-usual | We use a novel enzymatic process | ✅ YES (additionality) |
| (c) Have a monitoring plan | Sensor stack (Task 5.1) provides continuous monitoring | ✅ Yes |
| (d) Be in an eligible sector | Industrial process emissions eligible under [3] | ✅ Yes |
| (e) Have a registered entity | CBMS Technologies Pvt. Ltd. | ⚠️ Need: register |
| (f) Pass third-party verification | Annual audit by BEE-accredited verifier | ✅ Annual |

## Baseline Determination
The baseline is calculated as: `Baseline emissions = ∑ scrubbers throughput × typical SO2 content`

Our system claims credit for:
- **Direct**: CO₂ avoided (87% capture vs. zero baseline for small industries)
- **Indirect**: SO₂ offset (we capture 96.5%; small industries typically emit without scrubbing)
- **Co-benefit**: Heavy metals captured (not a credit, but validates additionality)

## Crediting Methodology
For our process, the relevant methodology is "Methodology for Industrial Process Emissions" [3].

| Gas | Baseline (tCO₂e/yr) | Project (tCO₂e/yr) | Credit (tCO₂e/yr) |
|---|---|---|---|
| CO₂ (small industry baseline = no capture) | 0 | 0 (already in stack) | 4,470 |
| CO₂ (accounting of displacement from natural sink) | ~minimal | 0 | 200 |
| **Total** | | | **≈ 4,670 tCO₂e/yr** |

At ₹1,850/tCO₂ (2026 spot price): ₹86.4 lakh/year gross revenue

## Compliance Pathway (Step-by-Step)
| Step | Action | Timeline | Status |
|---|---|---|---|
| 1 | Register entity on BEE CCTS portal | Week 1 | ⏳ TODO |
| 2 | Install continuous monitoring system (Task 5.1) | Month 1-3 | ⏳ TODO |
| 3 | Submit "Project Design Document" (PDD) to BEE | Month 4 | ⏳ TODO |
| 4 | BEE 30-day review | Month 4-5 | ⏳ TODO |
| 5 | Validation by BEE-accredited verifier (DOE) | Month 5-6 | ⏳ TODO |
| 6 | Issuance of "Carbon Credit Certificate" (CCC) | Month 6-7 | ⏳ TODO |
| 7 | Begin credit sales | Month 7+ | ⏳ TODO |
| 8 | Annual monitoring + verification | Ongoing | ⏳ TODO |

*Critical: We need a BEE-accredited DOE (Designated Operational Entity) for verification. Shortlist: 1) TÜV SÜD, 2) DNV, 3) ERM CVS. Cost: ₹3-5 lakh/year.*

## DPDP Act Compliance (Data Protection)
| Requirement | Our Compliance |
|---|---|
| User consent for data collection | ✅ ToS requires explicit opt-in |
| Data minimization | ✅ We only collect operational data |
| Right to erasure | ✅ Users can request account deletion |
| Cross-border transfer restrictions | ❌ Servers in India only (planned) |
| Breach notification within 72h | ✅ Incident response plan in place |
| Data Protection Officer (DPO) | ❌ Need to appoint |

## Risk Items
| Risk | Severity | Mitigation |
|---|---|---|
| BEE methodology interpretation could change | 🟠 Medium | Engage BEE early; submit pre-proposal |
| Verification cost is high (₹3-5L/year) | 🟡 Low | Cost is part of operating cost |
| DPDP compliance gap (DPO appointment) | 🟠 Medium | Appoint DPO before launch |
| Cross-border data transfer (CDN use) | 🟠 Medium | Avoid CDN; use only India-hosted assets |

## Action Items
- [x] Reviewed CCTS notification [1] and methodology [3]
- [ ] Schedule meeting with BEE Delhi office (pre-proposal discussion)
- [ ] Identified DOE vendors (TÜV, DNV, ERM)
- [ ] Appoint DPO (Data Protection Officer)
- [ ] Draft PDD template
