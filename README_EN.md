# Data Science Analytics API

## Overview

This FastAPI-based Data Science Analytics API provides data analysis endpoints for processing and analyzing business data stored in AWS S3. The API specializes in processing claims, payments, and audit transaction data from various database sources (Cassandra, MySQL, PostgreSQL) that have been ingested into S3.

## Features

- **Claims Analytics**: Statistical analysis of insurance claims data
- **Payment Analytics**: Financial payment data analysis and averages
- **Audit Analytics**: Transaction audit reporting and top services analysis
- **Cloud Integration**: Direct integration with AWS S3 for data processing
- **High Performance**: Built with FastAPI for optimal performance
- **Containerized**: Ready-to-deploy Docker container

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Data Sources  │    │   AWS S3 Bucket │    │  Analytics API  │
│                 │───▶│                 │───▶│                 │
│ Cassandra/MySQL │    │ CSV Files       │    │ FastAPI Service │
│ PostgreSQL      │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## API Endpoints

### 1. Claims Statistics
**GET** `/claims/stats`

- **Description**: Returns statistical analysis of insurance claims grouped by status
- **Data Source**: `cassandra/reclamos/reclamos.csv`
- **Response**: JSON object with claim status counts

**Example Response:**
```json
{
  "aprobado": 150,
  "pendiente": 75,
  "rechazado": 25,
  "en_revision": 50
}
```

### 2. Payment Averages
**GET** `/payments/avg`

- **Description**: Calculates the average payment amount from payment data
- **Data Source**: `cassandra/pagos/pagos.csv`
- **Response**: JSON object with average payment amount

**Example Response:**
```json
{
  "avg_monto": 1250.75
}
```

### 3. Top Audit Services
**GET** `/audits/top-services`

- **Description**: Returns the top 5 most frequently used services from transaction audits
- **Data Source**: `cassandra/transaction_audit/transaction_audit.csv`
- **Response**: JSON object with service names and their usage counts

**Example Response:**
```json
{
  "payment_service": 342,
  "user_authentication": 298,
  "data_backup": 187,
  "notification_service": 156,
  "report_generation": 134
}
```

## Environment Variables

The API requires the following environment variables for AWS S3 integration:

| Variable | Description | Default Value |
|----------|-------------|--------------|
| `AWS_ACCESS_KEY_ID` | AWS Access Key ID | Required |
| `AWS_SECRET_ACCESS_KEY` | AWS Secret Access Key | Required |
| `AWS_SESSION_TOKEN` | AWS Session Token (if using temporary credentials) | Optional |
| `AWS_DEFAULT_REGION` | AWS Region | `us-east-1` |
| `S3_BUCKET` | S3 Bucket name containing the data | `bucket's-name` |

## Installation & Setup

### Prerequisites

- Python 3.11+
- Docker (optional)
- AWS credentials with S3 access
- Access to the S3 bucket containing the CSV data files

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
   export S3_BUCKET="bucket's-name"
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
     -e S3_BUCKET="bucket's-name" \
     API-Analytic-Primac
   ```

### Docker Compose Setup

From the project root directory:

1. **Create a `.env` file with your AWS credentials:**
   ```env
   AWS_ACCESS_KEY_ID=your_access_key
   AWS_SECRET_ACCESS_KEY=your_secret_key
   AWS_DEFAULT_REGION=us-east-1
   S3_BUCKET=bucket's-name
   ```

2. **Start the service:**
   ```bash
   docker-compose up API-Analytic-Primac
   ```

## Usage Examples

### Using curl

```bash
# Get claims statistics
curl http://localhost:8000/claims/stats

# Get payment averages
curl http://localhost:8000/payments/avg

# Get top audit services
curl http://localhost:8000/audits/top-services
```

### Using Python requests

```python
import requests

base_url = "http://localhost:8000"

# Get claims statistics
response = requests.get(f"{base_url}/claims/stats")
print(response.json())

# Get payment averages
response = requests.get(f"{base_url}/payments/avg")
print(response.json())

# Get top audit services
response = requests.get(f"{base_url}/audits/top-services")
print(response.json())
```

## API Documentation

Once the API is running, you can access:

- **Interactive API docs (Swagger UI)**: `http://localhost:8000/docs`
- **Alternative API docs (ReDoc)**: `http://localhost:8000/redoc`
- **OpenAPI schema**: `http://localhost:8000/openapi.json`

## Data Sources & Schema

### Expected S3 Structure

```
s3://bucket's-name/
├── cassandra/
│   ├── reclamos/
│   │   └── reclamos.csv
│   ├── pagos/
│   │   └── pagos.csv
│   └── transaction_audit/
│       └── transaction_audit.csv
```

## Deployment

### Production Considerations

1. **Security**: Use IAM roles instead of hardcoded credentials
2. **Monitoring**: Implement logging and monitoring
3. **Scaling**: Consider using AWS ECS, EKS, or similar container orchestration
4. **Load Balancing**: Use Application Load Balancer for multiple instances

### AWS ECS Deployment Example

```bash
# Build and push to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com
docker build -t API-Analytic-Primac .
docker tag API-Analytic-Primac:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/API-Analytic-Primac:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/API-Analytic-Primac:latest
```

## Dependencies

- **FastAPI 0.100.0**: Modern web framework for building APIs
- **Uvicorn 0.23.2**: ASGI server implementation
- **Boto3 1.26.150**: AWS SDK for Python
- **Pandas 2.1.1**: Data manipulation and analysis library
- **NumPy 1.26.0**: Numerical computing library
- **python-dotenv 1.1.1**: Environment variable management

## Troubleshooting

### Common Issues

1. **AWS Credentials Error**
   - Ensure AWS credentials are properly set
   - Check IAM permissions for S3 access

2. **S3 Access Error**
   - Verify bucket name and region
   - Check if CSV files exist in the expected S3 paths

3. **Data Processing Error**
   - Verify CSV file format and column names
   - Check for empty or corrupted files

### Health Check

Add a health check endpoint by visiting: `http://localhost:8000/docs`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the terms specified in the LICENSE file.

## Support

For support and questions, please contact the development team or create an issue in the project repository.
