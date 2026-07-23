# Software Specification: Corrosion Test Data Pipeline

**Companion to:** [`corrosion-test-protocol.md`](corrosion-test-protocol.md)  
**Owner:** Science / Platform Engineering  
**Status:** 🟡 Specification Complete — Implementation Pending Lab Pilot  
**Last updated:** 2026-07-20

---

## 1. Overview

`corrosion-test-protocol.md` defines a 30-day immersion test for 5 material specimens before full reactor budget commitment. This document specifies the software needed to:

1. Register test specimens and track their test conditions
2. Log inspection measurements (mass loss, crack observations, compression set)
3. Evaluate pass/fail against specified criteria
4. Generate a material qualification report
5. Gate the procurement workflow — no full-budget PO can be raised until all specimens pass

---

## 2. Corrosion Test Data Model

```sql
-- Alembic migration: 0026_add_corrosion_test_tables.py

CREATE TABLE corrosion_tests (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id     UUID NOT NULL REFERENCES organizations(id),
    plant_id            UUID REFERENCES plant_profiles(id),
    test_name           TEXT NOT NULL,       -- e.g. "PP-H Vessel Pre-Qualification 2026-Q3"
    start_date          DATE NOT NULL,
    planned_end_date    DATE NOT NULL,       -- start_date + 30 days per protocol
    status              TEXT NOT NULL DEFAULT 'running',   -- running|complete|failed|aborted
    test_conditions     JSONB NOT NULL,      -- {ph: 9.5, temp_c: 50, so2_ppm: 500}
    created_by          UUID REFERENCES users(id),
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE corrosion_specimens (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    test_id         UUID NOT NULL REFERENCES corrosion_tests(id),
    specimen_code   TEXT NOT NULL,           -- e.g. "PP-H-01"
    material        TEXT NOT NULL,           -- e.g. "PP-H 12mm"
    condition       TEXT NOT NULL,           -- e.g. "As-specified"
    test_conditions JSONB,                   -- can override test-level conditions
    initial_mass_g  DOUBLE PRECISION,        -- for mass-loss calculation
    pass_criteria   JSONB NOT NULL,          -- {"max_mass_loss_pct": 2.0, "no_cracking": true}
    result          TEXT,                    -- null | 'PASS' | 'FAIL'
    UNIQUE (test_id, specimen_code)
);

CREATE TABLE corrosion_inspections (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    specimen_id     UUID NOT NULL REFERENCES corrosion_specimens(id),
    inspected_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    inspected_by    UUID REFERENCES users(id),
    day_number      INT NOT NULL,            -- 1, 7, 14, 21, 30
    mass_g          DOUBLE PRECISION,        -- measured mass
    mass_loss_pct   DOUBLE PRECISION,        -- computed: (initial - current) / initial * 100
    visual_notes    TEXT,                    -- "no cracking", "surface discolouration at weld"
    crack_observed  BOOLEAN NOT NULL DEFAULT FALSE,
    delamination    BOOLEAN NOT NULL DEFAULT FALSE,
    pitting         BOOLEAN NOT NULL DEFAULT FALSE,
    compression_set_pct DOUBLE PRECISION,    -- for O-rings only
    photos          TEXT[],                  -- URIs to uploaded inspection photos
    quality_flags   TEXT[],                  -- ['HIGH_MASS_LOSS', 'CRACK_DETECTED']
    passed_interim  BOOLEAN                  -- null until evaluated
);
```

---

## 3. Specimen Registry (from protocol)

The 5 specimens defined in `corrosion-test-protocol.md` are pre-registered at test creation:

```python
DEFAULT_SPECIMENS = [
    {
        "specimen_code": "PP-H-BULK",
        "material":      "PP-H 12mm homopolymer",
        "condition":     "As specified — no weld",
        "test_conditions": {"ph": 9.5, "temp_c": 50, "medium": "alkaline_slurry"},
        "pass_criteria": {
            "max_mass_loss_pct": 2.0,
            "no_cracking":       True,
            "no_delamination":   True,
        },
    },
    {
        "specimen_code": "PP-H-WELD",
        "material":      "PP-H hot-gas welded joint",
        "condition":     "Hot gas welded, 2mm bead",
        "test_conditions": {"ph": 9.5, "temp_c": 50, "medium": "alkaline_slurry"},
        "pass_criteria": {
            "max_mass_loss_pct": 2.0,
            "no_delamination":   True,
            "no_cracking":       True,
        },
    },
    {
        "specimen_code": "SS316L-BARE",
        "material":      "316L Stainless Steel — bare",
        "condition":     "Polished, no coating",
        "test_conditions": {"ph": 9.5, "temp_c": 50, "so2_ppm": 500, "medium": "alkaline_slurry"},
        "pass_criteria": {
            "no_pitting":        True,
            "max_mass_loss_pct": 1.0,
        },
    },
    {
        "specimen_code": "SS316L-COAT",
        "material":      "316L SS with 3mm PP coating",
        "condition":     "PP-coated impeller coupon",
        "test_conditions": {"ph": 9.5, "temp_c": 50, "medium": "alkaline_slurry"},
        "pass_criteria": {
            "no_coating_failure": True,
            "no_delamination":    True,
        },
    },
    {
        "specimen_code": "EPDM-ORING",
        "material":      "EPDM O-ring (DN25)",
        "condition":     "As-received, uncompressed",
        "test_conditions": {"ph": 9.5, "temp_c": 55, "medium": "alkaline_slurry"},
        "pass_criteria": {
            "max_compression_set_pct": 10.0,
            "no_cracking":             True,
        },
    },
]
```

---

## 4. Inspection Schedule & Reminders

Inspections are scheduled at days 1, 7, 14, 21, and 30. The platform auto-schedules reminders:

```python
INSPECTION_DAYS = [1, 7, 14, 21, 30]

async def schedule_corrosion_reminders(test: CorrosionTest, db: AsyncSession):
    """
    Creates Celery Beat entries to send email/webhook notifications
    to the assigned lab technician 24h before each inspection day.
    """
    for day in INSPECTION_DAYS:
        remind_at = test.start_date + timedelta(days=day - 1)
        await create_scheduled_notification(
            recipient_id=test.created_by,
            send_at=remind_at,
            subject=f"Corrosion test '{test.test_name}' — Day {day} inspection due",
            body=f"Please inspect all {len(DEFAULT_SPECIMENS)} specimens and log results "
                 f"at /corrosion-tests/{test.id}/inspect",
        )
```

---

## 5. Pass/Fail Evaluation

```python
def evaluate_specimen(
    specimen: CorrosionSpecimen,
    inspections: list[CorrosionInspection]
) -> tuple[str, list[str]]:
    """
    Returns ('PASS'|'FAIL'|'PENDING', [list of failure reasons])
    Evaluated at day 30 final inspection.
    """
    if not inspections:
        return "PENDING", []

    final = max(inspections, key=lambda i: i.day_number)
    failures = []
    criteria = specimen.pass_criteria

    if "max_mass_loss_pct" in criteria:
        if final.mass_loss_pct and final.mass_loss_pct > criteria["max_mass_loss_pct"]:
            failures.append(
                f"Mass loss {final.mass_loss_pct:.2f}% > limit {criteria['max_mass_loss_pct']}%"
            )

    if criteria.get("no_cracking") and any(i.crack_observed for i in inspections):
        failures.append("Cracking observed in one or more inspections")

    if criteria.get("no_delamination") and any(i.delamination for i in inspections):
        failures.append("Delamination observed")

    if criteria.get("no_pitting") and any(i.pitting for i in inspections):
        failures.append("Pitting observed on 316L SS specimen")

    if criteria.get("no_coating_failure") and any(i.delamination for i in inspections):
        failures.append("PP coating failure / delamination")

    if "max_compression_set_pct" in criteria:
        if final.compression_set_pct and final.compression_set_pct > criteria["max_compression_set_pct"]:
            failures.append(
                f"EPDM compression set {final.compression_set_pct:.1f}% > limit "
                f"{criteria['max_compression_set_pct']}%"
            )

    return ("PASS" if not failures else "FAIL", failures)


def evaluate_test(test: CorrosionTest, specimens: list) -> str:
    """
    Test passes only if ALL specimens pass.
    Returns 'PASS'|'FAIL'|'PENDING'
    """
    results = [s.result for s in specimens]
    if any(r == "FAIL" for r in results):
        return "FAIL"
    if any(r is None or r == "PENDING" for r in results):
        return "PENDING"
    return "PASS"
```

---

## 6. Material Qualification Gate

The procurement workflow enforces that no capital purchase order for reactor vessel, impeller, or seals can proceed until the corrosion test passes:

```python
async def check_procurement_gate(
    plant_id: UUID,
    item_category: str,   # 'reactor_vessel' | 'impeller' | 'seals'
    db: AsyncSession,
) -> tuple[bool, str]:
    """
    Returns (approved: bool, reason: str)
    Blocks if:
      - No completed corrosion test exists for this plant
      - The most recent test result is 'FAIL' or 'PENDING'
    """
    relevant_specimens = {
        "reactor_vessel": ["PP-H-BULK", "PP-H-WELD"],
        "impeller":       ["SS316L-COAT"],
        "seals":          ["EPDM-ORING"],
    }
    codes = relevant_specimens.get(item_category, [])

    test = await get_latest_passed_test(plant_id, specimen_codes=codes, db=db)
    if not test:
        return False, (
            f"No passed corrosion test found for '{item_category}'. "
            f"Complete the 30-day immersion test per hardware/corrosion-test-protocol.md first."
        )
    return True, f"Qualified by test '{test.test_name}' (passed {test.status_updated_at.date()})"
```

---

## 7. Qualification Report Generation

At test completion, the API generates a PDF-ready report:

```python
def render_qualification_report(test: CorrosionTest, specimens: list) -> dict:
    return {
        "report_title":     f"Material Qualification Report — {test.test_name}",
        "protocol_version": "corrosion-test-protocol.md v1.0",
        "test_period":      f"{test.start_date} → {test.planned_end_date}",
        "test_conditions":  test.test_conditions,
        "overall_result":   evaluate_test(test, specimens),
        "specimens": [
            {
                "code":         s.specimen_code,
                "material":     s.material,
                "result":       s.result,
                "failure_reasons": evaluate_specimen(s, s.inspections)[1],
                "mass_loss_pct":   _final_mass_loss(s),
                "compression_set_pct": _final_compression(s),
                "inspection_count": len(s.inspections),
            }
            for s in specimens
        ],
        "recommended_materials": _build_recommendation(specimens),
        "procurement_gates_unlocked": [
            cat for cat in ["reactor_vessel", "impeller", "seals"]
            if _gate_passes(specimens, cat)
        ],
        "generated_at":  datetime.now(UTC).isoformat(),
    }
```

The report is downloadable as JSON (for machine consumption) and rendered as PDF via WeasyPrint in the API.

---

## 8. API Endpoints

```
POST /api/corrosion-tests                            → create new test + schedule reminders
GET  /api/corrosion-tests                            → list tests (org-scoped)
GET  /api/corrosion-tests/{id}                       → test detail + specimens + status
POST /api/corrosion-tests/{id}/inspect               → log inspection for all specimens
GET  /api/corrosion-tests/{id}/report                → qualification report JSON
GET  /api/corrosion-tests/{id}/report.pdf            → PDF version
GET  /api/plants/{plant_id}/procurement-gate/{item}  → check procurement gate
```

---

## 9. Operator UI — Corrosion Test Tracker

In `packages/web/src/features/experimental/`, a **Corrosion Test** section shows:

```
┌─────────────────────────────────────────────────────────────────┐
│ 🧪 Material Qualification Test — PP-H Pre-Qualification 2026-Q3 │
│ Day 14 of 30  ████████████████░░░░░░░░░░  47% complete          │
├─────────────────────────────────────────────────────────────────┤
│ Specimen         │ Mass Loss │ Visual │ Status  │ Next Inspect │
│ PP-H Bulk        │ 0.3%      │ Clear  │ 🟢 OK   │ Day 21 (7d)  │
│ PP-H Welded      │ 0.5%      │ Clear  │ 🟢 OK   │ Day 21 (7d)  │
│ 316L SS Bare     │ 0.8%      │ ⚠ Tint │ 🟡 Watch│ Day 21 (7d)  │
│ 316L SS Coated   │ 0.1%      │ Clear  │ 🟢 OK   │ Day 21 (7d)  │
│ EPDM O-Ring      │  —        │ Clear  │ 🟢 OK   │ Day 21 (7d)  │
├─────────────────────────────────────────────────────────────────┤
│ 🔒 Procurement Gates                                             │
│ Reactor Vessel:  LOCKED — test in progress                      │
│ Impeller:        LOCKED — test in progress                      │
│ Seals:           LOCKED — test in progress                      │
└─────────────────────────────────────────────────────────────────┘
```

---

## 10. Open Items

| Item | Priority | Owner |
|---|---|---|
| Alembic migration for corrosion test tables | 🔴 High | Platform Eng |
| `evaluate_specimen` + `evaluate_test` service logic | 🔴 High | Platform Eng |
| Celery Beat reminder scheduling | 🟡 Medium | Platform Eng |
| Procurement gate endpoint | 🟡 Medium | Platform Eng |
| Qualification report PDF (WeasyPrint template) | 🟡 Medium | Platform Eng |
| Corrosion test tracker UI in experimental/ | 🟡 Medium | Frontend |
| Photo upload support (inspection photos) | 🟢 Low | Platform Eng |
