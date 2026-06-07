# Claude Code Plugin Field Guide Design

## Goal

Create a single-page educational website that explains every concept in `Claude_Code_Plugin_Guide.md` to developers who are new to Claude Code plugins. The site must remain useful as a reference after the first read, while using animated diagrams to make system behavior easy to understand.

## Audience

The primary reader is a developer who understands basic software development but has not built a Claude Code plugin. Explanations introduce the mental model before terminology, define each component in plain language, and reveal production details after the core concept is clear.

## Visual Thesis

The site is an industrial technical field manual brought to life. Warm paper surfaces, near-black ink, Claude-inspired orange, precise line work, and restrained terminal details make the material feel authoritative without becoming cold. The page uses editorial scale and strong chapter numbering instead of a generic grid of cards.

## Information Architecture

The page follows the ten chapters in the source Markdown:

1. What a Claude Code plugin is
2. Plugin building blocks
3. End-to-end plugin lifecycle
4. Decisions to make before building
5. Reasons to build a plugin
6. How Claude Code interacts with plugins
7. Security design
8. Repetitive workflow design
9. Architecture best practices
10. Advanced insights

A quick-reference section at the end covers file locations, hook events, development commands, the security checklist, and sources.

Each chapter uses a layered teaching pattern:

1. A short beginner-friendly statement explains the concept.
2. A diagram, comparison, or concrete example makes the statement visible.
3. Detailed notes cover the complete source material.
4. Expandable production notes expose advanced detail without interrupting the main reading path.

## Page Composition

### Navigation

A slim fixed header contains the site identity and a chapter menu. A vertical progress rail on larger screens shows the current chapter and enables direct navigation. Mobile uses a compact chapter drawer.

### Hero

The full-viewport opening introduces plugins as capability bundles. A large animated diagram assembles the plugin directory into skills, agents, hooks, MCP, LSP, monitors, settings, and executables, then routes those capabilities into Claude Code.

The hero establishes the central mental model: if Claude Code is the operating system, plugins are installable applications that extend what it can perceive, decide, and do.

### Chapters

Chapters use alternating editorial compositions rather than repeated cards. Diagrams sit beside concise explanations on desktop and become vertical sequences on mobile. Code examples appear only when they clarify a concrete file or behavior.

### Quick Reference

The final section is optimized for scanning. It includes file locations, hook events, development commands, the publishing security checklist, and links to the source material.

## Animated Diagrams

Animations are teaching devices and must remain understandable when motion is disabled.

### Plugin Anatomy Assembly

Directory branches appear one at a time. Each component sends a labeled signal into Claude Code, showing that a plugin is a bundle rather than a single prompt.

### Installation and Activation Lifecycle

A marketplace package moves through manifest registration, component discovery, server startup, monitor startup, and readiness before Claude responds.

### Skill Invocation Paths

Two paths converge on context injection: explicit slash-command invocation and automatic description-based routing.

### Hook Execution Flow

A tool call moves through `PreToolUse`, execution, and `PostToolUse`. A blocked branch shows how a non-zero hook exit prevents the action and returns guidance to Claude.

### Orchestrator Flow

A user message enters the main Claude instance. Animated routes show skill loading, MCP tool calls, agent delegation, and hook interception.

### Repetitive Workflow Transformation

A long manual PR-review workflow compresses into one plugin command. The animation highlights where MCP, an agent, and hooks remove copy-paste and manual checks.

### Security Threat and Defense Map

Threats move toward the plugin boundary. Least privilege, validation, consent, pinning, secret hygiene, and audit logging stop them at distinct layers.

## Content Coverage

All source Markdown points must appear in the site. Dense prose may be rewritten, grouped, or moved into expandable notes, but no concept may be omitted.

Required coverage includes:

- Plugin versus standalone configuration
- Manifest fields and directory placement
- Skills, agents, hooks, MCP servers, LSP servers, monitors, settings, and executables
- Installation, activation, namespacing, invocation, and hot reload
- Plugin planning decisions, dependencies, versioning, and distribution
- Institutional knowledge, standards, repetitive context, personas, integrations, organization scale, and community distribution
- Orchestration, context injection, tool routing, delegation, and the hook feedback loop
- Threat classes, security controls, signing, and the publishing checklist
- Four automation patterns, hook glue, monitors, and skill composition
- Observability, graceful failure, progressive disclosure, idempotency, domain scope, namespaces, versions, test matrix, and documentation
- All ten advanced insights in the source guide

## Interaction Design

- Hero elements enter as a coordinated sequence.
- Diagram steps activate on a timer and pause on hover or keyboard focus.
- Scroll-linked reveals highlight the current part of a flow.
- Building-block controls reveal file locations, responsibilities, and examples.
- Expandable notes use native disclosure controls for accessibility.
- Copy buttons provide feedback for command and code examples.
- The active chapter updates as the reader scrolls.

## Accessibility and Responsive Behavior

- Semantic headings preserve the chapter hierarchy.
- All interactive elements are keyboard accessible.
- Diagrams include visible labels and text descriptions.
- Color never carries meaning alone.
- `prefers-reduced-motion` disables continuous and scroll-linked animation.
- Desktop diagrams collapse into readable vertical flows on narrow screens.
- Contrast meets WCAG AA for body text and controls.

## Technical Architecture

The site uses static HTML, CSS, and JavaScript with no framework or build dependency. This fits the empty repository, keeps deployment simple for GitHub Pages, and makes every visual behavior inspectable.

Files have focused responsibilities:

- `index.html`: semantic content and diagram markup
- `styles.css`: visual system, layout, responsive behavior, and animation
- `script.js`: chapter progress, diagram sequencing, mobile navigation, and copy feedback

## Verification

Verification includes:

- Confirm every Markdown chapter and quick-reference topic is represented.
- Validate HTML structure and check for JavaScript errors.
- Test desktop and mobile layouts in a real browser.
- Confirm navigation, disclosures, copy controls, and diagram animation work.
- Confirm reduced-motion mode leaves every diagram understandable.
- Scan all authored documentation and website copy to ensure it contains no em dashes.
