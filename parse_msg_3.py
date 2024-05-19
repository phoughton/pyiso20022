from xsdata.formats.dataclass.parsers import XmlParser
from pyiso20022.pain.pain_001_001_08 import *
import sys


parser = XmlParser()

with open("example_files/gs_pain/pain001_001_08.xml", "rb") as xml_file:
    doc: Document = parser.parse(xml_file, Document, )

# These are needed if using Type checking mode basic or higher in PyLance
if doc.cstmr_cdt_trf_initn is None or \
      doc.cstmr_cdt_trf_initn.pmt_inf[0].dbtr is None or \
      doc.cstmr_cdt_trf_initn.pmt_inf[0].dbtr.pstl_adr is None:
    print("Exiting as we will access None objects")
    sys.exit(2)

doc.cstmr_cdt_trf_initn.pmt_inf[0].dbtr.pstl_adr.pst_cd = "E1 8RL"

print(doc.cstmr_cdt_trf_initn.pmt_inf[0].dbtr.pstl_adr.pst_cd)

doc.cstmr_cdt_trf_initn.pmt_inf[0].dbtr.pstl_adr.pst_cd = "X1 FY"

print(doc.cstmr_cdt_trf_initn.pmt_inf[0].dbtr.pstl_adr.pst_cd)
