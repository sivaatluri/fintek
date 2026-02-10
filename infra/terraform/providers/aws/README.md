# Terraform Configuration for AWS Deployment

This directory contains Terraform modules for deploying the FinOps SaaS platform on AWS.

## Structure

```
aws/
├── main.tf           # Main configuration
├── variables.tf      # Input variables
├── outputs.tf        # Output values
├── vpc.tf            # VPC and networking
├── eks.tf            # EKS cluster
├── rds.tf            # PostgreSQL RDS
├── elasticache.tf    # Redis ElastiCache
├── s3.tf             # S3 buckets
├── msk.tf            # Managed Kafka (MSK)
├── iam.tf            # IAM roles and policies
└── versions.tf       # Provider versions
```

## Prerequisites

- Terraform 1.5+
- AWS CLI configured
- Valid AWS credentials

## Usage

```bash
# Initialize
terraform init

# Plan
terraform plan -var-file="dev.tfvars"

# Apply
terraform apply -var-file="dev.tfvars"

# Destroy
terraform destroy -var-file="dev.tfvars"
```

## Variables

Key variables to configure:

- `region`: AWS region (default: us-east-1)
- `environment`: Environment name (dev/staging/prod)
- `vpc_cidr`: VPC CIDR block
- `db_instance_class`: RDS instance type
- `eks_node_instance_types`: EKS node instance types

## Outputs

- `vpc_id`: VPC identifier
- `eks_cluster_endpoint`: EKS cluster endpoint
- `rds_endpoint`: PostgreSQL endpoint
- `s3_bucket_name`: Data lake S3 bucket

## Security

- All resources use encryption at rest
- VPC with private subnets for data layer
- Security groups with least privilege
- IAM roles with minimal permissions

See [main documentation](/docs/architecture/) for architecture details.
