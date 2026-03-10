"""Unit tests for Stripe-status to internal-plan mapping."""

from billing.model.subscription import resolve_plan_for_status


def test_active_and_trialing_map_to_premium() -> None:
    assert resolve_plan_for_status("active") == "premium"
    assert resolve_plan_for_status("trialing") == "premium"


def test_non_premium_statuses_map_to_freemium() -> None:
    for status in [
        None,
        "past_due",
        "canceled",
        "unpaid",
        "incomplete",
        "incomplete_expired",
        "paused",
    ]:
        assert resolve_plan_for_status(status) == "freemium"
