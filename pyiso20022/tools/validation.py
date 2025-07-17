"""ISO20022 Dataclass Validation System.
This module provides validation functionality for ISO20022 dataclasses based on
their metadata constraints without requiring XSD files. It extracts validation
rules from field metadata and applies them to validate field values.
"""
import inspect
import re
from dataclasses import fields, is_dataclass
from decimal import Decimal
from enum import Enum
from typing import Any, Dict, List, Optional, Type, Union

# XmlDate, XmlDateTime, XmlTime are available for future use


class ValidationError(Exception):
    """Raised when validation fails."""
    def __init__(self, field_name: str, value: Any, constraint: str,
                 message: str):
        """Initialize ValidationError.
        Args:
            field_name: Name of the field that failed validation
            value: The value that failed validation
            constraint: The constraint that was violated
            message: Human-readable error message
        """
        self.field_name = field_name
        self.value = value
        self.constraint = constraint
        self.message = message
        super().__init__(f"Field '{field_name}': {message}")


class ValidationResult:
    """Contains the results of a validation operation."""
    def __init__(self):
        """Initialize ValidationResult."""
        self.errors: List[ValidationError] = []
        self.warnings: List[str] = []
        self.is_valid = True

    def add_error(self, field_name: str, value: Any, constraint: str,
                  message: str):
        """Add a validation error.
        Args:
            field_name: Name of the field that failed validation
            value: The value that failed validation
            constraint: The constraint that was violated
            message: Human-readable error message
        """
        error = ValidationError(field_name, value, constraint, message)
        self.errors.append(error)
        self.is_valid = False

    def add_warning(self, message: str):
        """Add a validation warning.
        Args:
            message: Warning message
        """
        self.warnings.append(message)

    def to_yaml(self) -> str:
        """Return YAML representation of validation result."""
        import yaml

        result_dict = {
            'validation_status': 'PASSED' if self.is_valid else 'FAILED',
            'error_count': len(self.errors),
            'warning_count': len(self.warnings)
        }

        if self.errors:
            result_dict['errors'] = []
            for error in self.errors:
                error_dict = {
                    'field': error.field_name,
                    'constraint': error.constraint,
                    'value': (str(error.value) if error.value is not None
                              else None),
                    'message': error.message
                }
                result_dict['errors'].append(error_dict)

        if self.warnings:
            result_dict['warnings'] = self.warnings

        return yaml.dump(result_dict, default_flow_style=False,
                         sort_keys=False)

    def to_summary_yaml(self) -> str:
        """Return concise YAML summary of validation result."""
        import yaml

        summary = {
            'status': 'PASSED' if self.is_valid else 'FAILED',
            'errors': len(self.errors),
            'warnings': len(self.warnings)
        }

        if not self.is_valid and self.errors:
            # Group errors by constraint type
            error_types = {}
            for error in self.errors:
                constraint = error.constraint
                if constraint not in error_types:
                    error_types[constraint] = 0
                error_types[constraint] += 1
            summary['error_breakdown'] = error_types

        return yaml.dump(summary, default_flow_style=False, sort_keys=False)

    def __str__(self):
        """Return string representation of validation result."""
        if self.is_valid:
            return "Validation passed"
        result = f"Validation failed with {len(self.errors)} error(s):\n"
        for error in self.errors:
            result += f"  - {error}\n"
        if self.warnings:
            result += f"\nWarnings ({len(self.warnings)}):\n"
            for warning in self.warnings:
                result += f"  - {warning}\n"
        return result


class ISO20022Validator:
    """Validates ISO20022 dataclass instances based on metadata constraints."""
    def __init__(self):
        """Initialize ISO20022Validator."""
        self.type_validators = {
            'pattern': self._validate_pattern,
            'min_length': self._validate_min_length,
            'max_length': self._validate_max_length,
            'min_inclusive': self._validate_min_inclusive,
            'max_inclusive': self._validate_max_inclusive,
            'min_exclusive': self._validate_min_exclusive,
            'max_exclusive': self._validate_max_exclusive,
            'total_digits': self._validate_total_digits,
            'fraction_digits': self._validate_fraction_digits,
            'required': self._validate_required,
            'min_occurs': self._validate_min_occurs,
            'max_occurs': self._validate_max_occurs,
        }
        self._validation_path = []  # Track validation path for nested objects

    def validate_message(self, instance: Any,
                         strict: bool = True) -> ValidationResult:
        """Validate a complete ISO20022 message recursively.
        This method validates an entire message structure, including all nested
        dataclass instances, lists, and their constraints.
        Args:
            instance: The message instance to validate (typically Document or
                     root)
            strict: If True, stops on first error. If False, collects all
                   errors.
        Returns:
            ValidationResult containing validation results for entire message
        """
        self._validation_path = []
        return self._validate_recursive(instance, strict)

    def _validate_recursive(self, instance: Any,
                            strict: bool) -> ValidationResult:
        """Recursively validate an instance and all its nested components.
        Args:
            instance: The instance to validate
            strict: Whether to stop on first error
        Returns:
            ValidationResult containing all validation errors found
        """
        result = ValidationResult()
        if instance is None:
            return result
        # Handle lists
        if isinstance(instance, list):
            for i, item in enumerate(instance):
                self._validation_path.append(f"[{i}]")
                item_result = self._validate_recursive(item, strict)
                self._merge_results(result, item_result)
                self._validation_path.pop()
                if strict and not result.is_valid:
                    break
            return result
        # Handle dataclass instances
        if is_dataclass(instance):
            # First validate the current instance
            current_result = self.validate(instance, strict=False)
            self._merge_results(result, current_result)
            if strict and not result.is_valid:
                return result
            # Then recursively validate nested fields
            dataclass_fields = fields(instance)
            for field in dataclass_fields:
                field_value = getattr(instance, field.name)
                if field_value is not None:
                    self._validation_path.append(field.name)
                    # Recursively validate nested objects
                    nested_result = self._validate_recursive(field_value,
                                                             strict)
                    self._merge_results(result, nested_result)
                    self._validation_path.pop()
                    if strict and not result.is_valid:
                        break
        return result

    def _merge_results(self, target: ValidationResult,
                       source: ValidationResult):
        """Merge validation results, updating field names with path context.
        Args:
            target: The target ValidationResult to merge into
            source: The source ValidationResult to merge from
        """
        path_prefix = ".".join(self._validation_path)
        for error in source.errors:
            # Update field name with full path, avoiding duplicates
            if path_prefix and not error.field_name.startswith(path_prefix):
                full_field_name = f"{path_prefix}.{error.field_name}"
            else:
                full_field_name = error.field_name
            target.add_error(full_field_name, error.value,
                             error.constraint, error.message)
        for warning in source.warnings:
            # Update warning with path context if needed
            full_warning = (f"{path_prefix}: {warning}"
                            if path_prefix else warning)
            target.add_warning(full_warning)

    def validate(self, instance: Any, strict: bool = True) -> ValidationResult:
        """Validate a dataclass instance against its metadata constraints.
        Args:
            instance: The dataclass instance to validate
            strict: If True, raises ValidationError on first failure.
                   If False, collects all errors.
        Returns:
            ValidationResult containing validation results
        Raises:
            ValueError: If instance is not a dataclass
        """
        if not is_dataclass(instance):
            raise ValueError("Instance must be a dataclass")
        result = ValidationResult()
        # Get all fields for this dataclass
        dataclass_fields = fields(instance)
        for field in dataclass_fields:
            field_value = getattr(instance, field.name)
            self._validate_field(field, field_value, result, strict)
            if strict and not result.is_valid:
                break
        return result

    def validate_field_value(self, dataclass_type: Type, field_name: str,
                             value: Any) -> ValidationResult:
        """Validate a single field value against its constraints.
        Args:
            dataclass_type: The dataclass type containing the field
            field_name: Name of the field to validate
            value: Value to validate
        Returns:
            ValidationResult containing validation results
        Raises:
            ValueError: If dataclass_type is not a dataclass or field not found
        """
        if not is_dataclass(dataclass_type):
            raise ValueError("dataclass_type must be a dataclass")
        # Find the field
        dataclass_fields = fields(dataclass_type)
        target_field = None
        for field in dataclass_fields:
            if field.name == field_name:
                target_field = field
                break
        if target_field is None:
            raise ValueError(
                f"Field '{field_name}' not found in {dataclass_type.__name__}"
            )
        result = ValidationResult()
        self._validate_field(target_field, value, result, strict=False)
        return result

    def _validate_field(self, field, value: Any, result: ValidationResult,
                        strict: bool):
        """Validate a single field against its metadata constraints.
        Args:
            field: The dataclass field to validate
            value: The value to validate
            result: ValidationResult to add errors to
            strict: Whether to stop on first error
        """
        metadata = field.metadata
        field_name = field.name
        # Skip validation if value is None and field is optional
        if value is None:
            if metadata.get('required', False):
                result.add_error(
                    field_name, value, 'required',
                    'Field is required but value is None'
                )
            return

        # Special handling for list fields
        if isinstance(value, list):
            # First validate list-specific constraints (min_occurs, max_occurs)
            self._validate_list_constraints(field, value, result)

            # For lists, apply string constraints to each item,
            # not the list itself
            string_constraints = ['min_length', 'max_length', 'pattern']
            list_item_constraints = {k: v for k, v in metadata.items()
                                     if k in string_constraints}

            # Validate each item in the list
            if list_item_constraints:
                for i, item in enumerate(value):
                    for constraint_name, constraint_value in (
                            list_item_constraints.items()):
                        if constraint_name in self.type_validators:
                            try:
                                self.type_validators[constraint_name](
                                    f"{field_name}[{i}]", item,
                                    constraint_value, result
                                )
                            except Exception as e:
                                result.add_error(
                                    f"{field_name}[{i}]", item,
                                    constraint_name,
                                    f"Validation error: {str(e)}"
                                )
                            if strict and not result.is_valid:
                                break
                    if strict and not result.is_valid:
                        break

            # Skip the normal constraint validation for lists
            non_list_constraints = {
                k: v for k, v in metadata.items()
                if (k in self.type_validators and
                    k not in string_constraints and
                    k not in ['min_occurs', 'max_occurs'])
            }
        else:
            # For non-list fields, validate all constraints normally
            non_list_constraints = {k: v for k, v in metadata.items()
                                    if k in self.type_validators}

        # Validate non-list constraints
        for constraint_name, constraint_value in non_list_constraints.items():
            try:
                self.type_validators[constraint_name](
                    field_name, value, constraint_value, result
                )
            except Exception as e:
                result.add_error(
                    field_name, value, constraint_name,
                    f"Validation error: {str(e)}"
                )
            if strict and not result.is_valid:
                break

        # Validate enum values
        enum_type = self._get_enum_type(field.type)
        if enum_type and value is not None:
            self._validate_enum(field_name, value, enum_type, result)

    def _get_enum_type(self, field_type) -> Optional[Type[Enum]]:
        """Extract enum type from field type annotation.
        Args:
            field_type: The field type annotation
        Returns:
            Enum type if found, None otherwise
        """
        if (hasattr(field_type, '__origin__') and
                field_type.__origin__ is Union):
            # Handle Optional[EnumType] case
            args = field_type.__args__
            for arg in args:
                if (arg is not type(None) and inspect.isclass(arg) and
                        issubclass(arg, Enum)):
                    return arg
        elif inspect.isclass(field_type) and issubclass(field_type, Enum):
            return field_type
        return None

    def _validate_pattern(self, field_name: str, value: Any, pattern: str,
                          result: ValidationResult):
        """Validate regex pattern constraint.
        Args:
            field_name: Name of the field being validated
            value: Value to validate
            pattern: Regex pattern to match
            result: ValidationResult to add errors to
        """
        if not isinstance(value, str):
            return  # Pattern only applies to strings
        try:
            if not re.match(pattern, value):
                result.add_error(
                    field_name, value, 'pattern',
                    f"Value '{value}' does not match required pattern "
                    f"'{pattern}'"
                )
        except re.error as e:
            result.add_error(
                field_name, value, 'pattern',
                f"Invalid regex pattern '{pattern}': {str(e)}"
            )

    def _validate_min_length(self, field_name: str, value: Any,
                             min_length: int, result: ValidationResult):
        """Validate minimum length constraint.
        Args:
            field_name: Name of the field being validated
            value: Value to validate
            min_length: Minimum required length
            result: ValidationResult to add errors to
        """
        if hasattr(value, '__len__'):
            if len(value) < min_length:
                result.add_error(
                    field_name, value, 'min_length',
                    f"Length {len(value)} is less than minimum required "
                    f"length {min_length}"
                )

    def _validate_max_length(self, field_name: str, value: Any,
                             max_length: int, result: ValidationResult):
        """Validate maximum length constraint.
        Args:
            field_name: Name of the field being validated
            value: Value to validate
            max_length: Maximum allowed length
            result: ValidationResult to add errors to
        """
        if hasattr(value, '__len__'):
            if len(value) > max_length:
                result.add_error(
                    field_name, value, 'max_length',
                    f"Length {len(value)} exceeds maximum allowed "
                    f"length {max_length}"
                )

    def _validate_min_inclusive(self, field_name: str, value: Any,
                                min_value: Union[int, float, Decimal],
                                result: ValidationResult):
        """Validate minimum inclusive constraint.
        Args:
            field_name: Name of the field being validated
            value: Value to validate
            min_value: Minimum allowed value (inclusive)
            result: ValidationResult to add errors to
        """
        if isinstance(value, (int, float, Decimal)):
            if value < min_value:
                result.add_error(
                    field_name, value, 'min_inclusive',
                    f"Value {value} is less than minimum allowed "
                    f"value {min_value}"
                )

    def _validate_max_inclusive(self, field_name: str, value: Any,
                                max_value: Union[int, float, Decimal],
                                result: ValidationResult):
        """Validate maximum inclusive constraint.
        Args:
            field_name: Name of the field being validated
            value: Value to validate
            max_value: Maximum allowed value (inclusive)
            result: ValidationResult to add errors to
        """
        if isinstance(value, (int, float, Decimal)):
            if value > max_value:
                result.add_error(
                    field_name, value, 'max_inclusive',
                    f"Value {value} exceeds maximum allowed "
                    f"value {max_value}"
                )

    def _validate_min_exclusive(self, field_name: str, value: Any,
                                min_value: Union[int, float, Decimal],
                                result: ValidationResult):
        """Validate minimum exclusive constraint.
        Args:
            field_name: Name of the field being validated
            value: Value to validate
            min_value: Minimum value (exclusive)
            result: ValidationResult to add errors to
        """
        if isinstance(value, (int, float, Decimal)):
            if value <= min_value:
                result.add_error(
                    field_name, value, 'min_exclusive',
                    f"Value {value} must be greater than {min_value}"
                )

    def _validate_max_exclusive(self, field_name: str, value: Any,
                                max_value: Union[int, float, Decimal],
                                result: ValidationResult):
        """Validate maximum exclusive constraint.
        Args:
            field_name: Name of the field being validated
            value: Value to validate
            max_value: Maximum value (exclusive)
            result: ValidationResult to add errors to
        """
        if isinstance(value, (int, float, Decimal)):
            if value >= max_value:
                result.add_error(
                    field_name, value, 'max_exclusive',
                    f"Value {value} must be less than {max_value}"
                )

    def _validate_total_digits(self, field_name: str, value: Any,
                               total_digits: int, result: ValidationResult):
        """Validate total digits constraint for Decimal values.
        Args:
            field_name: Name of the field being validated
            value: Value to validate
            total_digits: Maximum total digits allowed
            result: ValidationResult to add errors to
        """
        if isinstance(value, Decimal):
            # Convert to string and count digits (excluding decimal point and
            # sign)
            value_str = str(abs(value)).replace('.', '')
            if len(value_str) > total_digits:
                result.add_error(
                    field_name, value, 'total_digits',
                    f"Total digits {len(value_str)} exceeds maximum "
                    f"allowed {total_digits}"
                )

    def _validate_fraction_digits(self, field_name: str, value: Any,
                                  fraction_digits: int,
                                  result: ValidationResult):
        """Validate fraction digits constraint for Decimal values.
        Args:
            field_name: Name of the field being validated
            value: Value to validate
            fraction_digits: Maximum fraction digits allowed
            result: ValidationResult to add errors to
        """
        if isinstance(value, Decimal):
            # Get the number of decimal places
            exponent = value.as_tuple().exponent
            decimal_places = abs(exponent) if isinstance(exponent, int) else 0
            if decimal_places > fraction_digits:
                result.add_error(
                    field_name, value, 'fraction_digits',
                    f"Fraction digits {decimal_places} exceeds maximum "
                    f"allowed {fraction_digits}"
                )

    def _validate_required(self, field_name: str, value: Any, required: bool,
                           result: ValidationResult):
        """Validate required constraint.
        Args:
            field_name: Name of the field being validated
            value: Value to validate
            required: Whether field is required
            result: ValidationResult to add errors to
        """
        if required and value is None:
            result.add_error(
                field_name, value, 'required',
                "Field is required but value is None"
            )

    def _validate_min_occurs(self, field_name: str, value: Any,
                             min_occurs: int, result: ValidationResult):
        """Validate minimum occurrences constraint for lists.
        Args:
            field_name: Name of the field being validated
            value: Value to validate
            min_occurs: Minimum number of items required
            result: ValidationResult to add errors to
        """
        if isinstance(value, list):
            if len(value) < min_occurs:
                result.add_error(
                    field_name, value, 'min_occurs',
                    f"List has {len(value)} items but minimum required "
                    f"is {min_occurs}"
                )

    def _validate_max_occurs(self, field_name: str, value: Any,
                             max_occurs: int, result: ValidationResult):
        """Validate maximum occurrences constraint for lists.
        Args:
            field_name: Name of the field being validated
            value: Value to validate
            max_occurs: Maximum number of items allowed
            result: ValidationResult to add errors to
        """
        if isinstance(value, list):
            if len(value) > max_occurs:
                result.add_error(
                    field_name, value, 'max_occurs',
                    f"List has {len(value)} items but maximum allowed "
                    f"is {max_occurs}"
                )

    def _validate_enum(self, field_name: str, value: Any,
                       enum_type: Type[Enum], result: ValidationResult):
        """Validate enum value constraint.
        Args:
            field_name: Name of the field being validated
            value: Value to validate
            enum_type: The enum type to validate against
            result: ValidationResult to add errors to
        """
        try:
            if isinstance(value, enum_type):
                return  # Already a valid enum instance
            # Try to convert string to enum
            if isinstance(value, str):
                enum_type(value)
            else:
                result.add_error(
                    field_name, value, 'enum',
                    f"Value '{value}' is not a valid {enum_type.__name__} "
                    f"enum value"
                )
        except ValueError:
            valid_values = [e.value for e in enum_type]
            result.add_error(
                field_name, value, 'enum',
                f"Value '{value}' is not a valid {enum_type.__name__} "
                f"enum value. Valid values: {valid_values}"
            )

    def _validate_list_constraints(self, field, value: list,
                                   result: ValidationResult):
        """Validate constraints specific to list fields.
        Args:
            field: The dataclass field being validated
            value: List value to validate
            result: ValidationResult to add errors to
        """
        metadata = field.metadata
        field_name = field.name
        # Validate min_occurs and max_occurs
        if 'min_occurs' in metadata:
            self._validate_min_occurs(
                field_name, value, metadata['min_occurs'], result
            )
        if 'max_occurs' in metadata:
            self._validate_max_occurs(
                field_name, value, metadata['max_occurs'], result
            )

    def get_field_constraints(self, dataclass_type: Type) -> Dict[str, Dict[str, Any]]:  # noqa: E501
        """Extract all validation constraints for fields in a dataclass.
        Args:
            dataclass_type: The dataclass type to analyze
        Returns:
            Dictionary mapping field names to their constraints
        Raises:
            ValueError: If dataclass_type is not a dataclass
        """
        if not is_dataclass(dataclass_type):
            raise ValueError("dataclass_type must be a dataclass")
        constraints = {}
        dataclass_fields = fields(dataclass_type)
        for field in dataclass_fields:
            field_constraints = {}
            # Extract validation constraints from metadata
            for key, value in field.metadata.items():
                if (key in self.type_validators or
                        key in ['type', 'namespace', 'name']):
                    field_constraints[key] = value
            # Add type information
            field_constraints['field_type'] = field.type
            field_constraints['default'] = (
                field.default if field.default is not field.default_factory
                else None
            )
            constraints[field.name] = field_constraints
        return constraints


def validate_instance(instance: Any, strict: bool = True) -> ValidationResult:
    """Convenience function to validate a dataclass instance.
    Args:
        instance: The dataclass instance to validate
        strict: If True, stops on first error. If False, collects all errors.
    Returns:
        ValidationResult containing validation results
    """
    validator = ISO20022Validator()
    return validator.validate(instance, strict)


def validate_message(instance: Any, strict: bool = True) -> ValidationResult:
    """Convenience function to validate a complete ISO20022 message.
    Args:
        instance: The message instance to validate (typically Document or root)
        strict: If True, stops on first error. If False, collects all errors.
    Returns:
        ValidationResult containing validation results for entire message
    """
    validator = ISO20022Validator()
    return validator.validate_message(instance, strict)


def validate_field(dataclass_type: Type, field_name: str,
                   value: Any) -> ValidationResult:
    """Convenience function to validate a single field value.
    Args:
        dataclass_type: The dataclass type containing the field
        field_name: Name of the field to validate
        value: Value to validate
    Returns:
        ValidationResult containing validation results
    """
    validator = ISO20022Validator()
    return validator.validate_field_value(dataclass_type, field_name, value)


def get_constraints(dataclass_type: Type) -> Dict[str, Dict[str, Any]]:
    """Convenience function to get all constraints for a dataclass.
    Args:
        dataclass_type: The dataclass type to analyze
    Returns:
        Dictionary mapping field names to their constraints
    """
    validator = ISO20022Validator()
    return validator.get_field_constraints(dataclass_type)
