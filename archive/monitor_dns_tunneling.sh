#!/bin/bash
# monitor_dns_tunneling.sh

# Default values
LOG_FILE="/var/log/syslog"  # System log (adjust for your DNS server logs)
THRESHOLD=50  # Number of DNS queries threshold
ALERT_FILE="logs/dns_alerts.json"
INTERVAL=300  # Time window in seconds (5 minutes)

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

echo "Starting DNS tunneling detection..."
echo "Log file: $LOG_FILE"
echo "Alert threshold: $THRESHOLD queries within $INTERVAL seconds"
echo "Alert output: $ALERT_FILE"

# Function to detect DNS tunneling
detect_dns_tunneling() {
  local current_time=$(date +%s)
  local time_window=$(($current_time - $INTERVAL))
  
  # Convert to format usable in grep
  local time_window_formatted=$(date -d @$time_window "+%b %d %H:%M:%S")
  
  # Look for DNS query patterns indicating possible tunneling
  # 1. High volume of queries from a single source
  # 2. Unusually long subdomains
  # 3. High entropy in domain names
  
  echo "Analyzing DNS queries for tunneling indicators..."
  
  # Get IPs with high query volume
  volume_suspects=$(grep -E "named.*query" $LOG_FILE | \
                    awk -v time="$time_window_formatted" '$0 >= time {print $8}' | \
                    sort | uniq -c | sort -nr | \
                    awk -v threshold=$THRESHOLD '$1 >= threshold {print $1","$2}')
  
  # Look for long subdomain queries (potential data exfiltration)
  length_suspects=$(grep -E "named.*query" $LOG_FILE | \
                    awk -v time="$time_window_formatted" '$0 >= time {print $8,$9}' | \
                    awk 'length($1) > 30 {print $1,$2}' | sort | uniq -c | \
                    sort -nr | head -10 | \
                    awk '{print $1","$2","$3}')
  
  # Process results
  if [ -z "$volume_suspects" ] && [ -z "$length_suspects" ]; then
    echo "No suspicious DNS activity detected."
    return 0
  fi
  
  echo "Suspicious DNS activity detected!"
  
  # Format alerts as JSON
  local alert_json=""
  local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
  
  # Process volume-based suspects
  while IFS=',' read -r count ip; do
    if [ -z "$alert_json" ]; then
      alert_json="["
    else
      alert_json="$alert_json,"
    fi
    
    # Get sample domains being queried
    sample_domains=$(grep "$ip" $LOG_FILE | grep "query" | \
                    tail -5 | awk '{print $9}' | tr '\n' ',' | sed 's/,$//')
    
    alert_json="$alert_json{\"timestamp\":\"$timestamp\",\"source_ip\":\"$ip\",\"attack_type\":\"dns_tunneling_volume\",\"query_count\":$count,\"sample_domains\":\"$sample_domains\"}"
  done <<< "$volume_suspects"
  
  # Process length-based suspects
  while IFS=',' read -r count domain ip; do
    if [ -z "$alert_json" ]; then
      alert_json="["
    else
      alert_json="$alert_json,"
    fi
    
    alert_json="$alert_json{\"timestamp\":\"$timestamp\",\"source_ip\":\"$ip\",\"attack_type\":\"dns_tunneling_length\",\"query_count\":$count,\"domain\":\"$domain\",\"domain_length\":${#domain}}"
  done <<< "$length_suspects"
  
  if [ ! -z "$alert_json" ]; then
    alert_json="$alert_json]"
    
    # Write to JSON file
    if [ -f "$ALERT_FILE" ]; then
      # Merge with existing alerts
      sed -i '$ s/]$/,/' "$ALERT_FILE"
      echo "$alert_json" | sed 's/^\[//' >> "$ALERT_FILE"
    else
      echo "$alert_json" > "$ALERT_FILE"
    fi
    
    echo "Alerts written to $ALERT_FILE"
  fi
  
  return 1
}

# Main monitoring loop
while true; do
  detect_dns_tunneling
  sleep 60
done
