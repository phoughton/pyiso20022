from pyiso20022.pacs.pacs_008_001_08 import *
import pyiso20022.head.head_001_001_02 as hd
from xsdata.formats.dataclass.serializers import XmlSerializer
from xsdata.formats.dataclass.serializers.config import SerializerConfig
import uuid
from lxml import etree


clr_sys = ClearingSystemIdentification3Choice(cd="STG")
the_sttlinf = SettlementInstruction7(sttlm_mtd="CLRG",
                                     clr_sys=clr_sys)

# Create the Group Header
grp_header = GroupHeader93(msg_id="MIDTheMessageId",
                           nb_of_txs=1,
                           cre_dt_tm="2019-01-01T00:00:00",
                           sttlm_inf=the_sttlinf)


pmt_id = PaymentIdentification7(instr_id="IXWEDRFTGHJK5",
                                end_to_end_id="E2EDRFGHJK7",
                                tx_id="TIDRFGHJ54678",
                                uetr=str(uuid.uuid4()))


zero_amt = ActiveOrHistoricCurrencyAndAmount("GBP", 0)

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
rmt_inf = RemittanceInformation16(ustrd="INVOICE 123456")
cdtrtx = CreditTransferTransaction39(pmt_id=pmt_id,
                                     chrg_br="SHAR",
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

ns_map_header = {
    None: "urn:iso:std:iso:20022:tech:xsd:head.001.001.02"
}
ns_map_doc = {
    None: "urn:iso:std:iso:20022:tech:xsd:pacs.008.001.08"
}

header_el = serializer_subs.render(header, ns_map=ns_map_header)
doc_el = serializer_subs.render(doc, ns_map=ns_map_doc)

msg_root = etree.Element('MSGRoot')
msg_root.append(etree.fromstring(header_el))
msg_root.append(etree.fromstring(doc_el))

msg_full = etree.tostring(msg_root, pretty_print=True,
                          xml_declaration=True, encoding='UTF-8')

with open("my_pacs_008_from_code.xml", "w") as xml_file:
    xml_file.write(str(msg_full, encoding='utf-8'))
