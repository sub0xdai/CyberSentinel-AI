# metrics_analyzer.py
import json
import os
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import numpy as np

class MetricsAnalyzer:
    def __init__(self, logs_dir="logs"):
        self.logs_dir = logs_dir
        self.metrics = {
            "detection_times": [],
            "false_positives": 0,
            "true_positives": 0,
            "attack_types": {},
            "severity_distribution": {},
            "response_times": [],
            "blocked_ips": set()
        }
        
    def parse_logs(self):
        """Parse log files to extract metrics"""
        # Parse alerts.json
        try:
            with open(os.path.join(self.logs_dir, "alerts.json"), 'r') as f:
                alerts = json.load(f)
                
            # Process alerts
            for alert in alerts:
                # Count attack types
                attack_type = alert.get("attack_type", "unknown")
                self.metrics["attack_types"][attack_type] = self.metrics["attack_types"].get(attack_type, 0) + 1
        except Exception as e:
            print(f"Error parsing alerts: {e}")
        
        # Parse AI analysis logs
        try:
            with open(os.path.join(self.logs_dir, "ai", "openai_analysis.json"), 'r') as f:
                analyses = json.load(f)
            
            # Process AI analyses
            for analysis in analyses:
                # Extract severity distribution
                severity = analysis.get("severity", "unknown")
                self.metrics["severity_distribution"][severity] = self.metrics["severity_distribution"].get(severity, 0) + 1
                
                # Record false/true positives based on AI determination
                if "false_positive" in analysis and analysis["false_positive"] == True:
                    self.metrics["false_positives"] += 1
                else:
                    self.metrics["true_positives"] += 1
        except Exception as e:
            print(f"Error parsing AI analysis: {e}")
        
        # Parse response logs
        try:
            with open(os.path.join(self.logs_dir, "ai", "responses.log"), 'r') as f:
                lines = f.readlines()
            
            # Process response logs
            for line in lines:
                if "Blocked IP" in line:
                    # Extract IP address
                    ip = line.split("Blocked IP")[1].strip().split(" ")[0]
                    self.metrics["blocked_ips"].add(ip)
                
                # Calculate response times if timestamp info available
                if "Alert time:" in line and "Response time:" in line:
                    try:
                        alert_time = line.split("Alert time:")[1].split(",")[0].strip()
                        response_time = line.split("Response time:")[1].split(",")[0].strip()
                        
                        alert_dt = datetime.strptime(alert_time, "%Y-%m-%dT%H:%M:%SZ")
                        response_dt = datetime.strptime(response_time, "%Y-%m-%dT%H:%M:%SZ")
                        
                        # Calculate difference in seconds
                        time_diff = (response_dt - alert_dt).total_seconds()
                        self.metrics["response_times"].append(time_diff)
                    except Exception as e:
                        print(f"Error parsing timestamps: {e}")
        except Exception as e:
            print(f"Error parsing response logs: {e}")
            
        return self.metrics
        
    def calculate_key_metrics(self):
        """Calculate key performance metrics"""
        results = {}
        
        # Detection accuracy
        total_alerts = self.metrics["true_positives"] + self.metrics["false_positives"]
        results["detection_accuracy"] = (self.metrics["true_positives"] / total_alerts * 100) if total_alerts > 0 else 0
        
        # Average response time
        results["avg_response_time"] = np.mean(self.metrics["response_times"]) if self.metrics["response_times"] else 0
        
        # Time savings compared to manual analysis (assumed 5 minutes per alert)
        manual_time = total_alerts * 300  # 5 minutes in seconds
        automated_time = sum(self.metrics["response_times"]) if self.metrics["response_times"] else 0
        results["time_savings"] = (manual_time - automated_time) / manual_time * 100 if manual_time > 0 else 0
        
        # Unique threats identified
        results["unique_attack_types"] = len(self.metrics["attack_types"])
        
        # Blocked threats
        results["blocked_threats"] = len(self.metrics["blocked_ips"])
        
        return results
        
    def generate_metrics_report(self, output_file="logs/metrics_report.json"):
        """Generate a comprehensive metrics report"""
        self.parse_logs()
        results = self.calculate_key_metrics()
        
        report = {
            "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "summary_metrics": results,
            "detailed_metrics": {
                "attack_distribution": self.metrics["attack_types"],
                "severity_distribution": self.metrics["severity_distribution"],
                "response_times": self.metrics["response_times"]
            }
        }
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # Write report
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
            
        return report
    
    def generate_visualizations(self, output_dir="logs/visualizations"):
        """Generate visualization charts for the metrics"""
        # Create directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # 1. Attack Type Distribution
        if self.metrics["attack_types"]:
            plt.figure(figsize=(10, 6))
            plt.bar(self.metrics["attack_types"].keys(), self.metrics["attack_types"].values())
            plt.title('Attack Type Distribution')
            plt.xlabel('Attack Type')
            plt.ylabel('Count')
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.savefig(os.path.join(output_dir, 'attack_distribution.png'))
            plt.close()
        
        # 2. Severity Distribution
        if self.metrics["severity_distribution"]:
            plt.figure(figsize=(8, 8))
            plt.pie(self.metrics["severity_distribution"].values(), 
                   labels=self.metrics["severity_distribution"].keys(),
                   autopct='%1.1f%%',
                   startangle=90)
            plt.title('Alert Severity Distribution')
            plt.axis('equal')
            plt.tight_layout()
            plt.savefig(os.path.join(output_dir, 'severity_distribution.png'))
            plt.close()
        
        # 3. Response Time Histogram
        if self.metrics["response_times"]:
            plt.figure(figsize=(10, 6))
            plt.hist(self.metrics["response_times"], bins=10, alpha=0.7)
            plt.title('Response Time Distribution')
            plt.xlabel('Response Time (seconds)')
            plt.ylabel('Frequency')
            plt.axvline(np.mean(self.metrics["response_times"]), color='r', linestyle='dashed', linewidth=1)
            min_ylim, max_ylim = plt.ylim()
            plt.text(np.mean(self.metrics["response_times"])*1.1, max_ylim*0.9, 
                    f'Mean: {np.mean(self.metrics["response_times"]):.2f}s')
            plt.tight_layout()
            plt.savefig(os.path.join(output_dir, 'response_times.png'))
            plt.close()
        
        # 4. Detection Accuracy
        results = self.calculate_key_metrics()
        plt.figure(figsize=(8, 6))
        plt.bar(['True Positives', 'False Positives'], 
               [self.metrics["true_positives"], self.metrics["false_positives"]])
        plt.title(f'Detection Accuracy: {results["detection_accuracy"]:.1f}%')
        plt.ylabel('Count')
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, 'detection_accuracy.png'))
        plt.close()
        
        return os.path.join(output_dir)

# Example usage
if __name__ == "__main__":
    analyzer = MetricsAnalyzer()
    report = analyzer.generate_metrics_report()
    vis_path = analyzer.generate_visualizations()
    print(f"Generated metrics report and visualizations")
    
    # Print key metrics
    for key, value in report["summary_metrics"].items():
        if isinstance(value, float):
            print(f"{key}: {value:.2f}")
        else:
            print(f"{key}: {value}")
