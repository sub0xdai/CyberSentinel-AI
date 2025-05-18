#!/usr/bin/env python3
# iso27001_mapper.py - ISO 27001 Compliance Mapper
# Part of CyberSentinel-AI

import json
import os
from datetime import datetime

# Banner display
print("┌───────────────────────────────────────────────┐")
print("│                                               │")
print("│ CyberSentinel-AI: Compliance Mapper          │")
print("│ ISO 27001 Control Mapping                    │")
print("│                                               │")
print("└───────────────────────────────────────────────┘")

class ISO27001Mapper:
    def __init__(self, logs_dir="logs"):
        self.logs_dir = logs_dir
        self.compliance_dir = f"{logs_dir}/compliance"
        
        # Ensure directories exist
        os.makedirs(self.compliance_dir, exist_ok=True)
        
        # Define ISO 27001 controls relevant to credential-based attacks
        self.controls = {
            "A.9": {
                "title": "Access Control",
                "controls": {
                    "A.9.2.1": "User registration and de-registration",
                    "A.9.2.4": "Management of secret authentication information",
                    "A.9.3.1": "Use of secret authentication information",
                    "A.9.4.2": "Secure log-on procedures",
                    "A.9.4.3": "Password management system",
                    "A.9.4.5": "Access control to program source code"
                }
            },
            "A.12": {
                "title": "Operations Security",
                "controls": {
                    "A.12.2.1": "Controls against malware",
                    "A.12.4.1": "Event logging",
                    "A.12.4.3": "Administrator and operator logs",
                    "A.12.6.1": "Management of technical vulnerabilities"
                }
            },
            "A.16": {
                "title": "Information Security Incident Management",
                "controls": {
                    "A.16.1.1": "Responsibilities and procedures",
                    "A.16.1.2": "Reporting information security events",
                    "A.16.1.5": "Response to information security incidents",
                    "A.16.1.7": "Collection of evidence"
                }
            }
        }
    
    def timestamp(self):
        """Generate current timestamp"""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def map_attack_to_controls(self, attack_type, severity):
        """Map an attack type and severity to ISO 27001 controls"""
        mapped_controls = []
        
        # Basic mappings based on attack type
        if "brute_force" in attack_type or "credential" in attack_type:
            # Access Control mappings
            mapped_controls.append({
                "control_id": "A.9.4.2", 
                "control_name": self.controls["A.9"]["controls"]["A.9.4.2"],
                "section": self.controls["A.9"]["title"],
                "justification": "Brute force attempts indicate weaknesses in log-on procedures"
            })
            
            mapped_controls.append({
                "control_id": "A.9.4.3", 
                "control_name": self.controls["A.9"]["controls"]["A.9.4.3"],
                "section": self.controls["A.9"]["title"],
                "justification": "Credential attacks exploit weak password management"
            })
            
        # Operational Security mappings (apply to all attacks)
        mapped_controls.append({
            "control_id": "A.12.4.1", 
            "control_name": self.controls["A.12"]["controls"]["A.12.4.1"],
            "section": self.controls["A.12"]["title"],
            "justification": "Event logging enabled detection of this security event"
        })
        
        # Incident Management mappings (apply to high severity attacks)
        if severity >= 7:
            mapped_controls.append({
                "control_id": "A.16.1.5", 
                "control_name": self.controls["A.16"]["controls"]["A.16.1.5"],
                "section": self.controls["A.16"]["title"],
                "justification": "High severity attack requiring incident response procedures"
            })
        
        return mapped_controls
    
    def generate_compliance_report(self):
        """Generate ISO 27001 compliance report from AI analysis"""
        print(f"[{self.timestamp()}] Generating ISO 27001 compliance report")
        
        # Initialize compliance report
        compliance_report = {
            "framework": "ISO 27001:2013",
            "timestamp": self.timestamp(),
            "mapped_controls": [],
            "compliance_summary": {}
        }
        
        # Load AI analysis
        ai_analysis_file = f"{self.logs_dir}/ai/openai_analysis.json"
        if not os.path.exists(ai_analysis_file):
            print(f"[{self.timestamp()}] Warning: AI analysis file not found. Using sample data.")
            
            # Create sample analysis data
            analysis = {
                "is_credential_attack": True,
                "severity": 7,
                "source": "192.168.122.100",
                "attack_type": "brute_force",
                "mitre_technique": "T1110 - Brute Force"
            }
        else:
            # Load actual analysis data
            try:
                with open(ai_analysis_file, 'r') as f:
                    analysis = json.load(f)
                print(f"[{self.timestamp()}] Loaded AI analysis from {ai_analysis_file}")
            except Exception as e:
                print(f"[{self.timestamp()}] Error loading AI analysis: {e}. Using sample data.")
                analysis = {
                    "is_credential_attack": True,
                    "severity": 7,
                    "source": "192.168.122.100",
                    "attack_type": "brute_force",
                    "mitre_technique": "T1110 - Brute Force"
                }
        
        # Also check for web alerts
        web_alerts_file = f"{self.logs_dir}/web_alerts.json"
        web_analysis = None
        if os.path.exists(web_alerts_file):
            try:
                with open(web_alerts_file, 'r') as f:
                    web_analysis = json.load(f)
                print(f"[{self.timestamp()}] Loaded web alerts from {web_alerts_file}")
            except Exception as e:
                print(f"[{self.timestamp()}] Error loading web alerts: {e}")
        
        # Map SSH credential attack to controls
        if analysis.get("is_credential_attack", False):
            attack_type = analysis.get("mitre_technique", "brute_force")
            severity = analysis.get("severity", 5)
            
            # Get mapped controls
            mapped_controls = self.map_attack_to_controls(attack_type, severity)
            compliance_report["mapped_controls"].extend(mapped_controls)
            
            print(f"[{self.timestamp()}] Mapped SSH credential attack to {len(mapped_controls)} controls")
        
        # Map web credential attack to controls if available
        if web_analysis:
            if isinstance(web_analysis, dict):
                web_attack_type = web_analysis.get("attack_type", "")
                web_severity = web_analysis.get("rule_level", 5)
                
                # Get mapped controls
                mapped_controls = self.map_attack_to_controls(web_attack_type, web_severity)
                compliance_report["mapped_controls"].extend(mapped_controls)
                
                print(f"[{self.timestamp()}] Mapped web attack to {len(mapped_controls)} controls")
        
        # Build compliance summary
        control_ids = set()
        for control in compliance_report["mapped_controls"]:
            control_ids.add(control["control_id"])
            
        for section_id, section_data in self.controls.items():
            for control_id, control_name in section_data["controls"].items():
                if control_id in control_ids:
                    if section_id not in compliance_report["compliance_summary"]:
                        compliance_report["compliance_summary"][section_id] = {
                            "title": section_data["title"],
                            "controls_triggered": []
                        }
                    compliance_report["compliance_summary"][section_id]["controls_triggered"].append({
                        "id": control_id,
                        "name": control_name
                    })
        
        # Save compliance report
        output_file = f"{self.compliance_dir}/iso27001_report.json"
        with open(output_file, "w") as f:
            json.dump(compliance_report, f, indent=2)
        
        print(f"[{self.timestamp()}] Compliance report saved to {output_file}")
        print(f"[{self.timestamp()}] Mapped {len(compliance_report['mapped_controls'])} controls across {len(compliance_report['compliance_summary'])} control sections")
        
        return compliance_report

# Run if executed directly
if __name__ == "__main__":
    mapper = ISO27001Mapper()
    report = mapper.generate_compliance_report()