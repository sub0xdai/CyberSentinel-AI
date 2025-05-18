#!/bin/bash
# respond.sh - Automated response actions for detected threats
# Part of CyberSentinel-AI

# Banner display
echo "┌───────────────────────────────────────────────┐"
echo "│                                               │"
echo "│ CyberSentinel-AI: Response System            │"
echo "│ Automated Threat Response                    │"
echo "│                                               │"
echo "└───────────────────────────────────────────────┘"

# Configuration parameters
LOG_DIR="logs"
ALERT_FILE="$LOG_DIR/alerts.json"
AI_ANALYSIS_FILE="$LOG_DIR/ai/openai_analysis.json"
RESPONSE_LOG="$LOG_DIR/ai/responses.log"
COMMAND_LOG="$LOG_DIR/ai/commands.log"
BLOCK_LIST="$LOG_DIR/blocked_ips.txt"

# Ensure log directory exists
mkdir -p "$LOG_DIR/ai"

# Timestamp for logs
timestamp() {
  date "+%Y-%m-%d %H:%M:%S"
}

echo "[$(timestamp)] Starting automated response system"

# Check if analysis file exists
if [ ! -f "$AI_ANALYSIS_FILE" ]; then
  echo "[$(timestamp)] No AI analysis found. Run cybersentinel.py first."
  exit 1
fi

# Extract key information from AI analysis
is_attack=$(grep -o '"is_credential_attack":\s*\(true\|false\)' "$AI_ANALYSIS_FILE" | grep -o '\(true\|false\)') 
severity=$(grep -o '"severity":\s*[0-9]*' "$AI_ANALYSIS_FILE" | grep -o '[0-9]*')
source_ip=$(grep -o '"source":\s*"[^"]*"' "$AI_ANALYSIS_FILE" | grep -o '"[^"]*"' | tr -d '"')

# Log analysis details
echo "[$(timestamp)] AI Analysis Results:" | tee -a "$RESPONSE_LOG"
echo "  - Credential Attack: $is_attack" | tee -a "$RESPONSE_LOG"
echo "  - Severity: $severity/10" | tee -a "$RESPONSE_LOG"
echo "  - Source IP: $source_ip" | tee -a "$RESPONSE_LOG"

# Check if no attack detected
if [ "$is_attack" != "true" ]; then
  echo "[$(timestamp)] INFO: Not identified as a credential attack" | tee -a "$RESPONSE_LOG"
  exit 0
fi

# Check if source IP is missing
if [ -z "$source_ip" ] || [ "$source_ip" == "null" ]; then
  echo "[$(timestamp)] WARNING: No source IP identified in analysis" | tee -a "$RESPONSE_LOG"
  exit 1
fi

# Execute response based on severity
if [ "$severity" -ge "8" ]; then
  # High severity - block IP
  echo "[$(timestamp)] CRITICAL: Blocking IP $source_ip due to high-severity attack (severity=$severity)" | tee -a "$RESPONSE_LOG"
  
  # Check if already blocked
  if grep -q "$source_ip" "$BLOCK_LIST" 2>/dev/null; then
    echo "[$(timestamp)] NOTE: IP $source_ip is already blocked" | tee -a "$RESPONSE_LOG"
  else
    # Create iptables command
    iptables_cmd="iptables -A INPUT -s $source_ip -j DROP"
    
    # Log command
    echo "[$(timestamp)] Command: $iptables_cmd" | tee -a "$COMMAND_LOG"
    
    # Execute command (uncomment to actually block)
    # sudo $iptables_cmd
    
    # Add to block list
    echo "$source_ip" >> "$BLOCK_LIST"
    
    echo "[$(timestamp)] IP blocking simulated. To actually block, uncomment the sudo line in this script." | tee -a "$RESPONSE_LOG"
  fi
  
elif [ "$severity" -ge "5" ]; then
  # Medium severity - alert only
  echo "[$(timestamp)] WARNING: Potential credential attack from $source_ip detected (severity=$severity)" | tee -a "$RESPONSE_LOG"
else
  # Low severity - log only
  echo "[$(timestamp)] INFO: Low-severity suspicious activity logged from $source_ip (severity=$severity)" | tee -a "$RESPONSE_LOG"
fi

# Extract and log compliance information
mitre_technique=$(grep -o '"mitre_technique":\s*"[^"]*"' "$AI_ANALYSIS_FILE" | cut -d'"' -f4)
app_impact=$(grep -o '"app_impact":\s*"[^"]*"' "$AI_ANALYSIS_FILE" | cut -d'"' -f4)

echo "[$(timestamp)] Compliance Information:" | tee -a "$RESPONSE_LOG"
echo "  - MITRE ATT&CK: $mitre_technique" | tee -a "$RESPONSE_LOG"
echo "  - APP Impact: $app_impact" | tee -a "$RESPONSE_LOG"

echo "[$(timestamp)] Response completed" | tee -a "$RESPONSE_LOG"
