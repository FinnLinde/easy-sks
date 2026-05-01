from uuid import UUID

from card.model.card import Card
from card.model.card_content import CardContent
from card.model.card_image import CardImage


class TestCardDefaults:
    def test_generates_valid_uuid(self):
        card = Card()
        UUID(card.card_id)  # raises if not a valid UUID

    def test_default_front_is_empty_content(self):
        card = Card()
        assert card.front.text == ""
        assert card.front.images == []

    def test_default_answer_is_empty_content(self):
        card = Card()
        assert card.answer.text == ""
        assert card.answer.images == []

    def test_default_short_answer_is_empty_list(self):
        card = Card()
        assert card.short_answer == []

    def test_default_tags_is_empty_list(self):
        card = Card()
        assert card.tags == []

    def test_default_tags_are_independent(self):
        a = Card()
        b = Card()
        a.tags.append("math")
        assert b.tags == []


class TestCardCustomValues:
    def test_custom_fields_are_preserved(self):
        front_img = CardImage(storage_key="front.png")
        front = CardContent(text="What is this?", images=[front_img])
        answer = CardContent(text="It is a cat.")
        short_answer = ["Cat", "Feline animal"]

        card = Card(
            card_id="custom-id",
            front=front,
            answer=answer,
            short_answer=short_answer,
            tags=["animals", "biology"],
        )

        assert card.card_id == "custom-id"
        assert card.front.text == "What is this?"
        assert len(card.front.images) == 1
        assert card.answer.text == "It is a cat."
        assert card.short_answer == ["Cat", "Feline animal"]
        assert card.tags == ["animals", "biology"]
