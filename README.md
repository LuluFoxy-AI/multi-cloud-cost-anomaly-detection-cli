# Multi-Cloud Cost Anomaly Detection CLI

🚨 **Catch cloud cost spikes before they drain your budget**

A lightweight Python CLI that monitors AWS and Azure spending patterns, automatically detecting cost anomalies from misconfigured autoscaling, zombie resources, and dev environment sprawl.

## The Problem

DevOps teams typically discover cloud cost overruns **after** they happen—when the bill arrives. By then, a misconfigured autoscaling group or forgotten test environment may have already cost thousands.

## What This Tool Does

- **Compares** last 7 days of spending vs. the previous 7-day period
- **Flags** services with >20% cost increases (configurable threshold)
- **Detects** new services with unexpected charges
- **Alerts** via terminal output or webhook (Slack, Discord, PagerDuty)
- **Supports** AWS (Azure coming soon)

## Installation

```bash
# Clone the repository
git clone https://github.com/LuluFoxy-AI/multi-cloud-cost-anomaly-detection-cli.git
cd multi-cloud-cost-anomaly-detection-cli

# Install dependencies
pip install -r requirements.txt

# Configure AWS credentials
aws configure
```

## Usage

```bash
# Analyze AWS costs with default 20% threshold
python cost_anomaly_detector.py --cloud aws

# Custom threshold and webhook notification
python cost_anomaly_detector.py --cloud aws --threshold 15 --webhook https://hooks.slack.com/services/YOUR/WEBHOOK/URL

# JSON output for automation
python cost_anomaly_detector.py --cloud aws --json
```

## Configuration

### AWS Setup
Requires AWS credentials with `ce:GetCostAndUsage` permission:

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": "ce:GetCostAndUsage",
    "Resource": "*"
  }]
}
```

### Webhook Integration
Supports any webhook endpoint accepting JSON POST requests (Slack, Discord, Microsoft Teams, PagerDuty).

## Free vs Paid

**Free (Open Source)**
- ✅ 1 cloud account monitoring
- ✅ Terminal output
- ✅ Basic webhook support
- ✅ Manual execution

**Pro ($29/mo per account)**
- ✅ Unlimited cloud accounts
- ✅ Automated daily checks
- ✅ Slack/Teams integration
- ✅ Historical trend analysis
- ✅ Custom alert rules
- ✅ Priority support

**Team ($99/mo)**
- ✅ Everything in Pro
- ✅ 5 cloud accounts included
- ✅ Shared team dashboard
- ✅ Role-based access

## Roadmap

- [ ] Azure support
- [ ] GCP support
- [ ] Scheduled execution (cron)
- [ ] Web dashboard
- [ ] Cost forecasting

## License

MIT License - Free for personal and commercial use

## Support

- 🐛 Issues: [GitHub Issues](https://github.com/LuluFoxy-AI/multi-cloud-cost-anomaly-detection-cli/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/LuluFoxy-AI/multi-cloud-cost-anomaly-detection-cli/discussions)
- 📧 Email: support@lulufoxy.ai

---

**Star this repo** if it saves you from a surprise cloud bill! ⭐