"""
Unit tests for custom CloudWatch metrics module
"""

import pytest
from unittest.mock import Mock, patch, call
from custom_metrics import (
    emit_metric,
    QuestionsMetrics,
    EvaluationMetrics,
    SystemMetrics,
    NAMESPACE
)


@patch('custom_metrics.cloudwatch')
def test_emit_metric_basic(mock_cloudwatch):
    """Test basic metric emission"""
    emit_metric('TestMetric', 42.0, 'Count')

    mock_cloudwatch.put_metric_data.assert_called_once()
    call_args = mock_cloudwatch.put_metric_data.call_args

    assert call_args[1]['Namespace'] == NAMESPACE
    assert call_args[1]['MetricData'][0]['MetricName'] == 'TestMetric'
    assert call_args[1]['MetricData'][0]['Value'] == 42.0
    assert call_args[1]['MetricData'][0]['Unit'] == 'Count'


@patch('custom_metrics.cloudwatch')
def test_emit_metric_with_dimensions(mock_cloudwatch):
    """Test metric emission with dimensions"""
    dimensions = [{'Name': 'Category', 'Value': 'AWS'}]
    emit_metric('TestMetric', 1, 'Count', dimensions)

    call_args = mock_cloudwatch.put_metric_data.call_args
    assert call_args[1]['MetricData'][0]['Dimensions'] == dimensions


@patch('custom_metrics.cloudwatch')
def test_emit_metric_handles_errors(mock_cloudwatch):
    """Test that metric errors don't crash the function"""
    mock_cloudwatch.put_metric_data.side_effect = Exception("CloudWatch error")

    # Should not raise exception
    emit_metric('TestMetric', 1, 'Count')


@patch('custom_metrics.emit_metric')
def test_questions_retrieved(mock_emit):
    """Test QuestionsRetrieved metric"""
    QuestionsMetrics.questions_retrieved(15)

    mock_emit.assert_called_once_with('QuestionsRetrieved', 15, 'Count')


@patch('custom_metrics.emit_metric')
def test_question_viewed(mock_emit):
    """Test QuestionViewed metric with category"""
    QuestionsMetrics.question_viewed('q123', 'AWS')

    mock_emit.assert_called_once_with(
        'QuestionViewed',
        1,
        'Count',
        [{'Name': 'Category', 'Value': 'AWS'}]
    )


@patch('custom_metrics.emit_metric')
def test_question_viewed_no_category(mock_emit):
    """Test QuestionViewed metric without category"""
    QuestionsMetrics.question_viewed('q123')

    mock_emit.assert_called_once_with('QuestionViewed', 1, 'Count', [])


@patch('custom_metrics.emit_metric')
def test_question_not_found(mock_emit):
    """Test QuestionNotFound metric"""
    QuestionsMetrics.question_not_found()

    mock_emit.assert_called_once_with('QuestionNotFound', 1, 'Count')


@patch('custom_metrics.emit_metric')
def test_api_latency(mock_emit):
    """Test APILatency metric"""
    QuestionsMetrics.api_latency(150.5, 'GetQuestion')

    mock_emit.assert_called_once_with(
        'APILatency',
        150.5,
        'Milliseconds',
        [{'Name': 'Operation', 'Value': 'GetQuestion'}]
    )


@patch('custom_metrics.emit_metric')
def test_search_performed(mock_emit):
    """Test SearchPerformed metric"""
    QuestionsMetrics.search_performed(23)

    # Should emit two metrics
    assert mock_emit.call_count == 2
    calls = mock_emit.call_args_list

    # First call: SearchPerformed
    assert calls[0] == call('SearchPerformed', 1, 'Count')
    # Second call: SearchResultCount
    assert calls[1] == call('SearchResultCount', 23, 'Count')


@patch('custom_metrics.emit_metric')
def test_answer_evaluated(mock_emit):
    """Test AnswerEvaluated metric with all sub-metrics"""
    EvaluationMetrics.answer_evaluated(
        score=85,
        competency_type='AWS',
        is_correct=True
    )

    # Should emit 4 metrics
    assert mock_emit.call_count == 4
    calls = mock_emit.call_args_list

    # Check each metric
    assert calls[0] == call('AnswerEvaluated', 1, 'Count')
    assert calls[1] == call('EvaluationScore', 85, 'None')
    assert calls[2] == call(
        'EvaluationByCompetency',
        1,
        'Count',
        [{'Name': 'CompetencyType', 'Value': 'AWS'}]
    )
    assert calls[3] == call(
        'AnswerCorrectness',
        1,
        'Count',
        [{'Name': 'IsCorrect', 'Value': 'True'}]
    )


@patch('custom_metrics.emit_metric')
def test_evaluation_success(mock_emit):
    """Test EvaluationSuccess metric"""
    EvaluationMetrics.evaluation_success()

    mock_emit.assert_called_once_with('EvaluationSuccess', 1, 'Count')


@patch('custom_metrics.emit_metric')
def test_evaluation_failure(mock_emit):
    """Test EvaluationFailure metric with error type"""
    EvaluationMetrics.evaluation_failure('JSONDecodeError')

    mock_emit.assert_called_once_with(
        'EvaluationFailure',
        1,
        'Count',
        [{'Name': 'ErrorType', 'Value': 'JSONDecodeError'}]
    )


@patch('custom_metrics.emit_metric')
def test_ai_response_time(mock_emit):
    """Test MarcusResponseTime metric"""
    EvaluationMetrics.ai_response_time(2543.7)

    mock_emit.assert_called_once_with('MarcusResponseTime', 2543.7, 'Milliseconds')


@patch('custom_metrics.emit_metric')
def test_user_engagement_high(mock_emit):
    """Test UserEngagement metric - High level"""
    EvaluationMetrics.user_engagement(85)

    mock_emit.assert_called_once_with(
        'UserEngagement',
        1,
        'Count',
        [{'Name': 'EngagementLevel', 'Value': 'High'}]
    )


@patch('custom_metrics.emit_metric')
def test_user_engagement_medium(mock_emit):
    """Test UserEngagement metric - Medium level"""
    EvaluationMetrics.user_engagement(65)

    mock_emit.assert_called_once_with(
        'UserEngagement',
        1,
        'Count',
        [{'Name': 'EngagementLevel', 'Value': 'Medium'}]
    )


@patch('custom_metrics.emit_metric')
def test_user_engagement_low(mock_emit):
    """Test UserEngagement metric - Low level"""
    EvaluationMetrics.user_engagement(30)

    mock_emit.assert_called_once_with(
        'UserEngagement',
        1,
        'Count',
        [{'Name': 'EngagementLevel', 'Value': 'Low'}]
    )


@patch('custom_metrics.emit_metric')
def test_user_engagement_boundaries(mock_emit):
    """Test UserEngagement boundaries"""
    # Test score 80 (should be High)
    EvaluationMetrics.user_engagement(80)
    assert mock_emit.call_args[0][3][0]['Value'] == 'High'

    mock_emit.reset_mock()

    # Test score 50 (should be Medium)
    EvaluationMetrics.user_engagement(50)
    assert mock_emit.call_args[0][3][0]['Value'] == 'Medium'

    mock_emit.reset_mock()

    # Test score 49 (should be Low)
    EvaluationMetrics.user_engagement(49)
    assert mock_emit.call_args[0][3][0]['Value'] == 'Low'


@patch('custom_metrics.emit_metric')
def test_cold_start(mock_emit):
    """Test ColdStart metric"""
    SystemMetrics.cold_start()

    mock_emit.assert_called_once_with('ColdStart', 1, 'Count')


@patch('custom_metrics.emit_metric')
def test_memory_usage(mock_emit):
    """Test MemoryUsage metric"""
    SystemMetrics.memory_usage(128.5)

    mock_emit.assert_called_once_with('MemoryUsage', 128.5, 'Megabytes')


@patch('custom_metrics.emit_metric')
def test_concurrent_executions(mock_emit):
    """Test ConcurrentExecutions metric"""
    SystemMetrics.concurrent_executions(5)

    mock_emit.assert_called_once_with('ConcurrentExecutions', 5, 'Count')
