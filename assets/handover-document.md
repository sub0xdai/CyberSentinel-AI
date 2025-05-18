# CyberSentinel-AI: Handover Document

## Project Overview

CyberSentinel-AI is an AI-enhanced security monitoring solution designed to detect, analyze, and respond to credential-based attacks. The project uses a hybrid architecture combining bash scripts for system-level operations and Python for AI integration with OpenAI's GPT-4o model.

## System Architecture

The implementation follows a hybrid approach with these key components:

1. **Attack Simulation**: Bash script using Hydra for SSH brute force attacks
2. **Detection System**: Bash script for monitoring authentication logs
3. **AI Analysis Engine**: Python script for GPT-4o integration and security intelligence
4. **Response System**: Bash script for implementing automated actions
5. **Workflow Coordinator**: Bash script that orchestrates all components

## Key Files

| File | Language | Purpose |
|------|----------|---------|
| `run_attack.sh` | Bash | Simulates SSH brute force attacks using Hydra |
| `monitor_auth.sh` | Bash | Monitors auth logs for suspicious activity |
| `cybersentinel.py` | Python | Analyzes alerts using OpenAI's GPT-4o |
| `respond.sh` | Bash | Implements automated response actions |
| `cybersentinel.sh` | Bash | Coordinates all components into a workflow |

## Setup and Installation

### Prerequisites

- Kali Linux (tested on 2023.1)
- Python 3.8+ with pip
- Hydra (standard in Kali)
- OpenAI API key

### Installation Steps

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/CyberSentinel-AI.git
   cd CyberSentinel-AI
   ```

2. **Install Python dependencies**:
   ```bash
   pip install python-dotenv requests
   ```

3. **Configure your API key**:
   ```bash
   # Create a .env file with your OpenAI API key
   echo "OPENAI_API_KEY=your_actual_key_here" > .env
   ```

4. **Set file permissions**:
   ```bash
   chmod +x *.sh
   chmod +x *.py
   ```

## Usage Guide

### Complete Workflow

To run the full attack-detect-analyze-respond workflow:

```bash
./cybersentinel.sh
```

This interactive script will guide you through each phase with options to customize parameters.

### Individual Components

Each component can also be run independently:

#### 1. Attack Simulation

```bash
# Basic usage with defaults
./run_attack.sh

# Custom parameters
./run_attack.sh 192.168.122.167 msfadmin custom_passwords.txt 6
```

Parameters:
- Target IP (default: 192.168.122.167)
- Username (default: msfadmin)
- Password list (default: passwords.txt)
- Concurrent tasks (default: 4)

#### 2. Authentication Log Monitoring

```bash
# Basic usage with defaults
./monitor_auth.sh

# Custom parameters
./monitor_auth.sh /var/log/auth.log 5
```

Parameters:
- Log file (default: /var/log/auth.log)
- Threshold (default: 3 failed attempts)

#### 3. AI Analysis

```bash
# Run AI analysis on detected alerts
python3 cybersentinel.py
```

#### 4. Response Actions

```bash
# Implement responses based on AI analysis
./respond.sh
```

## System Configuration

### Directory Structure

```
CyberSentinel-AI/
├── run_attack.sh       # Attack simulation
├── monitor_auth.sh     # Log monitoring
├── cybersentinel.py    # AI analysis
├── respond.sh          # Response actions
├── cybersentinel.sh    # Main workflow
├── passwords.txt       # Default wordlist
├── .env                # API key (not in repo)
├── .gitignore          # Git ignore file
└── logs/               # Generated logs
    ├── alerts.json     # Alert data
    ├── attack.log      # Attack logs
    └── ai/             # AI analysis logs
```

### Log Files

- `logs/alerts.json`: Structured alert data
- `logs/attack.log`: Attack simulation logs
- `logs/ai/openai_analysis.json`: AI analysis results
- `logs/ai/responses.log`: Response action logs

## Implementation Details

### 1. Attack Simulation (`run_attack.sh`)

This script provides a wrapper around Hydra for SSH brute force attacks:

- Creates default password list if none exists
- Configurable parameters (target, username, wordlist, tasks)
- Comprehensive logging of attack process
- Summary statistics after completion

### 2. Log Monitoring (`monitor_auth.sh`)

Monitors authentication logs for failed login attempts:

- Uses efficient grep/awk for pattern matching
- Configurable threshold for alert generation
- Generates structured JSON alerts
- Extracts usernames, timestamps, and source IPs

### 3. AI Analysis (`cybersentinel.py`)

Processes alerts using OpenAI's GPT-4o model:

- Securely handles API key through environment variables
- Sends structured prompts for consistent analysis
- Provides MITRE ATT&CK mapping and compliance insights
- Generates severity assessments and response recommendations

### 4. Response System (`respond.sh`)

Implements automated responses based on AI analysis:

- Reads and parses AI analysis
- Implements response actions based on severity
- Blocks IPs using iptables for high-severity attacks
- Logs all actions for audit purposes

### 5. Workflow Coordinator (`cybersentinel.sh`)

Coordinates all components into a cohesive workflow:

- Checks environment and dependencies
- Interactive mode for parameter customization
- Step-by-step execution with user confirmation
- Summary of results after completion

## Technical Design Decisions

### 1. Hybrid Architecture

The project uses a hybrid bash/Python approach for these reasons:

- **Bash Advantages**: Efficient for system operations, log parsing, and direct tool integration
- **Python Advantages**: Better for complex API interactions, JSON handling, and advanced data processing
- **Communication**: Standard file formats (JSON) and consistent file locations

### 2. Security Considerations

- API key stored in .env file (not committed to repository)
- Response actions simulated by default (uncomment to enable actual blocking)
- Comprehensive logging for audit trail
- Clear separation between detection and response

### 3. Extensibility

The modular design allows for easy extension:

- Additional log sources can be monitored
- Different AI models can be integrated
- New response actions can be implemented
- Different attack simulations can be added

## Known Limitations

1. **Current Detection Scope**: Limited to SSH brute force attacks
2. **Log Rotation**: Doesn't explicitly handle log rotation scenarios
3. **Response Actions**: Simulated by default for safety
4. **AI Token Usage**: Be mindful of OpenAI API usage costs

## Future Development

Areas for further enhancement:

1. **Enhanced Detection**: Add support for additional attack vectors
2. **Multiple Log Sources**: Expand monitoring beyond authentication logs
3. **Advanced Response**: Implement more sophisticated response actions
4. **Visualization**: Add graphical reporting of security events
5. **Containerization**: Package for easier deployment

## Troubleshooting

### Common Issues

1. **API Key Issues**:
   - Ensure .env file exists and contains valid key
   - Check API key permissions in OpenAI dashboard

2. **Permission Problems**:
   - Run `chmod +x *.sh *.py` to ensure all scripts are executable

3. **Log Access**:
   - Run with sudo if accessing system logs: `sudo ./monitor_auth.sh`

4. **Hydra Not Found**:
   - Install with `sudo apt install hydra`

5. **Python Dependencies**:
   - Run `pip install -r requirements.txt` if available
   - Or install directly: `pip install python-dotenv requests`

## Conclusion

CyberSentinel-AI demonstrates how traditional security tools can be enhanced with AI capabilities. The hybrid architecture leverages the strengths of both bash and Python to create an efficient, flexible, and powerful security monitoring solution.

This handover document should provide all the information needed to understand, use, and further develop the project. For any questions not covered here, please refer to the inline documentation within each script or contact the original developer.

Last Updated: May 20, 2025
