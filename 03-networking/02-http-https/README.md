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
