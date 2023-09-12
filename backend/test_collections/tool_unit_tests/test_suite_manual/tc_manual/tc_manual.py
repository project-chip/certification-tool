"""Manual Test Case Unit Test."""

from app.test_engine.models import ManualTestCase, TestStep


class TCManual(ManualTestCase):
    metadata = {
        "public_id": "TCManual",
        "version": "1.2.3",
        "title": "A Test Case that must be done manually.",
        "description": "This Test case will prompt the user if this case"
        "pass/failed and to upload a log as evidence.",
    }

    def create_test_steps(self) -> None:
        self.test_steps = [
            TestStep("Manually preform this step first."),
            TestStep("Manually perform this step second."),
            TestStep("Manually perform this step last."),
        ]
