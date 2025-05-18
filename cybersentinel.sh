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
chmod +x "$SCRIPT_DIR/respond.sh"
chmod +x "$SCRIPT_DIR/cybersentinel.py"

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

# Execute monitoring
echo
echo "[$(timestamp)] PHASE 2: Log Monitoring"
read -p "Run log monitoring? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
  # Get monitoring parameters
  read -p "Log file [logs/auth.log]: " logfile
  logfile=${logfile:-"logs/auth.log"}
  
  read -p "Threshold [3]: " threshold
  threshold=${threshold:-3}
  
  # Run monitoring
  "$SCRIPT_DIR/monitor_auth.sh" "$logfile" "$threshold"
else
  echo "[$(timestamp)] Skipping log monitoring"
fi

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
  # Run response
  "$SCRIPT_DIR/respond.sh"
else
  echo "[$(timestamp)] Skipping automated response"
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

# Check if AI analysis was performed
if [ -f "$LOG_DIR/ai/openai_analysis.json" ]; then
  # Use multi-method detection - similar to respond.sh
  if grep -q "is_credential_attack.*true" "$LOG_DIR/ai/openai_analysis.json" || 
     grep -q "Credential Attack: Yes" "$LOG_DIR/ai/openai_analysis.json" ||
     grep -q '"attack":.*true' "$LOG_DIR/ai/openai_analysis.json"; then
    SEVERITY=$(grep -o '"severity":\s*[0-9]*' "$LOG_DIR/ai/openai_analysis.json" | grep -o '[0-9]*')
    echo "│ AI Analysis: Attack confirmed (Severity: $SEVERITY/10)"
  else
    # Check response log as a last resort
    if [ -f "$LOG_DIR/ai/responses.log" ] && grep -q "Credential attack detected" "$LOG_DIR/ai/responses.log"; then
      SEVERITY=$(grep -o "severity=[0-9]*" "$LOG_DIR/ai/responses.log" | grep -o '[0-9]*' | head -1)
      echo "│ AI Analysis: Attack confirmed (Severity: $SEVERITY/10)"
    else
      echo "│ AI Analysis: No attack confirmed"
    fi
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
