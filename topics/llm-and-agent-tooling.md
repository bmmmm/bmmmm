# LLM & agent tooling

Instrumenting, measuring and fact-checking what models actually do. The common thread: a claim is not a result. Every one of these exists because something was asserted — a release note, a cost estimate, a changelog — and nothing was checking it.

Newest first — this page is generated, so the order follows the code.

## [wallii](https://github.com/bmmmm/wallii)

`Go`

An append-only message wall for agents: NDJSON feed plus a CLI to post, tail and browse it. Agents report finished work — including the failures — so a long-running fleet leaves a readable trail rather than a scrollback.

<sub>last pushed 2026-09-03</sub>

## [claudii](https://github.com/bmmmm/claudii)

`Shell` · [live](https://bmmmm.github.io/claudii/) · `brew install bmmmm/tap/claudii`

A statusline for Claude Code: session cost, context usage in percent, rate-limit headroom and model health, refreshed in the prompt. Pure bash and jq — no daemon, no background process, nothing that outlives the shell.

<sub>last pushed 2026-09-03</sub>

## [bumpii](https://github.com/bmmmm/bumpii)

`TypeScript`

Reads what changed in the CLI tools and containers you run, keeps only what touches the features you use, and then bumps them. The judgement is the point: most upgrade notes matter to somebody, but not to you.

<sub>last pushed 2026-09-03</sub>

## [check0r3000](https://github.com/bmmmm/check0r3000)

`Python` · [scorecard](https://github.com/bmmmm/check0r3000/blob/main/benchmarks/rechtsschutz/scorecard.md)

Extracts comparable facts out of German insurance terms (AVB), ranks them by quality and tracks prices over time — an entire market in one terminal. Ships with its own benchmark: golden files per line of business, scored on faithfulness, schema validity, hallucinations and coverage, because an extraction pipeline whose accuracy you have not measured is a rumour. Finding so far: what you feed the model matters more than which model — on one contract a local 20B model scored 100 where Opus scored 57, same input.

<sub>last pushed 2026-09-03</sub>

## [comparereleaseii](https://github.com/bmmmm/comparereleaseii)

`TypeScript` · [live](https://bmmmm.github.io/comparereleaseii/demo/) · [gh extension](https://github.com/bmmmm/gh-comparereleaseii)

Fact-checks release notes against the diff that shipped. Works on GitHub, Forgejo, GitLab or any local git clone. Answers the question you have before an upgrade: does the changelog describe what changed, and what did it leave out?

<sub>last pushed 2026-09-03</sub>

## [gateii](https://github.com/bmmmm/gateii)

`Lua`

A minimal self-hosted proxy in front of LLM APIs. One place that sees every request, so latency, spend and failure rates are measurable instead of anecdotal.

<sub>last pushed 2026-09-02</sub>

## [cc-insomnii](https://github.com/bmmmm/cc-insomnii)

`Shell`

A bedtime-shaming statusline for Claude Code. Small, and it works.

<sub>last pushed 2026-09-02</sub>

---

[← back to profile](https://github.com/bmmmm)
