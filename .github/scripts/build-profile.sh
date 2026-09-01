#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0
# build-profile.sh — render projects.json, the README block and topics/ from
# .github/projects.curated.json plus live GitHub metadata.
#
# The curated file owns membership and prose. Everything that goes stale on its
# own — order, language, live URL, freshness — is read from the API at build
# time, so the profile re-sorts itself instead of being re-edited.
#
# Idempotent: running it twice produces byte-identical output for the same API
# state, which is what lets the workflow commit only on a real change. That is
# also why the feed carries no "generated" timestamp — it would differ on every
# run and turn the daily cron into a daily empty commit. When the feed was
# built is the commit's date.
#
# Usage: .github/scripts/build-profile.sh [owner]   (default: bmmmm)
set -euo pipefail

owner="${1:-bmmmm}"
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
curated="$root/.github/projects.curated.json"
feed="$root/projects.json"
readme="$root/README.md"
topics="$root/topics"

command -v jq >/dev/null || { echo "build-profile: jq is required" >&2; exit 1; }
command -v gh >/dev/null || { echo "build-profile: gh is required" >&2; exit 1; }
[ -r "$curated" ] || { echo "build-profile: missing $curated" >&2; exit 1; }

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

# ── live metadata ───────────────────────────────────────────────────────────
# One paginated call for the whole account rather than one per repo: cheaper,
# and it is also how a repo that was archived or made private disappears from
# the profile without anyone remembering to remove it.
gh api "users/$owner/repos?per_page=100&type=owner" --paginate \
  --jq '.[] | select(.fork == false and .archived == false and .private == false)
        | {key: .name, value: {name: .name, url: .html_url, description: .description,
           language: .language, homepage: .homepage, pushed_at: .pushed_at,
           stars: .stargazers_count, topics: .topics}}' \
  | jq -s 'from_entries' > "$tmp/live.json"

# ── join, filter, sort ──────────────────────────────────────────────────────
# A repo that is public on GitHub has already passed the three fail-closed
# stage gates (pre-push hook, mirror-setup, fleet sync), so its presence here
# IS the >= alpha proof; re-checking .project-stage would cost one API call per
# repo to learn what its visibility already tells us.
#
# The live link is allowlisted by host, never taken from `homepage` as-is: that
# field also holds self-referential github.com links and upstream project
# pages, and an allowlist is the only shape that keeps a private host out by
# construction rather than by remembering to exclude it.
jq -n \
  --slurpfile curated "$curated" \
  --slurpfile live "$tmp/live.json" \
  --arg owner "$owner" \
  '
  ($curated[0]) as $c | ($live[0]) as $l |
  ($c.site_hosts) as $hosts |
  def live_url($hp):
    if ($hp // "") == "" then null
    elif ($hosts | map(. as $h | ($hp | test("^https?://" + ($h | gsub("\\."; "\\.")) + "(/|$)"))) | any)
    then $hp else null end;
  {
    owner: $owner,
    intro: $c.intro,
    sites: $c.sites,
    categories: [
      $c.categories[] | . as $cat | {
        key: $cat.key,
        title: $cat.title,
        tagline: $cat.tagline,
        intro: $cat.intro,
        projects: [
          $cat.projects[] | . as $p | ($l[$p.repo] // empty) | {
            repo: $p.repo,
            name: ($p.name // $p.repo),
            url: .url,
            blurb: $p.blurb,
            detail: $p.detail,
            install: $p.install,
            links: ($p.links // []),
            language: .language,
            stars: .stars,
            # Carried into the feed so the landing page can derive knowsAbout
            # from topics actually set on the repos, never from a list of
            # terms someone wished were true.
            topics: .topics,
            live: live_url(.homepage),
            pushed_at: .pushed_at,
            updated: (.pushed_at | split("T")[0])
          }
        ] | sort_by(.pushed_at) | reverse
      }
    ]
  }' > "$feed"

# A curated repo that did not survive the join was archived, made private or
# renamed. That is a legitimate outcome, but a silent one would let the profile
# quietly shrink, so name the dropped repos on stderr.
dropped="$(jq -r --slurpfile f "$feed" '
  [$f[0].categories[].projects[].repo] as $rendered
  | ([.categories[].projects[].repo] - $rendered) | join(", ")' "$curated")"
if [ -n "$dropped" ]; then
  echo "build-profile: dropped (archived, private or renamed): $dropped" >&2
fi

# ── shared renderers ────────────────────────────────────────────────────────
# Rendered by jq rather than a shell loop so the markdown is a pure function of
# the feed — the same reason the feed exists at all.
render_readme() {
  jq -r '
    def meta($p):
      [ ($p.language // empty | "`" + . + "`"),
        ($p.live // empty | "[live](" + . + ")"),
        ($p.links[]? | "[" + .label + "](" + .url + ")")
      ] | if length == 0 then "" else " · " + join(" · ") end;
    def entry($p):
      "- **[" + $p.name + "](" + $p.url + ")** — " + $p.blurb + meta($p);
    "<!-- projects:start -->", "",
    "## What I build", "",
    .intro, "",
    ( .categories | to_entries[] | .key as $i | .value as $cat |
      ( "<details" + (if $i == 0 then " open" else "" end) + ">" ),
      ( "<summary><strong>" + ($cat.title | gsub("&"; "&amp;")) + "</strong> — "
        + (($cat.tagline[0:1] | ascii_downcase) + $cat.tagline[1:])
        + " · " + ($cat.projects | length | tostring) + " projects</summary>" ),
      "",
      ( $cat.projects[] | entry(.) ),
      "",
      ( "<sub>More on each — <a href=\"https://github.com/bmmmm/bmmmm/blob/main/topics/"
        + $cat.key + ".md\">" + ($cat.title | gsub("&"; "&amp;")) + " in detail →</a></sub>" ),
      "",
      "</details>",
      ""
    ),
    "### Sites", "",
    ( [.sites[] | "[" + .name + "](" + .url + ")" + (if .note then " — " + .note else "" end)] | join(" · ") ), "",
    "<!-- projects:end -->"
  ' "$feed"
}

render_topic() {  # <category-key>
  jq -r --arg key "$1" '
    .categories[] | select(.key == $key) |
    def meta($p):
      [ ($p.language // empty | "`" + . + "`"),
        ($p.live // empty | "[live](" + . + ")"),
        ($p.links[]? | "[" + .label + "](" + .url + ")"),
        ($p.install // empty | "`" + . + "`")
      ] | join(" · ");
    "# " + .title, "",
    .tagline + ". " + .intro, "",
    "Newest first — this page is generated, so the order follows the code.", "",
    ( .projects[] |
      "## [" + .name + "](" + .url + ")", "",
      meta(.), "",
      .detail, "",
      "<sub>last pushed " + .updated + "</sub>", ""
    ),
    "---", "",
    "[← back to profile](https://github.com/bmmmm)"
  ' "$feed"
}

# ── write README block between the markers ──────────────────────────────────
# Only the block is replaced; the terminal art above it and the snake below are
# never touched, which is the whole point of the markers.
grep -q '<!-- projects:start -->' "$readme" || {
  echo "build-profile: no projects:start marker in README.md" >&2; exit 1; }
grep -q '<!-- projects:end -->' "$readme" || {
  echo "build-profile: no projects:end marker in README.md" >&2; exit 1; }

render_readme > "$tmp/block.md"
awk -v block="$tmp/block.md" '
  /<!-- projects:start -->/ { while ((getline line < block) > 0) print line; skip = 1; next }
  /<!-- projects:end -->/   { skip = 0; next }
  !skip
' "$readme" > "$tmp/README.md"
mv "$tmp/README.md" "$readme"

# ── write the topic pages ───────────────────────────────────────────────────
mkdir -p "$topics"
for key in $(jq -r '.categories[].key' "$feed"); do
  render_topic "$key" > "$topics/$key.md"
done

# A category removed from the curated file must lose its page too, otherwise
# the profile stops linking to a file that stays behind and goes stale.
for page in "$topics"/*.md; do
  key="$(basename "$page" .md)"
  jq -e --arg k "$key" '.categories[] | select(.key == $k)' "$feed" >/dev/null \
    || { echo "build-profile: removing orphaned $page" >&2; rm -f "$page"; }
done

echo "build-profile: $(jq -r '[.categories[].projects[]] | length' "$feed") projects in $(jq -r '.categories | length' "$feed") categories"
