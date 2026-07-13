# Availability

> **Phase:** Core System Properties → **Topic:** 2 of 5 → **Read time:** ~50 minutes

---

## Before You Begin

The previous document taught you to measure *speed* — how long one request takes, how many the system handles, and how to state both with precision (percentiles, load, conditions). It ended on a promise: once you can describe performance precisely, you can *promise* it — and formalized promises are called **SLOs**. This document is where that thread gets pulled all the way through.

But first, a more primitive question than "how fast?" — one that has to be answered before speed even matters:

> **Is the system there at all?**

That sounds binary and obvious. It is neither. By the end of this document you'll see that "up" is a spectrum, not a switch; that a system answering every request in 30 seconds may be worse than one that's cleanly *offline*; and that the single most quoted reliability metric in the industry — "the nines" — hides more than it reveals until you know exactly what's being counted.

You already have the pieces you need. Group 5 taught you that distributed systems fail **partially** — not all-or-nothing, but one node here, one dependency there. Group 4 taught you **redundancy** — running more than one of everything. This document fuses them into a single measurable property and gives you the vocabulary teams actually use to argue about it: SLI, SLO, SLA, error budgets, and the availability math that decides how many nines you can honestly claim.

Here's the trap this document exists to disarm. "Is it up?" feels like a yes/no question a monitoring dashboard can answer. But *up for whom?* The user in another region seeing timeouts, while your dashboard is green? *Up doing what?* Serving the homepage but failing every checkout? *Up over what window?* 100% this second, but down for two hours last Tuesday? Every one of those is an availability question, and "yes, it's up" answers none of them.

> **The mindset shift:** stop asking *"is it up?"* — start asking *"available **to whom**, measured **how**, over **what window** — and is **degraded** the same as **down**?"* Availability is not a light switch. It's a *ratio*, over a *window*, against a *definition of working* you had to choose.

---

## Table of Contents

1. [What "Available" Actually Means](#1-what-available-actually-means)
2. [The Nines — Availability as a Number](#2-the-nines--availability-as-a-number)
3. [What Counts as Down? — Defining the SLI](#3-what-counts-as-down--defining-the-sli)
4. [SLI · SLO · SLA — The Vocabulary of Promises](#4-sli--slo--sla--the-vocabulary-of-promises)
5. [Error Budgets — Spending Unreliability Wisely](#5-error-budgets--spending-unreliability-wisely)
6. [The Math of Availability — Serial vs Parallel](#6-the-math-of-availability--serial-vs-parallel)
7. [Redundancy and Failover — Buying Nines](#7-redundancy-and-failover--buying-nines)
8. [The Cost of Nines — Diminishing Returns](#8-the-cost-of-nines--diminishing-returns)
9. [Production Reasoning — Windows, Correlation, and Blast Radius](#9-production-reasoning--windows-correlation-and-blast-radius)
10. [Putting It All Together — Brimble Sets an SLO](#10-putting-it-all-together--brimble-sets-an-slo)
11. [Final Recap](#11-final-recap)

---

## 1. What "Available" Actually Means

Start with the definition most people carry, then break it — because it's wrong in a way that matters.

**The naive definition:** "available" = "the server is running." The process is up, the port answers, the health check is green. Done.

**The problem:** none of that is what a *user* means by available. A user calls the system available when it **does useful work for them, at the moment they need it.** The server being alive is necessary but nowhere near sufficient. Consider all the ways a "running" system is unavailable to a real person:

- The process is up, but every request times out after 30 seconds (overloaded — remember the utilization curve from the latency doc).
- The homepage loads, but checkout returns 500 for everyone.
- It works perfectly — in the US datacenter, while the entire EU is cut off by a network partition.
- It returns *instantly* — the wrong data, a cached error, a "try again later" page.

In each case a naive health check says 🟢 and the user says "it's down." That gap — between *the system thinks it's fine* and *the user cannot do the thing* — is where availability actually lives.

> **Availability** is the probability that the system can successfully do what a user asks, **when** they ask it. It is measured from the user's side of the request, not the server's.

### Up Is a Spectrum

The deepest reframing in this whole topic: **"up" is not binary.** Between "perfect" and "totally offline" lies a wide band of *degraded* states, and a mature engineer thinks in that band, not at its endpoints:

```mermaid
flowchart LR
    A["🟢 Fully working<br/>fast + correct"] --> B["🟡 Degraded<br/>slow, or some<br/>features off"]
    B --> C["🟠 Partially down<br/>some users /<br/>regions failing"]
    C --> D["🔴 Fully down<br/>nothing works"]
```

This spectrum is *good news for engineers*, and it's the thread that runs through this entire document. If availability were binary, your only defense against failure would be "never fail" — impossible. Because it's a spectrum, you have a vastly richer toolkit: when something breaks, you can **degrade instead of collapse** — turn off the recommendations panel but keep checkout alive, serve slightly stale data instead of an error, drop to read-only instead of fully down. Group 5 called this *graceful degradation*; here you can see *why* it's possible at all — because "available" has a middle.

> 💡 **Key Insight**
>
> The question is never just "is it up?" — it's "**how much** of it is up, **for whom**, doing **what**?" Systems rarely die all at once; they *degrade*. Teams that only instrument "up/down" are blind to the entire middle of the spectrum — which is exactly where most real incidents live, and where the cheapest wins are found.

### Availability vs Its Cousins

Three words get used as if they're synonyms. This phase separates them, one document each — keep the distinction straight from the start:

| Property | The question it answers |
|---|---|
| **Availability** (this doc) | Is it **there and responding** usefully when I need it? |
| **Reliability** (next doc) | Does it do the **correct** thing, consistently, over time? |
| **Fault tolerance** (Group 5) | Can it **keep working when a part fails**? |

They're related but not the same: a system can be *available* but unreliable (always answers, sometimes wrong), or *reliable* but unavailable (always correct when it answers, but often down). This document is strictly about the first — being **there**. The next one takes on being **right**.

### Quick Recap — What Available Means

- Availability is measured from the **user's side**: can they do the thing, when they ask? "Server running" is not the same as "available."
- **"Up" is a spectrum**, not a binary — fully working → degraded → partially down → fully down.
- The spectrum is what makes **graceful degradation** possible: degrade instead of collapse.
- Availability (*there?*) is distinct from reliability (*correct?*) and fault tolerance (*survives a part failing?*).

---

## 2. The Nines — Availability as a Number

You cannot manage what you cannot measure, so availability gets turned into a number: the fraction of time (or of requests) the system was working, over some window.

```text
              uptime                        good requests
Availability = ───────────────────   or    ─────────────
              uptime + downtime             total requests
```

Expressed as a percentage, it's almost always very close to 100% — so the interesting information is in the *nines* after the decimal point. "Three nines" means 99.9%. And the single most important skill in this section is translating an abstract percentage into **concrete allowed downtime**, because that's where the number stops sounding impressive and starts sounding like an on-call schedule.

### The Table Worth Memorizing

| Availability | "Nines" | Downtime / year | Downtime / month | Downtime / day |
|---|---|---|---|---|
| 99% | two nines | ~3.65 days | ~7.2 hours | ~14 min |
| 99.9% | three nines | ~8.76 hours | ~43 min | ~1.4 min |
| 99.95% | | ~4.38 hours | ~22 min | ~43 s |
| 99.99% | four nines | ~52.6 min | ~4.3 min | ~8.6 s |
| 99.999% | five nines | ~5.26 min | ~26 s | ~0.86 s |

Read that table slowly, because it reshapes intuition. **99.9% sounds excellent** — and it allows *nearly nine hours of downtime a year*. **99.99%** — one more nine — cuts that to under an hour. **Five nines** ("carrier grade") leaves you **five minutes for the entire year** — which means no human can be in the recovery loop; a single bad deploy or a five-minute cloud blip blows the whole annual budget. Each nine you add cuts allowed downtime by **10×** — a fact Section 8 turns into a statement about *cost*.

```mermaid
flowchart LR
    N2["99%<br/>3.65 days/yr"] -->|"×10 less downtime"| N3["99.9%<br/>8.8 hrs/yr"]
    N3 -->|"×10"| N4["99.99%<br/>53 min/yr"]
    N4 -->|"×10"| N5["99.999%<br/>5 min/yr"]
```

### More Nines Is Not "Better" — It's a Choice

The beginner instinct is that five nines is the goal and everything else is settling. **Wrong**, and expensively so. More nines is not a quality ranking; it's a *requirements decision* with a steep price (doc 00's tradeoff thinking, applied to uptime):

- A **payment or emergency system** may genuinely need four or five nines — an outage means lost money or lost lives.
- An **internal analytics dashboard** at 99.9% (or even 99%) is completely fine — nobody is harmed if it's down for an hour during a quiet weekend, and the money to make it five-nines would be pure waste.

The right number is set by **what a minute of downtime actually costs** *this* system's users — not by how impressive the number looks in a slide. Section 8 makes the economics explicit; for now, internalize that chasing nines you don't need is one of the most common and costly over-engineering mistakes there is.

> ⚠️ **A nines figure with no window and no definition is marketing, not engineering.** "We're 99.99% available" means almost nothing until you know: measured over what window (a good year can hide a catastrophic month), counting what as "down" (all requests? checkout only?), and for whom (globally? per region?). The next two sections make those the *first* questions you ask — before you believe any availability number, including your own.

### Quick Recap — The Nines

- Availability = uptime ÷ total time (or good ÷ total requests) — the useful information is in the **nines**.
- Translate nines to **downtime**: 99.9% ≈ 8.8 hrs/year, 99.99% ≈ 53 min/year, 99.999% ≈ 5 min/year.
- Each added nine cuts allowed downtime **10×** — and (Section 8) costs roughly 10× more.
- **More nines isn't "better"** — the target is a requirements decision set by the cost of downtime, not a quality score.
- A nines number is meaningless without its **window**, **definition of down**, and **audience**.

---

*(Sections 3–11 continue in subsequent commits.)*
