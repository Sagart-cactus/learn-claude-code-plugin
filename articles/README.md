# Promo articles

Five standalone, shareable articles drawn from [The Definitive Guide to Claude Code Plugins](../index.html). Each one leads with a hook, stays crisp, and uses animated GIF diagrams to make a concept land. Drop any of them into a blog, a newsletter, or a dev community as-is.

| # | Article | Hook | Header |
|---|---------|------|--------|
| 01 | [Give your AI permanent memory](01-give-your-ai-permanent-memory.md) | You re-explain your stack to your AI every morning | `assets/hdr-capabilities.png` |
| 02 | [Enforce standards with hooks](02-enforce-standards-with-hooks.md) | The style guide nobody reads, the linter someone disabled | `assets/hdr-hooks.png` |
| 03 | [The description is your most important code](03-the-description-is-your-most-important-code.md) | A great tool your AI never reaches for | `assets/hdr-description.png` |
| 04 | [The plugin security model](04-the-plugin-security-model.md) | Installing a plugin is the most trusting thing you do all day | `assets/hdr-security.png` |
| 05 | [Automate repetitive workflows](05-automate-repetitive-workflows.md) | The chore your hands do without you | `assets/hdr-workflow.png` |

## Assets

All header images (`hdr-*.png`, 1200×630, social-share sized) and animated diagrams (`*.gif`) live in [`assets/`](assets/). They are generated from [`scripts/gen_assets.py`](../scripts/gen_assets.py), so the look stays in sync with the website's blueprint-and-clay aesthetic. Regenerate them with:

```bash
python3 -m venv .venv-assets
.venv-assets/bin/pip install Pillow
.venv-assets/bin/python scripts/gen_assets.py
```

| GIF | Shows |
|-----|-------|
| `cap-bloom.gif` | A plugin's six capabilities lighting up around the Claude Code core |
| `activation.gif` | The seven subsystems coming online at load |
| `hook-flow.gif` | A tool call passing through Pre/Post hooks |
| `hook-loop.gif` | The hook → Claude auto-correct feedback loop |
| `routing.gif` | A task routed to the matching skill by its description |
| `gate.gif` | A validation gate passing good input and blocking bad |
| `trust-pyramid.gif` | The components you implicitly trust on install |
| `compress.gif` | 20 minutes of manual work collapsing into one command |
