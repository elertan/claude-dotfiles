#!/usr/bin/env python3
"""
Analyze CSV for functional dependencies and normal form assessment.

Usage:
    python analyze.py input.csv [--output analysis.json] [--sample N]
"""

import argparse
import json
import sys
from pathlib import Path
from itertools import combinations
from typing import Optional

try:
    import pandas as pd
except ImportError:
    print("Error: pandas required. Install with: pip install pandas")
    sys.exit(1)


def load_csv(path: str, sample: Optional[int] = None) -> pd.DataFrame:
    """Load CSV file, optionally sampling rows."""
    df = pd.read_csv(path)
    if sample and len(df) > sample:
        df = df.sample(n=sample, random_state=42)
    return df


def infer_column_types(df: pd.DataFrame) -> dict:
    """Infer semantic types for each column."""
    types = {}
    for col in df.columns:
        series = df[col].dropna()
        if len(series) == 0:
            types[col] = {"type": "empty", "nullable": True}
            continue

        dtype = str(df[col].dtype)
        null_ratio = df[col].isna().sum() / len(df)
        unique_ratio = series.nunique() / len(series)

        # Infer semantic type
        if unique_ratio == 1.0:
            semantic = "unique_identifier"
        elif dtype in ("int64", "float64"):
            semantic = "numeric"
        elif dtype == "object":
            # Check for patterns
            sample_vals = series.head(100).astype(str)
            if sample_vals.str.match(r"^\d{5}(-\d{4})?$").all():
                semantic = "zip_code"
            elif sample_vals.str.match(r"^[\w\.-]+@[\w\.-]+\.\w+$").all():
                semantic = "email"
            elif sample_vals.str.match(r"^\d{4}-\d{2}-\d{2}").any():
                semantic = "date"
            else:
                semantic = "text"
        else:
            semantic = "unknown"

        types[col] = {
            "dtype": dtype,
            "semantic_type": semantic,
            "null_ratio": round(null_ratio, 4),
            "unique_ratio": round(unique_ratio, 4),
            "unique_count": int(series.nunique()),
            "sample_values": series.head(5).tolist()
        }
    return types


def check_fd(df: pd.DataFrame, determinant: list, dependent: str) -> dict:
    """Check if functional dependency holds."""
    # Group by determinant, count unique dependent values per group
    if df[determinant].isna().any().any() or df[dependent].isna().any():
        # Filter out nulls for FD check
        mask = ~df[determinant + [dependent]].isna().any(axis=1)
        df_clean = df[mask]
    else:
        df_clean = df

    if len(df_clean) == 0:
        return {"holds": False, "confidence": 0, "violations": 0}

    groups = df_clean.groupby(determinant)[dependent].nunique()
    violations = (groups > 1).sum()
    total_groups = len(groups)

    confidence = 1.0 - (violations / total_groups) if total_groups > 0 else 0

    return {
        "holds": violations == 0,
        "confidence": round(confidence, 4),
        "violations": int(violations),
        "total_groups": int(total_groups)
    }


def detect_fds(df: pd.DataFrame, confidence_threshold: float = 0.8) -> list:
    """Detect functional dependencies between columns."""
    fds = []
    columns = list(df.columns)

    # Check single-column determinants
    for det_col in columns:
        for dep_col in columns:
            if det_col == dep_col:
                continue

            result = check_fd(df, [det_col], dep_col)
            if result["confidence"] >= confidence_threshold:
                fds.append({
                    "determinant": [det_col],
                    "dependent": dep_col,
                    **result,
                    "status": "confirmed" if result["confidence"] == 1.0 else "needs_review"
                })

    # Check two-column determinants for remaining high-cardinality columns
    high_card_cols = [c for c in columns
                      if df[c].nunique() / len(df) > 0.5]

    for det_cols in combinations(high_card_cols, 2):
        for dep_col in columns:
            if dep_col in det_cols:
                continue

            result = check_fd(df, list(det_cols), dep_col)
            if result["confidence"] >= confidence_threshold:
                # Only add if not already determined by single column
                single_determines = any(
                    fd["determinant"] == [det_cols[0]] and fd["dependent"] == dep_col
                    or fd["determinant"] == [det_cols[1]] and fd["dependent"] == dep_col
                    for fd in fds if fd["confidence"] == 1.0
                )
                if not single_determines:
                    fds.append({
                        "determinant": list(det_cols),
                        "dependent": dep_col,
                        **result,
                        "status": "confirmed" if result["confidence"] == 1.0 else "needs_review"
                    })

    return fds


def find_candidate_keys(df: pd.DataFrame, fds: list) -> list:
    """Find candidate keys based on detected FDs."""
    columns = set(df.columns)
    candidate_keys = []

    # Find columns that are never on the right side of an FD
    all_dependents = set(fd["dependent"] for fd in fds if fd["confidence"] == 1.0)
    must_be_in_key = columns - all_dependents

    # Check if must_be_in_key determines everything
    if must_be_in_key:
        determined = set()
        for fd in fds:
            if fd["confidence"] == 1.0 and set(fd["determinant"]).issubset(must_be_in_key):
                determined.add(fd["dependent"])

        if determined | must_be_in_key == columns:
            candidate_keys.append({
                "columns": sorted(must_be_in_key),
                "is_minimal": True
            })

    # Also check for unique columns (trivial keys)
    for col in columns:
        if df[col].nunique() == len(df) and not df[col].isna().any():
            if not any(set(ck["columns"]) == {col} for ck in candidate_keys):
                candidate_keys.append({
                    "columns": [col],
                    "is_minimal": True
                })

    return candidate_keys


def assess_normal_form(df: pd.DataFrame, fds: list, candidate_keys: list) -> dict:
    """Assess current normal form and identify violations."""
    violations = {"1NF": [], "2NF": [], "3NF": [], "BCNF": []}

    # Get key columns
    key_cols = set()
    for ck in candidate_keys:
        key_cols.update(ck["columns"])

    confirmed_fds = [fd for fd in fds if fd["confidence"] == 1.0]

    # Check 1NF (assume atomic if loaded into pandas)
    # Could check for delimiter-separated values
    for col in df.columns:
        sample = df[col].dropna().head(100).astype(str)
        if sample.str.contains(r"[,;|]").mean() > 0.3:
            violations["1NF"].append(f"Column '{col}' may contain non-atomic values")

    # Check 2NF (partial dependencies)
    for ck in candidate_keys:
        if len(ck["columns"]) > 1:
            for fd in confirmed_fds:
                det = set(fd["determinant"])
                if det < set(ck["columns"]) and fd["dependent"] not in ck["columns"]:
                    violations["2NF"].append(
                        f"Partial dependency: {fd['determinant']} → {fd['dependent']}"
                    )

    # Check 3NF (transitive dependencies)
    for fd in confirmed_fds:
        det = set(fd["determinant"])
        if not det.intersection(key_cols) and fd["dependent"] not in key_cols:
            violations["3NF"].append(
                f"Transitive dependency: {fd['determinant']} → {fd['dependent']}"
            )

    # Check BCNF (determinant must be superkey)
    for fd in confirmed_fds:
        det = set(fd["determinant"])
        is_superkey = any(set(ck["columns"]).issubset(det) for ck in candidate_keys)
        if not is_superkey:
            violations["BCNF"].append(
                f"Non-superkey determinant: {fd['determinant']} → {fd['dependent']}"
            )

    # Determine current NF
    if violations["1NF"]:
        current_nf = "UNF"
    elif violations["2NF"]:
        current_nf = "1NF"
    elif violations["3NF"]:
        current_nf = "2NF"
    elif violations["BCNF"]:
        current_nf = "3NF"
    else:
        current_nf = "BCNF"

    return {
        "current_normal_form": current_nf,
        "violations": {k: v for k, v in violations.items() if v}
    }


def generate_questions(fds: list, column_types: dict) -> list:
    """Generate questions for user about uncertain dependencies."""
    questions = []

    for fd in fds:
        if fd["status"] == "needs_review":
            questions.append({
                "type": "fd_confirmation",
                "fd": {"determinant": fd["determinant"], "dependent": fd["dependent"]},
                "confidence": fd["confidence"],
                "violations": fd["violations"],
                "question": (
                    f"Does {fd['determinant']} → {fd['dependent']} hold? "
                    f"({fd['violations']} violations found, {fd['confidence']*100:.1f}% confidence)"
                )
            })

    # Check for potential semantic dependencies
    semantic_pairs = [
        (["zip_code"], ["city", "state"]),
        (["department_id", "dept_id"], ["department_name", "dept_name", "manager"]),
        (["country"], ["currency", "country_code"]),
    ]

    for det_patterns, dep_patterns in semantic_pairs:
        for col in column_types:
            col_lower = col.lower()
            if any(p in col_lower for p in det_patterns):
                for dep_col in column_types:
                    dep_lower = dep_col.lower()
                    if any(p in dep_lower for p in dep_patterns):
                        # Check if this FD is not already detected
                        exists = any(
                            fd["determinant"] == [col] and fd["dependent"] == dep_col
                            for fd in fds
                        )
                        if not exists:
                            questions.append({
                                "type": "semantic_fd",
                                "fd": {"determinant": [col], "dependent": dep_col},
                                "question": (
                                    f"Does {col} determine {dep_col}? "
                                    f"(Semantic pattern detected)"
                                )
                            })

    return questions


def analyze(csv_path: str, output_path: Optional[str] = None,
            sample: Optional[int] = None) -> dict:
    """Main analysis function."""
    df = load_csv(csv_path, sample)

    print(f"Analyzing {csv_path}...")
    print(f"  Rows: {len(df)}, Columns: {len(df.columns)}")

    # Analysis steps
    column_types = infer_column_types(df)
    print("  Column types inferred")

    fds = detect_fds(df)
    print(f"  Found {len(fds)} functional dependencies")

    candidate_keys = find_candidate_keys(df, fds)
    print(f"  Found {len(candidate_keys)} candidate key(s)")

    nf_assessment = assess_normal_form(df, fds, candidate_keys)
    print(f"  Current normal form: {nf_assessment['current_normal_form']}")

    questions = generate_questions(fds, column_types)

    result = {
        "file": csv_path,
        "rows": len(df),
        "columns": list(df.columns),
        "column_types": column_types,
        "functional_dependencies": fds,
        "candidate_keys": candidate_keys,
        **nf_assessment,
        "questions": questions
    }

    if output_path:
        with open(output_path, "w") as f:
            json.dump(result, f, indent=2, default=str)
        print(f"  Analysis saved to {output_path}")

    return result


def main():
    parser = argparse.ArgumentParser(description="Analyze CSV for normalization")
    parser.add_argument("input", help="Input CSV file")
    parser.add_argument("--output", "-o", help="Output JSON file")
    parser.add_argument("--sample", "-s", type=int, help="Sample N rows for large files")

    args = parser.parse_args()

    if not Path(args.input).exists():
        print(f"Error: File not found: {args.input}")
        sys.exit(1)

    result = analyze(args.input, args.output, args.sample)

    if not args.output:
        print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()
