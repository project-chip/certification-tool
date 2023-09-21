from app.test_engine.models.test_declarations import TestCollectionDeclaration

from .sdk_yaml_tests import sdk_yaml_test_collection

# Test engine will auto load TestCollectionDeclarations declared inside the package
# initializer
sdk_collection: TestCollectionDeclaration = sdk_yaml_test_collection()
