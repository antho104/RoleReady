#!/usr/bin/env python3
"""
DynamoDB Table Transfer Script
Transfers all items from epa-prod table to role-ready-prod and role-ready-alpha tables.
"""

import boto3
import sys
from typing import List, Dict, Any
from botocore.exceptions import ClientError
from decimal import Decimal
import json


class DecimalEncoder(json.JSONEncoder):
    """Helper class to convert Decimal to float for JSON serialization"""
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)


def get_table_name(profile: str) -> str:
    """Get the DynamoDB table name from CloudFormation stack outputs"""
    try:
        session = boto3.Session(profile_name=profile)
        cfn_client = session.client('cloudformation')

        # Try to find the stack - adjust stack name if needed
        stack_names = [
            'RoleReadyServiceStack',
            'InterviewQuestionBankStack',
            'ServiceStack'
        ]

        for stack_name in stack_names:
            try:
                response = cfn_client.describe_stacks(StackName=stack_name)
                if response['Stacks']:
                    stack = response['Stacks'][0]
                    outputs = stack.get('Outputs', [])

                    # Look for table name in outputs
                    for output in outputs:
                        if 'table' in output.get('OutputKey', '').lower():
                            return output['OutputValue']

                    # If no specific table output, try to get from resources
                    resources = cfn_client.describe_stack_resources(StackName=stack_name)
                    for resource in resources['StackResources']:
                        if resource['ResourceType'] == 'AWS::DynamoDB::Table':
                            return resource['PhysicalResourceId']
            except ClientError:
                continue

        raise ValueError(f"Could not find DynamoDB table for profile {profile}")

    except Exception as e:
        print(f"Error getting table name for profile {profile}: {e}")
        raise


def scan_table(dynamodb_client, table_name: str) -> List[Dict[str, Any]]:
    """Scan entire DynamoDB table with pagination"""
    print(f"Scanning table '{table_name}'...")

    items = []
    scan_kwargs = {'TableName': table_name}

    try:
        while True:
            response = dynamodb_client.scan(**scan_kwargs)
            items.extend(response.get('Items', []))

            print(f"  Retrieved {len(response.get('Items', []))} items (total: {len(items)})")

            # Check if there are more items to scan
            last_evaluated_key = response.get('LastEvaluatedKey')
            if not last_evaluated_key:
                break

            scan_kwargs['ExclusiveStartKey'] = last_evaluated_key

        print(f"✓ Total items retrieved: {len(items)}")
        return items

    except ClientError as e:
        print(f"✗ Error scanning table: {e}")
        raise


def batch_write_items(dynamodb_client, table_name: str, items: List[Dict[str, Any]],
                      profile: str) -> None:
    """Write items to DynamoDB table in batches of 25 (AWS limit)"""
    print(f"\nWriting {len(items)} items to '{table_name}' (profile: {profile})...")

    if not items:
        print("  No items to write.")
        return

    batch_size = 25
    success_count = 0
    failed_count = 0

    try:
        for i in range(0, len(items), batch_size):
            batch = items[i:i + batch_size]

            # Prepare batch write request
            request_items = {
                table_name: [
                    {'PutRequest': {'Item': item}}
                    for item in batch
                ]
            }

            # Execute batch write with retry logic for unprocessed items
            unprocessed_items = request_items
            retries = 0
            max_retries = 5

            while unprocessed_items and retries < max_retries:
                try:
                    response = dynamodb_client.batch_write_item(
                        RequestItems=unprocessed_items
                    )

                    unprocessed_items = response.get('UnprocessedItems', {})

                    if unprocessed_items:
                        retries += 1
                        print(f"  Retry {retries}/{max_retries} for {len(unprocessed_items.get(table_name, []))} unprocessed items")
                        import time
                        time.sleep(2 ** retries)  # Exponential backoff
                    else:
                        success_count += len(batch)
                        print(f"  ✓ Batch {i//batch_size + 1}/{(len(items)-1)//batch_size + 1} written ({success_count}/{len(items)} items)")

                except ClientError as e:
                    print(f"  ✗ Error writing batch: {e}")
                    failed_count += len(batch)
                    break

            if retries >= max_retries and unprocessed_items:
                failed_count += len(unprocessed_items.get(table_name, []))
                print(f"  ✗ Failed to write {len(unprocessed_items.get(table_name, []))} items after {max_retries} retries")

        print(f"\n{'='*60}")
        print(f"Profile: {profile}")
        print(f"Table: {table_name}")
        print(f"Successfully written: {success_count} items")
        if failed_count > 0:
            print(f"Failed: {failed_count} items")
        print(f"{'='*60}\n")

    except Exception as e:
        print(f"✗ Error during batch write: {e}")
        raise


def verify_profiles_exist(source_profile: str, target_profiles: List[str]) -> None:
    """Verify that all AWS profiles exist"""
    print("Verifying AWS profiles...")
    session = boto3.Session()
    available_profiles = session.available_profiles

    all_profiles = [source_profile] + target_profiles
    for profile in all_profiles:
        if profile not in available_profiles:
            raise ValueError(f"AWS profile '{profile}' not found. Available profiles: {available_profiles}")
        print(f"  ✓ Profile '{profile}' exists")


def main():
    # Configuration
    SOURCE_PROFILE = 'epa-prod'
    TARGET_PROFILES = ['role-ready-prod', 'role-ready-alpha']

    print(f"""
{'='*60}
DynamoDB Table Transfer Script
{'='*60}
Source Profile: {SOURCE_PROFILE}
Target Profiles: {', '.join(TARGET_PROFILES)}
{'='*60}
""")

    try:
        # Verify profiles exist
        verify_profiles_exist(SOURCE_PROFILE, TARGET_PROFILES)

        # Get source table details
        print("\n1. Getting source table information...")
        source_session = boto3.Session(profile_name=SOURCE_PROFILE)
        source_dynamodb = source_session.client('dynamodb')
        source_table_name = get_table_name(SOURCE_PROFILE)
        print(f"  ✓ Source table: {source_table_name}")

        # Scan source table
        print("\n2. Scanning source table...")
        items = scan_table(source_dynamodb, source_table_name)

        if not items:
            print("\n⚠ No items found in source table. Nothing to transfer.")
            return 0

        # Preview first item
        print("\n3. Preview of first item:")
        print(f"  {json.dumps(items[0], indent=2, cls=DecimalEncoder)[:200]}...")

        # Confirm before proceeding
        response = input("\nProceed with transfer? (yes/no): ").strip().lower()
        if response != 'yes':
            print("Transfer cancelled.")
            return 0

        # Transfer to target profiles
        print("\n4. Transferring data to target profiles...")

        for target_profile in TARGET_PROFILES:
            try:
                target_session = boto3.Session(profile_name=target_profile)
                target_dynamodb = target_session.client('dynamodb')
                target_table_name = get_table_name(target_profile)

                print(f"\n  Target: {target_profile} -> {target_table_name}")
                batch_write_items(target_dynamodb, target_table_name, items, target_profile)

            except Exception as e:
                print(f"\n  ✗ Failed to transfer to {target_profile}: {e}")
                print(f"  Continuing with next profile...\n")
                continue

        print(f"\n{'='*60}")
        print("✓ Transfer completed!")
        print(f"{'='*60}\n")
        return 0

    except Exception as e:
        print(f"\n✗ Error: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
