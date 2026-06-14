## LinkedIn

Installing a plugin is one of the most trusting things you do all day, and you probably do it without reading a single line inside.

The moment a plugin is enabled, you have handed it the ability to run skills, spawn agents, fire shell hooks, and start MCP servers, all in your environment, with your credentials in reach. That trust is transitive and usually opaque. This is not hypothetical: real CVEs have already used this surface for remote code execution through malicious hooks and API-key exfiltration through a rogue MCP server.

The discipline that contains it is old and still wins: least privilege, component by component. Declare the exact tools each skill uses. Give agents explicit tool lists. Treat every hook input as hostile, validate first, allowlist what is permitted. Then run the publish checklist before anyone else installs it.

Takeaway: a plugin you did not audit is a plugin you do not trust. Powerful tools deserve careful owners.

Read the full chapter: https://sagart-cactus.github.io/learn-claude-code-plugin/

#ClaudeCode #DevSecOps #SupplyChainSecurity #DevTools #AICoding

## X / Twitter

A plugin you didn't audit is a plugin you can't trust.

One install hands it your shell, your agents, your credentials. Real CVEs already prove it. Least privilege, every component.

https://sagart-cactus.github.io/learn-claude-code-plugin/

#ClaudeCode #DevSecOps
