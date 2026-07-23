"""
Hardware Specification Markdown Exporter.

Converts a HardwareSpecSheet object into a formal, printable Markdown engineering
deliverable (HARDWARE_SPEC_HANDOFF_PILOT_01.md) suitable for EPC contractors,
fabrication workshops, and procurement procurement leads.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional
from datetime import datetime, timezone
from cbms_sim.domain.hardware.spec_sheet import HardwareSpecSheet


class HardwareSpecMarkdownExporter:
    """Exports HardwareSpecSheet deliverables into markdown specifications."""

    def export_to_markdown(
        self,
        spec: HardwareSpecSheet,
        output_path: Optional[Path] = None,
    ) -> str:
        """Format HardwareSpecSheet as printable Markdown text."""
        
        trust = spec.trust_score
        status_badge = (
            "🟢 **HIGH CONFIDENCE (BENCH-VALIDATED)**"
            if trust.trust_level == "HIGH_CONFIDENCE_VALIDATED"
            else "🟡 **MODERATE UNCERTAINTY (UNVALIDATED LITERATURE)**"
            if "MODERATE" in trust.trust_level
            else "🔴 **HIGH RISK (DISCREPANT MODEL)**"
        )

        md_lines = [
            f"# 🏗️ Hardware Procurement Specification Sheet: {spec.project_name}",
            "",
            f"**Generated Date:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}",
            f"**Target Flue Gas Flow:** `{spec.target_flue_gas_flow_nm3_hr:,.1f} Nm³/hr`",
            f"**Target CO₂ Capture Efficiency:** `{spec.target_co2_capture_pct:.1f}%`",
            f"**Unified Trust Level:** {status_badge}",
            "",
            "> [!IMPORTANT]",
            f"> **Engineering Guidance:** {trust.hardware_guidance_text}",
            f"> **Applied Safety Margin:** `+{spec.applied_safety_margin_pct:.1f}%`",
            "",
            "## 1. Primary Reactor Column Geometry",
            "",
            "| Sizing Metric | Unbuffered Base Value | Applied Buffer | Sized Procurement Value | Unit |",
            "| :--- | :--- | :--- | :--- | :--- |",
            f"| **Reactor Volume ($V_r$)** | {spec.reactor_volume_m3:.2f} | +{spec.applied_safety_margin_pct:.1f}% | **{spec.sized_reactor_volume_m3:.2f}** | m³ |",
            f"| **Column Diameter ($D$)** | {spec.column_diameter_m:.2f} | Superficial Velocity 1.5 m/s | **{spec.column_diameter_m:.2f}** | m |",
            f"| **Column Height ($H$)** | {spec.column_height_m:.2f} | Aspect Ratio $H/D \\approx {spec.column_height_m / (spec.column_diameter_m or 1.0):.1f}$ | **{spec.column_height_m:.2f}** | m |",
            f"| **Gas Residence Time ($\\tau$)** | {spec.residence_time_s:.1f} | Fixed Integration Window | **{spec.residence_time_s:.1f}** | s |",
            f"| **Liquid-to-Gas Ratio ($L/G$)** | {spec.liquid_to_gas_ratio_l_per_nm3:.1f} | Counter-current Spray | **{spec.liquid_to_gas_ratio_l_per_nm3:.1f}** | L/Nm³ |",
            "",
            "## 2. 24-Hour Consumables & Chemical Feed Schedule",
            "",
            "| Chemical Reagent / Consumable | Dosage / Concentration | Daily Consumption Rate | Unit |",
            "| :--- | :--- | :--- | :--- |",
            f"| **Chitosan Biopolymer Matrix** | {spec.chitosan_wt_pct:.1f} Wt % | **{spec.chitosan_consumption_kg_per_day:,.1f}** | kg/day |",
            f"| **Hydrated Lime / Calcium Source** | 3.5 Wt % | **{spec.ca_lime_consumption_kg_per_day:,.1f}** | kg/day |",
            f"| **Carbonic Anhydrase Enzyme** | {spec.ca_enzyme_dosage_mg_per_l:.1f} mg/L slurry | Continuous Slipstream | mg/L |",
            f"| **Structured Mesh Filter Packs** | 6.0 Mesh Count | Every **{spec.mesh_replacement_interval_days}** days | days |",
            "",
            "## 3. Engineering Safety & Control Notes",
            "",
        ]

        for note in spec.notes:
            md_lines.append(f"- {note}")

        md_text = "\n".join(md_lines) + "\n"

        if output_path is not None:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(md_text, encoding="utf-8")

        return md_text
