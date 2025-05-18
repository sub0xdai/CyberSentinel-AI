#!/bin/bash
# generate_dashboard.sh

# Default output directory
OUTPUT_DIR="dashboard"

# Parse command line arguments
while getopts "o:" opt; do
  case $opt in
    o) OUTPUT_DIR="$OPTARG" ;;
    \?) echo "Invalid option -$OPTARG" >&2; exit 1 ;;
  esac
done

echo "Generating dashboard in $OUTPUT_DIR..."

# Create output directory if it doesn't exist
mkdir -p "$OUTPUT_DIR"

# Copy dashboard HTML to output directory
cp dashboard.html "$OUTPUT_DIR/index.html"

# Create logs directory structure in dashboard
mkdir -p "$OUTPUT_DIR/logs/compliance"
mkdir -p "$OUTPUT_DIR/logs/visualizations"

# Run metrics analysis and copy report to dashboard
echo "Generating metrics report..."
python3 metrics_analyzer.py

# Copy latest data to dashboard
cp logs/metrics_report.json "$OUTPUT_DIR/logs/"
cp logs/alerts.json "$OUTPUT_DIR/logs/"
cp logs/compliance/iso27001_report.json "$OUTPUT_DIR/logs/compliance/"
cp -r logs/visualizations/* "$OUTPUT_DIR/logs/visualizations/"

echo "Dashboard generated successfully"
echo "To view the dashboard, open $OUTPUT_DIR/index.html in a web browser"
