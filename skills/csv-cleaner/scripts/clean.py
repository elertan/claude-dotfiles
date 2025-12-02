#!/usr/bin/env python3
"""Apply cleaning operations to CSV file."""
import pandas as pd
import json
import sys
import chardet
import re
from pathlib import Path
from datetime import datetime


def detect_encoding(path: str) -> str:
    """Detect file encoding using chardet."""
    with open(path, 'rb') as f:
        return chardet.detect(f.read(100000))['encoding'] or 'utf-8'


def apply_operation(df: pd.DataFrame, op: dict) -> tuple[pd.DataFrame, dict]:
    """Apply single operation, return modified df and change log."""
    op_type = op["type"]
    log = {"operation": op_type, "column": op.get("column"), "timestamp": datetime.now().isoformat()}

    if op_type == "fill_missing":
        col = op["column"]
        strategy = op["strategy"]
        count = int(df[col].isna().sum())

        if count == 0:
            log["filled"] = 0
            log["note"] = "No missing values to fill"
            return df, log

        if strategy == "mean":
            fill_val = df[col].mean()
            df[col] = df[col].fillna(fill_val)
            log["fill_value"] = round(float(fill_val), 4)
        elif strategy == "median":
            fill_val = df[col].median()
            df[col] = df[col].fillna(fill_val)
            log["fill_value"] = float(fill_val)
        elif strategy == "mode":
            mode_val = df[col].mode()
            if len(mode_val) > 0:
                fill_val = mode_val[0]
                df[col] = df[col].fillna(fill_val)
                log["fill_value"] = str(fill_val)
            else:
                log["error"] = "No mode found"
                return df, log
        elif strategy == "constant":
            fill_val = op.get("value", "")
            df[col] = df[col].fillna(fill_val)
            log["fill_value"] = str(fill_val)
        elif strategy == "forward":
            df[col] = df[col].ffill()
            log["method"] = "forward_fill"
        elif strategy == "backward":
            df[col] = df[col].bfill()
            log["method"] = "backward_fill"
        else:
            log["error"] = f"Unknown strategy: {strategy}"
            return df, log

        log["filled"] = count

    elif op_type == "drop_missing":
        cols = op.get("columns")
        how = op.get("how", "any")
        before = len(df)
        df = df.dropna(subset=cols, how=how)
        dropped = before - len(df)
        log["dropped"] = dropped
        log["remaining"] = len(df)

    elif op_type == "remove_duplicates":
        cols = op.get("columns")
        keep = op.get("keep", "first")
        before = len(df)

        if keep == "none":
            df = df.drop_duplicates(subset=cols, keep=False)
        else:
            df = df.drop_duplicates(subset=cols, keep=keep)

        removed = before - len(df)
        log["removed"] = removed
        log["remaining"] = len(df)

    elif op_type == "normalize_strings":
        col = op["column"]
        ops = op.get("ops", ["trim"])
        series = df[col].astype(str)
        applied = []

        for string_op in ops:
            if string_op == "trim":
                series = series.str.strip()
                applied.append("trim")
            elif string_op == "lowercase":
                series = series.str.lower()
                applied.append("lowercase")
            elif string_op == "uppercase":
                series = series.str.upper()
                applied.append("uppercase")
            elif string_op == "titlecase":
                series = series.str.title()
                applied.append("titlecase")
            elif string_op == "remove_special":
                series = series.str.replace(r'[^\w\s]', '', regex=True)
                applied.append("remove_special")
            elif string_op == "remove_digits":
                series = series.str.replace(r'\d', '', regex=True)
                applied.append("remove_digits")
            elif string_op == "collapse_whitespace":
                series = series.str.replace(r'\s+', ' ', regex=True)
                applied.append("collapse_whitespace")

        # Handle 'nan' strings that resulted from NaN values
        series = series.replace('nan', '')

        df[col] = series
        log["applied"] = applied
        log["rows_affected"] = len(df)

    elif op_type == "standardize_dates":
        from dateutil import parser as date_parser

        col = op["column"]
        fmt = op.get("format", "%Y-%m-%d")
        dayfirst = op.get("dayfirst", False)
        yearfirst = op.get("yearfirst", False)

        def parse_date(x):
            if pd.isna(x) or str(x).strip() == '':
                return None
            try:
                parsed = date_parser.parse(str(x), dayfirst=dayfirst, yearfirst=yearfirst)
                return parsed.strftime(fmt)
            except:
                return None

        before_nulls = df[col].isna().sum()
        df[col] = df[col].apply(parse_date)
        after_nulls = df[col].isna().sum()

        log["converted"] = int(len(df) - after_nulls)
        log["failed"] = int(after_nulls - before_nulls)
        log["format"] = fmt

    elif op_type == "normalize_phones":
        try:
            import phonenumbers
        except ImportError:
            log["error"] = "phonenumbers library not installed"
            return df, log

        col = op["column"]
        country = op.get("country", "US")

        def normalize_phone(x):
            if pd.isna(x) or str(x).strip() == '':
                return None
            try:
                parsed = phonenumbers.parse(str(x), country)
                if phonenumbers.is_valid_number(parsed):
                    return phonenumbers.format_number(
                        parsed, phonenumbers.PhoneNumberFormat.E164
                    )
            except:
                pass
            return None

        before = df[col].notna().sum()
        df[col] = df[col].apply(normalize_phone)
        after = df[col].notna().sum()

        log["valid"] = int(after)
        log["invalid"] = int(before - after)
        log["country"] = country

    elif op_type == "validate_emails":
        col = op["column"]
        # RFC 5322 simplified pattern
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

        def validate_email(x):
            if pd.isna(x) or str(x).strip() == '':
                return None
            email = str(x).strip().lower()
            if re.match(email_pattern, email):
                return email
            return None

        before = df[col].notna().sum()
        df[col] = df[col].apply(validate_email)
        after = df[col].notna().sum()

        log["valid"] = int(after)
        log["invalid"] = int(before - after)

    elif op_type == "cap_outliers":
        col = op["column"]
        method = op.get("method", "iqr")
        multiplier = op.get("multiplier", 1.5)
        series = df[col]

        if not pd.api.types.is_numeric_dtype(series):
            log["error"] = f"Column {col} is not numeric"
            return df, log

        clean = series.dropna()

        if method == "iqr":
            q1, q3 = clean.quantile([0.25, 0.75])
            iqr = q3 - q1
            lower = q1 - multiplier * iqr
            upper = q3 + multiplier * iqr
        elif method == "zscore":
            mean = clean.mean()
            std = clean.std()
            lower = mean - multiplier * std
            upper = mean + multiplier * std
        elif method == "percentile":
            lower_pct = op.get("lower_percentile", 1)
            upper_pct = op.get("upper_percentile", 99)
            lower = clean.quantile(lower_pct / 100)
            upper = clean.quantile(upper_pct / 100)
        else:
            log["error"] = f"Unknown method: {method}"
            return df, log

        capped_low = int((series < lower).sum())
        capped_high = int((series > upper).sum())
        df[col] = series.clip(lower, upper)

        log["capped_low"] = capped_low
        log["capped_high"] = capped_high
        log["bounds"] = {"lower": round(float(lower), 4), "upper": round(float(upper), 4)}
        log["method"] = method

    elif op_type == "convert_type":
        col = op["column"]
        target_type = op["target_type"]

        try:
            if target_type == "int":
                df[col] = pd.to_numeric(df[col], errors='coerce').astype('Int64')
            elif target_type == "float":
                df[col] = pd.to_numeric(df[col], errors='coerce')
            elif target_type == "string":
                df[col] = df[col].astype(str).replace('nan', '')
            elif target_type == "datetime":
                df[col] = pd.to_datetime(df[col], errors='coerce')
            elif target_type == "category":
                df[col] = df[col].astype('category')
            elif target_type == "boolean":
                # Map common boolean representations
                bool_map = {
                    'true': True, 'false': False,
                    'yes': True, 'no': False,
                    '1': True, '0': False,
                    't': True, 'f': False,
                    'y': True, 'n': False,
                }
                df[col] = df[col].astype(str).str.lower().map(bool_map)

            log["converted_to"] = target_type
            log["success"] = True
        except Exception as e:
            log["error"] = str(e)
            log["success"] = False

    elif op_type == "rename_column":
        old_name = op["old_name"]
        new_name = op["new_name"]
        if old_name in df.columns:
            df = df.rename(columns={old_name: new_name})
            log["renamed"] = {old_name: new_name}
        else:
            log["error"] = f"Column {old_name} not found"

    elif op_type == "drop_column":
        cols = op["columns"] if isinstance(op.get("columns"), list) else [op["column"]]
        existing = [c for c in cols if c in df.columns]
        df = df.drop(columns=existing)
        log["dropped_columns"] = existing

    else:
        log["error"] = f"Unknown operation type: {op_type}"

    return df, log


def generate_report(logs: list, input_path: str, output_path: str) -> str:
    """Generate markdown report of cleaning operations."""
    report = f"""# Data Cleaning Report

## Summary
- **Input**: {input_path}
- **Output**: {output_path}
- **Operations Applied**: {len(logs)}
- **Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Operations Log

"""
    for i, log in enumerate(logs, 1):
        report += f"### {i}. {log['operation']}\n"
        if log.get('column'):
            report += f"- **Column**: `{log['column']}`\n"

        # Add operation-specific details
        for key, value in log.items():
            if key not in ['operation', 'column', 'timestamp']:
                report += f"- **{key}**: {value}\n"

        report += "\n"

    return report


def clean(input_path: str, output_path: str, operations: list) -> tuple[list, pd.DataFrame]:
    """Apply cleaning operations and return logs and cleaned dataframe."""
    encoding = detect_encoding(input_path)
    df = pd.read_csv(input_path, encoding=encoding)

    logs = []
    for op in operations:
        df, log = apply_operation(df.copy(), op)
        logs.append(log)

        # Check for errors and continue
        if "error" in log:
            print(f"Warning: {log['error']}", file=sys.stderr)

    df.to_csv(output_path, index=False, encoding='utf-8')
    return logs, df


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python clean.py <input.csv> <output.csv> --operations ops.json [--report report.md]")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2]

    # Parse arguments
    ops_path = None
    report_path = None

    if "--operations" in sys.argv:
        idx = sys.argv.index("--operations")
        if idx + 1 < len(sys.argv):
            ops_path = sys.argv[idx + 1]

    if "--report" in sys.argv:
        idx = sys.argv.index("--report")
        if idx + 1 < len(sys.argv):
            report_path = sys.argv[idx + 1]

    if not ops_path:
        print("Error: --operations argument required", file=sys.stderr)
        sys.exit(1)

    try:
        with open(ops_path) as f:
            ops_data = json.load(f)

        logs, df = clean(input_path, output_path, ops_data["operations"])

        # Output logs
        print(json.dumps({"logs": logs, "output_rows": len(df)}, indent=2, ensure_ascii=False))

        # Generate report if requested
        if report_path:
            report = generate_report(logs, input_path, output_path)
            Path(report_path).write_text(report)
            print(f"Report written to {report_path}", file=sys.stderr)

    except Exception as e:
        print(json.dumps({"error": str(e)}, ensure_ascii=False), file=sys.stderr)
        sys.exit(1)
