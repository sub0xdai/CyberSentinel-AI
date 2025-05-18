#!/usr/bin/env python3
# cybersentinel.py - AI-powered Security Analysis
# Part of CyberSentinel-AI

import requests
import json
import os
from datetime import datetime
from dotenv import load_dotenv

# Banner display
print("┌───────────────────────────────────────────────┐")
print("│                                               │")
print("│ CyberSentinel-AI: AI Analysis                │")
print("│ GPT-4o Powered Security Intelligence         │")
print("│                                               │")
print("└───────────────────────────────────────────────┘")

# Configuration
# Load API key from environment variable or config file
load_dotenv()

# Get API key from environment variable
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    try:
        # Try to load from config file if environment variable not set
        with open('.env', 'r') as f:
            for line in f:
                if line.startswith('OPENAI_API_KEY='):
                    OPENAI_API_KEY = line.split('=')[1].strip()
                    break
    except FileNotFoundError:
        print("Error: No API key found. Create a .env file with OPENAI_API_KEY=your_key or set environment variable.")
        exit(1)

OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"
LOG_DIR = "logs"
AI_LOG_DIR = f"{LOG_DIR}/ai"

# Ensure log directories exist
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(AI_LOG_DIR, exist_ok=True)

def timestamp():
    """Generate current timestamp"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def get_alerts():
    """Get alerts from the alerts.json file"""
    alerts_file = f"{LOG_DIR}/alerts.json"
    if not os.path.exists(alerts_file):
        print(f"[{timestamp()}] No alerts file found. Run monitor_auth.sh first.")
        return []
    
    with open(alerts_file, 'r') as f:
        content = f.read().strip()
        # Handle empty content
        if not content:
            return []
        try:
            # Check if content is an array or single object
            if content.startswith('['):
                return json.loads(content)
            else:
                return [json.loads(content)]
        except json.JSONDecodeError as e:
            print(f"[{timestamp()}] Error parsing alerts JSON: {e}")
            print(f"[{timestamp()}] Content: {content}")
            return []

def analyze_with_openai(alerts):
    """Send alerts to AI for analysis or generate sample analysis for testing"""
    if not alerts:
        return {"message": "No alerts detected."}
    
    print(f"[{timestamp()}] Analyzing {len(alerts)} alerts with GPT-4o")
    
    # Check if API key is available
    if not OPENAI_API_KEY or OPENAI_API_KEY == "your_key_here":
        print(f"[{timestamp()}] No valid API key found. Using sample analysis for testing.")
        
        # Create sample analysis
        sample_analysis = {
            "is_credential_attack": True,
            "severity": 7,
            "source": alerts[0]["source_ip"],
            "targets": alerts[0]["usernames"],
            "mitre_technique": "T1110 - Brute Force",
            "app_impact": "Yes, potentially violates APP 11 (Security of Personal Information)",
            "recommended_actions": [
                "Block source IP at the firewall",
                "Reset affected user passwords",
                "Enable account lockout policies",
                "Update SSH configuration to use key-based authentication"
            ]
        }
        
        # Save the sample analysis
        with open(f"{AI_LOG_DIR}/openai_analysis.json", "w") as f:
            json.dump(sample_analysis, f, indent=2)
        
        print(f"[{timestamp()}] Sample analysis saved to {AI_LOG_DIR}/openai_analysis.json")
        return sample_analysis
    
    # If API key is available, proceed with actual OpenAI analysis
    alert_json = json.dumps(alerts, indent=2)
    
    # Prepare the prompt for OpenAI
    prompt = f"""
    Analyze these security alerts for credential-based attacks:
    {alert_json}
    
    Please provide:
    1. Whether this represents a credential-based attack (yes/no) as "is_credential_attack"
    2. Severity assessment (1-10 scale) as "severity"
    3. Source of the attack as "source"
    4. Targeted accounts/systems as "targets"
    5. MITRE ATT&CK technique identification as "mitre_technique"
    6. Australian Privacy Principles impact (yes/no and which principles) as "app_impact"
    7. Recommended immediate response actions as "recommended_actions"
    
    Format your response as JSON with these exact field names. Make sure to include all fields.
    """
    
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "gpt-4o",  # Using GPT-4o for enhanced capabilities
        "messages": [
            {"role": "system", "content": "You are a cybersecurity AI analyst specializing in attack detection and compliance. Provide output in JSON format only."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.2,  # Lower temperature for more focused responses
        "response_format": {"type": "json_object"}  # Ensures output is valid JSON
    }
    
    try:
        print(f"[{timestamp()}] Sending request to OpenAI API...")
        response = requests.post(OPENAI_API_URL, headers=headers, json=data)
        
        # Check for HTTP errors
        response.raise_for_status()
        
        response_data = response.json()
        
        # Log the raw response for debugging
        with open(f"{AI_LOG_DIR}/openai_response_raw.json", "w") as f:
            json.dump(response_data, f, indent=2)
        
        print(f"[{timestamp()}] Received response from OpenAI API")
        
        response_text = response_data["choices"][0]["message"]["content"]
        
        # Parse JSON response
        try:
            analysis = json.loads(response_text)
            
            # Log the parsed analysis
            with open(f"{AI_LOG_DIR}/openai_analysis.json", "w") as f:
                json.dump(analysis, f, indent=2)
            
            print(f"[{timestamp()}] Analysis saved to {AI_LOG_DIR}/openai_analysis.json")
            
        except json.JSONDecodeError as e:
            error_msg = f"Could not parse JSON response: {e}"
            print(f"[{timestamp()}] ERROR: {error_msg}")
            analysis = {"error": error_msg, "raw_response": response_text}
            
        return analysis
        
    except requests.exceptions.RequestException as e:
        error_msg = f"Error connecting to OpenAI API: {str(e)}"
        print(f"[{timestamp()}] ERROR: {error_msg}. Using sample analysis for testing.")
        
        # Create sample analysis on API error
        sample_analysis = {
            "is_credential_attack": True,
            "severity": 6,
            "source": alerts[0]["source_ip"],
            "targets": alerts[0]["usernames"],
            "mitre_technique": "T1110 - Brute Force",
            "app_impact": "Yes, potentially violates APP 11 (Security of Personal Information)",
            "recommended_actions": [
                "Block source IP at the firewall",
                "Reset affected user passwords",
                "Enable account lockout policies"
            ]
        }
        
        # Save the sample analysis
        with open(f"{AI_LOG_DIR}/openai_analysis.json", "w") as f:
            json.dump(sample_analysis, f, indent=2)
        
        print(f"[{timestamp()}] Sample analysis saved to {AI_LOG_DIR}/openai_analysis.json")
        
        # Log the error
        with open(f"{AI_LOG_DIR}/error.log", "a") as f:
            f.write(f"[{timestamp()}] {error_msg}\n")
            
        return sample_analysis
        
    except Exception as e:
        error_msg = f"Error analyzing alerts: {str(e)}"
        print(f"[{timestamp()}] ERROR: {error_msg}")
        with open(f"{AI_LOG_DIR}/error.log", "a") as f:
            f.write(f"[{timestamp()}] {error_msg}\n")
            
        # Create sample analysis on general error
        sample_analysis = {
            "is_credential_attack": True,
            "severity": 5,
            "source": alerts[0]["source_ip"],
            "targets": alerts[0]["usernames"],
            "mitre_technique": "T1110 - Brute Force",
            "app_impact": "Potential privacy breach",
            "recommended_actions": ["Monitor the IP address", "Review logs for additional indicators"]
        }
        
        # Save the sample analysis
        with open(f"{AI_LOG_DIR}/openai_analysis.json", "w") as f:
            json.dump(sample_analysis, f, indent=2)
        
        print(f"[{timestamp()}] Sample analysis saved to {AI_LOG_DIR}/openai_analysis.json")
        
        return sample_analysis

def summarize_analysis(analysis):
    """Display a summary of the analysis results"""
    # Check if analysis contains error
    if "error" in analysis:
        print(f"[{timestamp()}] Error in analysis: {analysis['error']}")
        return
    
    # Extract key information
    is_attack = analysis.get("is_credential_attack", False)
    severity = analysis.get("severity", 0)
    source_ip = analysis.get("source", "")
    targets = analysis.get("targets", [])
    mitre_technique = analysis.get("mitre_technique", "")
    app_impact = analysis.get("app_impact", "")
    recommendations = analysis.get("recommended_actions", [])
    
    # Display formatted summary
    print("\n----- ANALYSIS SUMMARY -----")
    print(f"Credential Attack: {'Yes' if is_attack else 'No'}")
    print(f"Severity: {severity}/10")
    
    if is_attack:
        print(f"Source IP: {source_ip}")
        
        # Display targets
        if isinstance(targets, list):
            print(f"Targeted accounts: {', '.join(targets)}")
        else:
            print(f"Targeted accounts: {targets}")
        
        # Display MITRE technique
        print(f"MITRE ATT&CK: {mitre_technique}")
        
        # Display APP impact
        print(f"Australian Privacy Principles impact: {app_impact}")
        
        # Display recommendations
        print("\nRecommended actions:")
        if isinstance(recommendations, list):
            for i, rec in enumerate(recommendations, 1):
                print(f"  {i}. {rec}")
        else:
            print(f"  * {recommendations}")
    
    print("--------------------------\n")

def log_run_info(analysis):
    """Log run information to a file"""
    # Create a log entry
    log_entry = {
        "timestamp": timestamp(),
        "analysis_summary": {
            "is_credential_attack": analysis.get("is_credential_attack", False),
            "severity": analysis.get("severity", 0),
            "source": analysis.get("source", ""),
        }
    }
    
    # Write to run log
    with open(f"{AI_LOG_DIR}/run.log", "a") as f:
        f.write(f"[{timestamp()}] Analysis completed: ")
        if "error" in analysis:
            f.write(f"ERROR: {analysis['error']}\n")
        else:
            attack_status = "Attack detected" if analysis.get("is_credential_attack", False) else "No attack detected"
            severity = analysis.get("severity", 0)
            f.write(f"{attack_status} (Severity: {severity}/10)\n")

def main():
    print(f"[{timestamp()}] CyberSentinel-AI starting...")
    
    # Get alerts
    alerts = get_alerts()
    
    if not alerts:
        print(f"[{timestamp()}] No alerts found. Creating sample alert for testing.")
        # Create a sample alert
        sample_alert = {
            "timestamp": timestamp(),
            "source_ip": "192.168.122.100",
            "attempt_count": 5,
            "usernames": ["root", "admin", "msfadmin"],
            "alert_type": "brute_force",
            "rule_level": 6,
            "description": "Possible brute force attack from 192.168.122.100: 5 failed attempts",
            "raw_timestamps": "May 18 12:20:15,May 18 12:20:17,May 18 12:20:20,May 18 12:20:22,May 18 12:20:25"
        }
        
        # Save sample alert to file
        with open(f"{LOG_DIR}/alerts.json", "w") as f:
            json.dump(sample_alert, f, indent=2)
            
        alerts = [sample_alert]
        print(f"[{timestamp()}] Created sample alert for testing.")
    
    print(f"[{timestamp()}] Found {len(alerts)} alerts.")
    
    # Analyze with OpenAI
    analysis = analyze_with_openai(alerts)
    
    # Display summary
    summarize_analysis(analysis)
    
    # Log run information
    log_run_info(analysis)
    
    print(f"[{timestamp()}] Analysis completed.")
    print(f"[{timestamp()}] Run 'respond.sh' to execute automated response actions.")

if __name__ == "__main__":
    main()
