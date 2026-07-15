# Scalability

> **Phase:** Core System Properties → **Topic:** 4 of 5 → **Read time:** ~50 minutes

---

## Before You Begin

Three properties down. You can now reason about whether a system is **fast** (latency/throughput), **there** (availability), and **right** (reliability). Each was measured under some *given* load. This document removes that comfort and asks what happens when the load itself **grows** — 10×, 100×, 1000× — because a system that's fast, available, and reliable for a thousand users can quietly become none of those things for ten million.

> **As load grows, does the system keep up — and what does it cost to make it?**

That is **scalability**, and it's the property that quietly governs whether a product can *become successful without collapsing under its own success.* The cruel irony of systems is that the reward for building something people love is a traffic curve that destroys naive designs. Scalability is how you earn the right to grow.

You already have every tool you need to reason about it — you just haven't pointed them at *growth* yet:

- **Little's Law and the utilization curve** (Latency doc) told you concurrency, throughput, and latency are linked, and that latency explodes as you approach capacity. Scaling is the art of raising that capacity ceiling — and of understanding why raising it is harder than it looks.
- **The redundancy math** (Availability doc) showed how adding parallel copies changes a system. Scaling *out* is that same instinct aimed at capacity instead of uptime.
- **Failure multiplies under scale** (Reliability doc) — more components mean more faults, more partial failures, more correlated blast radius. Growth is an adversary of reliability, not just performance.
- **Bottleneck thinking** (Group 4) is the master skill here: a system scales exactly as far as its *narrowest shared resource*, and no further.

One scoping note, so this document stays in its lane. This is the **property** of scalability — what it *is*, how to reason about it, the vocabulary and the laws. The *techniques* for achieving it — horizontal scaling mechanics, sharding, replication, caching, load balancing, auto-scaling — get their proper, deep treatment in **Group 4** (intro) and the later **Scaling & Performance** phase. Here they appear only as *named pointers*. We're building the yardstick, not the toolbox.

Here's the trap. Beginners equate "scalable" with "fast," or think scalability is a feature you can bolt on later ("we'll make it scale when we need to"). Both are wrong, and expensively so. Scalability isn't speed, and it isn't a switch — it's a *property of how your system's cost and performance respond to growth*, largely determined by structural decisions made early. By the end, you'll see scalability not as "handling lots of traffic" but as a **slope**: the relationship between load and cost.

> **The mindset shift:** stop asking *"is it fast?"* — start asking *"as load grows 10×, does cost grow **10× or 100×** — and what **breaks first**?"* Scalability is not a speed. It's the *shape of the curve* relating load to the resources needed to serve it.

---

## Table of Contents

1. [What Scalability Actually Means](#1-what-scalability-actually-means)
2. [Load and the Dimensions of Scale](#2-load-and-the-dimensions-of-scale)
3. [Scalability vs Performance vs Capacity](#3-scalability-vs-performance-vs-capacity)
4. [Vertical vs Horizontal Scaling](#4-vertical-vs-horizontal-scaling)
5. [The Limits of Scaling — Amdahl and the USL](#5-the-limits-of-scaling--amdahl-and-the-usl)
6. [Why Scaling Is Hard — State](#6-why-scaling-is-hard--state)
7. [Bottlenecks and the Shifting Constraint](#7-bottlenecks-and-the-shifting-constraint)
8. [Scaling Reads, Writes, and Data](#8-scaling-reads-writes-and-data)
9. [Elasticity, Cost, and the Economics of Scale](#9-elasticity-cost-and-the-economics-of-scale)
10. [Putting It All Together — Brimble Grows 100×](#10-putting-it-all-together--brimble-grows-100)
11. [Final Recap](#11-final-recap)

---

## 1. What Scalability Actually Means

As always, start with the definition most people carry, then break it.

**The naive definition:** "scalable" = "handles a lot of traffic" or, worse, "fast." A system that serves 100,000 users must be scalable; a slow system must be unscalable.

**The problem:** speed and scale are different properties, and conflating them hides the whole idea. A blisteringly fast system can be *completely* unscalable, and a rather slow one can scale beautifully:

- A trading system answers in 50 microseconds — but only because everything lives on one enormous machine, and there is *no way to add a second*. Fast, and utterly unscalable. Growth has a hard wall.
- A batch analytics pipeline takes *hours* per job — but double the machines and it does twice the work, forever. Slow, and perfectly scalable.

So scalability is not about how the system performs *right now*. It's about how performance and cost **respond to growth**:

> **Scalability** is the ability of a system to handle increased load by adding resources — ideally with cost growing *proportionally* to load, not faster. It's a property of the **slope**, not the starting point.

### It's a Slope, Not a Number

This is the reframing that makes everything else click. Picture load on the x-axis and the resources (cost) needed to serve it on the y-axis. Scalability is the *shape of that line*:

```mermaid
flowchart LR
    subgraph G["Cost vs Load — the shape IS scalability"]
        direction TB
        L["📈 Linear<br/>2× load → 2× cost<br/>(the goal)"]
        S["📉 Sub-linear<br/>2× load → 1.5× cost<br/>(economies of scale — rare)"]
        X["💥 Super-linear<br/>2× load → 4× cost<br/>(the death spiral)"]
    end
```

- **Linear:** double the load, double the cost. Boring — and *excellent*. You can grow forever by writing proportionally larger cheques.
- **Sub-linear:** cost grows *slower* than load (economies of scale). Rare and wonderful.
- **Super-linear:** cost grows *faster* than load — 2× the users needs 4× the machines. This is a **death spiral**: growth becomes more expensive per user the bigger you get, until success itself bankrupts you. Most naive architectures are secretly super-linear, and don't discover it until the traffic arrives.

> 💡 **Key Insight**
>
> Scalability is not "how much can it handle?" — it's "**how does the cost of handling more grow?**" A system is scalable when load can increase and you have a *proportional, affordable* answer (add resources), not a *rewrite*. The question is never the absolute number on the machine today; it's the **slope** of the curve you're standing on. Fast tells you where you start; scalable tells you where the line goes.

### Quick Recap — What Scalability Means

- Scalability ≠ speed and ≠ "handles lots of traffic" — a fast system can be unscalable and a slow one perfectly scalable.
- It's the ability to absorb growth by **adding resources**, with cost ideally growing *proportionally* to load.
- Think of it as a **slope**: **linear** (goal), **sub-linear** (rare, economies of scale), **super-linear** (death spiral — most naive designs).
- The right question is not "how much?" but "**how does cost grow as load grows?**"

---

## 2. Load and the Dimensions of Scale

Before you can reason about handling *more* load, you have to answer a question beginners skip: **more of what, exactly?** "Load" sounds like one number. It never is — and the mistake of treating it as one is why systems get blindsided by a kind of growth they never measured.

### Load Is a Vector, Not a Scalar

A system is stressed along *many independent axes* at once. These are its **load parameters**, and which one grows determines what breaks:

| Load parameter | "More" means… | What it stresses first |
|---|---|---|
| **Request rate** (RPS/QPS) | More requests per second | Compute, throughput ceiling (Latency doc) |
| **Concurrent users/connections** | More sessions open at once | Memory, connection pools, Little's Law's *L* |
| **Data volume** | More total stored data | Storage, index size, query time |
| **Request complexity / fan-out** | Each request does more work or touches more services | Downstream capacity, the tail (Latency doc §5) |
| **Read/write ratio** | The *mix* shifts | Very different — reads and writes scale differently (§8) |
| **Payload size** | Bigger requests/responses | Bandwidth, transmission time |

The crucial consequence: **these grow independently, and a system can scale wonderfully on one axis while collapsing on another.** A system tuned for many small requests can be destroyed by a few enormous ones. A design that's fine with a billion rows can melt when concurrent *connections* spike, even if request rate is flat. "Will it scale?" is meaningless until you ask "*along which dimension?*"

### The Classic Trap — Fan-Out

The most famous example of a *hidden* load dimension, worth burning into intuition. Consider a social feed. Two operations:

- A user **posts** — write one row.
- A user **loads their feed** — read recent posts from everyone they follow.

Now an ordinary user has 200 followers; a celebrity has 50 million. When the celebrity posts, *delivering* that single post to 50 million feeds is a **fan-out** of 50 million writes from one action. The load parameter that explodes isn't "posts per second" — it's *followers per poster*, a dimension nobody thinks to put on the dashboard until a celebrity joins and the feed system falls over.

```mermaid
flowchart TD
    P["✍️ 1 celebrity posts<br/>(one action)"] --> F["📤 Fan-out:<br/>deliver to 50,000,000 feeds"]
    F --> W["💥 50M writes from 1 write<br/>— a hidden load dimension"]
```

The lesson isn't about social feeds; it's that **the dimension that kills you is usually the one you weren't measuring.** Real scalability analysis starts by *enumerating* the load parameters and asking which are growing and how fast — a direct application of the estimation discipline from *What Is System Design?* (§4).

> 💡 **Key Insight**
>
> "Scale" is multi-dimensional. Before asking whether a system scales, ask **which load parameter is growing** — request rate, data, concurrency, fan-out, or the read/write mix. Systems fail on the axis nobody instrumented. The senior habit is to name the dimensions *first*, estimate which will grow fastest, and design for *that* — not for a vague blob called "traffic."

### Quick Recap — Dimensions of Scale

- **Load is a vector**, not a scalar — request rate, concurrency, data volume, fan-out, read/write mix, payload size all grow *independently*.
- A system can scale on one dimension and **collapse on another** — "will it scale?" requires "*along which axis?*"
- **Fan-out** is the classic hidden dimension: one action causing millions of downstream operations (the celebrity-post problem).
- Real analysis starts by **enumerating and estimating** the load parameters — the killer is usually the one you didn't measure.

---

*(Sections 3–11 continue in subsequent commits.)*
