# ISO20022 Validation System

This validation system provides comprehensive validation for ISO20022 dataclasses based on their metadata constraints, without requiring XSD files. It extracts validation rules directly from the field metadata in the generated dataclasses.

## Features

- **Complete Message Validation**: Validates entire ISO20022 messages recursively, including all nested structures
- **Pattern Validation**: Validates string fields against regex patterns (e.g., UETR UUID format)
- **Length Constraints**: Validates minimum and maximum string lengths
- **Numeric Constraints**: Validates decimal values with min/max inclusive/exclusive bounds
- **Decimal Precision**: Validates total digits and fraction digits for Decimal fields
- **Required Fields**: Validates that required fields are not None
- **Enum Validation**: Validates enum values against allowed options
- **List Constraints**: Validates minimum and maximum occurrences for list fields
- **Nested Field Path Reporting**: Provides detailed field paths for errors in complex message structures
- **Comprehensive Error Reporting**: Collects all validation errors with detailed messages

## Installation

The validation system is included in the `pyiso20022.tools` module. No additional installation is required.

## Quick Start

```python
from pyiso20022.pacs.pacs_008_001_08.pacs_008_001_08 import PaymentIdentification7
from pyiso20022.tools.validation import validate_instance, validate_field

# Validate a single field
result = validate_field(PaymentIdentification7, 'uetr', 'invalid-uuid')
if not result.is_valid:
    print(f"Validation failed: {result.errors[0].message}")

# Validate a complete instance
payment = PaymentIdentification7(
    end_to_end_id="E2E123",
    uetr="550e8400-e29b-41d4-a716-446655440000"
)
result = validate_instance(payment)
print(f"Valid: {result.is_valid}")
```

## API Reference

### Core Functions

#### `validate_instance(instance, strict=True)`
Validates a complete dataclass instance against all its field constraints.

**Parameters:**
- `instance`: The dataclass instance to validate
- `strict`: If True, stops on first error. If False, collects all errors.

**Returns:** `ValidationResult`

#### `validate_field(dataclass_type, field_name, value)`
Validates a single field value against its constraints.

**Parameters:**
- `dataclass_type`: The dataclass type containing the field
- `field_name`: Name of the field to validate
- `value`: Value to validate

**Returns:** `ValidationResult`

#### `validate_message(instance, strict=True)`
Validates a complete ISO20022 message recursively, including all nested structures and lists.

**Parameters:**
- `instance`: The message instance to validate (typically Document or root message)
- `strict`: If True, stops on first error. If False, collects all errors.

**Returns:** `ValidationResult` with nested field paths for errors

#### `get_constraints(dataclass_type)`
Extracts all validation constraints for fields in a dataclass.

**Parameters:**
- `dataclass_type`: The dataclass type to analyze

**Returns:** Dictionary mapping field names to their constraints

### Classes

#### `ValidationResult`
Contains the results of a validation operation.

**Properties:**
- `is_valid`: Boolean indicating if validation passed
- `errors`: List of `ValidationError` objects
- `warnings`: List of warning messages

**Methods:**
- `add_error(field_name, value, constraint, message)`: Add a validation error
- `add_warning(message)`: Add a validation warning
- `__str__()`: Returns formatted validation results

#### `ValidationError`
Represents a validation error.

**Properties:**
- `field_name`: Name of the field that failed validation
- `value`: The value that failed validation
- `constraint`: The constraint that was violated
- `message`: Human-readable error message

## Supported Constraints

The validation system supports the following constraint types from field metadata:

### String Constraints
- `pattern`: Regex pattern validation
- `min_length`: Minimum string length
- `max_length`: Maximum string length

### Numeric Constraints
- `min_inclusive`: Minimum value (inclusive)
- `max_inclusive`: Maximum value (inclusive)
- `min_exclusive`: Minimum value (exclusive)
- `max_exclusive`: Maximum value (exclusive)

### Decimal Constraints
- `total_digits`: Maximum total number of digits
- `fraction_digits`: Maximum number of decimal places

### Field Constraints
- `required`: Field must not be None

### List Constraints
- `min_occurs`: Minimum number of list items
- `max_occurs`: Maximum number of list items

## Examples

### Example 1: UETR Validation
```python
from pyiso20022.pacs.pacs_008_001_08.pacs_008_001_08 import PaymentIdentification7
from pyiso20022.tools.validation import validate_field

# Valid UETR (UUID v4 format)
result = validate_field(
    PaymentIdentification7, 
    'uetr', 
    '550e8400-e29b-41d4-a716-446655440000'
)
print(f"Valid: {result.is_valid}")  # True

# Invalid UETR
result = validate_field(
    PaymentIdentification7, 
    'uetr', 
    'not-a-valid-uuid'
)
print(f"Valid: {result.is_valid}")  # False
print(f"Error: {result.errors[0].message}")
```

### Example 2: Currency Amount Validation
```python
from decimal import Decimal
from pyiso20022.pacs.pacs_008_001_08.pacs_008_001_08 import ActiveCurrencyAndAmount
from pyiso20022.tools.validation import validate_instance

# Valid amount
amount = ActiveCurrencyAndAmount(
    value=Decimal('100.50'),
    ccy='USD'
)
result = validate_instance(amount)
print(f"Valid: {result.is_valid}")  # True

# Invalid amount (negative value)
amount = ActiveCurrencyAndAmount(
    value=Decimal('-10.00'),
    ccy='USD'
)
result = validate_instance(amount)
print(f"Valid: {result.is_valid}")  # False
```

### Example 3: Multiple Validation Errors
```python
from pyiso20022.pacs.pacs_008_001_08.pacs_008_001_08 import PaymentIdentification7
from pyiso20022.tools.validation import validate_instance

# Instance with multiple validation errors
payment = PaymentIdentification7(
    end_to_end_id="",  # Too short (min_length = 1)
    tx_id="a" * 50,    # Too long (max_length = 35)
    uetr="invalid-uuid"  # Invalid pattern
)

# Non-strict validation (collect all errors)
result = validate_instance(payment, strict=False)
print(f"Valid: {result.is_valid}")  # False
print(f"Number of errors: {len(result.errors)}")  # 3

for error in result.errors:
    print(f"- {error}")
```

### Example 4: Complete PACS.008 Message Validation
```python
from decimal import Decimal
from datetime import datetime
from xsdata.models.datatype import XmlDateTime
from pyiso20022.pacs.pacs_008_001_08.pacs_008_001_08 import (
    Document, FitoFicustomerCreditTransferV08, GroupHeader93,
    CreditTransferTransaction39, PaymentIdentification7,
    ActiveCurrencyAndAmount, BranchAndFinancialInstitutionIdentification6,
    FinancialInstitutionIdentification18, PartyIdentification135,
    SettlementInstruction7, SettlementMethod1Code, ChargeBearerType1Code
)
from pyiso20022.tools.validation import validate_message

# Create a complete PACS.008 message
settlement_instruction = SettlementInstruction7(
    sttlm_mtd=SettlementMethod1Code.CLRG
)

group_header = GroupHeader93(
    msg_id="MSG20250111001",
    cre_dt_tm=XmlDateTime.from_datetime(datetime.now()),
    nb_of_txs="1",
    sttlm_inf=settlement_instruction
)

# Create financial institutions
debtor_agent = BranchAndFinancialInstitutionIdentification6(
    fin_instn_id=FinancialInstitutionIdentification18(bicfi="DEUTDEFF")
)

creditor_agent = BranchAndFinancialInstitutionIdentification6(
    fin_instn_id=FinancialInstitutionIdentification18(bicfi="CHASUS33")
)

# Create payment transaction
payment_id = PaymentIdentification7(
    end_to_end_id="E2E20250111001",
    uetr="550e8400-e29b-41d4-a716-446655440000"
)

settlement_amount = ActiveCurrencyAndAmount(
    value=Decimal('50000.00'),
    ccy='USD'
)

credit_transfer = CreditTransferTransaction39(
    pmt_id=payment_id,
    intr_bk_sttlm_amt=settlement_amount,
    chrg_br=ChargeBearerType1Code.SHAR,
    dbtr=PartyIdentification135(nm="ACME Corporation Ltd"),
    dbtr_agt=debtor_agent,
    cdtr=PartyIdentification135(nm="Global Suppliers Inc"),
    cdtr_agt=creditor_agent
)

# Create the complete message
fi_to_fi_transfer = FitoFicustomerCreditTransferV08(
    grp_hdr=group_header,
    cdt_trf_tx_inf=[credit_transfer]
)

document = Document(fito_ficstmr_cdt_trf=fi_to_fi_transfer)

# Validate the complete message
result = validate_message(document)
print(f"Valid: {result.is_valid}")  # True

# Example with validation errors
invalid_payment_id = PaymentIdentification7(
    end_to_end_id="",  # Invalid: empty string
    uetr="invalid-uuid"  # Invalid: wrong pattern
)

invalid_credit_transfer = CreditTransferTransaction39(
    pmt_id=invalid_payment_id,
    intr_bk_sttlm_amt=settlement_amount,
    chrg_br=ChargeBearerType1Code.SHAR,
    dbtr=PartyIdentification135(nm="ACME Corporation Ltd"),
    dbtr_agt=debtor_agent,
    cdtr=PartyIdentification135(nm="Global Suppliers Inc"),
    cdtr_agt=creditor_agent
)

invalid_transfer = FitoFicustomerCreditTransferV08(
    grp_hdr=group_header,
    cdt_trf_tx_inf=[invalid_credit_transfer]
)

invalid_document = Document(fito_ficstmr_cdt_trf=invalid_transfer)

# Validate message with errors
result = validate_message(invalid_document, strict=False)
print(f"Valid: {result.is_valid}")  # False

for error in result.errors:
    print(f"Field: {error.field_name}")
    print(f"Error: {error.message}")
    # Field paths will show nested structure like:
    # fito_ficstmr_cdt_trf.cdt_trf_tx_inf.[0].pmt_id.end_to_end_id
    # fito_ficstmr_cdt_trf.cdt_trf_tx_inf.[0].pmt_id.uetr
```

### Example 5: Getting Field Constraints
```python
from pyiso20022.pacs.pacs_008_001_08.pacs_008_001_08 import PaymentIdentification7
from pyiso20022.tools.validation import get_constraints

constraints = get_constraints(PaymentIdentification7)

# Check UETR constraints
uetr_constraints = constraints['uetr']
print(f"UETR pattern: {uetr_constraints['pattern']}")

# Check end_to_end_id constraints
e2e_constraints = constraints['end_to_end_id']
print(f"Required: {e2e_constraints['required']}")
print(f"Min length: {e2e_constraints['min_length']}")
print(f"Max length: {e2e_constraints['max_length']}")
```

## Integration with IDE

The validation system works alongside your IDE's existing tooltip functionality. While your IDE shows the constraints as tooltips, this validation system allows you to programmatically validate values against those same constraints at runtime.

## Error Handling

The validation system provides detailed error messages that include:
- The field name that failed validation
- The actual value that was invalid
- The specific constraint that was violated
- A human-readable description of the problem

## Performance

The validation system is designed to be efficient:
- Constraints are extracted once and cached
- Validation logic is optimized for common constraint types
- Optional strict mode allows early termination on first error

## Testing

Run the validation system tests:
```bash
python -m pytest tests/test_validation.py -v
```

Run the example demonstration:
```bash
python example_validation.py
```

## Supported Message Types

The validation system works with all ISO20022 dataclasses in the pyiso20022 package, including:
- PACS (Payments Clearing and Settlement)
- PAIN (Payments Initiation)
- CAMT (Cash Management)
- REMT (Remittance)
- ADMI (Administration)
- HEAD (Business Application Header)

## Contributing

To extend the validation system:
1. Add new constraint validators to the `type_validators` dictionary in `ISO20022Validator`
2. Implement the validation logic following the existing pattern
3. Add comprehensive tests for the new constraint type
4. Update this documentation

## License

This validation system is part of the pyiso20022 package and follows the same license terms.
