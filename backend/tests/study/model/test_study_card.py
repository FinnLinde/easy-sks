import pytest

from card.model.card import Card
from card.model.card_content import CardContent
from scheduling.model.card_scheduling_info import CardSchedulingInfo

from study.model.study_card import StudyCard


class TestStudyCardConstruction:
    def test_combines_card_and_scheduling_info(self):
        card = Card(
            card_id="card-1",
            front=CardContent(text="What is a peilung?"),
            answer=CardContent(text="A bearing measurement."),
            short_answer=CardContent(text="Bearing"),
            tags=["navigation"],
        )
        info = CardSchedulingInfo(card_id="card-1")

        study_card = StudyCard(card=card, scheduling_info=info)

        assert study_card.card.card_id == "card-1"
        assert study_card.scheduling_info.card_id == "card-1"
        assert study_card.card.front.text == "What is a peilung?"


class TestStudyCardFrozen:
    def test_cannot_replace_card(self):
        study_card = StudyCard(
            card=Card(card_id="c1"),
            scheduling_info=CardSchedulingInfo(card_id="c1"),
        )

        with pytest.raises(AttributeError):
            study_card.card = Card(card_id="c2")  # type: ignore[misc]

    def test_cannot_replace_scheduling_info(self):
        study_card = StudyCard(
            card=Card(card_id="c1"),
            scheduling_info=CardSchedulingInfo(card_id="c1"),
        )

        with pytest.raises(AttributeError):
            study_card.scheduling_info = CardSchedulingInfo(card_id="c2")  # type: ignore[misc]
