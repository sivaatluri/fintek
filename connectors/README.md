# Cloud Provider Connectors

This directory contains connectors for various cloud providers.

## Planned Connectors

- AWS Cost and Usage Reports
- Azure Cost Management
- Google Cloud Billing
- Oracle Cloud Infrastructure
- Alibaba Cloud

## Connector Structure

Each connector should:
1. Implement data fetching from the provider
2. Normalize data to canonical schema
3. Handle authentication and credentials
4. Support incremental sync
5. Handle rate limiting and retries

## Example Connector

```python
class AWSConnector:
    def __init__(self, credentials):
        self.credentials = credentials
    
    def fetch_costs(self, start_date, end_date):
        # Fetch cost data from AWS
        pass
    
    def normalize_data(self, raw_data):
        # Convert to canonical CostRecord schema
        pass
```

## Future Work

Connectors will be implemented as separate packages that can be:
- Installed independently
- Configured per tenant
- Scheduled for automatic sync
