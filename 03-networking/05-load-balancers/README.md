# Load Balancers

> **Phase:** Networking Deep Dives → **Topic:** 5 of 7 → **Read time:** ~55 minutes

---

## Before You Begin

**This document stands alone.** It assumes you have read nothing else — not the foundation series, not the phase before it, not the topics before it. Everything is built here from zero: why one address has to serve many machines, where the balancing decision happens, how a balancer decides which servers are alive, how servers join and leave without losing work, and how the balancer itself avoids being the thing that takes you down.

Two consequences of that choice:

- **Terms get defined where they're used** — pool, upstream, health check, draining, session affinity, virtual IP, single point of failure. Skim past what you already know.
- **Neighbouring topics are named, not taught.** The specific algorithms for choosing a server, consistent hashing, autoscaling, service discovery, and CDN strategy each have their own full treatment elsewhere in this curriculum. Where they touch balancing, this document says so and points; it doesn't absorb them. *Load balancers themselves are complete here.*

Load balancing is one of the concepts in the **Top 30 Must-Know Concepts** foundation series, where it gets a short introduction. This is that concept's deep-dive.

Here is the question the document answers:

> **When many machines can serve a request, how does anything decide where to send it — and how does it know that machine is still capable of answering?**

Here's the trap it disarms. A load balancer looks like a solved problem. It spreads requests across servers; the concept takes one sentence; every cloud provider offers one as a checkbox with sensible defaults. Nothing about it invites study.

Then you meet the outages. And what's striking about load-balancer outages is that they are almost never caused by the balancer failing to spread traffic. They're caused by it **doing precisely what it was configured to do** — removing servers that were perfectly healthy, keeping servers that had stopped working, discarding requests it was already holding during a routine deploy, or concluding that every machine in the fleet had died at the same instant. In each case the configuration was followed exactly. The configuration encoded a belief that turned out to be wrong.

> **The mindset shift:** stop thinking of a load balancer as *the thing that spreads requests* and start thinking of it as **the thing that continuously decides which servers exist.** Distribution is the easy half, and it is largely solved. The hard half is the judgement running underneath it, re-evaluated every few seconds: *is this machine alive? is it ready yet? is it still ready? should I stop sending it work — and what about the requests it is holding right now?* Every serious load-balancer failure is a wrong answer to one of those four questions. And wrong answers are dangerous precisely because they don't look like failures — they look exactly like the system working as designed.

---

## Table of Contents

1. [Many Servers, One Address](#1-many-servers-one-address)
2. [Where the Balancing Happens](#2-where-the-balancing-happens)
3. [Health Checking — Knowing What's Alive](#3-health-checking--knowing-whats-alive)
4. [What a Health Check Actually Proves](#4-what-a-health-check-actually-proves)
5. [Adding and Removing Servers](#5-adding-and-removing-servers)
6. [Session Affinity — When Requests Must Come Back](#6-session-affinity--when-requests-must-come-back)
7. [Making the Front Door Redundant](#7-making-the-front-door-redundant)
8. [When Balancing Makes Things Worse](#8-when-balancing-makes-things-worse)
9. [What a Load Balancer Cannot Do](#9-what-a-load-balancer-cannot-do)
10. [Putting It All Together — The Health Check That Caused the Outage](#10-putting-it-all-together--the-health-check-that-caused-the-outage)
11. [Final Recap](#11-final-recap)

---

## 1. Many Servers, One Address

Start with a mismatch that has no obvious resolution.

**A client can only address one thing.** It has a name, it resolves that name to an address, it connects. Whatever answers is the system, as far as the client is concerned.

**Capacity requires many things.** One machine has a ceiling — a finite number of requests per second, a finite amount of memory, and a hard limit past which adding work only makes everything slower. Serving more than one machine can handle means running several.

So: clients can hold one address, and you need many machines. Something has to reconcile that.

> **A load balancer is a component that accepts requests at a single address and distributes them across a group of servers, any of which can produce the answer. That group is the pool; each member is an upstream.**

Two words worth fixing now, because they recur throughout: **upstream** means toward the machines that do the work — from the balancer's view, its upstreams are the servers it forwards to. **Downstream** means toward the client that asked.

```mermaid
flowchart LR
    C1["👤"] --> LB["⚖️ Load balancer<br/>one address"]
    C2["👤"] --> LB
    C3["👤"] --> LB
    LB --> S1["🖥️ Upstream 1"]
    LB --> S2["🖥️ Upstream 2"]
    LB --> S3["🖥️ Upstream 3"]
```

### The Precondition Nobody States

There's a requirement hiding in that diagram, and it's the one that makes everything else possible:

> **Any server in the pool must be able to answer any request.**

If server 2 knows something server 1 doesn't — a logged-in user's shopping cart, a partially uploaded file, a cached computation — then "send it anywhere" stops being true, and the balancer's freedom to choose evaporates. Every request from that user must now return to server 2 specifically.

This property is called being **stateless**: the server holds nothing between requests that a later request depends on. Anything that must persist lives somewhere shared — a database, a cache, a token the client carries.

Statelessness is what makes machines **interchangeable**, and interchangeability is the entire foundation of this document. It's why you can add a server and immediately use it, remove one and lose nothing, and replace a failed one without any client noticing. §6 is what happens when you can't have it.

### What "Balancing" Actually Means

The name suggests equalising load, and that's the aspiration rather than the mechanism. A balancer doesn't measure load and equalise it; it applies a **selection rule** to each incoming request and hopes the result distributes work evenly.

That distinction matters because the rule can be wrong. Sending requests to servers in rotation distributes *requests* evenly — which distributes *work* evenly only if all requests cost the same and all servers are equally capable. Neither is reliably true.

**The specific rules — rotation, fewest-connections, weighted, hash-based — and how each behaves under load are Topic 06.** This document treats the choice as a black box: *something* picks an upstream. What matters here is everything around that choice, which turns out to be where the difficulty lives.

### Three Things You Get Beyond Capacity

Capacity is the obvious motivation. Three others come along with it, and in practice they're often the reason a balancer is deployed in front of a *single* server:

| Benefit | What it means |
|---|---|
| **Survives failure** | A machine dies; the others absorb its traffic. Nobody outside notices |
| **Deploys without downtime** | Update servers a few at a time while the rest serve (§5) |
| **The fleet is invisible** | Clients hold one address; what's behind it can grow, shrink, or be entirely replaced |

The middle row is worth flagging as the one teams underestimate. Deploying without dropping requests isn't an application capability — it's something the balancer provides by controlling which servers receive traffic and when. §5 is how.

> 💡 **Key Insight**
>
> A load balancer exists to resolve an unavoidable mismatch — **clients can address one thing, capacity requires many** — and the entire arrangement rests on one precondition that's easy to state and hard to keep: **any server must be able to answer any request.** Notice that distribution, the thing the component is named after, is the part that's essentially solved. Everything genuinely difficult is adjacent to it: knowing which servers are capable of answering, and changing that set safely while traffic is flowing.

### Quick Recap — Many Servers, One Address

- Clients can hold **one address**; capacity requires **many machines**. A load balancer reconciles that, distributing across a **pool** of **upstreams**.
- The precondition is **statelessness** — any server must answer any request — which is what makes machines **interchangeable**.
- "Balancing" is really applying a **selection rule** and hoping work distributes evenly; the rules themselves are **Topic 06**.
- Beyond capacity it buys **failure survival, zero-downtime deploys, and an invisible fleet** — and the deploy benefit is a balancer feature, not an application one (§5).

---

## 2. Where the Balancing Happens

§1 treated the selection rule as a black box. Before opening anything else, there's a prior question: **at what granularity does the balancer get to choose?**

The answer depends on how much of the traffic it interprets, and it produces two quite different components that share a name.

### Connections Versus Requests

Network traffic arrives in layers. A **connection** is the lower-level thing — two machines establish a channel identified by addresses and ports, and bytes flow through it. A **request** is the higher-level thing — a structured message with a destination path, headers, and a body, carried inside that channel.

The distinction matters enormously here, because **one connection carries many requests.** A browser opens a connection and sends dozens of requests over it. So a balancer that decides per *connection* makes one decision covering all of them, while a balancer that decides per *request* makes a fresh decision each time.

That single difference is what separates the two kinds:

| | **Connection-level (L4)** | **Request-level (L7)** |
|---|---|---|
| Decides once per | **Connection** | **Request** |
| Can distribute on | Source address, destination port | Path, headers, cookies, method, host |
| Interprets traffic | No — bytes are opaque | Yes — must parse each message |
| Works with encrypted traffic | ✅ Never needs to read it | ❌ Must decrypt first |
| Protocol support | Anything — databases, queues, custom | The protocol it implements (usually HTTP) |
| Cost per request | Minimal | Parsing and re-emitting |

The layer numbers come from a standard network model — **Layer 4** being the transport layer that moves bytes between ports, **Layer 7** the application layer where those bytes have meaning. The numbering is conventional shorthand; the substance is entirely in the first row of that table.

```mermaid
flowchart TD
    subgraph L4["🔌 L4 — one decision per connection"]
        C1["👤 One connection<br/>carrying 30 requests"] --> D1["⚖️ picks a server"]
        D1 --> A1["🖥️ ALL 30 go here"]
    end
    subgraph L7["📄 L7 — one decision per request"]
        C2["👤 One connection<br/>carrying 30 requests"] --> D2["⚖️ picks per request"]
        D2 --> B1["🖥️ Server A"]
        D2 --> B2["🖥️ Server B"]
        D2 --> B3["🖥️ Server C"]
    end
```

### What Each Granularity Costs You

The consequences run deeper than "L7 is more flexible."

**A long-lived connection pins its traffic.** With connection-level balancing, a client that keeps a connection open for an hour sends an hour of traffic to whichever server it was assigned. If that server is overloaded, nothing corrects it until the connection closes. Distribution that looked even at connection time drifts arbitrarily far from even as connections age — and the busiest clients, holding the most persistent connections, are exactly the ones least likely to be redistributed.

**Removing a server is harder at L4.** When a server must be taken out of service (§5), a request-level balancer simply stops choosing it and existing requests finish naturally. A connection-level balancer has connections *bound* to that server, and must either wait for them to close on their own or break them.

**Encryption forces the choice.** Reading a path or header means the traffic must be decrypted first. A connection-level balancer never reads anything, so it forwards encrypted traffic untouched and never needs a certificate. A request-level balancer must terminate the encryption to see inside — which means it holds the certificate and sees all content in plaintext. That's a security decision embedded in what looks like a routing choice.

**Health checking gets sharper at L7.** A connection-level balancer can generally establish that a port accepts connections. A request-level one can issue a real request and evaluate the response — which is where §3 and §4 live, and it's the more consequential difference than routing flexibility.

### Two Other Places Balancing Can Happen

A dedicated balancer isn't the only option, and both alternatives are worth recognising:

- **Name-resolution balancing.** The name-to-address lookup returns different addresses to different clients, spreading them before any connection is made. It's the only approach that distributes across *separate locations*, since a single balancer necessarily lives in one of them. Its weakness is that the answers are cached by machines you don't control, so removing a failed address doesn't take effect until those caches expire — which makes it poor at reacting to failure. §7 returns to this.
- **Client-side balancing.** The client holds the server list and chooses directly, with no middle component. This removes an entire hop and its failure mode, at the cost of every client needing the current list and the selection logic. Common inside systems where you control all the callers; impractical when the callers are browsers. *How clients obtain and refresh that list is service discovery, which belongs to Phase 09.*

> 💡 **Key Insight**
>
> The real question isn't which layer a balancer operates at — it's **how often it gets to decide.** Connection-level balancing makes one choice and lives with it for the life of that connection, which means a long-lived connection is effectively a long-term assignment that nothing revisits. Request-level balancing re-decides continuously, so the distribution self-corrects and servers can be removed cleanly. Everything else — routing flexibility, encryption handling, health-check depth — follows from that difference in decision frequency.

### Quick Recap — Where the Balancing Happens

- **One connection carries many requests**, so the decisive question is whether the balancer chooses per **connection** (L4) or per **request** (L7).
- Connection-level balancing **pins long-lived connections** to one server, so distribution drifts and removal is disruptive; request-level balancing re-decides and self-corrects.
- **Encryption forces the choice**: reading paths and headers requires terminating it, which means holding the certificate and seeing plaintext.
- **Name-resolution balancing** spreads across locations but reacts slowly to failure; **client-side balancing** removes the hop but requires every client to hold the server list.

---

## 3. Health Checking — Knowing What's Alive

A balancer distributing across a pool needs to know what's in the pool. Not the configured list — the *currently working* list. Servers crash, hang, run out of memory, get rebooted, and lose network connectivity, and none of them announce it.

> **A health check is a periodic test the balancer runs against each upstream to decide whether it should keep receiving traffic.**

This is the mechanism that turns a static configuration into a live view of reality, and it's where most of this document's difficulty concentrates.

### Two Ways to Find Out

**Active checking** — the balancer independently contacts each server on a schedule and evaluates the response. Every few seconds, every server, whether or not real traffic is flowing.

**Passive checking** — the balancer watches real traffic and draws conclusions. A server returning errors or timing out repeatedly gets marked bad, with no separate probe.

| | Active | Passive |
|---|---|---|
| Cost | Constant background traffic | Free — uses requests already happening |
| Detects a problem | Even with no traffic | Only by **failing real user requests** |
| Idle servers | Covered | Invisible until traffic arrives |
| Realism | Tests what the probe tests (§4) | Tests exactly what users experience |

The tradeoff is stark: passive checking is free and perfectly realistic, but it learns a server is broken by **letting real users hit it**. Active checking costs constant probing but finds problems before a user does. Most production setups run both — active checks as the primary signal, passive observation as a faster-reacting supplement.

### The Four Numbers

Active checking is configured almost entirely by four values, and their interaction is more consequential than any of them alone:

| Setting | Meaning | Typical |
|---|---|---|
| **Interval** | How often to probe | 5–30 s |
| **Timeout** | How long to wait before calling a probe failed | 1–5 s |
| **Unhealthy threshold** | Consecutive failures before removing the server | 2–3 |
| **Healthy threshold** | Consecutive successes before returning it | 2–5 |

The thresholds exist because a single failed probe means very little. Packets are lost, servers pause briefly, networks hiccup. Removing a server on one missed probe would produce constant churn from noise. Requiring several consecutive failures filters that out.

But the filtering isn't free, and this is the number that actually matters:

> **Detection budget = interval × unhealthy threshold (+ up to one timeout).** This is how long a dead server keeps receiving traffic before the balancer notices.

With a 10-second interval and a threshold of 3, a server that dies at any moment continues receiving requests for **up to 30 seconds**. Every request routed to it during that window fails.

```mermaid
flowchart LR
    D["💥 Server dies<br/>T+0"] --> P1["❌ probe 1 fails<br/>T+10s"]
    P1 --> P2["❌ probe 2 fails<br/>T+20s"]
    P2 --> P3["❌ probe 3 fails<br/>T+30s"]
    P3 --> R["🚫 Removed from pool<br/>T+30s"]
    D -.->|"⚠️ 30 seconds of<br/>failed user requests"| R
```

### Why Not Just Check Constantly

The obvious response is to shrink the interval and threshold. Both directions cost something:

- **A short interval** multiplies probe traffic across the fleet — a hundred servers checked every second is a hundred requests per second of pure overhead, and each probe consumes a connection and a worker slot.
- **A low threshold** makes the balancer twitchy. One lost packet removes a healthy server, its traffic redistributes onto the others, and it returns moments later. Under load this produces **flapping**: servers cycling in and out of the pool while traffic sloshes back and forth. §8 explains why flapping is genuinely worse than a clean failure.

There's also an asymmetry worth exploiting deliberately: **removing a server should be fast, returning it should be slow.** Removing a healthy server briefly costs a little capacity; returning a broken server costs failed requests. So a low unhealthy threshold with a higher healthy threshold is usually the right shape — quick to doubt, slow to re-trust.

### The Probe Is Not the Traffic

One structural caveat that §4 develops fully. A health check is a *separate* request the balancer makes on its own behalf. It is not the user's request, it doesn't follow the same path through the application, and it may succeed under exactly the conditions where real requests fail.

A server can pass every probe while being useless — its thread pool exhausted, its dependency unreachable, its responses wrong. The probe answered because answering the probe was cheap.

> ⚠️ **The detection budget is the most under-examined number in a load-balancer configuration.** Teams tune intervals and thresholds independently, without multiplying them, and are then surprised that a crashed server took half a minute to leave the pool. Every configuration contains that answer already — `interval × threshold` — and it directly determines how many user requests a sudden failure costs you. It is worth knowing before an incident rather than calculating during one.

### Quick Recap — Health Checking

- A **health check** converts a static server list into a live one; **active** checks probe on a schedule, **passive** checks infer from real traffic (learning by failing real users).
- Four settings govern it — **interval, timeout, unhealthy threshold, healthy threshold** — and the thresholds exist to filter transient noise.
- **Detection budget = interval × unhealthy threshold**: how long a dead server keeps receiving traffic. A 10 s interval with a threshold of 3 means **30 seconds of failed requests**.
- Tighten it and you get **flapping**; the right shape is asymmetric — **quick to remove, slow to restore** (§8).

---

## 4. What a Health Check Actually Proves

§3 ended on a caveat that deserves its own section, because it is the source of the most damaging load-balancer failures there are.

A health check answers exactly one question: **did this specific probe succeed?** Everything else — *is this server working, is it fast enough, can it serve users* — is inference. The gap between what the probe proves and what you believe it proves is where systems break.

### The Spectrum

Health checks range from trivially shallow to dangerously deep:

| Depth | The probe | Proves | Misses |
|---|---|---|---|
| **Connection** | Can I open a connection to the port? | Something is listening | A hung process still holds the port open |
| **Shallow** | `GET /health` → does it return OK? | The web layer answers | The application may be unable to do real work |
| **Deep** | `GET /health` → checks the database, cache, dependencies | The server can genuinely serve | **Failures shared across the whole fleet (below)** |
| **Synthetic** | Perform a representative real operation | Closest to user reality | Expensive; may have side effects |

Reading down that table, deeper looks strictly better. Each level catches failures the one above misses. The natural conclusion is to make health checks as deep as possible.

**That conclusion causes outages.**

### The Trap — Shared Dependencies

Consider a deep health check that verifies the database is reachable. It looks obviously correct: a server that can't reach the database genuinely cannot serve requests, so it shouldn't receive traffic.

Now the database has a brief problem. Not an outage — a 40-second pause from a failover, a lock, a network blip.

Every server in the fleet checks the same database. So every server fails its health check. **Simultaneously.**

```mermaid
flowchart TD
    DB["🗄️ Database pauses<br/>40 seconds"]
    DB --> S1["🖥️ Server 1<br/>❌ check fails"]
    DB --> S2["🖥️ Server 2<br/>❌ check fails"]
    DB --> S3["🖥️ Server 3<br/>❌ check fails"]
    DB --> S4["🖥️ Server 4<br/>❌ check fails"]
    S1 & S2 & S3 & S4 --> LB["⚖️ Balancer removes<br/>ALL of them"]
    LB --> R["💀 Empty pool<br/>every request fails"]
```

The balancer, following its configuration exactly, empties the entire pool. There are no healthy servers left, so every request now fails — including requests that don't touch the database at all, and including any request that might have succeeded while the database recovered.

A **degraded** system became a **dead** one, and the load balancer is what killed it. The database recovered after 40 seconds; the outage lasted far longer, because now the fleet has to pass its healthy threshold (§3) and the backlog of waiting clients arrives all at once (§8).

The failure mode generalises past databases: **any health check that tests a dependency shared by the whole fleet converts a partial failure of that dependency into a total failure of your service.** The check that was supposed to protect users from broken servers instead removed every working server they had.

### What Health Checks Are Actually For

The resolution comes from being precise about the question a health check answers:

> **A health check should answer: "is this server, specifically, worse than its peers?" — not "is the system healthy?"**

Health checking is a **comparative** mechanism. Its purpose is choosing among servers, and it only helps when servers can differ. A condition affecting every server equally carries no information for that decision — removing them all is never the right response, because there is nowhere better to send the traffic.

That gives a usable rule:

| Check for things that are… | Because |
|---|---|
| **Local to one server** — process alive, threads available, disk usable, warm-up finished | Some servers can be worse than others; removal helps |
| **Not** shared by the whole fleet — the database, a downstream API, a shared cache | Removal cannot help; there's nowhere better to route |

Shared dependencies still need monitoring — they just need *alerting*, not *traffic removal*. Those are different mechanisms with different consequences, and conflating them is precisely the trap.

### Practical Shapes

Two patterns that resolve most of this in practice:

**Separate the questions.** Expose two endpoints: one answering *"is this process alive and able to serve?"* for the balancer, another answering *"are my dependencies reachable?"* for monitoring dashboards. The balancer reads the first; humans and alerting read the second.

**Fail open at the fleet level.** Some balancers support a safety rule: if more than a set fraction of the pool is unhealthy, treat them all as healthy again. The reasoning is blunt and correct — if 90% of your servers report unhealthy, the far more likely explanation is that the *check* is wrong, and sending traffic to possibly-degraded servers beats sending it nowhere. It's a valuable last-resort guard against exactly the cascade above.

> 💡 **Key Insight**
>
> A health check is a **comparative** instrument, not a diagnostic one: its only job is deciding whether *this* server is worse than its peers. The moment a check tests something every server shares, it stops discriminating and starts synchronising — every server fails together, the pool empties, and a dependency hiccup becomes a total outage caused by the machinery meant to prevent one. The correct depth isn't "as deep as possible," it's **exactly as deep as the things that can differ between one server and the next.**

### Quick Recap — What a Health Check Proves

- A check proves only that **one probe succeeded**; "the server works" is inference, and the gap is where outages live.
- Depth ranges from **connection → shallow → deep → synthetic**, and deeper is *not* strictly better.
- **A deep check on a shared dependency fails the whole fleet at once**, converting a brief dependency problem into a total outage — the balancer emptying the pool exactly as configured.
- Check **only what can differ between servers**; monitor shared dependencies with alerting instead, and consider a **fail-open** rule when most of the pool reports unhealthy.
