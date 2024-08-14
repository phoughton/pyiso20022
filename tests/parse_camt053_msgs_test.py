import pytest
from xsdata.formats.dataclass.parsers import XmlParser
from pyiso20022.camt.camt_053_001_02 import *


@pytest.mark.parametrize("expected_acc_id", [
        ("DD01100056869")
    ])
def test_parse_camt053_001_02(expected_acc_id):

    parser = XmlParser()

    with open("example_files/gs_camt/camt053_001_02.xml", "rb") as xml_file:
        doc: Document = parser.parse(xml_file, Document, )

    acc_id = doc.bk_to_cstmr_stmt.stmt[0].acct.id.othr.id

    assert acc_id == expected_acc_id
