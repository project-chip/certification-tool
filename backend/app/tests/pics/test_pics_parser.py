from pathlib import Path

from app.pics.pics_parser import PICSParser
from app.schemas.pics import PICSError


def test_pics_parser() -> None:
    pics_file = (
        Path(__file__).parent.parent.parent / "tests" / "utils" / "test_pics.xml"
    )
    cluster = PICSParser.parse(file=pics_file.open())

    assert cluster is not None
    assert cluster.name == "On/Off"

    assert len(cluster.items) > 0
    # expected pic items and their values
    assert cluster.items["OO.S.A0000"].enabled is True
    assert cluster.items["OO.S.A4000"].enabled is False
    assert cluster.items["OO.S.C00"].enabled is True


def test_pics_parser_with_errors() -> None:
    # test pics parse with invalid root tag
    pics_file = (
        Path(__file__).parent.parent.parent
        / "tests"
        / "utils"
        / "test_pics_with_invalid_root_tag.xml"
    )

    try:
        PICSParser.parse(file=pics_file.open())

    except Exception as e:
        assert isinstance(e, PICSError)

    # test pics parse with no name element
    pics_file = (
        Path(__file__).parent.parent.parent
        / "tests"
        / "utils"
        / "test_pics_with_no_name_element.xml"
    )

    try:
        PICSParser.parse(file=pics_file.open())

    except Exception as e:
        assert isinstance(e, PICSError)

    # test pics parse with no name element
    pics_file = (
        Path(__file__).parent.parent.parent
        / "tests"
        / "utils"
        / "test_pics_with_empty_name_element.xml"
    )

    try:
        PICSParser.parse(file=pics_file.open())

    except Exception as e:
        assert isinstance(e, PICSError)
