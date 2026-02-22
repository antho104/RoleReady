# RoleReady - Interview Question Bank

A full-stack interview preparation platform with AI-powered feedback, built with React, Python Lambda functions, and AWS CDK.

## 📋 Table of Contents

- [Features](#-features)
- [Architecture](#️-architecture)
- [CI/CD Pipeline](#-cicd-pipeline)
- [Project Structure](#-project-structure)
- [Local Development](#-local-development)
- [Deployment](#-deployment)
- [Documentation](#-documentation)
- [Security](#-security)

## ✨ Features

- 🔐 **Secure Authentication** - AWS Cognito user management
- 📚 **Question Bank** - Searchable interview questions by category and difficulty
- 👨‍💼 **Admin Dashboard** - Role-based access control with Cognito groups for question management
- 🤖 **AI Interview Coach (Marcus)** - AWS Bedrock (Claude 3.7 Sonnet) powered answer evaluation
- 🎯 **Practice Mode** - Submit answers and receive instant AI feedback with scores (0-100)
- 💪 **Personalized Feedback** - Strengths, improvements, and actionable suggestions
- 🌐 **Multi-Environment** - Separate Alpha and Production deployments
- 📱 **Responsive Design** - Works on desktop, tablet, and mobile
- 🔄 **Automated Security Updates** - Dependabot monitors dependencies weekly

## 🏗️ Architecture

- **Frontend**: React 19 + TypeScript + Vite
- **Backend**: Python 3.14 Lambda functions
- **Infrastructure**: AWS CDK (TypeScript)
- **Database**: DynamoDB
- **AI**: AWS Bedrock (Claude 3.7 Sonnet)
- **Authentication**: AWS Cognito
- **Authorization**: Cognito Groups (Admin role-based access)
- **Hosting**: S3 + CloudFront CDN
- **Monitoring**: CloudWatch + CloudTrail

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
│   ├── src/           # Lambda handlers
│   │   ├── questions_handler.py   # CRUD operations
│   │   │   └── POST/PUT/DELETE (Admin only)
│   │   ├── evaluate_answer.py     # AI evaluation (Marcus)
│   │   └── admin_create_user.py   # Admin management
│   └── tests/         # Unit tests
│       └── test_admin_authorization.py  # Admin access tests
├── infrastructure/     # AWS CDK stacks
│   └── lib/           # CDK stack definitions
├── docs/              # Documentation
│   ├── PIPELINE.md        # CI/CD pipeline diagrams
│   ├── USER_STORIES.md    # User stories and requirements
│   └── THREAT_MODEL.md    # Security threat model
└── .github/workflows/ # GitHub Actions
```

### Admin Features

Users in the **Admin** Cognito group can access `/admin` to:
- ✏️ Create new interview questions
- 📝 Edit existing questions
- 🗑️ Delete questions

Admin endpoints (require `cognito:groups` claim containing "Admin"):
- `POST /questions` - Create question
- `PUT /questions/{id}` - Update question
- `DELETE /questions/{id}` - Delete question
- `GET /questions` - Available to all authenticated users

## 💻 Local Development

### Prerequisites

- Node.js 20+
- Python 3.14+
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

### Project Documentation
- **[User Stories](docs/USER_STORIES.md)** - Feature requirements and acceptance criteria
- **[Threat Model](docs/THREAT_MODEL.md)** - Security analysis and mitigations
- **[CI/CD Pipeline](docs/PIPELINE.md)** - Deployment workflows and diagrams

### Technical Resources
- **API Endpoints**: Documented in Lambda function docstrings
- **Infrastructure**: See CDK stack definitions in `infrastructure/lib/`
- **Frontend Components**: React components in `frontend/src/`

## 🔐 Security

- **Trivy vulnerability scanning** on every build
- **Dependabot security updates** check dependencies weekly
- **Manual approval gates** for production deployments
- **Separate environments** with isolated AWS resources
- **AWS IAM roles** with least privilege principle
- **Role-based access control** via Cognito groups for admin operations
- **Integration tests** validate alpha before production
- **HTTPS enforced** for all traffic
- **JWT token validation** on every API request
- **Group-based authorization** for destructive operations (POST/PUT/DELETE)
- **CloudTrail logging** for audit trail

## 📝 License

Private project - All rights reserved

---

**Last Updated:** 2026-02-22
**Version:** 2.1
**Author:** Antho103
