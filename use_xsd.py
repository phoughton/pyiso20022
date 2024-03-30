from pacs_008_001_08 import Document, FIToFICustomerCreditTransferV08
from pacs_008_001_08 import GroupHeader93, SettlementInstruction7
from pacs_008_001_08 import ClearingSystemIdentification2Choice


# Create the root document element
doc = Document()

the_sttlinf = SettlementInstruction7()
the_sttlinf.set_SttlmMtd("CLRG")
the_sttlinf.set_ClrSys(ClearingSystemIdentification2Choice(Cd="STG"))

# Create the Group Header
the_grp_header = GroupHeader93(MsgId="MIDTheMessageId",
                               NbOfTxs=1,
                               CreDtTm="2019-01-01T00:00:00",
                               SttlmInf=the_sttlinf)

the_fitc = FIToFICustomerCreditTransferV08()

the_fitc.set_GrpHdr(the_grp_header)

doc.set_FIToFICstmrCdtTrf(the_fitc)


# Export to an XML file
with open("payment_message.xml", "w") as xml_file:
    doc.export(xml_file, 0, name_='Document')


