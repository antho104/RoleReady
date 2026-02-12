#!/usr/bin/env node
import * as cdk from 'aws-cdk-lib/core';
import * as stacks from '../lib/stacks/stacks';

const app = new cdk.App();

// Get environment from environment variable (set in workflow or command line)
// Defaults to 'prod' for safety if not specified
const environment = (process.env.ENVIRONMENT || 'prod') as 'alpha' | 'prod';

// Get domain name from context
const domainName = app.node.tryGetContext('domainName');

// Get account and region from context (cdk.json)
const accounts = app.node.tryGetContext('accounts');
const regions = app.node.tryGetContext('regions');

// Allow environment variables to override cdk.json values
const account = process.env.CDK_DEFAULT_ACCOUNT || accounts?.[environment];
const region = process.env.CDK_DEFAULT_REGION || regions?.[environment] || 'eu-west-1';

if (!account) {
  console.error('\nERROR: AWS account not specified for environment:', environment);
  console.error('Please update infrastructure/cdk.json with your account IDs:\n');
  console.error('  "accounts": {');
  console.error('    "prod": "123456789012",');
  console.error('    "alpha": "987654321098"');
  console.error('  }\n');
  process.exit(1);
}

// Log the environment for deployment verification
console.log(`Deploying to ${environment.toUpperCase()} environment (account: ${account}, region: ${region})`);

// Optional: Get notification email from context or environment
const notificationEmail = app.node.tryGetContext('notificationEmail') || process.env.ALARM_NOTIFICATION_EMAIL;

const serviceStack = new stacks.ServiceStack(app, 'ServiceStack', {
  env: { account, region },
  enableMonitoring: true,
  notificationEmail: notificationEmail,
  environment: environment,
  domainName: domainName,
});
