# Webhooks

> **Phase:** APIs & Communication Deep Dives → **Topic:** 9 of 15 → **Read time:** ~48 minutes

---

## Before You Begin

**This document stands alone.** It assumes you have read nothing else — not the foundation series, not the topics before it. It builds webhooks from zero: why one system needs to know about events in another it doesn't control, how a webhook inverts an ordinary API call so the *other* side calls *you*, and — the part that matters most — everything you have to get right to receive one you can actually trust.

Two consequences of that choice:

- **Terms get defined where they're used** — webhook, registration, event payload, at-least-once delivery, idempotency, signature verification, replay protection. Skim what you know.
- **Neighbouring topics are named, not taught.** Where webhooks touch other tools — the WebSockets and server-sent events that push to *browsers*, the message queues that carry events between systems you own, the idempotency and rate-limiting techniques that get their own deep treatment — this document points at them rather than teaching them.

Webhooks appear in the **Top 30 Must-Know Concepts** foundation series. This is the deep-dive on how they actually work — and, more to the point, on what it takes to receive them correctly.

Here is the question the document answers:

> **Your system needs to know the instant something happens inside another system you don't own and can't see into — a payment clears, a file finishes processing, an order ships. You can't hold a connection open to it and you can't sensibly ask it "anything new?" a thousand times a second. So how does the other system *tell* you — and why is receiving that message correctly so much harder than it first looks?**

Here's the trap it disarms. A webhook looks trivial: the other service sends you an HTTP POST, you read the body, done. That framing is what produces broken integrations. *Sending* a webhook is trivial; *receiving one you can trust* is the whole subject — because the call crosses the boundary between two independently-failing systems over a network that drops things, and neither side controls the other. That boundary means the same event will sometimes arrive twice, sometimes out of order, sometimes long after it happened, and sometimes it isn't the real sender at all but someone forging calls to your public URL. A receiver that treats a webhook as "just a POST" silently double-charges customers, acts on refunds it hasn't received the charge for, and loses events every time it restarts.

> **The mindset shift:** stop thinking of a webhook as *a message the provider sends you* and start thinking of it as **a public endpoint you now operate, that another system calls on its own schedule, over an unreliable network.** The moment you see that you are running a little server for someone else's events — not receiving a tidy message — every hard part stops being a surprise and becomes obvious: of course it retries (the network fails), of course events duplicate (retries do that), of course they arrive out of order (independent deliveries race), of course you must verify the caller (your URL is public), and of course you must stay up and fast (the caller won't wait). The POST is the easy part. The endpoint is the project.

---

## Table of Contents

1. [The Problem — Knowing Without Asking](#1-the-problem--knowing-without-asking)
2. [The Inversion — You Become the Server](#2-the-inversion--you-become-the-server)
3. [Anatomy of a Delivery](#3-anatomy-of-a-delivery)
4. [At-Least-Once — Retries and the Duplicates They Cause](#4-at-least-once--retries-and-the-duplicates-they-cause)
5. [Idempotency — Processing the Same Event Twice Safely](#5-idempotency--processing-the-same-event-twice-safely)
6. [Ordering — Events Can Arrive Out of Sequence](#6-ordering--events-can-arrive-out-of-sequence)
7. [Trust — Verifying the Call Really Came From the Provider](#7-trust--verifying-the-call-really-came-from-the-provider)
8. [The Endpoint Is Your Responsibility Now](#8-the-endpoint-is-your-responsibility-now)
9. [When Webhooks Fit — and When They Don't](#9-when-webhooks-fit--and-when-they-dont)
10. [Putting It All Together — A Payment-Provider Integration](#10-putting-it-all-together--a-payment-provider-integration)
11. [Final Recap](#11-final-recap)

---
