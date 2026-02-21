# Technical Documentation

## RoleReady - Interview Question Bank Platform

**Project Repository:** RoleReady - **Domain:**
<https://apaps.people.aws.dev> - **Architecture:** Serverless Full-Stack
Web Application on AWS

## Table of Contents

1.  [Executive Summary](#executive-summary)
2.  [System Architecture](#system-architecture)
3.  [Technology Stack](#technology-stack)
4.  [Backend Implementation](#backend-implementation)
5.  [Frontend Implementation](#frontend-implementation)
6.  [Infrastructure as Code](#infrastructure-as-code)
7.  [CI/CD Pipeline](#cicd-pipeline)
8.  [Security Implementation](#security-implementation)
9.  [Monitoring & Observability](#monitoring--observability)
10. [Testing Strategy](#testing-strategy)
11. [Deployment Evidence](#deployment-evidence)
12. [File Structure Reference](#file-structure-reference)

## Executive Summary

RoleReady is a serverless full-stack web application for interview
preparation, featuring:

- **Serverless Backend**: Python Lambda functions with DynamoDB
- **AI Integration**: AWS Bedrock (Claude 3.7 Sonnet) for answer
  evaluation
- **Modern Frontend**: React 19 with TypeScript, Vite build system
- **Infrastructure as Code**: AWS CDK (TypeScript)
- **Multi-environment**: Alpha and Production environments
- **Security**: AWS Cognito authentication, API Gateway authorization
- **CI/CD**: GitHub Actions with automated testing and deployment
- **Monitoring**: CloudWatch (standard + custom business metrics), CloudTrail, and custom dashboards
- **Content Delivery**: CloudFront CDN with custom domain
- **Security Scanning**: Trivy vulnerability scanner in CI/CD

## System Architecture

### High-Level Architecture

### Architecture Components

  ------------------------------------------------------------------------
  Component                 Technology                Purpose
  ------------------------- ------------------------- --------------------
  **Frontend Hosting**      S3 + CloudFront           Static React SPA
                                                      with CDN

  **API Gateway**           AWS API Gateway           RESTful API with
                                                      Cognito
                                                      authorization

  **Compute**               AWS Lambda (Python 3.11)  Serverless backend
                                                      functions

  **Database**              DynamoDB                  NoSQL question
                                                      storage

  **Authentication**        AWS Cognito               User management &
                                                      JWT tokens

  **AI Service**            AWS Bedrock (Claude 3.7   Answer evaluation
                            Sonnet)                   

  **DNS**                   Route 53                  Custom domain
                                                      management

  **Certificates**          AWS Certificate Manager   SSL/TLS certificates

  **Monitoring**            CloudWatch + CloudTrail   Standard metrics, logs,
                            + Custom Metrics          audit trails, and business-specific
                                                      audit trails

  **Security Scanning**     Trivy                     Vulnerability
                                                      detection in CI/CD
  ------------------------------------------------------------------------

## Technology Stack

### Backend Technologies

    # backend/requirements.txt
    pytest==9.0.2        # Unit testing framework
    boto3==1.42.37       # AWS SDK for Python
    flake8==7.3.0        # Code linting
    black==26.1.0        # Code formatting
    requests==2.31.0     # HTTP client library

**Key Backend Technologies:**

- **Runtime**: Python 3.11 (AWS Lambda)

- **AWS Services**: boto3 SDK

- **API Framework**: Lambda with API Gateway integration

- **Database**: DynamoDB (boto3 resource API)

- **AI Integration**: Bedrock Runtime API

### Frontend Technologies

    // frontend/package.json - Key Dependencies
    {
      "@aws-amplify/ui-react": "^6.13.1",  // Amplify UI components
      "aws-amplify": "^6.15.9",            // AWS integration
      "react": "^19.2.0",                   // React 19
      "react-dom": "^19.2.0",
      "react-router-dom": "^7.10.1",       // Client-side routing
      "typescript": "~5.9.3",              // Type safety
      "vite": "^7.2.4"                     // Build tool
    }

**Key Frontend Technologies:**

- **Framework**: React 19 with TypeScript

- **Build Tool**: Vite 7.2.4

- **State Management**: React Context API

- **Routing**: React Router v7

- **Auth Integration**: AWS Amplify

- **Styling**: CSS modules

### Infrastructure Technologies

    // infrastructure/package.json
    {
      "aws-cdk": "2.1033.0",      // CDK CLI
      "aws-cdk-lib": "2.215.0",   // CDK constructs
      "constructs": "^10.0.0",    // CDK base constructs
      "typescript": "~5.9.3",     // Type-safe IaC
      "jest": "^29.7.0"           // Infrastructure testing
    }

**Key Infrastructure Technologies:**

- **IaC Framework**: AWS CDK (TypeScript)

- **Testing**: Jest for CDK tests

- **CI/CD**: GitHub Actions

- **Security Scanning**: Trivy

## Backend Implementation

### Lambda Functions Architecture

The backend consists of three primary Lambda functions:

#### 1. Questions Handler (`questions_handler.py`)

**Purpose**: CRUD operations for interview questions

**Key Features:**

- RESTful API design (GET, POST, PUT, DELETE)

- DynamoDB integration with pagination

- Structured JSON logging for CloudWatch

- Custom JSON formatter for observability

- Error handling with appropriate HTTP status codes

- CORS support for frontend integration

**Code Evidence:**

    # Structured Logging Implementation
    class JsonFormatter(logging.Formatter):
        def format(self, record):
            log_data = {
                "timestamp": self.formatTime(record),
                "level": record.levelname,
                "message": record.getMessage(),
                "logger": record.name,
            }
            # Dynamic field injection for traceability
            if hasattr(record, "request_id"):
                log_data["request_id"] = record.request_id
            if hasattr(record, "question_count"):
                log_data["question_count"] = record.question_count
            return json.dumps(log_data)

    # Pagination Support for Large Datasets
    def handler(event, context):
        items = []
        response = table.scan()
        items.extend(response.get("Items", []))

        # Handle DynamoDB pagination automatically
        while "LastEvaluatedKey" in response:
            response = table.scan(
                ExclusiveStartKey=response["LastEvaluatedKey"]
            )
            items.extend(response.get("Items", []))

**API Endpoints:**

- `GET /questions` - List all questions (with pagination)

- `GET /questions/{id}` - Get single question

- `POST /questions` - Create new question (Cognito auth required)

- `PUT /questions/{id}` - Update question (Cognito auth required)

- `DELETE /questions/{id}` - Delete question (Cognito auth required)

#### 2. Marcus AI Coach (`evaluate_answer.py`)

**Purpose**: AI-powered answer evaluation using AWS Bedrock

**Key Features:**

- AWS Bedrock integration (Claude 3.7 Sonnet)

- Structured JSON response parsing

- Markdown code block cleaning

- Competency-based evaluation

- Detailed feedback generation

**Code Evidence:**

    # Direct Bedrock Model Invocation
    bedrock = boto3.client("bedrock-runtime", region_name="eu-west-2")

    # Structured prompt engineering for consistent JSON responses
    prompt = f"""You are Marcus, an AI interview coach for AWS.
    Evaluate this candidate's answer:

    Question: {question_text}
    Candidate's Answer: {user_answer}
    Competency: {competency_type}

    Respond ONLY with valid JSON in this exact format:
    {{
      "is_correct": true/false,
      "score": 0-100,
      "strengths": ["point1", "point2"],
      "improvements": ["point1", "point2"],
      "suggestions": ["point1", "point2"],
      "marcus_comment": "Your encouraging message here"
    }}"""

    # Model invocation with error handling
    response = bedrock.invoke_model(
        modelId="anthropic.claude-3-7-sonnet-20250219-v1:0",
        body=json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1000,
            "messages": [{"role": "user", "content": prompt}],
        }),
    )

    # Response parsing with markdown cleanup
    response_body = json.loads(response["body"].read())
    feedback_text = response_body["content"][0]["text"]

    # Strip markdown code blocks if present
    if feedback_text.startswith("```"):
        feedback_text = feedback_text.strip("`").strip()
        if feedback_text.startswith("json"):
            feedback_text = feedback_text[4:].strip()

    feedback = json.loads(feedback_text)

**IAM Permissions:**

    // Bedrock model invocation permission
    evaluateAnswerFn.addToRolePolicy(new iam.PolicyStatement({
      actions: ['bedrock:InvokeModel'],
      resources: [
        'arn:aws:bedrock:eu-west-2::foundation-model/anthropic.claude-3-7-sonnet-20250219-v1:0'
      ],
    }));

#### 3. User Signup Handler (`admin_create_user.py`)

**Purpose**: Secure user registration bypassing self-signup restrictions

**Key Features:**

- AdminCreateUser API (bypasses selfSignUpEnabled=false)

- Email validation using regex

- Automatic email verification

- Temporary password delivery via Cognito

- Force password change on first login

- Error handling for duplicate users

**Code Evidence:**

    # Email validation
    def is_valid_email(email):
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return re.match(pattern, email) is not None

    # Secure user creation with AdminCreateUser
    cognito_client.admin_create_user(
        UserPoolId=USER_POOL_ID,
        Username=email,
        UserAttributes=[
            {"Name": "email", "Value": email},
            {"Name": "email_verified", "Value": "true"},  # Auto-verify
        ],
        DesiredDeliveryMediums=["EMAIL"],  # Send temp password via email
        ForceAliasCreation=False,
        # MessageAction NOT set - Cognito sends welcome email
    )

    # Error handling for existing users
    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        if error_code == "UsernameExistsException":
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "User already exists"}),
            }

**Security Considerations:**

- Email format validation before API call

- Rate limiting (recommended via API Gateway throttling)

- Cognito enforces password complexity

- Temporary password expires after first use

- Email verification handled by Cognito

## Frontend Implementation

### React Application Architecture

**Technology Stack:**

- **Framework** -React 19 with TypeScript

- **Build Tool** - Vite (fast HMR and optimized production builds)

- **Routing** - React Router v7 (client-side routing)

- **State Management** - React Context API (AuthContext)

- **AWS Integration** - AWS Amplify for Cognito authentication

### Key Components

#### 1. Authentication Context (`contexts/AuthContext.tsx`)

**Purpose**: Centralized authentication state management

**Features:**

- Amplify Cognito integration

- User session management

- JWT token retrieval

- Password change flow

- Context Provider pattern

<!-- -->

    interface AuthContextType {
      user: AuthUser | null;
      loading: boolean;
      login: (username: string, password: string) => Promise<SignInOutput>;
      logout: () => Promise<void>;
      getAuthToken: () => Promise<string>;
      updatePassword: (oldPassword: string, newPassword: string) => Promise<void>;
    }

    export function AuthProvider({ children }: { children: ReactNode }) {
      const [user, setUser] = useState<AuthUser | null>(null);
      const [loading, setLoading] = useState(true);

      // Check current authentication status on mount
      useEffect(() => {
        checkAuth();
      }, []);

      const checkAuth = async () => {
        try {
          const currentUser = await getCurrentUser();
          setUser(currentUser);
        } catch {
          setUser(null);
        } finally {
          setLoading(false);
        }
      };

      // Provide context to child components
      return (
        <AuthContext.Provider value={{ user, loading, login, logout, getAuthToken }}>
          {children}
        </AuthContext.Provider>
      );
    }

#### 2. Questions Page (`pages/Questions.tsx`)

**Purpose**: Main application interface for question browsing and AI
practice

**Features:**

- Real-time search and filtering

- Dynamic category/difficulty filters

- Modal-based answer practice

- AI feedback display

- Authentication-gated access

- Loading states and error handling

**Code Evidence:**

    // API integration with JWT authentication
    const loadQuestions = async () => {
      if (!user) return;

      try {
        setLoading(true);
        const token = await getAuthToken();  // JWT from Cognito
        const data = await getAllQuestions(token);
        setQuestions(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load questions');
      } finally {
        setLoading(false);
      }
    };

    // AI evaluation integration
    const handleSubmitAnswer = async () => {
      try {
        setEvaluating(true);
        const token = await getAuthToken();
        const result = await evaluateAnswer({
          question: selectedQuestion.question_text,
          answer: userAnswer,
          competency_type: selectedQuestion.competency,
        }, token);
        setEvaluation(result);
      } catch (err) {
        alert(err instanceof Error ? err.message : 'Failed to evaluate answer');
      } finally {
        setEvaluating(false);
      }
    };

    // Memoized filtering for performance
    const filteredQuestions = useMemo(() => {
      return questions.filter(question => {
        const matchesSearch =
          question.question_text.toLowerCase().includes(searchTerm.toLowerCase()) ||
          question.competency.toLowerCase().includes(searchTerm.toLowerCase());
        const matchesCategory =
          selectedCategory === 'All' || question.category === selectedCategory;
        const matchesDifficulty =
          selectedDifficulty === 'All' ||
          question.difficulty.toLowerCase() === selectedDifficulty.toLowerCase();
        return matchesSearch && matchesCategory && matchesDifficulty;
      });
    }, [questions, searchTerm, selectedCategory, selectedDifficulty]);

#### 3. API Service (`services/api.ts`)

**Purpose**: Centralized API client with type safety

**Code Evidence:**

    // Type-safe API interfaces
    export interface Question {
      id: string;
      question_text: string;
      category: string;
      competency: string;
      difficulty: string;
      reference_answer?: string;
    }

    export interface EvaluationResponse {
      is_correct: boolean;
      score: number;
      strengths: string[];
      improvements: string[];
      suggestions: string[];
      marcus_comment: string;
    }

    // API client with authentication
    const apiClient = {
      async getAllQuestions(token: string): Promise<Question[]> {
        const response = await fetch(`${API_URL}questions`, {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        });
        if (!response.ok) throw new Error('Failed to fetch questions');
        return response.json();
      },

      async evaluateAnswer(
        payload: EvaluationRequest,
        token: string
      ): Promise<EvaluationResponse> {
        const response = await fetch(`${API_URL}answers`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(payload),
        });
        if (!response.ok) throw new Error('Failed to evaluate answer');
        return response.json();
      }
    };

### Build Configuration

**Vite Configuration (**`vite.config.ts`**):**

    export default defineConfig({
      plugins: [react()],
      server: {
        port: 3000,
        open: true,
      },
      build: {
        outDir: 'dist',
        sourcemap: true,  // Source maps for debugging
        rollupOptions: {
          output: {
            manualChunks: {
              'react-vendor': ['react', 'react-dom', 'react-router-dom'],
              'aws-vendor': ['aws-amplify', '@aws-amplify/ui-react'],
            }
          }
        }
      }
    });

**Environment Variables:**

    # Injected at build time by CI/CD
    VITE_API_URL=https://api.apaps.people.aws.dev/
    VITE_USER_POOL_ID=<dynamically-fetched>
    VITE_USER_POOL_CLIENT_ID=<dynamically-fetched>

## Infrastructure as Code

### AWS CDK Implementation

**Technology**: TypeScript-based AWS CDK v2

**Stack Structure:**

    // infrastructure/lib/stacks/service.ts
    export interface ServiceStackProps extends cdk.StackProps {
      enableMonitoring?: boolean;
      notificationEmail?: string;
      environment?: 'alpha' | 'prod';
      domainName?: string;
    }

    export class ServiceStack extends cdk.Stack {
      constructor(scope: Construct, id: string, props?: ServiceStackProps) {
        super(scope, id, props);

        const environment = props?.environment ?? 'prod';
        const rootDomain = props?.domainName || 'apaps.people.aws.dev';
        const isProduction = environment === 'prod';

        // Infrastructure components...
      }
    }

### Infrastructure Components

#### 1. DNS & Custom Domain (Route 53 + ACM)

**Production Environment:**

    // Lookup Supernova-delegated hosted zone
    hostedZone = route53.HostedZone.fromLookup(this, 'RootHostedZone', {
      domainName: 'apaps.people.aws.dev',
    });

    // Certificate MUST be in us-east-1 for CloudFront
    certificate = new acm.DnsValidatedCertificate(this, 'WebsiteCertificate', {
      domainName: 'apaps.people.aws.dev',
      hostedZone: hostedZone,
      region: 'us-east-1',  // CloudFront requirement
    });

    // API certificate in same region as API Gateway
    apiCertificate = new acm.Certificate(this, 'ApiCertificate', {
      domainName: 'api.apaps.people.aws.dev',
      validation: acm.CertificateValidation.fromDns(hostedZone),
    });

**Alpha Environment (Subdomain Delegation):**

    // Create subdomain hosted zone for alpha
    hostedZone = new route53.PublicHostedZone(this, 'SubdomainHostedZone', {
      zoneName: 'alpha.apaps.people.aws.dev',
      caaAmazon: true,
    });

    // Output NS servers for manual delegation
    new cdk.CfnOutput(this, 'SubdomainNameServers', {
      value: cdk.Fn.join(', ', hostedZone.hostedZoneNameServers || []),
      description: 'Add these NS records to production account',
    });

**Supernova IAM Role (Production Only):**

    const supernovaRole = new iam.Role(this, 'SupernovaRole', {
      roleName: 'Nova-DO-NOT-DELETE',
      description: 'IAM role for Supernova DNS delegation',
      assumedBy: new iam.ServicePrincipal('nova.aws.internal'),
      maxSessionDuration: cdk.Duration.hours(12),
    });

    supernovaRole.addManagedPolicy(
      iam.ManagedPolicy.fromAwsManagedPolicyName('AmazonRoute53FullAccess')
    );

#### 2. Authentication (Cognito)

    const userPool = new cognito.UserPool(this, 'InterviewQuestionBankUserPool', {
      userPoolName: 'interview-question-bank-users',
      selfSignUpEnabled: false,  // Controlled registration via Lambda
      signInAliases: { email: true },
      autoVerify: { email: true },
      standardAttributes: {
        email: {
          required: true,
          mutable: false,  // Email cannot be changed
        },
      },
      passwordPolicy: {
        minLength: 8,
        requireLowercase: true,
        requireUppercase: true,
        requireDigits: true,
        requireSymbols: false,
      },
      accountRecovery: cognito.AccountRecovery.EMAIL_ONLY,
      removalPolicy: cdk.RemovalPolicy.RETAIN,  // Preserve users
    });

    const userPoolClient = userPool.addClient('WebAppClient', {
      userPoolClientName: 'web-app-client',
      authFlows: {
        userPassword: true,
        userSrp: true,  // Secure Remote Password protocol
      },
      preventUserExistenceErrors: true,  // Security best practice
    });

#### 3. Frontend Hosting (S3 + CloudFront)

    // S3 bucket with security hardening
    const frontendS3 = new s3.Bucket(this, 'FrontendBucket', {
      blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
      publicReadAccess: false,
      encryption: s3.BucketEncryption.S3_MANAGED,
      enforceSSL: true,
      removalPolicy: cdk.RemovalPolicy.RETAIN,
    });

    // Origin Access Identity for secure CloudFront access
    const originAccessIdentity = new cloudfront.OriginAccessIdentity(this, 'OAI', {
      comment: 'OAI for Interview Question Bank Frontend',
    });
    frontendS3.grantRead(originAccessIdentity);

    // CloudFront distribution with custom domain
    const distribution = new cloudfront.Distribution(this, 'FrontendDistribution', {
      domainNames: [websiteDomain],
      certificate: certificate,
      defaultBehavior: {
        origin: new origins.S3Origin(frontendS3, {
          originAccessIdentity: originAccessIdentity,
        }),
        viewerProtocolPolicy: cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
        compress: true,
      },
      defaultRootObject: 'index.html',
      errorResponses: [
        {
          httpStatus: 403,
          responseHttpStatus: 200,
          responsePagePath: '/index.html',  // SPA routing support
          ttl: cdk.Duration.minutes(5),
        },
        {
          httpStatus: 404,
          responseHttpStatus: 200,
          responsePagePath: '/index.html',
          ttl: cdk.Duration.minutes(5),
        },
      ],
      priceClass: cloudfront.PriceClass.PRICE_CLASS_100,  // US/Europe only
    });

    // Route 53 alias record
    new route53.ARecord(this, 'WebsiteAliasRecord', {
      zone: hostedZone,
      recordName: undefined,  // Apex record
      target: route53.RecordTarget.fromAlias(
        new route53Targets.CloudFrontTarget(distribution)
      ),
    });

#### 4. Database (DynamoDB)

    const table = new dynamodb.Table(this, 'InterviewQuestions', {
      partitionKey: { name: 'id', type: dynamodb.AttributeType.STRING },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,  // Auto-scaling
      removalPolicy: cdk.RemovalPolicy.RETAIN,  // Preserve data
      encryption: dynamodb.TableEncryption.AWS_MANAGED,
      pointInTimeRecovery: true,  // Backup for last 35 days
    });

#### 5. Lambda Functions

    // Questions handler
    const questionsHandler = new lambda.Function(this, 'QuestionsHandler', {
      runtime: lambda.Runtime.PYTHON_3_11,
      handler: 'questions_handler.handler',
      code: lambda.Code.fromAsset("../backend/src"),
      timeout: cdk.Duration.seconds(30),
      memorySize: 256,
      logRetention: logs.RetentionDays.ONE_MONTH,
      environment: {
        TABLE_NAME: table.tableName,
        LOG_LEVEL: 'INFO',
      },
    });
    table.grantReadWriteData(questionsHandler);

    // Marcus AI evaluation
    const evaluateAnswerFn = new lambda.Function(this, 'EvaluateAnswerFunction', {
      runtime: lambda.Runtime.PYTHON_3_11,
      handler: 'evaluate_answer.handler',
      code: lambda.Code.fromAsset("../backend/src"),
      timeout: cdk.Duration.seconds(30),
    });
    evaluateAnswerFn.addToRolePolicy(new iam.PolicyStatement({
      actions: ['bedrock:InvokeModel'],
      resources: [
        'arn:aws:bedrock:eu-west-2::foundation-model/anthropic.claude-3-7-sonnet-20250219-v1:0'
      ],
    }));

    // User signup handler
    const signupHandler = new lambda.Function(this, 'SignupHandler', {
      runtime: lambda.Runtime.PYTHON_3_11,
      handler: 'admin_create_user.handler',
      code: lambda.Code.fromAsset("../backend/src"),
      timeout: cdk.Duration.seconds(30),
      environment: {
        USER_POOL_ID: userPool.userPoolId,
      },
    });
    userPool.grant(signupHandler, 'cognito-idp:AdminCreateUser');

#### 6. API Gateway with Custom Domain

    // Cognito authorizer
    const cognitoAuthorizer = new apigw.CognitoUserPoolsAuthorizer(
      this,
      'CognitoAuthorizer',
      {
        cognitoUserPools: [userPool],
        authorizerName: 'CognitoAuthorizer',
        identitySource: 'method.request.header.Authorization',
      }
    );

    // REST API
    const api = new apigw.LambdaRestApi(this, 'InterviewQuestionBankApi', {
      handler: questionsHandler,
      proxy: false,
      description: 'Interview Question Bank API',
      defaultCorsPreflightOptions: {
        allowOrigins: apigw.Cors.ALL_ORIGINS,
        allowMethods: apigw.Cors.ALL_METHODS,
        allowHeaders: [
          'Content-Type',
          'Authorization',
          'X-Amz-Date',
          'X-Api-Key',
          'X-Amz-Security-Token',
        ],
        allowCredentials: true,
      },
    });

    // Custom domain
    const customDomain = new apigw.DomainName(this, 'ApiCustomDomain', {
      domainName: apiDomain,
      certificate: apiCertificate,
      endpointType: apigw.EndpointType.REGIONAL,
      securityPolicy: apigw.SecurityPolicy.TLS_1_2,
    });
    customDomain.addBasePathMapping(api, { basePath: '' });

    // Route 53 alias
    new route53.ARecord(this, 'ApiAliasRecord', {
      zone: hostedZone,
      recordName: 'api',
      target: route53.RecordTarget.fromAlias(
        new route53Targets.ApiGatewayDomain(customDomain)
      ),
    });

    // API routes with authorization
    const questions = api.root.addResource('questions');
    questions.addMethod('GET', lambdaIntegration, {
      authorizer: cognitoAuthorizer,
      authorizationType: apigw.AuthorizationType.COGNITO,
    });

    // Public signup endpoint (no auth)
    const signup = api.root.addResource('signup');
    signup.addMethod('POST', signupIntegration);

    // Marcus evaluation endpoint (authenticated)
    const answers = api.root.addResource('answers');
    answers.addMethod('POST', evaluateIntegration, {
      authorizer: cognitoAuthorizer,
      authorizationType: apigw.AuthorizationType.COGNITO,
    });

## CI/CD Pipeline

### Pipeline Diagrams

Overview

![](media/image2.png){width="6.5in" height="2.077777777777778in"}

Infrastructure & Backend workflow

![](media/image3.png){width="6.5in" height="1.1729166666666666in"}

Frontend workflow

![](media/image4.png){width="6.5in" height="1.3444444444444446in"}

### GitHub Actions Workflows

The project uses GitHub Actions with OpenID Connect (OIDC) for secure
AWS access.

#### Workflow 1: Infrastructure & Backend Deploy

**File**: `.github/workflows/infa-and-backend.yml`

**Triggers:** - Push to `main` branch - Pull requests to `main` - Paths:
`infrastructure/**, backend/**, package.json`

**Jobs:**

    jobs:
      # 1. Backend Tests
      backend-tests:
        runs-on: ubuntu-latest
        steps:
          - Checkout code
          - Set up Python 3.11
          - Install dependencies (requirements.txt)
          - Run make build (format, lint, test)
          - Run Trivy vulnerability scanner
            • Scans backend + infrastructure dependencies
            • Fails on CRITICAL/HIGH vulnerabilities
            • Ignores unfixed CVEs

      # 2. CDK Check
      cdk-check:
        needs: backend-tests
        steps:
          - Install Node dependencies
          - Run infrastructure unit tests (Jest)
          - TypeScript type checking
          - CDK synth (validate CloudFormation templates)

      # 3. Deploy to Alpha
      deploy-alpha:
        needs: [backend-tests, cdk-check]
        if: github.event_name == 'push' && github.ref == 'refs/heads/main'
        steps:
          - Configure AWS credentials (OIDC)
            • Role: arn:aws:iam::265870078323:role/github-actions-deploy
            • Account: Alpha (265870078323)
            • Region: eu-west-1
          - CDK deploy (no approval required)

      # 4. Integration Tests (Alpha)
      integration-tests-alpha:
        needs: deploy-alpha
        steps:
          - Get API URL from CloudFormation outputs
          - Run pytest integration tests against Alpha
            • Tests: backend/tests/test_alpha_integration.py

      # 5. Deploy to Production
      deploy-prod:
        needs: [deploy-alpha, integration-tests-alpha]
        environment: production  # Requires manual approval
        steps:
          - Configure AWS credentials (Production)
            • Role: arn:aws:iam::431081169070:role/github-actions-deploy
            • Account: Production (431081169070)
          - CDK deploy to production

**Security Features:**

- OIDC authentication (no long-lived credentials)

- Least privilege IAM roles per environment

- Vulnerability scanning with Trivy

- Manual approval for production deployment

- Integration tests before production promotion

#### Workflow 2: Frontend Deploy

**File**: `.github/workflows/frontend.yml`

**Triggers:** - Push to `main` branch - Paths:
`frontend/**, package.json`

**Jobs:**

    jobs:
      # 1. Deploy to Alpha
      deploy-alpha:
        runs-on: ubuntu-latest
        steps:
          - Install Node dependencies
          - Run linting (eslint)
          - Type check (tsc --noEmit)
          - Run Trivy (frontend npm dependencies only)
          - Configure AWS credentials (Alpha)
          - Get stack outputs (UserPoolId, UserPoolClientId)
          - Build frontend with environment variables:
            • VITE_API_URL=https://api.alpha.apaps.people.aws.dev/
            • VITE_USER_POOL_ID=<fetched-from-stack>
            • VITE_USER_POOL_CLIENT_ID=<fetched-from-stack>
          - Upload to S3 bucket (sync with --delete)

      # 2. Deploy to Production
      deploy-prod:
        needs: deploy-alpha
        environment: production  # Manual approval
        steps:
          - Build with production API URL:
            • VITE_API_URL=https://api.apaps.people.aws.dev/
          - Upload to production S3 bucket

**Key Features:**

- Environment-specific builds

- Dynamic configuration from CloudFormation outputs

- Separate Trivy scans (frontend-only dependencies)

- S3 sync with deletion of removed files

- Manual approval for production

### Trivy Security Scanning

**Backend/Infrastructure Scan:**

    - name: Run Trivy vulnerability scanner (All Dependencies)
      uses: aquasecurity/trivy-action@master
      with:
        scan-type: 'fs'
        scan-ref: '.'
        format: 'table'
        exit-code: '1'  # Fail build on vulnerabilities
        severity: 'CRITICAL,HIGH'
        ignore-unfixed: true  # Only fail on fixable issues

**Frontend Scan (Scoped):**

    - name: Run Trivy vulnerability scanner (npm dependencies only)
      uses: aquasecurity/trivy-action@master
      with:
        scan-type: 'fs'
        scan-ref: '.'
        scanners: 'vuln'
        skip-dirs: 'backend,infrastructure'  # Frontend only
        format: 'table'
        exit-code: '1'
        severity: 'CRITICAL,HIGH'
        ignore-unfixed: true

### OIDC Configuration

**GitHub OIDC Trust Policy (IAM):**

    {
      "Version": "2012-10-17",
      "Statement": [
        {
          "Effect": "Allow",
          "Principal": {
            "Federated": "arn:aws:iam::ACCOUNT_ID:oidc-provider/token.actions.githubusercontent.com"
          },
          "Action": "sts:AssumeRoleWithWebIdentity",
          "Condition": {
            "StringEquals": {
              "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
            },
            "StringLike": {
              "token.actions.githubusercontent.com:sub": "repo:apaps/RoleReady:*"
            }
          }
        }
      ]
    }

## Security Implementation

### 1. Authentication & Authorization

**AWS Cognito Configuration:**

    // User pool security settings
    const userPool = new cognito.UserPool(this, 'UserPool', {
      selfSignUpEnabled: false,  // Prevents unauthorized registration
      passwordPolicy: {
        minLength: 8,
        requireLowercase: true,
        requireUppercase: true,
        requireDigits: true,
        requireSymbols: false,
      },
      accountRecovery: cognito.AccountRecovery.EMAIL_ONLY,
      mfa: cognito.Mfa.OPTIONAL,  // Can be enforced per user
    });

**API Gateway Authorization:**

    // JWT token validation via Cognito
    const cognitoAuthorizer = new apigw.CognitoUserPoolsAuthorizer(
      this,
      'CognitoAuthorizer',
      {
        cognitoUserPools: [userPool],
        identitySource: 'method.request.header.Authorization',
      }
    );

    // Apply to protected endpoints
    questions.addMethod('GET', lambdaIntegration, {
      authorizer: cognitoAuthorizer,
      authorizationType: apigw.AuthorizationType.COGNITO,
    });

### 2. Network Security

**HTTPS Enforcement:**

- CloudFront: `viewerProtocolPolicy: REDIRECT_TO_HTTPS`

- S3: `enforceSSL: true`

- API Gateway: `securityPolicy: TLS_1_2`

**CORS Configuration:**

    defaultCorsPreflightOptions: {
      allowOrigins: apigw.Cors.ALL_ORIGINS,  // Production: lock to specific domain
      allowMethods: apigw.Cors.ALL_METHODS,
      allowHeaders: ['Content-Type', 'Authorization', ...],
      allowCredentials: true,
    }

### 3. Data Protection

**Encryption at Rest:**

- S3: `encryption: s3.BucketEncryption.S3_MANAGED`

- DynamoDB: `encryption: dynamodb.TableEncryption.AWS_MANAGED`

- CloudWatch Logs: Encrypted by default

- CloudTrail Logs: `encryption: s3.BucketEncryption.S3_MANAGED`

**Encryption in Transit:**

- All API calls use HTTPS

- TLS 1.2 minimum on all endpoints

- ACM certificates with automatic renewal

### 4. IAM Least Privilege

**Lambda Execution Roles:**

    // Questions handler - DynamoDB only
    table.grantReadWriteData(questionsHandler);

    // Marcus AI - Bedrock only
    evaluateAnswerFn.addToRolePolicy(new iam.PolicyStatement({
      actions: ['bedrock:InvokeModel'],
      resources: ['arn:aws:bedrock:...specific-model-arn'],
    }));

    // Signup handler - Cognito user creation only
    userPool.grant(signupHandler, 'cognito-idp:AdminCreateUser');

### 5. Secrets Management

**Environment Variables:**

- Sensitive values (User Pool ID) stored in Lambda environment variables

- API keys and tokens retrieved from AWS Secrets Manager (recommended)

- Frontend config injected at build time from CloudFormation outputs

### 6. Input Validation

**Backend Validation:**

    # Email validation
    def is_valid_email(email):
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return re.match(pattern, email) is not None

    # Input sanitization
    email = body.get("email", "").strip().lower()

    if not email:
        return {"statusCode": 400, "body": json.dumps({"error": "Email is required"})}

    if not is_valid_email(email):
        return {"statusCode": 400, "body": json.dumps({"error": "Invalid email format"})}

**Frontend Validation:**

    // Type-safe API client
    const handleSubmitAnswer = async () => {
      if (!selectedQuestion || !userAnswer.trim()) {
        return;  // Validation before API call
      }
      // API call...
    };

### 7. Security Scanning

**Trivy in CI/CD:**

- Scans all dependencies (npm, pip, infrastructure)

- Fails build on CRITICAL/HIGH vulnerabilities

- Ignores unfixed CVEs to avoid false positives

- Separate scans for frontend and backend

### 8. S3 Security Hardening

    const frontendS3 = new s3.Bucket(this, 'FrontendBucket', {
      blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,  // No public access
      publicReadAccess: false,
      encryption: s3.BucketEncryption.S3_MANAGED,
      enforceSSL: true,  // Reject non-HTTPS requests
      versioned: true,  // CloudTrail logs bucket
      lifecycleRules: [  // Cost optimization + compliance
        {
          id: 'DeleteOldLogs',
          enabled: true,
          expiration: cdk.Duration.days(90),
        },
      ],
      removalPolicy: cdk.RemovalPolicy.RETAIN,  // Prevent accidental deletion
    });

## Monitoring & Observability

### 1. CloudWatch Monitoring

**Lambda Metrics:**

    // Lambda error alarm
    const lambdaErrorAlarm = new cloudwatch.Alarm(this, 'LambdaErrorAlarm', {
      alarmName: `${this.stackName}-lambda-errors`,
      metric: questionsHandler.metricErrors({
        statistic: 'Sum',
        period: cdk.Duration.minutes(5),
      }),
      threshold: 5,
      evaluationPeriods: 1,
      comparisonOperator: cloudwatch.ComparisonOperator.GREATER_THAN_OR_EQUAL_TO_THRESHOLD,
    });

    // Lambda throttle alarm
    const lambdaThrottleAlarm = new cloudwatch.Alarm(this, 'LambdaThrottleAlarm', {
      alarmName: `${this.stackName}-lambda-throttles`,
      metric: questionsHandler.metricThrottles({
        statistic: 'Sum',
        period: cdk.Duration.minutes(5),
      }),
      threshold: 1,
      evaluationPeriods: 1,
    });

    // Lambda duration alarm (latency)
    const lambdaDurationAlarm = new cloudwatch.Alarm(this, 'LambdaDurationAlarm', {
      alarmName: `${this.stackName}-lambda-high-duration`,
      metric: questionsHandler.metricDuration({
        statistic: 'Average',
        period: cdk.Duration.minutes(5),
      }),
      threshold: 5000,  // 5 seconds
      evaluationPeriods: 2,
    });

    // API Gateway 5XX errors
    const api5xxAlarm = new cloudwatch.Alarm(this, 'Api5xxErrorAlarm', {
      alarmName: `${this.stackName}-api-5xx-errors`,
      metric: new cloudwatch.Metric({
        namespace: 'AWS/ApiGateway',
        metricName: '5XXError',
        dimensionsMap: { ApiName: api.restApiName },
        statistic: 'Sum',
        period: cdk.Duration.minutes(5),
      }),
      threshold: 5,
      evaluationPeriods: 1,
    });

**SNS Notifications:**

    // SNS topic for alarm notifications
    const alarmTopic = new sns.Topic(this, 'AlarmTopic', {
      displayName: 'Interview Questions API Alarms',
    });

    new sns.Subscription(this, 'AlarmEmailSubscription', {
      topic: alarmTopic,
      protocol: sns.SubscriptionProtocol.EMAIL,
      endpoint: props.notificationEmail,
    });

    // Attach to alarms
    const snsAction = new cloudwatch_actions.SnsAction(alarmTopic);
    lambdaErrorAlarm.addAlarmAction(snsAction);
    lambdaThrottleAlarm.addAlarmAction(snsAction);
    lambdaDurationAlarm.addAlarmAction(snsAction);
    api5xxAlarm.addAlarmAction(snsAction);

**CloudWatch Dashboard:**

    const dashboard = new cloudwatch.Dashboard(this, 'ApiDashboard', {
      dashboardName: `${this.stackName}-monitoring`,
    });

    dashboard.addWidgets(
      new cloudwatch.GraphWidget({
        title: 'Lambda Invocations',
        left: [questionsHandler.metricInvocations()],
        width: 12,
      }),
      new cloudwatch.GraphWidget({
        title: 'Lambda Errors',
        left: [questionsHandler.metricErrors()],
        width: 12,
      }),
      new cloudwatch.GraphWidget({
        title: 'Lambda Duration',
        left: [
          questionsHandler.metricDuration({ statistic: 'Average' }),
          questionsHandler.metricDuration({ statistic: 'p99' }),
        ],
        width: 12,
      }),
      new cloudwatch.GraphWidget({
        title: 'API Gateway Requests',
        left: [
          new cloudwatch.Metric({
            namespace: 'AWS/ApiGateway',
            metricName: 'Count',
            dimensionsMap: { ApiName: api.restApiName },
            statistic: 'Sum',
          }),
        ],
        width: 12,
      }),
    );

### 1.5. Custom Business Metrics

**Custom Metrics Module (`backend/src/custom_metrics.py`):**

    # Custom namespace for all RoleReady metrics
    NAMESPACE = "RoleReady"

    def emit_metric(
        metric_name: str,
        value: float,
        unit: str = "Count",
        dimensions: Optional[List[Dict[str, str]]] = None,
    ) -> None:
        """
        Emit a custom CloudWatch metric.

        Args:
            metric_name: Name of the metric
            value: Metric value
            unit: Unit type (Count, Seconds, Bytes, etc.)
            dimensions: Optional list of dimension dicts
        """
        cloudwatch.put_metric_data(Namespace=NAMESPACE, MetricData=[...])

**Three Metric Categories:**

1. **QuestionsMetrics** - Track question retrieval and viewing
2. **EvaluationMetrics** - Track AI evaluation performance
3. **SystemMetrics** - Track system health indicators

**Questions Handler Metrics:**

    # Emitted in questions_handler.py
    from custom_metrics import QuestionsMetrics

    # Track questions retrieved
    QuestionsMetrics.questions_retrieved(len(items))

    # Track individual question views with category dimension
    QuestionsMetrics.question_viewed(question_id, category)

    # Track 404 errors
    QuestionsMetrics.question_not_found()

    # Track API latency by operation
    QuestionsMetrics.api_latency(latency_ms, "ListQuestions")
    QuestionsMetrics.api_latency(latency_ms, "GetQuestion")

    # Track search operations
    QuestionsMetrics.search_performed(result_count)

**AI Evaluation Metrics (Marcus AI):**

    # Emitted in evaluate_answer.py
    from custom_metrics import EvaluationMetrics

    # Track answer evaluations with multiple dimensions
    EvaluationMetrics.answer_evaluated(
        score=85,
        competency_type="AWS",  # AWS, Leadership, System Design
        is_correct=True
    )

    # Track evaluation success/failure
    EvaluationMetrics.evaluation_success()
    EvaluationMetrics.evaluation_failure(error_type)

    # Track Marcus AI response time
    EvaluationMetrics.ai_response_time(duration_ms)

    # Track user engagement (High/Medium/Low based on score)
    EvaluationMetrics.user_engagement(score)
    # High: 80-100, Medium: 50-79, Low: 0-49

**System Metrics:**

    SystemMetrics.cold_start()  # Lambda cold start tracking
    SystemMetrics.memory_usage(memory_mb)  # Memory consumption
    SystemMetrics.concurrent_executions(count)  # Concurrency tracking

**Metric Dimensions:**

- **Category** - Question category (AWS, Azure, GCP, Leadership, etc.)
- **CompetencyType** - Evaluation competency type
- **IsCorrect** - Answer correctness (True/False)
- **EngagementLevel** - User engagement level (High/Medium/Low)
- **Operation** - API operation name (ListQuestions, GetQuestion)
- **ErrorType** - Error classification for failed evaluations

**CloudWatch Permissions:**

    // Added to Lambda IAM roles in service.ts
    questionsHandler.addToRolePolicy(new iam.PolicyStatement({
      actions: ['cloudwatch:PutMetricData'],
      resources: ['*'],
      conditions: {
        'StringEquals': { 'cloudwatch:namespace': 'RoleReady' }
      }
    }));

    evaluateAnswerFn.addToRolePolicy(new iam.PolicyStatement({
      actions: ['cloudwatch:PutMetricData'],
      resources: ['*'],
      conditions: {
        'StringEquals': { 'cloudwatch:namespace': 'RoleReady' }
      }
    }));

**Available Custom Metrics:**

  -----------------------------------------------------------------------
  Metric Name               Unit           Purpose
  ------------------------- -------------- ----------------------------
  QuestionsRetrieved        Count          Number of questions
                                           returned per request

  QuestionViewed            Count          Individual question views
                                           (by category)

  QuestionNotFound          Count          404 errors

  APILatency                Milliseconds   API response times (by
                                           operation)

  SearchPerformed           Count          Search operations

  SearchResultCount         Count          Number of search results

  AnswerEvaluated           Count          Total evaluations

  EvaluationScore           None           AI evaluation scores (0-100)

  EvaluationByCompetency    Count          Evaluations by competency
                                           type

  AnswerCorrectness         Count          Correct vs incorrect answers

  EvaluationSuccess         Count          Successful evaluations

  EvaluationFailure         Count          Failed evaluations (by error
                                           type)

  MarcusResponseTime        Milliseconds   Marcus AI response latency

  UserEngagement            Count          Engagement level tracking

  ColdStart                 Count          Lambda cold starts

  MemoryUsage               Megabytes      Lambda memory consumption

  ConcurrentExecutions      Count          Concurrent Lambda executions
  -----------------------------------------------------------------------

**Business Value:**

- Track user engagement patterns by competency type
- Monitor AI evaluation accuracy and performance
- Identify popular question categories
- Measure API latency for performance optimization
- Alert on evaluation failures or high latency
- Understand user learning behavior

### 2. Structured Logging

**Backend Logging Implementation:**

    # Custom JSON formatter for CloudWatch Logs Insights
    class JsonFormatter(logging.Formatter):
        def format(self, record):
            log_data = {
                "timestamp": self.formatTime(record),
                "level": record.levelname,
                "message": record.getMessage(),
                "logger": record.name,
            }

            # Dynamic field injection
            if hasattr(record, "request_id"):
                log_data["request_id"] = record.request_id
            if hasattr(record, "question_count"):
                log_data["question_count"] = record.question_count

            return json.dumps(log_data)

    # Usage in handler
    logger.info(
        "Successfully retrieved questions",
        extra={"request_id": context.aws_request_id, "question_count": len(items)},
    )

**CloudWatch Logs Insights Queries:**

    # Find all errors in last hour
    fields @timestamp, message, error_type, request_id
    | filter level = "ERROR"
    | sort @timestamp desc
    | limit 100

    # Monitor question retrieval performance
    fields @timestamp, question_count, @duration
    | filter message = "Successfully retrieved questions"
    | stats avg(@duration), max(@duration), count() by bin(5m)

    # Track API latency by endpoint
    fields @timestamp, path, method, @duration
    | stats avg(@duration), p99(@duration) by path

### 3. CloudTrail Audit Logging

    // S3 bucket for CloudTrail logs
    const trailBucket = new s3.Bucket(this, 'CloudTrailBucket', {
      bucketName: `cloudtrail-logs-${this.account}-${this.region}`,
      encryption: s3.BucketEncryption.S3_MANAGED,
      versioned: true,
      blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
      lifecycleRules: [
        {
          id: 'DeleteOldLogs',
          enabled: true,
          expiration: cdk.Duration.days(90),
        },
        {
          id: 'TransitionToIA',
          enabled: true,
          transitions: [
            {
              storageClass: s3.StorageClass.INFREQUENT_ACCESS,
              transitionAfter: cdk.Duration.days(30),
            },
          ],
        },
      ],
      removalPolicy: cdk.RemovalPolicy.RETAIN,
    });

    // CloudWatch Log Group for real-time analysis
    const trailLogGroup = new logs.LogGroup(this, 'CloudTrailLogGroup', {
      logGroupName: `/aws/cloudtrail/${this.stackName}`,
      retention: logs.RetentionDays.ONE_MONTH,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
    });

    // CloudTrail trail
    const trail = new cloudtrail.Trail(this, 'ApiActivityTrail', {
      trailName: 'ApiActivityTrail',
      bucket: trailBucket,
      cloudWatchLogGroup: trailLogGroup,
      enableFileValidation: true,  // Ensure log integrity
      includeGlobalServiceEvents: true,  // IAM, CloudFront
      isMultiRegionTrail: false,  // Single region (cost optimization)
      managementEvents: cloudtrail.ReadWriteType.ALL,  // Track all API calls
      sendToCloudWatchLogs: true,
    });

### 4. Log Retention

  -----------------------------------------------------------------------
  Log Type                   Retention Period      Storage Location
  -------------------------- --------------------- ----------------------
  Lambda Logs                30 days               CloudWatch Logs

  API Gateway Logs           30 days               CloudWatch Logs

  CloudTrail Logs            90 days (S3)          S3 + CloudWatch

  CloudTrail (real-time)     30 days               CloudWatch Logs
  -----------------------------------------------------------------------

## Testing Strategy

### 1. Backend Unit Tests

**Framework**: pytest

**Test Files:** - `backend/tests/test_questions_handler.py` -
`backend/tests/test_evaluate_answer.py` -
`backend/tests/test_admin_create_user.py` -
`backend/tests/test_custom_metrics.py` (253 lines - comprehensive metrics testing)

**Example Test:**

    import json
    import os
    from unittest.mock import patch, MagicMock

    # Mock boto3 and environment before import
    mock_table = MagicMock()
    mock_dynamodb = MagicMock()
    mock_dynamodb.Table.return_value = mock_table

    with patch.dict(os.environ, {"TABLE_NAME": "test-table"}):
        with patch("boto3.resource", return_value=mock_dynamodb):
            from questions_handler import handler

    @patch('questions_handler.table')
    def test_get_all_questions(mock_table):
        # Arrange
        mock_table.scan.return_value = {
            'Items': [
                {
                    'id': '1',
                    'title': 'Test Question',
                    'difficulty': 'Easy',
                    'tags': {'Networking', 'Fundamentals'}
                }
            ]
        }

        # Act
        event = {"path": "/questions"}
        response = handler(event, {})

        # Assert
        assert response["statusCode"] == 200
        body = json.loads(response["body"])
        assert len(body) == 1
        assert body[0]["title"] == "Test Question"
        assert isinstance(body[0]["tags"], list)  # Set converted to list

    @patch('questions_handler.table')
    def test_question_not_found(mock_table):
        mock_table.get_item.return_value = {}

        event = {"path": "/questions/999"}
        response = handler(event, {})

        assert response["statusCode"] == 404

    @patch('questions_handler.table')
    def test_error_handling(mock_table):
        mock_table.scan.side_effect = Exception("DynamoDB error")

        event = {"path": "/questions"}
        response = handler(event, {})

        assert response["statusCode"] == 500

**Running Tests:**

    cd backend
    make build  # Runs: black --check, flake8, pytest

### 2. Integration Tests (Alpha)

**File**: `backend/tests/test_alpha_integration.py`

**Purpose**: Validate deployed API in Alpha environment

    import os
    import requests

    ALPHA_API_URL = os.environ.get("ALPHA_API_URL")

    def test_testing_endpoint():
        """Verify Alpha testing endpoint is accessible"""
        response = requests.get(f"{ALPHA_API_URL}testing")

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert data["message"] == "Hello from Lambda!"

    def test_unauthorized_access_to_questions():
        """Verify authentication is required for questions endpoint"""
        response = requests.get(f"{ALPHA_API_URL}questions")

        # Should return 401 Unauthorized without valid JWT token
        assert response.status_code == 401

**CI/CD Integration:**

    - name: Run integration tests against Alpha
      run: pytest tests/test_alpha_integration.py -v

### 3. Infrastructure Tests

**Framework**: Jest

**File**: `infrastructure/test/service-stack.test.ts`

    import * as cdk from 'aws-cdk-lib/core';
    import { Template } from 'aws-cdk-lib/assertions';
    import * as stacks from '../lib/stacks/stacks';

    test('DynamoDB Table Created', () => {
      const app = new cdk.App();
      const stack = new stacks.ServiceStack(app, 'TestStack', {
        environment: 'alpha',
      });

      const template = Template.fromStack(stack);

      // Assert DynamoDB table exists with correct properties
      template.hasResourceProperties('AWS::DynamoDB::Table', {
        BillingMode: 'PAY_PER_REQUEST',
        PointInTimeRecoverySpecification: {
          PointInTimeRecoveryEnabled: true,
        },
      });
    });

    test('Lambda Functions Have Correct Runtime', () => {
      const app = new cdk.App();
      const stack = new stacks.ServiceStack(app, 'TestStack', {
        environment: 'alpha',
      });

      const template = Template.fromStack(stack);

      template.hasResourceProperties('AWS::Lambda::Function', {
        Runtime: 'python3.11',
        Timeout: 30,
      });
    });

    test('Cognito User Pool Has Password Policy', () => {
      const app = new cdk.App();
      const stack = new stacks.ServiceStack(app, 'TestStack', {
        environment: 'alpha',
      });

      const template = Template.fromStack(stack);

      template.hasResourceProperties('AWS::Cognito::UserPool', {
        Policies: {
          PasswordPolicy: {
            MinimumLength: 8,
            RequireLowercase: true,
            RequireUppercase: true,
            RequireNumbers: true,
          },
        },
      });
    });

**Running Infrastructure Tests:**

    cd infrastructure
    npm test  # Runs Jest tests

### 4. Frontend Validation

**Linting:**

    cd frontend
    npm run lint  # ESLint

**Type Checking:**

    npm run check  # TypeScript compiler (tsc --noEmit)

**Build Validation:**

    npm run build  # Ensures production build succeeds

### 5. Security Testing (Trivy)

**Backend Dependencies:**

    trivy fs . --severity CRITICAL,HIGH --ignore-unfixed

**Frontend Dependencies:**

    trivy fs . --severity CRITICAL,HIGH --ignore-unfixed --skip-dirs backend,infrastructure

**CI/CD Integration:**

- Automated on every push to `main`

- Fails build on CRITICAL/HIGH vulnerabilities

- Separate scans for frontend and backend

## Deployment Evidence

### Production Deployment

**URLs:** - **Frontend**: https://apaps.people.aws.dev - **API**:
https://api.apaps.people.aws.dev

**CloudFormation Stack Outputs:**

    Stack: ServiceStack (Production)
    Region: eu-west-1
    Account: 431081169070

    Outputs:
    ├── UserPoolId: eu-west-1_XXXXXXXXX
    ├── UserPoolClientId: YYYYYYYYYYYYYYYYYYYYYYYY
    ├── FrontendBucketName: servicestack-frontendbucket-XXXXXX
    ├── CloudFrontDistributionId: E1234567890ABC
    ├── CloudFrontDomainName: d1234567890abc.cloudfront.net
    ├── WebsiteDomain: apaps.people.aws.dev
    ├── ApiDomain: api.apaps.people.aws.dev
    ├── ApiUrl: https://api.apaps.people.aws.dev/
    ├── QuestionsEndpoint: https://api.apaps.people.aws.dev/questions
    ├── SignupEndpoint: https://api.apaps.people.aws.dev/signup
    ├── EPAproject (DynamoDB Table): ServiceStack-InterviewQuestions-XXXX
    ├── CloudTrailBucketName: cloudtrail-logs-431081169070-eu-west-1
    └── DashboardUrl: https://console.aws.amazon.com/cloudwatch/...

### Alpha Deployment

**URLs:** - **Frontend**: https://alpha.apaps.people.aws.dev - **API**:
https://api.alpha.apaps.people.aws.dev - **Testing Endpoint**:
https://api.alpha.apaps.people.aws.dev/testing

**CloudFormation Stack Outputs:**

    Stack: ServiceStack (Alpha)
    Region: eu-west-1
    Account: 265870078323

    Outputs:
    ├── SubdomainNameServers: ns-1234.awsdns-56.org, ns-789.awsdns-01.com, ...
    └── (same structure as Production)

### CI/CD Deployment History

**GitHub Actions:**

     Workflow: Infra & Backend Deploy
       ├── backend-tests:  Passed
       ├── cdk-check:  Passed
       ├── deploy-alpha:  Deployed
       ├── integration-tests-alpha:  Passed
       └── deploy-prod:  Deployed (manual approval)

     Workflow: Frontend Deploy
       ├── deploy-alpha:  Deployed
       └── deploy-prod:  Deployed (manual approval)

### DNS Configuration

**Route 53 Hosted Zones:**

    Production (apaps.people.aws.dev):
    ├── Type: Public Hosted Zone
    ├── Delegation: Supernova (nova.aws.internal)
    ├── Records:
    │   ├── A (Alias) → CloudFront Distribution
    │   └── A api (Alias) → API Gateway Custom Domain

    Alpha (alpha.apaps.people.aws.dev):
    ├── Type: Public Hosted Zone
    ├── Delegation: NS records in production account
    ├── Records:
    │   ├── A (Alias) → CloudFront Distribution
    │   └── A api (Alias) → API Gateway Custom Domain

### SSL/TLS Certificates

**ACM Certificates:**

    Production:
    ├── apaps.people.aws.dev (us-east-1 for CloudFront)
    │   └── Status: Issued, Auto-renewal enabled
    └── api.apaps.people.aws.dev (eu-west-1 for API Gateway)
        └── Status: Issued, Auto-renewal enabled

    Alpha:
    ├── alpha.apaps.people.aws.dev (us-east-1 for CloudFront)
    │   └── Status: Issued, Auto-renewal enabled
    └── api.alpha.apaps.people.aws.dev (eu-west-1 for API Gateway)
        └── Status: Issued, Auto-renewal enabled

## File Structure Reference

    RoleReady/
    ├── .github/
    │   └── workflows/
    │       ├── frontend.yml                    # Frontend CI/CD
    │       └── infa-and-backend.yml           # Infrastructure & Backend CI/CD
    │
    ├── backend/
    │   ├── src/
    │   │   ├── __init__.py
    │   │   ├── questions_handler.py           # CRUD operations for questions
    │   │   ├── evaluate_answer.py             # Marcus AI evaluation
    │   │   ├── admin_create_user.py           # User signup handler
    │   │   └── custom_metrics.py              # Custom CloudWatch metrics
    │   ├── tests/
    │   │   ├── test_questions_handler.py      # Unit tests
    │   │   ├── test_evaluate_answer.py
    │   │   ├── test_admin_create_user.py
    │   │   ├── test_custom_metrics.py         # Metrics unit tests (253 lines)
    │   │   └── test_alpha_integration.py      # Integration tests
    │   ├── requirements.txt                   # Python dependencies
    │   └── Makefile                           # Build automation
    │
    ├── frontend/
    │   ├── src/
    │   │   ├── assets/
    │   │   ├── contexts/
    │   │   │   └── AuthContext.tsx            # Authentication state management
    │   │   ├── pages/
    │   │   │   ├── Home.tsx
    │   │   │   ├── Login.tsx
    │   │   │   ├── Signup.tsx
    │   │   │   ├── Questions.tsx              # Main questions interface
    │   │   │   └── ChangePassword.tsx
    │   │   ├── services/
    │   │   │   └── api.ts                     # API client
    │   │   ├── App.tsx                        # Main app component
    │   │   ├── main.tsx                       # Entry point
    │   │   └── aws-config.ts                  # Amplify configuration
    │   ├── public/
    │   ├── package.json                       # NPM dependencies
    │   ├── vite.config.ts                     # Vite build configuration
    │   └── tsconfig.json                      # TypeScript configuration
    │
    ├── infrastructure/
    │   ├── lib/
    │   │   ├── stacks/
    │   │   │   ├── service.ts                 # Main CDK stack
    │   │   │   └── stacks.ts                  # Stack exports
    │   │   └── app.ts                         # CDK app entry point
    │   ├── test/
    │   │   └── service-stack.test.ts          # Infrastructure tests
    │   ├── cdk.out/                           # CDK synthesized templates
    │   ├── package.json                       # NPM dependencies
    │   ├── tsconfig.json                      # TypeScript configuration
    │   └── cdk.json                           # CDK context configuration
    │
    ├── package.json                           # Root workspace configuration
    ├── README.md                              # Project README
    └── TECHNICAL_DOCUMENTATION.md             # This document

## Conclusion

This technical documentation provides comprehensive evidence of all
techniques and implementations used in the RoleReady (Interview Question
Bank) project. The application demonstrates:

**Modern Serverless Architecture**: Lambda, DynamoDB, API Gateway,
CloudFront **AI Integration**: AWS Bedrock (Claude 3.7 Sonnet) for
answer evaluation **Infrastructure as Code**: AWS CDK with TypeScript
for type-safe IaC **CI/CD Automation**: GitHub Actions with OIDC, Trivy
scanning, and multi-environment deployment **Security Best Practices**:
Cognito authentication, IAM least privilege, encryption, audit logging
**Monitoring & Observability**: CloudWatch alarms, dashboards, custom
business metrics (RoleReady namespace), structured logging, CloudTrail **Testing Strategy**: Unit tests,
integration tests, infrastructure tests, security scanning
**Multi-Environment**: Separate Alpha and Production accounts with
subdomain delegation

**Key Technologies:** - **Backend**: Python 3.11, AWS Lambda, boto3,
DynamoDB, Bedrock - **Frontend**: React 19, TypeScript, Vite, AWS
Amplify - **Infrastructure**: AWS CDK (TypeScript), CloudFormation -
**CI/CD**: GitHub Actions, Trivy, pytest, Jest - **Security**: Cognito,
IAM, ACM, CloudTrail, encryption - **Monitoring**: CloudWatch (custom
metrics in RoleReady namespace), SNS, structured logging

**Deployment Evidence:** - **Production**:
https://apaps.people.aws.dev - **Alpha**:
https://alpha.apaps.people.aws.dev - **CloudFormation Stacks**:
ServiceStack (both environments) - **CI/CD**: Automated deployments via
GitHub Actions - **Security**: Trivy scanning, OIDC authentication,
manual production approval

This documentation, combined with the source code in the repository,
provides comprehensive evidence of implementation for independent
assessment.
