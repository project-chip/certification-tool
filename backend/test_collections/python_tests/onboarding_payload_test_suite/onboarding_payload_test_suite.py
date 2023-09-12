from app.test_engine.logger import test_engine_logger as logger
from app.test_engine.models import TestSuite


class OnboardingPayloadTestSuite(TestSuite):
    metadata = {
        "public_id": "OnboardingPayloadTestSuite",
        "version": "0.0.1",
        "title": "Onboarding Payload Test Suite",
        "description": "Test suite housing test cases related to onboarding payload",
    }

    async def setup(self) -> None:
        logger.info("Payload test suite setup")

    async def cleanup(self) -> None:
        logger.info("Payload test suite cleanup")
