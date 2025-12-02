# String Normalization

## Detection

Run `analyze.py` and look for:
- `semantic_type: text` - General text column
- Issue `whitespace_issues` - Leading/trailing spaces
- Issue `mixed_case` - Inconsistent casing

## Common Issues

| Issue | Example | Solution |
|-------|---------|----------|
| Leading/trailing spaces | `" John "` | `trim` |
| Inconsistent case | `"JOHN"`, `"john"`, `"John"` | `lowercase` or `titlecase` |
| Multiple spaces | `"John  Doe"` | `collapse_whitespace` |
| Special characters | `"John@Doe!"` | `remove_special` |
| Control characters | Hidden chars | `trim` handles some |

## Operations

### normalize_strings
```json
{
  "type": "normalize_strings",
  "column": "name",
  "ops": ["trim", "lowercase", "collapse_whitespace"]
}
```

### Available Operations

| Op | Effect | Example |
|----|--------|---------|
| `trim` | Remove leading/trailing whitespace | `" hello "` → `"hello"` |
| `lowercase` | All lowercase | `"HELLO"` → `"hello"` |
| `uppercase` | All uppercase | `"hello"` → `"HELLO"` |
| `titlecase` | Title Case | `"hello world"` → `"Hello World"` |
| `collapse_whitespace` | Multiple spaces → single | `"hello  world"` → `"hello world"` |
| `remove_special` | Remove non-alphanumeric | `"hello@world!"` → `"helloworld"` |
| `remove_digits` | Remove numbers | `"hello123"` → `"hello"` |

## Decision Tree

```
Is column a string/text type?
├── No → Skip
└── Yes →
    ├── Has whitespace issues?
    │   └── Add "trim", "collapse_whitespace"
    ├── Has mixed case?
    │   ├── Is it a name? → Add "titlecase"
    │   ├── Is it a code/ID? → Add "uppercase"
    │   └── General text? → Add "lowercase"
    └── Has special characters?
        ├── Should keep some? → Custom regex
        └── Remove all? → Add "remove_special"
```

## Examples

### Clean names
```json
{
  "operations": [
    {
      "type": "normalize_strings",
      "column": "full_name",
      "ops": ["trim", "collapse_whitespace", "titlecase"]
    }
  ]
}
```

### Clean codes/IDs
```json
{
  "operations": [
    {
      "type": "normalize_strings",
      "column": "product_code",
      "ops": ["trim", "uppercase", "remove_special"]
    }
  ]
}
```

### Clean for comparison
```json
{
  "operations": [
    {
      "type": "normalize_strings",
      "column": "company_name",
      "ops": ["trim", "lowercase", "collapse_whitespace", "remove_special"]
    }
  ]
}
```

## Unicode Considerations

The basic operations handle ASCII well. For international text:

1. **Accents**: May want to preserve (`Café`) or remove for matching
2. **Non-breaking spaces**: `trim` may not catch `\u00A0`
3. **Unicode normalization**: NFC/NFD forms for consistent representation

For advanced Unicode handling, consider custom Python preprocessing.

## Order of Operations

Apply in this order for best results:
1. `trim` - Remove edge whitespace first
2. `collapse_whitespace` - Clean internal spacing
3. `remove_special` or `remove_digits` - Remove unwanted chars
4. Case normalization (`lowercase`/`uppercase`/`titlecase`) - Last
