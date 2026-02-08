from study.model.sks_topic import SksTopic


class TestSksTopicMembers:
    def test_has_five_topics(self):
        assert len(SksTopic) == 5

    def test_navigation_value(self):
        assert SksTopic.NAVIGATION == "navigation"

    def test_schifffahrtsrecht_value(self):
        assert SksTopic.SCHIFFFAHRTSRECHT == "schifffahrtsrecht"

    def test_wetterkunde_value(self):
        assert SksTopic.WETTERKUNDE == "wetterkunde"

    def test_seemannschaft_i_value(self):
        assert SksTopic.SEEMANNSCHAFT_I == "seemannschaft_i"

    def test_seemannschaft_ii_value(self):
        assert SksTopic.SEEMANNSCHAFT_II == "seemannschaft_ii"


class TestSksTopicUsage:
    def test_can_iterate_all_topics(self):
        topics = list(SksTopic)
        assert len(topics) == 5

    def test_topic_value_matches_tag_string(self):
        """Topic values should be usable directly as card tags."""
        tags = ["navigation", "some-other-tag"]
        assert SksTopic.NAVIGATION in tags
        assert SksTopic.WETTERKUNDE not in tags
