# Reference Template

Reference documentation is **information-oriented**. It describes the machinery and how to operate it.

## Template Structure

```markdown
# [Component/Module Name]

[One-line description]

## Overview

[Brief summary of what this component does - 2-3 sentences max]

## API

### `functionName(param1, param2)`

[One-line description]

**Parameters**

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| param1 | string | Yes | - | [Description] |
| param2 | object | No | `{}` | [Description] |

**Returns**

`Type` - [Description]

**Example**

```[language]
[minimal usage example]
```

**Throws**

- `ErrorType` - [When this error occurs]

---

### `anotherFunction()`

[Continue pattern...]

## Configuration

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| option1 | string | `"default"` | [Description] |
| option2 | number | `100` | [Description] |

## Types

### `TypeName`

```typescript
interface TypeName {
  field1: string;
  field2: number;
}
```

| Field | Type | Description |
|-------|------|-------------|
| field1 | string | [Description] |
| field2 | number | [Description] |

## Constants

| Name | Value | Description |
|------|-------|-------------|
| MAX_SIZE | 1000 | [Description] |
| DEFAULT_TIMEOUT | 5000 | [Description] |

## See Also

- [Related component](./related.md)
- [How to use this](../howto/using-component.md)
```

## Writing Guidelines

### Do
- Be accurate and complete
- Use consistent structure across all entries
- Include type information
- Show minimal examples (not tutorials)
- Document all public API

### Don't
- Explain concepts (link to explanations)
- Provide step-by-step guidance (link to how-tos)
- Include opinions or recommendations
- Skip edge cases or error conditions

## Consistency Rules

1. **Same order** for all function docs: description → parameters → returns → example → throws
2. **Same table format** for all parameter lists
3. **Same code style** in all examples
4. **Same level of detail** across similar items

## Example: API Module Reference

```markdown
# Auth Module

Authentication utilities for JWT-based auth.

## Overview

Provides middleware and helpers for securing routes with JWT tokens. Handles token creation, verification, and user extraction.

## API

### `createToken(payload, options)`

Creates a signed JWT token.

**Parameters**

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| payload | object | Yes | - | Data to encode in token |
| options | TokenOptions | No | `{}` | Token configuration |

**Returns**

`string` - Signed JWT token

**Example**

```javascript
const token = createToken({ userId: 123 }, { expiresIn: '24h' });
```

**Throws**

- `Error` - If JWT_SECRET not configured

---

### `verifyToken(token)`

Verifies and decodes a JWT token.

**Parameters**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| token | string | Yes | JWT token to verify |

**Returns**

`object` - Decoded token payload

**Example**

```javascript
const payload = verifyToken(token);
console.log(payload.userId); // 123
```

**Throws**

- `JsonWebTokenError` - If token is malformed
- `TokenExpiredError` - If token has expired

---

### `authMiddleware`

Express middleware that validates JWT from Authorization header.

**Usage**

```javascript
app.get('/protected', authMiddleware, handler);
```

**Behavior**

1. Extracts token from `Authorization: Bearer <token>`
2. Verifies token
3. Attaches decoded payload to `req.user`
4. Returns 401 if invalid/missing

## Configuration

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| JWT_SECRET | string | - | **Required**. Secret for signing tokens |
| JWT_EXPIRES_IN | string | `"24h"` | Token expiration time |
| JWT_ALGORITHM | string | `"HS256"` | Signing algorithm |

## Types

### `TokenOptions`

```typescript
interface TokenOptions {
  expiresIn?: string;
  algorithm?: string;
}
```

| Field | Type | Description |
|-------|------|-------------|
| expiresIn | string | Duration string (e.g., "1h", "7d") |
| algorithm | string | JWT algorithm |

## See Also

- [How to Configure Authentication](../howto/configure-auth.md)
- [Why JWT?](../explanation/auth-decisions.md)
```
