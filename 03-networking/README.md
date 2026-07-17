# Phase 03 — Networking Deep Dives

> **Goal:** full treatment of the wire-level concepts introduced in Phase 01.
> Each topic expands on intuition you already have — **no cold starts**.
> This is where the network stops being an arrow between boxes.

Phase 01 gave you the *building blocks* and Phase 02 gave you the **yardsticks**
to judge them. But every one of those five properties, traced to its root, ran
into the same physical substrate: the **network**. Latency was dominated by
round trips. Availability came down to whether packets reach you. SPOFs hid in
DNS and load balancers. This phase goes underneath all of it.

The distinction that matters here is *intuition* versus *mechanism*. You already
know DNS resolves names and load balancers spread traffic — that's intuition,
and it's enough to sketch an architecture. It is **not** enough to reason about
why a failover took forty minutes, why a health check made an outage worse, or
why a retry storm formed. That takes mechanism, and mechanism is what these
seven documents are for.

**Prerequisites:** [Phase 01 — Foundation](../01-introduction/README.md) for the
wire model these documents expand, and
[Phase 02 — Core System Properties](../02-core-properties/README.md) for the
vocabulary they spend. Unlike earlier phases, this one leans on **both** — the
mechanisms below are only interesting because of the properties they threaten.

---

## Reading Order

| # | Topic | The question it answers |
|---|---|---|
| 1 | [DNS — Domain Name System](01-dns/README.md) | How does a name become an address — and why is the lookup in front of every request also a SPOF, a load balancer, and a latency tax? |
| 2 | HTTP & HTTPS *(coming)* | What the request is actually written in, how the protocol evolved, and what TLS costs you |
| 3 | TCP vs UDP *(coming)* | Reliable-but-slow or fast-but-lossy — what each guarantees, and when the guarantee is the problem |
| 4 | Proxy vs Reverse Proxy *(coming)* | Two things with the same name pointing opposite directions — who they serve and what they hide |
| 5 | Load Balancers *(coming)* | The box everything flows through: how it distributes, how it health-checks, and how it fails |
| 6 | Load Balancing Algorithms *(coming)* | Round-robin, least-connections, hashing — how the choice changes behavior under load |
| 7 | Checksums *(coming)* | How data proves it arrived intact, and what integrity costs |

---

## What "Done" Looks Like

You've finished this phase when a request is no longer a single arrow in your
head but a **sequence of mechanisms with costs** — a resolution you can trace,
a handshake you can price, a connection whose failure modes you can name. When
someone says "just update DNS" or "just add a load balancer," you'll know
exactly which question to ask next.

---

Progress and the full curriculum live in [ROADMAP.md](../ROADMAP.md).
