#!/bin/bash
# cybersentinel.sh - Main workflow script for CyberSentinel-AI
# Part of CyberSentinel-AI

# Handle broken pipe errors gracefully
trap '' PIPE
# Suppress Python pipe errors
export PYTHONIOENCODING=utf-8
export PYTHONUNBUFFERED=1

# Banner display
echo "┌───────────────────────────────────────────────┐"
echo "│                                               │"
echo "│ CyberSentinel-AI: Complete Workflow          │"
echo "│ Attack Detection, Analysis, and Response     │"
echo "│                                               │"
echo "└───────────────────────────────────────────────┘"

# Configuration parameters
LOG_DIR="logs"
SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"

# Ensure log directory exists
mkdir -p "$LOG_DIR"

# Timestamp for logs
timestamp() {
  date "+%Y-%m-%d %H:%M:%S"
}

# Function to check if a command exists
command_exists() {
  command -v "$1" >/dev/null 2>&1
}

# Check for required tools
if ! command_exists hydra; then
  echo "[$(timestamp)] ERROR: Hydra is not installed. Please install it with 'sudo apt install hydra'"
  exit 1
fi

if ! command_exists python3; then
  echo "[$(timestamp)] ERROR: Python 3 is not installed. Please install it with 'sudo apt install python3'"
  exit 1
fi

if ! command_exists pip; then
  echo "[$(timestamp)] ERROR: pip is not installed. Please install it with 'sudo apt install python3-pip'"
  exit 1
fi

# Check for required Python packages
if ! pip list | grep -q "python-dotenv"; then
  echo "[$(timestamp)] python-dotenv not found. Installing..."
  pip install python-dotenv
fi

if ! pip list | grep -q "requests"; then
  echo "[$(timestamp)] requests not found. Installing..."
  pip install requests
fi

# Check for .env file
if [ ! -f "$SCRIPT_DIR/.env" ]; then
  echo "[$(timestamp)] WARNING: No .env file found. AI analysis will fail without API key."
  echo "[$(timestamp)] Please create a .env file with your OpenAI API key:"
  echo "OPENAI_API_KEY=your_api_key_here"
  
  # Ask if user wants to continue
  read -p "Continue without API key? (y/n): " -n 1 -r
  echo
  if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 1
  fi
fi

# Make scripts executable if they aren't already
chmod +x "$SCRIPT_DIR/run_attack.sh"
chmod +x "$SCRIPT_DIR/monitor_auth.sh"
chmod +x "$SCRIPT_DIR/monitor_web_auth.sh"
chmod +x "$SCRIPT_DIR/respond.sh"
chmod +x "$SCRIPT_DIR/cybersentinel.py"
chmod +x "$SCRIPT_DIR/iso27001_mapper.py"
chmod +x "$SCRIPT_DIR/metrics_analyzer.py"
chmod +x "$SCRIPT_DIR/generate_dashboard.sh"

# Start workflow
echo "[$(timestamp)] Starting CyberSentinel-AI workflow"

# Execute attack simulation
echo
echo "[$(timestamp)] PHASE 1: Attack Simulation"
read -p "Run attack simulation? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
  # Get attack parameters
  read -p "Target IP [192.168.122.167]: " target
  target=${target:-"192.168.122.167"}
  
  read -p "Username [msfadmin]: " username
  username=${username:-"msfadmin"}
  
  read -p "Password list [passwords.txt]: " wordlist
  wordlist=${wordlist:-"passwords.txt"}
  
  read -p "Concurrent tasks [4]: " tasks
  tasks=${tasks:-4}
  
  # Run attack
  "$SCRIPT_DIR/run_attack.sh" "$target" "$username" "$wordlist" "$tasks"
else
  echo "[$(timestamp)] Skipping attack simulation"
fi

# Execute monitoring (multiple detection vectors)
echo
echo "[$(timestamp)] PHASE 2: Multi-Vector Monitoring"
echo "  1. SSH Authentication Log Monitoring"
echo "  2. Web Authentication Log Monitoring"
echo "  3. Both monitoring types"
echo "  4. Skip monitoring"
read -p "Choose monitoring type [3]: " monitoring_option
monitoring_option=${monitoring_option:-3}

case $monitoring_option in
  1)
    # Run SSH monitoring only
    read -p "SSH Log file [logs/auth.log]: " ssh_logfile
    ssh_logfile=${ssh_logfile:-"logs/auth.log"}
    
    read -p "Threshold [3]: " ssh_threshold
    ssh_threshold=${ssh_threshold:-3}
    
    echo "[$(timestamp)] Running SSH authentication monitoring"
    "$SCRIPT_DIR/monitor_auth.sh" "$ssh_logfile" "$ssh_threshold"
    ;;
  2)
    # Run web monitoring only
    read -p "Web Log file [logs/apache_access.log]: " web_logfile
    web_logfile=${web_logfile:-"logs/apache_access.log"}
    
    read -p "Threshold [5]: " web_threshold
    web_threshold=${web_threshold:-5}
    
    echo "[$(timestamp)] Running web authentication monitoring"
    "$SCRIPT_DIR/monitor_web_auth.sh" "$web_logfile" "$web_threshold"
    ;;
  3)
    # Run both monitoring types
    read -p "SSH Log file [logs/auth.log]: " ssh_logfile
    ssh_logfile=${ssh_logfile:-"logs/auth.log"}
    
    read -p "SSH Threshold [3]: " ssh_threshold
    ssh_threshold=${ssh_threshold:-3}
    
    read -p "Web Log file [logs/apache_access.log]: " web_logfile
    web_logfile=${web_logfile:-"logs/apache_access.log"}
    
    read -p "Web Threshold [5]: " web_threshold
    web_threshold=${web_threshold:-5}
    
    echo "[$(timestamp)] Running SSH authentication monitoring"
    "$SCRIPT_DIR/monitor_auth.sh" "$ssh_logfile" "$ssh_threshold"
    
    echo "[$(timestamp)] Running web authentication monitoring"
    "$SCRIPT_DIR/monitor_web_auth.sh" "$web_logfile" "$web_threshold"
    ;;
  4)
    echo "[$(timestamp)] Skipping monitoring phase"
    ;;
  *)
    echo "[$(timestamp)] Invalid option. Skipping monitoring phase"
    ;;
esac

# Execute AI analysis
echo
echo "[$(timestamp)] PHASE 3: AI Analysis"
read -p "Run AI analysis? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
  # Run AI analysis
  python3 "$SCRIPT_DIR/cybersentinel.py"
else
  echo "[$(timestamp)] Skipping AI analysis"
fi

# Execute response actions
echo
echo "[$(timestamp)] PHASE 4: Automated Response"
read -p "Run automated response? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
  # Enable actual blocking?
  read -p "Enable actual IP blocking? (CAUTION!) (y/n): " -n 1 -r real_blocking
  echo
  
  # Run response with or without actual blocking
  if [[ $real_blocking =~ ^[Yy]$ ]]; then
    echo "[$(timestamp)] Running response with REAL IP blocking"
    "$SCRIPT_DIR/respond.sh" "real_blocking"
  else
    echo "[$(timestamp)] Running response in simulation mode"
    "$SCRIPT_DIR/respond.sh"
  fi
else
  echo "[$(timestamp)] Skipping automated response"
fi

# Execute compliance mapping and metrics generation
echo
echo "[$(timestamp)] PHASE 5: Compliance & Metrics"
read -p "Run compliance mapping & metrics generation? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
  # Run ISO 27001 compliance mapping
  echo "[$(timestamp)] Running ISO 27001 compliance mapping"
  python3 "$SCRIPT_DIR/iso27001_mapper.py"
  
  # Run metrics analyzer
  echo "[$(timestamp)] Running security metrics analysis"
  python3 "$SCRIPT_DIR/metrics_analyzer.py"
  
  # Generate dashboard
  read -p "Generate visual dashboard? (y/n): " -n 1 -r
  echo
  if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "[$(timestamp)] Generating security dashboard"
    "$SCRIPT_DIR/generate_dashboard.sh"
  else
    echo "[$(timestamp)] Skipping dashboard generation"
  fi
else
  echo "[$(timestamp)] Skipping compliance & metrics phase"
fi

# Execute SIEM integration
echo
echo "[$(timestamp)] PHASE 6: SIEM Integration"
read -p "Send data to Wazuh SIEM? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
  # Configure SIEM connection
  read -p "Wazuh API URL [https://10.0.1.30:55000]: " wazuh_url
  wazuh_url=${wazuh_url:-"https://10.0.1.30:55000"}
  export WAZUH_API_URL="$wazuh_url"
  
  read -p "Wazuh API User [wazuh]: " wazuh_user
  wazuh_user=${wazuh_user:-"wazuh"}
  export WAZUH_API_USER="$wazuh_user"
  
  read -p "Wazuh API Password [wazuh]: " wazuh_password
  wazuh_password=${wazuh_password:-"wazuh"}
  export WAZUH_API_PASSWORD="$wazuh_password"
  
  # Run SIEM integration
  echo "[$(timestamp)] Running Wazuh SIEM integration"
  python3 "$SCRIPT_DIR/wazuh_integration.py"
else
  echo "[$(timestamp)] Skipping SIEM integration"
fi

# Display workflow summary
echo
echo "┌───────────────────────────────────────────────┐"
echo "│ Workflow Summary                              │"
echo "├───────────────────────────────────────────────┤"

# Check if attack was successful
if [ -f "$LOG_DIR/attack.log" ]; then
  SUCCESSFUL=$(grep "host:" "$LOG_DIR/attack.log" | grep "password:" | wc -l)
  echo "│ Attack: Completed ($SUCCESSFUL successful logins)"
else
  echo "│ Attack: Not executed"
fi

# Check if monitoring found alerts
if [ -f "$LOG_DIR/alerts.json" ]; then
  if grep -q "source_ip" "$LOG_DIR/alerts.json"; then
    echo "│ Monitoring: Alerts detected"
  else
    echo "│ Monitoring: No alerts detected"
  fi
else
  echo "│ Monitoring: Not executed"
fi

# Check if AI analysis was performed or response was executed
AI_EXECUTED=false
ATTACK_CONFIRMED=false
SEVERITY=""

# First, check the analysis summary text output in stdout capture or analysis log file
if [ -f "$LOG_DIR/ai/openai_analysis.json" ]; then
  AI_EXECUTED=true
  if grep -q "is_credential_attack.*true" "$LOG_DIR/ai/openai_analysis.json" || 
     grep -q "Credential Attack: Yes" "$LOG_DIR/ai/openai_analysis.json" ||
     grep -q '"attack":.*true' "$LOG_DIR/ai/openai_analysis.json"; then
    ATTACK_CONFIRMED=true
    SEVERITY=$(grep -o '"severity":\s*[0-9]*' "$LOG_DIR/ai/openai_analysis.json" | grep -o '[0-9]*')
  fi
fi

# Second, check the response log - which is more reliable since it's where actions are taken
if [ -f "$LOG_DIR/ai/responses.log" ]; then
  AI_EXECUTED=true
  if grep -q "Credential Attack: true" "$LOG_DIR/ai/responses.log" || 
     grep -q "WARNING" "$LOG_DIR/ai/responses.log" || 
     grep -q "CRITICAL" "$LOG_DIR/ai/responses.log"; then
    ATTACK_CONFIRMED=true
    SEVERITY=$(grep -o "severity=[0-9]*" "$LOG_DIR/ai/responses.log" | grep -o '[0-9]*' | head -1)
    if [ -z "$SEVERITY" ]; then
      SEVERITY=$(grep -o "Severity: [0-9]*" "$LOG_DIR/ai/responses.log" | grep -o '[0-9]*' | head -1)
    fi
  fi
fi

# Display the appropriate AI analysis status
if [ "$AI_EXECUTED" = true ]; then
  if [ "$ATTACK_CONFIRMED" = true ]; then
    if [ -n "$SEVERITY" ]; then
      echo "│ AI Analysis: Attack confirmed (Severity: $SEVERITY/10)"
    else
      echo "│ AI Analysis: Attack confirmed"
    fi
  else
    echo "│ AI Analysis: No attack confirmed"
  fi
else
  echo "│ AI Analysis: Not executed"
fi

# Check if response was executed
if [ -f "$LOG_DIR/ai/responses.log" ]; then
  if grep -q "CRITICAL" "$LOG_DIR/ai/responses.log"; then
    echo "│ Response: Critical response triggered"
  elif grep -q "WARNING" "$LOG_DIR/ai/responses.log"; then
    echo "│ Response: Warning response triggered"
  elif grep -q "INFO" "$LOG_DIR/ai/responses.log"; then
    echo "│ Response: Informational response triggered"
  else
    echo "│ Response: No response triggered"
  fi
else
  echo "│ Response: Not executed"
fi

echo "└───────────────────────────────────────────────┘"

echo "[$(timestamp)] CyberSentinel-AI workflow completed"
