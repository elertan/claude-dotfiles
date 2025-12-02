#!/usr/bin/env python3
"""
Normalize CSV data based on functional dependencies.

Usage:
    python normalize.py input.csv --config config.json --target 3NF --output-dir ./normalized
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Optional
from collections import defaultdict

try:
    import pandas as pd
except ImportError:
    print("Error: pandas required. Install with: pip install pandas")
    sys.exit(1)


def load_config(config_path: str) -> dict:
    """Load normalization configuration."""
    with open(config_path) as f:
        return json.load(f)


def compute_minimal_cover(fds: list) -> list:
    """Compute minimal cover of functional dependencies."""
    # Step 1: Split right-hand sides (already done in our format)
    minimal = []

    for fd in fds:
        det = tuple(sorted(fd["determinant"]))
        dep = fd["dependent"]
        minimal.append({"determinant": list(det), "dependent": dep})

    # Step 2: Remove redundant FDs
    result = []
    for i, fd in enumerate(minimal):
        other_fds = minimal[:i] + minimal[i+1:]
        # Check if fd is derivable from other_fds
        if not is_derivable(fd, other_fds):
            result.append(fd)

    # Step 3: Remove redundant attributes from determinants
    final = []
    for fd in result:
        det = fd["determinant"]
        if len(det) > 1:
            for attr in det:
                reduced_det = [a for a in det if a != attr]
                test_fd = {"determinant": reduced_det, "dependent": fd["dependent"]}
                if is_derivable(test_fd, result):
                    det = reduced_det
                    break
        final.append({"determinant": det, "dependent": fd["dependent"]})

    return final


def is_derivable(fd: dict, fd_set: list) -> bool:
    """Check if fd is derivable from fd_set using closure."""
    closure = set(fd["determinant"])

    changed = True
    while changed:
        changed = False
        for other in fd_set:
            if set(other["determinant"]).issubset(closure):
                if other["dependent"] not in closure:
                    closure.add(other["dependent"])
                    changed = True

    return fd["dependent"] in closure


def compute_closure(attrs: set, fds: list) -> set:
    """Compute attribute closure under FDs."""
    closure = set(attrs)

    changed = True
    while changed:
        changed = False
        for fd in fds:
            if set(fd["determinant"]).issubset(closure):
                if fd["dependent"] not in closure:
                    closure.add(fd["dependent"])
                    changed = True

    return closure


def decompose_3nf(columns: list, fds: list, candidate_keys: list) -> list:
    """Decompose relation into 3NF using synthesis algorithm."""
    minimal_cover = compute_minimal_cover(fds)

    # Group FDs by determinant
    fd_groups = defaultdict(list)
    for fd in minimal_cover:
        det = tuple(sorted(fd["determinant"]))
        fd_groups[det].append(fd["dependent"])

    tables = []
    covered_attrs = set()

    # Create table for each FD group
    for det, deps in fd_groups.items():
        cols = list(det) + deps
        tables.append({
            "name": generate_table_name(det, deps),
            "columns": cols,
            "primary_key": list(det),
            "source_fd": {"determinant": list(det), "dependents": deps}
        })
        covered_attrs.update(cols)

    # Add candidate key relation if not covered
    all_cols = set(columns)
    if candidate_keys:
        key_cols = set(candidate_keys[0]["columns"])
        if not key_cols.issubset(covered_attrs):
            tables.append({
                "name": "main_keys",
                "columns": list(key_cols),
                "primary_key": list(key_cols),
                "source_fd": None
            })

    # Check for uncovered columns
    uncovered = all_cols - covered_attrs
    if uncovered and candidate_keys:
        # Add to a main table with the key
        main_table = next((t for t in tables if t["source_fd"] is None), None)
        if main_table:
            main_table["columns"].extend(uncovered)
        else:
            key_cols = candidate_keys[0]["columns"]
            tables.append({
                "name": "main",
                "columns": key_cols + list(uncovered),
                "primary_key": key_cols,
                "source_fd": None
            })

    return tables


def decompose_bcnf(columns: list, fds: list, candidate_keys: list) -> list:
    """Decompose relation into BCNF."""

    def is_superkey(det: set, all_cols: set, fds: list) -> bool:
        closure = compute_closure(det, fds)
        return all_cols.issubset(closure)

    def bcnf_decompose(cols: list, fds: list) -> list:
        col_set = set(cols)
        relevant_fds = [fd for fd in fds
                       if set(fd["determinant"]).issubset(col_set)
                       and fd["dependent"] in col_set]

        # Find violating FD
        for fd in relevant_fds:
            det = set(fd["determinant"])
            if not is_superkey(det, col_set, relevant_fds):
                # Decompose
                r1_cols = list(det | {fd["dependent"]})
                r2_cols = list(col_set - {fd["dependent"]} | det)

                # Recursively decompose
                r1_tables = bcnf_decompose(r1_cols, relevant_fds)
                r2_tables = bcnf_decompose(r2_cols, relevant_fds)

                return r1_tables + r2_tables

        # No violation, return single table
        return [{
            "columns": cols,
            "primary_key": find_key(cols, fds, candidate_keys)
        }]

    tables = bcnf_decompose(columns, fds)

    # Add names to tables
    for i, table in enumerate(tables):
        table["name"] = generate_table_name(
            table["primary_key"],
            [c for c in table["columns"] if c not in table["primary_key"]]
        ) if len(tables) > 1 else "main"

    return tables


def find_key(columns: list, fds: list, candidate_keys: list) -> list:
    """Find primary key for a set of columns."""
    col_set = set(columns)

    # Check if any candidate key fits
    for ck in candidate_keys:
        if set(ck["columns"]).issubset(col_set):
            return ck["columns"]

    # Find minimal set that determines all columns
    relevant_fds = [fd for fd in fds
                   if set(fd["determinant"]).issubset(col_set)
                   and fd["dependent"] in col_set]

    for fd in relevant_fds:
        det = set(fd["determinant"])
        closure = compute_closure(det, relevant_fds)
        if col_set.issubset(closure):
            return list(det)

    return columns  # Fallback: all columns are key


def generate_table_name(key_cols: list, dep_cols: list) -> str:
    """Generate descriptive table name."""
    if len(dep_cols) == 1:
        return dep_cols[0] + "s"
    elif len(key_cols) == 1:
        return key_cols[0].replace("_id", "") + "s"
    else:
        return "_".join(key_cols[:2])


def infer_sql_type(series: pd.Series) -> str:
    """Infer SQL data type from pandas series."""
    dtype = str(series.dtype)

    if dtype == "int64":
        if series.max() < 2147483647:
            return "INTEGER"
        return "BIGINT"
    elif dtype == "float64":
        return "DECIMAL(18,6)"
    elif dtype == "bool":
        return "BOOLEAN"
    elif dtype == "datetime64[ns]":
        return "TIMESTAMP"
    else:
        max_len = series.dropna().astype(str).str.len().max()
        if pd.isna(max_len):
            max_len = 255
        return f"VARCHAR({int(max_len) + 50})"


def generate_sql_ddl(tables: list, df: pd.DataFrame, foreign_keys: list) -> str:
    """Generate SQL DDL statements."""
    ddl = []

    for table in tables:
        cols_sql = []
        for col in table["columns"]:
            sql_type = infer_sql_type(df[col])
            nullable = "" if col in table["primary_key"] else " NULL"
            cols_sql.append(f"    {col} {sql_type}{nullable}")

        pk_sql = f"    PRIMARY KEY ({', '.join(table['primary_key'])})"
        cols_sql.append(pk_sql)

        # Add foreign keys for this table
        for fk in foreign_keys:
            if fk["child_table"] == table["name"]:
                fk_sql = (
                    f"    FOREIGN KEY ({fk['column']}) "
                    f"REFERENCES {fk['parent_table']}({fk['parent_column']})"
                )
                cols_sql.append(fk_sql)

        ddl.append(
            f"CREATE TABLE {table['name']} (\n"
            + ",\n".join(cols_sql)
            + "\n);"
        )

    return "\n\n".join(ddl)


def generate_mermaid_erd(tables: list, foreign_keys: list) -> str:
    """Generate Mermaid ERD diagram."""
    lines = ["erDiagram"]

    # Add relationships
    for fk in foreign_keys:
        parent = fk["parent_table"]
        child = fk["child_table"]
        lines.append(f"    {parent} ||--o{{ {child} : has")

    # Add table definitions
    for table in tables:
        lines.append(f"    {table['name']} {{")
        for col in table["columns"]:
            pk_mark = "PK" if col in table["primary_key"] else ""
            fk_mark = "FK" if any(
                fk["child_table"] == table["name"] and fk["column"] == col
                for fk in foreign_keys
            ) else ""
            marks = ",".join(filter(None, [pk_mark, fk_mark]))
            marks_str = f" {marks}" if marks else ""
            lines.append(f"        string {col}{marks_str}")
        lines.append("    }")

    return "\n".join(lines)


def generate_transform_config(tables: list, foreign_keys: list, original_columns: list) -> dict:
    """Generate reusable transformation configuration."""
    return {
        "version": "1.0",
        "original_columns": original_columns,
        "tables": [
            {
                "name": t["name"],
                "columns": t["columns"],
                "primary_key": t["primary_key"]
            }
            for t in tables
        ],
        "foreign_keys": foreign_keys
    }


def compute_foreign_keys(tables: list) -> list:
    """Compute foreign key relationships between tables."""
    foreign_keys = []

    for table in tables:
        pk_set = set(table["primary_key"])
        non_pk_cols = [c for c in table["columns"] if c not in pk_set]

        for other_table in tables:
            if other_table["name"] == table["name"]:
                continue

            other_pk = set(other_table["primary_key"])

            # Check if other table's PK is in this table's non-PK columns
            for col in non_pk_cols:
                if col in other_pk and len(other_pk) == 1:
                    foreign_keys.append({
                        "child_table": table["name"],
                        "column": col,
                        "parent_table": other_table["name"],
                        "parent_column": col
                    })

    return foreign_keys


def normalize(csv_path: str, config_path: str, target_nf: str,
              output_dir: str) -> dict:
    """Main normalization function."""
    df = pd.read_csv(csv_path)
    config = load_config(config_path)

    print(f"Normalizing {csv_path} to {target_nf}...")

    columns = list(df.columns)
    fds = config.get("functional_dependencies", [])
    candidate_keys = config.get("candidate_keys", [])

    # Filter to confirmed FDs only
    confirmed_fds = [fd for fd in fds
                     if fd.get("status") == "confirmed" or fd.get("confidence", 0) == 1.0]

    # Decompose based on target NF
    if target_nf.upper() in ("3NF", "3"):
        tables = decompose_3nf(columns, confirmed_fds, candidate_keys)
    elif target_nf.upper() in ("BCNF", "BC"):
        tables = decompose_bcnf(columns, confirmed_fds, candidate_keys)
    else:
        print(f"Error: Unsupported target: {target_nf}. Use 3NF or BCNF.")
        sys.exit(1)

    print(f"  Decomposed into {len(tables)} tables")

    # Compute foreign keys
    foreign_keys = compute_foreign_keys(tables)
    print(f"  Identified {len(foreign_keys)} foreign key relationships")

    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    tables_path = output_path / "tables"
    tables_path.mkdir(exist_ok=True)

    # Write decomposed CSV files
    for table in tables:
        table_df = df[table["columns"]].drop_duplicates()
        table_path = tables_path / f"{table['name']}.csv"
        table_df.to_csv(table_path, index=False)
        print(f"  Created {table_path} ({len(table_df)} rows)")

    # Generate SQL DDL
    sql_ddl = generate_sql_ddl(tables, df, foreign_keys)
    sql_path = output_path / "schema.sql"
    sql_path.write_text(sql_ddl)
    print(f"  Created {sql_path}")

    # Generate Mermaid ERD
    erd = generate_mermaid_erd(tables, foreign_keys)
    erd_path = output_path / "erd.md"
    erd_path.write_text(f"# Entity Relationship Diagram\n\n```mermaid\n{erd}\n```\n")
    print(f"  Created {erd_path}")

    # Generate transform config
    transform_config = generate_transform_config(tables, foreign_keys, columns)
    config_out_path = output_path / "transform_config.json"
    with open(config_out_path, "w") as f:
        json.dump(transform_config, f, indent=2)
    print(f"  Created {config_out_path}")

    # Generate README
    readme = generate_readme(tables, foreign_keys, target_nf, csv_path)
    readme_path = output_path / "README.md"
    readme_path.write_text(readme)
    print(f"  Created {readme_path}")

    return {
        "tables": tables,
        "foreign_keys": foreign_keys,
        "output_dir": str(output_path)
    }


def generate_readme(tables: list, foreign_keys: list, target_nf: str,
                   source_file: str) -> str:
    """Generate README with instructions."""
    table_list = "\n".join(f"- `{t['name']}.csv`: {', '.join(t['columns'])}"
                           for t in tables)

    fk_list = "\n".join(
        f"- `{fk['child_table']}.{fk['column']}` → `{fk['parent_table']}.{fk['parent_column']}`"
        for fk in foreign_keys
    ) if foreign_keys else "None"

    return f"""# Normalized Database Schema

## Source
- Original file: `{source_file}`
- Target normal form: {target_nf}

## Tables

{table_list}

## Relationships

{fk_list}

## Files

- `tables/` - Normalized CSV files
- `schema.sql` - SQL DDL statements
- `erd.md` - Entity-relationship diagram (Mermaid)
- `transform_config.json` - Reusable transformation config

## Re-running Transformation

To apply this normalization to new data with the same structure:

```bash
python transform.py new_data.csv --config transform_config.json --output-dir ./output
```

## Importing to Database

```bash
# PostgreSQL example
psql -d yourdb -f schema.sql

# Then load CSVs
for f in tables/*.csv; do
    table=$(basename "$f" .csv)
    psql -d yourdb -c "\\copy $table FROM '$f' CSV HEADER"
done
```
"""


def main():
    parser = argparse.ArgumentParser(description="Normalize CSV to relational schema")
    parser.add_argument("input", help="Input CSV file")
    parser.add_argument("--config", "-c", required=True, help="Configuration JSON file")
    parser.add_argument("--target", "-t", default="3NF",
                       help="Target normal form (3NF or BCNF)")
    parser.add_argument("--output-dir", "-o", default="./normalized",
                       help="Output directory")

    args = parser.parse_args()

    if not Path(args.input).exists():
        print(f"Error: Input file not found: {args.input}")
        sys.exit(1)

    if not Path(args.config).exists():
        print(f"Error: Config file not found: {args.config}")
        sys.exit(1)

    normalize(args.input, args.config, args.target, args.output_dir)


if __name__ == "__main__":
    main()
