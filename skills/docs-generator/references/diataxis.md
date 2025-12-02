# Diátaxis Framework

The [Diátaxis framework](https://diataxis.fr/) organizes documentation into four types based on user needs.

## Decision Tree

```
What is the user trying to do?
│
├─► LEARN something new
│   └─► Is it practical/hands-on?
│       ├─► Yes → TUTORIAL
│       └─► No (conceptual) → EXPLANATION
│
└─► ACCOMPLISH a task
    └─► Do they need step-by-step guidance?
        ├─► Yes (specific goal) → HOW-TO
        └─► No (lookup info) → REFERENCE
```

## The Four Types

### Tutorial
**Purpose**: Learning-oriented
**User mindset**: "I want to learn"
**Analogy**: Teaching a child to cook

| Do | Don't |
|----|-------|
| Let learner achieve something meaningful | Teach everything at once |
| Start with simplest case | Explain concepts in depth |
| Ensure every step works | Offer choices or alternatives |
| Focus on concrete steps | Go off on tangents |

**Structure**:
1. What you'll learn (outcomes)
2. Prerequisites
3. Step-by-step with verification
4. Next steps

### How-To Guide
**Purpose**: Goal-oriented
**User mindset**: "I need to solve X"
**Analogy**: Recipe in a cookbook

| Do | Don't |
|----|-------|
| Solve a specific problem | Teach or explain concepts |
| Assume competence | Be too basic |
| Be flexible (multiple paths OK) | Assume specific starting point |
| Focus on results | Cover every edge case |

**Structure**:
1. Problem statement (one sentence)
2. Prerequisites/assumptions
3. Steps to solution
4. Verification/troubleshooting

### Reference
**Purpose**: Information-oriented
**User mindset**: "I need to look up X"
**Analogy**: Encyclopedia entry

| Do | Don't |
|----|-------|
| Describe the machinery | Explain concepts |
| Be accurate and complete | Instruct or guide |
| Structure consistently | Be conversational |
| Use examples sparingly | Provide opinions |

**Structure**:
- Consistent format across entries
- Clear headings for scanning
- Type signatures, parameters, returns
- Brief usage examples

### Explanation
**Purpose**: Understanding-oriented
**User mindset**: "I want to understand why"
**Analogy**: Discussion over coffee

| Do | Don't |
|----|-------|
| Provide context and background | Instruct or provide steps |
| Discuss alternatives and tradeoffs | Be too technical |
| Connect to bigger picture | Document specifics |
| Give opinions (with reasoning) | Be exhaustive |

**Structure**:
1. Context/background
2. Core concepts
3. How things connect
4. Tradeoffs and decisions
5. Further reading

## Mapping Codebase to Doc Types

| Codebase Element | Primary Doc Type | Secondary |
|------------------|------------------|-----------|
| New user onboarding | Tutorial | - |
| API endpoints | Reference | How-to |
| Configuration options | Reference | How-to |
| Architecture decisions | Explanation | - |
| Error handling | How-to | Reference |
| Database schema | Reference | Explanation |
| Auth flow | How-to | Explanation |
| Deployment | How-to | - |
| Design patterns used | Explanation | - |
| CLI commands | Reference | How-to |

## Common Mistakes

1. **Tutorial that explains too much** → Split explanation into separate doc
2. **How-to that teaches** → Focus on the goal, link to tutorial
3. **Reference with opinions** → Move to explanation
4. **Explanation with steps** → Extract to how-to

## Sources

- [Diátaxis](https://diataxis.fr/) - Official documentation
- [Diátaxis Quick Reference](https://manual.theatremanager.com/diataxis/)
