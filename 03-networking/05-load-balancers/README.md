# Load Balancers

> **Phase:** Networking Deep Dives → **Topic:** 5 of 7 → **Read time:** ~55 minutes

---

## Before You Begin

**This document stands alone.** It assumes you have read nothing else — not the foundation series, not the phase before it, not the topics before it. Everything is built here from zero: why one address has to serve many machines, where the balancing decision happens, how a balancer decides which servers are alive, how servers join and leave without losing work, and how the balancer itself avoids being the thing that takes you down.

Two consequences of that choice:

- **Terms get defined where they're used** — pool, upstream, health check, draining, session affinity, virtual IP, single point of failure. Skim past what you already know.
- **Neighbouring topics are named, not taught.** The specific algorithms for choosing a server, consistent hashing, autoscaling, service discovery, and CDN strategy each have their own full treatment elsewhere in this curriculum. Where they touch balancing, this document says so and points; it doesn't absorb them. *Load balancers themselves are complete here.*

Load balancing is one of the concepts in the **Top 30 Must-Know Concepts** foundation series, where it gets a short introduction. This is that concept's deep-dive.

Here is the question the document answers:

> **When many machines can serve a request, how does anything decide where to send it — and how does it know that machine is still capable of answering?**

Here's the trap it disarms. A load balancer looks like a solved problem. It spreads requests across servers; the concept takes one sentence; every cloud provider offers one as a checkbox with sensible defaults. Nothing about it invites study.

Then you meet the outages. And what's striking about load-balancer outages is that they are almost never caused by the balancer failing to spread traffic. They're caused by it **doing precisely what it was configured to do** — removing servers that were perfectly healthy, keeping servers that had stopped working, discarding requests it was already holding during a routine deploy, or concluding that every machine in the fleet had died at the same instant. In each case the configuration was followed exactly. The configuration encoded a belief that turned out to be wrong.

> **The mindset shift:** stop thinking of a load balancer as *the thing that spreads requests* and start thinking of it as **the thing that continuously decides which servers exist.** Distribution is the easy half, and it is largely solved. The hard half is the judgement running underneath it, re-evaluated every few seconds: *is this machine alive? is it ready yet? is it still ready? should I stop sending it work — and what about the requests it is holding right now?* Every serious load-balancer failure is a wrong answer to one of those four questions. And wrong answers are dangerous precisely because they don't look like failures — they look exactly like the system working as designed.

---

## Table of Contents

1. [Many Servers, One Address](#1-many-servers-one-address)
2. [Where the Balancing Happens](#2-where-the-balancing-happens)
3. [Health Checking — Knowing What's Alive](#3-health-checking--knowing-whats-alive)
4. [What a Health Check Actually Proves](#4-what-a-health-check-actually-proves)
5. [Adding and Removing Servers](#5-adding-and-removing-servers)
6. [Session Affinity — When Requests Must Come Back](#6-session-affinity--when-requests-must-come-back)
7. [Making the Front Door Redundant](#7-making-the-front-door-redundant)
8. [When Balancing Makes Things Worse](#8-when-balancing-makes-things-worse)
9. [What a Load Balancer Cannot Do](#9-what-a-load-balancer-cannot-do)
10. [Putting It All Together — The Health Check That Caused the Outage](#10-putting-it-all-together--the-health-check-that-caused-the-outage)
11. [Final Recap](#11-final-recap)
