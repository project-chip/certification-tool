import xml.etree.ElementTree as ET
from typing import IO
from xml.etree.ElementTree import Element

from loguru import logger

from app.schemas.pics import PICSCluster, PICSError, PICSItem


class PICSParser:
    """Parse PICS XML file"""

    @classmethod
    def parse(cls, file: IO) -> PICSCluster:
        logger.debug(f"Begin parsing {file.name}")
        root_element = cls.__find_root_element(file=file)
        cluster_name = cls.__text_for_element_child(root_element, "name")
        cluster: PICSCluster = PICSCluster(name=cluster_name)

        for pics_item_element in root_element.iter("picsItem"):
            pics_item = cls.__pics_item(pics_item_element)
            cluster.items[pics_item.number] = pics_item

        logger.debug(f"Total PICS found - {len(cluster.items.keys())}")
        return cluster

    @classmethod
    def __find_root_element(cls, file: IO) -> Element:
        root_element = ET.parse(file).getroot()
        # Verify that root element tag is on of the supported ones.
        if root_element.tag not in ["clusterPICS", "generalPICS"]:
            raise PICSError("Parser failed to find root tag")
        return root_element

    @classmethod
    def __text_for_element_child(
        cls, parent_element: Element, element_name: str
    ) -> str:
        logger.debug(f"Finding element {element_name}")
        element = parent_element.find(element_name)
        if element is None:
            raise PICSError(f"Parser failed to find element {element_name}")
        if element.text is None:
            raise PICSError(
                f"Parser failed to find text field in element {element_name}"
            )
        return element.text

    @classmethod
    def __pics_item(cls, element: Element) -> PICSItem:
        supported = cls.__text_for_element_child(element, "support")
        is_supported = supported.lower() == "true"
        item_number = cls.__text_for_element_child(element, "itemNumber")
        return PICSItem(number=item_number, enabled=is_supported)
