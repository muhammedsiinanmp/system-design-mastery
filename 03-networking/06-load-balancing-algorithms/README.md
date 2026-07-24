# Load Balancing Algorithms

> **Phase:** Networking Deep Dives → **Topic:** 6 of 7 → **Read time:** ~50 minutes

---

## Before You Begin

**This document stands alone.** It assumes you have read nothing else — not the foundation series, not the phase before it, not the topics before it. Everything is built here from zero: what the selection decision actually is, each algorithm that makes it, the assumption each one hides, and what happens to each when that assumption breaks.

Two consequences of that choice:

- **Terms get defined where they're used** — pool, upstream, stateless and stateful selection, rehashing. Skim past what you already know.
- **Neighbouring topics are named, not taught.** How a server comes to be added or removed, how the balancer knows a server is alive, consistent hashing's internals, and autoscaling each have their own full treatment elsewhere in this curriculum. Where they touch the selection decision, this document says so and points; it doesn't absorb them. *The algorithms themselves are complete here.*

Load balancing is one of the concepts in the **Top 30 Must-Know Concepts** foundation series, where it gets a short introduction. This document is the deep-dive on the one decision at its heart: given several servers that could all answer, which one gets the request.

Here is the question the document answers:

> **When any of several servers could handle a request, what rule decides — and why does the "obvious" rule quietly ruin performance for most real workloads?**

Here's the trap it disarms. The selection algorithm looks like the whole substance of load balancing, and it's the part most people give the least thought to. Every reference offers the same four names — round-robin, least-connections, weighted, hashing — a sentence each, presented as interchangeable defaults you pick between by taste. So teams take the default, it works in testing, and they never think about it again.

Then a latency tail appears that no dashboard explains, or an incident makes one server melt while its neighbours sit idle, and the cause turns out to be the selection rule doing exactly what it was designed to do — under conditions where its central assumption had quietly stopped being true.

> **The mindset shift:** stop asking *"which algorithm spreads requests most evenly?"* and start asking **"what does this algorithm assume, and what happens the moment that assumption is false?"** Every balancing algorithm is a bet about the world: that all requests cost roughly the same, that a server's connection count reflects its real load, that a server which answers is a server that works. On an ordinary day every bet pays off and the algorithms are genuinely hard to tell apart. The choice only becomes visible when a bet loses — and that is precisely the moment, under load or during failure, when you can least afford to have bet wrong.

---

## Table of Contents

1. [The Decision, Isolated](#1-the-decision-isolated)
2. [Round-Robin — Rotation and Its One Assumption](#2-round-robin--rotation-and-its-one-assumption)
3. [Weighted — When Servers Aren't Equal](#3-weighted--when-servers-arent-equal)
4. [Least-Connections — Reacting to Real State](#4-least-connections--reacting-to-real-state)
5. [The Trouble With Counting Connections](#5-the-trouble-with-counting-connections)
6. [Random and the Power of Two Choices](#6-random-and-the-power-of-two-choices)
7. [Hashing — Sending the Same Key to the Same Server](#7-hashing--sending-the-same-key-to-the-same-server)
8. [When the Pool Changes Size](#8-when-the-pool-changes-size)
9. [Choosing — There Is No Default](#9-choosing--there-is-no-default)
10. [Putting It All Together — The Algorithm That Wasn't the Problem](#10-putting-it-all-together--the-algorithm-that-wasnt-the-problem)
11. [Final Recap](#11-final-recap)
