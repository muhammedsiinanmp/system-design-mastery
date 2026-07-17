# DNS — The Domain Name System

> **Phase:** Networking Deep Dives → **Topic:** 1 of 7 → **Read time:** ~50 minutes

---

## Before You Begin

This is the **first** deep-dive of Phase 03, and it starts where Foundations §3 stopped. You already know the shape: DNS turns `github.com` into `140.82.121.4`, it's a cached hierarchy (resolver → root → TLD → authoritative), most lookups return in single-digit milliseconds, and every answer carries a **TTL**. None of that gets re-taught here. This document assumes it and goes underneath it, to answer one question:

> **What is DNS actually — as a *system* — and why does the thing in front of every request you will ever make behave so unlike the lookup you think it is?**

Because DNS is not a lookup. It's a **globally distributed, hierarchically delegated, aggressively cached, eventually consistent database** that happens to answer questions about names. Every one of those five words is a source of surprise, and every surprise shows up in production as an outage, a slow failover, or a migration that "should have been instant" and wasn't.

You've already met the consequences of that, scattered across four earlier documents, without meeting the cause:

- The Scaling doc pointed at **DNS-level balancing** in front of your load balancers (Scaling §5) and promised the mechanism would come later. It comes here (§6).
- The SPOF doc listed **DNS** as the archetypal *hidden* SPOF — "it just works," until nobody can find you however healthy your servers are (SPOF §4) — and called the resolution root **irreducible** (SPOF §7). Both are settled here (§8).
- The Distributed Systems doc used **DNS as its worked example of an AP system** — the canonical case of "up ≫ perfectly correct." That's not a curiosity; it's the reason half this document exists (§1, §7).
- Foundations §3 warned that **"just update DNS" is never instant**. §7 explains why the word everyone uses for it — *propagation* — describes something that does not happen.

One scoping note. This is DNS the *system*: how it resolves, caches, steers, and fails. The neighbors get their own documents and appear here only as **named pointers**: load balancer mechanics and algorithms are §05–§06 of this phase, TLS and certificates are §02, CDN and edge strategy are Phase 06, and internal service discovery — "DNS for your own services," promised by Architecture Patterns — is Phase 09.

Here's the trap this document disarms. DNS is the one piece of infrastructure engineers believe they already understand, because they've *used* it — they've edited a record, waited, and watched it work. That familiarity is the danger. It teaches you DNS as a control panel you type into, and hides the fact that you are writing to a database with **millions of independent replicas you do not own, cannot enumerate, and cannot invalidate**. You don't control DNS. You make suggestions to it, with an expiry date.

> **The mindset shift:** stop thinking of DNS as *a lookup that returns an address* — start thinking of it as *a globally replicated cache you can write to but never invalidate*. Every hard DNS problem — slow failover, migrations that drag for days, a provider outage that takes your healthy servers offline, traffic that ignores your steering — comes from that one sentence. You are not changing what a name means; you are **waiting for the world to forget what it used to mean.**

---

## Table of Contents

1. [What DNS Actually Is — Beyond the Phonebook](#1-what-dns-actually-is--beyond-the-phonebook)
2. [The Resolution Path](#2-the-resolution-path)
3. [Caching, TTL, and the Layers](#3-caching-ttl-and-the-layers)
4. [The Record Types That Matter](#4-the-record-types-that-matter)
5. [DNS as a Latency Cost](#5-dns-as-a-latency-cost)
6. [DNS as Traffic Control](#6-dns-as-traffic-control)
7. [Propagation Is a Myth](#7-propagation-is-a-myth)
8. [DNS as a SPOF](#8-dns-as-a-spof)
9. [How DNS Fails](#9-how-dns-fails)
10. [Putting It All Together — Brimble's DNS Migration](#10-putting-it-all-together--brimbles-dns-migration)
11. [Final Recap](#11-final-recap)

---

## 1. What DNS Actually Is — Beyond the Phonebook

Foundations §3 called DNS "the phone book of the internet." That analogy is a good on-ramp and a bad model, and the gap between them is this section.

A phone book is **one book**. It's complete — every listing is in it. It's **static** — printed once, identical for everyone holding a copy. And it's **consistent** — your copy and mine agree, because they're the same edition.

DNS is none of those things. Nothing about it is one book.

> **DNS is a globally distributed, hierarchically delegated, aggressively cached, eventually consistent database.**

Five words, five surprises. Take them one at a time, because the rest of this document is just their consequences.

### Nobody Has the Whole Database

This is the part the phonebook analogy actively conceals. There is no complete copy of DNS anywhere on Earth. No server holds "the mapping." The root nameservers — the top of the hierarchy, the thing everything starts at — **do not know** what `github.com` resolves to. They have never known. They cannot tell you.

What the root knows is one thing: *who to ask about `.com`*. And the `.com` TLD servers don't know `github.com`'s address either — they know *who to ask about `github.com`*. Only at the bottom, at GitHub's own **authoritative** nameservers, does an actual answer exist.

That's **delegation**, and it's the organizing principle of the entire system:

```mermaid
flowchart TD
    Root["🌐 Root<br/>knows: who runs .com<br/>does NOT know github.com"]
    TLD["🌐 .com TLD<br/>knows: who runs github.com<br/>does NOT know its IP"]
    Auth["🟢 github.com authoritative<br/>knows: the actual answer<br/>140.82.121.4"]
    Root -->|"ask them"| TLD
    TLD -->|"ask them"| Auth
    Auth -->|"here it is"| Ans["✅ the only real answer<br/>in the whole chain"]
```

Each level knows only **one level down**, and knows it as a *referral*, not an answer. The database isn't distributed in the sense of "copied around." It's distributed in the sense of **nobody is in charge of more than their own slice** — which is exactly why DNS scales to every name on the internet without any organization needing to hold the whole thing, and exactly why *authority* is the concept that matters (§4's `NS` and `SOA` records are how delegation is written down).

### It Is Eventually Consistent — and That's the Whole Story

The Distributed Systems doc already told you this, and it's worth quoting the frame it used: DNS is its worked example of an **AP system** (Dist §4) — availability and partition tolerance, chosen over consistency. "Up ≫ perfectly correct."

Sit with what that means. When you change a DNS record, there is a window — often hours — where **the internet disagrees with itself** about what your name means. One user's resolver has the new answer. Another's has the old one. Both are behaving correctly. Neither is broken. There is no mechanism to reconcile them faster, because there is no mechanism to *reach* them at all.

This isn't a flaw in DNS. It's the trade DNS deliberately made, and it bought something enormous: DNS keeps answering during partitions, outages, and provider failures, because caches everywhere hold answers that are *probably still good*. Strong consistency would mean checking with authority on every lookup — which would make DNS slow (§5), fragile (§8), and dependent on the authoritative server being reachable by everyone, always.

DNS chose to be *always up and sometimes stale*. Every frustration in this document is the bill for that choice.

> 💡 **Key Insight**
>
> The phonebook analogy fails because a phonebook is complete, static, and consistent — and DNS is **partial** (nobody holds the whole database, only referrals), **dynamic** (answers change under you), and **eventually consistent** (the world disagrees for a while, on purpose). Every DNS problem you will ever debug lives in one of those three gaps. You're not querying a directory; you're asking millions of independent caches what they last heard, and hoping they heard it recently.

### Quick Recap — What DNS Actually Is

- DNS is a **distributed, delegated, cached, eventually consistent database** — not a lookup table and not a phone book.
- **Nobody holds the whole database.** The root doesn't know your IP; it knows who to ask. Each level stores *referrals*, and only the authoritative server at the bottom holds a real answer.
- It's the canonical **AP system** (Dist §4): always answering, sometimes stale — a deliberate trade, not a bug.
- That trade is the source of **every** hard DNS problem: slow failover, dragging migrations, and steering that clients ignore (§6, §7).

---

## 2. The Resolution Path

Foundations §3 drew the walk: browser → recursive resolver → root → TLD → authoritative. That picture is correct and incomplete in one important way — it doesn't say **who does the work**. That's this section, because it's where the labor is unevenly divided in a way that explains the caching layers (§3) and the latency (§5).

### Two Kinds of Query, and Almost Everyone Does the Lazy One

There are two ways to ask a DNS question, and the difference is *who chases the referrals*:

| | **Recursive query** | **Iterative query** |
|---|---|---|
| The ask | "Give me the final answer. I'll wait." | "Tell me what you know — a referral is fine." |
| Who chases referrals | The server you asked | **You** — the asker |
| Who does it | Your device → its resolver | The resolver → root, TLD, authoritative |
| Round trips for the asker | **One** | As many as the chain is deep |

Your laptop runs a **stub resolver** — a deliberately minimal client that knows how to do exactly one thing: ask a configured recursive resolver a *recursive* question and wait for a complete answer. It does not walk the hierarchy. It has no idea the hierarchy exists.

The **recursive resolver** (your ISP's, or a public one like `8.8.8.8`) is where the real work happens. It accepts the recursive question, then turns around and asks a series of **iterative** questions — root, then TLD, then authoritative — chasing each referral itself:

```mermaid
flowchart LR
    Stub["👤 Stub resolver<br/>(your OS)<br/>asks ONE question"]
    Rec["⚙️ Recursive resolver<br/>does ALL the walking"]
    Stub -->|"recursive:<br/>'final answer please'"| Rec
    Rec -->|"iterative: .com?"| Root["🌐 Root"]
    Root -.->|"referral"| Rec
    Rec -->|"iterative: github.com?"| TLD["🌐 .com TLD"]
    TLD -.->|"referral"| Rec
    Rec -->|"iterative: A record?"| Auth["🟢 Authoritative"]
    Auth -.->|"the answer"| Rec
    Rec -->|"140.82.121.4"| Stub
```

The asymmetry is the point. **One** query leaves your machine; **three or more** leave the resolver. This is why the resolver's cache is the most valuable cache in the system (§3) — it absorbs the entire walk on behalf of every client it serves, and there may be millions of them.

### The Chicken-and-Egg Problem, and Glue

Here's a puzzle the referral model creates. The `.com` servers answer "ask `ns1.github.com`" — a **name**. But to contact `ns1.github.com`, you need its IP. So you look up `ns1.github.com`… which is a `.com` domain… whose nameserver is `ns1.github.com`. You need the answer to get the answer.

DNS breaks the loop with **glue records**: when a TLD hands back a referral to a nameserver that lives *inside the zone being delegated*, it attaches that nameserver's IP address directly to the referral. Not because it's authoritative for it — it isn't — but because the resolution is otherwise impossible. Glue is the system admitting that pure delegation has a bootstrap problem and patching it with a hint.

### The Root Is Not Thirteen Machines

The hierarchy has exactly **13 root server addresses** — a number fixed by an old packet-size constraint — and this fact routinely misleads people into thinking the internet's naming layer rests on thirteen computers. It doesn't. Those 13 *addresses* are served by **hundreds of physical servers** across the globe using **anycast**: many machines announce the same IP, and the network routes you to the topologically nearest one.

This matters for §8. "The root" sounds like a catastrophic SPOF, and structurally it is a single logical entity — but anycast means the failure of any given root instance is invisible; traffic simply routes to another. It's the clearest example in this document of the SPOF doc's distinction (SPOF §1): critical, yes — but *not alone*, and therefore not a SPOF.

> 💡 **Key Insight**
>
> The labor is deliberately lopsided: your device asks **one** recursive question and waits; the resolver does **all** the iterative walking. That's why the resolver — not your browser, not the authoritative server — is the load-bearing cache of the entire system, and why a resolver outage (§9) feels like DNS itself is down. You never talk to the root. You have almost certainly never sent a packet to a root server in your life; your resolver did it for you, and probably not recently, because the answer was cached.

### Quick Recap — The Resolution Path

- **Recursive query** = "give me the final answer" (what your device asks). **Iterative query** = "a referral is fine" (what the resolver asks everyone else).
- Your **stub resolver** is deliberately dumb — one question, one wait. The **recursive resolver** does all the real walking and absorbs it for millions of clients.
- **Glue records** solve the bootstrap loop when a zone's nameserver lives inside the zone it serves.
- The **13 root addresses** are hundreds of machines behind **anycast** — critical, but not alone, and therefore not a SPOF (SPOF §1).
