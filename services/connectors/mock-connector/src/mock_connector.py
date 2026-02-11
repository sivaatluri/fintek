"""
Mock connector for generating synthetic cost data.
"""

import uuid
import random
from datetime import date, datetime, timedelta
from typing import List, Dict, Any
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../cost-ingestion-service/src'))

from connectors.base import BaseConnector


class MockConnector(BaseConnector):
    """Mock connector that generates synthetic cost data"""
    
    CLOUD_CONFIGS = {
        "aws": {
            "services": [
                ("EC2", "t3.micro", "hours", 0.0104),
                ("S3", "gp3-storage", "GB", 0.08),
                ("RDS", "db.t3.micro", "hours", 0.017),
                ("Lambda", "lambda-requests", "requests", 0.0000002),
            ],
            "regions": ["us-east-1", "us-west-2", "eu-west-1", "ap-southeast-1"]
        },
        "azure": {
            "services": [
                ("Virtual Machines", "Standard_D2s_v3", "hours", 0.096),
                ("Storage", "StorageV2", "GB", 0.0184),
                ("SQL Database", "GP_Gen5_2", "hours", 0.562),
            ],
            "regions": ["eastus", "westus2", "westeurope", "southeastasia"]
        },
        "gcp": {
            "services": [
                ("Compute Engine", "n1-standard-1", "hours", 0.0475),
                ("Cloud Storage", "standard-storage", "GB", 0.02),
                ("BigQuery", "on-demand-queries", "TB", 5.0),
            ],
            "regions": ["us-central1", "us-west1", "europe-west1", "asia-southeast1"]
        },
        "oracle": {
            "services": [
                ("Compute", "VM.Standard2.1", "hours", 0.067),
                ("Block Storage", "block-storage", "GB", 0.0255),
                ("Autonomous Database", "autonomous-db", "hours", 3.0),
            ],
            "regions": ["us-ashburn-1", "us-phoenix-1", "eu-frankfurt-1", "ap-tokyo-1"]
        },
        "akamai": {
            "services": [
                ("CDN", "cdn-delivery", "GB", 0.085),
                ("WAF", "waf-requests", "requests", 0.000006),
                ("DNS", "dns-queries", "queries", 0.0000004),
            ],
            "regions": ["global"]
        },
        "datacenter": {
            "services": [
                ("Compute", "physical-server", "hours", 2.5),
                ("Storage", "san-storage", "TB", 50.0),
                ("Network", "network-port", "hours", 1.0),
            ],
            "regions": ["dc-us-east", "dc-us-west", "dc-eu-central"]
        }
    }
    
    async def fetch_data(
        self,
        start_date: date,
        end_date: date
    ) -> List[Dict[str, Any]]:
        """
        Generate synthetic cost data.
        
        Args:
            start_date: Start date
            end_date: End date
            
        Returns:
            List of raw cost records
        """
        records = []
        records_per_day = self.config.get("records_per_day", 1000)
        cloud_provider = self.config.get("cloud_provider", "aws")
        
        # Get cloud config
        cloud_config = self.CLOUD_CONFIGS.get(cloud_provider, self.CLOUD_CONFIGS["aws"])
        
        # Generate records for each day
        current_date = start_date
        while current_date <= end_date:
            for _ in range(records_per_day):
                service, sku, unit, base_price = random.choice(cloud_config["services"])
                region = random.choice(cloud_config["regions"])
                
                # Random variations
                quantity = random.uniform(0.1, 1000.0)
                price_variation = random.uniform(0.9, 1.1)
                cost = quantity * base_price * price_variation
                
                record = {
                    "record_id": str(uuid.uuid4()),
                    "org_id": self.org_id,
                    "cloud_provider": cloud_provider,
                    "billing_account_id": f"account-{random.randint(1000, 9999)}",
                    "service_name": service,
                    "sku": sku,
                    "usage_date": current_date.isoformat(),
                    "usage_quantity": round(quantity, 4),
                    "unit": unit,
                    "cost": round(cost, 6),
                    "currency": "USD",
                    "region": region,
                    "resource_id": f"resource-{uuid.uuid4().hex[:8]}",
                    "tags": {
                        "Environment": random.choice(["production", "staging", "development"]),
                        "Team": random.choice(["engineering", "data", "product"]),
                        "Project": f"project-{random.randint(1, 10)}"
                    },
                    "raw_metadata": {
                        "provider_specific": True,
                        "generated": True
                    }
                }
                
                records.append(record)
            
            current_date += timedelta(days=1)
        
        return records
    
    async def validate_config(self) -> bool:
        """Validate mock connector configuration"""
        # Mock connector is always valid
        return True


# Register with connector registry
if __name__ != "__main__":
    from connectors.registry import connector_registry
    connector_registry.register("mock", MockConnector)
