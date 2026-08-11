import unittest

from creator_cost_workflow import SubscriberUpdate, publish_decision


class PublishDecisionTest(unittest.TestCase):
    def test_ready_short_update_is_published(self) -> None:
        update = SubscriberUpdate("subscriber-1042", "Preset pack", "ZIP ready")
        self.assertTrue(publish_decision(update, total_tokens=240))

    def test_large_draft_stays_in_review(self) -> None:
        update = SubscriberUpdate("subscriber-1042", "Preset pack", "ZIP ready")
        self.assertFalse(publish_decision(update, total_tokens=801))


if __name__ == "__main__":
    unittest.main()

