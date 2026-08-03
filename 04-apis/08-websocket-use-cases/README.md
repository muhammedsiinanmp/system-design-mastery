# WebSocket Use Cases

> **Phase:** APIs & Communication Deep Dives → **Topic:** 8 of 15 → **Read time:** ~48 minutes

---

## Before You Begin

**This document builds directly on Topic 07 — WebSockets, and assumes you've read it.** Where every other topic in this phase stands alone, this one is deliberately *coupled*: Topic 07 already taught how a WebSocket works and — more importantly — what it costs to hold one open (the connection is server-held state; every open connection is memory, a file descriptor, and identity the server keeps for every client at once; scaling needs sticky routing and a backplane). This document does **not** re-teach any of that. It builds the layer above it: *given that you understand the mechanism and its cost, which features should actually use a WebSocket — and which of the many features called "real-time" should not.*

Two consequences of that choice:

- **The mechanism is recalled, not re-explained.** When this doc says "the backplane" or "the connection is state," it's leaning on what Topic 07 established, in one clause, and moving on. If a term feels unfamiliar, it's taught there.
- **Neighbouring tools are named, not taught.** The full head-to-head against lighter alternatives (long polling, server-sent events) is its own topic; webhooks and WebRTC are their own topics too. Where this doc reaches them, it points rather than teaches.

WebSockets appear in the **Top 30 Must-Know Concepts** foundation series. Topic 07 was the deep-dive on the mechanism; this is the deep-dive on *where it belongs*.

Here is the question the document answers:

> **"Real-time" is one of the most overloaded words in engineering — a chat, a live dashboard, a multiplayer game, and a push notification are all called real-time, yet they want completely different things. So when a feature is described as real-time, how do you tell whether it genuinely needs a WebSocket, something lighter, or something else entirely — and how do you know what will actually be hard to build?**

Here's the trap it disarms. The word "real-time" acts like a switch: someone says it, and the reflex is *"real-time means WebSockets."* That reflex is wrong far more often than it's right. Most features labelled real-time are *one-way server push* — a dashboard updating, a notification arriving, a feed refreshing — and for those a WebSocket is overkill that buys you Topic 07's entire statefulness bill for a capability (the client talking back) you never use. The features that genuinely need a WebSocket are a minority, and telling them apart isn't about the feature's *name* — it's about its underlying shape.

> **The mindset shift:** stop classifying a feature by its **label** — "chat", "dashboard", "notifications", "live tracking" — and start classifying it by its **communication pattern**: *who sends messages, to how many recipients, and how often.* Two features with different labels can be the same pattern, and two features with the same label can be different patterns. Once you name the pattern, two things fall out at once — **which transport fits** (often not a WebSocket) and **what will actually be hard** (ordering, delivery, reconnection, presence — problems that recur across features rather than being invented fresh for each). The label tells you what a feature is called; the pattern tells you how to build it.

---

## Table of Contents

1. [What "Real-Time" Actually Means](#1-what-real-time-actually-means)
2. [The Two Questions That Classify Any Feature](#2-the-two-questions-that-classify-any-feature)
3. [Pattern A — One-Way Server Push](#3-pattern-a--one-way-server-push)
4. [Pattern B — Two-Way Conversation](#4-pattern-b--two-way-conversation)
5. [Pattern C — Shared State Across Many](#5-pattern-c--shared-state-across-many)
6. [Presence — The Sub-Pattern Hiding in All of Them](#6-presence--the-sub-pattern-hiding-in-all-of-them)
7. [The Hard Parts Are Shared, Not Per-Feature](#7-the-hard-parts-are-shared-not-per-feature)
8. [When Real-Time Isn't a WebSocket](#8-when-real-time-isnt-a-websocket)
9. [A Practical Way to Choose](#9-a-practical-way-to-choose)
10. [Putting It All Together — A Delivery-Tracking App](#10-putting-it-all-together--a-delivery-tracking-app)
11. [Final Recap](#11-final-recap)

---
