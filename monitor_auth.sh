#!/bin/bash
# monitor_auth.sh - Authentication Log Monitor for SSH Brute Force Detection
# Part of CyberSentinel-AI

# Banner display
echo "┌───────────────────────────────────────────────┐"
echo "│                                               │"
echo "│ CyberSentinel-AI: Security Monitor           │"
echo "│ Authentication Log Monitor                   │"
echo "│                                               │"
echo "└───────────────────────────────────────────────┘"

# Configuration parameters (with defaults)
LOG_FILE=${1:-"/var/log/auth.log"}    # Default auth log location
THRESHOLD=${2:-3}                     # Minimum failed attempts to trigger alert
TIME_WINDOW=${3:-"10 minutes ago"}    # Time window to consider
LOG_DIR="logs"                        # Log output directory
ALERT_FILE="$LOG_DIR/alerts.json"     # Alert output file

# Ensure log directory exists
mkdir -p "$LOG_DIR"

# Timestamp for logs
timestamp() {
  date "+%Y-%m-%d %H:%M:%S"
}

echo "[$(timestamp)] Starting authentication log monitoring"
echo "[$(timestamp)] Monitoring $LOG_FILE for failed login attempts"
echo "[$(timestamp)] Alert threshold: $THRESHOLD failed attempts"

# Get recent entries only (using specified time window)
recent_entries=$(find "$LOG_FILE" -mmin -${TIME_WINDOW%% *} -exec grep "Failed password" {} \; 2>/dev/null)

# If no recent entries or file not found, try without time filter
if [ -z "$recent_entries" ]; then
  if [ -f "$LOG_FILE" ]; then
    recent_entries=$(grep "Failed password" "$LOG_FILE" 2>/dev/null | tail -n 100)
    echo "[$(timestamp)] Using last 100 log entries (time filter not applicable)"
  else
    echo "[$(timestamp)] ERROR: Log file $LOG_FILE not found or not accessible"
    exit 1
  fi
fi

# Check if we found any failed login attempts
if [ -z "$recent_entries" ]; then
  echo "[$(timestamp)] No failed login attempts found in specified time window"
  # Create empty JSON array for alerts
  echo "[]" > "$ALERT_FILE"
  exit 0
fi

# Process failed login attempts by IP address
# Extract IP addresses and count occurrences
echo "$recent_entries" | 
  awk '{
    for(i=1; i<=NF; i++) {
      if ($i ~ /[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+/) {
        print $i
      }
    }
  }' | 
  sort | 
  uniq -c | 
  sort -nr |
  while read count ip; do
    # Check if count exceeds threshold
    if [ "$count" -ge "$THRESHOLD" ]; then
      # Get usernames targeted by this IP
      usernames=$(echo "$recent_entries" | grep "$ip" | awk '{
        for(i=1; i<=NF; i++) {
          if ($i == "for") {
            print $(i+1)
          }
        }
      }' | sort | uniq | tr '\n' ',' | sed 's/,$//')
      
      # Get timestamps of attempts
      timestamps=$(echo "$recent_entries" | grep "$ip" | awk '{print $1, $2, $3}' | tr '\n' ',' | sed 's/,$//')
      
      # Calculate rule level based on count (5-10 scale)
      rule_level=5
      if [ "$count" -ge 10 ]; then
        rule_level=8
      elif [ "$count" -ge 5 ]; then
        rule_level=6
      fi

      # Create JSON alert
      current_timestamp=$(timestamp)
      # Handle case with multiple usernames
      username_json="\"${usernames//,/\",\"}\""
      
      # Create JSON structure
      cat > "$ALERT_FILE" << EOF
{
  "timestamp": "$current_timestamp",
  "source_ip": "$ip",
  "attempt_count": $count,
  "usernames": [$username_json],
  "alert_type": "brute_force",
  "rule_level": $rule_level,
  "description": "Possible brute force attack from $ip: $count failed attempts",
  "raw_timestamps": "$timestamps"
}
EOF
      
      echo "[$(timestamp)] ALERT: Possible brute force attack detected"
      echo "  - Source IP: $ip"
      echo "  - Attempt count: $count"
      echo "  - Targeted users: $usernames"
      echo "  - Severity level: $rule_level/10"
      echo "[$(timestamp)] Alert saved to $ALERT_FILE"
    fi
  done

# If no alerts were triggered, create an empty alert file
if [ ! -f "$ALERT_FILE" ]; then
  echo "[]" > "$ALERT_FILE"
  echo "[$(timestamp)] No brute force attacks detected above threshold"
fi

echo "[$(timestamp)] Monitoring completed"
