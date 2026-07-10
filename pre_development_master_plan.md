# 🏗️ Pre-Development Master Plan: Coral-Inspired Biomineralization Capture System (CBMS)

This document establishes the pre-development framework for the **Coral-Inspired Biomineralization Capture System (CBMS)**, outlining the validation strategy, risk assessment, compliance mapping, timeline, and technical readiness gates prior to full-scale engineering and code development.

---

## 1. Project Overview & Vision Statement

### 1.1 Project Codename
**CBMS** — *Coral-inspired Biomineralization Multi-Pollutant Solidification System*

### 1.2 Mission Statement
To develop a commercially viable, low-CAPEX industrial emissions control technology that simultaneously captures $\text{CO}_2$, $\text{SO}_2$, $\text{NO}_x$, heavy metals, and particulate matter into a sellable, construction-grade solid product—eliminating the geological storage dependency of conventional carbon capture while providing Indian mid-market industries with a turnkey retrofit solution.

### 1.3 Vision Statement (5-Year Horizon)
By 2030, deploy 25 CBMS units across Indian thermal power, cement, and steel facilities, capturing 500,000 tonnes of $\text{CO}_2$-equivalent annually and producing 2 million construction blocks from captured waste streams, while establishing India as a global leader in biomineralization-based pollution control.

### 1.4 Core Differentiators
| Differentiator | Value |
| :--- | :--- |
| **Multi-pollutant integration** | Single unit addresses 5 pollutant classes simultaneously |
| **Solid product output** | Eliminates geological aquifer storage dependencies |
| **Low CAPEX** | ~40% of standard electrocatalytic or MOF-based alternatives |
| **Indigenous supply chain** | Chitosan sourced from Indian coastal seafood biowaste |
| **CCTS revenue** | Dual revenue from Indian CCTS carbon credits + block sales |
| **Modular design** | Scalable configurations from 1,000 to 100,000 $\text{Nm}^3/\text{hr}$ |

---

## 2. Pre-Development Objectives

The pre-development phase (Months 0–6) focuses on establishing four primary objectives:

### 2.1 Objective Matrix
| # | Objective | Success Criterion | Validation Method |
| :--- | :--- | :--- | :--- |
| **O-1** | Validate core chemistry assumptions | 3 critical experiments completed with published data | Lab reports + peer review |
| **O-2** | Establish regulatory pathway | CPCB/CCTS pre-consultation complete; framework agreement signed | Meeting minutes + MoU |
| **O-3** | Secure IP position | 1 provisional patent filed + 2 freedom-to-operate analyses | Patent office receipts |
| **O-4** | Build credible simulation | Framework produces results validated against literature to $\pm 15\%$ | Benchmark testing |

### 2.2 Pre-Development "No-Go" Criteria
The project will halt or pivot if:
1.  Chitosan degrades $>50\%$ in 24 hours under simulated flue gas conditions (**O-1 Fail**).
2.  CPCB rules block solid waste product commercialization (**O-2 Fail**).
3.  UrjanovaC or competitor patents create an unresolvable blocking IP position (**O-3 Fail**).
4.  Simulation deviates $>30\%$ from published biomineralization rates (**O-4 Fail**).

---

## 3. Stakeholder & Team Structure

### 3.1 Core Team Requirements (Minimum Viable)
| Role | FTE | Core Responsibility | Required Expertise |
| :--- | :--- | :--- | :--- |
| **Principal Investigator** | 1.0 | Technical direction, publication strategy | PhD ChemEng/MatSci, 10+ yr experience |
| **Senior Process Engineer** | 1.0 | Reactor design, P&ID, scale-up | M.Tech ChemEng, 5+ yr experience |
| **Biochemist/Enzymologist** | 0.5 | CA characterization, stability testing | PhD Biochemistry |
| **Materials Scientist** | 0.5 | Chitosan modification, block characterization | PhD Polymer/Materials Science |
| **CFD/Modeling Engineer** | 1.0 | Simulation framework, digital twin | M.Tech Mech/ChemEng + CFD expertise |
| **Regulatory Affairs Lead** | 0.5 | CPCB/CCTS, EIA, compliance mapping | M.Sc Env Policy + 5 yr experience |
| **Lab Technician** | 1.0 | Bench experiments, sample prep | B.Sc Chemistry |
| **IP/Patent Attorney** | 0.2 | Patent filing, FTO analysis | Indian Patent Agent (Retainer) |

**Total Core Team:** 5.7 FTE

```
                    ┌─────────────────────────────┐
                    │    STEERING COMMITTEE        │
                    │  (Quarterly Review)          │
                    └──────────────┬──────────────┘
                                   │
                    ┌──────────────▼──────────────┐
                    │   PRINCIPAL INVESTIGATOR    │
                    │   (Weekly Sync)             │
                    └──────────────┬──────────────┘
                                   │
        ┌──────────────┬───────────┼───────────┬──────────────┐
        ▼              ▼           ▼           ▼              ▼
  ┌──────────┐  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
  │ Process  │  │Bio/Mat   │ │ CFD/     │ │Regulatory│ │  IP/Legal│
  │ Engineer │  │Science   │ │Modeling  │ │ & BizDev │ │ (External│
  │          │  │          │ │          │ │          │ │Retainer) │
  └──────────┘  └──────────┘ └──────────┘ └──────────┘ └──────────┘
        │              │           │           │              │
        └──────────────┴───────────┴───────────┴──────────────┘
                                   │
                    ┌──────────────▼──────────────┐
                    │   LAB TECHNICIAN (Shared)   │
                    └─────────────────────────────┘
```

---

## 4. Validation Strategy

### 4.1 Four-Tier Validation Pyramid
```
                         /\
                        /  \        TIER 3
                       / PILOT\     Industrial Pilot
                      /  (Yr2) \    (1:1 scale, 1000 Nm³/hr)
                     /──────────\
                    / BENCH      \  TIER 2
                   /  PROTOTYPE   \ Lab Prototype
                  /   (1:100, ~6mo)\ (10 L reactor)
                 /─────────────────\
                / CRITICAL          \  TIER 1
               /  EXPERIMENTS        \ Bench-Scale
              /   (100 mL, 3-6 mo)    \ Validation
             /─────────────────────────\
            /  LITERATURE              \  TIER 0
           /   SIMULATION               \ Computational
          /    (Current Phase)           \ Foundation
         /────────────────────────────────\
```

### 4.2 Validation Phase Gates
| Phase | Duration | Entry Criteria | Exit Criteria |
| :--- | :--- | :--- | :--- |
| **T0: Simulation** | 2 months | Literature parameters compiled | Framework validated $\pm 15\%$ vs. published data |
| **T1: Critical Experiments** | 3 months | T0 exit + lab access secured | All 3 critical experiments completed successfully |
| **T2: Bench Prototype** | 4 months | T1 exit + chitosan survives 7 days | Prototype runs continuously for 72 hours |
| **T3: Pilot Design** | 3 months | T2 exit + industry partner LOI | Complete engineering design package |

---

## 5. Risk Assessment Matrix

### 5.1 Comprehensive Risk Register
| ID | Category | Specific Risk | Prob. | Impact | Score | Mitigation Strategy |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **R-01** | Technical | Chitosan degrades in flue gas conditions | High | Critical | 9.0 | Modify with cross-linkers (glutaraldehyde, genipin); explore alternative biopolymers (alginate) |
| **R-02** | Technical | CA enzyme cost prohibitive at scale | High | High | 8.5 | Source thermophilic bulk CA; explore recombinant *E. coli* expression; design enzyme recovery loops |
| **R-03** | Technical | Heavy metals leach from cured blocks | Med | Critical | 8.0 | Add post-treatment immobilization layers (phosphate coating); verify TCLP parameters early |
| **R-04** | Technical | Gel formation clogs mesh screens | Med | High | 7.5 | Optimize ultrasonic demolding cycles; test alternative column geometries |
| **R-05** | Technical | Block strength $<5\text{ MPa}$ (substandard) | Med | High | 6.0 | Optimize press force, curing temp, and ash ratio; add OPC supplements |
| **R-06** | Regulatory | CPCB rules block waste-to-product classification | Med | Critical | 8.5 | Early pre-consultation; design for "co-product" status; hazardous waste compliance audits |
| **R-07** | Regulatory | CCTS credits denied for mineralization pathway | Med | High | 7.0 | Engage CCTS verifier early; align with CCTS methodology guidelines |
| **R-08** | IP | Competitor patent blocks market entry | Med | High | 6.0 | Comprehensive FTO analysis; design-around IP; focus on different mechanism claims |
| **R-09** | Financial | DST/SIDBI funding delayed $>6$ months | High | Med | 6.0 | Parallel applications to BIRAC, NIDHI, Atal Innovation Mission; secure bridge funding |

---

## 6. Regulatory & Compliance Mapping

### 6.1 Indian Regulatory Framework
| Authority | Regulation | Relevance | Engagement Strategy |
| :--- | :--- | :--- | :--- |
| **CPCB** | Air Act, 1981 | Stack emission limits | Pre-consultation meeting Q1 |
| **CPCB** | Hazardous Waste Rules, 2016 | Co-product vs. waste classification | Legal opinion + pre-application |
| **MoEFCC** | EIA Notification, 2006 | Environmental clearance | Verify EIA exemptions for R&D pilot plants |
| **BEE** | PAT Scheme | Energy efficiency credits | Register as PAT compliance measure |
| **CCTS** | Carbon Trading Scheme, 2024 | $\text{CO}_2$ credit generation | Methodology submission Q3 |
| **BIS** | IS 2185 / IS 1077 | Block strength certification | Sample testing at BIS labs Q4 |

---

## 7. Technical Readiness Gates (TRL Roadmap)

```
TRL 1 (Basic Principles) ──> TRL 2 (Concept) ──> TRL 3 (Proof of Concept) ──> TRL 4 (Lab Component Validation)
                                                   ▲
                                             (Current Stage)
```
*   **Current Assessment:** The integrated system sits at **TRL 2--3** (conceptualized architecture, parameterized simulation framework).
*   **Target TRL at Pre-Development End:** **TRL 4--5** (bench component verification and 72-hour continuous test runs).

---

## 8. Critical Experiments Protocol

### 8.1 Experiment Overview
1.  **CE-1: Chitosan Stability Protocol:** Expose $3.0\text{ wt}\\%$ chitosan solutions to simulated flue gas ($14\%\text{ CO}_2, 1200\text{ mg/Nm}^3\text{ SO}_2$) at $40^\circ\text{C}$ to evaluate molecular weight retention via GPC.
2.  **CE-2: Carbonic Anhydrase Activity:** Measure $k_{\text{cat}}$ in viscous chitosan slurries using stopped-flow spectroscopy.
3.  **CE-3: TCLP Leach Testing:** Perform EPA Method 1311 on crushed block samples to ensure lead, mercury, and cadmium concentrations remain below regulatory limits.
4.  **CE-4: Multi-Pollutant Bench Capture:** Verify simultaneous capture of $\text{CO}_2$, $\text{SO}_2$, and particulates inside a 10L bubble column.
5.  **CE-5: Strength Optimization:** Box-Behnken design mapping press forces (100–300 bar) and ash ratios to maximize composite compressive strength.

---

## 9. Budget & Funding Pipeline

### 9.1 Budget Summary (12-Month Pre-Development)
*   **Personnel (5.7 FTE):** ₹45,00,000
*   **Critical Experiments (CE-1 to CE-5):** ₹15,80,000
*   **Equipment & Consumables:** ₹14,00,000
*   **IP, Legal & Regulatory:** ₹8,50,000
*   **Compute, Travel & Contingency:** ₹12,10,000
*   **TOTAL BUDGET:** **₹95,40,000** (~$114,000 USD)

### 9.2 Funding Pipeline
*   **DST-NIDHI PRISM:** ₹20,00,000 (Month 1 Application)
*   **BIRAC BIG:** ₹30,00,000 (Month 3 Application)
*   **DST CERI:** ₹50,00,000 (Month 2 Application)
*   **Founders / Angel Bridge:** ₹15,00,000–₹45,00,000 (To cover gaps)

---

## 10. Pre-Development Deliverables Checklist

### 10.1 Documentation & Physical Deliverables
*   `[ ]` Literature review compilation (Annotated bibliography, 50+ papers) — **Due M1**
*   `[ ]` System architecture specification (50 pp engineering doc) — **Due M2**
*   `[ ]` Provisional Patent P-1 (Matrix composition) filed — **Due M2**
*   `[ ]` Freedom-to-Operate (FTO) analysis complete — **Due M3**
*   `[ ]` CE-1 (Chitosan stability) final report — **Due M5**
*   `[ ]` CE-2 (Enzyme kinetics) final report — **Due M6**
*   `[ ]` Bench prototype 72-hour continuous test report — **Due M9**
*   `[ ]` Signed industry partner Letters of Intent (LOI) — **Due M9**

---

## 🚀 Immediate Next Steps (First 30 Days)

### Week 1
*   [ ] Initialize recruitment postings for core technical roles (Senior Process Engineer, Biochemist).
*   [ ] Draft the lab access and collaboration MoU templates for target academic institutions (IIT Bombay CCU CoE, IISc).
*   [ ] Establish the literature review reference database.

### Week 2
*   [ ] Refine claims and prepare the disclosure document for Patent P-1 (Biopolymer matrix composition).
*   [ ] Issue formal Freedom-to-Operate search requests to the IP retainer attorney.

### Week 3
*   [ ] Submit pre-consultation request letters to the State Pollution Control Board.
*   [ ] Prepare draft proposals for DST-NIDHI PRISM funding.

### Week 4
*   [ ] Conduct first-round interviews for technical roles.
*   [ ] Convene the initial advisory board alignment meeting.
