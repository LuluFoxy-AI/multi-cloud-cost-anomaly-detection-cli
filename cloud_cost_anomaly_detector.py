#!/usr/bin/env python3
"""
Multi-Cloud Cost Anomaly Detection CLI
Detects cost spikes across AWS and Azure by comparing recent spending patterns.

Author: LuluFoxy-AI
License: MIT
"""

import argparse
import json
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import requests

try:
    import boto3
    from botocore.exceptions import ClientError, NoCredentialsError
except ImportError:
    boto3 = None

try:
    from azure.identity import DefaultAzureCredential
    from azure.mgmt.costmanagement import CostManagementClient
except ImportError:
    DefaultAzureCredential = None
    CostManagementClient = None


class CostAnalyzer:
    """Analyzes cloud costs and detects anomalies."""
    
    def __init__(self, threshold: float = 20.0, webhook_url: Optional[str] = None):
        self.threshold = threshold
        self.webhook_url = webhook_url
        self.anomalies = []
    
    def analyze_aws(self) -> Dict:
        """Analyze AWS costs using Cost Explorer API."""
        if not boto3:
            return {"error": "boto3 not installed. Run: pip install boto3"}
        
        try:
            client = boto3.client('ce', region_name='us-east-1')
            
            # Define time periods
            end_date = datetime.now().date()
            start_current = end_date - timedelta(days=7)
            start_previous = start_current - timedelta(days=7)
            
            # Get current period costs
            current_response = client.get_cost_and_usage(
                TimePeriod={
                    'Start': start_current.strftime('%Y-%m-%d'),
                    'End': end_date.strftime('%Y-%m-%d')
                },
                Granularity='DAILY',
                Metrics=['UnblendedCost'],
                GroupBy=[{'Type': 'SERVICE', 'Key': 'SERVICE'}]
            )
            
            # Get previous period costs
            previous_response = client.get_cost_and_usage(
                TimePeriod={
                    'Start': start_previous.strftime('%Y-%m-%d'),
                    'End': start_current.strftime('%Y-%m-%d')
                },
                Granularity='DAILY',
                Metrics=['UnblendedCost'],
                GroupBy=[{'Type': 'SERVICE', 'Key': 'SERVICE'}]
            )
            
            # Aggregate costs by service
            current_costs = self._aggregate_aws_costs(current_response)
            previous_costs = self._aggregate_aws_costs(previous_response)
            
            # Detect anomalies
            return self._detect_anomalies('AWS', current_costs, previous_costs)
            
        except NoCredentialsError:
            return {"error": "AWS credentials not found. Configure with 'aws configure'"}
        except ClientError as e:
            return {"error": f"AWS API error: {str(e)}"}
    
    def _aggregate_aws_costs(self, response: Dict) -> Dict[str, float]:
        """Aggregate AWS costs by service."""
        service_costs = {}
        for result in response.get('ResultsByTime', []):
            for group in result.get('Groups', []):
                service = group['Keys'][0]
                cost = float(group['Metrics']['UnblendedCost']['Amount'])
                service_costs[service] = service_costs.get(service, 0) + cost
        return service_costs
    
    def _detect_anomalies(self, cloud: str, current: Dict[str, float], 
                          previous: Dict[str, float]) -> Dict:
        """Compare current vs previous costs and flag anomalies."""
        results = {
            "cloud": cloud,
            "total_current": sum(current.values()),
            "total_previous": sum(previous.values()),
            "anomalies": []
        }
        
        for service, current_cost in current.items():
            previous_cost = previous.get(service, 0)
            
            if previous_cost == 0 and current_cost > 1:
                # New service with significant cost
                results["anomalies"].append({
                    "service": service,
                    "current_cost": round(current_cost, 2),
                    "previous_cost": 0,
                    "change_percent": 100,
                    "alert": "NEW_SERVICE"
                })
            elif previous_cost > 0:
                change_percent = ((current_cost - previous_cost) / previous_cost) * 100
                
                if change_percent > self.threshold:
                    results["anomalies"].append({
                        "service": service,
                        "current_cost": round(current_cost, 2),
                        "previous_cost": round(previous_cost, 2),
                        "change_percent": round(change_percent, 2),
                        "alert": "SPIKE_DETECTED"
                    })
        
        self.anomalies.extend(results["anomalies"])
        return results
    
    def send_webhook(self, data: Dict) -> bool:
        """Send anomaly data to webhook URL."""
        if not self.webhook_url:
            return False
        
        try:
            response = requests.post(
                self.webhook_url,
                json=data,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            return response.status_code == 200
        except Exception as e:
            print(f"Webhook error: {str(e)}", file=sys.stderr)
            return False
    
    def print_report(self, results: Dict):
        """Print formatted cost anomaly report."""
        print(f"\n{'='*60}")
        print(f"Cost Anomaly Report - {results['cloud']}")
        print(f"{'='*60}")
        print(f"Current Period (7d): ${results['total_current']:.2f}")
        print(f"Previous Period (7d): ${results['total_previous']:.2f}")
        
        if results['total_previous'] > 0:
            total_change = ((results['total_current'] - results['total_previous']) 
                          / results['total_previous']) * 100
            print(f"Total Change: {total_change:+.2f}%")
        
        if results['anomalies']:
            print(f"\n⚠️  {len(results['anomalies'])} Anomalies Detected:\n")
            for anomaly in results['anomalies']:
                print(f"  Service: {anomaly['service']}")
                print(f"  Current: ${anomaly['current_cost']:.2f}")
                print(f"  Previous: ${anomaly['previous_cost']:.2f}")
                print(f"  Change: {anomaly['change_percent']:+.2f}%")
                print(f"  Alert: {anomaly['alert']}\n")
        else:
            print("\n✓ No anomalies detected.\n")


def main():
    parser = argparse.ArgumentParser(
        description='Multi-Cloud Cost Anomaly Detection CLI'
    )
    parser.add_argument(
        '--cloud',
        choices=['aws', 'azure', 'all'],
        default='all',
        help='Cloud provider to analyze'
    )
    parser.add_argument(
        '--threshold',
        type=float,
        default=20.0,
        help='Percentage threshold for anomaly detection (default: 20)'
    )
    parser.add_argument(
        '--webhook',
        type=str,
        help='Webhook URL for notifications'
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output results as JSON'
    )
    
    args = parser.parse_args()
    analyzer = CostAnalyzer(threshold=args.threshold, webhook_url=args.webhook)
    
    all_results = []
    
    if args.cloud in ['aws', 'all']:
        aws_results = analyzer.analyze_aws()
        if 'error' not in aws_results:
            all_results.append(aws_results)
            if not args.json:
                analyzer.print_report(aws_results)
        else:
            print(f"AWS Error: {aws_results['error']}", file=sys.stderr)
    
    # Send webhook if anomalies found
    if analyzer.anomalies and args.webhook:
        analyzer.send_webhook({'anomalies': analyzer.anomalies})
        print("\n✓ Webhook notification sent")
    
    if args.json:
        print(json.dumps(all_results, indent=2))


if __name__ == '__main__':
    main()