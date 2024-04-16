# from pacs_008_001_08 import Document, FIToFICustomerCreditTransferV08
# from pacs_008_001_08 import GroupHeader93, SettlementInstruction7
# from pacs_008_001_08 import ClearingSystemIdentification2Choice
# from pacs_008_001_08 import CreditTransferTransaction39, PaymentIdentification7
# from pacs_008_001_08 import ActiveCurrencyAndAmount, Charges7
# from pacs_008_001_08 import BranchAndFinancialInstitutionIdentification6
# from pacs_008_001_08 import FinancialInstitutionIdentification18
# from pacs_008_001_08 import PartyIdentification135
# from pacs_008_001_08 import PostalAddress24
from pacs_008_001_08 import *
import uuid




clr_sys = ClearingSystemIdentification2Choice(cd="STG")
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
                                uetr=uuid.uuid4())


zero_amt = ActiveCurrencyAndAmount("GBP", 0)

bic_1 = FinancialInstitutionIdentification18("BARCGB22")
bic_2 = FinancialInstitutionIdentification18("VODAGB23")

agt = BranchAndFinancialInstitutionIdentification6(fin_instn_id=bic_1)
chrgs_inf = Charges7(amt=zero_amt, agt=agt)

ult_pstl = PostalAddress24(bldg_nm="10",
                           strt_nm="Cheapside",
                           twn_nm="London",
                           ctry="GB")
ult_debtr = PartyIdentification135(nm="Mr Ulti Debtor",
                                   pstl_adr=ult_pstl)
initd_pty = PartyIdentification135(nm="Ms Initd Party",
                                   pstl_adr=ult_pstl)

amt = ActiveCurrencyAndAmount("GBP", "555.01")
cdtrtx = CreditTransferTransaction39(pmt_id=pmt_id,
                                     chrg_br="SHAR",
                                     intr_bk_sttlm_dt="2019-01-01",
                                     intr_bk_sttlm_amt=amt,
                                     instd_amt=amt,
                                     chrgs_inf=[chrgs_inf],
                                     instg_agt=bic_1,
                                     instd_agt=bic_2,
                                     ultmt_dbtr=ult_debtr,
                                     initg_pty=initd_pty)


# fit_to_fi_cust_cred_trans = FIToFICustomerCreditTransferV08()

fit_to_fi_cust_cred_trans = FitoFicustomerCreditTransferV08(grp_hdr=grp_header,
                                                             cdt_trf_tx_inf=[cdtrtx])


# Create the root document element
doc = Document(fito_ficstmr_cdt_trf=fit_to_fi_cust_cred_trans)

# Export to an XML file
with open("payment_message.xml", "w") as xml_file:
    doc.export(xml_file, 0, name_='Document')
