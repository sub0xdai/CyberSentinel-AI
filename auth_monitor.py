#!/usr/bin/env python3
import subprocess
import re
import json
import os
from datetime import datetime

# Directory for our project logs
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

def check_auth_logs():
    """Check auth logs for failed login attempts"""
    # Use native Kali commands to check auth log
    cmd = "grep 'Failed password' /var/log/auth.log | tail -n 50"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    # Process output
    failed_attempts = {}
    pattern = r'(\w+\s+\d+\s+\d+:\d+:\d+).*Failed password.*for (\w+) from (\d+\.\d+\.\d+\.\d+)'
    
    for line in result.stdout.splitlines():
        match = re.search(pattern, line)
        if match:
            timestamp, username, ip = match.groups()
            if ip not in failed_attempts:
                failed_attempts[ip] = {"count": 0, "usernames": set(), "timestamps": []}
            
            failed_attempts[ip]["count"] += 1
            failed_attempts[ip]["usernames"].add(username)
            failed_attempts[ip]["timestamps"].append(timestamp)
    
    # Generate alerts for IPs with multiple attempts
    alerts = []
    for ip, data in failed_attempts.items():
        if data["count"] >= 3:  # Alert threshold
            alert = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "source_ip": ip,
                "attempt_count": data["count"],
                "usernames": list(data["usernames"]),
                "alert_type": "brute_force",
                "rule_level": 7,
                "description": f"Possible brute force attack from {ip}: {data['count']} failed attempts"
            }
            alerts.append(alert)
    
    # Save alerts to file
    if alerts:
        with open(f"{LOG_DIR}/alerts.json", "w") as f:
            json.dump(alerts, f, indent=2)
        print(f"Found {len(alerts)} potential brute force attempts")
        for alert in alerts:
            print(f"  - {alert['source_ip']}: {alert['attempt_count']} attempts")
    else:
        print("No brute force attempts detected")
    
    return alerts

if __name__ == "__main__":
    print("Checking auth logs for brute force attempts...")
    check_auth_logs()
