from app.pics_applicable_test_cases import applicable_test_cases_list
from app.schemas.pics import PICS
from app.tests.utils.test_pics_data import create_random_pics


def test_applicable_test_cases_list() -> None:
    pics = create_random_pics()

    applicable_test_cases = applicable_test_cases_list(pics)

    # Unit test case (TCPics) has AB.C and AB.C.0004 PICs enabled.
    # create_random_pics creates pics with these values set.
    # Applicable test cases should always be at least 1.
    assert len(applicable_test_cases.test_cases) > 0


def test_applicable_test_cases_list_with_no_pics() -> None:
    # create empty PICS list
    pics = PICS()

    applicable_test_cases = applicable_test_cases_list(pics)

    assert len(applicable_test_cases.test_cases) == 0
