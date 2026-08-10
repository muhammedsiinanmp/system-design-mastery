# Rate Limiting

> **Phase:** APIs & Communication Deep Dives → **Topic:** 12 of 15 → **Read time:** ~48 minutes

---

## Before You Begin

**This document stands alone.** It assumes you have read nothing else — not the foundation series, not the topics before it. It builds rate limiting from zero: why a shared resource has to protect itself from any single caller, what a "rate" even means once you look closely, the handful of algorithms that enforce one and how they differ, what to do with the requests you turn away, and the genuinely hard part — enforcing a single limit across a whole fleet of machines at once.

Two consequences of that choice:

- **Terms get defined where they're used** — rate, burst, fixed window, sliding window, token bucket, leaky bucket, `429`, fail-open. Skim what you know.
- **Neighbouring topics are named, not taught.** Rate limiting is often *performed* at a single front door (an API gateway) and is easily confused with its cousins (load shedding, backpressure, autoscaling). Where this document reaches them it names them and their destination, so it can stay on what's genuinely rate limiting's own.

Rate limiting appears in the **Top 30 Must-Know Concepts** foundation series. This is the deep-dive on how it actually works.

Here is the question the document answers:

> **A service has finite capacity, and it's shared by everyone who calls it — so one client that calls too much, whether by a bug, a scraper, or an attack, can consume the capacity meant for everyone else. How do you decide, for each individual request in the instant it arrives, whether a caller has already had more than its fair share — and why is that decision so much subtler than "count the requests and block over a number"?**

Here's the trap it disarms. Rate limiting looks like the simplest thing in this phase: keep a counter per caller, and when it passes a limit, start rejecting. That picture hides the whole subject. A raw count means nothing until you say *over what span of time* — and the instant you pin that down, you're forced into real choices. Do you allow the short bursts that real users legitimately make, or reject them? Can an attacker slip through at the edge of your time window? How much memory does tracking every caller cost? And when your limiter isn't one machine but fifty, how do they agree on a single count without talking to each other on every request? "A counter with a cap" answers none of these; the algorithms exist because each answers them differently.

> **The mindset shift:** stop thinking of a rate limit as *a counter that trips at a number* and start thinking of it as **a policy about how many requests are allowed per unit of time, for each caller** — where the unit of time is the hidden variable everything hard flows from. Once you see that a limit is fundamentally a statement about *time*, the rest of the subject falls into place: each algorithm is a different way of measuring time, the burst question is about how forgiving that measurement is, and the distributed problem is about many clocks and counters trying to agree. And underneath it all is one real job — telling a legitimate burst apart from sustained abuse — which is, again, a question about time.

---

## Table of Contents

1. [Why Limit — Protecting a Shared Resource](#1-why-limit--protecting-a-shared-resource)
2. [A Rate Is a Statement About Time](#2-a-rate-is-a-statement-about-time)
3. [Fixed Window — The Simple Counter and Its Flaw](#3-fixed-window--the-simple-counter-and-its-flaw)
4. [Sliding Window — Smoothing the Boundary](#4-sliding-window--smoothing-the-boundary)
5. [Token Bucket — Rate and Burst, Separated](#5-token-bucket--rate-and-burst-separated)
6. [Leaky Bucket — Smoothing the Output](#6-leaky-bucket--smoothing-the-output)
7. [What Happens When You Say No](#7-what-happens-when-you-say-no)
8. [Limiting Across Many Machines](#8-limiting-across-many-machines)
9. [Designing a Real Policy — and What It Isn't](#9-designing-a-real-policy--and-what-it-isnt)
10. [Putting It All Together — A Public API Platform](#10-putting-it-all-together--a-public-api-platform)
11. [Final Recap](#11-final-recap)

---

## 1. Why Limit — Protecting a Shared Resource

Before any algorithm, understand the problem rate limiting exists to solve, because the whole design follows from it. The problem is a consequence of one fact: a service has finite capacity, and that capacity is *shared*.

### One Caller Can Consume Everyone's Share

A running service can only do so much at once — so many requests per second, so much CPU, so many database connections, so much of a paid downstream it's billed for. That capacity is a common pool drawn from by every caller. And a common pool has a failure mode: **nothing stops a single caller from taking all of it.** When one client sends far more than its share, the pool empties, and *every other caller* is starved — slow responses, timeouts, errors — not because they did anything wrong, but because someone else drank the well dry. This is the "noisy neighbour," and it doesn't require malice to happen.

The excess traffic comes from several directions, and a system has to survive all of them:

- **A bug.** A client stuck in a loop, or a retry with no backoff, hammers the service thousands of times a second by accident. (Ironically, naive retries turn one struggling service into a self-inflicted flood.)
- **A scraper or greedy integrator.** A caller pulling far more data, far faster, than intended — not attacking, just inconsiderate.
- **An attack.** A deliberate flood meant to exhaust capacity and deny service to everyone else, or a credential-stuffing script trying millions of logins.
- **Runaway cost.** Even if capacity holds, each call may cost real money (a metered downstream, compute, bandwidth); unbounded calls mean an unbounded bill.

### The Limit Is a Fairness and Safety Boundary

Rate limiting is the mechanism that says: **no single caller may consume more than its allotted share of the pool.** That one rule buys three things at once:

- **Fairness** — capacity is divided among callers so one can't starve the rest.
- **Protection** — the service is shielded from being overwhelmed, whether by accident or attack, so it stays up for everyone.
- **Cost control** — usage has a ceiling, so a bug or an abuser can't run up an unbounded bill.

```mermaid
flowchart TD
    subgraph NO["🔴 No limit"]
        A1["🐛 buggy client<br/>(floods)"] --> P1["finite capacity"]
        B1["🙂 normal clients"] -.->|"starved"| P1
    end
    subgraph YES["🟢 Rate limited"]
        A2["🐛 buggy client<br/>(capped)"] --> P2["finite capacity"]
        B2["🙂 normal clients<br/>(get their share)"] --> P2
    end
```

### It's Not the Same as Load Shedding

One distinction to draw at the outset, because the two get conflated. Rate limiting is about **per-caller fairness**: each *individual* caller is held to its own share, all the time, whether or not the system is under stress. A related but different technique, **load shedding**, is about **system-wide survival**: when the whole system is overloaded regardless of who's responsible, it starts dropping *some* work — often the least important — to stay alive. Rate limiting asks "has *this caller* had its share?"; load shedding asks "is *the system as a whole* drowning?" They complement each other and often run together, but they answer different questions, and load shedding is its own subject in a later phase. This document is about the per-caller question.

> 💡 **Key Insight**
>
> A service's capacity is **finite and shared**, and a shared pool has one fatal flaw: nothing inherently stops a single caller from draining it and starving everyone else — by bug, by greed, or by attack. Rate limiting is the rule that no caller may take more than its share, and it buys **fairness** (one client can't starve the rest), **protection** (the service survives floods, accidental or hostile), and **cost control** (usage has a ceiling). It is distinct from **load shedding**, which drops work to save an overloaded *system* regardless of who caused it — rate limiting asks whether *this caller* has had its share, not whether the whole system is drowning.

### Quick Recap — Why Limit

- A service's capacity is **finite and shared**, so without a limit a single caller — buggy, greedy, or hostile — can consume it all and **starve everyone else** (the noisy neighbour).
- Excess traffic comes from **bugs, scrapers, attacks, and runaway cost**, and a system must survive all of them, not just the malicious ones.
- Rate limiting caps each caller's share, buying **fairness, protection, and cost control** in a single rule.
- It is **not load shedding**: rate limiting enforces *per-caller* fairness always, while load shedding drops work to save an *overloaded system* — different questions, often used together.

---

## 2. A Rate Is a Statement About Time

Everyone writes limits like "100 requests per minute" and imagines the meaning is obvious. It isn't — and seeing exactly *why* it's ambiguous is the key that unlocks every algorithm in this document. The ambiguity is about time, and resolving it is the whole game.

### "100 Per Minute" Doesn't Say What You Think

Take "100 requests per minute" literally and ask: *which* minute? Two very different behaviours both satisfy the phrase:

- A caller sends 100 requests spread evenly — a bit under two per second, all minute long. Clearly fine.
- A caller sends all 100 in the first half-second and nothing for the rest of the minute. Also "100 per minute" — but it just hit the service with a spike 100× denser than the first caller.

Both obey the same words and stress the system completely differently. The phrase "100 per minute" fixes a *count* but leaves the *shape over time* undefined — and the shape is what actually determines whether the service can cope. A limit isn't real until you decide how you measure the passage of that minute, and that decision is precisely what separates one algorithm from another. **Every rate-limiting algorithm is a different answer to "how do we measure the time in 'per minute'?"**

### Two Things a Limit Really Encodes: Rate and Burst

The example reveals that a good limit has to control *two* separate quantities, not one:

- **The sustained rate** — how fast a caller may go *on average, over the long run*. This protects the steady-state capacity: 100/minute means that, held up over many minutes, a caller averages no more than that.
- **The burst** — how much a caller may do *in a short spike* before the average catches up. Real traffic is bursty: a user opens an app and it fires ten requests at once, then goes quiet. A limit that forbids all bursts would reject normal behaviour; a limit that allows unlimited bursts protects nothing.

The art is allowing a *reasonable* burst while holding the *sustained* rate — and the algorithms differ mainly in how cleanly they let you express those two knobs. The ones that conflate them (a single window) are cruder; the one that separates them explicitly (the token bucket) is why it's the default.

```mermaid
flowchart LR
    L["'100 per minute'"] --> R["📏 sustained rate<br/>avg over the long run"]
    L --> B["💥 burst<br/>how much at once"]
    R --> A["algorithms differ in how<br/>they measure time to enforce both"]
    B --> A
```

### A Limit Is Always Per-Something

One more thing every limit needs before it means anything: a **key** — the *per-what*. You never limit "requests" in the abstract; you limit requests *per caller*, and you must choose what "caller" means:

- **Per user or per account** — fair across people, and the usual choice for a logged-in product.
- **Per API key** — the standard for a public API, where a key identifies the integrator (and often their paid tier).
- **Per IP address** — the fallback when there's no identity yet (an anonymous or login endpoint), though imperfect: many users can share one IP (behind a corporate network), and one attacker can spread across many IPs.

The key is half the policy, because it decides *what gets its own share*. A limit keyed on IP protects differently from one keyed on account, and choosing the wrong key can either punish innocents (many users behind one IP) or fail to contain an abuser (one account, many IPs). Identifying the caller reliably is an authentication concern of its own; here the point is that a rate limit is always *rate per key per unit of time* — three parts, and the sections that follow are about the third.

> 💡 **Key Insight**
>
> "100 per minute" is ambiguous because it fixes a **count** but not the **shape over time** — 100 spread evenly and 100 in a half-second both satisfy it while stressing the service utterly differently. So a real limit must control **two** things: a **sustained rate** (the long-run average) and a **burst** (how much at once), because real traffic is bursty and both "no bursts" and "unlimited bursts" are wrong. And a limit is always **per a key** — per user, per API key, per IP — which decides *what gets its own share* and is half the policy. Every algorithm ahead is a different way of measuring time to enforce rate-and-burst, per key.

### Quick Recap — A Rate Is About Time

- "100 per minute" fixes a **count** but not the **shape over time**; 100 evenly and 100 in a half-second both satisfy it yet stress the service completely differently.
- A real limit controls **two** things: a **sustained rate** (long-run average) and a **burst** (how much at once) — since real traffic is bursty, both forbidding and unbounding bursts are wrong.
- A limit is always **per a key** (user, API key, or IP) — the *per-what* decides what gets its own share and is half the policy; IP is the imperfect fallback when there's no identity.
- **Every algorithm is a different answer to "how do we measure the time"** in a rate — which is why choosing one is choosing how you treat bursts and boundaries.

---

## 3. Fixed Window — The Simple Counter and Its Flaw

The most obvious way to measure "per minute" is to chop time into fixed minute-long blocks by the clock and count within each. This is the **fixed-window** algorithm, and it's worth studying precisely because it's the one people invent by default — and because its one flaw teaches what all the later algorithms are fixing.

### How It Works

Divide time into fixed windows aligned to the clock — say, each calendar minute (12:00:00–12:00:59, then 12:01:00–12:01:59, and so on). For each key, keep one **counter** for the current window. Every request increments it; if the counter is at or below the limit, allow the request; if it's over, reject. When the clock ticks into the next window, the counter **resets to zero.**

That's the entire algorithm, and its appeal is obvious: it's almost nothing to build. One integer per caller, an increment, a compare, and a reset on the minute. It's cheap in memory (a single number per key) and trivially fast. For many low-stakes limits it's perfectly adequate, and its simplicity is a real virtue.

### The Boundary Burst

The flaw is subtle and shows up exactly at the seam between windows. Because the counter resets abruptly at the window boundary, a caller can spend its *entire* allowance at the very end of one window and its *entire* allowance again at the very start of the next — and those two bursts are only a moment apart.

Concretely, with a limit of 100 per minute: a caller sends 100 requests at 12:00:59.5, then 100 more at 12:01:00.5. Each window's counter saw only 100, so nothing was rejected — but the service just took **200 requests in one second**, twice the limit, in the span that straddles the boundary. Over any *aligned* minute the rule held; over the *real* 60-second window around the boundary, the caller did double.

```mermaid
flowchart LR
    subgraph W1["window 12:00 (limit 100)"]
        A["...quiet... then 100 @ :59.5"]
    end
    subgraph W2["window 12:01 (limit 100)"]
        B["100 @ :00.5 ...then quiet"]
    end
    A -->|"~1 second apart"| B
    B --> C["💥 200 requests in 1s<br/>— 2× the limit slipped through"]
```

This isn't a rare corner case an attacker has to work for — it's a predictable doubling available at every boundary, and a caller aiming to maximize throughput will simply align to it. The root cause is that the fixed window has **no memory across the reset**: the moment the clock ticks, it forgets everything that just happened, so the burst on one side is invisible to the other.

### What It Teaches

The fixed window fails because it measures time in *abrupt, aligned chunks* and resets with a hard edge. Everything that follows is a way of softening that edge — remembering across the boundary (the sliding window, §4) or replacing the "reset" with a smooth, continuous refill (the token bucket, §5). Hold onto the flaw: it's the concrete problem the next two sections exist to solve.

> ⚠️ **The fixed window is the cheapest algorithm and the one with the trap everyone hits: because its counter resets abruptly at each clock boundary, it has no memory across the reset — so a caller can spend a full allowance just before the boundary and a full allowance just after, pushing 2× the limit through in a moment while every aligned window still reads "within limit."** It's fine for loose, low-stakes limits where a transient double doesn't matter, but it does not truly hold a rate. The later algorithms are, at heart, ways of removing that hard edge.

### Quick Recap — Fixed Window

- **Fixed window** chops time into clock-aligned blocks (e.g. each minute), keeps **one counter per key**, allows up to the limit, and **resets to zero** at each boundary.
- It's the **cheapest** algorithm — one integer per caller, an increment and a compare — and adequate for loose, low-stakes limits.
- Its flaw is the **boundary burst**: with no memory across the reset, a caller can spend a full allowance just before *and* just after a boundary, pushing **up to 2× the limit** through in an instant.
- The lesson driving the rest of the topic: a hard, aligned reset doesn't truly hold a rate — later algorithms **soften the edge** by remembering across it or refilling smoothly.

---

## 4. Sliding Window — Smoothing the Boundary

The fixed window's flaw (§3) was the hard reset: it measures a *clock-aligned* minute and forgets everything at the boundary. The **sliding-window** family fixes this by measuring the minute *relative to now* — always looking back over the last 60 seconds from the current instant, so there's no boundary to exploit. There are two ways to do it, trading accuracy against cost.

### Sliding-Window Log — Exact, but Heavy

The precise version keeps, for each key, a **log of the timestamp of every request**. To decide a new request, you count how many timestamps fall within the last window (say, the last 60 seconds), discard any older than that, and allow the request only if the count is under the limit.

This is exactly correct: the window truly slides with each request, so there's no boundary to game — 100 in any rolling 60-second span is 100, full stop. The cost is the log: you store a timestamp for *every* request from *every* caller within the window, and busy callers mean large logs and real memory and processing per request. It's accurate but it scales poorly, which is why it's often not what runs in production at high volume.

### Sliding-Window Counter — A Cheap, Good-Enough Approximation

The practical version keeps the fixed window's cheapness but borrows just enough from the previous window to smooth the seam. You keep two counters — the **current** window's and the **previous** window's — and estimate the rolling count by *weighting* the previous window by how much of it still overlaps the rolling window.

Concretely: if you're 25% of the way into the current minute, then the last 60 seconds is 25% of the current window plus the last 75% of the previous one. So the estimate is `current_count + previous_count × 75%`. As the current window fills, the previous window's weight fades smoothly toward zero. That single weighted number approximates the true rolling count closely, kills the boundary burst (the previous window's requests still count, weighted, just after the reset), and costs only *two* integers per key instead of a full log.

```mermaid
flowchart LR
    subgraph SW["Sliding-window counter (25% into current minute)"]
        P["previous window<br/>count × 75%"] --> E["estimate ="]
        C["current window<br/>count × 100%"] --> E
        E --> D["compare to limit"]
    end
```

The approximation assumes traffic within a window is spread evenly, so it can be slightly off under very lumpy traffic — but in practice it's close enough that the sliding-window counter is one of the most widely used real-world algorithms: nearly as cheap as a fixed window, without the boundary hole.

### The Tradeoff It Illustrates

The two variants bracket a tradeoff you'll see throughout: **accuracy costs state.** The log is exact and expensive; the counter is approximate and cheap. Most systems choose the cheap approximation because "very close, for two integers" beats "exact, for an unbounded log" at scale — a recurring theme in rate limiting, where good-enough-and-cheap usually wins over perfect-and-heavy.

> 💡 **Key Insight**
>
> The sliding window fixes the fixed window's boundary burst by measuring the last N seconds **relative to now** rather than in clock-aligned chunks, so there's no seam to exploit. The **log** variant stores every request's timestamp — exactly correct but memory-heavy, scaling with traffic. The **counter** variant keeps just the current and previous window counts and **weights the previous one by its remaining overlap** (`current + previous × overlap%`) — killing the boundary burst for the cost of two integers, at the price of a mild even-traffic assumption. It illustrates the recurring rate-limiting tradeoff: **accuracy costs state**, and the cheap approximation usually wins.

### Quick Recap — Sliding Window

- The sliding window measures the last N seconds **relative to now**, not in clock-aligned blocks, so the §3 boundary burst has no seam to exploit.
- The **log** variant stores every request's timestamp — **exactly correct but memory-heavy**, scaling with traffic per caller.
- The **counter** variant weights the previous window by its remaining overlap (`current + previous × overlap%`) — **cheap (two integers) and close enough**, and one of the most widely used real algorithms.
- It illustrates the recurring tradeoff — **accuracy costs state** — and most systems pick the cheap approximation over the exact, heavy log.

---
