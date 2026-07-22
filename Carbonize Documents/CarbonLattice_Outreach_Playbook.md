# CarbonLattice / CBMS-Sim — Outreach Playbook
*Repo analyzed: github.com/SahilKhutey/Carbonize · Compiled July 2026*

---

## 1. What the repo actually signals to an outsider

CBMS-Sim is a coral-inspired biomineralization simulator for multi-pollutant industrial capture (CO2, SO2, NOx, heavy metals, PM), built as a proper SaaS stack — React front end, FastAPI backend, Celery workers, a Numba-based stiff ODE solver for the core sim, Terraform for deployment, plus uncertainty quantification (Latin Hypercube Sampling, Sobol sensitivity, First Passage Time stochastic models) and full techno-economic modeling (CAPEX/OPEX, CCTS credits, NPV, payback).

That's a strong signal for a technical audience: it reads as a founder who can build the full pipeline, not just the chemistry slide. Three things to fix before you send this repo to anyone external:

- **The repo is legally closed but structurally open.** The README states "Copyright (c) 2026 Sahil Khutey. All Rights Reserved" — good — but the repo itself is public with 0 stars/forks and visible file names like "Google Gemini" outputs. Investors and mentors *will* open the repo. Move AI-tool-branded working files (the Gemini-titled PDFs) into a private folder or rename them; they read as unpolished internal scratch, not IP.
- **No README section for outsiders.** There's no "Traction," "Team," "Status/TRL," or "Contact" section. Add 5–6 lines at the top stating what stage you're at (simulation/pre-development), what's been validated (bench trials, customer interviews), and a contact email — this is what a VC associate scans for in the first 20 seconds.
- **Solo commit history (3 commits) will raise a "can this person execute at scale" question**, not a "is the science real" question. That's actually good news — it means your gap is *team*, not *credibility*, which lines up with your active YC co-founder search.

---

## 2. Reality check on where you fit today

Be honest with yourself about stage before you reach out — it changes who says yes:

- You're **pre-seed, pre-prototype-at-scale**: strong simulation + techno-economic model + early customer discovery, no pilot deployment yet.
- Most **global accelerators** (Third Derivative, Elemental Excelerator) require a working prototype at **TRL 4+ and 2+ full-time employees** — you likely don't clear that bar solo yet. Don't let a rejection there read as a signal about the tech; it's a stage mismatch.
- Your best near-term wins are **India-based, deep-tech-friendly, pre-prototype programs** (SINE-IIT Bombay, CIIE.CO, AGNIi, Climate Collective) and **individual mentors/PIs**, not big-check VCs.
- Landing a co-founder *before* your next major outreach round will materially improve your odds everywhere else — investors and incubators will ask about team composition immediately.

---

## 3. Contact list

### A. Mentorship (technical + domain)

| Who | Why them | How to reach |
|---|---|---|
| **Prof. Vikram Vishal**, IIT Bombay — leads India's first Integrated CCUS Field Laboratory, co-founder of UrjanovaC (DST National Centre of Excellence in Carbon Capture & Utilization) | Closest domain-matched academic in India; his lab is now the literal national CCUS testbed. He's the single best-fit technical mentor for CarbonLattice. | IIT Bombay faculty directory (Earth Sciences/CCUS), LinkedIn InMail, or via SINE IIT Bombay introduction (below) |
| **Arnab Dutta**, co-founder of UrjanovaC (SINE-incubated CCUS startup, same NCoE ecosystem) | A founder-mentor who has *just* walked the exact "IIT lab tech → CCUS venture" path you're on — most relatable mentor on this list. | LinkedIn |
| **NCoE-CCU IIT Bombay (DST-funded Centre)** | Government-backed centre with an explicit mandate to build researcher/industry/startup networks in CCU — designed for exactly this kind of outreach. | Email via DST/IIT Bombay CCU centre page; ask specifically for mentorship or bench-testing collaboration, not funding |
| **Ostara Advisors — Vasudha Madhavan (CEO)** | One of India's first climate-tech-focused investment banks; she speaks publicly and precisely about what Indian climate-tech investors actually want to see (execution clarity, unit economics) — valuable pitch-sharpening mentor even before you fundraise. | LinkedIn, firm website contact form |
| **Theia Ventures — Priya (General Partner)** | Seed-stage climate/deep-tech fund explicitly thesis-focused on IP-led, defensible advanced-materials innovation — your biomimetic capture medium is exactly their stated thesis. Even if too early to invest, GPs at thesis-matched funds are often generous with mentorship calls. | LinkedIn, firm site |

### B. Investment (in order of stage-fit, earliest first)

| Who | Stage/Focus | Notes |
|---|---|---|
| **Speciale Invest** (Bengaluru) | Deep science/engineering, very early stage | Explicitly seeks science-and-engineering-first founders — good first check for a technical solo founder |
| **Theia Ventures** | Seed, IP-led climate/advanced materials | Best thesis match found; approach after co-founder is locked or in progress |
| **Inflection Point Ventures** | Angel network, early-to-mid stage, sector-agnostic | Useful for a smaller bridge/angel round; access to 3,300+ HNI/CXO network |
| **Climate Angels** | Dedicated climate-tech angel syndicate | Good for validating the pitch with climate-native angels before approaching funds |
| **NABARD Climate-Tech Fund (₹1,300 Cr, launching 2026)** | Government fund, early-stage agritech/climate-tech | Worth monitoring for application windows targeted at early-stage Indian climate-tech |
| **Third Derivative (D3)** | Global, 18-month accelerator, equity-free, needs TRL4 + 2 FTE | Apply once you have a co-founder and a working bench prototype — strong long-term fit given your industrial-hardtech profile |
| **Elemental Excelerator** | Global, non-dilutive grants up to $3M | Same stage gate as D3; keep on your 6–12 month radar |

### C. Incubators / Accelerators (India, deep-tech and climate-tech specific)

| Program | Fit | Notes |
|---|---|---|
| **SINE — Society for Innovation and Entrepreneurship, IIT Bombay** | Deep-tech TBI; incubated UrjanovaC (the other CCUS startup in your exact space) | Direct proximity to the NCoE-CCU facility and Prof. Vishal's lab — apply here first |
| **Climate Collective** | India's climate-tech-specific accelerator/community | Best for narrative sharpening, investor intros, and peer founder network in your exact vertical |
| **AGNIi (Office of PSA, Govt of India)** | Deep-tech commercialization and industry-matching platform | Useful specifically for connecting your capture tech to industrial pilot partners (your mid-size industrial retrofit target market) |
| **CIIE.CO (IIM Ahmedabad)** | Broad early-stage incubator with climate/deep-tech cohorts | Strong investor-readiness programming |
| **UChicago India Deep Tech Accelerator** (via SINE/FITT/IIT Madras Research Park) | US-market bridge for IIT-network-affiliated deep tech, with Aroa Venture Partners as conviction capital partner | 2026 cohort deadline has passed — track for the next cycle; strong if you want US market access later |

### D. Co-founder search (in addition to YC Co-Founder Matching, which you're already using)

| Channel | Why |
|---|---|
| **SINE IIT Bombay founder network / CCUS ecosystem events** | Business/GTM people already fluent in CCUS and India's compliance carbon market (CCTS) are concentrated here |
| **Climate Collective community & Slack/events** | India's most active climate-tech founder and operator community — strong for non-technical GTM/fundraising co-founders |
| **IIM Ahmedabad/Bangalore alumni networks (via CIIE.CO, NSRCEL)** | Good source for a business co-founder with fundraising and GTM ownership, your stated gap |
| **AngelList/Wellfound India + explicit LinkedIn posts tagged #CCUS #ClimateTech #CoFounder** | Passive but wide net; pair with the direct outreach below rather than relying on it alone |

---

## 4. How to reach out — templates by channel

### Cold LinkedIn message (mentor or investor)
Keep it under 80 words, lead with relevance not ask:

> Hi [Name] — I'm building CarbonLattice, a biomimetic flue-gas capture system (carbonic anhydrase + chitosan biomineralization) targeting India's mid-size industrial retrofit market ahead of CCTS. I saw your work on [specific thing — e.g. the IIT Bombay CCUS field lab / Theia's advanced-materials thesis] and would love 15 minutes to get your read on [one specific question — e.g. our sorbent regeneration approach / GTM sequencing]. Happy to send a 1-pager first if useful.

### Cold email (incubator/program)
Subject: `CarbonLattice — biomimetic industrial CO2/SO2/NOx capture, seeking [mentorship/incubation]`

> [2 lines: what it is, what stage] I've built a full techno-economic simulation platform (CBMS-Sim) modeling CAPEX/OPEX, CCTS credit revenue, and NPV for the system, and I'm now doing bench validation and customer discovery with mid-size Indian industrial emitters. I'm a solo technical founder currently building out a business/GTM co-founder search in parallel. I'd value [specific ask: a mentorship conversation / applying to your program] — happy to share the pitch deck and simulator.

### Warm intro ask (to someone who knows the target)
> Would you be open to a quick intro to [Name] at [Org]? I'm building an industrial carbon capture startup and think there's a strong thesis/expertise match — happy to send you a one-line blurb you can forward as-is.

### The "explain your idea in one breath" line (memorize this)
> "We capture CO2, SO2, NOx and heavy metals in one process, the same way corals build their skeletons — using an enzyme and a biopolymer instead of expensive amine chemistry — so mid-size Indian factories can hit CCTS compliance without the CAPEX of a Svante-style system."

---

## 5. Suggested sequence (next 90 days)

1. **Weeks 1–2:** Clean up the repo (README status section, hide/rename scratch files), finalize the 1-pager and simulator demo link.
2. **Weeks 2–4:** Reach out to Prof. Vishal's lab / SINE IIT Bombay for a mentorship conversation and possible bench-testing collaboration — this is your highest-leverage single contact given direct domain overlap.
3. **Weeks 3–6:** Parallel-track co-founder search through SINE network, Climate Collective, and continued YC matching — prioritize business/GTM candidates who already understand CCTS.
4. **Weeks 4–8:** Apply to Climate Collective and AGNIi; use Ostara Advisors or a Theia Ventures conversation to pressure-test your pitch before approaching angel networks.
5. **Weeks 8–12:** Once you have a co-founder (even a committed part-time one) and initial bench data, approach Speciale Invest, Inflection Point Ventures, and Climate Angels for a pre-seed conversation. Keep Third Derivative / Elemental Excelerator on the radar for once you clear TRL4 + 2 FTE.

---

*Note: fundraising and investor introductions carry real financial stakes — treat the above as a research starting point. Verify current program deadlines, GP contact details, and fund thesis fit directly on each organization's site before reaching out, since accelerator cohorts and fund mandates change often.*
