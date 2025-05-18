# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

CyberSentinel-AI is an AI-powered security platform that detects, analyzes, and responds to credential-based attacks. The system integrates Kali Linux security tools with OpenAI's GPT-4o model to provide enhanced threat detection capabilities with a focus on SSH brute force attacks.

## Architecture

The project uses a hybrid architecture with these core components:

1. **Attack Simulation (`run_attack.sh`)**: Simulates SSH brute force attacks using Hydra
2. **Detection System (`monitor_auth.sh`)**: Monitors authentication logs for suspicious login attempts
3. **AI Analysis Engine (`cybersentinel.py`)**: Uses GPT-4o to analyze alerts and provide security intelligence
4. **Response System (`respond.sh`)**: Implements automated responses based on AI analysis
5. **Workflow Coordinator (`cybersentinel.sh`)**: Orchestrates all components in a unified workflow
6. **Dashboard (`generate_dashboard.sh` & `dashboard.html`)**: Visualizes security metrics and alerts

## Commands

### Core Operations

```bash
# Run the complete workflow interactively
./cybersentinel.sh

# Run individual components
./run_attack.sh [TARGET_IP] [USERNAME] [WORDLIST] [CONCURRENT_TASKS]
./monitor_auth.sh [LOG_FILE] [THRESHOLD]
python3 cybersentinel.py
./respond.sh
./generate_dashboard.sh
```

### Development Setup

```bash
# Install required Python dependencies
pip install python-dotenv requests

# Set up API key
echo "OPENAI_API_KEY=your_key_here" > .env
```

## Component Interactions

The system follows a linear workflow:

1. **Attack Simulation (Optional)**: Generates attack traffic
2. **Log Monitoring**: Creates structured JSON alerts from log patterns
3. **AI Analysis**: Processes alerts with GPT-4o to determine:
   - Credential attack verification
   - Severity assessment
   - MITRE ATT&CK mapping
   - Compliance impact analysis
   - Response recommendations
4. **Response Actions**: Implements protective measures based on severity
5. **Dashboard Generation**: Creates visual metrics and reports

Data flows between components via JSON files in the `logs/` directory.
