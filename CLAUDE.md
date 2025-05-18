# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

CyberSentinel-AI is an enterprise-grade AI-powered security platform that detects, analyzes, and responds to credential-based attacks. The system integrates Kali Linux security tools with OpenAI's GPT-4o model to provide enhanced threat detection capabilities, compliance mapping, and metrics generation.

## Architecture

The project uses a hybrid architecture with these core components:

1. **Attack Simulation (`run_attack.sh`)**: Simulates SSH brute force attacks using Hydra
2. **Multi-Vector Detection System**:
   - **SSH Monitoring (`monitor_auth.sh`)**: Monitors SSH authentication logs
   - **Web Monitoring (`monitor_web_auth.sh`)**: Monitors web server authentication logs
3. **AI Analysis Engine (`cybersentinel.py`)**: Uses GPT-4o to analyze alerts and provide security intelligence
4. **Response System (`respond.sh`)**: Implements automated responses with actual or simulated IP blocking
5. **Compliance Mapping (`iso27001_mapper.py`)**: Maps security events to ISO 27001 controls
6. **Metrics Analysis (`metrics_analyzer.py`)**: Generates security metrics and performance indicators
7. **Workflow Coordinator (`cybersentinel.sh`)**: Orchestrates all components in a unified workflow
8. **Dashboard (`generate_dashboard.sh` & `dashboard.html`)**: Visualizes security metrics and alerts

## Commands

### Core Operations

```bash
# Run the complete workflow interactively
./cybersentinel.sh

# Run individual components
./run_attack.sh [TARGET_IP] [USERNAME] [WORDLIST] [CONCURRENT_TASKS]
./monitor_auth.sh [LOG_FILE] [THRESHOLD]
./monitor_web_auth.sh [LOG_FILE] [THRESHOLD]
python3 cybersentinel.py
./respond.sh [real_blocking]
python3 iso27001_mapper.py
python3 metrics_analyzer.py
./generate_dashboard.sh
```

### Development Setup

```bash
# Install required Python dependencies
pip install python-dotenv requests matplotlib numpy

# Set up API key
echo "OPENAI_API_KEY=your_key_here" > .env

# Make all scripts executable
chmod +x *.sh *.py
```

## Component Interactions

The system follows an enhanced multi-vector workflow:

1. **Attack Simulation (Optional)**: Generates SSH brute force attack traffic
2. **Multi-Vector Log Monitoring**: 
   - SSH Authentication: Monitors for SSH brute force attempts
   - Web Authentication: Monitors for web login brute force attempts
3. **AI Analysis**: Processes alerts with GPT-4o to determine:
   - Credential attack verification
   - Severity assessment (scale 1-10)
   - MITRE ATT&CK mapping
   - Compliance impact analysis
   - Response recommendations
4. **Response Actions**: 
   - Implements protective measures based on severity
   - Can perform actual IP blocking via iptables/ufw
   - Maintains block list of malicious IPs
5. **Compliance Mapping**:
   - Maps security events to ISO 27001 controls
   - Generates compliance reports for audit purposes
6. **Metrics Generation**:
   - Calculates detection accuracy and response times
   - Generates performance metrics and visualizations
7. **Dashboard Generation**: Creates visual security reports

Data flows between components via structured JSON files in the `logs/` directory hierarchy, including specialized subdirectories for AI, compliance, metrics, and visualizations.
