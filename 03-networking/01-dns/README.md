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
