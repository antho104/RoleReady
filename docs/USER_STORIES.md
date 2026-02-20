# EPA Project User Stories
**RoleReady - Interview Question Bank**

**Version:** 2.1
**Last Updated:** February 20, 2026
**Project:** Independent Assessment Submission

---

## Table of Contents
1. [End Users](#end-users)
2. [Developers](#developers)
3. [Admin Users](#admin-users)
4. [Platform Administrators](#platform-administrators)

---

## End Users
### _"As an end user..."_

#### Story 1: Create Account and Access Questions
**I want to** create an account and log in **so that** I can access the interview question bank and prepare for my interviews.

**Acceptance Criteria:**
- I can sign up using my email address
- I receive a temporary password via email that I must change on first login
- I can log in with my email and password
- I can change my password from my account settings if needed
- I cannot access questions without logging in (shown a login prompt)
- My session stays logged in until I log out or it expires

---

#### Story 2: Find Relevant Questions
**I want to** search and filter interview questions by category and difficulty **so that** I can practice topics relevant to my target role and skill level.

**Acceptance Criteria:**
- Questions display in browsable cards with text, category, and difficulty
- Search box filters questions by keyword (question text, category, competency)
- Filter dropdown for category (AWS, System Design, Security, etc.)
- Filter dropdown for difficulty (Easy, Medium, Hard)
- Multiple filters work together (AND logic)
- Results count shows "X of Y questions"
- Filters work in real-time without page reload

---

#### Story 3: Practice with AI Feedback
**I want to** submit my answers and receive instant AI-powered evaluation **so that** I can understand my strengths, improve weaknesses, and build confidence.

**Acceptance Criteria:**
- User can type/paste answer in multi-line text area
- "Get AI Feedback" button submits answer to Marcus (AWS Bedrock)
- Loading state shows "Marcus is evaluating..." while processing
- Evaluation returns within 10 seconds
- Feedback displays: score (0-100), correctness indicator, strengths list, improvements list, suggestions list, personal comment
- User can click "Try Again" to clear and resubmit a new answer
- Optional reference answer available (expandable, hidden by default)

---


## Developers
### _"As a developer..."_

#### Story 1: Secure Backend API
**I want to** implement secure authentication and authorization with AWS Cognito **so that** only authorized users can access protected resources and data.

**Acceptance Criteria:**
- Cognito user pool configured with password policies
- API Gateway validates JWT tokens on all requests
- Unauthenticated requests return 401
- Lambda functions use least-privilege IAM roles
- All traffic enforced over HTTPS
- Server-side input validation on all endpoints
- CORS configured properly for frontend domain

---

#### Story 2: AI-Powered Answer Evaluation
**I want to** integrate AWS Bedrock for answer evaluation **so that** candidates receive instant, intelligent feedback on their interview answers.

**Acceptance Criteria:**
- Lambda function invokes Bedrock Claude 3.7 Sonnet model
- Evaluation prompt tailored to competency type (LP, System Design, Technical)
- AI response parsed and validated as JSON
- Response includes: score, correctness, strengths, improvements, suggestions, comment
- Evaluation completes in <10 seconds
- Graceful error handling if AI service unavailable
- Evaluation metrics logged (latency, errors)

---

#### Story 3: Scalable Data Layer
**I want to** use DynamoDB for question storage **so that** the system scales efficiently and handles large question sets reliably.

**Acceptance Criteria:**
- Questions stored in DynamoDB with on-demand capacity
- Lambda functions retrieve questions via Scan operation
- Pagination handled for large datasets
- DynamoDB types converted properly (sets → arrays)
- GET /questions returns all questions
- GET /questions/{id} returns single question
- Structured JSON logging for all database operations

---

#### Story 4: Infrastructure as Code
**I want to** define infrastructure using AWS CDK **so that** environments are reproducible, version-controlled, and deployable via CI/CD.

**Acceptance Criteria:**
- All AWS resources defined in TypeScript CDK code
- Separate stacks for Alpha and Production environments
- GitHub Actions deploys infrastructure automatically
- Trivy scans CDK dependencies for vulnerabilities
- Production deployments require manual approval
- CloudWatch alarms configured for Lambda errors and API 5xx errors
- Structured logging to CloudWatch with request IDs

---

## Admin Users
### _"As an admin..."_

**Note:** Admin functionality is currently implemented at the API level only. No admin UI exists yet.

#### Story 1: Manage Question Bank
**I want to** manage interview questions with proper authorization **so that** the question bank remains high-quality and only authorized users can make changes.

**Acceptance Criteria:**
- Admin users assigned to Cognito "Admin" group
- Non-admin users receive 403 Forbidden for admin operations
- Questions can be added/edited via API (no UI yet)
- Admin actions logged to CloudWatch with user identity and timestamp
- Role checks enforced in Lambda before DynamoDB writes

---

#### Story 2: Delegate Admin Responsibilities
**I want to** assign users to admin groups **so that** question management responsibilities can be shared across the team.

**Acceptance Criteria:**
- Script exists to add users to Cognito Admin group (`admin_create_user.py`)
- Group membership reflected in JWT claims
- Admin permissions take effect immediately after group assignment

---

## Platform Administrators
### _"As a platform administrator..."_

#### Story 1: Multi-Environment Infrastructure
**I want to** manage separate Alpha and Production environments **so that** changes can be tested safely before reaching end users.

**Acceptance Criteria:**
- Separate Cognito user pools for Alpha and Production
- Separate DynamoDB tables per environment
- Separate API Gateway instances per environment
- Custom domains: alpha.apaps.people.aws.dev and apaps.people.aws.dev
- CloudFront distributions per environment
- S3 buckets per environment
- Changes to Alpha do not affect Production (full isolation)

---

#### Story 2: Automated CI/CD Pipeline
**I want to** automate deployments with quality gates **so that** releases are consistent, tested, and secure before reaching production.

**Acceptance Criteria:**
- GitHub Actions triggers on push to main branch
- Parallel pipelines for frontend and backend
- Frontend pipeline: ESLint → TypeScript check → Trivy scan → Alpha → Manual approval → Production
- Backend pipeline: Unit tests → CDK check → Trivy scan → Alpha → Integration tests → Manual approval → Production
- Security scans fail build if high/critical vulnerabilities found
- Manual approval required before production deployment
- Deployment failures roll back automatically (or prevent promotion)

---

#### Story 3: Monitoring and Observability
**I want to** monitor system health with alarms and centralized logging **so that** I can detect and resolve issues quickly.

**Acceptance Criteria:**
- CloudWatch Logs capture all Lambda function output
- Structured JSON logging with request IDs
- CloudWatch alarms configured for:
  - Lambda errors (> threshold)
  - Lambda throttles
  - Lambda duration (high latency)
  - API Gateway 5xx errors
- Alarms send notifications via SNS (email)
- CloudTrail enabled for AWS API audit trail
- Logs retained for minimum 30 days

---

#### Story 4: Security and Cost Management
**I want to** enforce security best practices and optimize costs **so that** the application is secure and cost-efficient.

**Acceptance Criteria:**
- IAM roles follow least-privilege principle
- HTTPS enforced on CloudFront (HTTP redirects)
- DynamoDB encryption at rest enabled
- S3 bucket encryption enabled
- Serverless architecture (Lambda, DynamoDB on-demand) scales with usage
- CloudFront caching reduces origin requests
- Cost Explorer available for manual cost review

---

## Appendix

### User Personas Summary
1. **End User (Candidate):** Prepares for interviews by practicing questions and receiving AI feedback.
2. **Developer:** Builds and maintains the application, ensuring security, reliability, and code quality.
3. **Admin User:** Manages interview questions, ensuring content is accurate and up-to-date.
4. **Platform Administrator:** Manages infrastructure, deployments, monitoring, and security.

**Document Version:** 2.1
**Last Updated:** February 20, 2026
**Updated By:** Antho103

