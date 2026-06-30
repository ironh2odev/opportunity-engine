import copy
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


if __name__ == "__main__":
    unittest.main()
