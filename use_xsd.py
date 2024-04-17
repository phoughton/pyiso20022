from pacs_008_001_08 import *
import uuid


# Create the root document element
doc = Document()

the_sttlinf = SettlementInstruction7(sttlm_mtd="CLRG",
                                     clr_sys=ClearingSystemIdentification2Choice(cd="STG"))

# Create the Group Header
grp_header = GroupHeader93(msg_id="MIDTheMessageId",
                           NbOfTxs=1,
                           CreDtTm="2019-01-01T00:00:00",
                           SttlmInf=the_sttlinf)


pmt_id = PaymentIdentification7(InstrId="IXWEDRFTGHJK5",
                                EndToEndId="E2EDRFGHJK7",
                                TxId="TIDRFGHJ54678",
                                UETR=uuid.uuid4())


zero_amt = ActiveCurrencyAndAmount("GBP", 0)

bic_1 = FinancialInstitutionIdentification18("BARCGB22")
bic_2 = FinancialInstitutionIdentification18("VODAGB23")

agt = BranchAndFinancialInstitutionIdentification6(FinInstnId=bic_1)
chrgs_inf = Charges7(Amt=zero_amt, Agt=agt)

ult_pstl = PostalAddress24(BldgNb="10",
                           StrtNm="Cheapside",
                           TwnNm="London",
                           Ctry="GB")
ult_debtr = PartyIdentification135(Nm="Mr Ulti Debtor",
                                   PstlAdr=ult_pstl)


amt = ActiveCurrencyAndAmount("GBP", "555.01")
cdtrtx = CreditTransferTransaction39(PmtId=pmt_id,
                                     ChrgBr="SHAR",
                                     IntrBkSttlmDt="2019-01-01",
                                     IntrBkSttlmAmt=amt,
                                     InstdAmt=amt,
                                     ChrgsInf=[chrgs_inf],
                                     InstdAgt=bic_1,
                                     InstgAgt=bic_2,
                                     UltmtDbtr=ult_debtr, initg_pty=)


fit_to_fi_cust_cred_trans = FitoFicustomerCreditTransferV08()

fit_to_fi_cust_cred_trans.set_GrpHdr(grp_header)
fit_to_fi_cust_cred_trans.set_CdtTrfTxInf([cdtrtx])


doc(FitoFicustomerCreditTransferV08=fit_to_fi_cust_cred_trans)


# Export to an XML file
with open("payment_message.xml", "w") as xml_file:
    doc.export(xml_file, 0, name_='Document')


