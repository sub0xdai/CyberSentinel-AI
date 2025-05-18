#!/usr/bin/env python3
# wazuh_integration.py - SIEM Integration for CyberSentinel-AI
# Part of CyberSentinel-AI

import json
import requests
import os
import ssl
import urllib3
import socket
from datetime import datetime

# Disable SSL warnings for testing (remove in production)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Banner display
print("┌───────────────────────────────────────────────┐")
print("│                                               │")
print("│ CyberSentinel-AI: SIEM Integration           │")
print("│ Wazuh SIEM Connector                         │")
print("│                                               │")
print("└───────────────────────────────────────────────┘")

# Configuration
WAZUH_API_URL = os.getenv("WAZUH_API_URL", "https://10.0.1.30:55000")
WAZUH_API_USER = os.getenv("WAZUH_API_USER", "wazuh")
WAZUH_API_PASSWORD = os.getenv("WAZUH_API_PASSWORD", "wazuh")
LOG_DIR = "logs"
AI_LOG_DIR = f"{LOG_DIR}/ai"
SIEM_LOG_DIR = f"{LOG_DIR}/siem"

# Ensure log directories exist
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(AI_LOG_DIR, exist_ok=True)
os.makedirs(SIEM_LOG_DIR, exist_ok=True)

def timestamp():
    """Generate current timestamp"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def send_to_wazuh(alert_data):
    """Send alert data to Wazuh via API"""
    # Format for Wazuh
    wazuh_alert = {
        "timestamp": alert_data.get("timestamp", timestamp()),
        "rule": {
            "level": alert_data.get("rule_level", 6),
            "description": alert_data.get("description", "CyberSentinel-AI Alert"),
            "groups": ["cybersentinel", "attack", "credential"]
        },
        "agent": {
            "name": socket.gethostname(),
            "ip": "127.0.0.1"
        },
        "data": alert_data
    }
    
    # Log the alert being sent
    with open(f"{SIEM_LOG_DIR}/sent_alerts.json", "a") as f:
        f.write(json.dumps(wazuh_alert, indent=2) + "\n")
    
    try:
        # Get auth token
        auth_headers = {'Content-Type': 'application/json'}
        auth_data = {'username': WAZUH_API_USER, 'password': WAZUH_API_PASSWORD}
        
        print(f"[{timestamp()}] Authenticating with Wazuh API at {WAZUH_API_URL}")
        
        # In testing mode, check if API is available
        if "10.0.1.30" in WAZUH_API_URL:
            print(f"[{timestamp()}] SIMULATION MODE: Wazuh server appears to be a test/placeholder address")
            print(f"[{timestamp()}] Simulating successful SIEM integration")
            
            # Log simulated auth
            with open(f"{SIEM_LOG_DIR}/siem.log", "a") as f:
                f.write(f"[{timestamp()}] Simulated authentication with Wazuh API\n")
            
            # Return success without actually connecting
            return True
        
        # Actual API connection
        auth_response = requests.post(f"{WAZUH_API_URL}/security/user/authenticate", 
                              headers=auth_headers,
                              json=auth_data,
                              verify=False)  # In production, use valid SSL cert
        
        if auth_response.status_code != 200:
            print(f"[{timestamp()}] Error authenticating with Wazuh API: {auth_response.text}")
            
            # Log error
            with open(f"{SIEM_LOG_DIR}/siem.log", "a") as f:
                f.write(f"[{timestamp()}] Error authenticating with Wazuh API: {auth_response.text}\n")
            
            return False
            
        token = auth_response.json()['data']['token']
        
        # Send alert
        alert_headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}'
        }
        
        print(f"[{timestamp()}] Sending alert to Wazuh SIEM")
        
        response = requests.post(f"{WAZUH_API_URL}/events",
                               headers=alert_headers,
                               json=wazuh_alert,
                               verify=False)  # In production, use valid SSL cert
        
        if response.status_code == 200:
            print(f"[{timestamp()}] Alert sent to Wazuh SIEM successfully")
            
            # Log success
            with open(f"{SIEM_LOG_DIR}/siem.log", "a") as f:
                f.write(f"[{timestamp()}] Alert sent to Wazuh SIEM successfully\n")
            
            return True
        else:
            print(f"[{timestamp()}] Error sending alert to Wazuh: {response.text}")
            
            # Log error
            with open(f"{SIEM_LOG_DIR}/siem.log", "a") as f:
                f.write(f"[{timestamp()}] Error sending alert to Wazuh: {response.text}\n")
            
            return False
    
    except Exception as e:
        print(f"[{timestamp()}] Exception when sending to Wazuh: {str(e)}")
        
        # Log exception
        with open(f"{SIEM_LOG_DIR}/siem.log", "a") as f:
            f.write(f"[{timestamp()}] Exception when sending to Wazuh: {str(e)}\n")
        
        return False

def get_alerts():
    """Get alerts from alert files"""
    alerts = []
    
    # Check SSH alerts
    ssh_alerts_file = f"{LOG_DIR}/alerts.json"
    if os.path.exists(ssh_alerts_file):
        with open(ssh_alerts_file, 'r') as f:
            content = f.read().strip()
            if content:
                try:
                    if content.startswith('['):
                        alerts.extend(json.loads(content))
                    else:
                        alerts.append(json.loads(content))
                except json.JSONDecodeError as e:
                    print(f"[{timestamp()}] Error parsing SSH alerts JSON: {e}")
    
    # Check Web alerts
    web_alerts_file = f"{LOG_DIR}/web_alerts.json"
    if os.path.exists(web_alerts_file):
        with open(web_alerts_file, 'r') as f:
            content = f.read().strip()
            if content:
                try:
                    if content.startswith('['):
                        alerts.extend(json.loads(content))
                    else:
                        alerts.append(json.loads(content))
                except json.JSONDecodeError as e:
                    print(f"[{timestamp()}] Error parsing Web alerts JSON: {e}")
    
    return alerts

def get_analysis():
    """Get AI analysis from the openai_analysis.json file"""
    analysis_file = f"{AI_LOG_DIR}/openai_analysis.json"
    if not os.path.exists(analysis_file):
        print(f"[{timestamp()}] No analysis file found.")
        return None
    
    with open(analysis_file, 'r') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError as e:
            print(f"[{timestamp()}] Error parsing analysis JSON: {e}")
            return None

def get_iso27001_data():
    """Get ISO 27001 compliance data"""
    compliance_file = f"{LOG_DIR}/compliance/iso27001_report.json"
    if not os.path.exists(compliance_file):
        print(f"[{timestamp()}] No ISO 27001 compliance data found.")
        return None
    
    with open(compliance_file, 'r') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError as e:
            print(f"[{timestamp()}] Error parsing compliance JSON: {e}")
            return None

def main():
    print(f"[{timestamp()}] Starting Wazuh SIEM integration...")
    
    # Get alerts from both SSH and Web monitoring
    alerts = get_alerts()
    if not alerts:
        print(f"[{timestamp()}] No alerts to send to SIEM.")
        return
    
    print(f"[{timestamp()}] Found {len(alerts)} alerts to process")
    
    # Get AI analysis
    analysis = get_analysis()
    if analysis:
        print(f"[{timestamp()}] Found AI analysis data")
    
    # Get ISO 27001 compliance data
    compliance = get_iso27001_data()
    if compliance:
        print(f"[{timestamp()}] Found ISO 27001 compliance data")
    
    # Record start time for metrics
    start_time = datetime.now()
    
    # Process and send each alert to Wazuh
    success_count = 0
    for i, alert in enumerate(alerts):
        print(f"[{timestamp()}] Processing alert {i+1}/{len(alerts)}")
        
        # Enrich alert with AI analysis if available
        if analysis:
            alert["ai_analysis"] = {
                "is_credential_attack": analysis.get("is_credential_attack", False),
                "severity": analysis.get("severity", 0),
                "mitre_technique": analysis.get("mitre_technique", ""),
                "app_impact": analysis.get("app_impact", "")
            }
        
        # Enrich alert with compliance data if available
        if compliance and compliance.get("mapped_controls"):
            # Add the first 3 controls or all if less than 3
            alert["compliance"] = {
                "framework": "ISO 27001:2013",
                "controls": compliance.get("mapped_controls")[:3]
            }
        
        # Send enriched alert to Wazuh
        if send_to_wazuh(alert):
            success_count += 1
    
    # Calculate processing time
    end_time = datetime.now()
    processing_time = (end_time - start_time).total_seconds()
    
    # Log SIEM integration metrics
    siem_metrics = {
        "timestamp": timestamp(),
        "alerts_processed": len(alerts),
        "alerts_sent_successfully": success_count,
        "processing_time_seconds": processing_time,
        "ai_enrichment": analysis is not None,
        "compliance_enrichment": compliance is not None
    }
    
    with open(f"{SIEM_LOG_DIR}/metrics.json", "w") as f:
        json.dump(siem_metrics, f, indent=2)
    
    print(f"[{timestamp()}] SIEM integration completed:")
    print(f"  - Processed: {len(alerts)} alerts")
    print(f"  - Successfully sent: {success_count} alerts")
    print(f"  - Processing time: {processing_time:.2f} seconds")

if __name__ == "__main__":
    main()