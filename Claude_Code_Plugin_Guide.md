# The Definitive Guide to Claude Code Plugins

> A comprehensive knowledge base covering everything from fundamentals to production-grade plugin architecture — built from official documentation, real-world patterns, and security research.

---

## Table of Contents

1. [What Is a Claude Code Plugin?](#1-what-is-a-claude-code-plugin)
2. [Building Blocks of Claude Plugins](#2-building-blocks-of-claude-plugins)
3. [How Plugins Work — End to End](#3-how-plugins-work--end-to-end)
4. [What to Consider Before Building a Plugin](#4-what-to-consider-before-building-a-plugin)
5. [Why Build a Plugin?](#5-why-build-a-plugin)
6. [How Claude Code Interacts with Plugins](#6-how-claude-code-interacts-with-plugins)
7. [Security Design for Claude Plugins](#7-security-design-for-claude-plugins)
8. [Designing Plugins for Repetitive Workflows](#8-designing-plugins-for-repetitive-workflows)
9. [Architecture Best Practices](#9-architecture-best-practices)
10. [Going Beyond: What the Internet Doesn't Tell You](#10-going-beyond-what-the-internet-doesnt-tell-you)

---

## 1. What Is a Claude Code Plugin?

A **Claude Code plugin** is a self-contained, installable extension that adds new capabilities to Claude Code — Anthropic's AI-powered CLI coding assistant. Think of it as a reusable "capability bundle" that Claude can load, understand, and invoke on your behalf.

Plugins are not just prompt wrappers. They are composable units that can contain:

- **Skills** — reusable instruction sets Claude invokes automatically or on demand
- **Agents** — custom sub-agent definitions with their own system prompts and tool access
- **Hooks** — event-driven shell scripts that fire on Claude Code lifecycle events
- **MCP Servers** — external tool integrations via the Model Context Protocol
- **LSP Servers** — real-time code intelligence for specific programming languages
- **Background Monitors** — persistent watchers that stream context to Claude as events arrive

### Plugin vs. Standalone Configuration

| Approach | Skill Syntax | Best For |
|---|---|---|
| **Standalone** (`.claude/` directory) | `/hello` | Personal workflows, single-project, quick experiments |
| **Plugin** (`.claude-plugin/plugin.json` + component dirs) | `/my-plugin:hello` | Team sharing, multi-project reuse, versioned distribution, marketplace |

The key distinction is **shareability and namespace isolation**. Standalone config is fast to set up; plugins are designed for scale.

### The Mental Model

If Claude Code is the operating system, plugins are applications. They extend what Claude can perceive, decide, and act on — without requiring the user to re-explain context every session.

---

## 2. Building Blocks of Claude Plugins

Every plugin is a directory. Its power comes from what you put inside it.

### 2.1 The Manifest — `plugin.json`

**Location:** `.claude-plugin/plugin.json`

The manifest is the single required file (though technically optional if components use default locations). It declares your plugin's identity.

```json
{
  "name": "my-plugin",
  "description": "Automates our internal code review workflow",
  "version": "1.0.0",
  "author": {
    "name": "Engineering Platform Team",
    "email": "platform@company.com"
  },
  "homepage": "https://github.com/company/my-plugin",
  "repository": "https://github.com/company/my-plugin",
  "license": "MIT"
}
```

Key fields:
- **`name`** — doubles as the skill namespace prefix (e.g., skills become `/my-plugin:skill-name`)
- **`version`** — if set, users receive updates only when you increment this; if omitted, every git commit is treated as a new version
- **`description`** — shown in the plugin manager UI when users browse or install

> ⚠️ **Common mistake:** Never put `skills/`, `agents/`, or `hooks/` *inside* `.claude-plugin/`. Only `plugin.json` goes there. All component directories live at the plugin root.

### 2.2 Skills

**Location:** `skills/<skill-name>/SKILL.md`

Skills are the lightest-weight extension primitive. A skill is a markdown file with YAML frontmatter that gives Claude a reusable set of instructions.

```text
my-plugin/
└── skills/
    └── code-review/
        ├── SKILL.md          ← required
        ├── reference.md      ← optional supporting detail
        └── scripts/          ← optional helper scripts
```

```markdown
---
description: Reviews code for security vulnerabilities, performance issues, and style violations. Use when reviewing PRs, checking diffs, or auditing code quality.
disable-model-invocation: true
---

# Code Review Skill

When reviewing code:
1. Check for injection vulnerabilities (SQL, shell, path traversal)
2. Identify N+1 query patterns
3. Flag missing error handling
4. Verify test coverage for new logic
5. Note style violations against $ARGUMENTS (defaults to our internal guide)

Output findings as: [SEVERITY] Location — Issue — Suggested fix
```

**Key frontmatter fields:**
- `description` — critical for Claude to know *when* to invoke the skill automatically
- `disable-model-invocation` — set to `true` for skills that are pure instruction sets (no sub-LLM call)
- `$ARGUMENTS` — captures any text the user passes after the skill name at invocation time

### 2.3 Agents (Sub-agents)

**Location:** `agents/<agent-name>.md`

Agents are specialized Claude instances with their own system prompts, restricted tool sets, and behavior constraints. Unlike skills (which are invoked directly), agents can be delegated to by the orchestrator Claude instance.

```markdown
---
name: security-reviewer
description: A security-focused agent that audits code changes for vulnerabilities
tools: Read, Grep, Glob
---

You are a security engineer reviewing code changes.

Your scope is limited to security analysis. Do not suggest refactors or style changes.
Flag any finding with: [CRITICAL|HIGH|MEDIUM|LOW] — CWE reference — File:Line — Remediation
```

**Restrictions for plugin-shipped agents:** Hooks, `mcpServers`, and `permissionMode` are deliberately not supported inside agent definitions for security reasons. These must be declared at the plugin root level.

### 2.4 Hooks

**Location:** `hooks/hooks.json`

Hooks let your plugin react to Claude Code lifecycle events by running shell commands automatically. They are the automation backbone for enforcing policies, running checks, and integrating with external systems.

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [{
          "type": "command",
          "command": "jq -r '.tool_input.file_path' | xargs npm run lint:fix"
        }]
      }
    ],
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [{
          "type": "command",
          "command": "echo 'Running safety check...' && jq -r '.tool_input.command' | grep -qvE '(rm -rf|sudo|curl.*sh)' || exit 1"
        }]
      }
    ]
  }
}
```

**Supported hook events:**

| Event | When it fires |
|---|---|
| `PreToolUse` | Before Claude executes any tool |
| `PostToolUse` | After a tool completes |
| `ConfigChange` | When session configuration is mutated |
| `SessionStart` | When a new Claude Code session begins |
| `SessionEnd` | When a session terminates |

### 2.5 MCP Servers

**Location:** `.mcp.json` at plugin root

MCP (Model Context Protocol) servers extend Claude with tools backed by external APIs or local processes. Your plugin can bundle MCP server configurations so users get the integration automatically upon install.

```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@company/github-mcp-server"],
      "env": {
        "GITHUB_TOKEN": "${GITHUB_TOKEN}"
      }
    },
    "datadog": {
      "command": "python3",
      "args": ["-m", "datadog_mcp"],
      "env": {
        "DD_API_KEY": "${DD_API_KEY}"
      }
    }
  }
}
```

### 2.6 LSP Servers

**Location:** `.lsp.json` at plugin root

LSP (Language Server Protocol) servers give Claude real-time code intelligence — completions, diagnostics, go-to-definition — for specific languages. Most common languages have official LSP plugins; build custom ones only for proprietary or niche languages.

```json
{
  "terraform": {
    "command": "terraform-ls",
    "args": ["serve"],
    "extensionToLanguage": {
      ".tf": "terraform",
      ".tfvars": "terraform"
    }
  }
}
```

### 2.7 Background Monitors

**Location:** `monitors/monitors.json`

Monitors run persistent background processes that stream context to Claude as events arrive. Claude Code starts them automatically when the plugin is active.

```json
[
  {
    "name": "error-log",
    "command": "tail -F ./logs/error.log",
    "description": "Application error log — notify Claude of new ERROR entries"
  },
  {
    "name": "test-watcher",
    "command": "npm run test:watch --reporter=json",
    "description": "Live test results — alert Claude when tests fail"
  }
]
```

### 2.8 Default Settings

**Location:** `settings.json` at plugin root

Plugins can ship default Claude Code settings that activate when the plugin is enabled. Currently supported keys: `agent` and `subagentStatusLine`.

```json
{
  "agent": "security-reviewer"
}
```

This activates the named agent from the plugin's `agents/` directory as the main thread for the session.

### 2.9 Executables

**Location:** `bin/` at plugin root

Executables placed here are added to the Bash tool's `PATH` while the plugin is active, making CLI utilities available to Claude without PATH manipulation by the user.

### Complete Plugin Directory Structure

```text
my-plugin/
├── .claude-plugin/
│   └── plugin.json              ← manifest (only file here)
├── skills/
│   └── code-review/
│       ├── SKILL.md
│       └── reference.md
├── commands/                    ← legacy flat-file format (prefer skills/)
├── agents/
│   └── security-reviewer.md
├── hooks/
│   └── hooks.json
├── .mcp.json                    ← MCP server configs
├── .lsp.json                    ← LSP server configs
├── monitors/
│   └── monitors.json
├── bin/                         ← executables added to PATH
├── settings.json                ← default settings
└── README.md
```

---

## 3. How Plugins Work — End to End

Understanding the full lifecycle helps you build plugins that behave predictably.

### 3.1 Installation

Plugins are installed from **marketplaces** — repositories containing a `marketplace.json` catalog. There are two official ones:

- `claude-plugins-official` — curated by Anthropic, available by default
- `claude-plugins-community` — community-submitted, add with `/plugin marketplace add anthropics/claude-plugins-community`

Users can also install from private team marketplaces or directly via `--plugin-dir` for local development.

```bash
# Install from marketplace
/plugin install @marketplace-name/plugin-name

# Load locally for development
claude --plugin-dir ./my-plugin

# Load from a hosted zip (e.g., CI build artifact)
claude --plugin-url https://example.com/my-plugin.zip
```

### 3.2 Loading and Activation

When Claude Code starts with a plugin:

1. The manifest is read and the plugin's identity is registered
2. Skills are discovered and added to Claude's available command list
3. Agents are loaded into the agent registry
4. Hooks are registered for the relevant lifecycle events
5. MCP servers are started as child processes
6. LSP servers are initialized
7. Background monitors begin streaming

All of this happens before Claude's first response. Skills appear under `/plugin-name:skill-name`; agents appear in `/agents`.

### 3.3 Skill Invocation — Two Paths

Skills can be triggered in two ways:

**Explicit invocation** — user types `/plugin-name:skill-name [arguments]`

**Automatic invocation** — Claude reads the skill's `description` frontmatter and decides to use it based on task context. This is why a precise, trigger-condition-aware description is the most important part of any skill.

```yaml
# Weak description — Claude may miss the trigger
description: Code review helper

# Strong description — Claude knows exactly when to invoke
description: Reviews code changes for security vulnerabilities and style issues. Use when the user asks to review a PR, audit a diff, check code quality, or before merging any branch.
```

### 3.4 Hook Execution Flow

```
User request
    ↓
Claude decides to use a tool (e.g., Write, Bash, Edit)
    ↓
PreToolUse hooks fire → shell command runs → result returned to Claude
    ↓
Tool executes
    ↓
PostToolUse hooks fire → shell command runs → result returned to Claude
    ↓
Claude continues
```

Hooks receive JSON on stdin describing the tool call. They can:
- Return exit code `0` to allow the action
- Return non-zero to block it (Claude sees the stderr output as context)
- Return structured JSON to add context to Claude's next decision

### 3.5 Namespacing

All plugin skills are prefixed: `/plugin-name:skill-name`. This prevents conflicts when multiple plugins have overlapping skill names. The prefix comes from the `name` field in `plugin.json`.

During development, to change the prefix, just update `name` in the manifest and run `/reload-plugins`.

### 3.6 Hot Reloading

During development, run `/reload-plugins` to pick up changes without restarting Claude Code. This reloads skills, agents, hooks, MCP servers, and LSP servers. Monitors restart automatically.

---

## 4. What to Consider Before Building a Plugin

Before writing a single line, answer these questions. They determine whether you're building the right thing.

### 4.1 Plugin vs. Standalone Config?

| Signal | Build a plugin |
|---|---|
| Multiple people will use this | ✅ |
| Works across several projects | ✅ |
| Needs versioning and controlled rollout | ✅ |
| Has external dependencies (MCP servers, LSP) | ✅ |
| It's just for you, one project, quick test | ❌ — use standalone |

Start standalone. Convert to a plugin when sharing becomes necessary.

### 4.2 What Is the Core Capability?

Be specific. "Developer productivity" is too broad. "Automatically lints files after every edit and surfaces lint results inline" is actionable. Your capability statement should complete this sentence: *"With this plugin enabled, Claude can now ____."*

### 4.3 Scope and Boundaries

- What tools does this plugin need? (File read, Bash, MCP calls?)
- What should it explicitly *not* do? (Scope creep breaks trust)
- Does it need persistent state between sessions? (If yes, think about how — file-based, MCP server state, etc.)
- Does it need network access? (MCP server vs. Bash curl — big security difference)

### 4.4 Dependency Inventory

- External binaries required on the user's machine?
- API keys or environment variables needed?
- Network access to specific domains?
- Other plugins this depends on?

Document all dependencies in your README and fail gracefully when they're missing.

### 4.5 Namespace Conflicts

Choose a plugin name that is unique. If `name: "review"` conflicts with another plugin, users will see strange behavior. Prefer organization-scoped names: `acme-code-review` over `code-review`.

### 4.6 Version Strategy

- **Explicit version in manifest:** users receive updates only when you bump the version. Good for stability, requires discipline.
- **No version (git commit SHA):** every commit is a new version. Good for rapid iteration, can break users unexpectedly.

Pick explicit versioning for any plugin used by more than yourself.

### 4.7 Distribution Channel

- **Personal use:** install from local directory or `--plugin-dir`
- **Team use:** private git repository as a marketplace
- **Community:** submit to `claude-plugins-community` after passing `claude plugin validate`
- **Enterprise:** private marketplace hosted behind your org's auth

---

## 5. Why Build a Plugin?

### 5.1 Encode Institutional Knowledge

Every team has "the way we do things" — code review standards, deployment runbooks, onboarding checklists, naming conventions. Without a plugin, this knowledge lives in wikis that Claude can't access, or gets re-explained in every session. A plugin makes that knowledge permanently available and automatically applied.

### 5.2 Enforce Standards Consistently

Hooks are enforcement mechanisms. A `PostToolUse` hook on `Write|Edit` that runs your linter means code that violates style standards never gets committed — Claude sees the lint output and fixes it before moving on. No human review step needed for mechanical checks.

### 5.3 Compress Repetitive Context

If you find yourself typing the same background in every session ("we use hexagonal architecture, our DB layer lives in `src/infra/`, never use `any` in TypeScript..."), that context belongs in a plugin skill. A well-written skill primes Claude with everything it needs at session start.

### 5.4 Create Specialized AI Personas

Agents let you create focused Claude instances — a security reviewer that only thinks about vulnerabilities, a documentation writer that only generates docs, a migration planner that only handles database schema changes. Specialization reduces cognitive overhead and produces better outputs.

### 5.5 Integrate Your Toolchain

MCP servers turn Claude Code into a hub that talks directly to your issue tracker, CI system, observability platform, and internal APIs. Instead of copy-pasting from Datadog into the chat, Claude queries Datadog directly and acts on the data.

### 5.6 Scale Across Your Org

A plugin installed org-wide means every engineer's Claude Code instance has the same baseline capabilities, standards, and tool integrations. One update to the plugin propagates everywhere. This is qualitatively different from asking everyone to maintain their own `.claude/` directories.

### 5.7 Monetization and Community

Well-built plugins can be published to the community marketplace. If you've solved a general problem elegantly (e.g., a plugin that integrates with a popular SaaS tool), there's a real user base waiting for it.

---

## 6. How Claude Code Interacts with Plugins

Understanding this layer makes you a better plugin author.

### 6.1 The Orchestrator Model

Claude Code operates as an orchestrator. It has a main thread (the conversation) and can spawn sub-agents for delegated tasks. Plugins extend what the orchestrator knows (skills, context) and what it can do (agents, tools via MCP).

The interaction model:

```
User message
    ↓
Main Claude instance (orchestrator)
    ├── Reads loaded skill descriptions → decides which to invoke
    ├── Sees available MCP tools → decides which to call
    ├── Can spawn agents from agents/ → delegates subtasks
    └── Hooks intercept tool calls → shell scripts run
```

### 6.2 Context Injection

Skills don't just give Claude instructions — they give it *context at the right moment*. When a skill is invoked (explicitly or automatically), its `SKILL.md` content is injected into Claude's working context. This is why progressive disclosure matters: put the most critical information near the top of the skill file, and load detailed reference material only when needed.

### 6.3 Tool Routing

When a plugin includes an MCP server, Claude sees the server's tools as first-class capabilities alongside built-in tools like `Read`, `Write`, and `Bash`. Claude decides which tool to use based on the task — it doesn't need to be told "use the GitHub MCP server for this."

This means **your MCP tool descriptions are as important as your skill descriptions**. Claude routes to tools based on their descriptions. Vague descriptions produce poor routing.

### 6.4 Agent Delegation

The orchestrator can delegate to plugin-defined agents. The agent runs with its own system prompt and restricted tool set, produces output, and returns it to the orchestrator. This is the mechanism for creating specialized sub-workflows within a session.

Example flow:
```
User: "Review this PR for security issues"
    ↓
Orchestrator sees the security-reviewer agent is available
    ↓
Delegates to security-reviewer agent with the diff as input
    ↓
security-reviewer runs with Read, Grep, Glob (only) and returns findings
    ↓
Orchestrator synthesizes findings into response
```

### 6.5 Monitor Feed

Background monitors run as persistent processes and pipe stdout to Claude as notifications. Claude incorporates these into its context as they arrive. This makes monitors powerful for ambient awareness — Claude knows about new test failures, error logs, or external status changes without being asked.

### 6.6 Reload Without Restart

`/reload-plugins` is your development inner loop. It hot-swaps skills, agents, hooks, and MCP/LSP configurations mid-session. Use it constantly during development.

---

## 7. Security Design for Claude Plugins

This is the section that separates thoughtful plugin authors from ones who create real risk. Plugins are powerful — that power needs constraints.

### 7.1 The Trust Pyramid Problem

When a user installs a plugin, they implicitly trust every component inside it: skills, agents, hooks, MCP servers, monitors, and executables. **Trust is transitive and often opaque.** A single malicious hook or MCP server inside an otherwise helpful plugin can exfiltrate API keys, execute arbitrary code, or tamper with files.

Real CVEs have exploited this:
- **CVE-2025-59536:** Remote code execution via malicious hooks planted in a repository's settings file
- **CVE-2026-21852:** API key exfiltration by overriding environment variables through a rogue MCP server

### 7.2 Principle of Least Privilege for Plugin Components

**Skills:** Only request the tools you need. If a skill only needs to read files, explicitly restrict it:

```yaml
---
description: Analyzes log files for error patterns
tools: Read, Glob
---
```

**Agents:** Define explicit tool lists. Don't give agents access to `Bash` unless strictly necessary. A documentation agent needs `Read` and `Write` — not `Bash`.

```markdown
---
name: doc-writer
tools: Read, Write, Glob
---
```

**Hooks:** The most dangerous surface. Design hooks defensively:

- Always quote shell variables: `"$FILE_PATH"` not `$FILE_PATH`
- Validate and sanitize all inputs before using in shell commands
- Never pipe user-provided content directly to `sh` or `bash`
- Use an allowlist approach: block everything that isn't explicitly permitted

```bash
# Dangerous
command: "$(jq -r '.tool_input.file_path')" && npm run check

# Safer
command: "FILE=$(jq -r '.tool_input.file_path' | sed 's/[^a-zA-Z0-9._/-]//g') && [ -f \"$FILE\" ] && npm run check -- \"$FILE\""
```

**MCP Servers:** Treat each MCP server as a separate trust boundary:
- Only ship MCP servers you control or have fully audited
- Use environment variable references for secrets — never hardcode credentials in `.mcp.json`
- Scope API tokens to the minimum required permissions
- Prefer read-only tokens where write access isn't needed

### 7.3 Input Validation at Every Layer

Hooks receive JSON from Claude on stdin. Treat this as untrusted input. Always:
- Parse with `jq` and extract specific fields, never eval the whole blob
- Validate field types and lengths
- Reject inputs containing shell metacharacters when used in commands

```bash
# Extract and validate
FILE_PATH=$(echo "$STDIN" | jq -r '.tool_input.file_path // empty')
if [ -z "$FILE_PATH" ]; then exit 0; fi
# Ensure no path traversal
case "$FILE_PATH" in *../*) exit 1 ;; esac
```

### 7.4 Secret Management

Never store secrets in plugin files. Use environment variable references:

```json
{
  "mcpServers": {
    "github": {
      "env": {
        "GITHUB_TOKEN": "${GITHUB_TOKEN}"
      }
    }
  }
}
```

Document in your README exactly which environment variables are required. Fail gracefully (with a clear message) if they're missing rather than silently proceeding with reduced capability.

### 7.5 Sandbox Your Development and Testing

When building plugins with hooks or MCP servers:
- Develop inside a container or VM, not on your main machine
- Never run Claude Code as root during plugin development
- Use temporary API tokens with limited scope for testing
- Run `claude plugin validate` before every distribution

### 7.6 Monitor for Supply Chain Risk

If your plugin depends on npm packages (via npx in MCP server commands) or Python packages:
- Pin exact versions: `npx -y @company/server@1.2.3` not `@latest`
- Review dependency changelogs before bumping versions
- Use lock files (`package-lock.json`) in any bundled MCP server code

### 7.7 ConfigChange Hook as a Security Sensor

Use the `ConfigChange` hook to detect unexpected configuration mutations during a session. This mirrors the security value of monitoring CI configuration or Terraform state changes:

```json
{
  "hooks": {
    "ConfigChange": [
      {
        "hooks": [{
          "type": "command",
          "command": "echo \"Config changed: $(jq -r '.change_type')\" >> ~/.claude/audit.log"
        }]
      }
    ]
  }
}
```

### 7.8 Distribution Signing and Verification

- Publish plugins with explicit version pinning in `plugin.json`
- The community marketplace pins approved plugins to a specific commit SHA — don't bypass this
- For enterprise distribution, consider signing your plugin zip archives and verifying on install via a PreInstall hook

### 7.9 Security Checklist Before Publishing

- [ ] No hardcoded secrets anywhere in the plugin
- [ ] All hook shell commands use quoted variables
- [ ] MCP servers pin dependency versions
- [ ] Agent definitions have explicit tool restrictions
- [ ] `claude plugin validate` passes with no warnings
- [ ] README documents all required environment variables
- [ ] Tested in a sandboxed environment (container/VM)
- [ ] No unnecessary network access
- [ ] Principle of least privilege applied to every component

---

## 8. Designing Plugins for Repetitive Workflows

This is where plugins deliver the most leverage — converting high-friction, multi-step workflows into one-command operations.

### 8.1 Identify the Repetition

Before designing, map the current manual workflow:

```
Without plugin (current state):
  1. Developer opens PR
  2. Copies diff into Claude chat
  3. Types "Review this for security issues"
  4. Receives findings
  5. Manually creates GitHub comments
  6. Updates ticket in Jira
  7. Runs the linter manually
  8. Fixes issues
  Repeat for every PR — ~20 minutes each

With plugin:
  /pr-tools:full-review PR-456
  → Claude fetches diff via GitHub MCP
  → security-reviewer agent analyzes it
  → PostToolUse hook runs linter
  → GitHub MCP posts review comments
  → Jira MCP updates ticket status
  → 2 minutes, zero copy-paste
```

Map the "before" state in detail. Every manual step is a candidate for automation.

### 8.2 The Four Automation Patterns for Skills

**Pattern 1: Context Loader**
A skill that primes Claude with everything it needs at the start of a session or task. No action — just context injection.

```markdown
---
description: Load project context. Use at the start of any session working on the payments service.
---
# Payments Service Context

This service handles all payment processing. Key facts:
- Written in Go 1.22
- Uses PostgreSQL with GORM
- Follows hexagonal architecture (domain/ infra/ application/)
- Never use any external HTTP calls inside domain/ layer
- All money amounts are in cents (int64), never floats
```

**Pattern 2: Workflow Executor**
A skill that runs a multi-step process — fetch data, analyze, act, report.

```markdown
---
description: Run the full pre-deployment checklist. Use before any production deployment.
---
# Pre-Deploy Checklist

Run the following checks IN ORDER and stop if any fail:
1. Run `npm run test:all` — must pass 100%
2. Run `npm run build` — must produce zero warnings
3. Check `git log --oneline main..HEAD` — confirm all commits are reviewed
4. Verify environment variables in `.env.production.example` are all set
5. Run `npm run db:migrate:dry-run` — confirm migration is safe

Report status of each step clearly. Block deployment if any check fails.
```

**Pattern 3: State-Aware Operator**
A skill that checks external state (via MCP tools) and acts conditionally.

```markdown
---
description: Triage incoming support tickets. Use when asked to handle the support queue.
---
# Support Triage Skill

For each open ticket in Intercom:
1. Read ticket content and conversation history
2. Classify: [BUG | FEATURE_REQUEST | QUESTION | BILLING]
3. For BUG: create a Linear issue, link it to the ticket, reply to customer with ETA
4. For BILLING: escalate to billing@company.com, mark as Priority 1
5. For QUESTION: search our docs, reply with relevant link, close if answered
6. For FEATURE_REQUEST: add to the feedback Notion database, reply with thanks
```

**Pattern 4: Feedback Loop**
A skill paired with hooks that creates a continuous improvement cycle.

```markdown
---
description: Write code following TDD — write test first, then implementation.
---
# TDD Workflow

ALWAYS follow this order:
1. Write failing tests in `*.test.ts` file
2. Run tests (they must fail — confirm red state)
3. Write minimal implementation to pass tests
4. Run tests again (must be green)
5. Refactor only after green

The PostToolUse hook will automatically run tests after each Write.
Use test output to guide your next action.
```

### 8.3 Hooks as Workflow Glue

Hooks are what make skills truly automatic. Design hooks that:

- **Auto-correct:** lint and format immediately after code is written
- **Auto-verify:** run tests after any implementation change
- **Auto-document:** update a change log after significant edits
- **Auto-notify:** post to Slack when a milestone is reached

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [{
          "type": "command",
          "command": "FILE=$(jq -r '.tool_input.file_path') && npx tsc --noEmit 2>&1 || true"
        }]
      }
    ]
  }
}
```

The key insight: hooks return their stdout to Claude. A TypeScript error in the hook output is read by Claude, which then fixes the error — all without user intervention.

### 8.4 Stateful Workflows with Monitors

For workflows that need to react to external events over time, pair a monitor with a skill:

```json
// monitors/monitors.json
[{
  "name": "ci-status",
  "command": "scripts/poll-ci.sh",
  "description": "CI pipeline status — alert Claude when a build fails or completes"
}]
```

```bash
# scripts/poll-ci.sh
while true; do
  STATUS=$(curl -s $CI_API/status | jq -r '.state')
  if [ "$STATUS" = "failed" ]; then
    echo "CI FAILED: $(curl -s $CI_API/status | jq -r '.message')"
  fi
  sleep 30
done
```

Claude receives the monitor output as a notification and can automatically triage the failure, open an issue, and notify the team — without the developer needing to check CI.

### 8.5 Composing Skills into Larger Workflows

Skills can reference each other in their instructions. Design a skill hierarchy:

```
Level 1: Atomic skills
  /my-plugin:fetch-pr        — fetches PR diff via GitHub MCP
  /my-plugin:security-check  — runs security analysis
  /my-plugin:post-review     — posts GitHub review comments

Level 2: Composite workflow skills
  /my-plugin:full-review     — calls fetch-pr, security-check, post-review in sequence
```

In your composite skill:

```markdown
---
description: Run complete PR review. Use when asked to review a PR end to end.
---
# Full PR Review

Follow this exact sequence:
1. Invoke the fetch-pr skill with $ARGUMENTS as the PR number
2. Invoke the security-check skill with the fetched diff
3. Invoke the post-review skill with the findings
4. Report a summary of what was posted
```

---

## 9. Architecture Best Practices

Lessons from building production-grade plugins.

### 9.1 Design for Observability

Your plugin runs autonomously. You need to know what it did.

- Write audit logs from hooks: `echo "$(date) HOOK:PostToolUse FILE:$FILE" >> ~/.claude/plugin-audit.log`
- Use monitor output as a real-time feed, not just a trigger
- Add a `/my-plugin:status` skill that reports the plugin's current state (MCP server health, recent hook activity, etc.)

### 9.2 Fail Gracefully and Loudly

When dependencies are missing, don't silently degrade:

```bash
# In a hook
if ! command -v jq &>/dev/null; then
  echo "ERROR: jq is required by my-plugin hooks. Install with: brew install jq" >&2
  exit 0  # Exit 0 to not block Claude, but stderr surfaces the issue
fi
```

Skills should include explicit fallback instructions:

```markdown
If the GitHub MCP server is unavailable, ask the user to paste the PR diff directly.
```

### 9.3 Progressive Disclosure in Skills

Don't dump everything into `SKILL.md`. Use the reference file pattern:

```text
skills/deploy/
├── SKILL.md          ← core instructions (100-200 lines max)
└── reference.md      ← deep detail loaded on demand
```

In `SKILL.md`, reference the detail file explicitly: *"For edge cases and environment-specific configurations, see the reference guide."* Claude will load it when needed.

### 9.4 Idempotency

Design skills and hooks to be safe to run multiple times. A hook that runs `npm run lint:fix` is idempotent. A hook that appends to a file without deduplication is not.

Test: *"What happens if this skill/hook runs twice in a row on the same input?"* The answer should be: nothing bad.

### 9.5 One Plugin, One Domain

Resist the temptation to build a Swiss army knife. A plugin that does code review, deployment, ticket management, and documentation will have naming conflicts, permission sprawl, and unclear boundaries.

**Better:** `acme-code-review`, `acme-deploy`, `acme-jira` — three focused plugins that can be installed independently.

### 9.6 Namespace Your Everything

Plugin name → skill names → MCP server names → agent names. All should share a coherent namespace. Users who install your plugin should immediately understand what every component belongs to.

```
Plugin: acme-review
Skills: /acme-review:pr, /acme-review:security, /acme-review:docs
Agents: acme-security-reviewer, acme-doc-auditor
```

### 9.7 Version and Changelog Discipline

Every published plugin change should include:
1. Bumped version in `plugin.json`
2. Entry in `CHANGELOG.md` describing what changed
3. A `README.md` section on migration if breaking changes exist

Users can't adopt updates confidently without this.

### 9.8 Test Matrix

Before releasing any version, test:

| Scenario | Check |
|---|---|
| Clean install (no prior version) | Skills appear, MCP starts, hooks fire |
| Upgrade from prior version | Settings migrate, no stale skills |
| Missing dependencies | Graceful error messages |
| Multiple plugins co-installed | No namespace conflicts |
| Concurrent skill invocations | No race conditions in hooks |
| `--plugin-dir` local load | Overrides marketplace version |

### 9.9 Document the Why, Not Just the How

Your `README.md` should explain:
- **The problem this plugin solves** (don't assume users understand the context)
- **What changes in Claude's behavior** when the plugin is enabled
- **Required setup** (env vars, binaries, accounts)
- **Known limitations** (what it can't do, when not to use it)

Your skill `description` fields should explain *when to use the skill*, not what the skill is called.

### 9.10 Treat Plugin Development Like Production Code

- Use a git repository from day one
- Write tests for hook scripts (shell unit tests with bats or shunit2)
- Use CI to run `claude plugin validate` on every PR
- Tag releases; use GitHub releases for distribution
- Review security before every publish

---

## 10. Going Beyond: What the Internet Doesn't Tell You

Most guides stop at "here's the manifest format." Here's what you actually need to know to build plugins that work at scale.

### 10.1 The Description Is Your Most Important Code

Every resource focuses on file structure. The single highest-leverage thing you can do is write precise skill and tool descriptions. Claude's decision to use a skill is entirely based on the description. Test descriptions by asking: "Would Claude know, from this description alone, exactly when to use this skill and when not to?"

Run this test: describe a scenario to Claude without invoking the skill explicitly. Does Claude automatically use it? If not, rewrite the description.

### 10.2 Skill Descriptions as Negative Constraints

Include what the skill is *not* for:

```yaml
description: Reviews TypeScript code for type safety and runtime errors. Use when reviewing TS files. Do NOT use for JavaScript, Python, or configuration files.
```

Negative constraints prevent Claude from over-applying a skill to contexts where it doesn't help.

### 10.3 The Hook → Claude Feedback Loop Is Underutilized

Most hook examples show hooks that validate or block. But hooks that *return rich context* are far more powerful. Structure your hook output as actionable data:

```bash
# Instead of just running lint silently
jq -r '.tool_input.file_path' | xargs eslint --format json 2>/dev/null | \
  jq '[.[] | select(.errorCount > 0) | {file: .filePath, errors: [.messages[] | {line, message, ruleId}]}]'
```

This structured JSON output is parsed by Claude, which then understands *exactly* what to fix and where — no guessing, no re-reading the file.

### 10.4 MCP Tool Descriptions Are Claude's Routing Table

When you ship an MCP server, every tool's description is Claude's decision criterion for calling it. Write MCP tool descriptions with the same care as skill descriptions:

```
# Weak MCP tool description
name: create_issue
description: Creates an issue

# Strong MCP tool description  
name: create_issue
description: Creates a new GitHub issue in the specified repository. Use when the user asks to file a bug, report a problem, track a task, or create a ticket. Requires repository name and issue title at minimum.
```

### 10.5 Agents vs. Skills — When to Use Each

A common source of confusion:

| Use a Skill when | Use an Agent when |
|---|---|
| Instructions can be followed by the main Claude instance | The task benefits from strict tool isolation |
| No strict tool restriction needed | You want a different "persona" for the subtask |
| The task is linear and well-defined | The subtask requires deep focus without distraction |
| Speed matters (no sub-agent spawn overhead) | The output should be clearly attributable to a specialized role |

Agents have overhead — they spawn, run, and return. For simple instructions, a skill is faster and simpler.

### 10.6 Monitors Are a Background Intelligence Layer

Most developers think of monitors as log tails. They're actually a general-purpose event stream. Anything you can express as a line of stdout from a shell command can be a monitor:

- Git commit messages as they land on main (`git log --follow -p`)
- External API polling (error rate thresholds, SLA breaches)
- File system changes (`fswatch` on a config directory)
- Database query performance (`tail -f slow-query.log`)

When monitors feed Claude continuously, the session becomes proactive instead of reactive. Claude sees state change and acts — before the developer even notices the problem.

### 10.7 Settings.json Agent Activation for Role-Based Plugins

The most underused feature: setting a default agent via `settings.json`. This lets you build **role-specific plugins** — install the `security-team` plugin and Claude Code becomes a security-focused assistant for that session. Install the `frontend` plugin and Claude becomes a UI/UX-focused pair programmer.

This is a qualitatively different experience from generic Claude Code. It's Claude Code with organizational identity.

### 10.8 Private Marketplace as a Team Distribution Mechanism

Most teams don't realize they can host their own plugin marketplace in a private git repository. The format is simple: a `marketplace.json` file listing plugin names and git URLs. This gives you:

- Centralized plugin management across your org
- Version-pinned, audited plugins for every developer
- The ability to add/remove plugins for your team without touching individual machines
- A review gate before any plugin reaches developers

### 10.9 The `bin/` Directory for Embedded Tooling

Shipping a plugin with a `bin/` directory lets you provide custom CLI tools that Claude can use via Bash — without requiring users to install anything extra. This is how you can embed custom linters, formatters, or analysis tools directly in your plugin.

The tools are scoped to Claude Code's Bash environment only — they don't pollute the user's system PATH.

### 10.10 Building a Plugin That Teaches Itself

The most sophisticated pattern: a plugin skill that reads its own SKILL.md and reference files, evaluates whether they're still accurate given the current codebase, and proposes updates. Combine this with a `PostToolUse` hook that detects when project patterns change (new file structure, new dependencies) and triggers the self-evaluation skill.

The result is a plugin that improves itself over time as your project evolves — a living knowledge base rather than a static one.

---

## Quick Reference

### Plugin File Locations

| File | Purpose |
|---|---|
| `.claude-plugin/plugin.json` | Manifest (name, version, author) |
| `skills/<name>/SKILL.md` | Skill definition |
| `agents/<name>.md` | Agent definition |
| `hooks/hooks.json` | Hook event handlers |
| `.mcp.json` | MCP server configs |
| `.lsp.json` | LSP server configs |
| `monitors/monitors.json` | Background monitors |
| `settings.json` | Default session settings |
| `bin/` | Executables added to Bash PATH |

### Hook Events

| Event | Fires when |
|---|---|
| `PreToolUse` | Before any tool executes |
| `PostToolUse` | After any tool executes |
| `ConfigChange` | Config is mutated |
| `SessionStart` | Session begins |
| `SessionEnd` | Session ends |

### Development Commands

```bash
# Create plugin scaffold
claude plugin init my-plugin

# Load plugin locally
claude --plugin-dir ./my-plugin

# Load from URL
claude --plugin-url https://example.com/my-plugin.zip

# Validate before publish
claude plugin validate

# Reload during dev
/reload-plugins
```

### Security Checklist

- [ ] No hardcoded secrets
- [ ] Hook variables quoted: `"$VAR"` not `$VAR`
- [ ] MCP servers pin dependency versions
- [ ] Agents have explicit tool restrictions
- [ ] `claude plugin validate` passes
- [ ] Tested in container/VM
- [ ] README documents all env var requirements

---

## Sources and Further Reading

- [Official Plugin Creation Guide — code.claude.com](https://code.claude.com/docs/en/plugins)
- [Plugins Reference — code.claude.com](https://code.claude.com/docs/en/plugins-reference)
- [Claude Code Plugins README — GitHub](https://github.com/anthropics/claude-code/blob/main/plugins/README.md)
- [DataCamp: How to Build Claude Code Plugins](https://www.datacamp.com/tutorial/how-to-build-claude-code-plugins)
- [MindStudio: Automate Repetitive Workflows with Skills](https://www.mindstudio.ai/blog/claude-code-skills-automate-workflows)
- [MindStudio: Four-Pattern Framework for Claude Code Skills](https://www.mindstudio.ai/blog/four-pattern-framework-claude-code-skills)
- [Pluto Security: Claude Extension Ecosystem Security Guide](https://pluto.security/blog/claude-extension-ecosystem-security-practitioner-guide/)
- [General Analysis: How to Secure Claude Code](https://generalanalysis.com/guides/how-to-secure-claude-code)
- [Backslash: Claude Code Security Best Practices](https://www.backslash.security/blog/claude-code-security-best-practices)
- [Towards AI: Claude Code Extensions Explained](https://pub.towardsai.net/claude-code-extensions-explained-skills-mcp-hooks-subagents-agent-teams-plugins-9294907e84ff)
- [CodingNomads: Build & Distribute Plugins](https://codingnomads.com/claude-code-building-distributing-plugins)
- [MindStudio: 5 Workflow Patterns Explained](https://www.mindstudio.ai/blog/claude-code-5-workflow-patterns-explained)
- [Penligent: Inside Claude Code Architecture](https://www.penligent.ai/hackinglabs/inside-claude-code-the-architecture-behind-tools-memory-hooks-and-mcp/)
- [alexop.dev: Building My First Claude Code Plugin](https://alexop.dev/posts/building-my-first-claude-code-plugin/)
- [Claude Plugin Hub: Safety & Trust Guide](https://www.claudepluginhub.com/learn/safety)
