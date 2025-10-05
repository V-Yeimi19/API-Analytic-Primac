# Data Science Analytics API - Primac S3

## Overview

This FastAPI-based API provides essential data analysis endpoints for processing and analyzing enterprise data stored in AWS S3. The API specializes in processing Primac company data from multiple database sources (MySQL, PostgreSQL and Cassandra) that have been ingested and stored in S3 for unified analysis.

## Key Features

### 📊 Multi-Database Analytics
- **MySQL Analytics**: 2 queries - User statistics + Growth by state
- **PostgreSQL Analytics**: 2 queries - Product analysis + Product profitability
- **Cassandra Analytics**: 2 queries - Claims analysis + Claims-payments correlation

### 🔗 Cross-System Analytics (3 Key Queries)
- **Customer Policy Profile**: Customer and policy profile (MySQL + PostgreSQL)
- **Agent Performance**: Agent performance across systems (MySQL + PostgreSQL)
- **Claims vs Policies**: Claims analysis (PostgreSQL + Cassandra)

### 🎨 Technical Features
- **High Performance**: Built with FastAPI for optimal performance
- **S3 Integration**: Direct processing from AWS S3 without direct DB connections
- **Clean Architecture**: Simplified and maintainable code
- **Containerized**: Ready-to-deploy Docker container
- **Interactive Documentation**: Swagger UI and ReDoc included

## Architecture

```
┌────────────────────────┐    ┌──────────────────────┐    ┌─────────────────────────┐
│      Data Sources      │    │    AWS S3 Bucket    │    │     Analytics API     │
│                        │───▶│                      │───▶│                       │
│ • MySQL (Users)        │    │ • mysql/*.csv        │    │ • MySQL Analytics     │
│ • PostgreSQL (Policies)│    │ • postgresql/*.csv   │    │ • PostgreSQL Analytics│
│ • Cassandra (Payments) │    │ • cassandra/*.csv    │    │ • Cassandra Analytics │
│                        │    │                      │    │ • Cross-Analytics     │
└────────────────────────┘    └──────────────────────┘    └─────────────────────────┘
```

### Data Flow
1. **Ingestion**: Data from MySQL, PostgreSQL and Cassandra is ingested into AWS S3
2. **Storage**: Data is stored as CSV files organized by source
3. **Analysis**: The API reads directly from S3 and processes data using Pandas
4. **Response**: Results are returned as structured JSON

## Complete Endpoint Documentation

**Base URL**: `http://localhost:8000`  
**Version**: `2.0.0` (S3 Analytics)

### 🟢 Health Check

#### GET `/`
**Description**: General API information  
**Response**:
```json
{
    "message": "API Analytics - Primac S3",
    "version": "2.0.0",
    "status": "OK",
    "data_source": "S3 Bucket",
    "available_databases": ["MySQL", "PostgreSQL", "Cassandra"],
    "endpoints": {
        "mysql": 2,
        "postgresql": 2,
        "cassandra": 2,
        "cross_microservice": 3
    }
}
```

#### GET `/health`
**Description**: S3 data availability status  
**Response**:
```json
{
    "status": "OK",
    "timestamp": "2024-10-04T20:39:08Z",
    "data_availability": {
        "mysql": {"users": true, "clients": true, "agents": true, "beneficiaries": true},
        "postgresql": {"products": true, "policies": true, "policy_coverage": true, "beneficiaries": true},
        "cassandra": {"reclamos": true, "pagos": true, "transaction_audit": true}
    },
    "bucket_summary": {
        "total_objects": 9,
        "total_size_mb": 156.7,
        "databases": {"mysql": 4, "postgresql": 4, "cassandra": 3}
    }
}
```

## 🎯 ENDPOINTS (11 Total)

### 📊 MySQL Analytics (2 endpoints)

**1. [GENERAL] User Statistics:**
- **GET** `/mysql/analytics/users` - Complete user analysis including roles, states, and data quality

**2. [SPECIFIC] Growth by State:**
- **GET** `/mysql/analytics/growth-by-state?months=12` - User growth by state over N months

### 📄 PostgreSQL Analytics (2 endpoints)

**1. [GENERAL] Product Analysis:**
- **GET** `/postgresql/analytics/products` - Complete product analysis including types, premiums, and codes

**2. [SPECIFIC] Product Profitability:**
- **GET** `/postgresql/analytics/product-profitability` - Profitability analysis combining products and policies

### 💰 Cassandra Analytics (2 endpoints)

**1. [GENERAL] Claims Analysis:**
- **GET** `/cassandra/analytics/claims` - Complete claims analysis including status, amounts, and temporal patterns

**2. [SPECIFIC] Claims-Payments Correlation:**
- **GET** `/cassandra/analytics/claims-payments-correlation` - Correlation between claims and payments patterns

### 🔗 Cross-Microservice Analytics (3 key endpoints)

**1. [CROSS 1] Customer-Policy Profile:**
- **GET** `/cross/analytics/customer-policy-profile` - JOIN MySQL + PostgreSQL for complete customer profile

**2. [CROSS 2] Agent Performance:**
- **GET** `/cross/analytics/agent-performance` - JOIN MySQL + PostgreSQL for cross-system agent performance

**3. [CROSS 3] Claims Analysis:**
- **GET** `/cross/analytics/claims-vs-policies` - JOIN PostgreSQL + Cassandra for claims analysis

## 📝 Response Format and HTTP Codes

### HTTP Status Codes

- **200**: OK - Successful request
- **404**: Not Found - Resource not found
- **422**: Validation Error - Error in input parameters
- **500**: Internal Server Error - Internal server error (S3 or processing issue)

### Error Format
```json
{
    "detail": "Error: Could not load mysql/users/users.csv: NoSuchKey"
}
```

### Analytics Response Examples

#### MySQL User Statistics Response
```json
{
    "total_users": 1500,
    "users_by_role": {"USER": 1200, "ADMIN": 50, "AGENT": 250},
    "users_by_state": {"LIMA": 800, "AREQUIPA": 300, "CUSCO": 200},
    "recent_registrations": 45,
    "top_cities": {"Lima": 800, "Arequipa": 300, "Cusco": 200},
    "monthly_registrations": {"2024-09": 123, "2024-10": 89},
    "data_quality": {
        "missing_emails": 12,
        "missing_phones": 45,
        "duplicate_emails": 3
    }
}
```

#### PostgreSQL Product Analysis Response
```json
{
    "total_products": 50,
    "product_types": {"VIDA": 20, "SALUD": 15, "AUTO": 15},
    "premium_statistics": {
        "average_premium": 250.75,
        "median_premium": 200.0,
        "max_premium": 1500.0,
        "premium_distribution": {"< 100": 10, "100-499": 25, "500-999": 10}
    },
    "data_completeness": {
        "products_with_premium": 48,
        "products_with_description": 45
    }
}
```

#### Cross-Analytics Customer Profile Response
```json
{
    "summary": {
        "total_customers": 10000,
        "customers_with_policies": 6200,
        "penetration_rate": 62.0,
        "total_policies": 8500,
        "total_premium_volume": 15750000.50
    },
    "demographic_analysis": {
        "by_state": {
            "LIMA": {"total_users": 5000, "with_policies": 3200, "conversion_rate": 64.0}
        }
    }
}
```

## Environment Variables

The API requires the following environment variables for AWS S3 integration:

| Variable | Description | Default Value |
|----------|-------------|---------------|
| `AWS_ACCESS_KEY_ID` | AWS Access Key ID | Required |
| `AWS_SECRET_ACCESS_KEY` | AWS Secret Access Key | Required |
| `AWS_SESSION_TOKEN` | AWS Session Token (if using temporary credentials) | Optional |
| `AWS_DEFAULT_REGION` | AWS Region | `us-east-1` |
| `S3_BUCKET` | S3 Bucket name containing the data | `bucket-name` |

## Database Management

### Unified Orchestrator

The project includes an improved orchestration script that manages MySQL, PostgreSQL, and Cassandra

```bash
# Start all databases + setup + seed
python orchestrator.py all

# Start individual databases
python orchestrator.py mysql
python orchestrator.py postgresql  
python orchestrator.py cassandra

# Start database + configure schema
python orchestrator.py mysql+setup
python orchestrator.py postgresql+setup
python orchestrator.py cassandra+setup

# Only fake data (requires DBs already configured)
python orchestrator.py faker
```

### Database Project


## API Installation and Setup

### Prerequisites

- Python 3.11+
- Docker and Docker Compose
- AWS credentials with S3 access
- S3 bucket configured with CSV data

### Local Development Setup

1. **Clone and navigate to the project:**
   ```bash
   cd API-Analytic-Primac
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set environment variables:**
   ```bash
   export AWS_ACCESS_KEY_ID="your_access_key"
   export AWS_SECRET_ACCESS_KEY="your_secret_key"
   export AWS_DEFAULT_REGION="us-east-1"
   export S3_BUCKET="bucket-name"
   ```

5. **Run the application:**
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

### Docker Setup

1. **Build the Docker image:**
   ```bash
   docker build -t API-Analytic-Primac .
   ```

2. **Run with Docker:**
   ```bash
   docker run -p 8000:8000 \
     -e AWS_ACCESS_KEY_ID="your_access_key" \
     -e AWS_SECRET_ACCESS_KEY="your_secret_key" \
     -e AWS_DEFAULT_REGION="us-east-1" \
     -e S3_BUCKET="bucket-name" \
     API-Analytic-Primac
   ```

### Docker Compose Setup

From the project root directory:

1. **Create a `.env` file with your AWS credentials:**
   ```env
   AWS_ACCESS_KEY_ID=your_access_key
   AWS_SECRET_ACCESS_KEY=your_secret_key
   AWS_DEFAULT_REGION=us-east-1
   S3_BUCKET=bucket-name
   ```

2. **Start the service:**
   ```bash
   docker-compose up API-Analytic-Primac
   ```

## Usage Examples

### 📊 MySQL Analytics (2 endpoints)

```bash
# [GENERAL] User analysis
curl "http://localhost:8000/mysql/analytics/users"

# [SPECIFIC] Growth by state (6 months)
curl "http://localhost:8000/mysql/analytics/growth-by-state?months=6"
```

### 📄 PostgreSQL Analytics (2 endpoints)

```bash
# [GENERAL] Product analysis
curl "http://localhost:8000/postgresql/analytics/products"

# [SPECIFIC] Product profitability
curl "http://localhost:8000/postgresql/analytics/product-profitability"
```

### 💰 Cassandra Analytics (2 endpoints)

```bash
# [GENERAL] Claims analysis
curl "http://localhost:8000/cassandra/analytics/claims"

# [SPECIFIC] Claims-payments correlation
curl "http://localhost:8000/cassandra/analytics/claims-payments-correlation"
```

### 🔗 Cross-System Analytics (3 key endpoints)

```bash
# [CROSS 1] Customer-policy profile
curl "http://localhost:8000/cross/analytics/customer-policy-profile"

# [CROSS 2] Agent performance
curl "http://localhost:8000/cross/analytics/agent-performance"

# [CROSS 3] Claims analysis (claims vs policies)
curl "http://localhost:8000/cross/analytics/claims-vs-policies"
```

### 🐍 Using Python

```python
import requests
import json

base_url = "http://localhost:8000"

# [CROSS 1] Complete customer-policy profile
response = requests.get(f"{base_url}/cross/analytics/customer-policy-profile")
profile_data = response.json()

print(f"Penetration rate: {profile_data['summary']['penetration_rate']}%")
print(f"Total customers: {profile_data['summary']['total_customers']}")
print(f"Customers with policies: {profile_data['summary']['customers_with_policies']}")

# [SPECIFIC] Product profitability
response = requests.get(f"{base_url}/postgresql/analytics/product-profitability")
profitability = response.json()

print("\nTop products by volume:")
for product in profitability['top_products_by_volume'][:3]:
    print(f"- {product['name']}: {product['policy_number_count']} policies")

# [GENERAL] MySQL user statistics
response = requests.get(f"{base_url}/mysql/analytics/users")
users_data = response.json()

print(f"\nTotal users: {users_data['total_users']}")
print(f"Recent registrations: {users_data['recent_registrations']}")
```

## 📚 Interactive Documentation

Once the API is running, you can access:

- **Swagger UI**: `http://localhost:8000/docs` - Interactive documentation with live testing
- **ReDoc**: `http://localhost:8000/redoc` - Alternative documentation with better readability
- **OpenAPI Schema**: `http://localhost:8000/openapi.json` - Complete technical specification

## 🚽 Troubleshooting

### Common Issues

#### AWS Credentials Error
```
Detail: Error: An error occurred (InvalidAccessKeyId) when calling the GetObject operation
```
**Solution:**
- Verify that `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` are correctly configured
- Check IAM permissions for S3 access
- Use the `/health` endpoint to diagnose connection

#### S3 Access Error
```
Detail: Error: Could not load mysql/users/users.csv: NoSuchKey
```
**Solution:**
- Verify bucket name and region in `S3_BUCKET` and `AWS_DEFAULT_REGION`
- Check that CSV files exist in expected S3 paths
- Use `/health` to see dataset availability

#### Data Processing Error
```
Detail: Error analyzing users: 'estado' column not found
```
**Solution:**
- Verify CSV file format and column names
- Check for empty or corrupted files
- Review expected structure in "Key Fields per Dataset" section

#### Error 422 - Validation Error
```json
{
    "detail": [
        {
            "loc": ["query", "months"],
            "msg": "ensure this value is greater than or equal to 1",
            "type": "value_error.number.not_ge"
        }
    ]
}
```
**Solution:**
- Verify parameters are in correct format
- `months` must be between 1 and 36

### Diagnostic Commands

```bash
# Check general status
curl http://localhost:8000/health

# Test a simple endpoint
curl http://localhost:8000/mysql/analytics/users

# Check container logs
docker logs <container_name>
```

## S3 Data Structure

### S3 Bucket Organization

```
s3://bucket-name/
├── mysql/
│   ├── users/
│   │   └── users.csv
│   ├── clients/
│   │   └── clients.csv
│   ├── agents/
│   │   └── agents.csv
│   └── beneficiaries/
│       └── beneficiaries.csv
├── postgresql/
│   ├── products/
│   │   └── products.csv
│   ├── policies/
│   │   └── policies.csv
│   ├── policy_coverage/
│   │   └── policy_coverage.csv
│   └── beneficiaries/
│       └── beneficiaries.csv
└── cassandra/
    ├── reclamos/
    │   └── reclamos.csv
    ├── pagos/
    │   └── pagos.csv
    └── transaction_audit/
        └── transaction_audit.csv
```

### Key Fields per Dataset

**MySQL:**
- `users`: id, username, email, role, phone, state, city, created_at
- `clients`: user_id, first_name, last_name, document_type, birth_date
- `agents`: id, code, first_name, last_name, is_active
- `beneficiaries`: client_id, relationship, birth_date

**PostgreSQL:**
- `products`: id, code, name, product_type, base_premium
- `policies`: id, policy_number, customer_id, agent_id, premium, sum_insured
- `policy_coverage`: policy_id, coverage_name, coverage_limit, deductible
- `beneficiaries`: policy_id, client_id, full_name, relationship

**Cassandra:**
- `reclamos`: id, policy_number, estado, monto, fecha_reclamo
- `pagos`: id, customer_id, monto, metodo_pago, fecha_pago
- `transaction_audit`: timestamp, servicio, operacion, user_id

## Deployment

### AWS ECS Deployment Example

```bash
# Build and push to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com
docker build -t API-Analytic-Primac .
docker tag API-Analytic-Primac:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/API-Analytic-Primac:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/API-Analytic-Primac:latest
```

## Main Dependencies

- **FastAPI 0.100.0+**: Modern web framework for building APIs
- **Uvicorn 0.23.2+**: High-performance ASGI server
- **Boto3 1.26.150+**: AWS SDK for S3 integration
- **Pandas 2.1.1+**: Data manipulation and analysis library
- **NumPy 1.26.0+**: Numerical computing and matrix operations
- **python-dotenv 1.1.1+**: Environment variable management

## Analysis Modules

- **s3_data_manager**: Unified S3 data manager
- **mysql_s3_analytics**: MySQL data analysis from S3
- **postgresql_s3_analytics**: PostgreSQL data analysis from S3
- **cassandra_s3_analytics**: Cassandra data analysis from S3
- **cross_microservice_analytics**: Cross-system analytics

## Problem Solving

### Common Issues

1. **AWS Credentials Error**
   - Ensure AWS credentials are properly configured
   - Check IAM permissions for S3 access

2. **S3 Access Error**
   - Verify bucket name and region
   - Check if CSV files exist in expected S3 paths

3. **Data Processing Error**
   - Verify CSV file format and column names
   - Check for empty or corrupted files

### Status Verification

Add a status verification endpoint by visiting: `http://localhost:8000/docs`

## Useful Commands

### Local Development
```bash
# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run in development mode
uvicorn main:app --reload

# Run tests (if they exist)
pytest

# Format code
black main.py

# Check linting
flake8 main.py
```

## Available Analysis Types

### 📊 Descriptive Analytics
- Basic statistics and distributions
- Counts and averages by categories
- Data completeness analysis

### 📈 Temporal Analytics
- Monthly and seasonal trends
- Hourly activity patterns
- Growth and temporal changes

### 🔗 Relational Analytics
- JOINs between different data sources
- Complete customer journey
- Metric correlations

### 🎯 Specialized Analytics
- Product profitability
- Claims and risk analysis
- Agent performance
- Data quality

---

**API Version:** 2.0.0
**Last Update:** October 2024 
**Status:** Functional and optimized for S3 analytics
**Total Endpoints:** 11 (2 health + 6 microservice + 3 cross-analytics)

### Docker
```bash
# Build image
docker build -t API-Analytic-Primac .

# Run container
docker run -p 8000:8000 API-Analytic-Primac

# View container logs
docker logs <container_id>

# Access container
docker exec -it <container_id> /bin/bash
```

### AWS CLI
```bash
# Configure credentials
aws configure

# List objects in S3
aws s3 ls s3://bucket-name/

# Download file from S3
aws s3 cp s3://bucket-name/cassandra/reclamos/reclamos.csv ./

# Verify bucket permissions
aws s3api get-bucket-policy --bucket bucket-name
```
