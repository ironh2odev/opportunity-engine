import os
import tempfile
import unittest

from fastapi.testclient import TestClient

from app.main import app


class PersonalLeadsApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.temp_dir.name, "personal_test.db")
        os.environ["OE_PERSONAL_DB_PATH"] = self.db_path
        self.client = TestClient(app)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()
        if "OE_PERSONAL_DB_PATH" in os.environ:
            del os.environ["OE_PERSONAL_DB_PATH"]

    def _create_lead(self) -> str:
        response = self.client.post(
            "/personal/leads",
            json={
                "name": "Avery Pike",
                "role": "Founder",
                "organisation": "Northfield Systems",
                "source": "manual",
                "opportunity_type": "client",
                "relationship_strength": "cold",
                "status": "new",
                "fit_score": 7,
                "priority": "high",
                "problem_observed": "Slow lead response workflow",
                "why_relevant": "Clear fit with workflow automation offer",
                "suggested_angle": "Start with lightweight process audit",
                "notes": "First pass note",
                "tags": ["saas", "revops"],
                "next_action": "prepare connection request",
            },
        )
        self.assertEqual(response.status_code, 200)
        return response.json()["id"]

    def test_create_lead(self) -> None:
        lead_id = self._create_lead()
        get_response = self.client.get(f"/personal/leads/{lead_id}")
        self.assertEqual(get_response.status_code, 200)
        self.assertEqual(get_response.json()["name"], "Avery Pike")

    def test_update_lead(self) -> None:
        lead_id = self._create_lead()
        update_response = self.client.patch(
            f"/personal/leads/{lead_id}",
            json={"status": "reviewed", "priority": "medium", "notes": "Updated note"},
        )
        self.assertEqual(update_response.status_code, 200)
        self.assertEqual(update_response.json()["status"], "reviewed")
        self.assertEqual(update_response.json()["priority"], "medium")

    def test_import_csv(self) -> None:
        csv_text = """name,role,organisation,organisationWebsite,linkedinUrl,email,location,source,opportunityType,relationshipStrength,problemObserved,whyRelevant,suggestedAngle,notes,tags,nextAction,followUpDate
Riley North,Growth Lead,Summit Relay,https://summit.example,https://linkedin.example/riley,riley@example.com,Austin,csv,client,warm,Lead qualification lag,Good fit with advisory ops,Use roadmap-first pitch,Note one,revops|b2b,review website,2026-07-10
"""
        import_response = self.client.post(
            "/personal/leads/import-csv",
            json={"csv_text": csv_text},
        )
        self.assertEqual(import_response.status_code, 200)
        self.assertEqual(len(import_response.json()), 1)

    def test_invalid_csv_rejected(self) -> None:
        csv_text = """name,role,organisation,organisationWebsite,linkedinUrl,email,location,source,opportunityType,relationshipStrength,problemObserved,whyRelevant,suggestedAngle,notes,tags,nextAction,followUpDate
Jordan Vale,Founder,Cobalt Ridge,https://cobalt.example,https://linkedin.example/jordan,jordan@example.com,Remote,csv,unknown_type,warm,Ops pain,Interesting,Angle,Note,t1,prepare outreach,
"""
        import_response = self.client.post(
            "/personal/leads/import-csv",
            json={"csv_text": csv_text},
        )
        self.assertEqual(import_response.status_code, 400)
        self.assertIn("Invalid CSV row", import_response.json()["detail"])

    def test_create_rule_action_from_lead(self) -> None:
        lead_id = self._create_lead()
        action_response = self.client.post(f"/personal/leads/{lead_id}/create-rule-action")
        self.assertEqual(action_response.status_code, 200)
        action = action_response.json()
        self.assertEqual(action["status"], "suggested")
        self.assertIn("approval_required", action)


if __name__ == "__main__":
    unittest.main()
