# Project Handover Blueprint - CyberSentinel-AI

## Core Insight
This document transfers complete project context for CyberSentinel-AI, enabling the recipient to assume full ownership of this AI-enhanced security monitoring platform with minimal friction.

## Project Fundamentals
* **Project Name**: CyberSentinel-AI
* **Project Purpose**: An AI-powered security platform that detects, analyzes, and responds to credential-based attacks, integrating Kali Linux security tools with OpenAI's GPT-4o for enhanced threat intelligence
* **Current Status**: Completed (MVP with enhancement opportunities)
* **Repository**: GitHub (private repository)
* **Environment URLs**: Local Kali Linux VM environment with optional Metasploitable integration
* **Timeline**: Started May 2025 | Completed May 18, 2025

## Architecture Overview
* **Tech Stack**: 
  * Bash scripting for system operations and tool integration
  * Python for AI analysis and API integration
  * OpenAI API (GPT-4o) for security intelligence
  * Hydra for penetration testing
  * HTML/JavaScript for dashboard visualization
  * Optional Wazuh SIEM integration (proof-of-concept)

* **System Design**: Hybrid architecture with modular workflow:
  * Phase 1: Attack simulation (SSH brute force)
  * Phase 2: Multi-vector detection (SSH and web authentication)
  * Phase 3: AI-powered analysis
  * Phase 4: Automated response actions
  * Phase 5: Compliance and metrics
  * Phase 6: SIEM integration (proof-of-concept)

* **Infrastructure**: 
  * Primary: Single Kali Linux VM for all components
  * Extended: 3-VM architecture with Kali, Metasploitable, and SIEM VM (conceptual)
  * File-based data exchange using structured JSON

* **Key Dependencies**: 
  * OpenAI API for GPT-4o integration
  * Hydra penetration testing tool
  * Python libraries: python-dotenv, requests
  * Optional: Wazuh SIEM platform (for enterprise integration)

## Codebase Navigation
* **Project Structure**:
  * Root directory: Main scripts and configuration
  * `/logs`: Output directories for various components
  * `/logs/ai`: AI analysis results
  * `/archive`: Previous implementations and alternative components
  * `/assets`: Documentation and resources

* **Critical Components**:
  * `cybersentinel.sh`: Main workflow coordinator
  * `run_attack.sh`: SSH brute force attack simulation
  * `monitor_auth.sh`: SSH authentication log monitoring
  * `monitor_web_auth.sh`: Web authentication monitoring
  * `cybersentinel.py`: AI-powered security analysis using GPT-4o
  * `respond.sh`: Automated threat response
  * `iso27001_mapper.py`: Maps detected threats to ISO controls
  * `metrics_analyzer.py`: Calculates and visualizes security metrics
  * `dashboard.html`: Security metrics visualization
  * `serve_dashboard.py`: Web server for dashboard visualization
  * `wazuh_integration.py`: Proof-of-concept SIEM integration

* **Code Style & Patterns**: 
  * Bash scripts for system operations and tool integration
  * Python for API interactions and complex data processing
  * JSON for structured data exchange between components
  * Modular design with clear component separation
  * Comprehensive error handling and fallback mechanisms

* **Technical Debt**: 
  * Hydra SSH algorithm compatibility issues with older systems
  * Simulated responses for high-risk actions (actual blocking disabled by default)
  * SIEM integration implemented as proof-of-concept only
  * Source IP extraction shows "source" prefix in some cases

## Development Workflow
* **Local Setup**:
  1. Clone repository to Kali Linux environment
  2. Create `.env` file with `OPENAI_API_KEY=your_key_here`
  3. Make scripts executable with `chmod +x *.sh *.py`
  4. Ensure Hydra is installed (`sudo apt install hydra` if needed)
  5. Install Python dependencies: `pip install python-dotenv requests`

* **Build Process**: 
  * No build required, scripts run directly
  * Dashboard can be served with `python3 serve_dashboard.py`

* **Deployment Protocol**: 
  * Run `./cybersentinel.sh` to execute the complete workflow
  * Individual components can be run separately for testing
  * For demonstration: `./cybersentinel.sh` provides interactive workflow

* **Branch Strategy**: 
  * `main` branch for stable releases
  * Feature branches for specific improvements
  * `enterprise` branch for SIEM integration work

* **Testing Framework**: 
  * Each component includes robust error handling and sample data generation
  * Automated fallbacks ensure workflow completion even with missing components
  * Script flags for enabling/disabling actual security actions

## Current State
* **Completed Tasks**:
  * SSH brute force attack simulation with Hydra
  * Multi-vector authentication monitoring (SSH and web)
  * AI-powered analysis with GPT-4o integration
  * Automated response system with simulated IP blocking
  * ISO 27001 compliance mapping
  * Metrics calculation and visualization
  * Interactive dashboard for security monitoring
  * Sample data generation for testing all components
  * Proof-of-concept Wazuh SIEM integration

* **In-Progress Tasks**: 
  * None (MVP complete)

* **Upcoming Milestones**:
  * Full implementation of Wazuh SIEM integration
  * Integration with actual firewall systems for blocking
  * Additional attack vector simulations
  * Enhanced AI analysis with more security frameworks
  * Real-time notification system

* **Known Issues**:
  * Hydra SSH algorithm compatibility issues with Metasploitable VM
  * Source IP extraction shows "source" prefix in response output
  * Dashboard needs HTTP server for proper rendering
  * SIEM integration requires additional VM setup

## Access & Credentials
* **Required Accounts**: 
  * OpenAI API account
  * GitHub account (for repository access)
  * Optional: Wazuh account (for SIEM integration)

* **Access Process**: 
  * OpenAI API: Create account at https://platform.openai.com/
  * Repository: Request access from repository owner

* **Environment Variables**:
  * `OPENAI_API_KEY`: Your OpenAI API key
  * `WAZUH_API_URL`: Wazuh API endpoint (for SIEM integration)
  * `WAZUH_API_USER`: Wazuh API username (for SIEM integration)
  * `WAZUH_API_PASSWORD`: Wazuh API password (for SIEM integration)

* **Secrets Management**: 
  * `.env` file (excluded from git via .gitignore)
  * Environment variables for sensitive data
  * Simulation mode for potentially risky operations

## Stakeholders
* **Product Owner**: Sub0x
* **Technical Lead**: Sub0x
* **Team Members**: Sub0x (development)
* **Key Users/Clients**: Cybersecurity students, security professionals, system administrators

## Domain Knowledge
* **Business Context**: 
  * Cybersecurity monitoring and incident response automation
  * Credential-based attack detection and mitigation
  * AI-enhanced security operations

* **Key Requirements**:
  * Automated security incident detection across multiple vectors
  * AI-powered analysis of security events
  * Compliance mapping (ISO 27001, MITRE ATT&CK)
  * Metrics calculation and visualization
  * Response automation

* **User Workflows**:
  1. **Complete Security Lifecycle**:
     * Run attack simulation for testing
     * Monitor multiple authentication sources
     * Analyze security events with AI
     * Implement automated responses
     * View security metrics and compliance status

  2. **Security Analysis Only**:
     * Monitor authentication logs
     * Analyze detected events
     * View security dashboards

  3. **Penetration Testing**:
     * Configure attack parameters
     * Run attack simulation
     * Review attack results

* **Edge Cases**:
  * Missing log files: System generates sample data
  * API failures: Fallback to sample analysis data
  * Network connectivity issues: Local operation mode
  * Missing dependencies: Guided installation process
  * Older target systems: SSH algorithm compatibility issues

## Support & Operations
* **Monitoring**: 
  * Script logs to various files in logs/ directory
  * AI analysis stored in logs/ai/ directory
  * Security metrics visualized in dashboard
  * Optional SIEM integration for enterprise monitoring

* **Common Issues**:
  * **SSH Compatibility**: Add `-cPKI` to Hydra command for older systems
  * **Dashboard Rendering**: Use `serve_dashboard.py` to serve the dashboard
  * **Log Access**: Run with sudo for system log access or use sample data
  * **API Key**: Ensure .env file is properly configured

* **Incident Response**: 
  * System generates warnings and recommendations for detected attacks
  * Response script can simulate or implement actual IP blocking
  * Compliance impact assessment for security events

* **Performance Considerations**: 
  * OpenAI API latency during analysis phase
  * Log file size growth over time
  * Dashboard data refresh frequency
  * Multiple attack simulations can trigger rate limiting

## Recommendations
* **Immediate Focus**:
  1. Test with real-world scenarios beyond SSH brute force
  2. Implement actual firewall integration for blocking
  3. Complete the Wazuh SIEM integration
  4. Enhance visualization with real-time updates

* **Learning Resources**:
  * Hydra documentation for SSH options: https://github.com/vanhauser-thc/thc-hydra
  * MITRE ATT&CK framework: https://attack.mitre.org/
  * ISO 27001 security controls
  * OpenAI API documentation: https://platform.openai.com/docs/
  * Wazuh documentation (for SIEM): https://documentation.wazuh.com/

* **Enhancement Opportunities**:
  * Implement additional attack simulations (DNS tunneling, web attacks)
  * Add machine learning for anomaly detection
  * Create visualization dashboard for security events
  * Integrate with email/Slack for alerts
  * Implement multi-system monitoring
  * Develop custom AI security models

## Additional Context
* **Project History**:
  * Initially developed as pure Python implementation
  * Migrated to hybrid bash/Python for performance and native tool integration
  * Added web authentication monitoring for multi-vector approach
  * Incorporated ISO 27001 compliance framework
  * Added dashboard visualization
  * Created proof-of-concept SIEM integration

* **Failed Approaches**:
  * Pure Python implementation was less efficient for system operations
  * Simple regex parsing for credential attack detection proved unreliable
  * Direct access to system auth.log had permission issues
  * Local file-based dashboard had rendering issues due to browser security

* **Lessons Learned**:
  * Hybrid architecture leverages strengths of different languages
  * Sample data generation enables end-to-end testing
  * JSON provides effective data exchange between components
  * Modular design allows for easy enhancement
  * AI integration provides valuable context to security events
  * Compliance mapping adds significant value to security analysis

This project provides an end-to-end security testing, monitoring, and response system that uses AI to analyze security events and recommend appropriate actions, with enterprise integration capabilities through its proof-of-concept SIEM component.
