#!/usr/bin/env python3
import json
import os
import random
from datetime import datetime

# Directory for our project logs
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

def generate_mock_alerts(count=5):
    """Generate mock SSH brute force alerts for testing"""
    alerts = []
    
    for i in range(count):
        source_ip = f"192.168.122.{random.randint(10, 250)}"
        attempts = random.randint(5, 20)
        usernames = random.sample(["root", "admin", "user", "msfadmin", "kali"], random.randint(1, 3))
        
        alert = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "source_ip": source_ip,
            "attempt_count": attempts,
            "usernames": usernames,
            "alert_type": "brute_force",
            "rule_level": random.randint(5, 10),
            "description": f"Possible brute force attack from {source_ip}: {attempts} failed attempts"
        }
        alerts.append(alert)
    
    # Save alerts to file
    with open(f"{LOG_DIR}/alerts.json", "w") as f:
        json.dump(alerts, f, indent=2)
    
    print(f"Generated {len(alerts)} mock brute force alerts")
    for alert in alerts:
        print(f"  - {alert['source_ip']}: {alert['attempt_count']} attempts")
    
    return alerts

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate mock SSH brute force alerts")
    parser.add_argument("-c", "--count", type=int, default=5, help="Number of alerts to generate")
    args = parser.parse_args()
    
    generate_mock_alerts(args.count)
