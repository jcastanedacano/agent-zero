# Contributing

Contributions are welcome. This project improves with real-world experience from practitioners running these labs.

---

## What to Contribute

### KQL Queries
The most valuable contributions. To add a query:
- Place it in `/KQL-Library/` in the relevant `P0X-*.kql` file
- Include a comment block with: description, target tables, required permissions, recommended alert frequency if applicable
- Test against a demo or trial tenant before submitting
- Note any table availability requirements (e.g., "requires Sentinel workspace", "requires MDE connector")

### Lab Module Improvements
- Corrections to step-by-step instructions when Microsoft UI changes
- Additional exercises for specific scenarios (regulated industries, specific agent types)
- Translations of Track A materials into Spanish, Portuguese, or French

### ARM Template
- Improvements to the demo environment deployment
- Additional pre-loaded data sets for lab exercises
- Bicep conversion of the ARM template

### Issues
Open an issue for:
- Broken instructions due to Microsoft product updates
- KQL queries that no longer work due to schema changes
- Missing coverage for a risk vector or agent type

---

## What Not to Contribute

- Vendor-specific content not using Microsoft native controls
- Content that assumes infrastructure beyond M365 E5 + Azure subscription
- Marketing content or references to specific consulting services

---

## Pull Request Process

1. Fork the repository
2. Create a branch: `feature/your-contribution-name`
3. Make your changes
4. Test any KQL queries in a demo tenant
5. Submit a PR with a brief description of what changed and why

---

## Code of Conduct

Be direct, be accurate, be useful. Attribution for original contributions is maintained in commit history.
