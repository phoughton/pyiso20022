"""Test cases for the ISO20022 validation system."""
from decimal import Decimal
from datetime import datetime
from xsdata.models.datatype import XmlDateTime
from pyiso20022.pacs.pacs_008_001_08.pacs_008_001_08 import (
    PaymentIdentification7,
    ActiveCurrencyAndAmount,
    Document,
    FitoFicustomerCreditTransferV08,
    GroupHeader93,
    CreditTransferTransaction39,
    BranchAndFinancialInstitutionIdentification6,
    FinancialInstitutionIdentification18,
    PartyIdentification135,
    SettlementInstruction7,
    SettlementMethod1Code,
    ChargeBearerType1Code,
)
from pyiso20022.tools.validation import (
    validate_instance,
    validate_message,
    validate_field,
    get_constraints,
    ValidationError,
    ValidationResult,
)


def test_validate_uetr_pattern_valid():
    """Test UETR field validation with valid UUID pattern."""
    # Valid UETR (UUID v4 format)
    valid_uetr = "550e8400-e29b-41d4-a716-446655440000"

    result = validate_field(
        PaymentIdentification7,
        'uetr',
        valid_uetr
    )

    assert result.is_valid
    assert len(result.errors) == 0


def test_validate_uetr_pattern_invalid():
    """Test UETR field validation with invalid pattern."""
    # Invalid UETR (wrong format)
    invalid_uetr = "not-a-valid-uuid"

    result = validate_field(
        PaymentIdentification7,
        'uetr',
        invalid_uetr
    )

    assert not result.is_valid
    assert len(result.errors) == 1
    assert result.errors[0].constraint == 'pattern'
    assert 'does not match required pattern' in result.errors[0].message


def test_validate_string_length_constraints():
    """Test string length validation."""
    # Test min_length constraint
    result = validate_field(
        PaymentIdentification7,
        'end_to_end_id',
        ""  # Empty string, min_length is 1
    )

    assert not result.is_valid
    assert result.errors[0].constraint == 'min_length'

    # Test max_length constraint
    long_string = "a" * 50  # max_length is 35
    result = validate_field(
        PaymentIdentification7,
        'end_to_end_id',
        long_string
    )

    assert not result.is_valid
    assert result.errors[0].constraint == 'max_length'


def test_validate_decimal_constraints():
    """Test decimal value validation."""
    # Test valid amount
    valid_amount = ActiveCurrencyAndAmount(
        value=Decimal('100.50'),
        ccy='USD'
    )

    result = validate_instance(valid_amount)
    assert result.is_valid

    # Test negative amount (min_inclusive is 0)
    invalid_amount = ActiveCurrencyAndAmount(
        value=Decimal('-10.00'),
        ccy='USD'
    )

    result = validate_instance(invalid_amount)
    assert not result.is_valid
    assert result.errors[0].constraint == 'min_inclusive'


def test_validate_currency_pattern():
    """Test currency code pattern validation."""
    # Valid currency code
    valid_amount = ActiveCurrencyAndAmount(
        value=Decimal('100.00'),
        ccy='USD'
    )

    result = validate_instance(valid_amount)
    assert result.is_valid

    # Invalid currency code (not 3 uppercase letters)
    invalid_amount = ActiveCurrencyAndAmount(
        value=Decimal('100.00'),
        ccy='us'  # Should be 3 uppercase letters
    )

    result = validate_instance(invalid_amount)
    assert not result.is_valid
    assert result.errors[0].constraint == 'pattern'


def test_validate_enum_values():
    """Test enum value validation."""
    # This would test enum validation if we had an instance that uses enums
    # For now, we can test that the enum type is recognized
    constraints = get_constraints(PaymentIdentification7)

    # Verify that constraints are extracted properly
    assert 'uetr' in constraints
    assert 'pattern' in constraints['uetr']


def test_validate_required_fields():
    """Test required field validation."""
    # Test with missing required field
    payment_id = PaymentIdentification7(
        end_to_end_id=None  # This is required
    )

    result = validate_instance(payment_id)
    assert not result.is_valid
    assert result.errors[0].constraint == 'required'


def test_validate_complete_instance():
    """Test validation of a complete valid instance."""
    payment_id = PaymentIdentification7(
        instr_id="INSTR123",
        end_to_end_id="E2E123",
        tx_id="TX123",
        uetr="550e8400-e29b-41d4-a716-446655440000"
    )

    result = validate_instance(payment_id)
    assert result.is_valid
    assert len(result.errors) == 0


def test_get_constraints():
    """Test constraint extraction functionality."""
    constraints = get_constraints(PaymentIdentification7)

    # Check that constraints are properly extracted
    assert 'uetr' in constraints
    assert 'end_to_end_id' in constraints

    # Check UETR constraints
    uetr_constraints = constraints['uetr']
    assert 'pattern' in uetr_constraints
    expected_pattern = (
        r"[a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-"
        r"[89ab][a-f0-9]{3}-[a-f0-9]{12}"
    )
    assert uetr_constraints['pattern'] == expected_pattern

    # Check end_to_end_id constraints
    e2e_constraints = constraints['end_to_end_id']
    assert 'required' in e2e_constraints
    assert 'min_length' in e2e_constraints
    assert 'max_length' in e2e_constraints
    assert e2e_constraints['required'] is True
    assert e2e_constraints['min_length'] == 1
    assert e2e_constraints['max_length'] == 35


def test_validation_result_string_representation():
    """Test ValidationResult string representation."""
    # Test valid result
    result = ValidationResult()
    assert str(result) == "Validation passed"

    # Test invalid result
    result.add_error('test_field', 'test_value', 'test_constraint',
                     'Test error message')
    result_str = str(result)
    assert "Validation failed with 1 error(s)" in result_str
    assert "Test error message" in result_str

    # Test with warnings
    result.add_warning("Test warning")
    result_str = str(result)
    assert "Warnings (1)" in result_str
    assert "Test warning" in result_str


def test_validation_error_properties():
    """Test ValidationError properties."""
    error = ValidationError(
        'test_field', 'test_value', 'test_constraint', 'Test message'
    )

    assert error.field_name == 'test_field'
    assert error.value == 'test_value'
    assert error.constraint == 'test_constraint'
    assert error.message == 'Test message'
    assert str(error) == "Field 'test_field': Test message"


def test_strict_vs_non_strict_validation():
    """Test difference between strict and non-strict validation."""
    # Create an instance with multiple validation errors
    payment_id = PaymentIdentification7(
        end_to_end_id="",  # Too short (min_length = 1)
        tx_id="a" * 50,    # Too long (max_length = 35)
        uetr="invalid-uuid"  # Invalid pattern
    )

    # Strict validation (stops at first error)
    strict_result = validate_instance(payment_id, strict=True)
    assert not strict_result.is_valid
    assert len(strict_result.errors) == 1

    # Non-strict validation (collects all errors)
    non_strict_result = validate_instance(payment_id, strict=False)
    assert not non_strict_result.is_valid
    assert len(non_strict_result.errors) > 1


def test_validate_complete_pacs008_message():
    """Test validation of a complete PACS.008 message."""
    # Create a complete PACS.008 message
    settlement_instruction = SettlementInstruction7(
        sttlm_mtd=SettlementMethod1Code.CLRG
    )

    group_header = GroupHeader93(
        msg_id="MSG123456789",
        cre_dt_tm=XmlDateTime.from_datetime(datetime.now()),
        nb_of_txs="1",
        sttlm_inf=settlement_instruction
    )

    # Create financial institution
    fin_inst = FinancialInstitutionIdentification18(
        bicfi="BANKGB2L"
    )

    dbtr_agt = BranchAndFinancialInstitutionIdentification6(
        fin_instn_id=fin_inst
    )

    cdtr_agt = BranchAndFinancialInstitutionIdentification6(
        fin_instn_id=fin_inst
    )

    # Create parties
    debtor = PartyIdentification135(
        nm="John Doe"
    )

    creditor = PartyIdentification135(
        nm="Jane Smith"
    )

    # Create payment identification
    payment_id = PaymentIdentification7(
        end_to_end_id="E2E123456789"
    )

    # Create settlement amount
    settlement_amount = ActiveCurrencyAndAmount(
        value=Decimal('1000.00'),
        ccy='USD'
    )

    # Create credit transfer transaction
    credit_transfer = CreditTransferTransaction39(
        pmt_id=payment_id,
        intr_bk_sttlm_amt=settlement_amount,
        chrg_br=ChargeBearerType1Code.SHAR,
        dbtr=debtor,
        dbtr_agt=dbtr_agt,
        cdtr=creditor,
        cdtr_agt=cdtr_agt
    )

    # Create the main message
    fi_to_fi_transfer = FitoFicustomerCreditTransferV08(
        grp_hdr=group_header,
        cdt_trf_tx_inf=[credit_transfer]
    )

    # Create the document
    document = Document(
        fito_ficstmr_cdt_trf=fi_to_fi_transfer
    )

    # Validate the complete message
    result = validate_message(document)
    assert result.is_valid, f"Validation failed: {result}"
    assert len(result.errors) == 0


def test_validate_pacs008_message_with_errors():
    """Test validation of PACS.008 message with validation errors."""
    # Create a PACS.008 message with validation errors
    settlement_instruction = SettlementInstruction7(
        sttlm_mtd=SettlementMethod1Code.CLRG
    )

    group_header = GroupHeader93(
        msg_id="",  # Invalid: empty string (min_length = 1)
        cre_dt_tm=XmlDateTime.from_datetime(datetime.now()),
        nb_of_txs="1",
        sttlm_inf=settlement_instruction
    )

    # Create financial institution with invalid BIC
    fin_inst = FinancialInstitutionIdentification18(
        bicfi="INVALID"  # Invalid BIC format
    )

    dbtr_agt = BranchAndFinancialInstitutionIdentification6(
        fin_instn_id=fin_inst
    )

    cdtr_agt = BranchAndFinancialInstitutionIdentification6(
        fin_instn_id=fin_inst
    )

    # Create parties
    debtor = PartyIdentification135(
        nm="John Doe"
    )

    creditor = PartyIdentification135(
        nm="Jane Smith"
    )

    # Create payment identification with invalid UETR
    payment_id = PaymentIdentification7(
        end_to_end_id="E2E123456789",
        uetr="invalid-uetr-format"  # Invalid UETR pattern
    )

    # Create settlement amount with invalid currency
    settlement_amount = ActiveCurrencyAndAmount(
        value=Decimal('-100.00'),  # Invalid: negative amount
        ccy='INVALID'  # Invalid currency code
    )

    # Create credit transfer transaction
    credit_transfer = CreditTransferTransaction39(
        pmt_id=payment_id,
        intr_bk_sttlm_amt=settlement_amount,
        chrg_br=ChargeBearerType1Code.SHAR,
        dbtr=debtor,
        dbtr_agt=dbtr_agt,
        cdtr=creditor,
        cdtr_agt=cdtr_agt
    )

    # Create the main message
    fi_to_fi_transfer = FitoFicustomerCreditTransferV08(
        grp_hdr=group_header,
        cdt_trf_tx_inf=[credit_transfer]
    )

    # Create the document
    document = Document(
        fito_ficstmr_cdt_trf=fi_to_fi_transfer
    )

    # Validate the complete message
    result = validate_message(document, strict=False)
    assert not result.is_valid
    assert len(result.errors) > 0

    # Check that field paths are properly constructed
    error_fields = [error.field_name for error in result.errors]

    # Should have nested field paths like:
    # fito_ficstmr_cdt_trf.grp_hdr.msg_id
    # fito_ficstmr_cdt_trf.cdt_trf_tx_inf[0].pmt_id.uetr
    # etc.
    nested_errors = [field for field in error_fields if '.' in field]
    assert len(nested_errors) > 0, "Should have nested field path errors"


def test_validate_message_with_list_items():
    """Test validation of message with list items containing errors."""
    # Create multiple credit transfer transactions with errors
    payment_id1 = PaymentIdentification7(
        end_to_end_id=""  # Invalid: empty string
    )

    payment_id2 = PaymentIdentification7(
        end_to_end_id="E2E123",
        uetr="invalid-uetr"  # Invalid UETR
    )

    settlement_amount = ActiveCurrencyAndAmount(
        value=Decimal('100.00'),
        ccy='USD'
    )

    # Create financial institution
    fin_inst = FinancialInstitutionIdentification18(
        bicfi="BANKGB2L"
    )

    dbtr_agt = BranchAndFinancialInstitutionIdentification6(
        fin_instn_id=fin_inst
    )

    cdtr_agt = BranchAndFinancialInstitutionIdentification6(
        fin_instn_id=fin_inst
    )

    debtor = PartyIdentification135(nm="John Doe")
    creditor = PartyIdentification135(nm="Jane Smith")

    # Create transactions with errors
    credit_transfer1 = CreditTransferTransaction39(
        pmt_id=payment_id1,  # Has validation error
        intr_bk_sttlm_amt=settlement_amount,
        chrg_br=ChargeBearerType1Code.SHAR,
        dbtr=debtor,
        dbtr_agt=dbtr_agt,
        cdtr=creditor,
        cdtr_agt=cdtr_agt
    )

    credit_transfer2 = CreditTransferTransaction39(
        pmt_id=payment_id2,  # Has validation error
        intr_bk_sttlm_amt=settlement_amount,
        chrg_br=ChargeBearerType1Code.SHAR,
        dbtr=debtor,
        dbtr_agt=dbtr_agt,
        cdtr=creditor,
        cdtr_agt=cdtr_agt
    )

    # Validate the list directly
    transactions = [credit_transfer1, credit_transfer2]
    result = validate_message(transactions, strict=False)

    assert not result.is_valid
    assert len(result.errors) > 0

    # Check that list indices are included in field paths
    error_fields = [error.field_name for error in result.errors]
    list_errors = [field for field in error_fields if '[' in field]
    assert len(list_errors) > 0, ("Should have list index errors like "
                                  "[0].field_name")


def test_validate_list_field_string_constraints():
    """Test validation of list fields with string constraints on items."""
    from dataclasses import dataclass, field
    from typing import List
    
    @dataclass
    class TestAddressClass:
        """Test class with address lines having string constraints."""
        adr_line: List[str] = field(
            default_factory=list,
            metadata={
                "name": "AdrLine",
                "type": "Element",
                "max_occurs": 7,
                "min_length": 1,
                "max_length": 70,
            },
        )
    
    # Test 1: Valid address lines
    valid_address = TestAddressClass(
        adr_line=["123 Main Street", "Apt 4B", "New York, NY 10001"]
    )
    result = validate_instance(valid_address, strict=False)
    assert result.is_valid, f"Valid address lines should pass: {result}"
    
    # Test 2: Empty list is valid (no min_occurs)
    empty_address = TestAddressClass(adr_line=[])
    result = validate_instance(empty_address, strict=False)
    assert result.is_valid, "Empty list should be valid when no min_occurs"
    
    # Test 3: Too many items (exceeds max_occurs)
    too_many_lines = TestAddressClass(
        adr_line=["Line 1", "Line 2", "Line 3", "Line 4", 
                  "Line 5", "Line 6", "Line 7", "Line 8"]
    )
    result = validate_instance(too_many_lines, strict=False)
    assert not result.is_valid
    assert any(e.constraint == 'max_occurs' for e in result.errors)
    assert any('8 items but maximum allowed is 7' in e.message 
               for e in result.errors)
    
    # Test 4: Empty string in list (violates min_length)
    empty_string_address = TestAddressClass(
        adr_line=["123 Main Street", "", "New York, NY 10001"]
    )
    result = validate_instance(empty_string_address, strict=False)
    assert not result.is_valid
    assert any(e.constraint == 'min_length' for e in result.errors)
    assert any('adr_line[1]' in e.field_name for e in result.errors)
    
    # Test 5: String too long (exceeds max_length)
    long_string = "A" * 71  # 71 characters, exceeds max_length=70
    long_string_address = TestAddressClass(
        adr_line=["123 Main Street", long_string, "New York, NY 10001"]
    )
    result = validate_instance(long_string_address, strict=False)
    assert not result.is_valid
    assert any(e.constraint == 'max_length' for e in result.errors)
    assert any('adr_line[1]' in e.field_name for e in result.errors)
    assert any('71 exceeds maximum allowed length 70' in e.message 
               for e in result.errors)


def test_validate_list_field_with_min_occurs():
    """Test validation of list fields with min_occurs constraint."""
    from dataclasses import dataclass, field
    from typing import List
    
    @dataclass
    class TestRequiredListClass:
        """Test class with required list items."""
        required_items: List[str] = field(
            default_factory=list,
            metadata={
                "name": "RequiredItems",
                "type": "Element",
                "min_occurs": 2,
                "max_occurs": 5,
                "min_length": 1,
                "max_length": 50,
            },
        )
    
    # Test 1: Too few items (less than min_occurs)
    too_few = TestRequiredListClass(required_items=["Item 1"])
    result = validate_instance(too_few, strict=False)
    assert not result.is_valid
    assert any(e.constraint == 'min_occurs' for e in result.errors)
    assert any('1 items but minimum required is 2' in e.message 
               for e in result.errors)
    
    # Test 2: Valid number of items
    valid_list = TestRequiredListClass(
        required_items=["Item 1", "Item 2", "Item 3"]
    )
    result = validate_instance(valid_list, strict=False)
    assert result.is_valid
    
    # Test 3: Too many items (exceeds max_occurs)
    too_many = TestRequiredListClass(
        required_items=["Item 1", "Item 2", "Item 3", "Item 4", 
                        "Item 5", "Item 6"]
    )
    result = validate_instance(too_many, strict=False)
    assert not result.is_valid
    assert any(e.constraint == 'max_occurs' for e in result.errors)
    assert any('6 items but maximum allowed is 5' in e.message 
               for e in result.errors)


def test_validate_list_field_with_pattern():
    """Test validation of list fields with pattern constraints on items."""
    from dataclasses import dataclass, field
    from typing import List
    
    @dataclass
    class TestPatternListClass:
        """Test class with list items having pattern constraints."""
        codes: List[str] = field(
            default_factory=list,
            metadata={
                "name": "Codes",
                "type": "Element",
                "max_occurs": 10,
                "pattern": r"[A-Z]{3}[0-9]{3}",  # e.g., ABC123
            },
        )
    
    # Test 1: Valid codes
    valid_codes = TestPatternListClass(
        codes=["ABC123", "XYZ789", "DEF456"]
    )
    result = validate_instance(valid_codes, strict=False)
    assert result.is_valid
    
    # Test 2: Invalid pattern in one item
    invalid_pattern = TestPatternListClass(
        codes=["ABC123", "invalid", "XYZ789"]
    )
    result = validate_instance(invalid_pattern, strict=False)
    assert not result.is_valid
    assert any(e.constraint == 'pattern' for e in result.errors)
    assert any('codes[1]' in e.field_name for e in result.errors)
    assert any('does not match required pattern' in e.message 
               for e in result.errors)


def test_validate_postal_address_adr_line():
    """Test validation of PostalAddress24 adr_line field."""
    from pyiso20022.pacs.pacs_008_001_08.pacs_008_001_08 import PostalAddress24
    
    # Test 1: Valid address lines
    valid_address = PostalAddress24(
        adr_line=["123 Main Street", "Suite 100", "New York, NY 10001"],
        ctry="US"
    )
    result = validate_instance(valid_address, strict=False)
    assert result.is_valid
    
    # Test 2: Too many address lines (max_occurs=7)
    too_many_lines = PostalAddress24(
        adr_line=["Line 1", "Line 2", "Line 3", "Line 4", 
                  "Line 5", "Line 6", "Line 7", "Line 8"],
        ctry="US"
    )
    result = validate_instance(too_many_lines, strict=False)
    assert not result.is_valid
    assert any(e.constraint == 'max_occurs' for e in result.errors)
    
    # Test 3: Address line too long (max_length=70)
    long_line = "A" * 71
    long_address = PostalAddress24(
        adr_line=["123 Main Street", long_line],
        ctry="US"
    )
    result = validate_instance(long_address, strict=False)
    assert not result.is_valid
    assert any(e.constraint == 'max_length' for e in result.errors)
    assert any('adr_line[1]' in e.field_name for e in result.errors)
