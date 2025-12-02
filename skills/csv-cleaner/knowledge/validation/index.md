# Validation Rules

Define and apply constraints to ensure data quality.

## JSON Schema Style Validation

Data can be validated against JSON Schema-like rules.

## Constraint Types

| Constraint | Purpose | Example |
|------------|---------|---------|
| Type | Data type check | `"type": "string"` |
| Format | Semantic format | `"format": "email"` |
| Range | Numeric bounds | `"minimum": 0, "maximum": 100` |
| Length | String length | `"minLength": 1, "maxLength": 255` |
| Pattern | Regex match | `"pattern": "^[A-Z]{3}$"` |
| Enum | Allowed values | `"enum": ["A", "B", "C"]` |
| Required | Must be present | Non-null check |

## Example Schema

```json
{
  "columns": {
    "email": {
      "type": "string",
      "format": "email",
      "required": true
    },
    "age": {
      "type": "integer",
      "minimum": 0,
      "maximum": 150
    },
    "status": {
      "type": "string",
      "enum": ["active", "inactive", "pending"]
    },
    "code": {
      "type": "string",
      "pattern": "^[A-Z]{3}-[0-9]{4}$"
    }
  }
}
```

## Validation Workflow

1. **Define schema** based on expected data
2. **Run analyze.py** to profile actual data
3. **Compare** actual vs expected
4. **Clean** to bring data into compliance
5. **Validate** final output

## Common Rules

### Required Fields
```json
{
  "email": {"required": true},
  "phone": {"required": false}
}
```
Use `drop_missing` to enforce required fields.

### Numeric Ranges
```json
{
  "age": {"minimum": 0, "maximum": 150},
  "percentage": {"minimum": 0, "maximum": 100}
}
```
Use `cap_outliers` or custom filtering.

### String Patterns
```json
{
  "zip_code": {"pattern": "^[0-9]{5}(-[0-9]{4})?$"},
  "country_code": {"pattern": "^[A-Z]{2}$"}
}
```

### Allowed Values (Enum)
```json
{
  "status": {"enum": ["active", "inactive", "pending"]},
  "priority": {"enum": ["low", "medium", "high"]}
}
```

## Applying Constraints

For each constraint type, corresponding cleaning operation:

| Constraint | Cleaning Approach |
|------------|-------------------|
| required | `drop_missing` |
| type | `convert_type` |
| format: email | `validate_emails` |
| format: phone | `normalize_phones` |
| format: date | `standardize_dates` |
| minimum/maximum | `cap_outliers` |
| enum | Filter or normalize |
| pattern | Custom validation |

## Building Cleaning Plan from Schema

1. **Required fields**: Add `drop_missing` for required columns
2. **Type mismatches**: Add `convert_type` operations
3. **Format fields**: Add appropriate normalization
4. **Range violations**: Add `cap_outliers` or filters
5. **Enum violations**: Normalize values or filter

## Example: Schema-Driven Cleaning

Given schema requiring:
- `email`: required, email format
- `age`: integer, 0-150
- `status`: enum [active, inactive]

```json
{
  "operations": [
    {"type": "validate_emails", "column": "email"},
    {"type": "drop_missing", "columns": ["email"], "how": "any"},
    {"type": "convert_type", "column": "age", "target_type": "int"},
    {"type": "cap_outliers", "column": "age", "method": "percentile", "lower_percentile": 0, "upper_percentile": 100},
    {"type": "normalize_strings", "column": "status", "ops": ["trim", "lowercase"]}
  ]
}
```
