#!/bin/bash
# Run all benchmarks and generate report

set -e

OUTPUT_DIR="packages/sim-core/tests/performance/results"
mkdir -p "$OUTPUT_DIR"

echo "====================================================================="
echo "⚡ Starting CBMS-Sim Performance Benchmarks"
echo "====================================================================="

# Run benchmarks using pytest
python -m pytest packages/sim-core/tests/performance/ \
    -v --tb=short

# Generate HTML report from results
echo "📊 Generating human-readable performance report..."
python packages/sim-core/tests/performance/report_generator.py

echo "====================================================================="
echo "✓ Performance Benchmarks Completed Successfully"
echo "Report: $OUTPUT_DIR/report.html"
echo "====================================================================="
