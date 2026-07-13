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

## 5. Error Budgets — Spending Unreliability Wisely

Section 4 ended on a claim that sounds almost heretical: **100% availability is not the goal.** This section is why — and it contains the single most behavior-changing idea in the whole topic. It's the concept that turns availability from a vague virtue ("try not to break things") into a *currency teams actively spend*.

### Why 100% Is the Wrong Target

Three independent reasons, each sufficient on its own:

1. **It's impossible.** Hardware fails, networks partition, dependencies go down, deploys go wrong. Physics and other people's systems guarantee you cannot hit 100%.
2. **The user can't tell.** If the user's own network, phone, or ISP is 99.9% reliable, the difference between your 99.99% and your 100% is *invisible to them* — it's drowned out by everything between your servers and their eyes. Paying to eliminate failures no user can perceive is spending real money for zero delivered value.
3. **It would freeze the system.** The only way to approach 100% is to *never change anything* — no deploys, no new features, no experiments. But shipping change is the entire point of a product. **Perfect availability and progress are in direct conflict.**

That third reason is the important one, and it reframes everything:

> 💡 **Key Insight**
>
> The tension isn't "availability vs. laziness" — it's **availability vs. velocity.** Every deploy, migration, and feature risks availability; refusing to ship protects availability but kills the product. So the real question is never "how do we never fail?" It's "**how much failure can we afford** — and how do we spend it on the changes worth making?" That budget has a name.

### The Error Budget

If your SLO is 99.9%, you are *promising* 99.9% — which means you are explicitly declaring the other **0.1% is allowed to fail.** That 0.1% is not a shameful accident to drive to zero. It's a **resource you are permitted to spend.**

> **Error budget = 100% − SLO.** It is the amount of unreliability you've *pre-approved* for the window — a currency the team gets to spend on risk.

For a 99.9% monthly SLO, the budget is 0.1% of the month ≈ **43 minutes** of allowed downtime. That 43 minutes is *yours to allocate*:

```mermaid
flowchart LR
    B["💰 Error budget<br/>0.1% ≈ 43 min/month"] --> D["🚀 Risky deploys<br/>& migrations"]
    B --> E["🧪 Experiments<br/>& new features"]
    B --> F["🔧 Planned maintenance"]
    B --> U["💥 Unplanned incidents"]
```

### How a Budget Changes Behavior

The magic is what an error budget does to the age-old fight between the team that wants to *ship* and the team that wants *stability*. Instead of a values argument ("move fast!" vs. "be careful!"), it becomes a **data question about the remaining balance** — and that resolves the classic tension the way few things in engineering do:

- **Budget healthy (lots left):** ship aggressively, take risks, run experiments, push deploys. You're being *too* conservative if you're not spending it — unused reliability budget is shipped features you didn't build.
- **Budget spent (SLO breached):** the calculus flips automatically. Feature work pauses; the team's priority becomes reliability — fix the fragility, add redundancy, improve testing — until the budget refills over the next window.

This is the mechanism famously formalized by Google's SRE practice: the error budget makes "should we ship this risky change?" an objective decision instead of a personality clash. Reliability and velocity stop being enemies and become two sides of one account.

### Burn Rate — Reading the Budget in Real Time

One refinement makes budgets operational: you watch not just *how much* is left but *how fast it's draining* — the **burn rate**. Spending your monthly budget evenly is fine; spending half of it in ten minutes is an emergency in progress. Burn-rate alerts fire on the *slope*, not just the level: "at this rate you'll exhaust the month's budget in 45 minutes" pages someone *now*, while there's still budget left to protect — the same early-warning philosophy the latency doc applied to P99.

> ⚠️ **An unspent error budget is not a trophy — it's a signal.** A team that ends every month at 100% availability isn't winning; it's very likely shipping too slowly and being too cautious. The budget exists to be *spent* on progress. Consistently leaving it untouched means your SLO is probably too lax, or your team is leaving product velocity on the table out of misplaced fear.

### Quick Recap — Error Budgets

- **100% is the wrong target**: impossible, imperceptible to users, and only reachable by freezing all change.
- The real tradeoff is **availability vs. velocity** — every change risks uptime, but not changing kills the product.
- **Error budget = 100% − SLO** — pre-approved unreliability, a *currency* to spend on deploys, experiments, and risk.
- It turns ship-vs-stability from a values fight into a **balance check**: spend freely when healthy, freeze features when exhausted.
- Watch **burn rate** (the slope) for early warning; a chronically *unspent* budget means you're shipping too cautiously.

---

## 6. The Math of Availability — Serial vs Parallel

Time for the result that reorganizes how you see every architecture diagram. Availability *composes* — the availability of a whole system is a function of its parts' availabilities — and it composes in two opposite directions depending on whether parts are arranged **in series** or **in parallel.** This is the mathematical heart of the topic.

### Series — Dependencies Multiply (and It's Brutal)

When a request must pass through several components and **every one must work**, they're in *series*. The system works only if component A **and** B **and** C all work — and probabilities of independent "and" conditions **multiply**:

```text
A_total = A_1 × A_2 × A_3 × … × A_n
```

Multiplying numbers below 1 always gives something *smaller than any of them.* A chain is **less available than its weakest link** — and far less available than intuition expects. Watch how fast it decays even with excellent parts:

```mermaid
flowchart LR
    U["👤"] --> LB["LB<br/>99.99%"] --> API["API<br/>99.95%"] --> Auth["Auth<br/>99.95%"] --> DB["DB<br/>99.9%"] --> Pay["Payments<br/>99.9%"]
```

| Services in series (each 99.9%) | Combined availability | Downtime / year |
|---|---|---|
| 1 | 99.9% | ~8.8 hrs |
| 5 | 99.5% | ~1.8 days |
| 10 | 99.0% | ~3.6 days |
| 30 | 97.0% | ~11 days |
| 50 | 95.1% | ~18 days |

Thirty "three-nines" services in a chain produce a **97%** system — barely two nines. This is one of the most important and least intuitive facts in system design, and it explains a defining pain of microservices (Group 6): decomposing a monolith into 30 services means a single user request may now traverse 30 independently-failing hops, and their availabilities *multiply downward*. **You cannot build a highly-available system by chaining many mediocre parts** — the math forbids it.

> ⚠️ **Every dependency you add to the critical path drags total availability *down*, multiplicatively.** Before adding a synchronous call to another service into a request, ask: does this belong on the critical path at all? Each hop there spends availability you can't easily get back. This is a core reason to push non-essential work *off* the request path and into async processing (Group 6) — work that isn't in the chain can't lower the chain's availability.

### Parallel — Redundancy Multiplies the *Failures*

Now the opposite arrangement — and the only escape from the series problem. When you run **redundant copies** and the system works if **any one** of them works, they're in *parallel*. Here it's easier to reason about *failure*: the system is down only if **all** copies are down simultaneously, and those failure probabilities multiply:

```text
Unavailability_total = (1 − A) ^ n
A_total = 1 − (1 − A) ^ n
```

Because unavailabilities are small numbers below 1, multiplying them makes them *tiny* — redundancy adds nines fast:

| Redundant copies (each 99%) | Combined availability | Downtime / year |
|---|---|---|
| 1 | 99% | ~3.65 days |
| 2 | 99.99% | ~53 min |
| 3 | 99.9999% | ~32 s |

Two 99% components in parallel yield **99.99%** — the same jump that costs a fortune to buy inside a single component (Section 8) comes almost free from a second cheap copy. This is *why* redundancy is the universal availability tool: series drags you down, parallel lifts you back up, and real systems are a constant interplay of both.

```mermaid
flowchart TD
    U["👤 Request"] --> LB["⚖️ Load balancer"]
    LB --> S1["Server A · 99%"]
    LB --> S2["Server B · 99%"]
    LB --> S3["Server C · 99%"]
    S1 & S2 & S3 --> R["System up if ANY works<br/>→ 99.9999%"]
```

> 💡 **Key Insight**
>
> Availability composes in two directions: **series multiplies availabilities** (every dependency drags the total *down* — a chain is weaker than its weakest link), while **parallel multiplies failure probabilities** (every redundant copy lifts the total *up*, fast). Reading any architecture, your eye should now split it instinctually into "what's in series here (risk stacking up) and what's in parallel (risk cancelling out)?"

### Quick Recap — Serial vs Parallel

- **Series (all must work):** availabilities *multiply* → total is **below the weakest link**; 30 × 99.9% ≈ 97%.
- Every **critical-path dependency** lowers availability multiplicatively — keep non-essential work off the request path.
- **Parallel (any can work):** *unavailabilities* multiply → redundancy adds nines cheaply; 2 × 99% ≈ 99.99%.
- Real systems interleave both — train your eye to see which parts stack risk and which cancel it.

---

## 7. Redundancy and Failover — Buying Nines

Section 6 proved *that* parallelism buys availability. This section is the *mechanism* — how redundancy actually works in practice, and the costs the clean math hides. (True to the Phase 02 charter, this is the intuition, not a build guide — the deep mechanics live in the Scaling and Distributed Systems phases.)

### Redundancy Needs a Switch

A spare copy is useless unless traffic can actually move to it when the primary dies. Redundancy therefore always has two parts: **replicas** (the spare capacity) and **failover** (the mechanism that detects failure and redirects). The two dominant arrangements:

| Model | How it works | Tradeoff |
|---|---|---|
| **Active–Passive** (standby) | One live node serves; a standby waits, ready to take over | Simpler, but the standby is idle capacity you pay for and rarely test |
| **Active–Active** | All nodes serve traffic simultaneously; losing one just sheds load onto the rest | Full use of capacity + instant failover, but harder — state, balancing, consistency |

```mermaid
flowchart LR
    subgraph AP["Active–Passive"]
        LB1["LB"] --> P1["🟢 Active"]
        LB1 -. "on failure" .-> S1["⚪ Standby"]
    end
    subgraph AA["Active–Active"]
        LB2["LB"] --> A1["🟢 Node 1"]
        LB2 --> A2["🟢 Node 2"]
        LB2 --> A3["🟢 Node 3"]
    end
```

### Failover Time Is Its Own Downtime

Here's what Section 6's tidy formula quietly ignored: **failover is not instant.** Between the primary failing and the replica serving, there's a gap — detect the failure (health checks must notice), promote the standby, reroute traffic, warm caches and connection pools (cold-start, from the latency doc). That gap is *real downtime*, and it caps the availability redundancy can actually deliver:

- Failover in **milliseconds** (active-active behind a load balancer): the math nearly holds.
- Failover in **minutes** (detect + promote a database replica): you've *reduced* downtime, not eliminated it — and if failover is flaky or needs a human, your real availability is far below what the parallel formula promised.

> ⚠️ **Untested failover is not redundancy — it's a hope.** The standby that has never actually taken traffic, the replica promotion nobody has rehearsed, the "automatic" failover that silently broke three deploys ago — these routinely fail at the exact moment they're needed, turning your paper 99.99% into a real outage. This is why teams practice failure on purpose (chaos engineering, from Group 5): the only redundancy that counts is the kind you've *watched* work.

### The Ceiling: Correlated Failure and SPOF

The parallel formula assumes failures are **independent** — that's what lets you multiply them. Reality rarely cooperates, and this is the crack that Section 9 widens: two servers in the *same rack* share a power supply; two replicas in the *same datacenter* share a network and a cooling system; two services sharing *one config system* fail together when it does. When copies fail *together*, the `(1−A)ⁿ` math evaporates — you weren't running `n` independent copies, you were running one copy with `n` faces.

The extreme case has a name you'll meet as a full topic soon: a **Single Point of Failure (SPOF)** — a single component with no redundancy whose failure takes the whole system down, no matter how much redundancy surrounds it. The load balancer in front of your beautifully redundant server fleet, if there's only one of it, is a SPOF that caps the entire system at *its* availability. Finding and eliminating SPOFs is Topic 5 of this phase; for now, note that **redundancy only helps where failures are genuinely independent** — and making them independent (spreading across racks, zones, regions, providers) is most of the actual work.

> 💡 **Key Insight**
>
> Redundancy buys nines only to the degree that failures are *independent* and failover is *fast and tested*. The clean `1−(1−A)ⁿ` is an **upper bound** you approach but never reach — eroded by failover time, correlated failure, and the SPOFs hiding in shared infrastructure. Diminishing returns set in hard: going from one copy to two is transformative; from three to four often buys almost nothing, because by then correlated failure, not lack of copies, is your real ceiling.

### Quick Recap — Redundancy and Failover

- Redundancy = **replicas + failover**; the switch matters as much as the spare.
- **Active-passive** (simple, idle standby) vs **active-active** (efficient, instant failover, harder).
- **Failover time is downtime** — a slow, flaky, or human-in-the-loop switch undercuts the parallel-availability math.
- The formula assumes **independent** failures; **correlated failure** and **SPOFs** (shared racks/zones/configs) are the real ceiling — and the reason returns diminish fast past two copies.

---

*(Sections 8–11 continue in subsequent commits.)*
