# Phase 04 — APIs & Communication Deep Dives

> **Goal:** full treatment of the contracts that ride on top of the wire.
> Phase 03 got bytes to the right machine; this phase is about what those
> bytes *agree to say* once they arrive.

Phase 03 followed a request down to the metal — a name resolved to an address,
a protocol structured the conversation, a transport carried the bytes, and
intermediaries spread them across servers. At the end of all that, two machines
can exchange bytes reliably. **They still have to agree on what the bytes
mean.** That agreement is an **API**, and it is the entire subject of this
phase.

The distinction that matters here is *transport* versus *contract*. Phase 03
answered "how does a message get there?" This phase answers "what is the message
allowed to say, in what shape, with what guarantees — and how does that
agreement survive two teams changing their software independently?" The wire is
neutral; the contract is where design decisions and their consequences live.

Most topics here expand on intuition Phase 01's APIs group already built. Some —
where the foundation series named a concept without teaching it — are written to
**stand alone**, assuming no prior reading and defining their terms from zero.
Those are marked in the table below, and you can start with any of them cold.

**Prerequisites:** [Phase 01 — Foundation](../01-introduction/README.md) for the
API intuition these documents expand, and
[Phase 03 — Networking Deep Dives](../03-networking/README.md) for the wire the
contracts ride on. The reason APIs are hard is that the wire underneath them can
fail — so the two phases are read together.

---

## Reading Order

| # | Topic | The question it answers |
|---|---|---|
| 1 | [What Is an API?](01-what-is-an-api/README.md) | What actually changes when the function you're calling lives on another machine, owned by another team, that can fail or change without warning? *(standalone — assumes no prior reading)* |
| 2 | [Data Formats (JSON, XML, Protobuf)](02-data-formats/README.md) | How does a value cross the gap between two programs — and why is "just use JSON" a decision with consequences? *(standalone — assumes no prior reading)* |
| 3 | [API Architectural Styles](03-api-architectural-styles/README.md) | REST, gRPC, GraphQL, WebSockets, webhooks — what actually distinguishes them, and how would you choose without a favorite? *(standalone — assumes no prior reading)* |
| 4 | [REST API Design](04-rest-api-design/README.md) | REST's rules sound obvious — so why are so many APIs technically RESTful and miserable to use? *(standalone — assumes no prior reading)* |
| 5 | REST vs GraphQL *(coming)* | Over-fetching, under-fetching, and who decides the shape of a response |
| 6 | GraphQL *(coming)* | A query language for APIs — its power, and the cost of that power |
| 7 | WebSockets *(coming)* | When request/response isn't enough and the connection has to stay open |
| 8 | WebSocket Use Cases *(coming)* | Where persistent bidirectional channels earn their keep — and where they don't |
| 9 | Webhooks *(coming)* | Inverting the call so the server tells you, instead of you asking |
| 10 | gRPC *(coming)* | Contract-first, binary, and built for service-to-service speed |
| 11 | API Gateways *(coming)* | The one front door that owns auth, routing, limits, and aggregation |
| 12 | Rate Limiting *(coming)* | Protecting a shared resource from abuse and runaway clients |
| 13 | Idempotency *(coming)* | Making a retried request safe to run more than once |
| 14 | API Versioning *(coming)* | Evolving a contract without breaking the callers you can't control |
| 15 | WebRTC *(idea)* | Peer-to-peer real-time media, and why it barely resembles the rest |

---

## What "Done" Looks Like

You've finished this phase when an API is no longer "the thing you call to get
JSON" but a **contract with obligations** — a shape, a set of guarantees, a
failure model, and an evolution story. When someone says "just add an endpoint,"
you'll know to ask who calls it, what happens when it's retried, and how it
changes without breaking them.

---

Progress and the full curriculum live in [ROADMAP.md](../ROADMAP.md).
When you're through this phase, **Phase 05 — Storage & Databases** is next,
where the state these APIs expose finally has to live somewhere.
