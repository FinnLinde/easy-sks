"""Unit tests for the heuristic navigation evaluator."""

import pytest

from navigation.service.heuristic_navigation_evaluator import HeuristicNavigationEvaluator
from navigation.service.navigation_evaluator_port import NavigationEvaluationRequest


@pytest.fixture
def evaluator() -> HeuristicNavigationEvaluator:
    return HeuristicNavigationEvaluator()


_DEFAULT_KEYS = ["KaK = 286° [± 1°]", "d = 9,7 sm [± 0,2 sm]"]


def _request(student_answer: str, key_answers: list[str] | None = None) -> NavigationEvaluationRequest:
    return NavigationEvaluationRequest(
        context="Test context",
        sub_questions=["What is X?"],
        key_answers=_DEFAULT_KEYS if key_answers is None else key_answers,
        solution_text="Full solution text",
        student_answer=student_answer,
        max_score=2.0,
    )


@pytest.mark.asyncio
async def test_empty_answer_scores_zero(evaluator):
    result = await evaluator.evaluate(_request(""))
    assert result.score == 0.0
    assert result.is_correct is False


@pytest.mark.asyncio
async def test_matching_values_score_full(evaluator):
    result = await evaluator.evaluate(_request("KaK = 286 und d = 9,7"))
    assert result.score == 2.0
    assert result.is_correct is True


@pytest.mark.asyncio
async def test_partial_match_scores_proportionally(evaluator):
    result = await evaluator.evaluate(_request("KaK = 286"))
    assert result.score == 1.0
    assert result.is_correct is False


@pytest.mark.asyncio
async def test_no_match_scores_zero(evaluator):
    result = await evaluator.evaluate(_request("I have no idea"))
    assert result.score == 0.0


@pytest.mark.asyncio
async def test_no_key_answers_gives_half_score(evaluator):
    result = await evaluator.evaluate(_request("Some answer", key_answers=[]))
    assert result.score == 1.0
    assert result.is_correct is False
    assert "Musterlösung" in result.feedback
