# AWS Serverless Starter

Production-ready AWS serverless application template with Lambda, API Gateway, DynamoDB, and CI/CD.

## Architecture

```
Client → API Gateway → Lambda → DynamoDB
                ↓
            CloudWatch Logs
```

## Features

- **Lambda Functions** — Python 3.12, modular handler structure
- **API Gateway** — HTTP API with CORS, request validation
- **DynamoDB** — Single-table design with GSIs
- **CI/CD** — GitHub Actions pipeline with staging/production
- **Monitoring** — CloudWatch alarms, structured logging
- **IaC** — SAM template for infrastructure as code

## Project Structure

```
├── functions/
│   ├── create_item/
│   │   └── handler.py
│   ├── get_item/
│   │   └── handler.py
│   ├── list_items/
│   │   └── handler.py
│   └── shared/
│       ├── models.py
│       ├── responses.py
│       └── utils.py
├── tests/
│   ├── test_create_item.py
│   ├── test_get_item.py
│   └── conftest.py
├── infrastructure/
│   └── template.yaml
├── .github/
│   └── workflows/
│       └── deploy.yml
├── Makefile
└── README.md
```

## Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
make test

# Deploy to AWS
make deploy

# Deploy to production
make deploy-prod
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | /items | Create a new item |
| GET | /items/{id} | Get item by ID |
| GET | /items | List all items |
| PUT | /items/{id} | Update item |
| DELETE | /items/{id} | Delete item |

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `TABLE_NAME` | DynamoDB table name | Yes |
| `AWS_REGION` | AWS region | Yes |
| `STAGE` | Deployment stage (dev/prod) | Yes |

## License

MIT
