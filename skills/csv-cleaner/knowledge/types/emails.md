# Email Validation

## Detection

Run `analyze.py` and check:
- `semantic_type: email` - Detected as email addresses

## Common Issues

| Issue | Example | Solution |
|-------|---------|----------|
| Whitespace | `" user@example.com "` | Trim |
| Mixed case | `User@Example.COM` | Lowercase |
| Invalid format | `not-an-email` | Validate and nullify |
| Typos in domain | `user@gmial.com` | Manual review |
| Disposable emails | `user@tempmail.com` | Optional filtering |

## Operations

### validate_emails
```json
{
  "type": "validate_emails",
  "column": "email"
}
```

This operation:
1. Trims whitespace
2. Converts to lowercase
3. Validates against RFC 5322 pattern
4. Sets invalid emails to `null`

## Validation Pattern

The validation uses a simplified RFC 5322 pattern:
```
^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$
```

Matches:
- `user@example.com` ✓
- `user.name@example.co.uk` ✓
- `user+tag@example.com` ✓

Rejects:
- `not-an-email` ✗
- `user@` ✗
- `@example.com` ✗

## Best Practices

1. **Always lowercase**: Emails are case-insensitive
2. **Trim whitespace**: Common data entry issue
3. **Review failures**: Check why emails failed validation
4. **Consider business rules**: Some domains may be blocked

## Examples

### Basic validation
```json
{
  "operations": [
    {"type": "validate_emails", "column": "email"}
  ]
}
```

### With string preprocessing
```json
{
  "operations": [
    {"type": "normalize_strings", "column": "email", "ops": ["trim", "lowercase"]},
    {"type": "validate_emails", "column": "email"}
  ]
}
```

## Decision Tree

```
Is column detected as email type?
├── Yes →
│   ├── Apply validate_emails
│   ├── Check log for invalid count
│   └── Investigate invalid emails if needed
└── No → Skip email validation
```

## Handling Invalid Emails

After validation:
1. Check `invalid` count in operation log
2. Review original data for patterns:
   - Consistent typos (fix source)
   - Placeholder values (`na@na.com`) - may be intentional
   - Format issues - may need preprocessing

## Limitations

The validation:
- Does NOT verify domain exists
- Does NOT verify mailbox exists
- Does NOT check for disposable emails
- Uses simplified pattern (covers most cases)

For stricter validation, consider additional checks:
- DNS lookup for domain
- SMTP verification (invasive)
- Disposable email domain list
