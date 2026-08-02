# WebSockets

> **Phase:** APIs & Communication Deep Dives → **Topic:** 7 of 15 → **Read time:** ~50 minutes

---

## Before You Begin

**This document stands alone.** It assumes you have read nothing else — not the foundation series, not the topics before it. It builds WebSockets from zero: why ordinary web requests can't do what real-time needs, how a WebSocket connection is created and kept open, and — the part that matters most — what it costs to hold one open for every connected client at once.

Two consequences of that choice:

- **Terms get defined where they're used** — the upgrade handshake, frames, full-duplex, ping/pong, sticky routing, backplane. Skim what you know.
- **Neighbouring topics are named, not taught.** This document is about the *mechanism* — how a WebSocket works and what it costs. The full comparison against lighter alternatives (long polling, server-sent events) is its own topic, and the catalogue of *which real-time features* to build on WebSockets is another. Where this doc reaches them, it points rather than teaches.

WebSockets appear in the **Top 30 Must-Know Concepts** foundation series. This is the deep-dive on how they actually work.

Here is the question the document answers:

> **The web is built on request-response: the client asks, the server answers, done. So how does a server *push* — send you a message you didn't ask for, the instant it happens — and why is the mechanism that allows it so much more expensive to run than an ordinary API?**

Here's the trap it disarms. WebSockets get filed as "the real-time upgrade" — a switch you flip to make an app live, a faster kind of API. That framing hides the actual subject. A WebSocket is not a faster request; it's a *different kind of connection* with a different cost model, and the moment you open one you have stepped out of the world HTTP quietly did everything for you — stateless servers, free caching, trivial load balancing, clean error codes — and into a world where every one of those becomes your problem. The messaging is the easy part. The **connection** is the subject.

> **The mindset shift:** stop thinking of a WebSocket as *a channel you send messages over* and start thinking of it as **a long-lived, stateful relationship the server must hold open for every client simultaneously.** An HTTP server forgets you the instant it answers; a WebSocket server *remembers* you, in memory, for as long as you're connected — and it's doing that for every other connected client too. That statefulness, not the two-way messaging, is what makes WebSockets powerful and what makes everything about running them hard. Learn to see the held-open connection as the cost, and the rest of this document is its consequences.

---

## Table of Contents

1. [Why Request-Response Hits a Wall](#1-why-request-response-hits-a-wall)
2. [The Upgrade — Becoming a WebSocket](#2-the-upgrade--becoming-a-websocket)
3. [Frames — How the Open Pipe Carries Messages](#3-frames--how-the-open-pipe-carries-messages)
4. [Full-Duplex — Both Sides Speak at Once](#4-full-duplex--both-sides-speak-at-once)
5. [The Connection Is State the Server Holds](#5-the-connection-is-state-the-server-holds)
6. [What You Gave Up Leaving HTTP](#6-what-you-gave-up-leaving-http)
7. [Keeping It Alive — Ping, Pong, Timeout, Reconnect](#7-keeping-it-alive--ping-pong-timeout-reconnect)
8. [Scaling Stateful Connections](#8-scaling-stateful-connections)
9. [When Not to Reach for One](#9-when-not-to-reach-for-one)
10. [Putting It All Together — A Live Collaboration Feature](#10-putting-it-all-together--a-live-collaboration-feature)
11. [Final Recap](#11-final-recap)
