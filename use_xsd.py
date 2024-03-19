from pacs_008_001_12 import Document, FIToFICustomerCreditTransferV12
from pacs_008_001_12 import GroupHeader113

# Create the root document element
doc = Document()

# Assume we're creating a single payment instruction
top_level = FIToFICustomerCreditTransferV12()

top_level.set_GrpHdr(GrpHdr=GroupHeader113(MsgId="TheMessageId",
                                           NbOfTxs=2))

doc.set_FIToFICstmrCdtTrf(top_level)
# Export to an XML file
with open("payment_message.xml", "w") as xml_file:
    doc.export(xml_file, 0, name_='Document')
