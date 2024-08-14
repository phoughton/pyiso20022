<iMG SRC="https://github.com/phoughton/pyiso20022/raw/main/docs/logo_pyiso20022.png?raw=true" WIDTH=400>


Table of Contents: _(Links to this page on GitHub)_
1. [PYISO20022 - an ISO 20022 Message Generator and Parser](https://github.com/phoughton/pyiso20022/blob/main/README.md#pyiso20022-an-iso-20022-message-generator-and-parser)
1. [Parse an ISO 20022 PAIN.001 message](https://github.com/phoughton/pyiso20022/blob/main/README.md#parse-an-iso-20022-pain001-message)
1. [Create a ISO 20022 PAIN.001 message](https://github.com/phoughton/pyiso20022/blob/main/README.md#create-a-iso-20022-pain001-message)
1. [Create a ISO 20022 PACS.008 message](https://github.com/phoughton/pyiso20022/blob/main/README.md#create-a-iso-20022-pacs008-message)


# PYISO20022 an ISO 20022 Message Generator and Parser

A package of classes to support payment, financial, securities & accounting message generation (for ISO 20022 messages).

These are the type of payments messages used in payment schemes such as FedNow, TARGET2, CHAPS, CBPR+, MEPS+ and other SWIFT/Wire Transfer style payments etc. You may hear them refered to as PACS messages (but there are others types as well, like CAMT.056 or PAIN.001).

You might use these messages if you intitate payments from your company into a larger financial institution, in this scenario you will be generating PAIN (thats _Payment Initiation_) messages.

See a full list of types and versions [here](https://github.com/phoughton/pyiso20022/blob/main/supported_msg_types_final.md).

(Raise an issue in github if find a version or msg type is missing! We are constantly expanding the scope of messages we support.)


## Parse an ISO 20022 PAIN.001 message

Install this package and some others...
```bash
pip install pyiso20022
pip install xsdata[cli,lxml,soap]
```

Then use this code to parse a PAIN message, like [this one](https://github.com/phoughton/pyiso20022/blob/main/example_files/gs_pain/pain001_001_08.xml).:

```python
from xsdata.formats.dataclass.parsers import XmlParser
from pyiso20022.pain.pain_001_001_08 import *
import sys


parser = XmlParser()

# Read in a file, you can get an example PAIN (Payment Initiation) message from: 
# https://developer.gs.com/docs/services/transaction-banking/pain001sample/
with open("example_files/gs_pain/pain001_001_08.xml", "rb") as xml_file:
    doc: Document = parser.parse(xml_file, Document, )

# Print out the Post Code.
print(doc.cstmr_cdt_trf_initn.pmt_inf[0].dbtr.pstl_adr.pst_cd)
```

or...

## Create a ISO 20022 PAIN.001 message

Use this code to create a `PA`yment `IN`itiation message. We've used `pain.001.001.08` but other versions are available. 

It will create a file called: `my_pain_001_001_08_from_code.xml`

```python
from pyiso20022.pain.pain_001_001_08 import *
from xsdata.formats.dataclass.serializers import XmlSerializer
from xsdata.formats.dataclass.serializers.config import SerializerConfig
from xsdata.models.datatype import XmlDate


initg_pty__id = Party11Choice(
    org_id=OrganisationIdentification8(
                                  othr=GenericOrganisationIdentification1(
                                          id="uktestdda")
                                          ))

initg_pty = PartyIdentification43(nm="TXB Test Account",
                                  id=initg_pty__id)


grp_hdr = GroupHeader48(msg_id="test-160620",
                        cre_dt_tm="2019-12-03T13:01:00+00:00",
                        nb_of_txs=1,
                        ctrl_sum=10,
                        initg_pty=initg_pty)

dbtr__pstl_adr = PostalAddress6(strt_nm="DBTR LUEZOF",
                                bldg_nb="88",
                                pst_cd="052",
                                twn_nm="VVR MBDB",
                                ctry="QA")

dbtr = PartyIdentification43(nm="UFXQHBE",
                             pstl_adr=dbtr__pstl_adr)


dbtr_acct = CashAccount24(id=AccountIdentification4Choice(
    othr=GenericAccountIdentification1(id="50000970")),
                          ccy="GBP")

dbtr_agt = BranchAndFinancialInstitutionIdentification5(
    fin_instn_id=FinancialInstitutionIdentification8(
        bicfi="GSLDGB20"))

amt = AmountType4Choice(instd_amt=ActiveOrHistoricCurrencyAndAmount(value=10,
                                                                    ccy="GBP"))

cdtr_agt = BranchAndFinancialInstitutionIdentification5(
    fin_instn_id=FinancialInstitutionIdentification8(
        bicfi="BARCGB22"))

cdtr__pstl_adr = PostalAddress6(strt_nm="CDTR LUEZOF",
                                bldg_nb="99",
                                pst_cd="052",
                                twn_nm="VVR MBDB",
                                ctry="QA")

cdtr = PartyIdentification43(nm="Creditor account name",
                             pstl_adr=cdtr__pstl_adr)

cdtr_acct = CashAccount24(id=AccountIdentification4Choice(
    othr=GenericAccountIdentification1(id="12345678")))

rmt_inf = RemittanceInformation11(ustrd="USD Payment from USD account")

cdt_trf_tx_inf = CreditTransferTransaction26(
    pmt_id=PaymentIdentification1(end_to_end_id="test-160620"),
    pmt_tp_inf=PaymentTypeInformation19(
        ctgy_purp=CategoryPurpose1Choice(prtry="Tax Payment")),
    amt=amt,
    cdtr_agt=cdtr_agt,
    cdtr=cdtr,
    cdtr_acct=cdtr_acct,
    purp=Purpose2Choice(prtry="Purpose of payment"),
    rmt_inf=rmt_inf)

pmt_inf = PaymentInstruction22(pmt_inf_id="test-160620",
                               pmt_mtd=PaymentMethod3Code("TRF"),
                               reqd_exctn_dt=DateAndDateTimeChoice(
                                   dt=XmlDate.from_string("2020-06-16")),
                               dbtr=dbtr,
                               dbtr_acct=dbtr_acct,
                               dbtr_agt=dbtr_agt,
                               cdt_trf_tx_inf=cdt_trf_tx_inf)

cstmr_cdt_trf_initn = CustomerCreditTransferInitiationV08(grp_hdr=grp_hdr,
                                                          pmt_inf=pmt_inf)

doc = Document(cstmr_cdt_trf_initn=cstmr_cdt_trf_initn)

ns_map_doc: dict[None, str] = {
    None: "urn:iso:std:iso:20022:tech:xsd:pain.001.001.08"
}

config = SerializerConfig(pretty_print=True,
                          xml_declaration=True,
                          encoding='UTF-8'
                          )
serializer = XmlSerializer(config=config)

xml_content = serializer.render(doc, ns_map=ns_map_doc)

with open("my_pain_001_001_08_from_code.xml", "w") as xml_file:
    xml_file.write(xml_content)

```

or...

## Create a ISO 20022 PACS.008 message

This is an example of how to create a realistic PACS.008 MX payment message.

(it should write out a file called: `my_pacs_008_from_code.xml`)

Depending on your setup you may need a different or even no wrapper element (We've used &lt;MSGRoot&gt; here, but yours might be called something different etc)

```python
from pyiso20022.pacs.pacs_008_001_08 import *
import pyiso20022.head.head_001_001_02 as hd
from xsdata.formats.dataclass.serializers import XmlSerializer
from xsdata.formats.dataclass.serializers.config import SerializerConfig
import uuid
from lxml import etree
from xsdata.models.datatype import XmlDateTime


clr_sys = ClearingSystemIdentification3Choice(cd="STG")
the_sttlinf = SettlementInstruction7(sttlm_mtd=SettlementMethod1Code("CLRG"),
                                     clr_sys=clr_sys)

# Create the Group Header
grp_header = GroupHeader93(msg_id="MIDTheMessageId",
                           nb_of_txs=1,
                           cre_dt_tm=XmlDateTime.from_string("2019-01-01T00:00:00"),
                           sttlm_inf=the_sttlinf)


pmt_id = PaymentIdentification7(instr_id="IXWEDRFTGHJK5",
                                end_to_end_id="E2EDRFGHJK7",
                                tx_id="TIDRFGHJ54678",
                                uetr=str(uuid.uuid4()))


zero_amt = ActiveOrHistoricCurrencyAndAmount(ccy="GBP", value=0)

bic_1 = FinancialInstitutionIdentification18("BARCGB22")
bic_2 = FinancialInstitutionIdentification18("VODAGB23")

agt = BranchAndFinancialInstitutionIdentification6(fin_instn_id=bic_1)

instd_agt = BranchAndFinancialInstitutionIdentification6(fin_instn_id=bic_2)
instg_agt = BranchAndFinancialInstitutionIdentification6(fin_instn_id=bic_1)

chrgs_inf = Charges7(amt=zero_amt, agt=agt)

ult_pstl = PostalAddress24(bldg_nm="10",
                           strt_nm="Cheapside",
                           twn_nm="London",
                           ctry="GB")
dbtr_pstl = PostalAddress24(bldg_nm="11",
                            strt_nm="Farside",
                            twn_nm="York",
                            ctry="GB")
ult_debtr = PartyIdentification135(nm="Mr Ulti Debtor",
                                   pstl_adr=ult_pstl)
initg_pty = PartyIdentification135(nm="Ms Initd Party",
                                   pstl_adr=ult_pstl)
reg_debtr = PartyIdentification135(nm="Mrs Reg Debtor",
                                   pstl_adr=dbtr_pstl)
instr_for_nxt_agt = InstructionForNextAgent1(instr_inf="HOLD")
instd_amt = ActiveOrHistoricCurrencyAndAmount(ccy="GBP", value=555.01)
intra_bk_st_amt = ActiveCurrencyAndAmount(ccy="GBP", value=555.01)

purp = Purpose2Choice(cd="PHON")
rem_loc = RemittanceLocation7(rmt_id="BUSINESS DEBIT")
rmt_inf = RemittanceInformation16(ustrd=["INVOICE 123456"])
cdtrtx = CreditTransferTransaction39(pmt_id=pmt_id,
                                     chrg_br=ChargeBearerType1Code("SHAR"),
                                     intr_bk_sttlm_dt="2019-01-01",
                                     intr_bk_sttlm_amt=intra_bk_st_amt,
                                     instd_amt=instd_amt,
                                     chrgs_inf=[chrgs_inf],
                                     instg_agt=instg_agt,
                                     instd_agt=instd_agt,
                                     ultmt_dbtr=ult_debtr,
                                     initg_pty=initg_pty,
                                     dbtr=reg_debtr,
                                     dbtr_agt=instg_agt,
                                     cdtr_agt=instd_agt,
                                     instr_for_nxt_agt=[instr_for_nxt_agt],
                                     purp=purp,
                                     rltd_rmt_inf=[rem_loc],
                                     rmt_inf=rmt_inf)


f2f_cust_cred_trans = FitoFicustomerCreditTransferV08(grp_hdr=grp_header,
                                                      cdt_trf_tx_inf=[cdtrtx])

doc = Document(fito_ficstmr_cdt_trf=f2f_cust_cred_trans)

# Create the AppHdr
fr_fiid = hd.FinancialInstitutionIdentification18(bicfi="BARCGB22")
fr_bafii = hd.BranchAndFinancialInstitutionIdentification6(fin_instn_id=fr_fiid)
fr_party44 = hd.Party44Choice(fiid=fr_bafii)

to_fiid = hd.FinancialInstitutionIdentification18(bicfi="BARCGB22")
to_bafii = hd.BranchAndFinancialInstitutionIdentification6(fin_instn_id=to_fiid)
to_party44 = hd.Party44Choice(fiid=to_bafii)

header = hd.AppHdr(fr=fr_party44,
                   to=to_party44,
                   biz_msg_idr="MIDRFGHJKL",
                   msg_def_idr="pacs.008.001.08",
                   biz_svc="boe.chaps.enh.01",
                   cre_dt="2019-01-01T00:00:00",
                   prty="NORM")

config_subs = SerializerConfig(pretty_print=True, xml_declaration=False)
serializer_subs = XmlSerializer(config=config_subs)

ns_map_header: dict[None, str] = {
    None: "urn:iso:std:iso:20022:tech:xsd:head.001.001.02"
}
ns_map_doc: dict[None, str] = {
    None: "urn:iso:std:iso:20022:tech:xsd:pacs.008.001.08"
}

header_el: str = serializer_subs.render(header, ns_map=ns_map_header)
doc_el: str = serializer_subs.render(doc, ns_map=ns_map_doc)

msg_root = etree.Element('MSGRoot')
msg_root.append(etree.fromstring(header_el))
msg_root.append(etree.fromstring(doc_el))

msg_full = etree.tostring(msg_root, pretty_print=True,
                          xml_declaration=True, encoding='UTF-8')

with open("my_pacs_008_from_code.xml", "w") as xml_file:
    xml_file.write(str(msg_full, encoding='utf-8'))

```

## Convert a CAMT.053 into an Excel file?

You can convert the entries in a CAMT.053 into a Excel file using the tools.

Currently this will extract the `Ntry` list and take all details and place them into seperate columns. It will also translate the element names intro their more meaningful English versions.

Use it like this:

```python
import pyiso20022.tools as isotools

isotools.camt053_to_excel("my_camt053_file.xml",
                          "my_camt053_excel_file.xlsx")
```




## Message types?
Currently pyiso20022 supports PACS, PAIN and CAMT messages as well as HEAD (header documents for the messages).


## Source of truth?

If you want the original source of truth for all things ISO 20022 schema related then check out [www.iso20022.org](https://www.iso20022.org/)
