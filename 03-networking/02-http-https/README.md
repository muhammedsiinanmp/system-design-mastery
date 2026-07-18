# HTTP & HTTPS

> **Phase:** Networking Deep Dives → **Topic:** 2 of 7 → **Read time:** ~60 minutes

---

## Before You Begin

**This document stands alone.** Unlike its neighbours, it assumes you have read nothing else — not the foundation series, not the phase before it, not the topic before it. Everything about HTTP and HTTPS is built here from zero: the message format, the methods, the status codes, statelessness, caching, all three protocol versions, TLS, and certificates. If you know only that "websites use HTTP" and that the `s` means something about security, you are exactly the reader this was written for.

Two consequences of that choice, stated up front so the shape of the document makes sense:

- **Terms get defined where they're used**, even ones a systems engineer would consider obvious — round trip, latency percentile, single point of failure. Skim past what you already know.
- **Neighbouring topics are named, not taught.** REST API design, idempotency keys, TCP's internals, reverse proxies, load balancers, and CDN strategy each have their own full treatment elsewhere in this curriculum. Where they touch HTTP, this document says so and points; it doesn't absorb them. *HTTP and HTTPS themselves are complete here.*

HTTP also appears as one of the six concepts in the **Top 30 Must-Know Concepts** foundation series, where it gets a short introduction. This is that concept's deep-dive.

Here is the question the document answers:

> **What actually happens between "your browser has an address" and "the page appears" — and why has the industry rewritten that answer three times in thirty years?**

Here's the trap it disarms. HTTP looks like the easy part of the stack. It's human-readable, its errors are famous enough to be jokes, and every engineer has typed a `200` and a `404` into a codebase. That familiarity produces a false model: **HTTP as a format** — a text shape with a verb, a path, and a number in it. If HTTP were a format, there would be nothing to say, and it certainly wouldn't have needed three major revisions.

The truth is that HTTP is where a request's real cost is decided. Not the format — the **conversation**: how many times the client and server must talk before useful data moves, whether a connection is reused or rebuilt, whether one slow response blocks nine fast ones, and what encryption adds to all of it. Two systems can speak identical HTTP and differ by a factor of ten in how long a page takes to appear.

> **The mindset shift:** stop reading HTTP as *a format* and start reading it as *a negotiation with a price*. Every version of HTTP — 1.1, 2, 3 — is an attack on the same enemy: **round trips**, the unavoidable there-and-back delay of talking to a machine far away. And every guarantee you add on top — encryption, identity, integrity — is paid for in that same currency, *before* your server does a single useful thing. Learn to count the round trips and you can predict a system's speed without measuring it.

---

## Table of Contents

1. [What HTTP Actually Is](#1-what-http-actually-is)
2. [Statelessness — and How the Web Fakes State](#2-statelessness--and-how-the-web-fakes-state)
3. [HTTP Caching](#3-http-caching)
4. [The Connection Underneath](#4-the-connection-underneath)
5. [HTTP/1.1 and Head-of-Line Blocking](#5-http11-and-head-of-line-blocking)
6. [HTTP/2 — Multiplexing, and the Blocking It Didn't Fix](#6-http2--multiplexing-and-the-blocking-it-didnt-fix)
7. [HTTP/3 and QUIC — Abandoning TCP](#7-http3-and-quic--abandoning-tcp)
8. [HTTPS — What TLS Guarantees, and What It Costs](#8-https--what-tls-guarantees-and-what-it-costs)
9. [Certificates — Chain of Trust and the Expiry Trap](#9-certificates--chain-of-trust-and-the-expiry-trap)
10. [Putting It All Together — A Commerce Team Goes HTTPS-Only](#10-putting-it-all-together--a-commerce-team-goes-https-only)
11. [Final Recap](#11-final-recap)
