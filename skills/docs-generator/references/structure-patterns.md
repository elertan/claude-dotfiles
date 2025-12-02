# Structure Patterns

Patterns for detecting codebase structure and generating appropriate documentation.

## Monorepo Detection

### Package Manager Workspaces

**npm/yarn workspaces** - `package.json`:
```json
{
  "workspaces": ["packages/*", "apps/*"]
}
```

**pnpm** - `pnpm-workspace.yaml`:
```yaml
packages:
  - 'packages/*'
  - 'apps/*'
```

**Lerna** - `lerna.json`:
```json
{
  "packages": ["packages/*"]
}
```

### Language-Specific

**Rust** - `Cargo.toml`:
```toml
[workspace]
members = ["crates/*"]
```

**Go** - `go.work`:
```
use (
    ./cmd/app1
    ./pkg/shared
)
```

**Python** - Multiple `pyproject.toml` or `setup.py` files

### Monorepo Documentation Strategy

For monorepos, generate:
1. **Root-level docs**: Overview, architecture, contributing
2. **Per-package docs**: Each package gets full Diátaxis treatment
3. **Shared docs**: Common utilities, types, cross-cutting concerns

```
docs/
├── index.md              # Project overview + package directory
├── architecture.md       # How packages relate
├── contributing.md       # Monorepo-specific contribution guide
├── packages/
│   ├── [package-a]/     # Full docs structure per package
│   └── [package-b]/
└── shared/              # Shared code documentation
```

## Framework Detection

### JavaScript/TypeScript

| Framework | Detection | Doc Focus |
|-----------|-----------|-----------|
| React | `react` in deps | Components, hooks, state |
| Next.js | `next` in deps | Pages, API routes, SSR |
| Express | `express` in deps | Routes, middleware, handlers |
| NestJS | `@nestjs/core` in deps | Modules, controllers, services |
| Vue | `vue` in deps | Components, composables |
| Svelte | `svelte` in deps | Components, stores |

### Python

| Framework | Detection | Doc Focus |
|-----------|-----------|-----------|
| Django | `django` in requirements | Models, views, URLs, admin |
| FastAPI | `fastapi` in requirements | Endpoints, Pydantic models |
| Flask | `flask` in requirements | Routes, blueprints |
| SQLAlchemy | `sqlalchemy` in requirements | Models, queries |

### Go

| Pattern | Detection | Doc Focus |
|---------|-----------|-----------|
| Web API | `net/http` or `gin`/`echo` | Handlers, routes |
| CLI | `cobra` or `urfave/cli` | Commands, flags |
| gRPC | `google.golang.org/grpc` | Services, proto |

### Rust

| Pattern | Detection | Doc Focus |
|---------|-----------|-----------|
| Web | `actix-web` or `axum` | Routes, handlers |
| CLI | `clap` | Commands, arguments |
| Library | No binary targets | Public API |

## Entry Point Detection

### By Language

| Language | Entry Points |
|----------|--------------|
| JavaScript | `main` in package.json, `index.js`, `src/index.ts` |
| Python | `__main__.py`, `main.py`, `app.py`, `manage.py` |
| Go | `main.go`, `cmd/*/main.go` |
| Rust | `src/main.rs`, `src/lib.rs` |
| Java | Classes with `public static void main` |

### By Framework

| Framework | Entry Points |
|-----------|--------------|
| Next.js | `pages/`, `app/`, `next.config.js` |
| Express | File exporting `app.listen()` |
| Django | `manage.py`, `wsgi.py`, `asgi.py` |
| FastAPI | File with `app = FastAPI()` |

## Module Organization Patterns

### Feature-Based (Recommended for larger codebases)

```
src/
├── features/
│   ├── auth/
│   │   ├── components/
│   │   ├── hooks/
│   │   └── api/
│   └── users/
│       ├── components/
│       └── api/
└── shared/
```

**Documentation approach**: Document each feature as a unit.

### Layer-Based

```
src/
├── controllers/
├── services/
├── models/
└── utils/
```

**Documentation approach**: Document by layer, cross-reference.

### Domain-Driven

```
src/
├── domain/
│   ├── entities/
│   └── value-objects/
├── application/
│   └── use-cases/
└── infrastructure/
```

**Documentation approach**: Explain domain concepts, document use cases.

## Configuration Detection

| Config Type | Files | Doc as |
|-------------|-------|--------|
| App config | `.env`, `config/*.js` | Reference (all options) |
| Build config | `webpack.config.js`, `vite.config.ts` | Reference + How-to |
| CI/CD | `.github/workflows/`, `Jenkinsfile` | How-to (deployment) |
| Docker | `Dockerfile`, `docker-compose.yml` | How-to + Reference |
| Linting | `.eslintrc`, `prettier.config.js` | Reference (brief) |

## Test Detection

| Pattern | Framework | Doc Consideration |
|---------|-----------|-------------------|
| `*.test.js`, `*.spec.js` | Jest/Vitest | Document testing conventions |
| `test_*.py`, `*_test.py` | pytest | Document fixtures, patterns |
| `*_test.go` | Go testing | Document test helpers |
| `tests/` directory | Various | Document test organization |

## Documentation Prioritization

### High Priority (Always Document)
- Public API surface
- Entry points
- Configuration options
- Authentication/authorization
- Database models/schema
- Core business logic

### Medium Priority (Document if Complex)
- Internal utilities
- Shared components
- Test utilities
- Build configuration

### Low Priority (Document if Requested)
- Development scripts
- CI/CD details
- Code style configuration
- IDE settings

## Questions to Ask User

When codebase structure is ambiguous:

1. **Monorepo scope**: "Should each package have separate documentation, or unified docs?"
2. **Private vs public**: "Should internal/private modules be documented?"
3. **Legacy code**: "Are there deprecated areas to exclude?"
4. **Depth**: "How detailed should API documentation be?"
5. **Audience**: "Is this for internal developers or external users?"
