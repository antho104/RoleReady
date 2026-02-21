"""
Questions Handler Lambda
Manages CRUD operations for interview questions in DynamoDB.

Endpoints:
- GET /questions - List all questions
- GET /questions/{id} - Get single question by ID
- POST /questions - Create new question
- PUT /questions/{id} - Update existing question
- DELETE /questions/{id} - Delete question
"""

import json
import logging
import os
import sys
from datetime import datetime, timezone
import uuid
import boto3

# Import custom metrics
from custom_metrics import QuestionsMetrics

# Configure JSON structured logging for CloudWatch
logger = logging.getLogger()
log_level = os.environ.get("LOG_LEVEL", "INFO")
logger.setLevel(getattr(logging, log_level))


# JSON formatter for structured logs
class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
        }

        # Add extra fields if present
        if hasattr(record, "request_id"):
            log_data["request_id"] = record.request_id
        if hasattr(record, "path"):
            log_data["path"] = record.path
        if hasattr(record, "method"):
            log_data["method"] = record.method
        if hasattr(record, "error_type"):
            log_data["error_type"] = record.error_type
        if hasattr(record, "question_id"):
            log_data["question_id"] = record.question_id
        if hasattr(record, "question_count"):
            log_data["question_count"] = record.question_count

        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data)


# Apply JSON formatter to handler
log_handler = logging.StreamHandler(sys.stdout)
log_handler.setFormatter(JsonFormatter())
logger.handlers = [log_handler]

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["TABLE_NAME"])


def convert_dynamodb_item(item):
    """
    Convert DynamoDB item to regular Python dict.
    Handles DynamoDB-specific types like sets.
    """
    if isinstance(item, dict):
        return {k: convert_dynamodb_item(v) for k, v in item.items()}
    elif isinstance(item, set):
        return list(item)
    else:
        return item


def get_user_groups(event):
    """
    Extract Cognito groups from the API Gateway event.

    Returns:
        List of group names the user belongs to (empty list if none)
    """
    try:
        claims = event.get("requestContext", {}).get("authorizer", {}).get("claims", {})
        groups_claim = claims.get("cognito:groups", "")

        if not groups_claim:
            return []

        # Groups can be comma-separated string or already a list
        if isinstance(groups_claim, str):
            return [g.strip() for g in groups_claim.split(",") if g.strip()]
        elif isinstance(groups_claim, list):
            return groups_claim

        return []
    except Exception as e:
        logger.warning(f"Failed to extract user groups: {str(e)}")
        return []


def is_admin(event):
    """
    Check if the authenticated user is an admin.

    Returns:
        True if user is in the Admin group, False otherwise
    """
    groups = get_user_groups(event)
    return "Admin" in groups


def require_admin(event):
    """
    Check admin access and return error response if not admin.

    Returns:
        None if user is admin, error response dict otherwise
    """
    if not is_admin(event):
        user_sub = (
            event.get("requestContext", {})
            .get("authorizer", {})
            .get("claims", {})
            .get("sub", "unknown")
        )
        logger.warning(f"Unauthorized admin access attempt by user: {user_sub}")

        return {
            "statusCode": 403,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Content-Type": "application/json",
            },
            "body": json.dumps(
                {
                    "error": "Forbidden",
                    "message": "Admin access required for this operation",
                }
            ),
        }

    return None


def handler(event, context):
    """
    Main Lambda handler for question operations.
    Routes requests based on HTTP method and path.
    """
    path = event["path"]
    method = event.get("httpMethod", "GET")
    request_id = context.aws_request_id if context else "local"

    # Create logger adapter with request context
    log_extra = {"request_id": request_id, "method": method, "path": path}

    import time

    start_time = time.time()

    logger.info("Incoming request", extra=log_extra)

    try:
        # List all questions
        if path == "/questions":
            if method == "GET":
                logger.info("Fetching all questions from DynamoDB", extra=log_extra)

                items = []
                response = table.scan()
                items.extend(response.get("Items", []))

                # Handle pagination
                while "LastEvaluatedKey" in response:
                    response = table.scan(
                        ExclusiveStartKey=response["LastEvaluatedKey"]
                    )
                    items.extend(response.get("Items", []))

                items = [convert_dynamodb_item(item) for item in items]

                # Emit custom metrics
                QuestionsMetrics.questions_retrieved(len(items))

                # Track API latency
                latency_ms = (time.time() - start_time) * 1000
                QuestionsMetrics.api_latency(latency_ms, "ListQuestions")

                logger.info(
                    "Successfully retrieved questions",
                    extra={**log_extra, "question_count": len(items)},
                )

                return {
                    "statusCode": 200,
                    "headers": {"Access-Control-Allow-Origin": "*"},
                    "body": json.dumps(items),
                }

            elif method == "POST":
                # Check admin access
                admin_check = require_admin(event)
                if admin_check:
                    return admin_check

                # Create new question
                body = json.loads(event.get("body", "{}"))

                # Validate required fields
                required_fields = ["question", "category"]
                required_fields = ["question_text", "category", "difficulty"]
                for field in required_fields:
                    if field not in body:
                        return {
                            "statusCode": 400,
                            "headers": {"Access-Control-Allow-Origin": "*"},
                            "body": json.dumps(
                                {"error": f"Missing required field: {field}"}
                            ),
                        }

                # Generate ID and create item
                question_id = str(uuid.uuid4())
                item = {
                    "id": question_id,
                    "question_text": body["question_text"],
                    "category": body["category"],
                    "difficulty": body["difficulty"],
                    "reference_answer": body.get("reference_answer", ""),
                    "created_at": datetime.now(timezone.utc).isoformat(),
                }

                table.put_item(Item=item)

                logger.info(
                    "Question created", extra={**log_extra, "question_id": question_id}
                )

                return {
                    "statusCode": 201,
                    "headers": {"Access-Control-Allow-Origin": "*"},
                    "body": json.dumps(item),
                }

        # Get single question by ID
        elif path.startswith("/questions/"):
            question_id = path.split("/")[-1]

            if method == "GET":
                logger.info(
                    "Fetching single question",
                    extra={**log_extra, "question_id": question_id},
                )

                response = table.get_item(Key={"id": question_id})

                if "Item" in response:
                    item = convert_dynamodb_item(response["Item"])

                    # Emit custom metrics for question view
                    category = item.get("category", "Unknown")
                    QuestionsMetrics.question_viewed(question_id, category)

                    latency_ms = (time.time() - start_time) * 1000
                    QuestionsMetrics.api_latency(latency_ms, "GetQuestion")

                    logger.info(
                        "Question found",
                        extra={**log_extra, "question_id": question_id},
                    )
                    return {
                        "statusCode": 200,
                        "headers": {"Access-Control-Allow-Origin": "*"},
                        "body": json.dumps(item),
                    }

                # Track 404 errors
                QuestionsMetrics.question_not_found()

                logger.warning(
                    "Question not found",
                    extra={**log_extra, "question_id": question_id},
                )
                return {
                    "statusCode": 404,
                    "headers": {"Access-Control-Allow-Origin": "*"},
                    "body": json.dumps({"error": "Not found"}),
                }

            elif method == "PUT":
                # Check admin access
                admin_check = require_admin(event)
                if admin_check:
                    return admin_check

                # Update existing question
                body = json.loads(event.get("body", "{}"))

                # Check if question exists
                response = table.get_item(Key={"id": question_id})
                if "Item" not in response:
                    return {
                        "statusCode": 404,
                        "headers": {"Access-Control-Allow-Origin": "*"},
                        "body": json.dumps({"error": "Question not found"}),
                    }

                # Build update expression
                update_fields = ["question_text", "category", "difficulty", "reference_answer"]
                update_expr = "SET " + ", ".join(
                    [f"#{f} = :{f}" for f in update_fields if f in body]
                )
                expr_attr_names = {f"#{f}": f for f in update_fields if f in body}
                expr_attr_values = {
                    f":{f}": body[f] for f in update_fields if f in body
                }

                if not expr_attr_values:
                    return {
                        "statusCode": 400,
                        "headers": {"Access-Control-Allow-Origin": "*"},
                        "body": json.dumps({"error": "No fields to update"}),
                    }

                table.update_item(
                    Key={"id": question_id},
                    UpdateExpression=update_expr,
                    ExpressionAttributeNames=expr_attr_names,
                    ExpressionAttributeValues=expr_attr_values,
                )

                # Fetch updated item
                updated = table.get_item(Key={"id": question_id})

                logger.info(
                    "Question updated", extra={**log_extra, "question_id": question_id}
                )
                return {
                    "statusCode": 200,
                    "headers": {"Access-Control-Allow-Origin": "*"},
                    "body": json.dumps(convert_dynamodb_item(updated["Item"])),
                }

            elif method == "DELETE":
                # Check admin access
                admin_check = require_admin(event)
                if admin_check:
                    return admin_check

                # TODO: Implement delete question logic
                logger.info(
                    "Deleting question",
                    extra={**log_extra, "question_id": question_id},
                )

                table.delete_item(Key={"id": question_id})

                return {
                    "statusCode": 204,
                    "headers": {"Access-Control-Allow-Origin": "*"},
                    "body": "",
                }

        # Default response
        else:
            logger.info("Fallback route accessed", extra=log_extra)
            return {
                "statusCode": 200,
                "headers": {"Access-Control-Allow-Origin": "*"},
                "body": json.dumps({"message": "Hello from Lambda!"}),
            }

    except Exception as e:
        logger.error(
            "Error processing request",
            extra={
                **log_extra,
                "error_type": type(e).__name__,
            },
            exc_info=True,
        )

        return {
            "statusCode": 500,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"error": str(e)}),
        }
