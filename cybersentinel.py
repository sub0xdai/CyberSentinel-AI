#/usr/bin/env python3
import requests
import json
import os
from datetime import datetime
from dotenv import load_dotenv

# Configuration
# Load API key from environment variable or config file


# Try to load from .env file
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

def get_alerts():
    """Get alerts from the alerts.json file"""
    alerts_file = f"{LOG_DIR}/alerts.json"
    if not os.path.exists(alerts_file):
        print("No alerts file found. Run auth_monitor.py first.")
        return []
    
    with open(alerts_file, 'r') as f:
        return json.load(f)

def analyze_with_openai(alerts):
    """Send alerts to AI for analysis"""
    if not alerts:
        return {"message": "No alerts detected."}
    
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
        "model": "gpt-4o",  # Use GPT-4o for best results
        "messages": [
            {"role": "system", "content": "You are a cybersecurity AI analyst specializing in attack detection and compliance. Provide output in JSON format only."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.2  # Lower temperature for more focused responses
    }
    
    try:
        response = requests.post(OPENAI_API_URL, headers=headers, json=data)
        response_data = response.json()
        
        # Log the raw response for debugging
        with open(f"{AI_LOG_DIR}/openai_response_raw.json", "w") as f:
            json.dump(response_data, f, indent=2)
        
        response_text = response_data["choices"][0]["message"]["content"]
        
        # Try to extract JSON from response
        try:
            # Look for JSON block in response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                analysis = json.loads(json_str)
            else:
                # Fallback if no JSON found
                analysis = {"error": "No JSON found in response", "raw_response": response_text}
        except json.JSONDecodeError:
            analysis = {"error": "Could not parse JSON", "raw_response": response_text}
        
        # Log the parsed analysis
        with open(f"{AI_LOG_DIR}/openai_analysis.json", "w") as f:
            json.dump(analysis, f, indent=2)
        
        return analysis
        
    except Exception as e:
        error_msg = f"Error analyzing alerts: {str(e)}"
        with open(f"{AI_LOG_DIR}/error.log", "a") as f:
            f.write(f"[{datetime.now()}] {error_msg}\n")
        return {"error": error_msg}

def execute_response(analysis):
    """Execute simulated response based on OpenAI's analysis"""
    try:
        is_attack = analysis.get("is_credential_attack", False)
        severity = analysis.get("severity", 0)
        source_ip = analysis.get("source", "")
        mitre_technique = analysis.get("mitre_technique", "")
        app_impact = analysis.get("app_impact", "")
        
        # Log the analysis
        with open(f"{AI_LOG_DIR}/responses.log", "a") as f:
            f.write(f"[{datetime.now()}] Analysis: {json.dumps(analysis)}\n")
        
        # Skip response if not an attack or low severity
        if not is_attack:
            return "INFO: Not identified as a credential attack"
        
        # Simulate response based on severity
        if severity >= 8 and source_ip:
            # High severity - block IP (simulation)
            response_msg = f"CRITICAL: IP {source_ip} would be blocked due to high-severity attack (severity={severity})"
            
            # Simulate iptables command for documentation
            iptables_cmd = f"iptables -A INPUT -s {source_ip} -j DROP"
            
            # Log command that would be executed in a real system
            with open(f"{AI_LOG_DIR}/commands.log", "a") as f:
                f.write(f"[{datetime.now()}] Command: {iptables_cmd}\n")
            
            # Log additional information for HD-grade documentation
            with open(f"{AI_LOG_DIR}/compliance.log", "a") as f:
                f.write(f"[{datetime.now()}] MITRE ATT&CK: {mitre_technique}\n")
                f.write(f"[{datetime.now()}] APP Impact: {app_impact}\n")
                
        elif severity >= 5 and source_ip:
            # Medium severity - alert only
            response_msg = f"WARNING: Potential credential attack from {source_ip} detected (severity={severity})"
        else:
            # Low severity - log only
            response_msg = f"INFO: Low-severity suspicious activity logged (severity={severity})"
        
        # Log the response action
        with open(f"{AI_LOG_DIR}/responses.log", "a") as f:
            f.write(f"[{datetime.now()}] Response: {response_msg}\n")
        
        return response_msg
        
    except Exception as e:
        error_msg = f"Error executing response: {str(e)}"
        with open(f"{AI_LOG_DIR}/error.log", "a") as f:
            f.write(f"[{datetime.now()}] {error_msg}\n")
        return error_msg

def main():
    print(f"[{datetime.now()}] CyberSentinel-AI starting...")
    
    # Get alerts
    alerts = get_alerts()
    
    if not alerts:
        print("No alerts found.")
        return
    
    print(f"Found {len(alerts)} alerts.")
    
    # Analyze with OpenAI
    analysis = analyze_with_openai(alerts)
    
    # Execute response
    response = execute_response(analysis)
    
    # Print output
    print(response)
    
    # Log the run
    with open(f"{AI_LOG_DIR}/run.log", "a") as f:
        f.write(f"[{datetime.now()}] {response}\n")

if __name__ == "__main__":
    main()
