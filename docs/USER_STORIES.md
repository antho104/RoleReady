# EPA Project User Stories
**RoleReady - Interview Question Bank**

**Version:** 2.0
**Last Updated:** February 2026
**Project:** Independent Assessment Submission

---

## Table of Contents
1. [End Users](#end-users)
2. [AI Interview Coach (Marcus)](#ai-interview-coach-marcus)
3. [Developers](#developers)
4. [Admin Users](#admin-users)
5. [Platform Administrators](#platform-administrators)

---

## End Users
### _"As an end user..."_

#### Authentication & Access
* I want to **securely create an account** with email and password so that I can access the interview question bank while protecting internal content.
* I want to **log in with my credentials** so that I can access my personalized experience and practice history.
* I want to **change my password** from my account settings so that I can maintain account security.
* I want to **securely access the interview question bank** so that internal interview content is protected from unauthorized access.

#### Question Discovery
* I want to **browse interview questions by category** so that I can quickly find questions relevant to a specific role or skill (e.g., AWS Fundamentals, System Design, Security).
* I want to **search for interview questions using keywords** so that I can efficiently locate specific questions by text, category, or competency.
* I want to **filter questions by difficulty level** (Easy, Medium, Hard) so that I can tailor my practice to my skill level and interview preparation needs.
* I want to **view interview questions in a clear and consistent format** so that they are easy to read and understand.
* I want to **see the number of filtered results** so that I understand how many questions match my search criteria.

#### Practice Mode & AI Feedback
* I want to **practice answering interview questions** in a safe environment so that I can prepare without pressure before real interviews.
* I want to **submit my answers for AI evaluation** so that I can receive instant, objective feedback on my performance.
* I want to **receive a numerical score (0-100)** for my answer so that I can quantify my understanding.
* I want to **see what I did well** (strengths) so that I can build confidence in my knowledge areas.
* I want to **understand what needs improvement** so that I can focus my study efforts effectively.
* I want to **receive actionable suggestions** for improvement so that I know how to get better.
* I want to **get encouraging feedback from Marcus** (AI Coach) so that I stay motivated during preparation.
* I want to **retry answering the same question** after receiving feedback so that I can improve my response based on suggestions.
* I want to **optionally view reference answers** after attempting a question so that I can compare my approach with recommended solutions.

#### User Experience
* I want the **application to work on desktop, tablet, and mobile** so that I can practice anywhere, anytime.
* I want to **see loading indicators** when content is being fetched so that I know the system is working.
* I want to **see helpful error messages** when something goes wrong so that I understand what happened and can take appropriate action.
* I want a **responsive and fast interface** so that I can focus on learning rather than waiting for pages to load.

---

## AI Interview Coach (Marcus)
### _"As Marcus, the AI Interview Coach..."_

#### Answer Evaluation
* I want to **receive the candidate's answer along with the question context** so that I can provide relevant, accurate feedback.
* I want to **evaluate answers for technical accuracy** so that candidates receive correct guidance.
* I want to **identify specific strengths** in candidate answers so that they understand what they're doing well.
* I want to **identify areas for improvement** so that candidates know what to study next.
* I want to **provide actionable suggestions** so that candidates have concrete next steps.
* I want to **deliver encouraging, constructive feedback** so that candidates stay motivated and engaged.
* I want to **score answers on a 0-100 scale** so that candidates can track their progress over time.
* I want to **respond with structured JSON** so that the frontend can display feedback in a clear, organized format.

#### Feedback Quality
* I want to **tailor feedback to the competency type** (Leadership Principles, System Design, Technical Depth) so that evaluation is contextually appropriate.
* I want to **be specific rather than generic** in my feedback so that candidates can take meaningful action.
* I want to **balance positive reinforcement with improvement areas** so that feedback is constructive and encouraging.

---

## Developers
### _"As a developer..."_

#### Security & Authentication
* I want to **implement AWS Cognito authentication** so that user identities are managed securely and reliably.
* I want to **validate JWT tokens on every API request** so that unauthorized users cannot access protected resources.
* I want to **enforce HTTPS for all traffic** so that data in transit is encrypted and secure.
* I want to **implement role-based access control (RBAC)** so that users can only perform actions permitted by their role.
* I want to **validate all user input on the server side** so that invalid or malicious data cannot be stored in the system.

#### API & Backend
* I want to **structure Lambda functions modularly** so that code is maintainable and testable.
* I want to **handle errors gracefully** so that the system remains stable and provides meaningful feedback to users.
* I want to **implement proper CORS configuration** so that the frontend can communicate with the API securely.
* I want to **use least-privilege IAM roles** so that each Lambda function has only the permissions it needs.
* I want to **integrate with AWS Bedrock** so that I can leverage advanced AI models for answer evaluation.
* I want to **parse and validate AI responses** so that evaluation feedback is always in the expected format.

#### Data Management
* I want to **use DynamoDB for question storage** so that data scales efficiently and is highly available.
* I want to **handle DynamoDB pagination** so that large question sets are retrieved efficiently.
* I want to **convert DynamoDB types properly** (e.g., sets to arrays) so that frontend receives clean JSON data.

#### Observability & Monitoring
* I want to **log key system actions** (such as question retrieval, answer evaluation) so that issues can be investigated and audited if necessary.
* I want to **use structured JSON logging** so that logs are easily searchable and parsable in CloudWatch.
* I want to **include request IDs in logs** so that I can trace requests across distributed components.
* I want to **log errors with context** (error type, stack trace, request details) so that debugging is efficient.
* I want to **monitor Lambda metrics** (duration, errors, throttles) so that I can identify performance issues.

#### Deployment & Infrastructure
* I want to **define infrastructure as code** (AWS CDK) so that environments are consistent and reproducible.
* I want to **support multiple environments** (Alpha, Production) so that changes can be tested before reaching users.
* I want to **automate deployments via CI/CD** (GitHub Actions) so that releases are reliable and repeatable.
* I want to **run security scans** (Trivy) in the pipeline so that vulnerabilities are caught before deployment.
* I want to **require manual approval for production deployments** so that changes are reviewed before going live.

#### Code Quality
* I want to **write unit tests for Lambda functions** so that I can catch bugs early and refactor safely.
* I want to **use linting and formatting tools** (ESLint, Black, Flake8) so that code follows consistent standards.
* I want to **structure the application modularly** so that it can be maintained and extended in the future.
* I want to **document code and APIs** so that other developers can understand and contribute to the system.

### _Acceptance Criteria_
* **Authentication:**
  * If a user is not authenticated, when they try to access the question bank, then they receive a 401 Unauthorized response.
  * If a JWT token is invalid or expired, when they make an API request, then they are denied access.
* **Authorization:**
  * If a user is authenticated but not an admin, when they try to create/edit/delete a question, then the action is denied with a 403 Forbidden response.
  * If a user is an admin, when they create/edit/delete a question, then the action succeeds and is logged.
* **AI Evaluation:**
  * If a user submits an answer, when Marcus evaluates it, then they receive a structured response within 10 seconds.
  * If the AI response is malformed, when parsing fails, then a graceful error is returned to the user.
* **Error Handling:**
  * If an API request fails, when an error occurs, then the user sees a helpful message (not a stack trace).
  * If DynamoDB is unavailable, when questions are requested, then the system returns a 503 Service Unavailable with retry guidance.

---

## Admin Users
### _"As an admin..."_

#### Question Management
* I want to **add new interview questions to the system** so that the question bank can be expanded as requirements change.
* I want to **include question metadata** (category, difficulty, competency, reference answer) so that questions are well-organized and searchable.
* I want to **edit existing interview questions** so that content can be corrected or improved over time.
* I want to **delete interview questions when they are no longer relevant** so that the question bank remains accurate and up-to-date.
* I want to **categorize questions by competency** (Leadership Principles, System Design, Technical Depth) so that questions align with evaluation frameworks.

#### Access Control
* I want to **control who can create, edit, or delete questions** so that only authorized users can modify interview content.
* I want to **assign users to admin groups** so that question management responsibilities can be delegated.
* I want to **ensure admin actions are authenticated and authorized** so that unauthorized modifications are prevented.

#### Audit & Accountability
* I want to **review changes made to interview questions** so that unauthorized or incorrect modifications can be identified.
* I want to **see an audit trail** (what changed, who changed it, when) so that I can track question evolution and accountability.
* I want to **have changes logged in CloudWatch** so that audit records are centralized and searchable.

### _Acceptance Criteria_
* **Question Creation:**
  * If I am an admin, when I create a question, then it is immediately available to end users.
  * If I am not an admin, when I try to create a question, then I receive a 403 Forbidden error.
* **Question Editing:**
  * If I edit a question, when I save changes, then the updated version is reflected immediately.
  * If I edit a question, when I save changes, then the action is logged with my user ID and timestamp.
* **Question Deletion:**
  * If I delete a question, when I confirm the action, then it is removed from the question bank.
  * If I delete a question, when the deletion completes, then the action is logged in CloudWatch.
* **Audit Trail:**
  * If a question has been created/edited/deleted, when I view the change history, then I can see what changed, who changed it, and when.

---

## Platform Administrators
### _"As a platform administrator..."_

#### Infrastructure Management
* I want to **manage infrastructure via AWS CDK** so that environments are version-controlled and reproducible.
* I want to **deploy to multiple environments** (Alpha, Production) so that changes can be tested before reaching end users.
* I want to **use separate AWS resources per environment** (Cognito pools, DynamoDB tables, API Gateways) so that environments are isolated.
* I want to **configure custom domains** for each environment so that users can access the application via friendly URLs.

#### CI/CD Pipeline
* I want to **automate builds and deployments** via GitHub Actions so that releases are consistent and repeatable.
* I want to **run automated tests** (unit tests, linting, type checking) so that code quality is enforced.
* I want to **scan for security vulnerabilities** (Trivy) so that risky dependencies are flagged before deployment.
* I want to **require manual approval for production** so that deployments are reviewed by a human before going live.
* I want to **deploy frontend and backend independently** so that changes can be released in parallel.

#### Monitoring & Alerting
* I want to **monitor Lambda function performance** (duration, errors, throttles) so that I can identify issues quickly.
* I want to **monitor API Gateway metrics** (request count, latency, 4xx/5xx errors) so that I can track API health.
* I want to **set up CloudWatch alarms** for critical errors so that I am notified when issues occur.
* I want to **enable CloudTrail logging** so that AWS API activity is auditable.
* I want to **review logs centrally in CloudWatch** so that debugging is efficient.

#### Security & Compliance
* I want to **enforce least-privilege IAM policies** so that services have only the permissions they need.
* I want to **enable encryption at rest** (DynamoDB, S3) so that stored data is protected.
* I want to **enforce HTTPS** for all traffic so that data in transit is encrypted.
* I want to **rotate credentials and secrets** regularly so that security best practices are followed.
* I want to **implement AWS WAF** (future) so that the application is protected from common web attacks.

#### Cost Optimization
* I want to **use serverless services** (Lambda, DynamoDB on-demand, S3) so that costs scale with usage.
* I want to **leverage CloudFront caching** so that static assets are served efficiently and cheaply.
* I want to **monitor AWS costs** via Cost Explorer so that I can identify optimization opportunities.
* I want to **set budget alerts** so that unexpected cost spikes are detected early.

### _Acceptance Criteria_
* **Environment Isolation:**
  * If I deploy to Alpha, when I make changes, then Production remains unaffected.
  * If I deploy to Production, when deployment completes, then Alpha remains unaffected.
* **Pipeline Automation:**
  * If I push code to main branch, when CI/CD runs, then Alpha is deployed automatically.
  * If Alpha deployment succeeds, when I approve the production gate, then Production is deployed.
* **Monitoring:**
  * If Lambda errors exceed threshold, when the alarm triggers, then I receive a notification.
  * If API Gateway 5xx errors occur, when the alarm triggers, then I receive a notification.
* **Security:**
  * If HTTPS is not used, when a user tries to connect via HTTP, then they are redirected to HTTPS.
  * If a Lambda function tries to access a resource it doesn't have permissions for, then the action is denied.

---

## Appendix

### User Personas Summary
1. **End User (Candidate):** Prepares for interviews by practicing questions and receiving AI feedback.
2. **Marcus (AI Coach):** AWS Bedrock-powered assistant that evaluates answers and provides constructive feedback.
3. **Developer:** Builds and maintains the application, ensuring security, reliability, and code quality.
4. **Admin User:** Manages interview questions, ensuring content is accurate and up-to-date.
5. **Platform Administrator:** Manages infrastructure, deployments, monitoring, and security.

### Technology Stack
- **Frontend:** React 19, TypeScript, Vite
- **Backend:** Python 3.14, AWS Lambda
- **Database:** DynamoDB
- **AI:** AWS Bedrock (Claude 3.7 Sonnet)
- **Authentication:** AWS Cognito
- **Infrastructure:** AWS CDK (TypeScript)
- **CI/CD:** GitHub Actions
- **Hosting:** S3 + CloudFront
- **Monitoring:** CloudWatch, CloudTrail

### Key Features Implemented
- ✅ User authentication and authorization (Cognito)
- ✅ Question browsing with search and filters
- ✅ AI-powered answer evaluation (Marcus)
- ✅ Practice mode with instant feedback
- ✅ Multi-environment deployment (Alpha, Production)
- ✅ Automated CI/CD pipeline with security scanning
- ✅ Structured logging and monitoring
- ✅ Responsive design (desktop, tablet, mobile)

### Future Enhancements (Roadmap)
- 📝 Admin UI for question CRUD operations
- 📊 User progress tracking and analytics
- 🏆 Gamification (badges, streaks, leaderboards)
- 🧪 Mock interview simulator (timed questions)
- 🎙️ Voice answer practice (speech-to-text)
- 📱 Mobile native apps

---

**Document Version:** 2.0
**Original Source:** EPA Project User Stories (Quip)
**Last Updated:** February 2026
**Updated By:** Andreas Papasavvas (apaps)
**Status:** Living Document
