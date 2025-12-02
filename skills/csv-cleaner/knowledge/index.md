# Data Cleaning Knowledge Base

Read subtopics as needed based on issues detected in the data.

## Quick Start

1. Run `python scripts/analyze.py input.csv` to profile data
2. Review `issues_summary` in output
3. Read relevant knowledge files below
4. Build operations JSON and run `python scripts/clean.py`

## Topics

### Operations
- [Missing Values](operations/missing-values.md) - Handling null/empty values
- [Duplicates](operations/duplicates.md) - Finding and removing duplicates
- [Outliers](operations/outliers.md) - Detecting and handling extreme values
- [Normalization](operations/normalization.md) - General data normalization

### Data Types
- [Strings](types/strings.md) - Text cleaning and normalization
- [Numbers](types/numbers.md) - Numeric validation and formatting
- [Dates](types/dates.md) - Date parsing and standardization
- [Emails](types/emails.md) - Email validation
- [Phones](types/phones.md) - Phone number normalization

### Other
- [Validation Rules](validation/index.md) - JSON Schema constraints
- [CSV Edge Cases](csv/edge-cases.md) - Encoding, quoting, delimiter issues

## Issue → Knowledge Mapping

| Detected Issue | Read This |
|----------------|-----------|
| `has_missing_values` | [Missing Values](operations/missing-values.md) |
| `high_missing_rate` | [Missing Values](operations/missing-values.md) |
| `exact_duplicate_rows > 0` | [Duplicates](operations/duplicates.md) |
| `has_outliers` | [Outliers](operations/outliers.md) |
| `whitespace_issues` | [Strings](types/strings.md) |
| `mixed_case` | [Strings](types/strings.md) |
| `semantic_type: email` | [Emails](types/emails.md) |
| `semantic_type: phone` | [Phones](types/phones.md) |
| `semantic_type: date` | [Dates](types/dates.md) |

## Data Quality Dimensions

When cleaning data, consider these quality dimensions:

| Dimension | Question | Operations |
|-----------|----------|------------|
| **Accuracy** | Is data correct? | Validation, outlier removal |
| **Completeness** | Is data present? | Missing value handling |
| **Consistency** | Is format uniform? | Normalization, standardization |
| **Validity** | Does data follow rules? | Type conversion, validation |
| **Uniqueness** | Are there duplicates? | Deduplication |

## Workflow Decision Tree

```
Start
├── Run analyze.py
├── Check issues_summary
│   ├── Missing values? → Read operations/missing-values.md
│   ├── Duplicates? → Read operations/duplicates.md
│   ├── Outliers? → Read operations/outliers.md
│   └── Type issues? → Read relevant types/*.md
├── Build operations.json based on knowledge
├── Run clean.py
└── Verify output
```
