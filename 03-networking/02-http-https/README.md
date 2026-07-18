# HTTP & HTTPS

> **Phase:** Networking Deep Dives → **Topic:** 2 of 7 → **Read time:** ~60 minutes

---

## Before You Begin

**This document stands alone.** Unlike its neighbours, it assumes you have read nothing else — not the foundation series, not the phase before it, not the topic before it. Everything about HTTP and HTTPS is built here from zero: the message format, the methods, the status codes, statelessness, caching, all three protocol versions, TLS, and certificates. If you know only that "websites use HTTP" and that the `s` means something about security, you are exactly the reader this was written for.

Two consequences of that choice, stated up front so the shape of the document makes sense:

- **Terms get defined where they're used**, even ones a systems engineer would consider obvious — round trip, latency percentile, single point of failure. Skim past what you already know.
- **Neighbouring topics are named, not taught.** REST API design, idempotency keys, TCP's internals, reverse proxies, load balancers, and CDN strategy each have their own full treatment elsewhere in this curriculum. Where they touch HTTP, this document says so and points; it doesn't absorb them. *HTTP and HTTPS themselves are complete here.*

HTTP also appears as one of the six concepts in the **Top 30 Must-Know Concepts** foundation series, where it gets a short introduction. This is that concept's deep-dive.

Here is the question the document answers:

> **What actually happens between "your browser has an address" and "the page appears" — and why has the industry rewritten that answer three times in thirty years?**

Here's the trap it disarms. HTTP looks like the easy part of the stack. It's human-readable, its errors are famous enough to be jokes, and every engineer has typed a `200` and a `404` into a codebase. That familiarity produces a false model: **HTTP as a format** — a text shape with a verb, a path, and a number in it. If HTTP were a format, there would be nothing to say, and it certainly wouldn't have needed three major revisions.

The truth is that HTTP is where a request's real cost is decided. Not the format — the **conversation**: how many times the client and server must talk before useful data moves, whether a connection is reused or rebuilt, whether one slow response blocks nine fast ones, and what encryption adds to all of it. Two systems can speak identical HTTP and differ by a factor of ten in how long a page takes to appear.

> **The mindset shift:** stop reading HTTP as *a format* and start reading it as *a negotiation with a price*. Every version of HTTP — 1.1, 2, 3 — is an attack on the same enemy: **round trips**, the unavoidable there-and-back delay of talking to a machine far away. And every guarantee you add on top — encryption, identity, integrity — is paid for in that same currency, *before* your server does a single useful thing. Learn to count the round trips and you can predict a system's speed without measuring it.

---

## Table of Contents

1. [What HTTP Actually Is](#1-what-http-actually-is)
2. [Statelessness — and How the Web Fakes State](#2-statelessness--and-how-the-web-fakes-state)
3. [HTTP Caching](#3-http-caching)
4. [The Connection Underneath](#4-the-connection-underneath)
5. [HTTP/1.1 and Head-of-Line Blocking](#5-http11-and-head-of-line-blocking)
6. [HTTP/2 — Multiplexing, and the Blocking It Didn't Fix](#6-http2--multiplexing-and-the-blocking-it-didnt-fix)
7. [HTTP/3 and QUIC — Abandoning TCP](#7-http3-and-quic--abandoning-tcp)
8. [HTTPS — What TLS Guarantees, and What It Costs](#8-https--what-tls-guarantees-and-what-it-costs)
9. [Certificates — Chain of Trust and the Expiry Trap](#9-certificates--chain-of-trust-and-the-expiry-trap)
10. [Putting It All Together — A Commerce Team Goes HTTPS-Only](#10-putting-it-all-together--a-commerce-team-goes-https-only)
11. [Final Recap](#11-final-recap)

---

## 1. What HTTP Actually Is

**HTTP** — HyperText Transfer Protocol — is an agreement about the shape of messages. That's genuinely all it is at the base layer: two parties agree that a request looks *like this* and a response looks *like that*, and because everyone agreed, a browser written by one company can talk to a server written by another in a language neither knew about the other.

The agreement has one governing property, and it shapes everything downstream: **the client always speaks first.** A server never initiates. It waits, receives a request, answers, and goes back to waiting. This request–response cycle is the atom of the web, and its one-directionality is why "push" features — live notifications, chat, streaming updates — need either separate protocols or clever workarounds. HTTP has no vocabulary for "the server has something to say."

### A Request Is Four Parts

A raw HTTP request is text. You could type one by hand:

```
POST /orders HTTP/1.1
Host: shop.example.com
Content-Type: application/json
Authorization: Bearer abc123

{"item": "keyboard", "qty": 1}
```

Four components, in order:

| Part | This example | What it carries |
|---|---|---|
| **Method** | `POST` | The verb — what you want done |
| **Path** | `/orders` | Which resource you want it done to |
| **Headers** | `Host`, `Content-Type`, … | Metadata — auth, formats, caching, everything about the request that isn't the request |
| **Body** | `{"item": …}` | The payload. Optional — `GET` requests normally have none |

The blank line between headers and body is structural, not cosmetic: it's how the receiver knows the headers ended. That detail sounds trivial and becomes important in §5, when we look at what it costs to parse a protocol made of text.

### A Response Is Three Parts

```
HTTP/1.1 200 OK
Content-Type: application/json
Cache-Control: max-age=3600

{"orderId": 1042, "status": "confirmed"}
```

A **status code** and its reason phrase, then **headers**, then a **body**. Same blank-line rule.

### The Methods

Methods tell the server what kind of operation you intend. There are more, but these five carry almost all real traffic:

| Method | Intent | Has a body? |
|---|---|---|
| `GET` | Read a resource. Should never change anything | No |
| `POST` | Create something, or submit data for processing | Yes |
| `PUT` | Replace a resource entirely | Yes |
| `PATCH` | Modify part of a resource | Yes |
| `DELETE` | Remove a resource | Usually not |

Two properties of these methods matter enough to name now, because caching (§3) depends on them:

- **Safe** — the method doesn't change server state. `GET` is safe; it only reads. This is precisely why `GET` responses can be cached and `POST` responses generally cannot: you can reuse a stored answer to "what is it?" but never to "make one."
- **Idempotent** — doing it twice has the same effect as doing it once. `GET`, `PUT`, and `DELETE` are idempotent. **`POST` is not** — send it twice and you may create two orders. That asymmetry is why retrying a failed request is dangerous in a way most people discover the hard way.

How to *design* around that — resource naming, API conventions, idempotency keys that make retries safe — belongs to REST API design and is covered fully in Phase 04. Here we only need the property itself, because the protocol's own caching rules are built on it.

### Status Codes Are Five Conversations

The number's first digit is the real information; the rest is detail:

| Class | Means | Common members |
|---|---|---|
| **1xx** | Informational — hold on, still going | `101 Switching Protocols` |
| **2xx** | It worked | `200 OK`, `201 Created`, `204 No Content` |
| **3xx** | Look elsewhere | `301 Moved Permanently`, `304 Not Modified` |
| **4xx** | **You** made a mistake | `400`, `401 Unauthorized`, `403 Forbidden`, `404 Not Found`, `429 Too Many Requests` |
| **5xx** | **I** made a mistake | `500 Internal Server Error`, `502 Bad Gateway`, `503 Service Unavailable` |

The 4xx/5xx split is the one to internalise, because it assigns blame and therefore assigns the person who should be paged. A `404` means the client asked for something that isn't there — nothing is broken. A `500` means the server failed at something it should have handled. Monitoring that treats them alike will either wake you for typos or stay silent through outages.

Two members are worth flagging early. **`304 Not Modified`** is the backbone of §3's caching — a response whose entire purpose is to have no body. And **`429 Too Many Requests`** is the server telling you to slow down, which matters in §4 when we discuss connection reuse.

```mermaid
flowchart LR
    C["👤 Client<br/>always speaks first"] -->|"method + path<br/>+ headers + body"| S["🖥️ Server<br/>never initiates"]
    S -->|"status + headers<br/>+ body"| C
    C -.->|"connection closes,<br/>server forgets everything (§2)"| C
```

> 💡 **Key Insight**
>
> HTTP is a **strict turn-taking conversation the client always starts** — and that single constraint explains far more than it looks like it should. It's why real-time features need workarounds (the server can't speak first). It's why `GET` can be cached and `POST` can't (safety). It's why retries are dangerous (`POST` isn't idempotent). The format is trivia you can look up; the *shape of the conversation* is the part that determines what you can build.

### Quick Recap — What HTTP Actually Is

- HTTP is an agreed **message shape**: request = method + path + headers + body; response = status + headers + body.
- The **client always speaks first** and the server never initiates — which is why server-push features need separate mechanisms.
- Methods carry two properties that the rest of the protocol builds on: **safe** (`GET` changes nothing → cacheable) and **idempotent** (repeatable safely — `POST` is neither).
- Status codes matter mostly by **first digit**, and the `4xx`/`5xx` split assigns blame: client error versus server failure.

---

## 2. Statelessness — and How the Web Fakes State

Here is the most consequential design decision in HTTP, and it sounds at first like a limitation:

> **HTTP is stateless. The server remembers nothing between requests. Every request arrives as if it were the first one that client has ever sent.**

Log in, then request your profile: as far as the protocol is concerned, those are two unrelated events from two strangers. The server has no memory that the first one happened.

That seems obviously bad. It's the reason the web scales.

### Why Amnesia Is a Feature

Imagine the alternative. If a server remembered who you were, then *that specific server* would have to handle all your subsequent requests — your session lives in its memory and nowhere else. Which means:

- You cannot freely add servers, because a new one knows nothing about existing users.
- You cannot remove one, because its memory dies with it and its users are logged out.
- A crash doesn't degrade the system, it *evicts* everyone it was serving.
- Traffic can't be spread evenly, because each request must return to its own server.

Statelessness deletes all four problems at once. If every request carries everything needed to process it, then **any server can handle any request**, and servers become interchangeable — add them, kill them, replace them, and no user notices:

```mermaid
flowchart TD
    subgraph Stateful["🔴 If HTTP remembered you"]
        U1["👤 User A"] -->|"must always return<br/>to the same box"| S1["Server 1<br/>holds A's session"]
        U1 -.->|"❌ can't be served by"| S2["Server 2<br/>knows nothing"]
    end
    subgraph Stateless["🟢 Stateless HTTP"]
        U2["👤 User A"] --> Any{"any server<br/>will do"}
        Any --> T1["Server 1"]
        Any --> T2["Server 2"]
        Any --> T3["Server 3"]
    end
```

This is the foundation the entire scaling toolkit is built on — putting many identical servers behind a distributor that sprays requests across them. That machinery (load balancers, the algorithms they use, health checking) is Topics 05 and 06 of this phase. The point here is that **it's only possible because HTTP forgets.**

### But Applications Need Memory

A shopping cart that empties between clicks is useless. So the web needs state on top of a protocol that refuses to keep it — and the resolution is elegant: **the server stays stateless by making the client carry the state, and present it every time.**

Three mechanisms, in increasing order of how much they let you forget.

### Cookies — The Original Trick

A **cookie** is a small piece of data the server asks the browser to store and send back on every subsequent request. The server sets it:

```
HTTP/1.1 200 OK
Set-Cookie: session=a1b2c3; HttpOnly; Secure; SameSite=Lax; Max-Age=3600
```

and the browser then attaches it automatically to every request to that site:

```
GET /profile HTTP/1.1
Cookie: session=a1b2c3
```

The protocol is still stateless — the server *is* being told who you are on every single request. It just isn't the server doing the remembering.

Those flags after the value are not decoration; they're the difference between a session mechanism and a vulnerability:

| Flag | Effect | Why it matters |
|---|---|---|
| `HttpOnly` | JavaScript can't read the cookie | A script injected into your page can't steal the session |
| `Secure` | Only sent over HTTPS | Prevents the cookie crossing the network in the clear (§8) |
| `SameSite` | Restricts sending on cross-site requests | Blocks a hostile site from riding your logged-in session |
| `Max-Age` / `Expires` | Lifetime | An eternal session cookie is an eternal stolen session |

> ⚠️ **A session cookie is a bearer token: whoever holds it *is* you.** The server doesn't verify a person, it verifies a string. This is why the flags above are mandatory rather than advisable, and why cookies must never travel unencrypted — anyone who reads one in transit gains the account without ever knowing the password. §8 is the reason HTTPS is not optional.

### Sessions — Cookie as Claim Ticket

The cookie above holds an opaque ID, not your data. The actual session — who you are, what's in your cart — lives server-side in a shared store, and the cookie is the claim ticket that retrieves it.

This keeps the *application servers* stateless while the state moves to a database or cache that all of them share. Note what happened, though: the state didn't disappear, it **relocated**. Every request now costs a lookup in that shared store, and the store is a dependency every server needs. That trade — stateless servers, stateful store — is the standard architecture for good reason, but it isn't free.

### Tokens — Carrying the Claim Itself

The third approach removes the lookup. Instead of an ID pointing at server-side data, the client carries a **token** containing the data itself, cryptographically signed so the server can verify it wasn't tampered with:

```
GET /profile HTTP/1.1
Authorization: Bearer eyJhbGciOiJIUzI1NiJ9...
```

The server validates the signature and trusts the contents. No lookup, no shared store — genuinely stateless.

The catch is the mirror image of the benefit: **you can't un-issue it.** A session ID is revoked by deleting one row. A signed token is valid until it expires, because validity is a mathematical property of the token, not a fact in your database. Log someone out, ban an account, revoke a compromised credential — the token keeps working. The usual mitigations (short lifetimes, refresh tokens, a revocation list) all amount to reintroducing some state, which is to say: paying back part of what you saved.

| | **Session (ID + store)** | **Token (signed, self-contained)** |
|---|---|---|
| Server lookup per request | Yes | No |
| Shared store needed | Yes | No |
| Revoke instantly | ✅ Delete the record | ❌ Valid until expiry |
| Scales across services | Needs shared access | Any service with the key |
| Size on the wire | Tiny | Larger, on every request |

> 💡 **Key Insight**
>
> HTTP's amnesia is not a gap that cookies patch — it's the **property that makes horizontal scaling possible**, and every "stateful" web feature is an illusion built by making the client re-present its identity on every single request. So state never vanishes; it *moves*. Into a cookie, into a shared session store, into a signed token — each choice trading lookup cost against revocation power. When someone says a service is "stateless," the honest question is **"where did you put the state, and what did that cost you?"**

### Quick Recap — Statelessness

- HTTP servers **remember nothing between requests** — every request must carry everything needed to process it.
- That amnesia is what makes servers **interchangeable**, which is the precondition for scaling horizontally and surviving individual failures.
- Applications fake memory by making the **client** re-present state each time: **cookies** (browser-stored, auto-sent, and security-critical via `HttpOnly`/`Secure`/`SameSite`), **sessions** (cookie as claim ticket to a shared store), **tokens** (signed, self-contained, no lookup).
- State is never eliminated, only **relocated** — sessions cost a lookup and gain instant revocation; tokens skip the lookup and **cannot be revoked** before expiry.

---

## 3. HTTP Caching

Caching is the highest-leverage feature in HTTP, and the one most likely to be misconfigured in a codebase you inherit. The premise is simple arithmetic:

> **The fastest request is the one that never happens. The second fastest is the one that returns without a body.**

HTTP gives you both, through headers, with no application code involved. Get this right and a repeat visit costs nearly nothing; get it wrong and you either serve stale content for a year or throw away every optimisation the protocol offers.

### Two Different Mechanisms

People say "caching" for two distinct things, and conflating them is the source of most confusion:

| | **Freshness** | **Validation** |
|---|---|---|
| Question | "Can I skip asking entirely?" | "Has it changed since I last asked?" |
| Network cost | **Zero** — nothing is sent | One round trip, tiny response |
| Governed by | `Cache-Control: max-age` | `ETag` / `Last-Modified` |
| Result | Serve from local copy | `304 Not Modified`, or a fresh body |

Freshness is the big win — the request doesn't happen at all. Validation is the fallback: you must ask, but if nothing changed the server replies with an empty `304` instead of resending a megabyte.

```mermaid
flowchart TD
    Need["👤 Browser needs a resource"] --> Have{"Cached copy?"}
    Have -->|no| Fetch["🌐 Full request<br/>full response"]
    Have -->|yes| Fresh{"Still fresh?<br/>(max-age not expired)"}
    Fresh -->|"🟢 yes"| Local["⚡ Use local copy<br/>ZERO network"]
    Fresh -->|"no — but we have an ETag"| Ask["🌐 Conditional request<br/>If-None-Match: abc123"]
    Ask --> Changed{"Changed?"}
    Changed -->|"no"| NM["✅ 304 Not Modified<br/>no body — cheap"]
    Changed -->|"yes"| Full["📦 200 + new body"]
```

### `Cache-Control` — The Header That Decides

Nearly all caching behaviour is one header. The directives that carry real weight:

| Directive | Meaning |
|---|---|
| `max-age=N` | Fresh for N seconds. During that window, **no request is made at all** |
| `no-cache` | Store it, but **always revalidate** before use. Misleadingly named — it does *not* mean "don't cache" |
| `no-store` | Genuinely don't store it anywhere. For sensitive data |
| `private` | Only the user's browser may cache it — not shared caches in between |
| `public` | Shared caches may store it too |
| `immutable` | This will never change; don't even revalidate on reload |

The `no-cache` / `no-store` naming trap is worth stopping on, because the two are routinely swapped in real codebases. **`no-cache` means "cache it, but check with me first."** **`no-store` means "never write this down."** Using `no-cache` for a bank statement stores it on disk; using `no-store` for your CSS throws away every performance gain on the site. The names are backwards from intuition and have been for decades.

### `ETag` — Fingerprinting a Response

An **`ETag`** is an opaque identifier the server attaches to a response — usually a hash of the content:

```
HTTP/1.1 200 OK
ETag: "a1b2c3"
Cache-Control: max-age=60
```

When freshness expires, the browser doesn't ask for the resource. It asks *whether it changed*:

```
GET /style.css HTTP/1.1
If-None-Match: "a1b2c3"
```

If the content still hashes to `a1b2c3`, the server sends back a bodiless `304 Not Modified` — a response measured in bytes instead of kilobytes. If it changed, you get a normal `200` with the new content and a new `ETag`.

`Last-Modified` / `If-Modified-Since` does the same dance with timestamps instead of hashes. It's weaker — one-second resolution, and it can't tell "edited then reverted" from "never touched" — but it's cheaper for the server to produce.

### The Versioned-URL Pattern

The strongest caching strategy sidesteps the freshness/staleness dilemma entirely, and you have seen its fingerprints without necessarily noticing: filenames like `app.7f3a9c.js`.

The trick is to make the URL change whenever the content changes. Then the content at any given URL is *immutable by construction*, so it can be cached essentially forever:

```
Cache-Control: max-age=31536000, immutable
```

A year. No revalidation, ever. And deploying a new version doesn't require expiring anything — it produces a *different URL*, which simply isn't in anyone's cache. The HTML that references those files stays uncached or short-cached, so it always points at current filenames.

This inverts the usual problem. Instead of asking "how do I invalidate a cache I don't control?", you arrange never to need to. Anything with a content-hashed name gets a year; anything without gets seconds.

### Where Caches Live

Your response may be stored in several places, and `private` versus `public` decides which:

- **Browser cache** — per user, on their disk.
- **Shared/proxy caches** — corporate proxies, ISP caches, anything between.
- **CDN edge caches** — geographically distributed copies. Strategy for these is Phase 06; the *headers* controlling them are the ones above.

The `private` directive exists precisely because of the middle two. Mark a personalised page `public` and a shared cache may hand one user's page to another — a real and recurring class of data-leak incident, caused by a single wrong word in a header.

> 💡 **Key Insight**
>
> Caching has two gears and they aren't interchangeable: **freshness** (`max-age`) eliminates the request; **validation** (`ETag` → `304`) eliminates the *body* when the request must happen. Reach for freshness first — a round trip you never make cannot be slow. And note that the highest-performing setup isn't clever expiry tuning, it's **making content immutable by versioning its URL**, so the invalidation problem stops existing. The one thing to never guess at is `no-cache` versus `no-store`: one caches and revalidates, the other refuses to write to disk, and swapping them either leaks sensitive data or destroys your performance.

### Quick Recap — HTTP Caching

- Two mechanisms: **freshness** (`Cache-Control: max-age` — no request at all) and **validation** (`ETag` + `If-None-Match` → a bodiless `304`).
- **`no-cache` means "revalidate every time," not "don't cache."** `no-store` is the one that refuses to write anything down.
- **Versioned URLs** (`app.7f3a9c.js` + `max-age=31536000, immutable`) make content immutable by construction, so invalidation never has to happen.
- `private` vs `public` controls which caches may store a response — getting it wrong on a personalised page can serve one user's data to another.

---

## 4. The Connection Underneath

Everything so far treated an HTTP request as if it simply *arrives*. It doesn't. HTTP is carried by a lower-level protocol that must establish a connection first, and that establishment has a price. Sections 5 through 8 are all, in one way or another, arguments about that price — so we need to name it precisely.

### The Round Trip — The Unit of Everything

> **A round trip is one message travelling from client to server plus the reply coming back. The time it takes is the round-trip time — RTT.**

RTT is set by physics and geography, not by your server's speed. Light in fibre covers roughly 200,000 km per second, and real paths are indirect, so:

| Path | Typical RTT |
|---|---|
| Same data centre | < 1 ms |
| Same city | ~5 ms |
| Across a continent | ~40–70 ms |
| Across an ocean | ~120–200 ms |
| Satellite / poor mobile | 300–600 ms+ |

Here is why this dominates the rest of the document. **You cannot optimise RTT.** You can't make a server faster than the speed of light, you can't out-engineer the Atlantic. A user in Sydney talking to a server in London pays ~250 ms per round trip no matter how good your code is.

So the only lever is **how many round trips you need**. A page requiring 6 sequential round trips at 100 ms RTT costs 600 ms before the server has done any work at all. Cut it to 2 and you've saved 400 ms without touching a line of application logic. This is the whole game, and every HTTP version is a move in it.

A related idea you'll meet in performance discussions: measure this at the **tail**, not the average. The p99 — the value 99% of requests come in under, meaning the worst 1% — is where connection setup costs concentrate, because that 1% is disproportionately first-time visitors and people on slow mobile networks who pay full setup price. An average hides them; they're the ones forming a first impression.

### Connections Cost Round Trips to Open

Before HTTP says a word, a **TCP** connection is established via a three-way handshake — a "hello," an acknowledgment, and a confirmation:

```mermaid
sequenceDiagram
    participant C as 👤 Client
    participant S as 🖥️ Server
    Note over C,S: TCP handshake — 1 RTT, before any HTTP
    C->>S: SYN
    S->>C: SYN-ACK
    C->>S: ACK
    Note over C,S: NOW HTTP may speak
    C->>S: GET /index.html
    S->>C: 200 OK
```

That's **1 RTT spent before your request exists**. Add encryption and it gets worse — TLS needs its own handshake on top, which §8 counts precisely.

TCP's own mechanics — how it guarantees delivery, retransmits losses, and controls congestion — are Topic 03 of this phase. What matters here is only the bill: **a connection is not free, and it is priced in round trips.**

### Keep-Alive — Stop Rebuilding What You Just Built

The obvious response is to reuse the connection. **Persistent connections** (`keep-alive`) do exactly that: after a response, the connection stays open for the next request instead of closing.

Consider ten resources — an HTML page, some CSS, images:

| | Without keep-alive | With keep-alive |
|---|---|---|
| TCP handshakes | 10 | **1** |
| Round trips on setup | 10 RTT | **1 RTT** |
| At 100 ms RTT | 1000 ms wasted | **100 ms** |

Ninety percent of setup cost, deleted by reusing a connection. This became the default in HTTP/1.1 and it's the single biggest performance difference between it and its predecessor — which closed the connection after every single response.

### Connection Pooling — The Server-Side Mirror

The same logic applies inside your infrastructure. When your application server talks to a database or another service, opening a fresh connection per request pays the same handshake tax, plus authentication.

A **connection pool** keeps a set of established connections open and lends them out. A request borrows one, uses it, returns it. The handshake happens once at startup rather than thousands of times per second.

Pools have their own failure mode worth knowing: **pool exhaustion.** If every connection is checked out and none is returned — typically because something downstream got slow — new requests queue waiting for one. The symptom is a service that appears to hang under load while its CPU sits idle, and the cause is almost never where people look first. It's usually a slow dependency propagating backwards, which is why "the database got slow" and "the API stopped responding" are so often the same incident.

> 💡 **Key Insight**
>
> **Round trips are the currency of web performance, and you can't devalue them** — RTT is physics. That reframes optimisation entirely: stop asking "how do I make this faster?" and start asking **"how many times must these two machines talk before the user sees anything?"** Reusing connections is the highest-return answer, because a connection you don't open is a full round trip you don't pay. Every remaining section of this document is a different attempt to reduce that count.

### Quick Recap — The Connection Underneath

- A **round trip** is one message out and its reply back; **RTT** is set by distance and physics — typically 40–70 ms cross-continent, 120–200 ms cross-ocean — and **cannot be optimised**.
- The only available lever is the **number** of round trips, which is why a page needing 6 sequential trips is slow before the server does anything.
- Opening a **TCP connection costs 1 RTT** before HTTP speaks at all; encryption adds more (§8).
- **Keep-alive** and **connection pools** amortise that cost by reusing established connections — and pool exhaustion is why a service can hang while looking completely idle.

---

## 5. HTTP/1.1 and Head-of-Line Blocking

HTTP/1.1 arrived in 1997, when a web page was a document with a few images. It is still, decades later, spoken by an enormous amount of the internet. It also contains a flaw so structural that fixing it required two more protocol versions — and the workarounds engineers invented to live with it defined front-end practice for fifteen years.

### One Connection, One Request at a Time

Keep-alive (§4) let a connection be *reused*. It did not let it be *shared*. On an HTTP/1.1 connection, requests are strictly serial: send a request, wait for the entire response, then send the next.

The reason is the format itself. HTTP/1.1 messages are plain text with no request identifiers — responses have no way to say which request they belong to. So the only way to know is ordering: the first response answers the first request. Break the ordering and the conversation is gibberish.

That constraint has a name:

> **Head-of-line blocking: the request at the front of the queue blocks every request behind it, no matter how fast those would have been.**

```mermaid
flowchart TD
    subgraph Conn["🔴 One HTTP/1.1 connection"]
        R1["1️⃣ GET /slow-api.json<br/>⏳ takes 2000ms"]
        R2["2️⃣ GET /logo.png<br/>would take 5ms — ⛔ waiting"]
        R3["3️⃣ GET /style.css<br/>would take 3ms — ⛔ waiting"]
        R1 --> R2 --> R3
    end
```

Two fast requests sit idle behind one slow one. Nothing is overloaded — the server is fine, the network is fine, the small files are ready. They simply aren't allowed to go first. **A single slow endpoint degrades everything queued behind it**, which is why one unoptimised API call can make an entire page feel broken.

There was an attempted fix in the spec — **pipelining**, sending multiple requests without waiting — but responses still had to come back in order, so a slow first response blocked the rest anyway. It moved the queue without removing the blocking, broke on intermediary proxies, and was disabled by default nearly everywhere. It's a useful reminder that the blocking is caused by the *ordering requirement*, not by the waiting.

### Six Connections, and the Hacks That Followed

Browsers worked around this by opening **~6 parallel connections per domain**. Six lanes instead of one — genuinely helpful, and still not enough for a page with 80 resources. Each connection also costs its own handshake (§4), and they compete for the same bandwidth.

So the workaround got a workaround. Since the limit is *per domain*, serve assets from several domains and multiply your lanes:

```
static1.example.com   →  6 connections
static2.example.com   →  6 connections
static3.example.com   →  6 connections
```

This is **domain sharding**, and for years it was standard practice. Alongside it came a family of techniques that were all, at heart, the same idea — *make fewer requests, because requests are expensive*:

| Hack | What it did | What it cost |
|---|---|---|
| **Domain sharding** | More parallel connections | Extra DNS lookups, extra handshakes, split caching |
| **Sprite sheets** | Many icons combined into one image | Change one icon, re-download all of them |
| **Concatenation** | All JS into one bundle | Change one line, invalidate the whole bundle |
| **Inlining** | Assets embedded in the HTML | Uncacheable — re-sent on every page load |

Every one of these trades cache efficiency and maintainability for fewer round trips. That was the correct trade under HTTP/1.1, and it stopped being correct the moment HTTP/2 shipped — which is why some of this advice is still repeated today by people who learned it when it was true.

> ⚠️ **These workarounds became actively harmful after HTTP/2.** Domain sharding on HTTP/2 forces multiple connections where one would do, discarding the multiplexing that made sharding unnecessary (§6). Bundling everything into one file means a one-line change invalidates a megabyte of cache (§3). If you inherit a codebase with heavy sharding and aggressive concatenation, you're likely looking at 2010-era optimisations that are now costing what they once saved.

> 💡 **Key Insight**
>
> HTTP/1.1's flaw isn't slowness — it's **seriality**. Because plain-text responses can't identify which request they answer, order becomes the only bookkeeping available, and order means one slow response stalls everything behind it. Notice the shape of this: an apparently minor *format* decision (no request IDs) produced a *performance* ceiling that shaped fifteen years of web engineering practice. Protocol design has consequences that look nothing like protocol design.

### Quick Recap — HTTP/1.1 and Head-of-Line Blocking

- HTTP/1.1 sends **one request at a time per connection**, because plain-text responses carry no ID and must be matched by **order**.
- **Head-of-line blocking**: one slow response stalls every fast request queued behind it — nothing is overloaded, they're just not allowed to pass.
- Browsers opened **~6 connections per domain**, and engineers piled on workarounds — **domain sharding, sprites, concatenation, inlining** — all trading cache efficiency for fewer requests.
- Those workarounds became **counterproductive** under HTTP/2, so they persist in old codebases as optimisations that now cost more than they save.

---

## 6. HTTP/2 — Multiplexing, and the Blocking It Didn't Fix

HTTP/2 (2015) attacked §5's problem at its root. If responses can't be reordered because they carry no identity, then **give them identity** — and the ordering requirement disappears.

### Binary Framing — The Enabling Change

HTTP/2 stopped being a text protocol. Messages are split into **frames**: small binary units, each tagged with a **stream ID** saying which request/response it belongs to.

That one change unlocks everything else. Frames from different streams can be interleaved on a single connection in any order, and the receiver reassembles them by ID. No ordering requirement, no blocking:

```mermaid
flowchart LR
    subgraph One["🟢 ONE HTTP/2 connection"]
        direction TB
        S1["Stream 1 — /slow-api.json ⏳"]
        S3["Stream 3 — /logo.png ✅ done"]
        S5["Stream 5 — /style.css ✅ done"]
    end
    Note["Frames interleave freely.<br/>Fast streams finish first —<br/>they no longer wait in line."]
    One --> Note
```

The slow API call from §5 no longer blocks anything. Its frames trickle in while the small files complete and render. Same connection, same server, dramatically different experience.

Note the trade: HTTP/2 is no longer human-readable. You can't type it by hand or read it off the wire without tooling. The protocol became less transparent in exchange for becoming faster — a bargain the industry accepted, and the reason your debugging tools now do work that used to be unnecessary.

### Header Compression

A second win, less glamorous but substantial. HTTP headers are verbose and highly repetitive — the same `User-Agent`, `Accept`, and `Cookie` values re-sent in full on every request. On a page with 100 requests, that's the same few hundred bytes repeated 100 times.

**HPACK** compresses them and, more importantly, maintains a shared table of headers already sent, so repeats become small references instead of full text. On header-heavy traffic — anything with large cookies — this alone is a serious reduction.

### Server Push — The Feature That Failed

HTTP/2 also let servers send resources the client hadn't yet asked for: you request `index.html`, and the server pushes the CSS it knows you'll need, saving a round trip.

It sounded excellent and worked badly. Servers routinely pushed resources the browser **already had cached**, wasting bandwidth to deliver duplicates. The server can't see the client's cache, so it's guessing — and guessing wrong is worse than not guessing. Browsers eventually removed support. It's a genuinely instructive failure: *an optimisation that requires knowing something you cannot know will lose more often than it wins.*

### The Blocking That Survived

Here's the part usually left out, and it's the reason there is an HTTP/3.

HTTP/2 eliminated head-of-line blocking **at the HTTP layer**. It could do nothing about the layer underneath — because TCP has the same problem, for the same reason.

TCP guarantees ordered delivery. If packet #5 is lost, TCP holds packets #6, #7, #8 in a buffer — it has them, they arrived safely — and refuses to hand them to the application until #5 is retransmitted and arrives. That's TCP doing its job correctly.

But now all your streams share one TCP connection:

```mermaid
flowchart TD
    Loss["📦❌ One TCP packet lost"] --> TCP["TCP: must deliver in order<br/>→ holds ALL later packets"]
    TCP --> Block["⛔ EVERY stream stalls —<br/>even streams whose data<br/>already arrived intact"]
    Block --> Irony["😖 HTTP/2 fixed HTTP's blocking.<br/>TCP's blocking remained —<br/>and hits all streams at once."]
```

The irony is sharp. Under HTTP/1.1's six connections, one lost packet stalled *one* connection and the other five carried on. Under HTTP/2's single connection, one lost packet stalls **every stream on it**. On a clean network HTTP/2 is clearly faster; on a lossy one — patchy mobile, congested public Wi-Fi — it can be *worse* than what it replaced.

That's the trap: HTTP/2 solved head-of-line blocking one layer up, and by consolidating onto a single connection it made the remaining layer's version of the problem hit harder.

> 💡 **Key Insight**
>
> HTTP/2's real innovation is **identity**: binary frames tagged with stream IDs, so responses no longer need to arrive in order. Everything else follows from that. But it fixed blocking only at *its own* layer — TCP's in-order delivery guarantee reproduces the identical problem underneath, and consolidating to one connection means a single lost packet now stalls every stream instead of one-sixth of them. **You cannot fix head-of-line blocking at layer 7 while layer 4 still enforces ordering.** That realisation is what makes §7 necessary.

### Quick Recap — HTTP/2

- HTTP/2 replaced text with **binary frames carrying stream IDs**, giving responses identity so they no longer need to arrive in order.
- **Multiplexing** lets many requests share one connection concurrently — a slow response no longer blocks fast ones (§5's problem, solved at the HTTP layer).
- **HPACK** compresses repetitive headers; **server push** failed and was removed, because the server can't see the client's cache and guessed wrong too often.
- **TCP-level head-of-line blocking survived** — one lost packet stalls *every* stream on the shared connection, which can make HTTP/2 worse than HTTP/1.1 on lossy networks.

---

## 7. HTTP/3 and QUIC — Abandoning TCP

§6 ended at a wall: head-of-line blocking can't be fixed above a transport that enforces ordering. HTTP/2 did everything possible at its own layer, and TCP still stalled every stream over one lost packet.

There were two ways forward. Fix TCP — or leave it.

Fixing TCP is effectively impossible. It's implemented in operating system kernels and burned into middleboxes, routers, firewalls, and load balancers worldwide. A change would need adoption by every one of them; boxes built a decade ago will never be updated. This is **protocol ossification**: TCP is not frozen because it's perfect, but because too much hardware assumes its exact current shape.

So HTTP/3 left. It runs on **UDP**.

### Why UDP, of All Things

UDP is TCP's minimal sibling: it sends packets with no ordering guarantee, no retransmission, no connection concept. It is, on paper, everything you don't want.

That's precisely why it was chosen. UDP is a **blank slate** — it does so little that middleboxes have no assumptions to break. HTTP/3 doesn't want UDP's absence of features; it wants somewhere to build its own, in user space where it can actually be deployed and updated. Those features are **QUIC**.

QUIC reimplements what TCP provided — reliable delivery, ordering, congestion control — with one decisive difference: **ordering is per-stream, not per-connection.**

```mermaid
flowchart TD
    subgraph T["🔴 HTTP/2 over TCP"]
        L1["📦❌ packet lost"] --> B1["ALL streams stall<br/>— one ordered byte stream"]
    end
    subgraph Q["🟢 HTTP/3 over QUIC"]
        L2["📦❌ packet lost<br/>on stream 1"] --> B2["Only stream 1 waits.<br/>Streams 2, 3, 4 keep flowing —<br/>independently ordered"]
    end
```

That's the fix §6 couldn't reach. A lost packet affects only the stream it belonged to; every other stream is untouched. Head-of-line blocking is finally gone at both layers.

### The Handshake Gets Cheaper Too

QUIC folds the transport and encryption handshakes together. Where TCP + TLS require separate negotiations stacked on each other, QUIC establishes both at once — typically **1 RTT**, and for a server you've connected to before, **0-RTT**: the very first packet can carry real request data (§8 covers what 0-RTT costs in security).

### Connection Migration — The Mobile Win

A TCP connection is identified by four things: source IP, source port, destination IP, destination port. Change any one and it's a different connection. So when your phone moves from Wi-Fi to cellular, its IP changes and **every connection dies** — that stutter when a video pauses on leaving the house is exactly this.

QUIC identifies connections by a **connection ID** independent of IP address. Change networks, keep the connection. The download continues, the call survives, nothing re-handshakes. For mobile users this is often a bigger practical win than the head-of-line fix.

### Where It Stands

| | HTTP/1.1 | HTTP/2 | HTTP/3 |
|---|---|---|---|
| Transport | TCP | TCP | **UDP + QUIC** |
| Format | Text | Binary frames | Binary frames |
| Concurrency | ~6 connections | Multiplexed, 1 connection | Multiplexed, 1 connection |
| HTTP-layer HOL | 🔴 Yes | 🟢 Fixed | 🟢 Fixed |
| Transport HOL | 🟡 Per-connection | 🔴 **All streams** | 🟢 **Fixed** |
| Encryption | Optional | Optional in spec, required in practice | **Built in, mandatory** |
| Survives network change | ❌ | ❌ | ✅ |

HTTP/3 is widely deployed — most major browsers and CDNs support it. It isn't universal: some corporate networks block or throttle UDP, so clients keep a TCP fallback. The gains are largest exactly where the old problems hurt most — lossy mobile networks, high-latency links, users who move between networks.

> 💡 **Key Insight**
>
> HTTP/3's headline is "it uses UDP," which sounds reckless and is actually the opposite. UDP was chosen **because it guarantees nothing** — a protocol that does almost nothing gives middleboxes nothing to assume, so QUIC can rebuild TCP's guarantees in user space where they can be *changed*. The lesson generalises past networking: when a layer is too ossified to fix, the move is to **build on something dumber and reimplement above it**. Note what actually changed — HTTP/3 isn't faster because UDP is fast. It's faster because ordering became per-stream instead of per-connection.

### Quick Recap — HTTP/3 and QUIC

- TCP couldn't be fixed — **ossification** means kernels and middleboxes worldwide assume its exact shape — so HTTP/3 moved to **UDP**.
- UDP was chosen for **guaranteeing nothing**: a blank slate on which **QUIC** rebuilds reliability and ordering in user space, where it can evolve.
- QUIC orders **per stream, not per connection**, which finally eliminates transport-level head-of-line blocking; it also merges the transport and encryption handshakes into ~1 RTT (0-RTT on repeat visits).
- **Connection migration** by connection ID lets a session survive a Wi-Fi-to-cellular switch — often the biggest practical gain for mobile users.
