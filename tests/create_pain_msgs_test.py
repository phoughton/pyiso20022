import tempfile
import pytest
from pyiso20022.pain.pain_001_001_08 import *
from xsdata.formats.dataclass.serializers import XmlSerializer
from xsdata.formats.dataclass.serializers.config import SerializerConfig
from xsdata.models.datatype import XmlDate
from xsdata.formats.dataclass.parsers import XmlParser


def create_pain001_001_008():
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

    amt = AmountType4Choice(instd_amt=ActiveOrHistoricCurrencyAndAmount(
        value=10,
        ccy="GBP"))

    cdtr_agt = BranchAndFinancialInstitutionIdentification5(
        fin_instn_id=FinancialInstitutionIdentification8(
            bicfi="BARCGB22"))

    cdtr__pstl_adr = PostalAddress6(strt_nm="CDTR LUEZOF",
                                    bldg_nb="99",
                                    pst_cd="E1 9TY",
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

    config = SerializerConfig(xml_declaration=True,
                              encoding='UTF-8'
                              )
    serializer = XmlSerializer(config=config)

    xml_content = serializer.render(doc, ns_map=ns_map_doc)

    return xml_content


@pytest.mark.parametrize("expected_dbtr_postcode, expected_cdtr_postcode", [
        ("052", "E1 9TY")
    ])
def test_parse_pain001_001_008(expected_dbtr_postcode, expected_cdtr_postcode):
    xml = create_pain001_001_008()

    with tempfile.NamedTemporaryFile() as temp_file:
        temp_file.write(bytes(xml, 'utf-8'))
        temp_file.seek(0)
        parser = XmlParser()

        doc: Document = parser.parse(temp_file, Document, )

        pmt_inf = doc.cstmr_cdt_trf_initn.pmt_inf[0]
        dbtr_post_code = pmt_inf.dbtr.pstl_adr.pst_cd
        cdtr_post_code = pmt_inf.cdt_trf_tx_inf[0].cdtr.pstl_adr.pst_cd

    assert dbtr_post_code == expected_dbtr_postcode
    assert cdtr_post_code == expected_cdtr_postcode
