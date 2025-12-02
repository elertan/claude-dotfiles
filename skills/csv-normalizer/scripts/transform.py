#!/usr/bin/env python3
"""
Apply saved normalization transformation to new CSV data.

Usage:
    python transform.py input.csv --config transform_config.json --output-dir ./output
"""

import argparse
import json
import sys
from pathlib import Path

try:
    import pandas as pd
except ImportError:
    print("Error: pandas required. Install with: pip install pandas")
    sys.exit(1)


def load_config(config_path: str) -> dict:
    """Load transformation configuration."""
    with open(config_path) as f:
        config = json.load(f)

    required_keys = ["version", "original_columns", "tables"]
    for key in required_keys:
        if key not in config:
            raise ValueError(f"Config missing required key: {key}")

    return config


def validate_input(df: pd.DataFrame, config: dict) -> list:
    """Validate input CSV matches expected structure."""
    errors = []

    expected_cols = set(config["original_columns"])
    actual_cols = set(df.columns)

    missing = expected_cols - actual_cols
    extra = actual_cols - expected_cols

    if missing:
        errors.append(f"Missing columns: {missing}")
    if extra:
        errors.append(f"Extra columns (will be ignored): {extra}")

    return errors


def transform(csv_path: str, config_path: str, output_dir: str,
              strict: bool = False) -> dict:
    """Apply transformation to new CSV data."""
    df = pd.read_csv(csv_path)
    config = load_config(config_path)

    print(f"Transforming {csv_path}...")
    print(f"  Input rows: {len(df)}")

    # Validate structure
    errors = validate_input(df, config)
    if errors:
        for err in errors:
            print(f"  Warning: {err}")
        if strict and any("Missing" in e for e in errors):
            print("Error: Strict mode - aborting due to missing columns")
            sys.exit(1)

    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    tables_path = output_path / "tables"
    tables_path.mkdir(exist_ok=True)

    results = {"tables": []}

    # Transform each table
    for table_config in config["tables"]:
        name = table_config["name"]
        columns = table_config["columns"]
        pk = table_config["primary_key"]

        # Check all columns exist
        available_cols = [c for c in columns if c in df.columns]
        if len(available_cols) != len(columns):
            missing = set(columns) - set(available_cols)
            print(f"  Skipping {name}: missing columns {missing}")
            continue

        # Extract and deduplicate
        table_df = df[columns].drop_duplicates()

        # Sort by primary key for consistency
        table_df = table_df.sort_values(by=pk).reset_index(drop=True)

        # Write to CSV
        table_path = tables_path / f"{name}.csv"
        table_df.to_csv(table_path, index=False)

        results["tables"].append({
            "name": name,
            "rows": len(table_df),
            "path": str(table_path)
        })

        print(f"  Created {name}.csv ({len(table_df)} rows)")

    # Validate foreign keys if present
    if "foreign_keys" in config:
        print("\n  Validating foreign keys...")
        fk_errors = validate_foreign_keys(tables_path, config["foreign_keys"])
        if fk_errors:
            for err in fk_errors:
                print(f"    Warning: {err}")
        else:
            print("    All foreign keys valid")

    print(f"\nTransformation complete. Output: {output_path}")

    return results


def validate_foreign_keys(tables_path: Path, foreign_keys: list) -> list:
    """Validate foreign key constraints."""
    errors = []

    for fk in foreign_keys:
        child_path = tables_path / f"{fk['child_table']}.csv"
        parent_path = tables_path / f"{fk['parent_table']}.csv"

        if not child_path.exists() or not parent_path.exists():
            continue

        child_df = pd.read_csv(child_path)
        parent_df = pd.read_csv(parent_path)

        child_values = set(child_df[fk["column"]].dropna())
        parent_values = set(parent_df[fk["parent_column"]].dropna())

        orphans = child_values - parent_values
        if orphans:
            errors.append(
                f"{fk['child_table']}.{fk['column']} has {len(orphans)} "
                f"orphan values not in {fk['parent_table']}"
            )

    return errors


def main():
    parser = argparse.ArgumentParser(
        description="Apply saved normalization to new CSV data"
    )
    parser.add_argument("input", help="Input CSV file")
    parser.add_argument("--config", "-c", required=True,
                       help="Transform config JSON (from normalize.py)")
    parser.add_argument("--output-dir", "-o", default="./output",
                       help="Output directory")
    parser.add_argument("--strict", "-s", action="store_true",
                       help="Fail on missing columns")

    args = parser.parse_args()

    if not Path(args.input).exists():
        print(f"Error: Input file not found: {args.input}")
        sys.exit(1)

    if not Path(args.config).exists():
        print(f"Error: Config file not found: {args.config}")
        sys.exit(1)

    transform(args.input, args.config, args.output_dir, args.strict)


if __name__ == "__main__":
    main()
