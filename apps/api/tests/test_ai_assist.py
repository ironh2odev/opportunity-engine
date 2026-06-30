import os
import unittest

from fastapi.testclient import TestClient

from app.main import app


class AIAssistApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)
        self.old_openai_key = os.environ.get("OPENAI_API_KEY")
        if "OPENAI_API_KEY" in os.environ:
            del os.environ["OPENAI_API_KEY"]

    def tearDown(self) -> None:
        if self.old_openai_key is not None:
            os.environ["OPENAI_API_KEY"] = self.old_openai_key
        elif "OPENAI_API_KEY" in os.environ:
            del os.environ["OPENAI_API_KEY"]

    def _payload(self):
        return {
            "action_id": "action_001",
            "action_type": "Connection request draft",
            "channel": "connection_request",
            "opportunity_type": "networking",
            "target_name": "Jordan Lee",
            "target_role": "Founder",
            "target_organisation": "Northfield Systems",
            "suggested_action": "Draft a concise connection note",
            "existing_suggested_message": "Hi Jordan, great to connect.",
            "rationale": "Shared focus on practical workflow execution.",
            "proof_to_reference": "Mention one shipped workflow improvement.",
            "source_type": "personal_lead",
            "source_lead_id": "lead_123",
            "user_tone": "thoughtful, clear, humble, premium, practical, not hype",
            "constraints": [
                "Draft only.",
                "No auto-send.",
                "No auto-apply.",
                "Connection note under 200 characters.",
            ],
        }

    def test_returns_mock_draft_without_api_key(self) -> None:
        response = self.client.post("/ai/draft-action", json=self._payload())
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertIn("draft_message", body)
        self.assertIn("review_notes", body)
        self.assertGreaterEqual(len(body["review_notes"]), 3)

    def test_rejects_missing_required_action_context(self) -> None:
        payload = self._payload()
        del payload["target_name"]
        response = self.client.post("/ai/draft-action", json=payload)
        self.assertEqual(response.status_code, 422)

    def test_connection_note_short_version_is_limited(self) -> None:
        response = self.client.post("/ai/draft-action", json=self._payload())
        self.assertEqual(response.status_code, 200)
        short_version = response.json().get("short_version")
        self.assertIsNotNone(short_version)
        self.assertLessEqual(len(short_version), 200)

    def test_ai_draft_does_not_change_action_status(self) -> None:
        actions_before = self.client.get("/rule-of-100/actions")
        self.assertEqual(actions_before.status_code, 200)
        first = actions_before.json()[0]

        payload = self._payload()
        payload["action_id"] = first["id"]
        payload["action_type"] = first["action_type"]
        payload["channel"] = first["channel"]
        payload["opportunity_type"] = first["opportunity_type"]
        payload["target_name"] = first["target_name"]
        payload["target_role"] = first["target_role"]
        payload["target_organisation"] = first["target_organisation"]
        payload["suggested_action"] = first["suggested_action"]
        payload["existing_suggested_message"] = first["suggested_message"]
        payload["rationale"] = first["rationale"]
        payload["proof_to_reference"] = first["proof_to_reference"]
        payload["source_type"] = first.get("source_type", "mock_demo")
        payload["source_lead_id"] = first.get("source_lead_id")

        draft_response = self.client.post("/ai/draft-action", json=payload)
        self.assertEqual(draft_response.status_code, 200)

        actions_after = self.client.get("/rule-of-100/actions")
        self.assertEqual(actions_after.status_code, 200)
        updated = next(item for item in actions_after.json() if item["id"] == first["id"])
        self.assertEqual(updated["status"], first["status"])


if __name__ == "__main__":
    unittest.main()
