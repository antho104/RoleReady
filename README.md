# RoleReady - Interview Question Bank

A full-stack interview preparation platform built with React, Python Lambda functions, and AWS CDK.

## 📋 Table of Contents

- [Architecture](#architecture)
- [CI/CD Pipeline](#cicd-pipeline)
- [Project Structure](#project-structure)
- [Local Development](#local-development)
- [Deployment](#deployment)
- [Documentation](#documentation)

## 🏗️ Architecture

- **Frontend**: React + TypeScript + Vite
- **Backend**: Python Lambda functions
- **Infrastructure**: AWS CDK (TypeScript)
- **Database**: DynamoDB
- **Authentication**: Cognito
- **Hosting**: S3 + CloudFront

## 🚀 CI/CD Pipeline

The project uses GitHub Actions for continuous deployment with parallel pipelines:

- **Frontend Pipeline**: ESLint → TypeScript → Trivy → Alpha → **Manual Gate** → Production
- **Backend Pipeline**: Tests → CDK Check → Trivy → Alpha → Integration Tests → **Manual Gate** → Production

**📊 [View Full Pipeline Diagram](docs/PIPELINE.md)**

### Environments

| Environment | URL |
|-------------|-----|
| **Alpha** | https://alpha.apaps.people.aws.dev |
| **Production** | https://apaps.people.aws.dev |

## 📁 Project Structure

```
RoleReady/
├── frontend/           # React application
├── backend/            # Python Lambda functions
├── infrastructure/     # AWS CDK stacks
├── docs/              # Documentation
│   └── PIPELINE.md    # CI/CD pipeline diagrams
└── .github/workflows/ # GitHub Actions
```

## 💻 Local Development

### Prerequisites

- Node.js 20+
- Python 3.11+
- AWS CLI configured

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Backend

```bash
cd backend
pip install -r requirements.txt
make build  # Run tests, lint, format
```

### Infrastructure

```bash
cd infrastructure
npm install
npm test
npx cdk synth  # Generate CloudFormation
npx cdk deploy # Deploy to AWS
```

## 🚢 Deployment

### Automatic Deployment

Push to `main` branch triggers automatic deployment:

```bash
git push origin main
```

- Changes to `frontend/**` trigger Frontend Pipeline
- Changes to `backend/**` or `infrastructure/**` trigger Backend Pipeline
- Production deployments require manual approval in GitHub

### Manual Deployment

```bash
# Deploy infrastructure
cd infrastructure
npx cdk deploy --profile <aws-profile>

# Deploy frontend
cd frontend
npm run build
aws s3 sync dist/ s3://<bucket-name>
```

## 📚 Documentation

- [CI/CD Pipeline Diagrams](docs/PIPELINE.md) - Detailed pipeline flows and architecture
- [Technical Documentation](TECHNICAL_DOCUMENTATION.md) - System design and API specs

## 🔐 Security

- Trivy vulnerability scanning on every build
- Manual approval gates for production
- Separate AWS accounts for alpha and production
- AWS IAM roles with least privilege
- Integration tests validate alpha before production deployment

## 📝 License

Private project - All rights reserved

---

*Last Updated: 2026-02-19*
