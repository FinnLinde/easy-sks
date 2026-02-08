from uuid import UUID

from card.model.card_image import CardImage


class TestCardImageDefaults:
    def test_generates_valid_uuid(self):
        image = CardImage(storage_key="images/test.png")
        UUID(image.image_id)  # raises if not a valid UUID

    def test_default_alt_text_is_none(self):
        image = CardImage(storage_key="images/test.png")
        assert image.alt_text is None


class TestCardImageCustomValues:
    def test_custom_fields_are_preserved(self):
        image = CardImage(
            storage_key="images/photo.jpg",
            image_id="custom-id",
            alt_text="A photo",
        )

        assert image.storage_key == "images/photo.jpg"
        assert image.image_id == "custom-id"
        assert image.alt_text == "A photo"
