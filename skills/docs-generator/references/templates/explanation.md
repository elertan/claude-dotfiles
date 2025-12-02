# Explanation Template

Explanations are **understanding-oriented**. They provide context, background, and insight into how and why things work.

## Template Structure

```markdown
# [Topic/Concept Name]

[Opening paragraph that frames the topic and why it matters]

## Background

[Historical context or problem that led to this approach]

## Core Concepts

### [Concept 1]

[Explanation with analogies if helpful]

### [Concept 2]

[Explanation]

## How It Works

[High-level description of the mechanism or architecture]

```
[Diagram if helpful - ASCII or description]
```

## Design Decisions

### Why [Decision X]?

[Reasoning and tradeoffs considered]

**Alternatives considered:**
- [Alternative A]: [Why not chosen]
- [Alternative B]: [Why not chosen]

### Why [Decision Y]?

[Continue pattern...]

## Tradeoffs

| Approach | Pros | Cons |
|----------|------|------|
| Current | [Benefits] | [Drawbacks] |
| Alternative | [Benefits] | [Drawbacks] |

## When to Use

- [Scenario 1]: [Why this approach fits]
- [Scenario 2]: [Why this approach fits]

## When Not to Use

- [Anti-pattern 1]: [Why this doesn't fit]
- [Anti-pattern 2]: [Consider alternative instead]

## Further Reading

- [Link to deeper resource]
- [Link to related explanation]
```

## Writing Guidelines

### Do
- Provide context and "why"
- Discuss alternatives and tradeoffs
- Connect to the bigger picture
- Use analogies for complex concepts
- Share opinions (with reasoning)

### Don't
- Provide step-by-step instructions (link to how-tos)
- Document every detail (link to reference)
- Be overly technical without context
- Skip the reasoning behind decisions

## When to Write Explanations

- Architecture decisions
- Design patterns used
- Technology choices
- Complex subsystems
- Historical context
- Tradeoffs made

## Example: Architecture Explanation

```markdown
# Authentication Architecture

This document explains our authentication system design and the reasoning behind key decisions.

## Background

The application needed to support:
- Stateless API authentication
- Multiple client types (web, mobile, CLI)
- Fine-grained permissions
- Session management without server-side storage

## Core Concepts

### Stateless Authentication

Traditional session-based auth stores user state on the server. Each request includes a session ID, and the server looks up the associated user.

Stateless auth embeds user information directly in the token. The server validates the token's signature without any database lookup.

### JSON Web Tokens (JWT)

JWTs are self-contained tokens with three parts:
- **Header**: Algorithm and token type
- **Payload**: User data (claims)
- **Signature**: Verification that payload wasn't tampered with

```
eyJhbGciOiJIUzI1NiJ9.eyJ1c2VySWQiOjEyM30.signature
[-----header-----].[-----payload-----].[signature]
```

## How It Works

```
┌─────────┐                    ┌─────────┐
│ Client  │                    │ Server  │
└────┬────┘                    └────┬────┘
     │ POST /login                  │
     │ {email, password}            │
     │─────────────────────────────>│
     │                              │ Verify credentials
     │                              │ Create JWT
     │         {token: "eyJ..."}    │
     │<─────────────────────────────│
     │                              │
     │ GET /api/data                │
     │ Authorization: Bearer eyJ... │
     │─────────────────────────────>│
     │                              │ Verify signature
     │                              │ Extract user from payload
     │         {data: [...]}        │
     │<─────────────────────────────│
```

## Design Decisions

### Why JWT over Sessions?

**Reasoning**: Our API serves multiple clients and needs horizontal scaling. JWTs eliminate the need for shared session storage.

**Alternatives considered:**
- **Server sessions + Redis**: Adds infrastructure complexity and a single point of failure
- **Database sessions**: Adds latency to every authenticated request
- **OAuth tokens**: Overkill for our use case, adds complexity

### Why Short-Lived Tokens with Refresh?

**Reasoning**: Balance security (compromised tokens expire quickly) with UX (users don't re-login constantly).

- Access tokens: 15 minutes
- Refresh tokens: 7 days

If an access token is stolen, the window of exploitation is limited.

## Tradeoffs

| Aspect | JWT | Sessions |
|--------|-----|----------|
| Scalability | Excellent (stateless) | Requires shared storage |
| Revocation | Difficult (wait for expiry) | Immediate |
| Payload size | Larger requests | Minimal (just session ID) |
| Server load | Lower (no lookup) | Higher (session lookup) |

### Handling Token Revocation

The main downside of JWTs is that they can't be revoked before expiry. We mitigate this with:
1. Short expiration times
2. Token blacklist for critical cases (logout, password change)
3. Refresh token rotation

## When to Use This Pattern

- APIs serving multiple client types
- Microservices needing distributed auth
- Serverless environments
- Applications requiring horizontal scaling

## When Not to Use

- **Single-server applications**: Sessions are simpler
- **Frequent permission changes**: JWT claims can become stale
- **Highly sensitive data**: Immediate revocation is critical

## Further Reading

- [JWT Reference](../reference/api/auth.md)
- [How to Configure Authentication](../howto/configure-auth.md)
- [RFC 7519: JSON Web Token](https://tools.ietf.org/html/rfc7519)
```
