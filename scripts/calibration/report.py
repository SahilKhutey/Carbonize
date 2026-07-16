"""
Generate HTML calibration reports.
"""

from __future__ import annotations

from pathlib import Path
from cbms_shared.logging import get_logger

logger = get_logger(__name__)


class ReportGenerator:
    """Generate calibration HTML report."""
    
    def __init__(self):
        self.logger = get_logger(self.__class__.__name__)
        
    def generate(
        self,
        output_path: Path,
        experiment: str,
        fit_result: any,
        uncertainty: dict,
        uq_results: dict | None,
        comparison: dict | None,
        baseline_params: dict,
        new_params: dict,
    ) -> None:
        self.logger.info("generating_html_report", path=str(output_path))
        
        # Ensure parent directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>Calibration Report - {experiment}</title>
    <style>
        body {{ font-family: sans-serif; margin: 40px; color: #333; }}
        h1 {{ color: #2C3E50; }}
        table {{ border-collapse: collapse; width: 100%; margin-top: 20px; }}
        th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
        .success {{ color: green; font-weight: bold; }}
    </style>
</head>
<body>
    <h1>Calibration Report: {experiment}</h1>
    <p>Status: <span class="success">Completed</span></p>
    <h2>Fit Performance</h2>
    <table>
        <tr><th>Metric</th><th>Value</th></tr>
        <tr><td>R-squared</td><td>{fit_result.r_squared:.4f}</td></tr>
        <tr><td>RMSE</td><td>{fit_result.rmse:.4e}</td></tr>
        <tr><td>MAE</td><td>{fit_result.mae:.4e}</td></tr>
    </table>
    
    <h2>Calibrated Parameters</h2>
    <table>
        <tr><th>Parameter</th><th>Baseline Value</th><th>Calibrated Value</th><th>95% Confidence Interval</th></tr>
        """
        for path, val in fit_result.parameters.items():
            # Safely get baseline value
            try:
                base_val = baseline_params["parameters"][path]["value"]
            except KeyError:
                base_val = "N/A"
            ci = uncertainty.get(path, ("N/A", "N/A"))
            ci_str = f"[{ci[0]:.4e}, {ci[1]:.4e}]" if isinstance(ci[0], float) else "N/A"
            html_content += f"""<tr>
                <td>{path}</td>
                <td>{base_val}</td>
                <td>{val:.4e}</td>
                <td>{ci_str}</td>
            </tr>"""
            
        html_content += """
    </table>
</body>
</html>
"""
        with open(output_path, "w") as f:
            f.write(html_content)
        self.logger.info("html_report_written", path=str(output_path))
