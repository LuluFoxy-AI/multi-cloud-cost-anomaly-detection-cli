# Multi-Cloud Cost Anomaly Detection CLI

🚨 **Stop cloud cost surprises before they drain your budget**

A lightweight Python CLI that monitors AWS, GCP, and Azure costs daily and alerts you to anomalies before they become expensive problems.

## The Problem

DevOps teams discover cost spikes weeks later when the bill arrives:
- Misconfigured auto-scaling groups spinning up hundreds of instances
- Zombie resources left running after testing
- Accidental deployments to expensive regions
- Data transfer costs from misrouted traffic

Enterprise tools cost $500+/month. Manual checking is tedious and error-prone.

## What This Does

✅ Compares today's cloud costs to your 7-day average
✅ Alerts when costs spike >20% (configurable threshold)
✅ Works as a CLI tool or GitHub Action for daily automation
✅ Supports AWS (GCP/Azure in Pro version)
✅ Zero configuration for AWS (uses existing credentials)

## Installation

```bash
pip install boto3 google-cloud-billing azure-mgmt-costmanagement azure-identity
git clone https://github.com/LuluFoxy-AI/multi-cloud-cost-anomaly-detection-cli.git
cd multi-cloud-cost-anomaly-detection-cli
```

## Usage

### Basic Usage (AWS)

```bash
python cloudcost.py --aws-profile default
```

### Custom Threshold

```bash
python cloudcost.py --threshold 15.0  # Alert on 15% change
```

### JSON Output (for automation)

```bash
python cloudcost.py --json
```

### GitHub Action (Daily Monitoring)

Add to `.github/workflows/cost-monitor.yml`:

```yaml
name: Daily Cost Check
on:
  schedule:
    - cron: '0 9 * * *'  # 9 AM daily
jobs:
  cost-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
      - run: pip install boto3
      - run: python cloudcost.py
        env:
          AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
```

## Configuration

### AWS Setup

Uses your existing AWS credentials (`~/.aws/credentials` or environment variables). Requires `ce:GetCostAndUsage` permission.

### Environment Variables

- `CLOUDCOST_LICENSE_KEY`: Your Pro license key (for unlimited accounts)
- `AWS_PROFILE`: AWS profile to use (default: 'default')

## Free vs Pro

### Free Tier
- ✅ 1 AWS account
- ✅ 7-day cost history
- ✅ 20% threshold detection
- ✅ CLI + GitHub Action

### Pro Tier ($29/month)
- ✅ Unlimited cloud accounts (AWS/GCP/Azure)
- ✅ Slack/Discord webhook integration
- ✅ 90-day cost history
- ✅ Custom thresholds per account
- ✅ Priority support

[Get Pro License](https://gumroad.com/l/cloudcost-pro)

### Team Tier ($99/month)
- Everything in Pro, plus:
- ✅ SSO/SAML authentication
- ✅ REST API access
- ✅ Custom integrations
- ✅ Dedicated support

## License

MIT License - Free tier is completely open source. Pro features require a license key.

## Support

Issues: https://github.com/LuluFoxy-AI/multi-cloud-cost-anomaly-detection-cli/issues
Email: support@cloudcost.dev