---
name: docs-generator
description: >
  Generate comprehensive codebase documentation using the Diátaxis framework.
  Creates tutorials (learning-oriented), how-to guides (problem-solving),
  reference docs (technical descriptions), and explanations (conceptual).
  Supports monorepos, multiple languages, and session persistence (resume anytime).
  Use when: (1) documenting a new codebase, (2) updating existing docs after
  code changes, (3) user mentions "generate docs", "document this code",
  "write documentation", (4) creating README, API docs, or user guides.
---

# Documentation Generator

Generate structured codebase documentation using the [Diátaxis framework](https://diataxis.fr/).

## Quick Reference

| Doc Type | Purpose | When to Use |
|----------|---------|-------------|
| Tutorial | Learning-oriented | Onboarding, getting started |
| How-to | Goal-oriented | Solve specific problems |
| Reference | Information-oriented | API docs, config options |
| Explanation | Understanding-oriented | Architecture, design decisions |

See [references/diataxis.md](references/diataxis.md) for decision tree.

## Workflow

### Step 1: Language Selection

Ask user for documentation language:
- English (default)
- Dutch, German, French, Spanish, or specify other

Store selection for entire session. Read [references/language-guidelines.md](references/language-guidelines.md) for style.

### Step 2: Check Existing Progress

```bash
python scripts/progress.py check <project-root>
```

If `docs/.progress.json` exists with pending work:
- Show summary: completed, in-progress, pending docs
- Ask: "Resume from where you left off, or start fresh?"

If no progress file, proceed to analysis.

### Step 3: Codebase Analysis

Perform comprehensive scan:

1. **Detect monorepo** - Check for:
   - `package.json` with `workspaces`
   - `pnpm-workspace.yaml`
   - `lerna.json`
   - `Cargo.toml` with `[workspace]`
   - `go.work`

2. **For each package/root**:
   - Project type: package.json, pyproject.toml, Cargo.toml, go.mod
   - Framework: Parse dependencies (React, Express, Django, etc.)
   - Structure: entry points, src/, test/, config files
   - Key modules: public API, core logic, utilities, shared code

3. **Cross-package analysis** (monorepo):
   - Shared dependencies
   - Internal package references
   - Dependency graph

4. **Save analysis immediately**:
```bash
python scripts/progress.py save <project-root> --phase analysis
```

See [references/structure-patterns.md](references/structure-patterns.md) for pattern detection.

### Step 4: Scope Proposal

Present proposed documentation to user:

```markdown
## Documentation Scope

**Project**: [name] ([framework])
**Type**: [single package / monorepo with N packages]
**Language**: [selected]

### Packages (monorepo only)
- package-a: [brief description]
- package-b: [brief description]

### Proposed Documents

#### Tutorials
- [ ] Getting Started
- [ ] [Feature] Tutorial

#### How-to Guides
- [ ] Configuration
- [ ] Deployment

#### Reference
- [ ] API: [modules]
- [ ] Configuration options

#### Explanation
- [ ] Architecture Overview
- [ ] [Design decision]

Proceed? (yes / modify / skip sections)
```

After confirmation:
```bash
python scripts/progress.py save <project-root> --phase scope
```

### Step 5: Generation

For each approved document:

1. Mark in-progress:
```bash
python scripts/progress.py save <project-root> --doc [path] --status in_progress
```

2. Read relevant template from [references/templates/](references/templates/)

3. Analyze source code for that document

4. Generate following template structure

5. **If uncertain**: Ask user
   - "Document only public API or internals too?"
   - "Config has 50+ options. Document all or common ones?"
   - "Multiple entry points. Which for getting started?"

6. Write to `docs/[category]/[name].md`

7. Mark completed:
```bash
python scripts/progress.py complete <project-root> --doc [path]
```

8. **User can stop anytime** - Progress is saved

### Step 6: Manifest Update

After all documents generated:

```bash
python scripts/manifest.py update <project-root> --files [sources] --docs [generated]
```

This enables incremental updates on future runs.

## Output Structure

### Single Package
```
docs/
├── index.md                    # Main entry + navigation
├── tutorials/
│   ├── index.md
│   └── getting-started.md
├── howto/
│   ├── index.md
│   └── [task].md
├── reference/
│   ├── index.md
│   └── api/[module].md
├── explanation/
│   ├── index.md
│   └── [concept].md
├── .docs-manifest.json
└── .progress.json
```

### Monorepo
```
docs/
├── index.md                    # Root overview + package links
├── architecture.md             # Cross-package architecture
├── packages/
│   ├── [package-a]/
│   │   ├── index.md
│   │   ├── tutorials/
│   │   ├── howto/
│   │   └── reference/
│   └── [package-b]/
│       └── ...
├── shared/                     # Shared utilities/types
├── .docs-manifest.json
└── .progress.json
```

## Existing Docs Handling

If `docs/` exists with files:

1. **Check for .progress.json** - If exists, offer to resume
2. **If no progress file**: Warn that generation will overwrite
3. Ask for explicit confirmation before proceeding
4. Only proceed if user confirms

## Incremental Updates

When codebase changes and user wants to update docs:

```bash
python scripts/manifest.py check <project-root>
```

Output shows:
- **Added**: New files needing documentation
- **Modified**: Files with changed content
- **Removed**: Orphaned documentation

Propose selective regeneration, user confirms before each.

## Resources

### scripts/

| Script | Purpose |
|--------|---------|
| `progress.py` | Session persistence (save/load/resume) |
| `manifest.py` | Change tracking for incremental updates |

### references/

| File | When to Read |
|------|--------------|
| `diataxis.md` | Deciding document type |
| `templates/tutorial.md` | Writing tutorials |
| `templates/howto.md` | Writing how-to guides |
| `templates/reference.md` | Writing reference docs |
| `templates/explanation.md` | Writing explanations |
| `language-guidelines.md` | Non-English documentation |
| `structure-patterns.md` | Detecting codebase patterns, monorepo handling |
