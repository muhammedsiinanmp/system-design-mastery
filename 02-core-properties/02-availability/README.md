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

## 3. What Counts as Down? — Defining the SLI

Section 2 handed you a formula with a term quietly hiding all the difficulty: *good* requests, or *up*time. Who decides what "good" and "up" mean? This is the hardest and most-skipped question in the whole topic — and getting it wrong makes every nine you report a fiction.

### The Measurement Problem

Imagine your service returns a response in **28 seconds**. Was that request "available"? Technically it succeeded — status 200, correct data. But the user gave up at second 4 and left. Or: a request returns instantly with `200 OK` and a body that says `{"error": "temporarily unavailable"}`. Status code says up; the user got nothing. Or: half your servers are serving fine and half are returning 503 — are you "up"?

There is no universe-given answer. **You have to define it** — and the definition is an engineering decision with real consequences. This is why the industry invented a precise term for "the thing we actually measure":

> **SLI — Service Level Indicator:** a specific, quantitative measurement of one aspect of the service's behavior. It is the *definition of "working"*, made concrete enough to compute.

### Slow Is a Kind of Down

Here the previous document pays off directly. That 28-second response is the bridge: **latency and availability are not separate concerns — past some threshold, slow simply *is* down.** A response nobody waits for is functionally a failure, whatever its status code. So mature availability SLIs almost always fold latency in:

> *"A request is **good** if it returns a non-error status **within 2 seconds**."*

That single sentence quietly unifies the two properties. A request that's correct but takes 30 seconds fails the SLI — counted as unavailable, exactly as the user experienced it. This is why the latency doc insisted you nail down percentiles and thresholds first: **your availability number is built on top of a latency threshold you chose.** Change "2 seconds" to "10 seconds" and your availability improves without a single line of code changing — which should make you suspicious of any availability figure whose latency threshold you don't know.

### Three Common SLI Shapes

Most availability SLIs are one of these, and picking among them is itself a decision:

| SLI type | "Good" means | Best when |
|---|---|---|
| **Availability (success rate)** | Non-5xx response | The basic "did it work?" signal |
| **Latency** | Response within threshold (e.g. P99 < 2s) | Slow = down; user-facing paths |
| **Quality / correctness** | Full response, not a degraded fallback | You serve partial results under stress (§1's spectrum) |

The third one is subtle and senior: if under load you drop the recommendations panel to keep checkout alive, is that request "good"? Checkout worked — but the user got a lesser experience. Whether you count degraded responses as available is a *product* judgment, and writing it into the SLI forces you to make it on purpose rather than by accident.

### Whose Availability? Request vs System vs Feature

"Available" needs a subject. Three different subjects give three very different numbers from the same incident:

```mermaid
flowchart TD
    I["🔥 Checkout is failing<br/>everything else fine"] --> R["Request availability<br/>99.2% (checkout reqs failing)"]
    I --> F["Feature availability<br/>Checkout: DOWN<br/>Browse: UP"]
    I --> S["System availability<br/>'up' — most endpoints fine"]
```

A dashboard reporting **system** availability can show a reassuring 99.95% while your **checkout feature** — the one that makes money — is completely down for an hour. This is why aggregate, system-wide availability is often a *comforting lie*: it averages your critical path together with your health-check endpoint. Senior teams measure availability **per critical user journey** (checkout, login, search), not as one blended site-wide number, because the blend hides exactly the failures that matter most.

> 💡 **Key Insight**
>
> Before you can improve availability, you must *define* it — and the definition is where the real decisions hide. What status counts as failure, what latency counts as down, whether degraded counts as up, and *which* user journey you're measuring: change any of those and the number moves without the system changing at all. An availability figure is only as honest as the SLI beneath it.

### Quick Recap — Defining the SLI

- An **SLI** is the concrete, computable *definition of "working"* — you must choose it; the universe won't.
- **Slow is a kind of down**: good availability SLIs fold in a latency threshold (the latency doc, cashed in).
- Common SLI shapes: **success rate**, **latency**, and **quality/correctness** (does degraded count as good?).
- Availability has a **subject** — request vs feature vs system — and system-wide numbers hide dead critical paths. Measure **per user journey**.

---

## 4. SLI · SLO · SLA — The Vocabulary of Promises

You now have the *measurement* (the SLI). Turning a measurement into a managed property takes two more terms — and the three together are the single most useful vocabulary in this document. They form a ladder: **measure → target → promise.**

```mermaid
flowchart LR
    SLI["📏 SLI<br/>what we measure<br/>'% of reqs < 2s'"] --> SLO["🎯 SLO<br/>the target<br/>'≥ 99.9% over 28 days'"]
    SLO --> SLA["📜 SLA<br/>the contract<br/>'≥ 99.5% or you get<br/>a refund'"]
```

| Term | Full name | What it is | Audience |
|---|---|---|---|
| **SLI** | Service Level *Indicator* | The metric — what you actually measure (§3) | Internal (engineers) |
| **SLO** | Service Level *Objective* | The **target** for that metric — the line between "fine" and "not fine" | Internal (the team's goal) |
| **SLA** | Service Level *Agreement* | A **contract** with customers, with **consequences** (refunds, credits) if breached | External (legal/commercial) |

### The Distinctions That Matter

**SLI → SLO** is measurement → goal. The SLI says "99.94% of requests were good over the last 28 days"; the SLO says "we promise ourselves ≥ 99.9%." The SLO is the *decision about how good is good enough* — and, as the next section shows, it's the thing that governs how the team behaves day to day.

**SLO → SLA** is goal → contract, and the gap between them is deliberate and important:

> ⚠️ **Your SLA should always be *looser* than your SLO.** You promise customers 99.5% (SLA) while targeting 99.9% internally (SLO). Why the gap? Because the SLA has *teeth* — money changes hands when you miss it — so you build in a safety margin. The SLO is your early-warning line; you want to be alerting and scrambling (SLO breached) *long before* you're paying refunds (SLA breached). A team whose SLA equals its SLO has no margin between "we're worried" and "we owe money."

Two more practical truths:

- **Not everything needs an SLA.** SLAs are commercial instruments — you write them for paying customers who demand guarantees. Internal services and free tiers often have SLOs (targets the team holds itself to) with no SLA at all.
- **100% is never the target.** No SLO is ever 100%, and no SLA promises it, because 100% is both impossible and — as the next section argues — *undesirable*. This is where availability stops being an aspiration ("stay up!") and becomes a managed budget.

> 💡 **Key Insight**
>
> SLI, SLO, SLA are **measure → target → promise**, aimed at three different audiences. The most common mistakes are conflating the target with the contract (leaving no safety margin before penalties) and writing an SLA for something that never needed one. Get the ladder straight and most availability conversations suddenly have precise words to happen in.

### Quick Recap — SLI · SLO · SLA

- **SLI** = the metric you measure; **SLO** = the internal target for it; **SLA** = the external contract with consequences.
- Keep the **SLA looser than the SLO** — the gap is your safety margin between "worried" and "paying refunds."
- **Not every service needs an SLA**; many have SLOs only.
- **No SLO is 100%** — which turns availability from an aspiration into a *budget* (next section).

---

*(Sections 5–11 continue in subsequent commits.)*
