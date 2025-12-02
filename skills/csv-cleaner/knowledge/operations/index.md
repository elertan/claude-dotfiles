# Operations Overview

Data cleaning operations modify the dataset to improve quality.

## Available Operations

| Operation | Purpose | When to Use |
|-----------|---------|-------------|
| [Missing Values](missing-values.md) | Handle null/empty data | `null_count > 0` in analysis |
| [Duplicates](duplicates.md) | Remove redundant rows | `exact_duplicate_rows > 0` |
| [Outliers](outliers.md) | Handle extreme values | `has_outliers` issue or unusual stats |
| [Normalization](normalization.md) | Standardize formats | Inconsistent formatting |

## Operation Order

Apply operations in this sequence for best results:

1. **Drop columns** with >50% missing (if applicable)
2. **Remove duplicates** (reduces processing)
3. **Handle outliers** (before imputation affects stats)
4. **Fill missing values** (after outliers handled)
5. **Normalize strings/dates/phones** (format standardization)
6. **Validate** (final check)

## General Principles

- **Preserve data** when possible - flag rather than delete
- **Document changes** - track what was modified
- **Be conservative** - prefer imputation over deletion
- **Check distributions** - verify stats before and after
