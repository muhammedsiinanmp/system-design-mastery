# What Is System Design?

> **Phase:** Foundation → **The Starting Point** → **Read time:** ~45 minutes

---

## Before You Begin

This is the **first document in the entire curriculum** — and it deliberately teaches you *nothing technical.*

That's not an accident. Before you learn how a load balancer works, how a database shards, or why the CAP theorem forces a choice, you need to understand the **game you're actually playing.** Otherwise every technique you learn is a tool with no sense of when — or why — to reach for it.

Most people rush past this. They dive straight into "learn Kafka," "learn microservices," "memorize how to design Twitter," and end up with a pile of disconnected facts. They can *name* a hundred technologies and *design* nothing, because they never learned the one thing underneath all of it:

> **System design is the discipline of making deliberate tradeoffs to build systems that meet real requirements under real constraints.**

Read that again. Not "knowing technologies." Not "drawing boxes." **Making deliberate tradeoffs.** Every chapter after this one is really just a catalog of tradeoffs — and this document is where you learn to *think in tradeoffs* in the first place.

By the end, you'll understand what system design actually is, how it differs from the coding you already know, what "good" even means for a system, and a repeatable way to approach *any* design problem — whether it's a real system at work or a whiteboard interview.

> **The mindset shift:** Programming asks *"how do I make this work?"* System design asks *"how do I make this work for millions of users, across many machines, when things fail — and what am I willing to give up to get there?"*

Welcome. Let's start with the big picture.

---

## Table of Contents

1. [What Is System Design, Really?](#1-what-is-system-design-really)
2. [Coding vs System Design — A Different Kind of Thinking](#2-coding-vs-system-design--a-different-kind-of-thinking)
3. [Requirements — The Foundation of Every Design](#3-requirements--the-foundation-of-every-design)
4. [Thinking in Scale — Back-of-the-Envelope Intuition](#4-thinking-in-scale--back-of-the-envelope-intuition)
5. [The Golden Truth — It's All Tradeoffs](#5-the-golden-truth--its-all-tradeoffs)
6. [The Qualities of a Good System](#6-the-qualities-of-a-good-system)
7. [The Building Blocks — A Map of the Toolkit](#7-the-building-blocks--a-map-of-the-toolkit)
8. [How to Approach Any System Design Problem](#8-how-to-approach-any-system-design-problem)
9. [A Walkthrough — Designing a URL Shortener](#9-a-walkthrough--designing-a-url-shortener)
10. [Final Recap](#10-final-recap)

---

## 1. What Is System Design, Really?

**System design is the process of defining the architecture, components, and data flow of a software system so that it satisfies a specific set of requirements.**

That's the textbook sentence. Here's the intuition behind it.

When you write a function, you're deciding how *one small thing* behaves. System design zooms all the way out. It asks: given a real product — say, a photo-sharing app used by fifty million people — **what are all the pieces, how do they connect, where does the data live, and how does a single user action travel through the whole thing?**

```mermaid
flowchart LR
    User["👤 User taps 'post'"] --> LB["⚖️ Load Balancer"]
    LB --> App["🖥️ App Servers"]
    App --> Cache["⚡ Cache"]
    App --> DB[("🗄️ Database")]
    App --> Queue["📨 Queue"]
    Queue --> Worker["⚙️ Background Worker"]
    App --> Store["📦 Object Storage"]
```

System design is deciding *what those boxes are, why each one exists, and how they talk to each other* — so that the whole system is fast enough, reliable enough, and cheap enough for what the business actually needs.

### It's Architecture, Not Code

An architect designing a building doesn't lay every brick. They decide how many floors, where the load-bearing walls go, how people flow through the space, and how it survives an earthquake. The *materials* (concrete, steel) matter, but the **arrangement and the tradeoffs** are the real work.

System design is exactly that, for software:

- **The components** — servers, databases, caches, queues, load balancers.
- **The connections** — how they communicate (and what happens when a connection fails).
- **The data** — where it's stored, how it's shaped, how it moves.
- **The behavior under stress** — what happens at 10× the traffic, or when a machine dies at 3 a.m.

### There Is No Single "Right" Answer

This is the part that trips up engineers coming from a coding background. A LeetCode problem has a correct answer and a test suite that proves it. **A system design problem does not.** Two senior engineers can design the same product completely differently and *both be right* — because "right" depends entirely on the requirements and constraints they're optimizing for.

> 💡 **Key Insight**
>
> System design isn't about finding *the* answer — it's about making a **defensible set of decisions** for a given context, and being able to explain *why* you chose each one and what you gave up. The skill being tested (in interviews) and used (in real work) is **reasoning**, not recall.

### Quick Recap — What System Design Is

- System design = defining the **architecture, components, and data flow** so a system meets its **requirements**.
- It's about the **whole system** and how pieces connect — not a single function.
- It's **architecture, not code** — the arrangement and the tradeoffs are the work.
- There is **no single correct answer** — only decisions that are defensible for a given context.

---

## 2. Coding vs System Design — A Different Kind of Thinking

You've almost certainly spent more time coding than designing systems, so it helps to name exactly how the two differ. They're related, but they exercise different muscles.

### The Core Difference

**Coding** lives inside one program on (usually) one machine. The world is predictable: memory is reliable, function calls always return, and there's a right answer you can test for.

**System design** lives across many machines, real networks, and real users. The world is *unpredictable*: machines fail, networks drop packets, traffic spikes 100× during a sale, and there's no test suite that says "correct."

```mermaid
flowchart TD
    subgraph Coding["💻 Coding"]
        C1["One program"]
        C2["One machine"]
        C3["Predictable world"]
        C4["A correct answer exists"]
    end
    subgraph SysDesign["🏗️ System Design"]
        S1["Many components"]
        S2["Many machines + network"]
        S3["Failure is normal"]
        S4["Only tradeoffs, no 'correct'"]
    end
```

### Side by Side

| Dimension | Coding / Algorithms | System Design |
|---|---|---|
| **Scope** | A function, a class, one program | An entire system of cooperating parts |
| **Environment** | One machine, reliable | Many machines, unreliable network |
| **Correctness** | Provable — tests pass or fail | Judgment — "good enough for the requirements" |
| **Main enemy** | Bugs and time complexity | Scale, failure, and tradeoffs |
| **Optimizes for** | Speed and correctness of code | Scalability, reliability, cost, latency |
| **The question** | "How do I make this work?" | "How does this work for millions, when things fail?" |

### You Don't Throw Coding Away

None of this means coding skills are irrelevant — they're the *foundation.* You still need to understand data structures (a hash map is why a cache is fast), complexity (why an unindexed query melts a database), and clean code (why a monolith rots without discipline). System design **builds on top of** coding; it doesn't replace it. It just adds a whole new axis of concerns that only appear once your software has to serve real people at real scale.

> 💡 **Key Insight**
>
> Coding is about making a computer do the right thing. System design is about making *many* computers keep doing a *good-enough* thing for *many* users, *even when parts of it are broken.* The moment you accept that failure and scale are the *normal* operating conditions — not edge cases — you're thinking like a systems engineer.

### Quick Recap — Coding vs System Design

- Coding = **one program, one machine, provable correctness.**
- System design = **many components, many machines, failure as the default, no single correct answer.**
- The guiding question shifts from *"how do I make this work?"* to *"how does this work at scale, under failure — and at what cost?"*
- System design **builds on** coding fundamentals; it doesn't discard them.

---

## 3. Requirements — The Foundation of Every Design

Here's a rule that separates people who *look* good at system design from people who *are* good at it:

> **You cannot design a system until you know what it must do. Every good design starts with requirements, not with technology.**

The weakest instinct — in interviews and in real projects alike — is to jump straight to solutions: "we'll use Kafka and a NoSQL database and microservices." Design *anything* before you understand the requirements and you're just guessing with buzzwords. Requirements are the target; architecture is how you hit it.

Requirements come in two flavors, and the second one matters far more than beginners expect.

### Functional Requirements — *What the System Does*

These are the features — the behaviors a user can see:

- A URL shortener must **turn a long URL into a short one** and **redirect** when someone visits it.
- A chat app must **send a message** and **deliver it** to the recipient.
- An e-commerce site must let users **browse products**, **add to cart**, and **check out**.

Functional requirements are usually the easy part — they're the obvious "what does it do?" list.

### Non-Functional Requirements — *How Well It Does It*

These describe the *qualities* the system must have while doing its job:

- **How many** users and requests? (scale)
- **How fast** must it respond? (latency)
- **How often** can it be down? (availability)
- **Can it ever lose data?** (durability)
- Must everyone see the **same data instantly**, or is a slight delay OK? (consistency)

```mermaid
flowchart TD
    Req["📋 Requirements"]
    Req --> F["✅ Functional<br/>WHAT it does<br/>(features: post, redirect, checkout)"]
    Req --> NF["⚙️ Non-Functional<br/>HOW WELL it does it<br/>(scale, latency, availability, durability)"]
    NF --> Arch["🏗️ These drive the architecture"]
```

> 💡 **Key Insight**
>
> **Non-functional requirements are what actually shape the architecture.** "Shorten a URL" (functional) is trivial — you could do it on a laptop. "Shorten a URL for **100 million users** with **<50ms redirects** and **99.99% uptime**" (non-functional) is what forces caching, replication, and global distribution. The *features* tell you what to build; the *numbers and qualities* tell you *how* to build it. Two systems with identical features and different NFRs are completely different designs.

### Ask Before You Answer

Because requirements drive everything, the *first* move in any design problem — especially an interview — is not to design. It's to **ask clarifying questions** until the problem is concrete:

- "How many users? How many requests per second?"
- "Read-heavy or write-heavy?"
- "How important is consistency vs availability here?"
- "What's the acceptable latency? Is downtime ever OK?"

An engineer who starts drawing before asking these is showing they don't understand what drives a design. An engineer who *asks first* has already demonstrated the most important system-design instinct.

### Quick Recap — Requirements

- **Requirements come before technology** — always. Never design before you know the target.
- **Functional** = what the system does (features). Usually the easy part.
- **Non-functional** = how well it does it (scale, latency, availability, durability, consistency).
- **Non-functional requirements drive the architecture** — the numbers decide the design.
- The first move on any problem is to **ask clarifying questions**, not to draw boxes.

---

## 4. Thinking in Scale — Back-of-the-Envelope Intuition

Non-functional requirements are mostly *numbers*, and numbers change designs. So a core system-design skill is being able to do rough math — **back-of-the-envelope estimation** — to turn "a lot of users" into concrete pressure on the system.

You're not looking for precision. You're looking for the **order of magnitude**, because that's what decides architecture. Ten requests per second and ten million requests per second are not the same system — and a quick estimate tells you which one you're building.

### A Simple Example

Say we're designing a service with **100 million** users, and each makes **10 requests per day** on average.

```text
100,000,000 users × 10 requests = 1,000,000,000 requests/day

1,000,000,000 / 86,400 seconds ≈ ~11,500 requests/second (average)
```

And traffic is never flat — there are peaks. A common rule of thumb is that peak load is a few times the average:

```text
Peak ≈ 2–3× average ≈ ~30,000 requests/second
```

Suddenly "100 million users" has become a concrete engineering target: **the system must handle ~30k requests/second at peak.** That single number immediately tells you a single server won't do — you'll need horizontal scaling, load balancing, and caching (all covered in Group 4).

### The Numbers That Matter

You'll estimate a handful of quantities again and again:

| Estimate | Why it matters |
|---|---|
| **Requests/second (QPS)** | Decides how many servers and how much caching you need |
| **Read : Write ratio** | Read-heavy → replicas & caches; write-heavy → sharding |
| **Storage growth** | "1M new records/day × 1KB × 365" → do we need one DB or many? |
| **Bandwidth** | Serving video vs text is a wildly different network bill |

> 💡 **Key Insight**
>
> The point of estimation isn't the exact figure — it's to reveal **where the pressure is.** A read-heavy system pushes you toward caches and replicas; a write-heavy one toward sharding; a storage-heavy one toward partitioning and cheaper storage tiers. The rough numbers tell you *which problem you're actually solving* before you pick a single technology. (Group 4 turns each of these pressures into a specific technique.)

> ⚠️ Don't over-index on perfect math. Interviewers and real designs care that you *can* reason about scale and that your numbers are in the right ballpark — not that you divided by 86,400 flawlessly. Round aggressively; think in powers of ten.

### Quick Recap — Thinking in Scale

- **Back-of-the-envelope estimation** turns vague scale ("lots of users") into concrete targets (QPS, storage, bandwidth).
- Aim for the **order of magnitude**, not precision — powers of ten decide architecture.
- Key estimates: **QPS**, **read:write ratio**, **storage growth**, **bandwidth**.
- Account for **peaks**, not just averages (peak ≈ 2–3× average is a common rule of thumb).
- The numbers reveal **where the pressure is** — and therefore which techniques you'll need.

---

## 5. The Golden Truth — It's All Tradeoffs

If you remember one idea from this entire curriculum, make it this one:

> **There is no perfect design. Every decision in system design is a tradeoff — you gain something and you pay for it somewhere else.**

This is *the* defining truth of the discipline. The reason there's no single correct answer (Section 1) is that every choice sits on a set of scales: push one down and another pops up. The expert isn't the person who avoids tradeoffs — that's impossible. The expert is the person who makes them **consciously**, in favor of what the requirements actually value.

### The "It Depends" That Isn't a Cop-Out

Ask a senior engineer almost any system design question — "SQL or NoSQL?", "cache or not?", "microservices or monolith?" — and the honest answer usually starts with **"it depends."** That's not indecision. It means: *the right choice depends on the requirements, and I need to know them before I can choose.* Learning system design is largely learning **what it depends on** for each decision.

### The Tradeoffs You'll Meet Everywhere

A few tensions show up again and again across the whole curriculum:

| You want more… | …you usually pay in |
|---|---|
| **Consistency** (everyone sees the latest data) | **Availability / latency** (coordination is slow) |
| **Low latency** (fast responses) | **Cost** (more caching, more servers, more regions) |
| **Scalability** (handle huge load) | **Complexity** (distributed systems are hard) |
| **Reliability** (never lose data / never go down) | **Cost & complexity** (replication, redundancy) |
| **Speed of development** (ship fast) | **Long-term maintainability** (shortcuts become debt) |

```mermaid
flowchart LR
    Choice["🎯 Any design decision"]
    Choice --> Gain["✅ You gain something<br/>(speed / scale / safety)"]
    Choice --> Cost["💸 You pay somewhere<br/>(cost / complexity / consistency)"]
```

You'll see these exact scales again with full depth: **consistency vs availability** in the CAP theorem (Group 5), **latency vs cost** in caching and CDNs (Group 4), **simplicity vs independence** in monolith vs microservices (Group 6). This section is just naming the pattern *before* you meet its instances.

> 💡 **Key Insight**
>
> A good system designer doesn't ask *"what's the best option?"* — they ask *"what does this specific system value most, and what can it afford to give up?"* A banking system will sacrifice availability to never show a wrong balance. A social feed will sacrifice consistency to always stay up and fast. **Same question, opposite answers — because their requirements value different things.** Naming your tradeoff out loud, and tying it to a requirement, is the single most senior-sounding thing you can do in a design discussion.

### Quick Recap — It's All Tradeoffs

- **There is no perfect design** — every decision gains something and costs something.
- **"It depends"** is the correct starting answer; learning system design = learning *what* it depends on.
- Recurring tensions: **consistency vs availability, latency vs cost, scalability vs complexity, speed vs maintainability.**
- Experts make tradeoffs **consciously**, aligned to what the requirements value most.
- Always tie a decision back to a requirement — that's what makes it defensible.

---

## 6. The Qualities of a Good System

If every design is a set of tradeoffs, then you need to know *what you're trading between.* These are the **qualities** — sometimes called the "-ilities" — that engineers evaluate every system against. They're the yardsticks. When you make a tradeoff, you're almost always trading one of these for another.

You don't need to master them now — the entire next phase of the curriculum (Phase 02) is dedicated to them. Here's the map so the vocabulary feels familiar when you meet each in depth.

```mermaid
flowchart TD
    Good["🏆 A Good System"]
    Good --> Scale["📈 Scalability"]
    Good --> Rel["🛡️ Reliability"]
    Good --> Avail["🟢 Availability"]
    Good --> Perf["⚡ Performance"]
    Good --> Maint["🔧 Maintainability"]
    Good --> Cost["💰 Cost"]
    Good --> Sec["🔒 Security"]
```

| Quality | The question it answers | Plain-English meaning |
|---|---|---|
| **Scalability** | Can it grow? | Handle 10× the load by adding resources, without falling over |
| **Reliability** | Can I trust it? | It does the right thing, and doesn't lose or corrupt data |
| **Availability** | Is it up? | It responds when users need it (measured in "nines" — 99.9%, 99.99%) |
| **Performance** | Is it fast? | Low **latency** (quick responses) and high **throughput** (lots of work/sec) |
| **Maintainability** | Can we keep changing it? | Engineers can understand, fix, and extend it without dread |
| **Cost** | Can we afford it? | Efficient use of servers, storage, bandwidth, and engineering time |
| **Security** | Is it safe? | Data is protected; only the right people can do the right things |

### A Few Distinctions Worth Locking In Early

- **Reliability vs Availability** — easy to confuse. *Availability* = the system is *up and responding*. *Reliability* = when it responds, it's *correct and doesn't lose your data*. A system can be available but unreliable (it answers, but with wrong data) — that's often *worse* than being down.
- **Latency vs Throughput** — *latency* is how long **one** request takes; *throughput* is how many requests you handle **per second**. You can improve one and hurt the other. (Full deep-dive in Phase 02.)

> 💡 **Key Insight**
>
> No system maxes out every quality — that's the tradeoff principle again. A good design **deliberately prioritizes** the two or three qualities its requirements care about most and consciously accepts less of the others. A stock-trading system obsesses over latency and reliability; an internal analytics dashboard happily trades both for lower cost. "Good" is always *relative to the requirements* — there is no universal "good system," only "good for this purpose."

### Quick Recap — Qualities of a Good System

- Systems are judged on **scalability, reliability, availability, performance, maintainability, cost, and security.**
- These "-ilities" are **what you trade between** when you make design decisions.
- **Availability** = "is it up?"; **reliability** = "is it correct and does it keep my data?" — not the same thing.
- **Latency** = time for one request; **throughput** = requests handled per second.
- A good design **prioritizes the few qualities the requirements value** and accepts less of the rest. (Phase 02 covers all of these in depth.)

---

## 7. The Building Blocks — A Map of the Toolkit

System design might feel like it has infinite concepts, but almost every system is assembled from a **small, reusable set of building blocks.** Once you know the blocks and what each one is *for*, real architectures stop looking like magic and start looking like combinations of familiar pieces.

Here's the toolkit — and, crucially, where each block gets its full treatment in this curriculum. **This section is your map of the road ahead.**

```mermaid
flowchart TD
    Client["📱 Client"] --> DNS["🌐 DNS"]
    DNS --> LB["⚖️ Load Balancer"]
    LB --> App["🖥️ App Servers"]
    App --> Cache["⚡ Cache"]
    App --> DB[("🗄️ Database")]
    App --> Queue["📨 Message Queue"]
    Queue --> Worker["⚙️ Workers"]
    App --> Blob["📦 Object Storage"]
    App --> CDN["🚀 CDN (edge)"]
```

| Building block | What it's for | Where you'll learn it |
|---|---|---|
| **Network, DNS, protocols** | How clients and servers find and talk to each other | **Group 1 — Networking** |
| **APIs (REST, gRPC, WebSockets)** | The structured contract for that communication | **Group 2 — APIs & Communication** |
| **Databases & storage** | Where data lives durably; SQL vs NoSQL, indexing | **Group 3 — Data Storage** |
| **Load balancers & app tier** | Spreading traffic across many servers | **Group 4 — Scaling** |
| **Caches & CDNs** | Serving frequent/nearby data fast to shield the database | **Group 4 — Scaling** |
| **Replication & sharding** | Copying and splitting data to scale reads, writes, and size | **Group 4 — Scaling** |
| **Queues & async messaging** | Decoupling services so they don't wait on each other | Async phase (previewed in G5/G6) |
| **Coordination & consensus** | Making many machines agree and survive failure | **Group 5 — Distributed Systems** |
| **Architecture patterns** | Arranging it all: monolith, microservices, event-driven, serverless | **Group 6 — Architecture Patterns** |

### The Pattern Behind the Blocks

Notice a theme: most blocks exist to solve one of just a few recurring problems —

- **"It's too slow / too far"** → caches, CDNs (bring data closer/faster).
- **"There's too much load"** → load balancers + more servers (spread the work).
- **"There's too much data / too many writes"** → replication, sharding (split it up).
- **"Things fail"** → redundancy, queues, coordination (survive it).

> 💡 **Key Insight**
>
> You will *never* design a system from a blank page. You assemble it from these blocks, choosing which ones you need based on the requirements and where the pressure is (Section 4). Master what each block does, what it costs, and when to reach for it, and you can design almost anything by composition. **The rest of this curriculum is a deep tour of this exact toolkit** — this table is the itinerary.

### Quick Recap — The Building Blocks

- Nearly every system is built from a **small, reusable set of blocks** — not invented from scratch.
- Core blocks: **network/DNS, APIs, databases, load balancers, caches/CDNs, replication/sharding, queues, coordination, architecture patterns.**
- Each block exists to solve a recurring problem: **too slow, too much load, too much data, or things fail.**
- Designing = **composing** the right blocks for the requirements — and this curriculum is a guided tour of every one.

---

## 8. How to Approach Any System Design Problem

Everything so far comes together into a **repeatable method.** Whether you're designing a real system at work or standing at a whiteboard in an interview, following a structured approach keeps you calm, thorough, and focused — instead of randomly drawing boxes and hoping.

Here is a framework that works for almost any problem. Follow it in order.

```mermaid
flowchart TD
    S1["1️⃣ Clarify requirements<br/>(functional + non-functional)"]
    S2["2️⃣ Estimate scale<br/>(QPS, storage, read:write)"]
    S3["3️⃣ Define the API & data model<br/>(the contract + the shapes)"]
    S4["4️⃣ Sketch the high-level design<br/>(the main boxes & flow)"]
    S5["5️⃣ Deep-dive & find bottlenecks<br/>(where does it break?)"]
    S6["6️⃣ Address failure & tradeoffs<br/>(what happens when X dies?)"]
    S1 --> S2 --> S3 --> S4 --> S5 --> S6
```

### The Six Steps

1. **Clarify the requirements.** Ask questions until the problem is concrete (Section 3). Nail down the features *and* the numbers — scale, latency, consistency needs. **Never skip this.** Everything downstream depends on it.

2. **Estimate the scale.** Do quick back-of-the-envelope math (Section 4) — QPS, read:write ratio, storage. This tells you whether you're building a one-server app or a globally distributed system, and where the pressure lies.

3. **Define the API and data model.** What are the core operations (e.g. `shorten(url)`, `redirect(code)`)? What does the data look like (the main entities and fields)? This grounds the design in concrete inputs and outputs before you draw architecture.

4. **Sketch the high-level design.** Now draw the main components and how a request flows through them — client → load balancer → app → cache/database. Keep it simple first; get an end-to-end path working on the whiteboard.

5. **Deep-dive and find the bottlenecks.** Walk through your design under the scale from step 2. *Where does it break?* The database can't handle the writes? The read path is too slow? This is where you apply the toolkit — caching, replication, sharding, queues — each to a *specific* bottleneck.

6. **Address failure and articulate tradeoffs.** Ask "what happens when this component dies?" and add redundancy where it matters. Then say out loud what you optimized for and what you gave up (Section 5). This step is what makes your design *senior*.

### Why the Order Matters

The sequence is deliberate: **requirements → scale → design → refine.** Each step feeds the next. People who struggle usually **jump to step 4** (drawing the architecture) without doing 1–3 — so their design isn't anchored to anything, and they can't defend their choices. Do the boring early steps and the impressive later ones almost write themselves.

> 💡 **Key Insight**
>
> A structured approach isn't just for passing interviews — it's how experienced engineers actually think. It turns an overwhelming, open-ended problem ("design YouTube") into a sequence of small, answerable questions. **The method is the skill.** Memorized architectures fade; the process works on any problem, including ones you've never seen.

### Quick Recap — How to Approach a Problem

- Use a **repeatable, ordered framework** instead of drawing boxes at random.
- The six steps: **clarify requirements → estimate scale → define API & data model → high-level design → deep-dive/bottlenecks → failure & tradeoffs.**
- **Requirements first, architecture later** — most failures come from skipping straight to step 4.
- Each step **feeds the next**; the boring early steps make the impressive later ones easy.
- The **method is the transferable skill** — it works on any problem, memorized or not.

---

## 9. A Walkthrough — Designing a URL Shortener

Let's make the framework concrete by lightly walking through a classic: **design a URL shortener** (like TinyURL or bit.ly). We'll stay high-level — the goal is to see the *method* in action, not to master the system. (It gets a full deep-dive in the interview phase.)

### Step 1 — Clarify Requirements

**Functional:** given a long URL, return a short one; when someone visits the short URL, redirect them to the original.
**Non-functional (the ones that shape the design):** huge scale, very **read-heavy** (people click links far more than they create them), redirects must be **fast** (<100ms), and the service must be **highly available** (a dead link is embarrassing).

### Step 2 — Estimate Scale

Say 100M new URLs/month and a **100:1 read:write ratio.**

```text
Writes: 100M / month ≈ ~40 writes/second
Reads:  100× that     ≈ ~4,000 reads/second
```

The signal is loud and clear: this is a **read-heavy** system. That one fact will dominate the design — we must make *reads* extremely fast and cheap.

### Step 3 — Define the API and Data Model

```text
POST /shorten   { long_url }          → { short_code }
GET  /{short_code}                     → 301 redirect to long_url

Data:  short_code (PK)  →  long_url
```

Dead simple: essentially a **key → value** lookup (short code → long URL).

### Step 4 — High-Level Design

```mermaid
flowchart LR
    User["👤 User"] --> LB["⚖️ Load Balancer"]
    LB --> App["🖥️ App Servers"]
    App --> Cache["⚡ Cache<br/>(hot short_codes)"]
    App --> DB[("🗄️ Database<br/>code → url")]
```

A user hits a load balancer → app servers → they look up the short code. To generate codes, we might use a counter or hash and Base62-encode it into a short string. Straightforward.

### Step 5 — Deep-Dive & Bottlenecks

Now stress it with the numbers from step 2. 4,000 reads/second all hitting the database is wasteful — and it's the same popular links over and over. **Bottleneck: read load on the database.** The fix is exactly the highest-leverage tool from the toolkit: **a cache.** Since the mapping never changes once created, it caches *perfectly* — a huge fraction of redirects can be served from memory, never touching the database. For scale and availability, we also **replicate** the database and can push popular links to a **CDN/edge.**

### Step 6 — Failure & Tradeoffs

*What if a cache node dies?* Reads fall back to the database (slower, but correct) — no data lost. *What if the database is briefly unreachable for writes?* We might reject *new* shortenings for a moment but keep *serving* existing redirects — an availability choice that fits the requirements. **The tradeoff we made:** we optimized hard for **fast, always-available reads** (caching, replication, edge) and accepted a bit more complexity and the rare stale/failed *write* — because the requirements told us reads dominate.

> 💡 **Key Insight**
>
> Notice we never guessed at technology first. The **read-heavy** discovery in step 2 drove *every* later decision — cache aggressively, replicate, serve from the edge. That's the whole discipline in miniature: **let the requirements and the numbers lead, and the architecture follows.** Change the requirements (say, write-heavy analytics instead) and the *same framework* produces a completely different design.

### Quick Recap — The Walkthrough

- The **same six-step framework** took us from a vague prompt to a defensible design.
- Step 2's **read-heavy** finding drove the whole architecture — caching, replication, edge.
- We reached for toolkit blocks (**cache, replica, CDN**) to fix **specific** bottlenecks, not at random.
- We named our **tradeoff** (optimize reads/availability, accept rare write hiccups) and tied it to the requirements.
- Method over memorization: the framework works on any problem.

---

## 10. Final Recap

| Idea | Core Insight | Why It Matters |
|---|---|---|
| **What system design is** | Defining architecture, components & data flow to meet requirements | It's about the whole system and its tradeoffs, not one function |
| **Coding vs system design** | Many machines, real failure, no single correct answer | Requires a new kind of thinking on top of coding skills |
| **Requirements first** | Functional (what) vs non-functional (how well) | Non-functional requirements are what actually shape the design |
| **Thinking in scale** | Back-of-the-envelope math reveals the real pressure | Numbers, not opinions, decide the architecture |
| **It's all tradeoffs** | Every decision gains something and costs something | "It depends" — align every choice to what the requirements value |
| **Qualities of a good system** | Scalability, reliability, availability, performance, cost, security | These are the yardsticks you trade between |
| **Building blocks** | A small reusable toolkit solves recurring problems | You compose systems from blocks, never from scratch |
| **A repeatable approach** | Clarify → estimate → API/data → design → deep-dive → failure/tradeoffs | The method is the transferable skill |

### The One Thing to Remember

> **System design is not about knowing every technology — it's about making deliberate tradeoffs to meet real requirements. Start with what the system must do and how well, let the numbers reveal the pressure, compose the right building blocks to relieve it, and always be able to say what you optimized for and what you gave up.**

---

## What's Next

> **Group 1 — Networking Foundations**

You now understand the *game*: what system design is, why it's all tradeoffs, what "good" means, the toolkit you'll compose from, and a method to approach any problem. That's the mental model. Everything from here builds the **depth** to fill it in.

The natural place to start is at the very bottom of the stack — **how machines actually talk to each other.** Before you can reason about load balancers, APIs, or distributed databases, you need to understand the network they all run on: clients and servers, IP and DNS, TCP vs UDP, HTTP, and the round trips that quietly set the speed limit on everything above them.

The journey from here:

```text
You are here → What Is System Design?
      ↓
Group 1 — Networking Foundations   (how machines talk)
Group 2 — APIs & Communication     (how that talk is structured)
Group 3 — Data Storage             (where data lives)
Group 4 — Scaling                  (growing past one machine)
Group 5 — Distributed Systems      (the hard truths of many machines)
Group 6 — Architecture Patterns    (arranging it all into a whole)
```

You've built the foundation for the foundation. Now let's go learn how the pieces actually work — starting with the network.

---

