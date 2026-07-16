# LICENSE POSTURE & IP HANDLING — CBMS-Sim Legal Framework

**Decision Date:** Q1 2026  
**Document Owner:** Project Team Lead (PTL) + Legal-Adjacent  
**Status:** Approved for publication  
**Scope:** All CBMS-Sim intellectual property, source code, documentation, and data  

---

## 🎯 Executive Summary
CBMS-Sim adopts a dual-tier license posture that balances:
*   **Open collaboration**: To attract contributors, researchers, and pilot partners.
*   **Trade secret protection**: To preserve competitive advantage in core IP.

*Core Principle:* Share the platform; protect the secret sauce.

---

## 📜 License Decision: Business Source License 1.1 (BSL 1.1)
We adopt the Business Source License 1.1 for the entire CBMS-Sim codebase.

| Alternative | Pros | Cons | Decision |
| :--- | :--- | :--- | :--- |
| **Open Source (MIT/Apache)** | Maximum adoption, easy contribution | No commercial protection, competitors can clone freely | ❌ Too permissive |
| **Closed Source** | Maximum protection | No community, slow development, hard to hire | ❌ Can't attract talent |
| **BSL 1.1** | Open source for non-production, converts to Apache 2.0 after 3 years | Slightly more complex, requires legal review | ✅ Selected |
| **SSPL (Server Side Public License)** | Strong copyleft | Discourages adoption, complex compliance | ❌ Too restrictive |
| **Dual License (AGPL + Commercial)** | Clear commercial path | AGPL is viral, scares enterprise | ❌ Reputational risk |

BSL 1.1 gives us:
*   Source-available for inspection, contribution, and non-production use.
*   Permissive for academic research and pilot projects.
*   Production use requires a commercial license.
*   Automatic conversion to Apache 2.0 after 3 years (February 14, 2028).

---

## 🗂️ Asset Classification (Shareable vs. Trade Secret)

### Tier 1: PUBLIC (Open Source / Shareable)
*License:* BSL 1.1 (non-production use)  
*Distribution:* Public GitHub repo, public docs site, published papers  
*   Source code (entire codebase)
*   Documentation (`docs/`, `manuscript/`)
*   Scientific papers and preprints (after journal embargo)
*   Anonymized, non-proprietary test data
*   Validation cases (published data)
*   API documentation (OpenAPI spec)

### Tier 2: CONTROLLED (Share with Caution)
*License:* BSL 1.1 + written agreement  
*Distribution:* Specific named collaborators, with NDA  
*   Customer-specific simulation results
*   Raw pilot data from industrial partners
*   Detailed cost models (vendor pricing redacted)
*   Investor due diligence materials (under NDA)

### Tier 3: TRADE SECRET (Never Share)
*License:* Proprietary, protected as trade secret  
*Distribution:* Only to employees with NDA + need-to-know  
*   Proprietary reaction kinetics coefficients (beyond published literature)
*   Cost-optimized reagent formulations (specific supplier combinations)
*   Pilot plant operational parameters and proprietary tuning
*   Unpublished bench-scale experimental data
*   Internal financial models and cap tables

---

## 🤝 Contributor License Agreement (CLA)

By submitting a pull request, you agree that:
*   You retain copyright to your contributions.
*   You grant CBMS Technologies a non-exclusive, perpetual, irrevocable, worldwide, royalty-free license to use, reproduce, modify, distribute, and sublicense your contributions.
*   Your contributions are licensed under BSL 1.1.

We use **CLA Assistant** to automate this check.

---

## ™️ Trademark Policy

### Protected Marks
*   "CBMS-Sim" (product name)
*   "CBMS" (company abbreviation)
*   "Coral-Inspired Biomineralization Capture"
*   CBMS logo (visual identity)

### Usage Rules
*   **Allowed**: Reference in academic papers, conference talks, and non-production fork usage.
*   **Prohibited**: Competing product branding, marketing usage without approval, and domain names containing "cbms".
