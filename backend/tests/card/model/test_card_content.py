from card.model.card_content import CardContent
from card.model.card_image import CardImage


class TestCardContentDefaults:
    def test_default_text_is_empty(self):
        content = CardContent()
        assert content.text == ""

    def test_default_images_is_empty_list(self):
        content = CardContent()
        assert content.images == []

    def test_default_images_are_independent(self):
        a = CardContent()
        b = CardContent()
        a.images.append(CardImage(storage_key="x"))
        assert b.images == []


class TestCardContentCustomValues:
    def test_custom_text_is_preserved(self):
        content = CardContent(text="What is 2+2?")
        assert content.text == "What is 2+2?"

    def test_custom_images_are_preserved(self):
        img = CardImage(storage_key="images/diagram.png", alt_text="diagram")
        content = CardContent(text="Look at this:", images=[img])

        assert len(content.images) == 1
        assert content.images[0].storage_key == "images/diagram.png"
        assert content.images[0].alt_text == "diagram"
