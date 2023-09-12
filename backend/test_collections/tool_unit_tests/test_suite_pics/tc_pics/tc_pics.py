from app.test_engine.models import TestCase, TestStep


class TCPics(TestCase):
    metadata = {
        "public_id": "TC_Pics",
        "version": "1.2.3",
        "title": "TC_Pics (Test)",
        "description": "Test PICS test case for unit testing",
    }

    @classmethod
    def pics(cls) -> set[str]:
        return set(
            [
                "AB.C",
                "AB.C.A0004",
            ]
        )

    def create_test_steps(self) -> None:
        self.test_steps = [TestStep("Test Step 1")]
        self.test_steps = [TestStep("Test Step 2")]
        self.test_steps = [TestStep("Test Step 3")]
