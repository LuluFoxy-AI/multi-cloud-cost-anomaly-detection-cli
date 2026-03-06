#!/usr/bin/env python3
"""
Multi-Cloud Cost Anomaly Detection CLI
AWS-focused MVP for detecting common cloud waste patterns

This tool scans your AWS infrastructure for:
- Unattached EBS volumes
- Idle load balancers (ELB/ALB/NLB)
- Oversized RDS instances with low CPU utilization
- Stopped EC2 instances still incurring costs

Author: LuluFoxy-AI
License: MIT
"""

import boto3
import json
from datetime import datetime, timedelta
from collections import defaultdict
import argparse
import sys


class AWSCostAnomalyDetector:
    """Detects cost anomalies in AWS infrastructure"""
    
    def __init__(self, region='us-east-1', profile=None):
        """Initialize AWS clients"""
        session_kwargs = {'region_name': region}
        if profile:
            session_kwargs['profile_name'] = profile
        
        session = boto3.Session(**session_kwargs)
        self.ec2 = session.client('ec2')
        self.elb = session.client('elb')
        self.elbv2 = session.client('elbv2')
        self.rds = session.client('rds')
        self.cloudwatch = session.client('cloudwatch')
        self.region = region
        self.anomalies = []
        self.total_monthly_waste = 0.0

    def scan_unattached_ebs_volumes(self):
        """Find EBS volumes not attached to any instance"""
        print("[*] Scanning for unattached EBS volumes...")
        volumes = self.ec2.describe_volumes(
            Filters=[{'Name': 'status', 'Values': ['available']}]
        )['Volumes']
        
        for volume in volumes:
            size = volume['Size']
            volume_type = volume['VolumeType']
            monthly_cost = size * 0.08
            
            self.anomalies.append({
                'type': 'Unattached EBS Volume',
                'resource_id': volume['VolumeId'],
                'details': f"{size}GB {volume_type}",
                'monthly_waste': monthly_cost,
                'recommendation': 'Delete if unused or create snapshot'
            })
            self.total_monthly_waste += monthly_cost

    def scan_idle_load_balancers(self):
        """Find load balancers with no active targets or low traffic"""
        print("[*] Scanning for idle load balancers...")
        
        classic_lbs = self.elb.describe_load_balancers()['LoadBalancerDescriptions']
        for lb in classic_lbs:
            lb_name = lb['LoadBalancerName']
            instances = lb['Instances']
            
            if len(instances) == 0:
                monthly_cost = 18.0
                self.anomalies.append({
                    'type': 'Idle Classic Load Balancer',
                    'resource_id': lb_name,
                    'details': 'No registered instances',
                    'monthly_waste': monthly_cost,
                    'recommendation': 'Delete if unused'
                })
                self.total_monthly_waste += monthly_cost
