"""
Unit tests for admin authorization in questions_handler
"""

import json
import os
from unittest.mock import patch, MagicMock

# Mock boto3 and environment before import
mock_table = MagicMock()
mock_dynamodb = MagicMock()
mock_dynamodb.Table.return_value = mock_table

with patch.dict(
    os.environ,
    {"TABLE_NAME": "test-table", "LOG_LEVEL": "INFO", "AWS_DEFAULT_REGION": "us-east-1"},
):
    with patch("boto3.resource", return_value=mock_dynamodb):
        from questions_handler import (
            handler,
            get_user_groups,
            is_admin,
            require_admin,
        )


def create_event(method, path, body=None, groups=None):
    """Helper to create API Gateway event with Cognito claims"""
    event = {
        "httpMethod": method,
        "path": path,
        "headers": {},
        "requestContext": {
            "authorizer": {
                "claims": {
                    "sub": "test-user-123",
                    "email": "test@example.com",
                    "cognito:username": "testuser",
                }
            }
        },
    }

    if body:
        event["body"] = json.dumps(body)

    if groups:
        event["requestContext"]["authorizer"]["claims"]["cognito:groups"] = groups

    return event


def test_get_user_groups_single_group():
    """Test extracting single group from event"""
    event = create_event("GET", "/questions", groups="Admin")
    groups = get_user_groups(event)
    assert groups == ["Admin"]


def test_get_user_groups_multiple_groups():
    """Test extracting multiple groups from comma-separated string"""
    event = create_event("GET", "/questions", groups="Admin,Users,Moderators")
    groups = get_user_groups(event)
    assert set(groups) == {"Admin", "Users", "Moderators"}


def test_get_user_groups_list():
    """Test extracting groups when already a list"""
    event = create_event("GET", "/questions", groups=["Admin", "Users"])
    groups = get_user_groups(event)
    assert groups == ["Admin", "Users"]


def test_get_user_groups_no_groups():
    """Test when user has no groups"""
    event = create_event("GET", "/questions")
    groups = get_user_groups(event)
    assert groups == []


def test_is_admin_true():
    """Test is_admin returns True for admin user"""
    event = create_event("GET", "/questions", groups="Admin,Users")
    assert is_admin(event) is True


def test_is_admin_false():
    """Test is_admin returns False for non-admin user"""
    event = create_event("GET", "/questions", groups="Users,Moderators")
    assert is_admin(event) is False


def test_is_admin_no_groups():
    """Test is_admin returns False when user has no groups"""
    event = create_event("GET", "/questions")
    assert is_admin(event) is False


def test_require_admin_allows_admin():
    """Test require_admin allows admin users"""
    event = create_event("DELETE", "/questions/123", groups="Admin")
    result = require_admin(event)
    assert result is None


def test_require_admin_blocks_non_admin():
    """Test require_admin blocks non-admin users"""
    event = create_event("DELETE", "/questions/123", groups="Users")
    result = require_admin(event)

    assert result is not None
    assert result["statusCode"] == 403
    assert "Forbidden" in result["body"]


def test_require_admin_blocks_no_group():
    """Test require_admin blocks users with no groups"""
    event = create_event("DELETE", "/questions/123")
    result = require_admin(event)

    assert result is not None
    assert result["statusCode"] == 403


def test_post_question_as_admin():
    """Test POST question succeeds for admin"""
    mock_table.put_item.return_value = {}

    event = create_event(
        "POST",
        "/questions",
        body={"question": "What is AWS?", "category": "AWS", "competency_type": "Technical", "answer": "Cloud platform"},
        groups="Admin"
    )

    context = MagicMock()
    context.aws_request_id = "test-request-123"

    response = handler(event, context)

    assert response["statusCode"] == 201
    body = json.loads(response["body"])
    assert "id" in body
    assert body["question"] == "What is AWS?"


def test_post_question_as_non_admin():
    """Test POST question fails for non-admin"""
    event = create_event(
        "POST",
        "/questions",
        body={"question": "What is AWS?", "category": "AWS", "competency_type": "Technical"},
        groups="Users"
    )

    context = MagicMock()
    context.aws_request_id = "test-request-123"

    response = handler(event, context)

    assert response["statusCode"] == 403
    assert "Forbidden" in response["body"]


def test_put_question_as_admin():
    """Test PUT question succeeds for admin"""
    mock_table.get_item.return_value = {
        "Item": {"id": "123", "question": "Old question", "category": "AWS", "competency_type": "Technical"}
    }
    mock_table.update_item.return_value = {}

    event = create_event(
        "PUT",
        "/questions/123",
        body={"question": "Updated question"},
        groups="Admin"
    )

    context = MagicMock()
    context.aws_request_id = "test-request-123"

    response = handler(event, context)

    assert response["statusCode"] == 200


def test_put_question_as_non_admin():
    """Test PUT question fails for non-admin"""
    event = create_event(
        "PUT",
        "/questions/123",
        body={"question": "Updated question"},
        groups="Users"
    )

    context = MagicMock()
    context.aws_request_id = "test-request-123"

    response = handler(event, context)

    assert response["statusCode"] == 403


def test_delete_question_as_admin():
    """Test DELETE question succeeds for admin"""
    mock_table.delete_item.return_value = {}

    event = create_event("DELETE", "/questions/123", groups="Admin")

    context = MagicMock()
    context.aws_request_id = "test-request-123"

    response = handler(event, context)

    assert response["statusCode"] == 204


def test_delete_question_as_non_admin():
    """Test DELETE question fails for non-admin"""
    event = create_event("DELETE", "/questions/123", groups="Users")

    context = MagicMock()
    context.aws_request_id = "test-request-123"

    response = handler(event, context)

    assert response["statusCode"] == 403


def test_get_question_allows_all_users():
    """Test GET question works for any authenticated user (not just admins)"""
    mock_table.get_item.return_value = {
        "Item": {"id": "123", "question": "Test question", "category": "AWS", "competency_type": "Technical"}
    }

    # Non-admin user
    event = create_event("GET", "/questions/123", groups="Users")

    context = MagicMock()
    context.aws_request_id = "test-request-123"

    response = handler(event, context)

    assert response["statusCode"] == 200


def test_post_question_missing_required_fields():
    """Test POST question fails with missing required fields"""
    event = create_event(
        "POST",
        "/questions",
        body={"question": "What is AWS?"},  # Missing category and competency_type
        groups="Admin"
    )

    context = MagicMock()
    context.aws_request_id = "test-request-123"

    response = handler(event, context)

    assert response["statusCode"] == 400
    assert "Missing required field" in response["body"]
