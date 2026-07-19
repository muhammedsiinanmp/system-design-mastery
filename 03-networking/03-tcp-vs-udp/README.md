# TCP vs UDP

> **Phase:** Networking Deep Dives → **Topic:** 3 of 7 → **Read time:** ~60 minutes

---

## Before You Begin

**This document stands alone.** It assumes you have read nothing else — not the foundation series, not the phase before it, not the topics before it. Everything about the transport layer is built here from zero: ports and sockets, what UDP is, how TCP manufactures reliability out of a network that offers none, flow control, congestion control, the connection lifecycle, and why the newest protocol on the web threw TCP away. If you know only that "TCP is the reliable one," you are exactly the reader this was written for.

Two consequences of that choice:

- **Terms get defined where they're used** — port, socket, datagram, MTU, jitter, bufferbloat. Skim past what you already know.
- **Neighbouring topics are named, not taught.** HTTP's semantics, proxies, load balancers, checksums, and CDN strategy each have their own full treatment elsewhere in this curriculum. Where they touch transport, this document says so and points; it doesn't absorb them. *TCP and UDP themselves are complete here.*

TCP vs UDP is one of the concepts promised in the **Top 30 Must-Know Concepts** foundation series' opening. This is where that promise is paid in full.

Here is the question the document answers:

> **A network can lose your data, reorder it, duplicate it, or deliver it late — and it never tells you which. So how does anything work at all, and why do some of the most important systems on the internet deliberately refuse the machinery that fixes it?**

Here's the trap it disarms. TCP is introduced to nearly everyone as *the reliable one* and UDP as *the unreliable one*, which frames the whole subject as a quality ranking with an obvious winner. Under that framing, UDP is a legacy curiosity — something you'd only choose by accident.

Then you notice what actually runs on UDP: DNS, every video call you've ever made, live streaming, multiplayer games, most metrics pipelines, and — since HTTP/3 — an enormous and growing share of ordinary web traffic. Those aren't careless choices made by people who didn't know better. They are deliberate, and the reasoning behind them is the most useful thing in this document.

> **The mindset shift:** stop ranking transports as *reliable versus unreliable* and start reading them as **a decision about what happens when a packet goes missing.** TCP says: *everything stops and waits until I get it back.* UDP says: *it's gone — keep going.* Neither answer is correct in general. The right one falls out of a single question: **does this data still have value if it arrives late?** For a payment, yes — it's worth any delay to get it right. For the audio frame you should have heard 200 ms ago, no — it is now worthless, and waiting for it only damages what comes after. Reliability isn't a quality you want more of. It's a trade you make against time.

---

## Table of Contents

1. [What the Transport Layer Is For](#1-what-the-transport-layer-is-for)
2. [UDP — The Honest Minimum](#2-udp--the-honest-minimum)
3. [TCP — Building Reliability Out of Nothing](#3-tcp--building-reliability-out-of-nothing)
4. [Ordered Delivery and Head-of-Line Blocking](#4-ordered-delivery-and-head-of-line-blocking)
5. [Flow Control — Don't Overwhelm the Receiver](#5-flow-control--dont-overwhelm-the-receiver)
6. [Congestion Control — Don't Overwhelm the Network](#6-congestion-control--dont-overwhelm-the-network)
7. [The Connection Lifecycle](#7-the-connection-lifecycle)
8. [When UDP Wins](#8-when-udp-wins)
9. [QUIC — Rebuilding TCP on Top of UDP](#9-quic--rebuilding-tcp-on-top-of-udp)
10. [Putting It All Together — A Mobile-First Team Meets the Transport Layer](#10-putting-it-all-together--a-mobile-first-team-meets-the-transport-layer)
11. [Final Recap](#11-final-recap)
