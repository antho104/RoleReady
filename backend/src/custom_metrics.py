"""
Custom CloudWatch Metrics Module
Emits business-specific metrics for RoleReady application monitoring.

Metrics tracked:
- Questions retrieval and viewing patterns
- AI evaluation usage and success rates
- User engagement metrics
- System performance indicators
"""

import boto3
import logging
from datetime import datetime
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)
cloudwatch = boto3.client("cloudwatch")

# Namespace for all RoleReady custom metrics
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
        dimensions: Optional list of dimension dicts [{'Name': 'x', 'Value': 'y'}]
    """
    try:
        metric_data = {
            "MetricName": metric_name,
            "Value": value,
            "Unit": unit,
            "Timestamp": datetime.utcnow(),
        }

        if dimensions:
            metric_data["Dimensions"] = dimensions

        cloudwatch.put_metric_data(Namespace=NAMESPACE, MetricData=[metric_data])

        logger.info(f"Emitted metric: {metric_name}={value} {unit}")

    except Exception as e:
        # Don't fail the Lambda if metrics fail
        logger.warning(f"Failed to emit metric {metric_name}: {str(e)}")


class QuestionsMetrics:
    """Metrics for questions_handler Lambda"""

    @staticmethod
    def questions_retrieved(count: int) -> None:
        """Track number of questions retrieved in a single request"""
        emit_metric("QuestionsRetrieved", count, "Count")

    @staticmethod
    def question_viewed(question_id: str, category: Optional[str] = None) -> None:
        """Track individual question views"""
        dimensions = []
        if category:
            dimensions.append({"Name": "Category", "Value": category})

        emit_metric("QuestionViewed", 1, "Count", dimensions)

    @staticmethod
    def question_not_found() -> None:
        """Track 404 errors for questions"""
        emit_metric("QuestionNotFound", 1, "Count")

    @staticmethod
    def api_latency(latency_ms: float, operation: str) -> None:
        """Track API operation latency"""
        dimensions = [{"Name": "Operation", "Value": operation}]
        emit_metric("APILatency", latency_ms, "Milliseconds", dimensions)

    @staticmethod
    def search_performed(result_count: int) -> None:
        """Track search operations and result counts"""
        emit_metric("SearchPerformed", 1, "Count")
        emit_metric("SearchResultCount", result_count, "Count")


class EvaluationMetrics:
    """Metrics for evaluate_answer Lambda (Marcus AI)"""

    @staticmethod
    def answer_evaluated(score: int, competency_type: str, is_correct: bool) -> None:
        """Track answer evaluations with score and competency breakdown"""
        # Overall evaluation count
        emit_metric("AnswerEvaluated", 1, "Count")

        # Score tracking
        emit_metric("EvaluationScore", score, "None")

        # Competency breakdown
        dimensions = [{"Name": "CompetencyType", "Value": competency_type}]
        emit_metric("EvaluationByCompetency", 1, "Count", dimensions)

        # Correctness tracking
        correctness_dim = [{"Name": "IsCorrect", "Value": str(is_correct)}]
        emit_metric("AnswerCorrectness", 1, "Count", correctness_dim)

    @staticmethod
    def evaluation_success() -> None:
        """Track successful evaluations"""
        emit_metric("EvaluationSuccess", 1, "Count")

    @staticmethod
    def evaluation_failure(error_type: str) -> None:
        """Track failed evaluations with error type"""
        dimensions = [{"Name": "ErrorType", "Value": error_type}]
        emit_metric("EvaluationFailure", 1, "Count", dimensions)

    @staticmethod
    def ai_response_time(duration_ms: float) -> None:
        """Track Marcus AI response latency"""
        emit_metric("MarcusResponseTime", duration_ms, "Milliseconds")

    @staticmethod
    def user_engagement(score: int) -> None:
        """
        Track user engagement level based on score ranges.
        High: 80-100, Medium: 50-79, Low: 0-49
        """
        if score >= 80:
            level = "High"
        elif score >= 50:
            level = "Medium"
        else:
            level = "Low"

        dimensions = [{"Name": "EngagementLevel", "Value": level}]
        emit_metric("UserEngagement", 1, "Count", dimensions)


class SystemMetrics:
    """System-wide metrics"""

    @staticmethod
    def cold_start() -> None:
        """Track Lambda cold starts"""
        emit_metric("ColdStart", 1, "Count")

    @staticmethod
    def memory_usage(memory_mb: float) -> None:
        """Track Lambda memory usage"""
        emit_metric("MemoryUsage", memory_mb, "Megabytes")

    @staticmethod
    def concurrent_executions(count: int) -> None:
        """Track concurrent Lambda executions"""
        emit_metric("ConcurrentExecutions", count, "Count")
