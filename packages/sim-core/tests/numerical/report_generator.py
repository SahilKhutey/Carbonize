"""
Generate a human-readable validation report.
Run: python packages/sim-core/tests/numerical/report_generator.py
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
import subprocess
import sys


def run_pytest_and_capture():
    """Run numerical tests and capture results."""
    # Execute pytest pointing to packages/sim-core/tests/numerical
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "packages/sim-core/tests/numerical", "-v", "--tb=short"],
        capture_output=True, text=True
    )
    return result.stdout, result.returncode


def generate_report(stdout: str, returncode: int):
    """Generate HTML report."""
    passed = stdout.count("PASSED")
    failed = stdout.count("FAILED")
    errors = stdout.count("ERROR")
    total = passed + failed + errors
    pass_rate = passed / total * 100 if total > 0 else 0
    
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>CBMS-Sim Numerical Validation Report</title>
    <style>
        body {{ font-family: monospace; max-width: 1200px; margin: 20px auto; padding: 20px; }}
        h1 {{ color: #059669; }}
        .summary {{ background: #f0fdf4; border: 1px solid #10b981; padding: 16px; border-radius: 8px; }}
        .test-pass {{ color: #10b981; }}
        .test-fail {{ color: #ef4444; }}
        table {{ border-collapse: collapse; width: 100%; margin: 16px 0; }}
        th, td {{ border: 1px solid #e5e7eb; padding: 6px 12px; text-align: left; }}
        th {{ background: #f3f4f6; }}
        pre {{ background: #f9fafb; border: 1px solid #e5e7eb; padding: 12px; border-radius: 4px; overflow-x: auto; }}
    </style>
</head>
<body>
    <h1>🔬 CBMS-Sim Numerical Validation Report</h1>
    <p>Date: {datetime.now(timezone.utc).isoformat()}</p>
    
    <div class="summary">
        <h2>Summary</h2>
        <p>Total tests executed: {total}</p>
        <p class="test-pass">✅ Passed: {passed}</p>
        <p class="test-fail">❌ Failed: {failed}</p>
        {f'<p class="test-fail">⚠️ Errors during collection/execution: {errors}</p>' if errors > 0 else ''}
        <p>Pass rate: {pass_rate:.1f}%</p>
    </div>
    
    <h2>Test Categories</h2>
    <table>
        <tr><th>Category</th><th>Tests Status</th></tr>
        <tr><td>Convergence (order verification, step independence)</td><td>{'✅ Passed' if failed == 0 and errors == 0 else '❌ Issues detected'}</td></tr>
        <tr><td>Stability (dilute concentration, temperature & pH bounds)</td><td>{'✅ Passed' if failed == 0 and errors == 0 else '❌ Issues detected'}</td></tr>
        <tr><td>Reference Solver Comparison (BDF vs Radau vs LSODA)</td><td>{'✅ Passed' if failed == 0 and errors == 0 else '❌ Issues detected'}</td></tr>
        <tr><td>Conservation (Ca, Carbon, Sulfur mass preservation)</td><td>{'✅ Passed' if failed == 0 and errors == 0 else '❌ Issues detected'}</td></tr>
        <tr><td>Stiffness Analysis (Jacobian eigenvalue ratios)</td><td>{'✅ Passed' if failed == 0 and errors == 0 else '❌ Issues detected'}</td></tr>
    </table>

    <h2>Pytest Console Output</h2>
    <pre>{stdout}</pre>
</body>
</html>
    """
    return html


if __name__ == "__main__":
    from datetime import timezone
    stdout, code = run_pytest_and_capture()
    report = generate_report(stdout, code)
    Path("numerical_validation_report.html").write_text(report, encoding="utf-8")
    print("Report saved to numerical_validation_report.html")
