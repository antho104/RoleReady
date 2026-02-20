# EPA Project: Threat Model

## Project background
Interview preparation within organisations is often inconsistent, with questions stored across personal documents, shared drives, or individual knowledge. This leads to duplicated effort, varying interview quality, and increased preparation time for interviewers.

There is also a risk that outdated or unauthorised interview content is used, as there is no central ownership or control over changes. From a business perspective, this impacts efficiency, consistency, and the overall quality of hiring decisions.

This project addresses these challenges by providing a centralised, secure interview question bank that enables authorised users to quickly find, maintain, and manage interview questions in a consistent way, while ensuring that changes can be made safely and reliably as requirements evolve.

---

## Service Overview
The Interview Question Bank is an internal web-based service that provides a single, central location for storing and managing interview questions.

When complete, the service will allow authorised users to browse and search interview questions by category, keyword, and difficulty level, enabling interviewers to quickly prepare for interviews in a consistent and efficient way.

Administrators will be able to create, edit, and remove interview questions, ensuring content remains accurate, relevant, and aligned with current hiring needs. Access to the service will be controlled to protect internal interview content, and changes to the system will be delivered through automated deployment to ensure reliability and minimise risk.

---

## Security Tenets

### 1. Least Privilege
Users, administrators, and services are granted only the permissions required to perform their intended functions.
This reduces the impact of compromised credentials and limits the risk of unauthorised actions.

### 2. Secure by Default
The system is designed so that secure behaviour is the default, not optional.
Unauthenticated access is denied, administrative actions are restricted and sensitive operations require explicit authorisation.

### 3. Defence in Depth
Security controls are applied at multiple layers, including:
* application logic
* authentication and authorisation
* infrastructure and deployment

This ensures that the failure of a single control does not result in a complete system compromise.

### 4. Separation of Responsibilities
Administrative, user, and development responsibilities are clearly separated.
This reduces the risk of privilege escalation and limits the potential impact of insider threats or human error.

### 5. Auditability and Accountability
Key actions, particularly administrative changes, are logged and traceable.
This supports accountability, incident investigation, and non-repudiation.

### 6. Automation and Consistency
Security-related tasks such as deployment, configuration, and validation are automated where possible.
Automation reduces human error and ensures consistent enforcement of security controls across environments.

### 7. Risk-Based Decision Making
Security decisions are made based on risk and business impact, rather than attempting to eliminate all possible threats.
Controls are prioritised where they provide the greatest reduction in risk relative to complexity and cost.

---

## Assumptions

The following assumptions were made to scope the threat model and focus on realistic threats and mitigations relevant to the Interview Question Bank service. If any assumption is invalidated, the threat model will be revisited. These assumptions support a risk-based approach by focusing threat identification on realistic attack paths for an internal, cloud-hosted service. If deployment, access patterns, or data types change (for example, the service becomes public-facing or begins storing personal data), this threat model will be updated accordingly.

| Assumption ID | Assumption | Why this assumption is made | Mitigation/Validation |
|---------------|------------|----------------------------|----------------------|
| A1 | The service is intended for internal organisational use and is not publicly promoted to external users. | Reduces focus on threats specific to large-scale public consumer applications. | Access requires authentication; no anonymous access to API endpoints. |
| A2 | All traffic to the application and API is served over HTTPS. | Prevents interception or modification of data in transit. | Enforce HTTPS on CloudFront and API Gateway; redirect/block HTTP where applicable. |
| A3 | User authentication is provided by Amazon Cognito, and users must be authenticated to use the system. | Centralises identity management and reduces custom auth implementation risk. | API Gateway authorizer validates JWTs; deny requests without valid tokens. |
| A4 | The system uses role-based access control (admin vs end user) and privileged actions are restricted to admins. | Ensures administrative operations have higher controls than read-only use. | Enforce role checks in Lambda for create/edit/delete operations; test negative cases. |
| A5 | The frontend does not directly access the database; all data access goes through API Gateway → Lambda → DynamoDB. | Creates a single controlled path for validation and authorisation. | DynamoDB permissions limited to Lambda IAM roles; no public endpoints to DynamoDB. |
| A6 | AWS services are configured following least privilege and "deny by default" where possible. | Reduces blast radius if a component or credential is compromised. | Review IAM policies; restrict Lambda to required DynamoDB actions only. |
| A7 | Static frontend assets stored in S3 are not intended to be modified manually in production. | Reduces risk of unauthorised changes and inconsistent deployments. | Deploy frontend via CI/CD; restrict S3 write permissions; enable CloudTrail logging. |
| A8 | The system stores interview questions and metadata only and does not intentionally store sensitive personal data beyond what is required for accounts (handled by Cognito). | Keeps privacy risks proportionate to the business need. | Avoid storing candidate data; minimise user profile fields; review data model. |
| A9 | Centralised logging and monitoring are available via CloudWatch, and infrastructure/audit logging via CloudTrail is enabled. | Supports investigation, accountability, and detection of anomalies. | Ensure logs are enabled and retained; restrict access to logs; monitor errors/unauthorised attempts. |
| A10 | Changes are deployed via an automated CI/CD pipeline, rather than manual production updates. | Reduces human error, supports repeatability, and improves traceability of changes. | Protect pipeline access; use version control; require code review (where feasible). |

---

# System Architecture

## High Level Design
The Interview Question Bank is a serverless web application hosted on AWS. Static frontend content is served from an S3 bucket via CloudFront. Users authenticate using Amazon Cognito and then interact with the backend through API Gateway. API Gateway validates authentication tokens and invokes Lambda functions, which implement business logic and read/write interview question data in DynamoDB. Operational monitoring is provided through CloudWatch, and AWS API activity is recorded in CloudTrail for audit purposes.

**Common design patterns:** serverless managed services, static frontend + authenticated API backend, centralised authentication, and a single controlled path to persistent data (API Gateway → Lambda → DynamoDB).

---

## Low Level Design

### Frontend (React on S3 + CloudFront)
* Frontend is deployed as static assets to an S3 bucket and delivered via CloudFront.
* The frontend does not access DynamoDB directly; all data operations occur via the API.
* Auth tokens obtained from Cognito are stored client-side and attached to API requests (e.g., in the `Authorization` header).

### Authentication (Cognito)
* Cognito is used for user authentication and token issuance.
* Authenticated users receive JWT tokens which are required to access protected API endpoints.
* User roles (e.g., admin vs end user) are used to control access to privileged operations.

### API Layer (API Gateway)
* API Gateway is the single entry point for dynamic operations.
* Requests require valid Cognito authentication (JWT validation) before reaching backend compute.
* Endpoints are separated by operation type (read vs write) to support different authorisation requirements (e.g., admin-only write operations).

### Business Logic (Lambda)
* Lambda functions handle request processing, input validation, and authorisation checks.
* Privileged actions (create/edit/delete) require admin role validation.
* Lambda uses least-privilege IAM permissions to interact with DynamoDB.
* Errors are handled in a controlled manner to avoid leaking sensitive information while providing usable feedback.

### Data Store (DynamoDB)
* DynamoDB stores interview questions and associated metadata (category, difficulty, tags).
* Only Lambda functions have permission to read/write the table.
* Data access is scoped to the minimum required actions (e.g., query, get, put, update, delete) based on role and function.

### Logging, Monitoring, and Auditability
* CloudWatch captures Lambda logs and metrics (errors, latency) for operational monitoring.
* CloudTrail captures AWS API activity to support auditing of infrastructure and configuration changes.
* Administrative actions within the application are logged to support accountability (who changed what and when).

---

## Data Flow Diagrams

The data flow diagram illustrates how data moves through the system during normal operation, from initial user access through to backend processing and storage. Interaction with the system occurs in a series of distinct stages rather than as a single continuous process.

First, a user accesses the application through a web browser, where the static frontend is delivered from Amazon S3 via CloudFront. Once the frontend is loaded, the user authenticates using Amazon Cognito, which validates credentials and issues an authentication token.

After authentication, the user performs actions such as browsing, searching, or managing interview questions. These actions trigger API requests from the frontend to API Gateway, with the authentication token included in each request. API Gateway validates the token before forwarding the request to the appropriate AWS Lambda function.

The Lambda function processes the request, performs server-side validation and authorisation checks, and then reads from or writes to DynamoDB as required. The response is returned to the user via API Gateway. Throughout this process, operational logs and metrics are generated and sent to CloudWatch, while infrastructure-level activity is recorded in CloudTrail to support monitoring and auditability.

---

## APIs

| API Endpoint Name | HTTP Method | Auth Required | Description | Key Threats | Security Controls | Logging and Monitoring |
|-------------------|-------------|---------------|-------------|-------------|-------------------|------------------------|
| / | OPTIONS | None (Recommended) | CORS pre-flight for root | Over-permissive CORS, reflective origins | Allowlist origins, restrict headers/methods, avoid `*` with credentials | Basic API Gateway access logs |
| /answers | OPTIONS | None | CORS pre-flight for /answers | CORS misconfig; browser failures if auth required | Same as above; ensure preflight succeeds without JWT | Low value logs; monitor CORS error rates |
| /answers | POST | Cognito Authoriser | Submit answers | Broken access control (submit as another user), injection, oversized payloads, replay/spam | Validate JWT, enforce user ownership (sub/claims), schema validation, size limits, rate limiting/WAF, idempotency key if needed | Log user id, request id; alarms on 4XX/5XX spikes |
| /questions | GET | Cognito Authoriser | List questions | Unauthorised access, scraping, enumeration, excessive data exposure | RBAC/claims checks, pagination, filtering, rate limiting, return minimum fields | Monitor high request volume; 401/403 spikes |
| /questions | OPTIONS | Cognito Authoriser | CORS pre-flight for /questions | CORS misconfig; auth-required OPTIONS breaking browsers | Allowlist origins; ensure OPTIONS does not require auth | Low value; track CORS failures |
| /questions | POST | Cognito Authoriser | Create question | Privilege escalation (non-admin creates), injection, malicious content | Require admin/role claim, input validation & allowlists, content moderation if needed | Log creator (sub), new resource ID |
| /questions/{id} | DELETE | Cognito Authoriser | Delete question by ID | Accidental/malicious deletion | Ownership/admin check, soft delete (recommended), least-privilege IAM, confirmation workflow if applicable | Audit log delete events; alert on unusual deletes |
| /questions/{id} | GET | Cognito Authoriser | Get question by ID | Enumeration (guessing IDs), data leakage | AuthZ check for visibility, use non-sequential IDs if sensitive, return minimal fields | Monitor repeated 404/403 patterns |
| /questions/{id} | OPTIONS | None | Update question by ID | CORS misconfig; auth-required OPTIONS breaking browsers | Same restrictive CORS config | Low value; track CORS failures |
| /questions/{id} | PUT | Cognito Authoriser | Update question by ID | Mass assignment, injection | Ownership/admin check, whitelist updatable fields, schema validation, optimistic locking/versioning if needed | Log updater (sub), changed fields metadata |
| /testing | GET | Cognito Authoriser | Test/health endpoint | Info leakage (stack traces, env/config), abuse if left open | Return minimal "OK", no internal details, restrict to admin or remove in prod | Monitor frequency; alert if hit heavily |
| /testing | OPTIONS | None | CORS test | CORS misconfig; auth-required OPTIONS breaking browsers | Same restrictive CORS config | Low value; track CORS failures |

---

## Assets

| Asset ID | Asset Name | Description | Why is this asset important? |
|----------|------------|-------------|------------------------------|
| A1 | Interview Question Data | Interview questions and associated metadata stored in DynamoDB. | Core business data required to prepare consistent and effective interviews. |
| A2 | User Accounts | User identities managed by Amazon Cognito. | Controls access to the system and protects internal content. |
| A3 | Authentication Tokens | JWT tokens issued by Cognito and used to access APIs. | Used to authenticate users and authorise API requests. |
| A4 | API Endpoints | Backend API endpoints exposed via API Gateway. | Provide controlled access to interview question data and admin functionality. |
| A5 | Application Frontend | Static frontend assets hosted in S3 and delivered via CloudFront. | Provides the user interface for accessing the service. |
| A6 | Business Logic | Lambda functions implementing application behaviour. | Enforces validation, authorisation, and business rules. |
| A7 | Audit and Application Logs | Logs generated by CloudWatch and CloudTrail. | Support monitoring, investigation, and accountability. |
| A8 | Cloud Infrastructure Configuration | AWS configuration including IAM roles and service settings. | Misconfiguration could lead to data exposure or service compromise. |

---

## Threat Actors

The following threat actors have been considered when identifying risks to the system. These actors represent different levels of access and trust and help ensure threats are assessed from multiple perspectives.

### 1. External Unauthenticated User (Internet-Based)
* An external threat actor with no legitimate access to the system, operating from the public internet.
This actor may attempt to:
  * Access the application without authentication
  * Exploit exposed endpoints or misconfigurations
  * Disrupt service availability through excessive or malformed requests
* This actor represents a low-trust, high-exposure threat.

### 2. Authenticated End User (Non-Admin)
A legitimate user of the system with standard (non-admin) permissions.
This actor may intentionally or unintentionally:
* Attempt to access administrative functionality
* Submit malformed or unexpected input
* Misuse legitimate features beyond their intended scope

This actor highlights the risk of privilege escalation and insufficient access control.

### 3. Administrator User
A legitimate administrator with permissions to manage interview questions.
This actor may:
* Accidentally modify or delete data
* Perform unauthorised changes if credentials are compromised
* Deny responsibility for changes if actions are not logged

This actor emphasises the need for audit logging, change tracking, and role separation.

### 4. Cloud Account User (AWS Account Access)
A threat actor with access to the AWS account hosting the service, either through misconfiguration, compromised credentials, or excessive permissions.
This actor may:
* Access infrastructure resources directly
* Modify deployment or configuration settings
* View or manipulate stored data outside the application

This actor represents a high-impact infrastructure-level threat.

### 5. Development or CI/CD Pipeline User
A threat actor with access to the source code repository or CI/CD pipeline.
This actor may:
* Introduce insecure or malicious code
* Modify pipeline configuration
* Bypass security controls during deployment

This actor highlights supply chain risk and the importance of secure DevOps practices.

---

# Threats

| Threat ID | Priority | Threat Description | STRIDE | Affected Assets | Mitigations |
|-----------|----------|-------------------|--------|-----------------|-------------|
| T1 | High | An unauthenticated external user attempts to access protected API endpoints to retrieve interview questions. | Spoofing | API Endpoints, Interview Question Data | Authentication is enforced using Amazon Cognito, with API Gateway validating JWT tokens before invoking Lambda functions. |
| T2 | High | A non-admin authenticated user attempts to create, edit, or delete interview questions. | Elevation of Privilege | API Endpoints, Interview Question Data | Role-based access control is enforced within Lambda functions to ensure only admin users can perform write operations. |
| T3 | High | Interview question data is modified or deleted without authorisation. | Tampering | Interview Question Data, DynamoDB | DynamoDB access is restricted to Lambda functions using least-privilege IAM roles, and all write operations are authenticated and authorised. |
| T4 | Medium | An administrator denies responsibility for modifying or deleting interview questions. | Repudiation | Audit Logs, Interview Question Data | Administrative actions are logged with user identity and timestamps using CloudWatch logging. |
| T5 | High | Sensitive interview questions are exposed to unauthorised users due to missing or incorrect access controls. | Information Disclosure | Interview Question Data | Access to interview questions is restricted to authenticated users, and the database is not directly accessible from the frontend. |
| T6 | Medium | Excessive or malicious API requests degrade system availability. | Denial of Service | API Gateway, Lambda | API Gateway throttling and request limits are configured to reduce the impact of excessive requests. |
| T7 | Medium | Malicious or malformed input causes application errors or data corruption. | Tampering | Lambda Functions, DynamoDB | Server-side input validation is performed within Lambda functions before processing or storing data. |
| T8 | High | Compromised authentication tokens are reused to impersonate a legitimate user. | Spoofing | Access Tokens (JWTs), API Endpoints | Short-lived JWT tokens issued by Cognito are validated on every request at the API Gateway layer. |
| T9 | Medium | Malicious or insecure code is introduced via the CI/CD pipeline. | Tampering | Source Code, CI/CD Pipeline | Code changes are deployed through an automated CI/CD pipeline with controlled access and version control. |
| T10 | Medium | Infrastructure or configuration changes occur without traceability or detection. | Repudiation | Cloud Infrastructure, Audit Logs | AWS CloudTrail is enabled to capture account-level API activity for audit and investigation purposes. |

---

# Mitigations

### Security Control Mitigations

| Threat ID | Threat Description | Affected Asset | Mitigation | Status |
|-----------|-------------------|----------------|------------|--------|
| T1 | Unauthenticated users attempt to access protected API endpoints | API Gateway, Interview Question Data | Authentication is enforced using Amazon Cognito, with API Gateway validating JWT tokens before invoking backend Lambda functions. | Implemented |
| T2 | A non-admin user attempts to create, edit, or delete interview questions | API Endpoints, Interview Question Data | Role-based access control is enforced within Lambda functions to ensure only users with admin privileges can perform write operations. | Implemented |
| T3 | Compromised or reused authentication tokens are used to impersonate a legitimate user | Access Tokens (JWTs), API Gateway | Short-lived JWT tokens issued by Cognito are required for all API requests, and tokens are validated on every request at the API Gateway layer. | Implemented |
| T4 | Interview question data is modified without authorisation | DynamoDB, Interview Question Data | DynamoDB access is restricted to Lambda functions only, using least-privilege IAM roles to prevent direct or unauthorised data modification. | Implemented |
| T5 | Malicious or malformed input causes unexpected behaviour or data corruption | Lambda Functions, DynamoDB | Server-side input validation is performed within Lambda functions before processing requests or writing data to DynamoDB. | Implemented |
| T6 | An administrator denies having modified or deleted interview questions | Application Logs, Audit Logs | Administrative actions are logged with user identity and timestamps using CloudWatch logging to support auditability and non-repudiation. | Implemented |
| T7 | Sensitive interview questions are exposed to unauthorised users | Interview Question Data, API Endpoints | Interview question data is only accessible via authenticated API endpoints, and the database is not directly accessible from the frontend. | Implemented |
| T8 | Excessive or abusive API requests degrade service availability | API Gateway, Lambda | API Gateway request throttling and rate limits are configured to reduce the impact of excessive or malformed requests. | Implemented |
| T9 | Malicious or insecure code is introduced through the deployment pipeline | Source Code, CI/CD Pipeline | Changes are deployed through an automated CI/CD pipeline, with version control and controlled access to reduce the risk of unauthorised changes. | Implemented |
| T10 | Infrastructure or configuration changes occur without traceability | AWS Infrastructure, Cloud Resources | AWS CloudTrail is enabled to capture account-level API activity, providing an audit trail for infrastructure and configuration changes. | Implemented |

---

## Security Tests

The following security tests were performed to validate that the mitigations identified in the threat model are implemented correctly and operate as expected. Testing focuses on authentication, authorisation, input validation, logging, and deployment controls, and is integrated with automated deployment where possible. These tests help ensure that security controls remain effective as changes are introduced to the system.

| Test Number | Mitigations Tested | Test Case | Expected Outcome | Test Type | Status |
|-------------|-------------------|-----------|------------------|-----------|--------|
| ST1 | Cognito authentication enforced at API Gateway | Attempt to access protected API endpoints without a valid JWT token | Request is denied with an unauthorised response | Manual | Passed |
| ST2 | Role-based access control (RBAC) for admin operations | Authenticate as a non-admin user and attempt to create a new interview question | Request is rejected and no data is written to DynamoDB | Manual | Passed |
| ST3 | RBAC for privileged delete operations | Authenticate as a non-admin user and attempt to delete an interview question | Request is denied and question remains unchanged | Manual | Passed |
| ST4 | Admin authorisation for write operations | Authenticate as an admin user and create a new interview question | Question is successfully created and persisted | Manual | Passed |
| ST5 | Server-side input validation | Submit malformed or unexpected input to question creation endpoint | Input is rejected and no invalid data is stored | Manual | Passed |
| ST6 | Least-privilege IAM permissions | Attempt direct access to DynamoDB from outside Lambda execution context | Access is denied due to IAM restrictions | Manual/Review | Passed |
| ST7 | Audit logging of administrative actions | Perform admin edit or delete operation and review logs | CloudWatch logs record action with user identity and timestamp | Manual | Passed |
| ST8 | Infrastructure audit logging | Modify infrastructure configuration and review CloudTrail logs | CloudTrail records AWS API activity | Manual/Review | Passed |
| ST9 | CI/CD deployment controls | Deploy a change via the CI/CD pipeline | Change is deployed successfully through automated pipeline | Automated | Passed |
| ST10 | Service availability post-deployment | Access the application after deployment | Application remains available and functional | Manual | Passed |

---

## Appendix

### Glossary

| # | Term | Definition | Example |
|---|------|------------|---------|
| 1 | Asset | Something of value that must be protected from unauthorised access, modification, or loss. | Interview questions stored in DynamoDB are a core asset of the system. |
| 2 | Threat | A potential event or action that could exploit a vulnerability and cause harm to an asset. | A non-admin user attempting to delete interview questions. |
| 3 | Threat Actor | An individual or entity that may attempt to compromise the system, intentionally or unintentionally. | An unauthenticated internet user attempting to access protected API endpoints. |
| 4 | Vulnerability | A weakness in a system that could be exploited by a threat actor. | Missing role checks on an admin-only API endpoint. |
| 5 | Mitigation | A control or measure put in place to reduce the likelihood or impact of a threat. | Role-based access control enforced via Cognito and API Gateway. |
| 6 | Data Flow Diagram | A diagram that shows how data moves through a system, including processes, data stores, and external entities. | A diagram showing data flowing from the user's browser through API Gateway and Lambda to DynamoDB. |
| 7 | STRIDE | A threat modelling framework used to categorise threats. | Elevation of Privilege threats were identified for admin-only API operations. |
| 8 | Least Privilege | A security principle where users and services are granted only the minimum permissions required. | Lambda functions are granted read/write access only to the required DynamoDB table. |
| 9 | Role-Based Access Control (RBAC) | A method of restricting system access based on assigned roles. | Admin users can create, edit, or delete questions, while end users can only view them. |
| 10 | Serverless Architecture | A cloud architecture where infrastructure management is handled by the cloud provider. | AWS Lambda is used instead of managing application servers. |
| 11 | CI/CD Pipeline | An automated process that builds, tests, and deploys changes to a system. | A code change pushed to the repository automatically triggers deployment to AWS. |
| 12 | Audit Logging | The recording of actions to support accountability and investigation. | CloudTrail logs record changes made to AWS resources. |
| 13 | Denial of Service | An attempt to make a system unavailable to legitimate users. | Excessive API requests overwhelming API Gateway. |
| 14 | Authentication | The process of verifying the identity of a user. | Users authenticate via Amazon Cognito before accessing the API. |
| 15 | Authorisation | The process of determining what actions an authenticated user is allowed to perform. | API endpoints restrict delete operations to admin users only. |

---

**Document Version**: 1.0
**Last Updated**: February 2026
