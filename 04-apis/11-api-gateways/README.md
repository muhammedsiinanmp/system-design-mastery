# API Gateways

> **Phase:** APIs & Communication Deep Dives → **Topic:** 11 of 15 → **Read time:** ~48 minutes

---

## Before You Begin

**This document stands alone.** It assumes you have read nothing else — not the foundation series, not the topics before it. It builds the API gateway from zero: why a fleet of services behind a public boundary all need the same handful of things done to every request, why those things want one home rather than a copy in each service, and — the part that matters most — why concentrating them into a single front door is at once the gateway's whole value and its whole danger.

Two consequences of that choice:

- **Terms get defined where they're used** — API gateway, routing, cross-cutting concern, TLS termination, protocol translation, aggregation, Backend-for-Frontend. Skim what you know.
- **Neighbouring topics are named, not taught.** A gateway *performs* jobs that are subjects in their own right — rate limiting, authentication, the reverse proxy it's built on, the load balancer it's often confused with, the gRPC it may translate to. Where this document reaches them, it points rather than teaches, so it can stay on what's genuinely the gateway's own.

The API gateway sits alongside the **Top 30 Must-Know Concepts** foundation series as the piece of infrastructure that makes a fleet of services usable from the outside. This is the deep-dive on what it is and what it costs.

Here is the question the document answers:

> **Behind a public API there is rarely one program — there's a fleet of services, each of which would otherwise have to authenticate callers, enforce limits, terminate encryption, and log traffic before doing any real work. Where should all that shared work live, who should the outside world actually talk to — and why does putting it all in one place solve the problem and create a new one in the same move?**

Here's the trap it disarms. A gateway gets filed as "a reverse proxy with a fancier name" — a box that forwards requests to the right server, nothing more. That framing misses what makes it a gateway. A plain reverse proxy forwards by *position* — this host, that path — and doesn't care what the request means. A gateway reads all the way up to the *API*: who the caller is, which quota they fall under, which several services a single request should fan out across, how to reshape the answer. It's not a smarter router; it's the tier where the public contract is deliberately held apart from the internal fleet, and where everything true of *every* request gets done once.

> **The mindset shift:** stop picturing a gateway as *a router sitting in front of your services* and start picturing it as **the boundary tier that owns everything true of every request** — identity, limits, encryption, observability, shaping, routing — so that no service behind it re-implements any of it. Hold that and the gateway's power and its peril turn out to be a single fact: a door that owns everything is a door everything depends on. Centralizing the shared work is exactly why the services behind it stay simple and consistent — and exactly why that one door is a chokepoint, a bottleneck, and a magnet for logic that was never supposed to live there. Learn to see the one door as both the answer and the risk, and the rest of this document is the two sides of that coin.

---

## Table of Contents

1. [The Problem — Concerns With No Home](#1-the-problem--concerns-with-no-home)
2. [The Gateway Is the One Front Door](#2-the-gateway-is-the-one-front-door)
3. [Routing — Getting a Request to the Right Service](#3-routing--getting-a-request-to-the-right-service)
4. [The Cross-Cutting Jobs — Done Once, at the Door](#4-the-cross-cutting-jobs--done-once-at-the-door)
5. [Translation — Decoupling the Public Contract from the Inside](#5-translation--decoupling-the-public-contract-from-the-inside)
6. [Aggregation and the Backend-for-Frontend](#6-aggregation-and-the-backend-for-frontend)
7. [The Cost — One Door Is a Chokepoint](#7-the-cost--one-door-is-a-chokepoint)
8. [When the Gateway Becomes a Monolith](#8-when-the-gateway-becomes-a-monolith)
9. [When You Need One — and When You Don't](#9-when-you-need-one--and-when-you-dont)
10. [Putting It All Together — A Streaming App's Mobile Edge](#10-putting-it-all-together--a-streaming-apps-mobile-edge)
11. [Final Recap](#11-final-recap)

---
