import copy
import os
import tempfile
import unittest

from fastapi.testclient import TestClient

from app.main import app
from app import mock_data


class RuleOf100ApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)
        self.plan_backup = mock_data.RULE_OF_100_PLAN.model_copy(deep=True)
        self.actions_backup = copy.deepcopy(mock_data.RULE_OF_100_ACTIONS)
        self.approvals_backup = copy.deepcopy(mock_data.APPROVAL_RECORDS)

    def tearDown(self) -> None:
        for field_name, value in self.plan_backup.model_dump().items():
            setattr(mock_data.RULE_OF_100_PLAN, field_name, copy.deepcopy(value))
        mock_data.RULE_OF_100_ACTIONS[:] = copy.deepcopy(self.actions_backup)
        mock_data.APPROVAL_RECORDS[:] = copy.deepcopy(self.approvals_backup)
        if "OE_PERSONAL_DB_PATH" in os.environ:
            del os.environ["OE_PERSONAL_DB_PATH"]

    def _personal_client(self):
        temp_dir = tempfile.TemporaryDirectory()
        os.environ["OE_PERSONAL_DB_PATH"] = os.path.join(temp_dir.name, "personal_test.db")
        return TestClient(app), temp_dir

    def _find_action(self, *, approval_required: bool) -> str:
        for action in mock_data.RULE_OF_100_ACTIONS:
            if action.approval_required == approval_required:
                return action.id
        raise AssertionError("Expected action not found")

    def test_outbound_action_cannot_complete_before_approval(self) -> None:
        action_id = self._find_action(approval_required=True)

        response = self.client.post(f"/rule-of-100/actions/{action_id}/complete")

        self.assertEqual(response.status_code, 409)
        self.assertIn("human approval", response.json()["detail"])

    def test_approved_outbound_action_can_complete(self) -> None:
        action_id = self._find_action(approval_required=True)

        approve_response = self.client.post(f"/rule-of-100/actions/{action_id}/approve")
        self.assertEqual(approve_response.status_code, 200)

        complete_response = self.client.post(f"/rule-of-100/actions/{action_id}/complete")
        self.assertEqual(complete_response.status_code, 200)
        self.assertEqual(complete_response.json()["status"], "completed")

    def test_non_outbound_action_can_complete(self) -> None:
        action_id = self._find_action(approval_required=False)

        response = self.client.post(f"/rule-of-100/actions/{action_id}/complete")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "completed")

    def test_status_transitions_include_skipped_blocked_and_in_review(self) -> None:
        action_id = self._find_action(approval_required=False)

        skipped = self.client.patch(
            f"/rule-of-100/actions/{action_id}/status",
            json={"status": "skipped"},
        )
        self.assertEqual(skipped.status_code, 200)
        self.assertEqual(skipped.json()["status"], "skipped")

        blocked = self.client.patch(
            f"/rule-of-100/actions/{action_id}/status",
            json={"status": "blocked"},
        )
        self.assertEqual(blocked.status_code, 200)
        self.assertEqual(blocked.json()["status"], "blocked")

        in_review = self.client.patch(
            f"/rule-of-100/actions/{action_id}/status",
            json={"status": "in_review"},
        )
        self.assertEqual(in_review.status_code, 200)
        self.assertEqual(in_review.json()["status"], "in_review")

    def test_invalid_plan_target_and_allocation_are_rejected(self) -> None:
        bad_target = self.client.patch(
            "/rule-of-100/today-plan",
            json={"target_count": 49},
        )
        self.assertEqual(bad_target.status_code, 422)

        bad_allocation = self.client.patch(
            "/rule-of-100/today-plan",
            json={"allocation": {"linkedin_comment": 60}},
        )
        self.assertEqual(bad_allocation.status_code, 400)
        self.assertIn("allocation total", bad_allocation.json()["detail"])

    def test_api_contract_uses_snake_case_fields(self) -> None:
        plan_response = self.client.get("/rule-of-100/today-plan")
        self.assertEqual(plan_response.status_code, 200)
        plan_json = plan_response.json()
        self.assertIn("target_count", plan_json)
        self.assertIn("min_target", plan_json)

        actions_response = self.client.get("/rule-of-100/actions")
        self.assertEqual(actions_response.status_code, 200)
        action = actions_response.json()[0]
        self.assertIn("action_type", action)
        self.assertIn("target_organisation", action)
        self.assertIn("approval_required", action)

        approvals_response = self.client.get("/rule-of-100/approvals")
        self.assertEqual(approvals_response.status_code, 200)
        if approvals_response.json():
            approval = approvals_response.json()[0]
            self.assertIn("approved_by", approval)
            self.assertIn("approved_at", approval)

    def test_personal_generated_action_appears_in_queue_with_metadata(self) -> None:
        client, temp_dir = self._personal_client()
        self.addCleanup(temp_dir.cleanup)

        lead_response = client.post(
            "/personal/leads",
            json={
                "name": "Jordan Lee",
                "role": "Founder",
                "organisation": "Northfield Systems",
                "source": "manual",
                "opportunity_type": "client",
                "relationship_strength": "warm",
                "status": "new",
                "fit_score": 8,
                "priority": "high",
                "next_action": "prepare outreach draft",
            },
        )
        self.assertEqual(lead_response.status_code, 200)
        lead_id = lead_response.json()["id"]

        action_response = client.post(f"/personal/leads/{lead_id}/create-rule-action")
        self.assertEqual(action_response.status_code, 200)
        personal_action_id = action_response.json()["id"]

        queue_response = client.get("/rule-of-100/actions")
        self.assertEqual(queue_response.status_code, 200)
        queue = queue_response.json()
        personal_action = next(item for item in queue if item["id"] == personal_action_id)
        self.assertEqual(personal_action["source_type"], "personal_lead")
        self.assertEqual(personal_action["source_lead_id"], lead_id)
        self.assertEqual(personal_action["private_mode"], True)
        self.assertEqual(personal_action["source_lead_name"], "Jordan Lee")

    def test_personal_action_approval_guard_still_applies(self) -> None:
        client, temp_dir = self._personal_client()
        self.addCleanup(temp_dir.cleanup)

        lead_response = client.post(
            "/personal/leads",
            json={
                "name": "Jordan Lee",
                "role": "Founder",
                "organisation": "Northfield Systems",
                "source": "manual",
                "opportunity_type": "client",
                "relationship_strength": "warm",
                "status": "new",
                "fit_score": 8,
                "priority": "high",
                "next_action": "prepare outreach draft",
            },
        )
        lead_id = lead_response.json()["id"]
        action_response = client.post(f"/personal/leads/{lead_id}/create-rule-action")
        action_id = action_response.json()["id"]

        complete_before_approval = client.post(f"/rule-of-100/actions/{action_id}/complete")
        self.assertEqual(complete_before_approval.status_code, 409)

        approve_response = client.post(f"/rule-of-100/actions/{action_id}/approve")
        self.assertEqual(approve_response.status_code, 200)

        complete_after_approval = client.post(f"/rule-of-100/actions/{action_id}/complete")
        self.assertEqual(complete_after_approval.status_code, 200)
        self.assertEqual(complete_after_approval.json()["status"], "completed")


if __name__ == "__main__":
    unittest.main()
