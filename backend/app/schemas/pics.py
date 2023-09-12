from pydantic import BaseModel


class PICSItem(BaseModel):
    number: str
    enabled: bool


class PICSCluster(BaseModel):
    name: str
    items: dict[str, PICSItem] = {}

    def enabled_items(self) -> list[PICSItem]:
        return list([item for item in self.items.values() if item.enabled])


class PICS(BaseModel):
    clusters: dict[str, PICSCluster] = {}

    def all_enabled_items(self) -> list[PICSItem]:
        # flatten all enabled items for all clusters
        return sum([c.enabled_items() for c in self.clusters.values()], [])


class PICSApplicableTestCases(BaseModel):
    test_cases: set[str]


class PICSError(Exception):
    """Raised when an error occurs during execution."""
