#!/usr/bin/env python3
"""Analyze CSV file and output data profile as JSON."""
import pandas as pd
import chardet
import json
import sys
import re
from pathlib import Path


def detect_encoding(path: str) -> str:
    """Detect file encoding using chardet."""
    with open(path, 'rb') as f:
        result = chardet.detect(f.read(100000))
    return result['encoding'] or 'utf-8'


def detect_semantic_type(series: pd.Series) -> str:
    """Detect semantic type from sample values."""
    sample = series.dropna().astype(str).head(100)
    if len(sample) == 0:
        return "unknown"

    # Email pattern
    email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    if sample.str.match(email_pattern).mean() > 0.8:
        return "email"

    # Phone pattern (loose - digits, spaces, dashes, plus, parens)
    phone_pattern = r'^[\d\s\-\+\(\)]{7,}$'
    if sample.str.match(phone_pattern).mean() > 0.8:
        return "phone"

    # URL pattern
    url_pattern = r'^https?://'
    if sample.str.match(url_pattern).mean() > 0.8:
        return "url"

    # UUID pattern
    uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
    if sample.str.lower().str.match(uuid_pattern).mean() > 0.8:
        return "uuid"

    # Date detection via dateutil
    try:
        from dateutil import parser
        parsed = 0
        for val in sample.head(20):
            try:
                parser.parse(str(val))
                parsed += 1
            except:
                pass
        if parsed / min(len(sample), 20) > 0.8:
            return "date"
    except ImportError:
        pass

    # Boolean-like
    bool_values = {'true', 'false', 'yes', 'no', '1', '0', 't', 'f', 'y', 'n'}
    if sample.str.lower().isin(bool_values).mean() > 0.9:
        return "boolean"

    # Numeric check
    if series.dtype in ['int64', 'float64', 'int32', 'float32']:
        return "numeric"

    return "text"


def detect_distribution_type(series: pd.Series) -> str:
    """Detect if numeric distribution is symmetric or skewed."""
    if not pd.api.types.is_numeric_dtype(series):
        return "n/a"

    clean = series.dropna()
    if len(clean) < 10:
        return "insufficient_data"

    try:
        skewness = clean.skew()
        if abs(skewness) < 0.5:
            return "symmetric"
        elif skewness > 0:
            return "right_skewed"
        else:
            return "left_skewed"
    except:
        return "unknown"


def analyze(path: str) -> dict:
    """Analyze CSV and return comprehensive data profile."""
    encoding = detect_encoding(path)

    # Try to detect delimiter
    with open(path, 'r', encoding=encoding, errors='replace') as f:
        sample = f.read(5000)

    # Simple delimiter detection
    delimiters = [',', ';', '\t', '|']
    delimiter_counts = {d: sample.count(d) for d in delimiters}
    detected_delimiter = max(delimiter_counts, key=delimiter_counts.get)

    df = pd.read_csv(path, encoding=encoding, sep=detected_delimiter)

    analysis = {
        "file": str(path),
        "encoding": encoding,
        "delimiter": detected_delimiter if detected_delimiter != ',' else "comma",
        "rows": len(df),
        "columns": len(df.columns),
        "memory_usage_mb": round(df.memory_usage(deep=True).sum() / 1024 / 1024, 2),
        "duplicates": {
            "exact_duplicate_rows": int(df.duplicated().sum()),
            "duplicate_percentage": round(df.duplicated().mean() * 100, 2)
        },
        "column_analysis": {}
    }

    for col in df.columns:
        series = df[col]
        semantic_type = detect_semantic_type(series)

        col_info = {
            "dtype": str(series.dtype),
            "semantic_type": semantic_type,
            "null_count": int(series.isna().sum()),
            "null_percent": round(series.isna().mean() * 100, 2),
            "unique_count": int(series.nunique()),
            "unique_percent": round(series.nunique() / len(series) * 100, 2) if len(series) > 0 else 0,
            "sample_values": [str(v) for v in series.dropna().head(5).tolist()],
        }

        # Add statistics for numeric columns
        if pd.api.types.is_numeric_dtype(series):
            clean = series.dropna()
            if len(clean) > 0:
                col_info["stats"] = {
                    "min": float(clean.min()),
                    "max": float(clean.max()),
                    "mean": round(float(clean.mean()), 4),
                    "median": float(clean.median()),
                    "std": round(float(clean.std()), 4) if len(clean) > 1 else 0,
                    "q1": float(clean.quantile(0.25)),
                    "q3": float(clean.quantile(0.75)),
                }
                col_info["distribution"] = detect_distribution_type(series)

                # Detect potential outliers using IQR
                q1, q3 = clean.quantile([0.25, 0.75])
                iqr = q3 - q1
                lower_bound = q1 - 1.5 * iqr
                upper_bound = q3 + 1.5 * iqr
                outliers = ((clean < lower_bound) | (clean > upper_bound)).sum()
                col_info["potential_outliers"] = int(outliers)

        # Add value counts for low-cardinality columns
        if col_info["unique_count"] <= 20 and col_info["unique_count"] > 0:
            value_counts = series.value_counts(dropna=False).head(10).to_dict()
            col_info["value_counts"] = {str(k): int(v) for k, v in value_counts.items()}

        # Detect issues
        issues = []
        if col_info["null_percent"] > 50:
            issues.append("high_missing_rate")
        elif col_info["null_percent"] > 0:
            issues.append("has_missing_values")

        if col_info["unique_percent"] == 100 and len(series) > 10:
            issues.append("potentially_unique_identifier")

        if col_info.get("potential_outliers", 0) > 0:
            issues.append("has_outliers")

        if semantic_type == "text":
            # Check for whitespace issues
            str_series = series.dropna().astype(str)
            if len(str_series) > 0:
                has_leading_space = str_series.str.startswith(' ').any()
                has_trailing_space = str_series.str.endswith(' ').any()
                if has_leading_space or has_trailing_space:
                    issues.append("whitespace_issues")

                # Check for mixed case
                has_upper = str_series.str.contains(r'[A-Z]').any()
                has_lower = str_series.str.contains(r'[a-z]').any()
                if has_upper and has_lower:
                    issues.append("mixed_case")

        if issues:
            col_info["issues"] = issues

        analysis["column_analysis"][col] = col_info

    # Summary of issues
    all_issues = []
    for col, info in analysis["column_analysis"].items():
        for issue in info.get("issues", []):
            all_issues.append({"column": col, "issue": issue})
    analysis["issues_summary"] = all_issues

    return analysis


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python analyze.py <input.csv> [--output analysis.json]")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = None

    if "--output" in sys.argv:
        idx = sys.argv.index("--output")
        if idx + 1 < len(sys.argv):
            output_path = sys.argv[idx + 1]

    try:
        result = analyze(input_path)
        output = json.dumps(result, indent=2, ensure_ascii=False)

        if output_path:
            Path(output_path).write_text(output)
            print(f"Analysis written to {output_path}")
        else:
            print(output)
    except Exception as e:
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        sys.exit(1)
