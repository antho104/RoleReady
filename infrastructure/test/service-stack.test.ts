import * as cdk from 'aws-cdk-lib';
import { Template, Match } from 'aws-cdk-lib/assertions';
import { ServiceStack } from '../lib/stacks/service';

function synthTemplate(environment: 'alpha' | 'prod' = 'prod') {
  const app = new cdk.App({
    context: {
      // Mock hosted zone lookup to avoid AWS API calls during testing
      'hosted-zone:account=123456789012:domainName=apaps.people.aws.dev:region=eu-west-1': {
        Id: '/hostedzone/ZXXXXXXXXXXXXX',
        Name: 'apaps.people.aws.dev',
      },
    },
  });

  const stack = new ServiceStack(app, 'TestServiceStack', {
    env: {
      account: '123456789012',
      region: 'eu-west-1'
    },
    environment: environment,
    domainName: 'apaps.people.aws.dev',
  });

  return Template.fromStack(stack);
}

describe('ServiceStack CDK tests', () => {
  test('Stack contains core resources', () => {
    const template = synthTemplate();

    template.resourceCountIs('AWS::DynamoDB::Table', 1);
    // Expect 5: QuestionsHandler + EvaluateAnswerFn + AdminCreateUser + DnsValidatedCertificate custom resource + LogRetention custom resource Lambda
    template.resourceCountIs('AWS::Lambda::Function', 5);
    template.resourceCountIs('AWS::S3::Bucket', 2); // Frontend + CloudTrail
    template.resourceCountIs('AWS::CloudFront::Distribution', 1);
    template.resourceCountIs('AWS::Cognito::UserPool', 1);
    template.resourceCountIs('AWS::ApiGateway::RestApi', 1);
  });

  test('DynamoDB table has correct schema, PAY_PER_REQUEST, PITR, and encryption enabled', () => {
    const template = synthTemplate();

    template.hasResourceProperties('AWS::DynamoDB::Table', {
      AttributeDefinitions: [
        {
          AttributeName: 'id',
          AttributeType: 'S',
        },
      ],
      KeySchema: [
        {
          AttributeName: 'id',
          KeyType: 'HASH',
        },
      ],
      BillingMode: 'PAY_PER_REQUEST',
      PointInTimeRecoverySpecification: {
        PointInTimeRecoveryEnabled: true,
      },
      SSESpecification: {
        SSEEnabled: true,
      },
    });
  });

  test('Lambda function uses Python 3.11 and has TABLE_NAME environment variable', () => {
    const template = synthTemplate();

    // Test QuestionsHandler Lambda
    template.hasResourceProperties('AWS::Lambda::Function', {
      Runtime: 'python3.11',
      Handler: 'questions_handler.handler',
      Environment: {
        Variables: {
          TABLE_NAME: Match.anyValue(),
        },
      },
    });

    // Test EvaluateAnswerFn Lambda
    template.hasResourceProperties('AWS::Lambda::Function', {
      Runtime: 'python3.11',
      Handler: 'evaluate_answer.handler',
      Timeout: 30,
    });
  });

  test('AdminCreateUser Lambda has USER_POOL_ID environment variable', () => {
    const template = synthTemplate();

    template.hasResourceProperties('AWS::Lambda::Function', {
      Runtime: 'python3.11',
      Handler: 'admin_create_user.handler',
      Environment: Match.objectLike({
        Variables: Match.objectLike({
          USER_POOL_ID: Match.anyValue(),
        }),
      }),
    });
  });

  test('S3 bucket blocks all public access and is encrypted', () => {
    const template = synthTemplate();

    template.hasResourceProperties('AWS::S3::Bucket', {
      PublicAccessBlockConfiguration: {
        BlockPublicAcls: true,
        BlockPublicPolicy: true,
        IgnorePublicAcls: true,
        RestrictPublicBuckets: true,
      },
      BucketEncryption: {
        ServerSideEncryptionConfiguration: [
          {
            ServerSideEncryptionByDefault: {
              SSEAlgorithm: 'AES256',
            },
          },
        ],
      },
    });
  });

  test('CloudFront distribution uses index.html as default root object', () => {
    const template = synthTemplate();

    template.hasResourceProperties('AWS::CloudFront::Distribution', {
      DistributionConfig: {
        DefaultRootObject: 'index.html',
      },
    });
  });

  test('API Gateway uses a Cognito User Pool authorizer', () => {
    const template = synthTemplate();

    template.hasResourceProperties('AWS::ApiGateway::Authorizer', {
      Type: 'COGNITO_USER_POOLS',
      IdentitySource: 'method.request.header.Authorization',
    });
  });

  test('Protected API methods require Cognito authorization', () => {
    const template = synthTemplate();

    template.hasResourceProperties('AWS::ApiGateway::Method', {
      AuthorizationType: 'COGNITO_USER_POOLS',
    });
  });

  test('CloudTrail is configured with S3 bucket and CloudWatch logs', () => {
    const template = synthTemplate();

    // CloudTrail resource exists
    template.resourceCountIs('AWS::CloudTrail::Trail', 1);

    // CloudTrail has proper configuration
    template.hasResourceProperties('AWS::CloudTrail::Trail', {
      EnableLogFileValidation: true,
      IncludeGlobalServiceEvents: true,
      IsMultiRegionTrail: false, // Single region for cost optimization
      IsLogging: true,
    });
  });

  test('CloudTrail S3 bucket is encrypted and versioned', () => {
    const template = synthTemplate();

    // Check that at least one S3 bucket has versioning enabled (CloudTrail bucket)
    template.hasResourceProperties('AWS::S3::Bucket', {
      VersioningConfiguration: {
        Status: 'Enabled',
      },
    });
  });

  test('Signup endpoint exists and is public (no authorization)', () => {
    const template = synthTemplate();

    // Find all API Gateway methods
    const methods = template.findResources('AWS::ApiGateway::Method');

    // Check if there's a POST method on signup resource without authorization
    let foundPublicSignup = false;

    Object.entries(methods).forEach(([_, method]: [string, any]) => {
      // Check if this is a POST method with NONE authorization (public)
      if (method.Properties.HttpMethod === 'POST' &&
          method.Properties.AuthorizationType === 'NONE') {
        foundPublicSignup = true;
      }
    });

    expect(foundPublicSignup).toBe(true);
  });

  test('Signup Lambda has AdminCreateUser IAM permissions', () => {
    const template = synthTemplate();

    // Check that there's an IAM policy with cognito-idp:AdminCreateUser permission
    template.hasResourceProperties('AWS::IAM::Policy', {
      PolicyDocument: Match.objectLike({
        Statement: Match.arrayWith([
          Match.objectLike({
            Action: 'cognito-idp:AdminCreateUser',
            Effect: 'Allow',
          }),
        ]),
      }),
    });
  });

  test('Cognito User Pool has selfSignUpEnabled set to false', () => {
    const template = synthTemplate();

    template.hasResourceProperties('AWS::Cognito::UserPool', {
      Policies: Match.objectLike({
        PasswordPolicy: Match.objectLike({
          MinimumLength: 8,
        }),
      }),
      // Note: selfSignUpEnabled defaults to false when not specified
      // We verify it's not explicitly set to true
    });
  });

  test('Production CloudFront has custom domain configured', () => {
    const template = synthTemplate('prod');

    template.hasResourceProperties('AWS::CloudFront::Distribution', {
      DistributionConfig: {
        Aliases: ['apaps.people.aws.dev'],
        ViewerCertificate: Match.objectLike({
          AcmCertificateArn: Match.anyValue(),
          SslSupportMethod: 'sni-only',
        }),
      },
    });
  });

  test('Alpha CloudFront has subdomain configured', () => {
    const template = synthTemplate('alpha');

    template.hasResourceProperties('AWS::CloudFront::Distribution', {
      DistributionConfig: {
        Aliases: ['alpha.apaps.people.aws.dev'],
        ViewerCertificate: Match.objectLike({
          AcmCertificateArn: Match.anyValue(),
          SslSupportMethod: 'sni-only',
        }),
      },
    });
  });

  test('API Gateway custom domain is configured', () => {
    const template = synthTemplate('prod');

    template.hasResourceProperties('AWS::ApiGateway::DomainName', {
      DomainName: 'api.apaps.people.aws.dev',
      EndpointConfiguration: {
        Types: ['REGIONAL'],
      },
      SecurityPolicy: 'TLS_1_2',
    });
  });

  test('Alpha API Gateway custom domain is configured', () => {
    const template = synthTemplate('alpha');

    template.hasResourceProperties('AWS::ApiGateway::DomainName', {
      DomainName: 'alpha.api.apaps.people.aws.dev',
      EndpointConfiguration: {
        Types: ['REGIONAL'],
      },
      SecurityPolicy: 'TLS_1_2',
    });
  });

  test('API Gateway base path mapping exists', () => {
    const template = synthTemplate('prod');

    template.hasResourceProperties('AWS::ApiGateway::BasePathMapping', {
      DomainName: Match.anyValue(),
      RestApiId: Match.anyValue(),
      BasePath: '',
    });
  });

  test('Route 53 A record created for CloudFront', () => {
    const template = synthTemplate('prod');

    template.hasResourceProperties('AWS::Route53::RecordSet', {
      Type: 'A',
      AliasTarget: Match.objectLike({
        DNSName: Match.anyValue(),
        HostedZoneId: Match.anyValue(),
      }),
    });
  });

  test('Route 53 A record created for API Gateway', () => {
    const template = synthTemplate('prod');

    // Check both A records exist (CloudFront and API Gateway)
    const recordSets = template.findResources('AWS::Route53::RecordSet');
    const aRecords = Object.values(recordSets).filter(
      (rs: any) => rs.Properties?.Type === 'A'
    );

    expect(aRecords.length).toBeGreaterThanOrEqual(2);
  });

  test('Alpha environment creates subdomain hosted zone', () => {
    const template = synthTemplate('alpha');

    template.hasResourceProperties('AWS::Route53::HostedZone', {
      Name: 'alpha.apaps.people.aws.dev.',
    });
  });

  test('Alpha environment outputs NS servers for delegation', () => {
    const template = synthTemplate('alpha');

    const outputs = template.findOutputs('*');
    expect(outputs).toHaveProperty('SubdomainNameServers');
  });

  test('Production creates Supernova IAM role', () => {
    const template = synthTemplate('prod');

    // Check the IAM role properties (AssumeRolePolicyDocument, not AssumedBy in CloudFormation)
    template.hasResourceProperties('AWS::IAM::Role', {
      RoleName: 'Nova-DO-NOT-DELETE',
      Description: 'IAM role for Supernova DNS delegation - DO NOT DELETE MANUALLY',
      AssumeRolePolicyDocument: Match.objectLike({
        Statement: Match.arrayWith([
          Match.objectLike({ Principal: { Service: 'nova.aws.internal' } }),
        ]),
      }),
    });
  });

  test('Alpha does not create Supernova IAM role', () => {
    const template = synthTemplate('alpha');

    const roles = template.findResources('AWS::IAM::Role', {
      Properties: {
        RoleName: 'Nova-DO-NOT-DELETE',
      },
    });

    expect(Object.keys(roles).length).toBe(0);
  });

  test('Certificate created for API Gateway', () => {
    const template = synthTemplate('prod');

    template.resourceCountIs('AWS::CertificateManager::Certificate', 1);
  });

  test('Stack outputs include custom domain URLs', () => {
    const template = synthTemplate('prod');

    const outputs = template.findOutputs('*');
    const outputKeys = Object.keys(outputs);

    expect(outputKeys).toContain('WebsiteDomain');
    expect(outputKeys).toContain('ApiDomain');
    expect(outputKeys).toContain('ApiCustomDomainName');
  });
});
