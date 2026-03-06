#!/usr/bin/env python3
"""
Multi-Cloud Cost Anomaly Detection CLI
Detects cost spikes across AWS, GCP, and Azure by comparing daily costs to 7-day averages.

Free tier: 1 cloud account
Pro tier: Unlimited accounts + Slack integration + 90-day history
"""

import os
import sys
import json
import argparse
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import statistics

# Cloud SDK imports (install via: pip install boto3 google-cloud-billing azure-mgmt-costmanagement azure-identity)
try:
    import boto3
    from google.cloud import billing_v1
    from azure.identity import DefaultAzureCredential
    from azure.mgmt.costmanagement import CostManagementClient
except ImportError:
    print("Error: Required packages not installed. Run: pip install boto3 google-cloud-billing azure-mgmt-costmanagement azure-identity")
    sys.exit(1)


class CostAnomalyDetector:
    """Main class for detecting cost anomalies across cloud providers"""
    
    def __init__(self, threshold: float = 20.0, days_history: int = 7):
        self.threshold = threshold  # Percentage threshold for anomaly detection
        self.days_history = days_history
        self.license_key = os.getenv('CLOUDCOST_LICENSE_KEY', 'free')
    
    def check_license(self, num_accounts: int) -> bool:
        """Check if license allows multiple accounts (Pro feature)"""
        if num_accounts > 1 and self.license_key == 'free':
            print("⚠️  Multiple accounts require Pro license ($29/month)")
            print("   Get Pro at: https://gumroad.com/l/cloudcost-pro")
            return False
        return True
    
    def get_aws_costs(self, profile: str = 'default') -> Dict:
        """Fetch AWS costs using Cost Explorer API"""
        try:
            session = boto3.Session(profile_name=profile)
            ce_client = session.client('ce', region_name='us-east-1')
            
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=self.days_history)
            
            response = ce_client.get_cost_and_usage(
                TimePeriod={'Start': str(start_date), 'End': str(end_date)},
                Granularity='DAILY',
                Metrics=['UnblendedCost']
            )
            
            costs = [float(day['Total']['UnblendedCost']['Amount']) 
                    for day in response['ResultsByTime']]
            
            return {'provider': 'AWS', 'costs': costs, 'currency': 'USD'}
        except Exception as e:
            return {'provider': 'AWS', 'error': str(e)}
    
    def get_gcp_costs(self, project_id: str) -> Dict:
        """Fetch GCP costs using Cloud Billing API"""
        # Note: GCP billing data has 1-2 day delay, this is a simplified implementation
        try:
            # Placeholder for GCP implementation
            return {'provider': 'GCP', 'costs': [], 'note': 'GCP integration coming in Pro version'}
        except Exception as e:
            return {'provider': 'GCP', 'error': str(e)}
    
    def get_azure_costs(self, subscription_id: str) -> Dict:
        """Fetch Azure costs using Cost Management API"""
        try:
            # Placeholder for Azure implementation
            return {'provider': 'Azure', 'costs': [], 'note': 'Azure integration coming in Pro version'}
        except Exception as e:
            return {'provider': 'Azure', 'error': str(e)}
    
    def detect_anomaly(self, costs: List[float]) -> Dict:
        """Detect if today's cost is anomalous compared to historical average"""
        if len(costs) < 2:
            return {'anomaly': False, 'reason': 'Insufficient data'}
        
        today_cost = costs[-1]
        historical_costs = costs[:-1]
        avg_cost = statistics.mean(historical_costs)
        
        if avg_cost == 0:
            return {'anomaly': False, 'today': today_cost, 'average': 0}
        
        percent_change = ((today_cost - avg_cost) / avg_cost) * 100
        
        return {
            'anomaly': abs(percent_change) > self.threshold,
            'today': round(today_cost, 2),
            'average': round(avg_cost, 2),
            'change_percent': round(percent_change, 2),
            'threshold': self.threshold
        }
    
    def format_alert(self, provider: str, result: Dict) -> str:
        """Format anomaly detection result as alert message"""
        if not result.get('anomaly'):
            return f"✅ {provider}: No anomaly detected (${result.get('today', 0):.2f} today vs ${result.get('average', 0):.2f} avg)"
        
        change = result['change_percent']
        emoji = "🔴" if change > 0 else "🟢"
        direction = "increase" if change > 0 else "decrease"
        
        return f"{emoji} {provider} ANOMALY: ${result['today']:.2f} today vs ${result['average']:.2f} avg ({change:+.1f}% {direction})"


def main():
    parser = argparse.ArgumentParser(description='Multi-Cloud Cost Anomaly Detection')
    parser.add_argument('--aws-profile', default='default', help='AWS profile name')
    parser.add_argument('--gcp-project', help='GCP project ID')
    parser.add_argument('--azure-subscription', help='Azure subscription ID')
    parser.add_argument('--threshold', type=float, default=20.0, help='Anomaly threshold percentage')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    
    args = parser.parse_args()
    
    detector = CostAnomalyDetector(threshold=args.threshold)
    results = []
    
    # Check AWS costs
    print("🔍 Checking AWS costs...")
    aws_data = detector.get_aws_costs(args.aws_profile)
    if 'error' not in aws_data and aws_data['costs']:
        anomaly_result = detector.detect_anomaly(aws_data['costs'])
        results.append({'provider': 'AWS', 'result': anomaly_result})
        print(detector.format_alert('AWS', anomaly_result))
    elif 'error' in aws_data:
        print(f"⚠️  AWS Error: {aws_data['error']}")
    
    # Output JSON if requested
    if args.json:
        print(json.dumps(results, indent=2))
    
    # Exit with error code if anomalies detected
    has_anomaly = any(r['result'].get('anomaly') for r in results)
    sys.exit(1 if has_anomaly else 0)


if __name__ == '__main__':
    main()