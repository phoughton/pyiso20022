import pytest
from xsdata.formats.dataclass.parsers import XmlParser
from pyiso20022.remt.remt_001_001_06 import *
from decimal import Decimal


@pytest.mark.parametrize("expected_RmtAmtAndTp", [
        ("3916.11")
    ])
def test_parse_remt001_001_006(expected_RmtAmtAndTp):

    parser = XmlParser()

    with open("example_files/remt/remt_001_001_06.xml", "rb") as xml_file:
        doc: Document = parser.parse(xml_file, Document, )

    amount = doc.rmt_advc.rmt_inf[0].strd[0].rfrd_doc_amt.rmt_amt_and_tp[0].amt.value

    assert amount == Decimal(expected_RmtAmtAndTp)
