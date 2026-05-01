from card.model.card_content import CardContent
from card.model.card_image import CardImage
from card.service.card_service import CardService


class FakeImageStorage:
    """In-memory fake implementing ImageStoragePort for testing."""

    def __init__(self) -> None:
        self.stored: dict[str, bytes] = {}
        self._counter = 0

    def upload(self, image_data: bytes, content_type: str) -> str:
        key = f"images/{self._counter}.{content_type.split('/')[-1]}"
        self._counter += 1
        self.stored[key] = image_data
        return key

    def get_url(self, storage_key: str) -> str:
        return f"https://cdn.example.com/{storage_key}"

    def delete(self, storage_key: str) -> None:
        self.stored.pop(storage_key, None)


class TestCreateCard:
    def test_returns_card_with_given_content(self):
        service = CardService(image_storage=FakeImageStorage())
        front = CardContent(text="Q?")
        answer = CardContent(text="A.")
        short_answer = ["A", "Short"]

        card = service.create_card(front, answer, short_answer, tags=["test"])

        assert card.front.text == "Q?"
        assert card.answer.text == "A."
        assert card.short_answer == ["A", "Short"]
        assert card.tags == ["test"]

    def test_generates_card_id(self):
        service = CardService(image_storage=FakeImageStorage())
        card = service.create_card(CardContent(), CardContent())

        assert card.card_id  # non-empty

    def test_tags_default_to_empty_list(self):
        service = CardService(image_storage=FakeImageStorage())
        card = service.create_card(CardContent(), CardContent())

        assert card.tags == []

    def test_short_answer_defaults_to_empty_list(self):
        service = CardService(image_storage=FakeImageStorage())
        card = service.create_card(CardContent(), CardContent())

        assert card.short_answer == []


class TestAddImageToContent:
    def test_appends_image_to_content(self):
        storage = FakeImageStorage()
        service = CardService(image_storage=storage)
        content = CardContent(text="Look:")

        updated = service.add_image_to_content(
            content, b"png-bytes", "image/png"
        )

        assert len(updated.images) == 1
        assert updated.images[0].storage_key == "images/0.png"

    def test_preserves_existing_images(self):
        storage = FakeImageStorage()
        service = CardService(image_storage=storage)
        existing = CardImage(storage_key="old.png")
        content = CardContent(text="X", images=[existing])

        updated = service.add_image_to_content(
            content, b"new-bytes", "image/jpeg"
        )

        assert len(updated.images) == 2
        assert updated.images[0].storage_key == "old.png"
        assert updated.images[1].storage_key == "images/0.jpeg"

    def test_preserves_text(self):
        service = CardService(image_storage=FakeImageStorage())
        content = CardContent(text="Keep this")

        updated = service.add_image_to_content(
            content, b"data", "image/png"
        )

        assert updated.text == "Keep this"

    def test_uploads_to_storage(self):
        storage = FakeImageStorage()
        service = CardService(image_storage=storage)

        service.add_image_to_content(
            CardContent(), b"the-image-data", "image/png"
        )

        assert b"the-image-data" in storage.stored.values()


class TestGetImageUrl:
    def test_returns_url_from_storage(self):
        storage = FakeImageStorage()
        service = CardService(image_storage=storage)
        image = CardImage(storage_key="images/photo.jpg")

        url = service.get_image_url(image)

        assert url == "https://cdn.example.com/images/photo.jpg"
