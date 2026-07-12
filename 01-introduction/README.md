# Phase 01 — Foundation

> **Goal:** build the mental models everything else compounds on.
> Seven documents that take you from *"what even is system design?"* to reading
> real architectures with confidence — intuition first, terminology second.

This phase is the on-ramp for the entire curriculum. Nothing here assumes prior
system design knowledge, and everything later assumes *this*. Distributed
systems, database internals, and architecture tradeoffs all become dramatically
easier once these seven documents feel intuitive.

**Do not skip foundations — and read them in order.** Each group deliberately
builds on the previous one: scaling reuses the networking model, distributed
systems reuse the scaling vocabulary, architecture patterns tie all of it
together. The series is written as one continuous arc, not seven isolated
articles.

---

## Reading Order

| # | Document | What it gives you |
|---|---|---|
| 0 | [What Is System Design?](00-what-is-system-design/README.md) | The mindset: requirements, back-of-envelope estimation, and why every answer is a tradeoff |
| 1 | [Networking Foundations](01-networking-foundations/README.md) | How data actually moves — DNS, TCP, TLS, HTTP — and where a request's time goes |
| 2 | [APIs & Communication](02-apis-and-communication/README.md) | The contracts between systems: REST, GraphQL, gRPC, and real-time communication |
| 3 | [Data Storage](03-data-storage/README.md) | Where state lives: SQL vs NoSQL, indexes, transactions, and why storage choices echo everywhere |
| 4 | [Scaling](04-scaling/README.md) | From one server to many: load balancing, caching, replication, sharding — and bottleneck thinking |
| 5 | [Distributed Systems](05-distributed-systems/README.md) | What breaks when many machines must act as one: partial failure, consistency, consensus |
| 6 | [Architecture Patterns](06-architecture-patterns/README.md) | Shaping whole systems: monoliths, microservices, event-driven — and how real architectures evolve |

---

## What "Done" Looks Like

You've finished this phase when you can look at a familiar product — a chat
app, a shopping site, a feed — and sketch its likely architecture: where
requests flow, where state lives, what's cached, what's async, and where it
breaks first. Not memorized — *reasoned*.

---

Progress and the full 150-topic curriculum live in [ROADMAP.md](../ROADMAP.md).
When you're through this phase, continue to
[Phase 02 — Core System Properties](../02-core-properties/README.md), where the
building blocks get their yardsticks.
