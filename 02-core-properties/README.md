# Phase 02 — Core System Properties

> **Goal:** establish the vocabulary every system design conversation uses.
> These are the properties engineers evaluate every design decision against.
> **No solutions yet — just the language and the intuition.**

Phase 01 gave you the *building blocks* — networking, APIs, storage, scaling,
distributed systems, architecture. This phase gives you the **yardsticks**: the
five properties every design is measured against, argued about, and traded off
along. When engineers debate a design, they are almost always debating one of
these five words — usually without defining it precisely. After this phase,
you will define it precisely.

Solution techniques (caching, replication, redundancy patterns) are deliberately
*not* retaught here — they get full treatment in later phases. This phase is
about being able to say **exactly what you're optimizing for, how it's
measured, and what it costs** — the skill that separates "make it scalable and
reliable" hand-waving from engineering.

**Prerequisite:** [Phase 01 — Foundation](../01-introduction/README.md). These
documents pick up threads planted there and assume its vocabulary.

---

## Reading Order

| # | Topic | The question it answers |
|---|---|---|
| 1 | [Latency vs Throughput](01-latency-vs-throughput/README.md) | How fast is one request — and how much can the system handle? Two different questions with opposite cures |
| 2 | [Availability](02-availability/README.md) | Is the system there at all? The "nines", what counts as down, and what each extra nine costs |
| 3 | [Reliability](03-reliability/README.md) | Does it do the *right thing* over time — and how is that different from merely being up? |
| 4 | [Scalability](04-scalability/README.md) | Does it stay fast and correct as load grows — and where does growth actually hurt? |
| 5 | [Single Point of Failure (SPOF)](05-single-point-of-failure/README.md) | Which single component takes everything down with it — and how do you find it before it finds you? |

---

## What "Done" Looks Like

You've finished this phase when "the system should be fast and reliable" sounds
as vague to you as it actually is — and you instinctively replace it with
numbers: *which percentile, under what load, how many nines, measured how*.
Every later phase spends this vocabulary; this is where you earn it.

---

Progress and the full curriculum live in [ROADMAP.md](../ROADMAP.md).
