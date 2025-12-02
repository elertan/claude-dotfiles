# CSV Cleaner Skill

A skill for Claude agents to clean and normalize CSV data. Provides hierarchical knowledge files and Python scripts that enable an agent to intelligently analyze, clean, and transform data.

## Overview

This skill enables a Claude agent to:
- **Analyze** CSV files (detect encoding, types, missing values, duplicates, outliers)
- **Clean** data using 10+ operations (imputation, deduplication, normalization, etc.)
- **Output** cleaned CSV, markdown reports, and inferred schemas

The knowledge base is hierarchical - the agent loads only relevant context based on detected issues, keeping token usage efficient.

## Project Structure

```
csv-cleaner-skill/
├── SKILL.md                    # Agent entry point - start here
├── scripts/
│   ├── analyze.py              # CSV profiling tool
│   └── clean.py                # Data cleaning tool
├── knowledge/                  # Hierarchical knowledge base
│   ├── index.md                # Main index with decision trees
│   ├── operations/             # Cleaning operation guides
│   │   ├── missing-values.md
│   │   ├── duplicates.md
│   │   ├── outliers.md
│   │   └── normalization.md
│   ├── types/                  # Data type handling
│   │   ├── strings.md
│   │   ├── numbers.md
│   │   ├── dates.md
│   │   ├── emails.md
│   │   └── phones.md
│   ├── validation/             # Schema validation
│   └── csv/                    # CSV parsing edge cases
├── requirements.txt
└── PROGRESS.md                 # Implementation tracker
```

## Usage

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Analyze a CSV

```bash
python scripts/analyze.py input.csv
```

Returns JSON with:
- Column types (inferred + semantic: email, phone, date, etc.)
- Missing value counts and percentages
- Duplicate detection
- Outlier detection for numeric columns
- Identified issues per column

### 3. Clean the Data

Create an operations file (`ops.json`):
```json
{
  "operations": [
    {"type": "fill_missing", "column": "age", "strategy": "median"},
    {"type": "normalize_strings", "column": "name", "ops": ["trim", "titlecase"]},
    {"type": "standardize_dates", "column": "created_at", "format": "%Y-%m-%d"},
    {"type": "remove_duplicates", "keep": "first"}
  ]
}
```

Run cleaning:
```bash
python scripts/clean.py input.csv output.csv --operations ops.json --report report.md
```

## Available Operations

| Operation | Description | Key Parameters |
|-----------|-------------|----------------|
| `fill_missing` | Impute missing values | `strategy`: mean, median, mode, constant, forward, backward |
| `drop_missing` | Drop rows with nulls | `columns`, `how`: any/all |
| `remove_duplicates` | Deduplicate rows | `columns`, `keep`: first/last/none |
| `normalize_strings` | Clean text | `ops`: trim, lowercase, uppercase, titlecase, remove_special |
| `standardize_dates` | Parse & format dates | `format`, `dayfirst` |
| `normalize_phones` | Convert to E.164 | `country` |
| `validate_emails` | Validate & lowercase | - |
| `cap_outliers` | Winsorize extremes | `method`: iqr/zscore/percentile |
| `convert_type` | Change data type | `target_type`: int, float, string, datetime, boolean |
| `drop_column` | Remove columns | `columns` |

## Agent Workflow

1. Agent reads `SKILL.md` for instructions
2. Runs `analyze.py` on input CSV
3. Reviews `issues_summary` in output
4. Reads relevant knowledge files (e.g., `knowledge/operations/missing-values.md`)
5. Builds operations JSON based on knowledge guidance
6. Runs `clean.py` with operations
7. Outputs cleaned CSV and report

## Knowledge Base

The knowledge files contain:
- Decision trees for choosing strategies
- Operation syntax and examples
- Edge cases and best practices
- Links to related topics

Example from `knowledge/operations/missing-values.md`:
```
Is >50% of column missing?
├── Yes → Drop column
└── No → Is it an ID?
    ├── Yes → Drop rows (never impute IDs)
    └── No → Is it categorical?
        ├── Yes → Mode imputation
        └── No → Check distribution → Mean or Median
```

## Requirements

- Python 3.11+
- pandas >= 2.0
- chardet (encoding detection)
- python-dateutil (date parsing)
- phonenumbers (phone validation)
- jsonschema (validation)
