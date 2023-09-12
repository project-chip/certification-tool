from typing import Dict

# {<TestCase.public_id>:iterations}
TestCaseSelection = Dict[str, int]
# {<TestSuite.public_id>:selected_test_cases}
TestSuiteSelection = Dict[str, TestCaseSelection]
# {<TestCollection.name>:selected_test_suites}
TestSelection = Dict[str, TestSuiteSelection]
