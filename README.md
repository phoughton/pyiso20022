# ISO 20022 Message Generator (pyiso20022)

A suite of classes to support payment message generation (for ISO 20022 payment messages)

## Using pyiso20022 package

```bash
pip install pyiso20022
```

Then use this code:

```python
from xsdata.formats.dataclass.parsers import XmlParser
from pyiso20022.pain.pain_001_001_08 import *
import sys


parser = XmlParser()

with open("example_files/gs_pain/pain001_001_08.xml", "rb") as xml_file:
    doc: Document = parser.parse(xml_file, Document, )

print(doc.cstmr_cdt_trf_initn.pmt_inf[0].dbtr.pstl_adr.pst_cd)
```

## Using the Repo (from Github rather than imnstalling the package)

### Create the message (just using the repo and not the package)

```bash
python -m pip install -r requirements.txt
./build_classes_from_xsds.py
python create_msg_1.py
```


### Message types?
Currently only supports PACS & PAIN messages as well as HEAD (header documents for the PACS).


### Source of truth?

If you want the original source of truth for all things ISO 20022 schema related then check out [www.iso20022.org](https://www.iso20022.org/)
