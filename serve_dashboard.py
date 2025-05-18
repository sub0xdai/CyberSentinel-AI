#!/usr/bin/env python3
# serve_dashboard.py - Dashboard Web Server
# Part of CyberSentinel-AI

import os
import json
import shutil
import http.server
import socketserver
import webbrowser
from pathlib import Path
import threading
import argparse
from datetime import datetime

# Banner display
print("┌───────────────────────────────────────────────┐")
print("│                                               │")
print("│ CyberSentinel-AI: Dashboard Server           │")
print("│ Web Visualization Interface                  │")
print("│                                               │")
print("└───────────────────────────────────────────────┘")

def timestamp():
    """Generate current timestamp"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def create_sample_data(dashboard_dir):
    """Create sample data files for dashboard if needed"""
    print(f"[{timestamp()}] Setting up dashboard data files")
    
    # Create necessary directories
    os.makedirs(f"{dashboard_dir}/logs/compliance", exist_ok=True)
    os.makedirs(f"{dashboard_dir}/logs/visualizations", exist_ok=True)
    
    # Create sample metrics data if not exists
    metrics_file = f"{dashboard_dir}/logs/metrics_report.json"
    if not os.path.exists(metrics_file):
        sample_metrics = {
            "timestamp": timestamp(),
            "summary_metrics": {
                "detection_accuracy": 92.5,
                "avg_response_time": 0.8,
                "time_savings": 85,
                "blocked_threats": 5
            },
            "detailed_metrics": {
                "attack_distribution": {
                    "brute_force": 7,
                    "web_brute_force": 3
                },
                "severity_distribution": {
                    "High": 3,
                    "Medium": 5,
                    "Low": 2
                }
            }
        }
        with open(metrics_file, 'w') as f:
            json.dump(sample_metrics, f, indent=2)
        print(f"[{timestamp()}] Created sample metrics data")
    
    # Create sample compliance data if not exists
    compliance_file = f"{dashboard_dir}/logs/compliance/iso27001_report.json"
    if not os.path.exists(compliance_file):
        sample_compliance = {
            "framework": "ISO 27001:2013",
            "timestamp": timestamp(),
            "mapped_controls": [
                {
                    "control_id": "A.9.4.2",
                    "control_name": "Secure log-on procedures",
                    "section": "Access Control",
                    "justification": "Brute force attack attempts"
                },
                {
                    "control_id": "A.12.4.1",
                    "control_name": "Event logging",
                    "section": "Operations Security",
                    "justification": "Security event logging enabled"
                },
                {
                    "control_id": "A.16.1.5",
                    "control_name": "Response to information security incidents",
                    "section": "Information Security Incident Management",
                    "justification": "Automated response procedures implemented"
                }
            ],
            "compliance_summary": {
                "A.9": {
                    "title": "Access Control",
                    "controls_triggered": [
                        {"id": "A.9.4.2", "name": "Secure log-on procedures"}
                    ]
                },
                "A.12": {
                    "title": "Operations Security",
                    "controls_triggered": [
                        {"id": "A.12.4.1", "name": "Event logging"}
                    ]
                },
                "A.16": {
                    "title": "Information Security Incident Management",
                    "controls_triggered": [
                        {"id": "A.16.1.5", "name": "Response to information security incidents"}
                    ]
                }
            }
        }
        with open(compliance_file, 'w') as f:
            json.dump(sample_compliance, f, indent=2)
        print(f"[{timestamp()}] Created sample compliance data")
    
    # Create sample alerts data if not exists
    alerts_file = f"{dashboard_dir}/logs/alerts.json"
    if not os.path.exists(alerts_file):
        sample_alerts = [
            {
                "timestamp": timestamp(),
                "source_ip": "192.168.122.100",
                "attack_type": "brute_force",
                "attempt_count": 7,
                "alert_type": "brute_force",
                "rule_level": 8,
                "description": "Possible brute force attack from 192.168.122.100: 7 failed attempts"
            },
            {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "source_ip": "192.168.122.150",
                "attack_type": "web_brute_force",
                "attempt_count": 5,
                "target_urls": "/admin/login.php,/wp-login.php",
                "alert_type": "web_brute_force",
                "rule_level": 6,
                "description": "Possible web brute force attack from 192.168.122.150: 5 failed attempts"
            }
        ]
        with open(alerts_file, 'w') as f:
            json.dump(sample_alerts, f, indent=2)
        print(f"[{timestamp()}] Created sample alerts data")

def copy_real_data(source_dir, dashboard_dir):
    """Copy actual data files from logs directory if they exist"""
    print(f"[{timestamp()}] Checking for real data files to copy")
    
    # List of files to copy if they exist
    files_to_copy = {
        "logs/metrics_report.json": f"{dashboard_dir}/logs/metrics_report.json",
        "logs/alerts.json": f"{dashboard_dir}/logs/alerts.json",
        "logs/web_alerts.json": f"{dashboard_dir}/logs/web_alerts.json",
        "logs/compliance/iso27001_report.json": f"{dashboard_dir}/logs/compliance/iso27001_report.json",
        "logs/ai/openai_analysis.json": f"{dashboard_dir}/logs/ai/openai_analysis.json"
    }
    
    # Create ai directory
    os.makedirs(f"{dashboard_dir}/logs/ai", exist_ok=True)
    
    # Copy files if they exist
    for source, dest in files_to_copy.items():
        source_path = os.path.join(source_dir, source)
        if os.path.exists(source_path):
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            shutil.copy2(source_path, dest)
            print(f"[{timestamp()}] Copied {source} to dashboard")
    
    # Copy any visualization files
    vis_source = os.path.join(source_dir, "logs/visualizations")
    vis_dest = f"{dashboard_dir}/logs/visualizations"
    if os.path.exists(vis_source) and os.path.isdir(vis_source):
        os.makedirs(vis_dest, exist_ok=True)
        for file in os.listdir(vis_source):
            if file.endswith('.png'):
                shutil.copy2(os.path.join(vis_source, file), os.path.join(vis_dest, file))
                print(f"[{timestamp()}] Copied visualization {file}")

def prepare_dashboard(source_dir, dashboard_dir):
    """Prepare dashboard files and data"""
    print(f"[{timestamp()}] Preparing dashboard in {dashboard_dir}")
    
    # Create dashboard directory
    os.makedirs(dashboard_dir, exist_ok=True)
    
    # Copy dashboard HTML
    shutil.copy2(os.path.join(source_dir, "dashboard.html"), os.path.join(dashboard_dir, "index.html"))
    print(f"[{timestamp()}] Copied dashboard HTML to {dashboard_dir}/index.html")
    
    # Copy real data files if they exist
    copy_real_data(source_dir, dashboard_dir)
    
    # Create sample data for missing files
    create_sample_data(dashboard_dir)
    
    print(f"[{timestamp()}] Dashboard preparation complete")

def open_browser(server_url):
    """Open the browser after a short delay"""
    def _open_browser():
        webbrowser.open(server_url)
        print(f"[{timestamp()}] Opening dashboard in browser: {server_url}")
    
    # Start browser thread after a 1-second delay
    browser_thread = threading.Timer(1.0, _open_browser)
    browser_thread.daemon = True
    browser_thread.start()

def start_server(port, dashboard_dir):
    """Start HTTP server for dashboard"""
    # Change to the dashboard directory
    os.chdir(dashboard_dir)
    
    # Create HTTP server
    handler = http.server.SimpleHTTPRequestHandler
    server = socketserver.TCPServer(("", port), handler)
    
    server_url = f"http://localhost:{port}"
    print(f"[{timestamp()}] Starting dashboard server at {server_url}")
    print(f"[{timestamp()}] Press Ctrl+C to stop the server")
    
    # Open browser automatically
    open_browser(server_url)
    
    # Start server
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print(f"[{timestamp()}] Server stopped by user")
    finally:
        server.server_close()

def main():
    """Main function"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="CyberSentinel-AI Dashboard Server")
    parser.add_argument("-p", "--port", type=int, default=8000, help="Port to run the server on (default: 8000)")
    parser.add_argument("-d", "--dir", type=str, default="dashboard", help="Directory to serve dashboard from (default: dashboard)")
    parser.add_argument("-s", "--source", type=str, default=".", help="Source directory containing project files (default: current directory)")
    args = parser.parse_args()
    
    # Prepare dashboard files
    prepare_dashboard(args.source, args.dir)
    
    # Start HTTP server
    start_server(args.port, args.dir)

if __name__ == "__main__":
    main()