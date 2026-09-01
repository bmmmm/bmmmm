# LLM & agent tooling

Instrumenting, measuring and fact-checking what models actually do. The common
thread: a claim is not a result. Every one of these exists because something
was asserted — a release note, a cost estimate, a changelog — and nothing was
checking it.

## [claudii](https://github.com/bmmmm/claudii)

`shell` · [docs](https://bmmmm.github.io/claudii/) · `brew install bmmmm/tap/claudii`

A statusline for Claude Code: session cost, context usage in percent, rate-limit
headroom and model health, refreshed in the prompt. Pure bash and jq — no
daemon, no background process, nothing that outlives the shell.

## [comparereleaseii](https://github.com/bmmmm/comparereleaseii)

`typescript` · [demo](https://bmmmm.github.io/comparereleaseii/demo/) · also a
[gh extension](https://github.com/bmmmm/gh-comparereleaseii)

Fact-checks release notes against the actual code diff. Works on GitHub,
Forgejo, GitLab or any local git clone. Answers the question you actually have
before an upgrade: does the changelog describe what changed, and what did it
leave out?

## [check0r3000](https://github.com/bmmmm/check0r3000)

`python` · Textual TUI

Extracts comparable facts out of German insurance terms (AVB), ranks them by
quality and tracks prices over time — an entire market in one terminal. Ships
with a model benchmark, because an extraction pipeline whose accuracy you have
not measured is a rumour.

## [bumpii](https://github.com/bmmmm/bumpii)

`typescript`

Reads what actually changed in the CLI tools and containers you run, judged
against how you use them, and then bumps them. The judgement is the point: most
upgrade notes matter to somebody, but not to you.

## [gateii](https://github.com/bmmmm/gateii)

`lua` · OpenResty + Prometheus + Grafana

A minimal self-hosted proxy in front of LLM APIs. One place that sees every
request, so latency, spend and failure rates are measurable instead of
anecdotal.

## [wallii](https://github.com/bmmmm/wallii)

`go`

An append-only message wall for agents: NDJSON feed plus a CLI to post, tail
and browse it. Agents report finished work — including the failures — so a
long-running fleet leaves a readable trail rather than a scrollback.

## [cc-insomnii](https://github.com/bmmmm/cc-insomnii)

`shell`

A bedtime-shaming statusline for Claude Code. Small, and it works.

---

[← back to profile](https://github.com/bmmmm)
