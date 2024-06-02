import pytest
from xsdata.formats.dataclass.parsers import XmlParser
from pyiso20022.camt.camt_052_001_02 import *


@pytest.mark.parametrize("expected_acc_id", [
        ("106068381")
    ])
def test_parse_camt052_001_02(expected_acc_id):

    parser = XmlParser()

    with open("example_files/gs_camt/camt052_001_02.xml", "rb") as xml_file:
        doc: Document = parser.parse(xml_file, Document, )

    acc_id = doc.bk_to_cstmr_acct_rpt.rpt[0].acct.id.othr.id

    assert acc_id == expected_acc_id
