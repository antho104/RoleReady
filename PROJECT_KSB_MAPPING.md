# Project KSB Mapping Document - RoleReady

## Document Control

**Version:** V1.0
**Last Updated:** 2026-02-21

## Apprentice Details

| Field | Value |
|-------|-------|
| **Name** | Anthony Papier |
| **ULN** | 8378668354 |
| **Training Provider** | QA ltd |
| **Employer** | Amazon UK Services Ltd (AWS) |

---

## Project Overview

### Project Title
**RoleReady**

### Project Brief
I will be developing a full-stack interview question bank application for interviewers at AWS. This app will allow users to access technical and situational interview questions that can be filtered by role, level, and question type. The questions will be stored in an AWS DynamoDB table, and the deployed resources will interact with the database to display the questions on the frontend.

I will design, build, and deploy the entire application using AWS cloud services and CI/CD pipelines. The backend will be serverless, with Lambda functions written in Python to handle requests via API Gateway. The infrastructure will be defined using AWS CDK in TypeScript, allowing me to manage all resources—Lambda, API Gateway, DynamoDB, Cognito, and CloudWatch—as code. The application will be deployed using GitHub Actions, with the source code stored in GitHub and version-controlled using Git.

I will also develop the frontend using Cloudscape, built on the React framework. The frontend will communicate with the backend through API Gateway and will be accessible only to authenticated users via AWS Cognito. I will configure Cognito for user authentication and authorization to ensure secure access. To monitor and maintain performance, I will use AWS CloudWatch and AWS CloudTrail, setting up dashboards to visualize metrics, logs, and activity for my Lambda resource.

### Project Timeline
- **Project setup and MVP definition:** 1 week
- **Pipeline, infrastructure, and testing:** 2 weeks
- **Workflow optimization and monitoring:** 1 week
- **API development + testing:** 3 weeks

---

## KSB Mapping by Category

### 1. Code Quality

#### K2: Distributed Source Control
**Mapping:** I will implement Git-based version control, using feature branches for isolated development and pull requests to ensure controlled code integration.

**Pass Criteria:**
- Writes code, both general purpose and infrastructure-as-code that is correctly versioned and easy to merge
- Adheres to principles of distributed Source Control

---

#### K5: Modern Security Tools and Techniques
**Mapping:** I will apply vulnerability scanners and threat modelling techniques to evaluate security risks, then develop a comprehensive risk assessment outlining potential vulnerabilities and mitigation actions.

**Pass Criteria:**
- Demonstrates an iterative approach to evolving code consistent with cloud security best practice
- Evidence of lack of vulnerabilities
- All dependent components present at run time

---

#### K7: General Purpose Programming and Infrastructure-as-Code
**Mapping:** I will be using Python for my Lambda functions, TypeScript for my frontend and infrastructure as code (CDK).

---

#### K14: Test Driven Development and Test Pyramid
**Mapping:** I will develop unit tests and use mocking frameworks to simulate dependencies, ensuring reliable and test-driven code development.

**Pass Criteria:**
- Writes code around unit tests
- Appropriate use of test doubles and mocking strategies

---

#### S9: Cloud Security Tools in Automated Pipeline
**Mapping:** I will use vulnerability scanning and threat modelling to identify potential risks and produce a risk assessment outlining possible issues and mitigation strategies.

---

#### S11: Systematic Problem-Solving Approach
**Mapping:** I will apply the PDAC framework to solve problems, using logic to develop and debug my code effectively.

**Pass Criteria:**
- Explains troubleshooting methods used to identify and resolve issues
- Provides example of identifying and remediating issue that compromised code quality

---

#### S14: Test Driven Development Discipline
**Mapping:** I will create validation and assertion tests for my code and implement automated testing within my pipeline.

---

#### S17: Code in General Purpose Programming Language
**Mapping:** I will use Python to develop my Lambda function and TypeScript for both my frontend and infrastructure as code (CDK).

---

#### S18: Specify Cloud Infrastructure in IaC Language
**Mapping:** I will define my AWS cloud infrastructure using AWS CDK, organizing it with modules, variables, and resources.

---

#### S20: Writing Merge-Friendly Code
**Mapping:** I will maintain code quality by using linters such as Flake8 and writing smaller, frequent commits to minimize merge conflicts.

---

#### S22: Incremental Refactoring
**Mapping:** I will refactor my code through code reviews and pair programming, ensuring it remains clean, efficient, and up to date.

---

### 2. Meeting User Needs

#### K4: Business Value of DevOps
**Mapping:** I will ensure my cloud environment supports automated deployment and removal of resources, while maintaining cost efficiency and performance optimization.

**Pass Criteria:**
- Creates quality product in terms of Mean Time To Recovery (MTTR)
- Reduced time to fix bugs

---

#### K10: User Experience at Heart of Development
**Mapping:** I will gather feedback from users on the application and use it to develop and refine user stories.

---

#### K21: Architecture Principles and Patterns
**Mapping:** The project will consist of both frontend and backend components, which I will develop and integrate to ensure seamless interaction between all resources.

**Pass Criteria:**
- Writes user stories understandable to wide range of stakeholders
- Stories stand up to scrutiny
- Solution based on common architectural patterns
- Passes all acceptance tests

---

#### S3: Translate User Needs into Tasks
**Mapping:** I will implement user stories on my Kanban board to represent the technical requirements, each containing relevant tasks and acceptance criteria.

**Pass Criteria:**
- Piece of code meets 'must have' identified functional/non-functional user needs
- Encapsulated in acceptance criteria for the task

**Distinction Criteria:**
- Code meets 'should have' identified functional/non-functional user needs

---

### 3. The CI-CD Pipeline

#### K1: Continuous Integration Benefits
**Mapping:** This will be evidenced through commits in my GitHub repository.

**Pass Criteria:**
- Builds fully functioning, automated CI-CD pipeline
- All tests passing
- Evidences code commit progressing seamlessly from build artefact to end user

---

#### K15: CI, CD, and Continuous Deployment Principles
**Mapping:** This will be evidenced through commits in my GitHub repository and through automated workflows in GitHub Actions.

**Pass Criteria:**
- Explains pipeline capability
- Benefits of frequent merging of code
- Differences between CI/CD/Continuous Deployment

---

#### S15: Release Automation and Orchestration
**Mapping:** Release automation will be integrated into the pipeline, allowing source code to be automatically released and deployed.

---

### 4. Refreshing and Patching

#### K8: Immutable Infrastructure
**Mapping:** The resource's health will be maintained and monitored through CloudWatch, with CloudFormation templates enabling configuration and updates.

**Pass Criteria:**
- Deploys immutable infrastructure
- Enables regular recycling of servers
- Refreshing of associated software based on manual processes

**Distinction Criteria:**
- Fully automates the refreshing and patching process

---

#### S5: Deploy Immutable Infrastructure
**Mapping:** Using CDK will enable the deployment of immutable infrastructure, while CloudFormation templates will allow the infrastructure to be rebuilt during updates or deletions, preserving the application.

---

### 5. Operability

#### K11: Monitoring and Alerting Technologies
**Mapping:** Monitoring will be implemented using CloudWatch and CloudTrail, with logs and alarms configured to track key metrics.

**Pass Criteria:**
- Installs and manages monitoring and alerting tools
- Provides coverage of infrastructure and applications
- Includes RAM and CPU utilisation, application error rates, availability

---

#### S6: Install, Manage, and Troubleshoot Monitoring Tools
**Mapping:** Monitoring will be implemented using CloudWatch and CloudTrail, with logs and alarms configured and deployed through CDK.

**Pass Criteria:**
- Configures appropriate alerting thresholds and visualisations
- Interprets in terms of failure scenarios
- Remedial/follow up actions for continuous improvement

---

#### S19: Interpret Logs and Metrics Data
**Mapping:** Monitoring will be done through CloudWatch, using dashboards to visualize metrics and identify issues through logs and performance data.

**Distinction Criteria:**
- Introduces custom metrics providing additional improvement areas
- Explains how improvement areas may be interpreted, implemented, and delivered

---

#### B3: 'You Build It, You Run It' Commitment
**Mapping:** I will take full ownership of the pipeline and deployment, ensuring all resources are integrated and contribute to the overall application.

---

### 6. Data Persistence

#### K12: Persistence/Data Layer
**Mapping:** The resources I deploy will interact with a cloud-hosted database. I will review documentation to determine the most suitable database configuration for the application.

**Pass Criteria:**
- Employs appropriate data persistence technology
- Meets non-functional and functional needs
- Database/configuration/infrastructure state management

---

#### S7: Navigate and Troubleshoot Stateful Distributed Systems
**Mapping:** I will use CloudWatch Logs for logging, allowing me to navigate and troubleshoot system issues effectively.

**Pass Criteria:**
- Explains troubleshooting steps taken
- Locates issues across end-to-end service

---

### 7. Automation

#### K13: Automation Techniques
**Mapping:** This will be demonstrated through scripting within the application project.

**Pass Criteria:**
- Introduces process efficiencies
- Automates setup/deploying project from scratch
- Both locally (including all tests) and to hosted environment

---

#### K17: APIs - Understanding and Documentation
**Mapping:** I will use Boto3 within my Lambda function to interact with AWS services, making API calls between the functions and the database.

---

#### S12: Automate Tasks for Process Efficiency
**Mapping:** I will develop a code review bot to automate notifications and streamline the code review process.

**Distinction Criteria:**
- Identifies additional opportunity
- Introduces automation that reduces overall effort

---

### 8. Data Security

#### K16: Best Practices for Securing Data
**Mapping:** I will secure data using HTTPS with requested certificates and manage access through IAM roles.

**Pass Criteria:**
- Builds in security so all data in transit is encrypted and secure
- Explains types of threats
- Rationale behind decision to encrypt data at rest or not

---

#### S10: Assess Security Threats and Take Action
**Mapping:** I will use threat modelling to identify security risks and design the application infrastructure accordingly.

---

## Technology Stack Summary

### Backend
- **Language:** Python
- **Compute:** AWS Lambda (serverless functions)
- **API:** AWS API Gateway
- **Database:** AWS DynamoDB

### Frontend
- **Framework:** React with Cloudscape Design System
- **Language:** TypeScript

### Infrastructure
- **IaC Tool:** AWS CDK (TypeScript)
- **Resource Management:** AWS CloudFormation
- **Authentication:** AWS Cognito

### DevOps & Monitoring
- **Version Control:** Git & GitHub
- **CI/CD:** GitHub Actions
- **Monitoring:** AWS CloudWatch
- **Logging:** AWS CloudTrail
- **Code Quality:** Flake8 (Python linter)

### Security
- **Encryption:** HTTPS with certificates
- **Access Control:** IAM roles and policies
- **Threat Analysis:** Vulnerability scanning and threat modelling

---

## Assessment Criteria Summary

### Pass Requirements Met
1. ✓ Code quality with version control and security best practices
2. ✓ User needs translated into clear user stories
3. ✓ Fully functioning CI-CD pipeline
4. ✓ Immutable infrastructure deployment
5. ✓ Monitoring and alerting implementation
6. ✓ Appropriate data persistence technology
7. ✓ Process automation from scratch
8. ✓ Data security with encryption

### Distinction Criteria Targeted
1. ✓ Meets 'should have' user needs in acceptance criteria
2. ✓ Fully automates refreshing and patching
3. ✓ Custom metrics for additional improvements
4. ✓ Additional automation reducing overall effort

---

## Document Sign-Off

**Apprentice Signature:** _________________________
**Date:** _________________________

**EPAO Reviewer:** _________________________
**Date:** _________________________

**Employer Representative:** _________________________
**Date:** _________________________

---

*This document must be submitted at Gateway and signed off by BCS within 2 weeks. The project must be completed within 13 weeks of sign-off approval.*
