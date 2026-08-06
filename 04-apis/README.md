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
| 5 | [REST vs GraphQL](05-rest-vs-graphql/README.md) | One tradeoff, not a rivalry — who should decide the shape of a response, and which side should you default to? *(standalone — assumes no prior reading)* |
| 6 | [GraphQL](06-graphql/README.md) | What actually happens when the server turns a query into data — and why every hard part follows from it being a graph? *(standalone — assumes no prior reading)* |
| 7 | [WebSockets](07-websockets/README.md) | The web is request-response, so how does a server *push* — and why is the connection that lets it so much costlier to run than an ordinary API? *(standalone — assumes no prior reading)* |
| 8 | [WebSocket Use Cases](08-websocket-use-cases/README.md) | "Real-time" hides several different patterns — so how do you tell which features genuinely need a WebSocket, which want something lighter, and what will actually be hard? *(builds on Topic 07)* |
| 9 | [Webhooks](09-webhooks/README.md) | When an event happens in a system you don't control, how does it tell you — and why is receiving that call correctly so much harder than sending it? *(standalone — assumes no prior reading)* |
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
