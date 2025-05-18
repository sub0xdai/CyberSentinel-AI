# iso27001_mapper.py
import json
import os

class ISO27001Mapper:
    def __init__(self):
        self.controls = {
            "A.12.4": {
                "title": "Logging and monitoring",
                "controls": {
                    "A.12.4.1": "Event logging",
                    "A.12.4.2": "Protection of log information",
                    "A.12.4.3": "Administrator logs"
                }
            },
            "A.9.4": {
                "title": "System and application access control",
                "controls": {
                    "A.9.4.1": "Information access restriction",
                    "A.9.4.2": "Secure log-on procedures",
                    "A.9.4.3": "Password management system"
                }
            },
            "A.16.1": {
                "title": "Management of information security incidents",
                "controls": {
                    "A.16.1.1": "Responsibilities and procedures", 
                    "A.16.1.2": "Reporting information security events",
                    "A.16.1.5": "Response to information security incidents"
                }
            }
        }
    
    def map_alert_to_controls(self, alert_data):
        """Map an alert to relevant ISO 27001 controls"""
        mapped_controls = []
        
        # Simple mapping logic based on alert properties
        if "brute_force" in alert_data.get("attack_type", "").lower():
            mapped_controls.append({
                "control_id": "A.9.4.2",
                "control_name": self.controls["A.9.4"]["controls"]["A.9.4.2"],
                "section": self.controls["A.9.4"]["title"],
                "justification": "Brute force attack attempts indicate potential weaknesses in log-on procedures"
            })
            
        # Add more mappings based on alert properties
        
        return mapped_controls
    
    def generate_compliance_report(self, alerts_file="logs/alerts.json", output_file="logs/compliance/iso27001_report.json"):
        """Generate a compliance report based on alerts"""
        if not os.path.exists("logs/compliance"):
            os.makedirs("logs/compliance")
            
        # Load alerts
        with open(alerts_file, 'r') as f:
            alerts = json.load(f)
        
        compliance_report = {
            "framework": "ISO 27001:2013",
            "timestamp": alerts[-1]["timestamp"] if alerts else "",
            "mapped_controls": [],
            "compliance_summary": {}
        }
        
        # Process each alert
        for alert in alerts:
            mapped = self.map_alert_to_controls(alert)
            compliance_report["mapped_controls"].extend(mapped)
        
        # Summarize compliance
        control_ids = set()
        for control in compliance_report["mapped_controls"]:
            control_ids.add(control["control_id"])
            
        for section, details in self.controls.items():
            for control_id, control_name in details["controls"].items():
                if control_id in control_ids:
                    if section not in compliance_report["compliance_summary"]:
                        compliance_report["compliance_summary"][section] = {
                            "title": details["title"],
                            "controls_triggered": []
                        }
                    compliance_report["compliance_summary"][section]["controls_triggered"].append({
                        "id": control_id,
                        "name": control_name
                    })
        
        # Write report
        with open(output_file, 'w') as f:
            json.dump(compliance_report, f, indent=2)
            
        return compliance_report

# Usage example
if __name__ == "__main__":
    mapper = ISO27001Mapper()
    report = mapper.generate_compliance_report()
    print(f"Generated ISO 27001 compliance report with {len(report['mapped_controls'])} mapped controls")
