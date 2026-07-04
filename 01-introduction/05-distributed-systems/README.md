# Group 5 — Distributed Systems Foundations

> **Phase:** Foundation → **Group:** 5 of 6 → **Read time:** ~50 minutes

---

## Before You Begin

In Group 4, you learned to scale a system: run many app servers, add read replicas, shard the database, cache aggressively, push content to the edge.

Every one of those techniques did the same thing — it spread your system across **more than one machine.**

And the moment your system lives on more than one machine, you've crossed a line. You are no longer building a program; you are building a **distributed system.** A new class of problem appears — one that has nothing to do with speed or capacity:

> **What happens when those machines disagree, or when the network between them fails?**

On a single machine, this never happens. There's one clock, one memory, one source of truth. If a function is called, it runs. If a value is written, it's there.

Across a network, none of that holds. Messages get lost. A machine that looks dead is just slow. Two replicas of the same data hold two different values. There is no shared clock to say which write happened "first." Failure is no longer all-or-nothing — parts of the system work while others don't, at the same time.

This group is about that world. You'll learn what a distributed system actually is, why it's fundamentally hard, and the core ideas engineers use to reason about it — **consistency models**, the **CAP theorem**, how machines **coordinate**, and how systems **survive failure**.

These are the ideas that separate "I can build a feature" from "I can design a system that stays correct when things go wrong." They get full deep-dives later. Here, you build the mental model that makes those deep-dives click.

> **The mindset shift:** On one machine, you reason about *logic*. Across many machines, you reason about *failure*. Distributed systems design is failure-first thinking.

---

## Table of Contents

1. [Big Picture — What Is a Distributed System?](#1-big-picture--what-is-a-distributed-system)
2. [Why Distributed Systems Are Hard — The Fallacies](#2-why-distributed-systems-are-hard--the-fallacies)
3. [Consistency Models — What "Consistent" Even Means](#3-consistency-models--what-consistent-even-means)
4. [The CAP Theorem — The Central Tradeoff](#4-the-cap-theorem--the-central-tradeoff)
5. [PACELC — Beyond CAP](#5-pacelc--beyond-cap)
6. [How Machines Coordinate](#6-how-machines-coordinate)
7. [Handling Failure Gracefully](#7-handling-failure-gracefully)
8. [Putting It All Together](#8-putting-it-all-together)
9. [Final Recap](#9-final-recap)

---

## 1. Big Picture — What Is a Distributed System?

A **distributed system** is a group of independent computers that cooperate to appear, to the user, as a single coherent system.

You already use dozens of them. When you open a web app, your request might touch a load balancer, five app servers, three database replicas, a cache cluster, and a CDN edge node — across multiple data centers on multiple continents. You experience "one website." It is, in reality, hundreds of machines pretending to be one.

```mermaid
flowchart TD
    User["👤 User<br/>(sees 'one system')"]
    User --> LB["⚖️ Load Balancer"]
    LB --> A1["🖥️ App"]
    LB --> A2["🖥️ App"]
    A1 --> Cache["⚡ Cache Cluster"]
    A2 --> Cache
    A1 --> DB[("🗄️ DB Replicas")]
    A2 --> DB
```

### Why Do We Even Build Them?

Nobody chooses distributed systems for fun — they're harder in every way. We're *forced* into them for exactly the reasons you saw in Group 4:

| Reason | What forces it |
|---|---|
| **Scale** | One machine can't handle the load or hold the data |
| **Fault tolerance** | If one machine dies, the system must keep running |
| **Low latency** | Users are global; you must be physically near them |

Every distributed system is a trade: you accept enormous complexity in exchange for scale, resilience, and reach that a single machine can never provide.

### The Two Truths That Change Everything

Almost every hard problem in distributed systems traces back to just two facts that don't exist on a single machine:

**1. The network is unreliable.**
Messages can be lost, delayed, duplicated, or reordered. And critically — when you send a request and hear nothing back, **you cannot tell why.** Did the request never arrive? Did it succeed but the *reply* got lost? Is the other machine just slow? From the outside, a crashed machine and a slow machine look *identical*. This single ambiguity is the source of most distributed-systems pain.

**2. There is no shared clock.**
Each machine has its own clock, and they drift. So there is no universal "now," and no reliable way to say which of two events on two machines happened *first*. "Order" — something you take completely for granted on one CPU — becomes a genuinely hard problem.

```mermaid
flowchart LR
    A["🖥️ Server A<br/>sends request"] -->|"???"| B["🖥️ Server B"]
    B -.->|"reply lost?"| A
    Note["A hears nothing.<br/>Did B crash? Is B slow?<br/>Did it work but the reply vanished?<br/>A cannot know."]
```

> 💡 **Key Insight**
>
> **Partial failure** is the defining feature of a distributed system. On one machine, either everything works or everything crashes. Across a network, *some* parts work while *others* fail — silently, at the same time — and you often can't tell which. Designing for that ambiguity is the entire discipline.

### Quick Recap — What Is a Distributed System

- A **distributed system** is many independent machines cooperating to look like one.
- We build them (despite the pain) for **scale**, **fault tolerance**, and **low latency**.
- Two facts change everything: the **network is unreliable**, and there is **no shared clock**.
- A crashed machine and a slow machine look identical from the outside.
- **Partial failure** — some parts working while others fail — is the core challenge.

---

## 2. Why Distributed Systems Are Hard — The Fallacies

In the 1990s, engineers at Sun Microsystems noticed that newcomers to distributed systems kept making the *same* wrong assumptions — assumptions that are perfectly true on one machine and dangerously false across a network. They wrote them down as **The Fallacies of Distributed Computing.**

Every one of them is a comfortable belief that will eventually cause an outage.

| # | The Fallacy ("we assume…") | The Reality |
|---|---|---|
| 1 | **The network is reliable** | Packets drop; connections fail. Design for it. |
| 2 | **Latency is zero** | A remote call is thousands of times slower than a local one. |
| 3 | **Bandwidth is infinite** | Links saturate; large payloads clog the pipe. |
| 4 | **The network is secure** | Anything on the wire can be seen or tampered with. |
| 5 | **Topology doesn't change** | Machines come and go; IPs change; nodes are added and removed. |
| 6 | **There is one administrator** | Many systems, many owners, many failure sources. |
| 7 | **Transport cost is zero** | Serialization, bandwidth, and infrastructure all cost. |
| 8 | **The network is homogeneous** | Different machines, protocols, and versions must interoperate. |

You don't need to memorize the list. You need the *pattern* behind it:

> **Every convenience you rely on within a single process — instant calls, guaranteed delivery, a shared truth — quietly disappears the moment a network is involved.**

### Why This Matters in Practice

Consider one innocent line of code: `user = getUser(id)`.

- **On one machine**, it's a function call. It returns in nanoseconds. It always returns.
- **Across a network**, that same line is a remote request. It might take 200ms. It might time out. It might succeed but the response gets lost. It might return *stale* data from a lagging replica.

The code looks identical. The reality is worlds apart. Distributed systems are hard precisely because the *hardest problems are invisible in the code* — they live in the gaps between the machines.

> ⚠️ **The most dangerous assumption is #1.** Beginners write code as if the network always works, test it on one machine where it always does, and ship it. Then in production — at 3 a.m., under load — a packet drops, and behavior nobody designed for takes over. Assume failure from line one.

### Quick Recap — Why They're Hard

- The **Fallacies of Distributed Computing** are the false-but-comfortable assumptions newcomers make.
- The unifying pattern: guarantees you get for free *within* a process vanish *across* a network.
- The same line of code means something completely different locally vs remotely.
- The hardest bugs are invisible in the code — they live between the machines.
- Assume the network will fail, from the very first line.

---

## 3. Consistency Models — What "Consistent" Even Means

The moment you keep **more than one copy** of data — a database and its replicas, a cache in front of a database, shards syncing state — a question appears that never existed on a single machine:

> **If two copies can disagree, what does the user actually see?**

The answer is a choice, not an accident. A **consistency model** is the contract a system makes about *when* a write becomes visible and *which* value a reader gets. It sits on a spectrum, and the two ends anchor everything in between.

### Strong Consistency

**The guarantee:** the instant a write succeeds, *every* subsequent read — from any replica — returns that new value. The system behaves as if there were only one copy.

```mermaid
flowchart LR
    Write["✍️ Write: balance = 100"] --> System["🗄️ System"]
    System --> R1["📖 Read → 100 ✅"]
    System --> R2["📖 Read → 100 ✅"]
    System --> R3["📖 Read → 100 ✅"]
```

- **Feels like:** a single, always-correct machine. Intuitive and safe.
- **Cost:** the system must coordinate across replicas *before* confirming the write — which means more latency, and if replicas can't be reached, the write may have to **block or fail**.
- **Use when:** correctness is non-negotiable — bank balances, inventory counts, "did my payment go through?"

### Eventual Consistency

**The guarantee:** if writes stop, all copies will *eventually* converge to the same value. But for a short window, different readers may see different (stale) values.

```mermaid
flowchart LR
    Write["✍️ Write: likes = 101"] --> System["🗄️ System"]
    System --> R1["📖 Read → 101 ✅ (updated)"]
    System --> R2["📖 Read → 100 ⏳ (not yet)"]
    System --> R3["📖 Read → 100 ⏳ (not yet)"]
```

- **Feels like:** occasionally out-of-date, but fast and always available.
- **Cost:** the application must tolerate temporarily stale reads.
- **Use when:** availability and speed matter more than instant accuracy — like counts, view counters, social feeds, DNS.

### The Real-World Spectrum

Strong and eventual are the endpoints; production systems live all along the line, often with useful middle grounds:

| Model | Guarantee | Classic example |
|---|---|---|
| **Strong** | Every read sees the latest write | Bank account balance |
| **Read-your-writes** | *You* always see your own writes (others may lag) | Editing your own profile |
| **Causal** | Related events are seen in order (cause before effect) | Comment appears after the post it replies to |
| **Eventual** | All copies converge... eventually | Like counts, view counts |

> 💡 **Key Insight**
>
> "Consistent" is not one thing — it's a **dial**, and turning it is a business decision, not just a technical one. A like counter that's stale for two seconds is fine; a bank balance that's stale for two seconds is a lawsuit. Engineers pick the *weakest* model the use case can tolerate, because weaker consistency buys speed and availability.

### Quick Recap — Consistency Models

- With multiple copies of data, you must choose **when** a write becomes visible.
- **Strong consistency** = every read sees the latest write; safe but slower and less available.
- **Eventual consistency** = copies converge over time; fast and available but temporarily stale.
- Real systems use a **spectrum** (read-your-writes, causal, …) between the two.
- Pick the **weakest** model the use case can safely tolerate.

---

## 4. The CAP Theorem — The Central Tradeoff

Why can't a distributed system just be strongly consistent *and* always available? The **CAP theorem** explains why — and it's the single most important idea in this group.

It says that a distributed system can offer at most **two** of these three properties at the same time:

- **C — Consistency:** every read sees the most recent write (the strong consistency from Section 3).
- **A — Availability:** every request gets a (non-error) response, even if some machines are down.
- **P — Partition tolerance:** the system keeps working even when the network between machines is broken (a **partition**).

```mermaid
flowchart TD
    CAP["CAP: pick 2 of 3"]
    CAP --> C["🎯 Consistency"]
    CAP --> A["🟢 Availability"]
    CAP --> P["🔌 Partition Tolerance"]
```

### The Catch — P Is Not Optional

Here's what makes CAP a *real* decision rather than an academic one: **in a distributed system, network partitions are a fact of life.** Cables get cut, switches fail, data centers lose connectivity. You *cannot* choose to not have partitions — so you *must* tolerate them.

That collapses "pick 2 of 3" into a much sharper choice. **When a partition happens, you get exactly one decision:**

> **Do you sacrifice Consistency, or sacrifice Availability?**

```mermaid
flowchart TD
    Start["🔌 Network partition happens<br/>(replicas can't talk)"]
    Start --> Q{"A write arrives.<br/>What do you do?"}
    Q -->|"Accept it anyway"| AP["🟢 AP — stay Available<br/>Risk: replicas now disagree<br/>(sacrifice Consistency)"]
    Q -->|"Refuse until healed"| CP["🎯 CP — stay Consistent<br/>Cost: some requests fail<br/>(sacrifice Availability)"]
```

- **CP (Consistency + Partition tolerance):** during a partition, refuse requests you can't safely serve. The system may return errors, but it **never gives a wrong answer.** → *banking, inventory, anything where wrong ≫ unavailable.*
- **AP (Availability + Partition tolerance):** during a partition, keep answering with whatever data you have. The system **stays up** but may return **stale or conflicting** data (reconciled later). → *social feeds, shopping carts, DNS — anything where "up" ≫ "perfectly correct."*

### It's Not All-or-Nothing

CAP describes behavior **during a partition** — which is rare. The rest of the time (the vast majority), a well-built system can be both consistent *and* available. CAP isn't a permanent label on your system; it's the answer to *"when the network splits, which way do you fall?"*

> 💡 **Key Insight**
>
> CAP is not about picking a database brand — it's about a promise you make to your users for the worst moment. "When I can't guarantee correctness, do I go *down* (CP) or go *wrong* (AP)?" Amazon famously chose **AP** for shopping carts: better to let you keep adding items (and reconcile later) than to show an error and lose the sale.

### Quick Recap — CAP Theorem

- A distributed system can guarantee at most **two** of **C**onsistency, **A**vailability, **P**artition tolerance.
- Partitions are unavoidable, so **P is mandatory** — the real choice is **C vs A during a partition**.
- **CP** systems stay correct but may reject requests (banking, inventory).
- **AP** systems stay up but may serve stale/conflicting data (feeds, carts, DNS).
- The tradeoff only bites *during* a partition; otherwise you can have both.

---

## 5. PACELC — Beyond CAP

CAP has a blind spot: it only describes what happens **during a partition.** But partitions are rare. What governs your system the other 99.9% of the time?

**PACELC** extends CAP to answer that. Read it as a sentence:

> **If** there is a **P**artition, choose between **A**vailability and **C**onsistency —
> **E**lse (normal operation), choose between **L**atency and **C**onsistency.

```mermaid
flowchart LR
    P{"Partition?"}
    P -->|"Yes"| AC["Availability vs Consistency<br/>(the CAP choice)"]
    P -->|"No (normal)"| LC["Latency vs Consistency<br/>(the everyday choice)"]
```

The second half is the insight most people miss: **even when the network is perfectly healthy, strong consistency still costs latency.** To guarantee every read sees the latest write, replicas must coordinate on every operation — and coordination takes time. So a system that insists on strong consistency pays a *latency tax on every single request*, partition or not.

That's why many high-scale systems relax consistency **even in normal operation** — not because they fear partitions, but because they refuse to pay that latency tax billions of times a day.

| System style | During partition | Normal operation |
|---|---|---|
| **PA/EL** (e.g. Dynamo-style, Cassandra) | Availability | Low latency (relax consistency) |
| **PC/EC** (e.g. traditional RDBMS) | Consistency | Consistency (accept the latency) |

> 💡 **Key Insight**
>
> CAP asks "what about the disaster?" PACELC adds "...and what about *every ordinary Tuesday*?" The everyday **latency vs consistency** tradeoff shapes far more of a system's design than the rare partition ever will.

### Quick Recap — PACELC

- CAP only covers the (rare) partition case; **PACELC** adds the normal case.
- **If Partition:** Availability vs Consistency. **Else:** Latency vs Consistency.
- Strong consistency costs latency **even when the network is healthy** — coordination isn't free.
- Many systems relax consistency in normal operation to avoid paying that tax constantly.

---
