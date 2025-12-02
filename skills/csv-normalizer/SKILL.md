---
name: csv-normalizer
description: >
  Database normalization for CSV files. Analyzes data structure, detects
  functional dependencies, and decomposes into normalized tables (1NF-BCNF).
  Outputs multiple CSV files, SQL DDL, and Mermaid ERD. Use when: (1) converting
  flat CSV data into relational database schema, (2) reducing data redundancy,
  (3) preparing denormalized exports for database import, (4) user mentions
  "normalize", "1NF/2NF/3NF/BCNF", "functional dependencies", or "database design".
---

# CSV Database Normalizer

Transform denormalized CSV data into properly normalized relational database structures.

## Quick Start

```bash
# 1. Analyze CSV to detect functional dependencies
python scripts/analyze.py data.csv --output analysis.json

# 2. Review analysis, confirm FDs with user, save to config.json

# 3. Normalize to target form
python scripts/normalize.py data.csv --config config.json --target 3NF --output-dir ./normalized

# 4. For future data with same structure
python scripts/transform.py new_data.csv --config normalized/transform_config.json --output-dir ./output
```

## Workflow

### Step 1: Analysis

Run analyze.py on input CSV:

```bash
python scripts/analyze.py input.csv --output analysis.json
```

Output includes:
- Column types and statistics
- Detected functional dependencies with confidence scores
- Candidate keys
- Current normal form assessment
- Questions for user review

### Step 2: User Confirmation

Review the analysis output. Key items to confirm:

1. **Functional dependencies** - especially those with < 100% confidence
2. **Primary key selection** - choose from candidate keys
3. **Semantic dependencies** - business rules the algorithm can't detect

Create `config.json` from analysis, marking FDs as confirmed:

```json
{
  "functional_dependencies": [
    {"determinant": ["employee_id"], "dependent": "name", "status": "confirmed"},
    {"determinant": ["dept_id"], "dependent": "dept_name", "status": "confirmed"}
  ],
  "candidate_keys": [{"columns": ["employee_id"]}]
}
```

### Step 3: Normalization

Run normalize.py with confirmed config:

```bash
python scripts/normalize.py input.csv --config config.json --target 3NF --output-dir ./normalized
```

Outputs:
- `tables/*.csv` - Decomposed normalized tables
- `schema.sql` - CREATE TABLE statements with constraints
- `erd.md` - Mermaid entity-relationship diagram
- `transform_config.json` - Reusable transformation config
- `README.md` - Usage instructions

### Step 4: Re-transformation

For new data with identical structure:

```bash
python scripts/transform.py new_export.csv --config transform_config.json --output-dir ./output
```

## When to Use This Skill

Use csv-normalizer when:
- Converting flat/denormalized CSV exports to relational schema
- Designing database from spreadsheet data
- Identifying redundancy and dependencies in data
- Preparing data for SQL database import

Do NOT use for:
- Data cleaning (use csv-cleaner instead)
- Format normalization (dates, phones, etc.)
- Data validation

## Scripts Reference

### analyze.py

```bash
python scripts/analyze.py INPUT [--output FILE] [--sample N]
```

| Arg | Description |
|-----|-------------|
| `INPUT` | CSV file to analyze |
| `--output` | Save analysis to JSON file |
| `--sample` | Sample N rows for large files |

### normalize.py

```bash
python scripts/normalize.py INPUT --config FILE --target NF [--output-dir DIR]
```

| Arg | Description |
|-----|-------------|
| `INPUT` | CSV file to normalize |
| `--config` | JSON config with confirmed FDs |
| `--target` | Target normal form: `3NF` or `BCNF` |
| `--output-dir` | Output directory (default: ./normalized) |

### transform.py

```bash
python scripts/transform.py INPUT --config FILE [--output-dir DIR] [--strict]
```

| Arg | Description |
|-----|-------------|
| `INPUT` | New CSV file with same structure |
| `--config` | transform_config.json from normalize.py |
| `--output-dir` | Output directory (default: ./output) |
| `--strict` | Fail on missing columns |

## Theory Reference

For database normalization theory:
- `references/normal-forms.md` - 1NF through BCNF definitions and examples
- `references/fd-detection.md` - How FD detection works
- `references/decomposition.md` - Decomposition algorithms

## Example Session

```
User: "I have a sales export CSV that I want to import into PostgreSQL"

1. Run: python scripts/analyze.py sales.csv --output analysis.json

2. Review analysis.json:
   - Detected FDs: order_id → customer_id, customer_id → customer_name
   - Questions: "Does product_id determine product_category?"

3. Confirm with user, create config.json

4. Run: python scripts/normalize.py sales.csv --config config.json --target 3NF

5. Output:
   - tables/orders.csv
   - tables/customers.csv
   - tables/products.csv
   - schema.sql (ready to run in PostgreSQL)
   - erd.md (visualize in VS Code/GitHub)
```

## Dependencies

```bash
pip install pandas
```
