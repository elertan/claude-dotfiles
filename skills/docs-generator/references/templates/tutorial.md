# Tutorial Template

Tutorials are **learning-oriented**. They guide newcomers through a series of steps to complete a meaningful project.

## Template Structure

```markdown
# Tutorial: [Learning Goal as Action]

[1-2 sentence hook: what the reader will accomplish]

## What You'll Learn

- [Concrete skill 1]
- [Concrete skill 2]
- [Concrete skill 3]

## Prerequisites

- [Prerequisite 1 with link if applicable]
- [Prerequisite 2]

## Time Required

Approximately [X] minutes

---

## Step 1: [Action Verb] [Object]

[Brief explanation of what we're doing and why]

```[language]
[code or command]
```

[Expected result or output]

## Step 2: [Action Verb] [Object]

[Brief explanation]

```[language]
[code or command]
```

> **Note**: [Any important callout]

[Expected result]

## Step 3: [Action Verb] [Object]

[Continue pattern...]

---

## Verify It Works

[How to confirm success]

```[language]
[verification command or code]
```

Expected output:
```
[expected output]
```

## What You've Learned

- [Skill 1 achieved]
- [Skill 2 achieved]

## Next Steps

- [Link to next tutorial]
- [Link to related how-to]
- [Link to deeper explanation]

## Troubleshooting

### [Common Issue 1]
[Solution]

### [Common Issue 2]
[Solution]
```

## Writing Guidelines

### Do
- Use imperative verbs: "Create", "Add", "Run", "Configure"
- Show expected output after each step
- Keep steps small and verifiable
- Provide working code that can be copy-pasted
- Use realistic but simple examples

### Don't
- Explain concepts in depth (link to explanations)
- Offer multiple ways to do things
- Include optional steps
- Use placeholder values without explanation
- Assume prior knowledge not listed in prerequisites

## Example: Getting Started Tutorial

```markdown
# Tutorial: Build Your First API Endpoint

Create a working REST endpoint in under 10 minutes.

## What You'll Learn

- Set up a basic Express server
- Create a GET endpoint
- Test with curl

## Prerequisites

- Node.js 18+ installed
- Basic terminal knowledge

## Time Required

Approximately 10 minutes

---

## Step 1: Create Project Directory

Create a new folder for your project:

```bash
mkdir my-api && cd my-api
```

## Step 2: Initialize Node Project

```bash
npm init -y
npm install express
```

You should see `package.json` created.

## Step 3: Create Server File

Create `server.js`:

```javascript
const express = require('express');
const app = express();

app.get('/hello', (req, res) => {
  res.json({ message: 'Hello, World!' });
});

app.listen(3000, () => {
  console.log('Server running on http://localhost:3000');
});
```

## Step 4: Start the Server

```bash
node server.js
```

Expected output:
```
Server running on http://localhost:3000
```

---

## Verify It Works

In a new terminal:

```bash
curl http://localhost:3000/hello
```

Expected output:
```json
{"message":"Hello, World!"}
```

## What You've Learned

- Created an Express server from scratch
- Defined a GET endpoint returning JSON
- Tested an API with curl

## Next Steps

- [Add POST endpoints →](./post-endpoints.md)
- [Connect a database →](./database-setup.md)
```
