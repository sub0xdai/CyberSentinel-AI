#!/bin/bash
# monitor_web_auth.sh

# Default values
LOG_FILE="/var/log/apache2/access.log"  # Apache log
THRESHOLD=10  # Failed attempts threshold
ALERT_FILE="logs/web_alerts.json"
INTERVAL=60  # Time window in seconds

# Check if logs directory exists
mkdir -p logs

# Parse command line arguments
while getopts "l:t:o:i:" opt; do
  case $opt in
    l) LOG_FILE="$OPTARG" ;;
    t) THRESHOLD="$OPTARG" ;;
    o) ALERT_FILE="$OPTARG" ;;
    i) INTERVAL="$OPTARG" ;;
    \?) echo "Invalid option -$OPTARG" >&2; exit 1 ;;
  esac
done

echo "Starting web authentication monitoring..."
echo "Log file: $LOG_FILE"
echo "Alert threshold: $THRESHOLD attempts within $INTERVAL seconds"
echo "Alert output: $ALERT_FILE"

# Function to detect login failures
detect_login_failures() {
  local current_time=$(date +%s)
  local time_window=$(($current_time - $INTERVAL))
  
  # Get timestamp in Apache log format for filtering
  local time_window_formatted=$(date -d @$time_window "+%d/%b/%Y:%H:%M:%S")
  
  # Look for POST requests to login pages with 401/403 response codes
  # Filter for recent entries and count by IP
  echo "Analyzing web login attempts..."
  suspicious_ips=$(grep -E "POST.*(login|signin|auth).*(401|403)" $LOG_FILE | \
                   awk -v time="$time_window_formatted" '$4 >= time {print $1}' | \
                   sort | uniq -c | sort -nr | \
                   awk -v threshold=$THRESHOLD '$1 >= threshold {print $1","$2}')
  
  # Process results
  if [ -z "$suspicious_ips" ]; then
    echo "No suspicious activity detected."
    return 0
  fi
  
  echo "Suspicious activity detected!"
  
  # Format alerts as JSON
  local alert_json=""
  local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
  
  while IFS=',' read -r count ip; do
    # Get the most recent URLs attempted
    recent_urls=$(grep "$ip" $LOG_FILE | grep -E "POST.*(login|signin|auth).*(401|403)" | \
                 tail -5 | awk '{print $7}' | tr '\n' ',' | sed 's/,$//')
    
    # Create JSON alert
    if [ -z "$alert_json" ]; then
      alert_json="["
    else
      alert_json="$alert_json,"
    fi
    
    alert_json="$alert_json{\"timestamp\":\"$timestamp\",\"source_ip\":\"$ip\",\"attack_type\":\"web_brute_force\",\"attempt_count\":$count,\"target_urls\":\"$recent_urls\"}"
  done <<< "$suspicious_ips"
  
  alert_json="$alert_json]"
  
  # Write to JSON file
  if [ -f "$ALERT_FILE" ]; then
    # Merge with existing alerts (remove the last "]", add ",", append new alerts)
    sed -i '$ s/]$/,/' "$ALERT_FILE"
    echo "$alert_json" | sed 's/^\[//' >> "$ALERT_FILE"
  else
    echo "$alert_json" > "$ALERT_FILE"
  fi
  
  echo "Alerts written to $ALERT_FILE"
  return 1
}

# Main monitoring loop
while true; do
  detect_login_failures
  sleep 5
done
