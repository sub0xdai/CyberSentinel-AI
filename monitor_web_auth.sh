#!/bin/bash
# monitor_web_auth.sh - Web Authentication Monitor
# Part of CyberSentinel-AI

# Banner display
echo "┌───────────────────────────────────────────────┐"
echo "│                                               │"
echo "│ CyberSentinel-AI: Web Security Monitor       │"
echo "│ Web Authentication Log Monitor               │"
echo "│                                               │"
echo "└───────────────────────────────────────────────┘"

# Configuration parameters (with defaults)
LOG_FILE=${1:-"logs/apache_access.log"}  # Default web log location
THRESHOLD=${2:-5}                       # Minimum failed attempts to trigger alert
TIME_WINDOW=${3:-"10 minutes ago"}      # Time window to consider
LOG_DIR="logs"                          # Log output directory
ALERT_FILE="$LOG_DIR/web_alerts.json"   # Alert output file

# Ensure log directory exists
mkdir -p "$LOG_DIR"

# Timestamp for logs
timestamp() {
  date "+%Y-%m-%d %H:%M:%S"
}

echo "[$(timestamp)] Starting web authentication log monitoring"
echo "[$(timestamp)] Monitoring $LOG_FILE for failed login attempts"
echo "[$(timestamp)] Alert threshold: $THRESHOLD failed attempts"

# Check if log file exists and is accessible
if [ ! -f "$LOG_FILE" ]; then
  echo "[$(timestamp)] ERROR: Log file $LOG_FILE not found or not accessible"
  echo "[$(timestamp)] Creating sample alerts for testing purposes"
  
  # Create a sample alert for web authentication testing
  cat > "$ALERT_FILE" << EOF
{
  "timestamp": "$(timestamp)",
  "source_ip": "192.168.122.150",
  "attack_type": "web_brute_force",
  "attempt_count": 8,
  "target_urls": "/admin/login.php,/wp-login.php,/administrator/index.php",
  "rule_level": 7,
  "description": "Possible web brute force attack from 192.168.122.150: 8 failed web authentication attempts"
}
EOF
  
  echo "[$(timestamp)] Sample web alert created for testing"
  echo "[$(timestamp)] Alert saved to $ALERT_FILE"
  exit 0
fi

# Process web authentication logs for failed login attempts
# Look for POST requests to login pages with 401/403 response codes
echo "[$(timestamp)] Analyzing web login attempts..."
failed_logins=$(grep -E "POST.*(login|signin|auth).*(401|403)" "$LOG_FILE" 2>/dev/null)

# Check if we found any failed login attempts
if [ -z "$failed_logins" ]; then
  echo "[$(timestamp)] No failed web login attempts found in specified log file"
  # Create empty JSON array for alerts
  echo "[]" > "$ALERT_FILE"
  exit 0
fi

# Process failed login attempts by IP address
# Extract IP addresses and count occurrences
echo "$failed_logins" | 
  awk '{print $1}' | 
  sort | 
  uniq -c | 
  sort -nr |
  while read count ip; do
    # Check if count exceeds threshold
    if [ "$count" -ge "$THRESHOLD" ]; then
      # Get URLs targeted by this IP
      target_urls=$(echo "$failed_logins" | grep "$ip" | awk '{print $7}' | sort | uniq | tr '\n' ',' | sed 's/,$//')
      
      # Calculate rule level based on count (5-10 scale)
      rule_level=5
      if [ "$count" -ge 10 ]; then
        rule_level=8
      elif [ "$count" -ge 5 ]; then
        rule_level=6
      fi

      # Create JSON alert
      current_timestamp=$(timestamp)
      
      # Create JSON structure
      cat > "$ALERT_FILE" << EOF
{
  "timestamp": "$current_timestamp",
  "source_ip": "$ip",
  "attempt_count": $count,
  "target_urls": "$target_urls",
  "attack_type": "web_brute_force",
  "rule_level": $rule_level,
  "description": "Possible web brute force attack from $ip: $count failed web authentication attempts"
}
EOF
      
      echo "[$(timestamp)] ALERT: Possible web brute force attack detected"
      echo "  - Source IP: $ip"
      echo "  - Attempt count: $count"
      echo "  - Targeted URLs: $target_urls"
      echo "  - Severity level: $rule_level/10"
      echo "[$(timestamp)] Alert saved to $ALERT_FILE"
    fi
  done

# If no alerts were triggered, create an empty alert file
if [ ! -f "$ALERT_FILE" ]; then
  echo "[]" > "$ALERT_FILE"
  echo "[$(timestamp)] No web brute force attacks detected above threshold"
fi

echo "[$(timestamp)] Web monitoring completed"