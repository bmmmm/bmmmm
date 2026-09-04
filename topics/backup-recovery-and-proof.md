# Backup, recovery & proof

Systems that assume the failure already happened and stay useful anyway. What matters after the bad thing is not that a backup exists, but that it cannot have been rewritten — and that you can show it.

Newest first — this page is generated, so the order follows the code.

## [stattii](https://github.com/bmmmm/stattii)

`Go`

An attestation layer over an event calendar. Responsible people confirm or cancel through tokenised links; a cancellation propagates outward to everyone downstream, with delivery proof at each hop. Built for the case where "I never got the message" has consequences.

<sub>last pushed 2026-09-03</sub>

## [how-small-can-we-go](https://github.com/bmmmm/how-small-can-we-go)

`Go` · [live](https://bmmmm.github.io/how-small-can-we-go/)

A trust-golf arena: one champion per task, dethroned by needing less trust — fewer third-party bytes, fewer dangerous constructs. Every entry is measured against the same surface metric, never self-declared, and the current champion is whoever survived the last challenge.

<sub>last pushed 2026-09-03</sub>

## [revertii](https://github.com/bmmmm/revertii)

`Shell`

Updates a service with the way back built in: snapshot, arm a dead man's switch, apply, health-check, and revert automatically if it does not come back. The switch is armed before the change, not after — an update that hangs is the case a manual rollback never covers.

<sub>last pushed 2026-09-02</sub>

## [baaackaaab](https://github.com/bmmmm/baaackaaab)

`Swift`

One-way, ransomware-resistant iCloud backup: Drive and Photos into an append-only restic store. One-way is the whole design — the machine holding the source can write new snapshots but cannot delete old ones, so an attacker with full control of it still cannot reach into yesterday.

<sub>last pushed 2026-09-02</sub>

---

[← back to profile](https://github.com/bmmmm)
