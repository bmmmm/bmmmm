# LLM & agent tooling

Instrumenting, measuring and fact-checking what models actually do. The common thread: a claim is not a result. Every one of these exists because something was asserted — a release note, a cost estimate, a changelog — and nothing was checking it.

Newest first — this page is generated, so the order follows the code.

## [claudii](https://github.com/bmmmm/claudii)

`Shell` · [live](https://bmmmm.github.io/claudii/) · `brew install bmmmm/tap/claudii`

A statusline for Claude Code: session cost, context usage in percent, rate-limit headroom and model health, refreshed in the prompt. Pure bash and jq — no daemon, no background process, nothing that outlives the shell.

<sub>last pushed 2026-10-28</sub>

## [comparereleaseii](https://github.com/bmmmm/comparereleaseii)

`TypeScript` · [live](https://bmmmm.github.io/comparereleaseii/demo/) · [gh extension](https://github.com/bmmmm/gh-comparereleaseii)

Fact-checks release notes against the diff that shipped. Works on GitHub, Forgejo, GitLab or any local git clone. Answers the question you have before an upgrade: does the changelog describe what changed, and what did it leave out?

<sub>last pushed 2026-10-20</sub>

---

[← back to profile](https://github.com/bmmmm)
