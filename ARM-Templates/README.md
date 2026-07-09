# ARM Templates

Deploy a pre-configured Microsoft Sentinel workspace for Track B and C labs.

## What Gets Deployed

- Log Analytics workspace with Microsoft Sentinel enabled
- Data connectors: Microsoft 365, Defender XDR, Purview
- Pre-loaded demo data (~20MB) simulating agentic activity
- Sample Analytics Rules for each security domain
- Sample Watchlist: known agent identifiers

## Deploy

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fjcastanedacano%2Fagent-zero%2Fmain%2FARM-Templates%2Fazuredeploy.json)

## Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `workspaceName` | Sentinel workspace name | `agentic-security-lab` |
| `location` | Azure region | Resource group location |
| `retentionDays` | Log retention in days | `30` |

## Cost

Expected cost for lab duration (1 day): < $5 USD using the Sentinel 30-day trial.
