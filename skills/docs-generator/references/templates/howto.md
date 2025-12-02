# How-To Guide Template

How-to guides are **goal-oriented**. They help users accomplish a specific task.

## Template Structure

```markdown
# How to [Achieve Specific Goal]

[One sentence describing what this guide helps you do]

## Prerequisites

- [What you need before starting]

## Steps

### 1. [First Action]

[Brief context if needed]

```[language]
[code or command]
```

### 2. [Second Action]

```[language]
[code or command]
```

### 3. [Continue as needed...]

## Verification

[How to confirm it worked]

## Common Variations

### [Variation A]
[Brief steps for this variation]

### [Variation B]
[Brief steps for this variation]

## Troubleshooting

| Problem | Solution |
|---------|----------|
| [Error X] | [Fix X] |
| [Issue Y] | [Fix Y] |

## Related

- [Link to related how-to]
- [Link to reference]
```

## Writing Guidelines

### Do
- Start with the goal in the title
- Assume competence (skip basics)
- Provide multiple paths when relevant
- Include common variations
- Focus on the outcome

### Don't
- Explain underlying concepts (link instead)
- Include learning material
- Be too specific about starting point
- Cover every edge case

## Key Differences from Tutorial

| Tutorial | How-To |
|----------|--------|
| For learning | For doing |
| Follows one path | Offers options |
| Explains why | Focuses on what |
| Complete beginner | Has some experience |
| End-to-end project | Specific task |

## Example: Configuration How-To

```markdown
# How to Configure Authentication

Set up JWT-based authentication for your API.

## Prerequisites

- Express app running
- `jsonwebtoken` package installed

## Steps

### 1. Set Environment Variables

```bash
# .env
JWT_SECRET=your-secret-key-here
JWT_EXPIRES_IN=24h
```

### 2. Create Auth Middleware

```javascript
// middleware/auth.js
const jwt = require('jsonwebtoken');

module.exports = (req, res, next) => {
  const token = req.headers.authorization?.split(' ')[1];
  if (!token) return res.status(401).json({ error: 'No token' });

  try {
    req.user = jwt.verify(token, process.env.JWT_SECRET);
    next();
  } catch {
    res.status(401).json({ error: 'Invalid token' });
  }
};
```

### 3. Apply to Protected Routes

```javascript
const auth = require('./middleware/auth');

app.get('/protected', auth, (req, res) => {
  res.json({ user: req.user });
});
```

## Verification

```bash
# Get a token (implement login first)
TOKEN=$(curl -X POST localhost:3000/login -d '{"user":"test"}' | jq -r .token)

# Access protected route
curl -H "Authorization: Bearer $TOKEN" localhost:3000/protected
```

## Common Variations

### Using Cookies Instead of Headers

```javascript
const token = req.cookies.token;
```

### Adding Role-Based Access

```javascript
const requireRole = (role) => (req, res, next) => {
  if (req.user.role !== role) return res.status(403).json({ error: 'Forbidden' });
  next();
};
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "jwt malformed" | Check token format, ensure no extra whitespace |
| "invalid signature" | Verify JWT_SECRET matches between sign and verify |
| Token expires immediately | Check JWT_EXPIRES_IN format (e.g., "24h", "7d") |

## Related

- [API Reference: Auth Middleware](../reference/api/auth.md)
- [Explanation: Why JWT?](../explanation/auth-decisions.md)
```
