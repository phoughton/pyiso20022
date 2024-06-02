import pytest
from xsdata.formats.dataclass.parsers import XmlParser
from pyiso20022.pain.pain_001_001_08 import *


@pytest.mark.parametrize("expected_postcode", [
        ("052")
    ])
def test_parse_pain001_001_008(expected_postcode):

    parser = XmlParser()

    with open("example_files/gs_pain/pain001_001_08.xml", "rb") as xml_file:
        doc: Document = parser.parse(xml_file, Document, )

    post_code = doc.cstmr_cdt_trf_initn.pmt_inf[0].dbtr.pstl_adr.pst_cd

    assert post_code == expected_postcode
