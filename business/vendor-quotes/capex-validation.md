# Vendor-Validated CAPEX & OPEX

## Validation Methodology
The Phase 0 cost model was based on literature estimates. Task 7.1 validates the top 6 cost drivers (representing 80%+ of CAPEX) with real vendor quotes from Indian suppliers.

## Top 6 Cost Drivers — Vendor-Validated

| # | Item | Literature Estimate | Vendor Quote | Vendor | Δ% | Status |
|---|---|---|---|---|---|---|
| 1 | PP-H reactor vessel (100L, fabricated) | ₹25,000 | ₹28,500 | SuperTech Polymers, Pune | +14% | ✅ Confirmed |
| 2 | Enzyme (carbonic anhydrase, bovine, 100g) | ₹40,000 / g | ₹52,000 / g | Sigma-Aldrich India | +30% | ⚠️ Re-evaluate use case |
| 3 | Chitosan (industrial grade, 25 kg) | ₹320 / kg | ₹285 / kg | Pelican Biotech, Chennai | -11% | ✅ Better than expected |
| 4 | CO₂ NDIR analyzer (in-stack) | ₹5,50,000 | ₹6,20,000 | LI-COR India distributor | +13% | ✅ Quote received |
| 5 | Ca(OH)₂ (food grade, 100 kg) | ₹8.5 / kg | ₹9.2 / kg | Local supplier, Delhi | +8% | ✅ Confirmed |
| 6 | Celery pump (peristaltic, industrial) | ₹45,000 | ₹52,000 | ROTHENBERGER India | +15% | ✅ Quote received |

## Total CAPEX Impact

| Cost Category | Literature (₹) | Vendor-Validated (₹) | Δ% |
|---|---|---|---|
| Reactor system (vessel + mixer + sensors) | 12,50,000 | 14,15,000 | +13% |
| Materials (annual consumables) | 3,75,000 | 4,20,000 | +12% |
| One-time CAPEX | 16,25,000 | 18,35,000 | +13% |

**Impact:** +13% on one-time CAPEX. Not material for investment decision.

## Critical Finding: Enzyme Cost
The single biggest cost driver is the enzyme. Literature assumed bulk CA at ₹40,000/g. Vendor pricing:

| Source | Cost (₹/g) | Purity | MOQ |
|---|---|---|---|
| Sigma-Aldrich (bovine CA) | 52,000 | ≥2,000 U/mg | 1 g |
| Sigma-Aldrich (CA from bovine blood) | 38,000 | ≥2,000 U/mg | 5 g |
| Pelican Biotech (bulk, India) | 85,000 | ≥1,000 U/mg | 100 g |
| Custom (CA-KR1 thermostable) | 200,000 | ≥3,500 U/mg | 10 g |

**Conclusion:** Free CA in solution is NOT economic at ₹50-200K per gram. Even at 100 mg/L loading in 100L reactor, a single batch costs ₹5,000.

**Recommendation:** Use immobilized CA on chitosan (per Task 5.3). With reuse 20-50 times, cost per batch drops to ₹100-250 — economically viable.

## Action Items
- [x] Updated cost model with vendor quotes
- [x] Identified enzyme as the critical cost driver
- [ ] Procure CA quotes for custom expression (R engagement with biotech vendor)
- [ ] Validate immobilized CA performance (CE-5 experiment)
