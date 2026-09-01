# Backup, recovery & proof

Systems built on the assumption that the bad thing already happened. What
matters then is not that a backup exists, but that it cannot have been
rewritten — and that you can show it.

## [baaackaaab](https://github.com/bmmmm/baaackaaab)

`swift` · macOS CLI and TUI

One-way, ransomware-resistant iCloud backup: Drive and Photos into an
append-only restic store. One-way is the whole design — the machine holding the
source can write new snapshots but cannot delete old ones, so an attacker with
full control of it still cannot reach into yesterday.

## [revertii](https://github.com/bmmmm/revertii)

`shell`

Updates a service with the way back built in: snapshot, arm a dead man's
switch, apply, health-check, and revert automatically if it does not come back.
The switch is armed before the change, not after — an update that hangs is the
case a manual rollback never covers.

## [how-small-can-we-go](https://github.com/bmmmm/how-small-can-we-go)

`go` · [arena](https://bmmmm.github.io/how-small-can-we-go/)

A trust-golf arena: one champion per task, dethroned by needing less trust —
fewer third-party bytes, fewer dangerous constructs. Every entry is measured
against the same surface metric, never self-declared, and the current champion
is whoever survived the last challenge.

## [stattii](https://github.com/bmmmm/stattii)

`go`

An attestation layer over an event calendar. Responsible people confirm or
cancel through tokenised links; a cancellation propagates outward to everyone
downstream, with delivery proof at each hop. Built for the case where "I never
got the message" has consequences.

---

[← back to profile](https://github.com/bmmmm)
