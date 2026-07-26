# Data Formats — JSON, XML, and Protocol Buffers

> **Phase:** APIs & Communication Deep Dives → **Topic:** 2 of 15 → **Read time:** ~50 minutes

---

## Before You Begin

**This document stands alone.** It assumes you have read nothing else — not the foundation series, not the topics before it. Everything is built here from zero: what serialization is, the two decisions every format makes, the three formats that dominate, and how a format lets you change your data's shape without breaking the programs already reading it.

Two consequences of that choice:

- **Terms get defined where they're used** — serialization, schema, text vs binary, field numbers, backward and forward compatibility. Skim past what you already know.
- **Neighbouring topics are named, not taught.** The RPC framework built on Protocol Buffers (gRPC), the styles that carry these formats (REST, GraphQL), and contract-level API versioning each have their own full treatment later in this phase. This document is about the formats themselves — the bytes on the wire.

Data formats are part of the APIs concept in the **Top 30 Must-Know Concepts** foundation series. This is the deep-dive on the specific question of how values become bytes.

Here is the question the document answers:

> **Two programs share no memory. One has a value — a number, a name, a nested object — and the other needs it. How does that value cross the gap, and why is "just use JSON" a decision with consequences most people never notice they made?**

Here's the trap it disarms. The data format feels like a settled, low-stakes choice — everyone uses JSON, you send it, it works, there's nothing to think about. That comfort hides that the format quietly decides four things that matter enormously later: whether you can read your own traffic when debugging, how many bytes every request costs, how much CPU is burned parsing them, and whether adding a field tomorrow breaks the clients you shipped today. None of those are visible on a good day. All of them arrive on a bad one.

> **The mindset shift:** stop asking *"which format is best?"* — there is no best — and start asking **"text or binary, schema or schemaless, for this data, read by whom, at what volume?"** Every format is a fixed set of answers to those two questions, and the answers that are perfect for a public API read by strangers are the wrong ones for a million-times-a-second internal call. The format isn't a default to inherit. It's a position on two axes, chosen — ideally on purpose — to fit who reads the bytes and how many of them there are.

---

## Table of Contents

1. [Serialization — The Problem Every Format Solves](#1-serialization--the-problem-every-format-solves)
2. [The First Axis — Text vs Binary](#2-the-first-axis--text-vs-binary)
3. [The Second Axis — Schema vs Schemaless](#3-the-second-axis--schema-vs-schemaless)
4. [JSON — Readable, Schemaless, Everywhere](#4-json--readable-schemaless-everywhere)
5. [XML — The Heritage Format](#5-xml--the-heritage-format)
6. [Protocol Buffers — Compact, Binary, Contract-First](#6-protocol-buffers--compact-binary-contract-first)
7. [Schema Evolution — Changing the Shape Without Breaking Readers](#7-schema-evolution--changing-the-shape-without-breaking-readers)
8. [Size and Speed — What the Wire Actually Costs](#8-size-and-speed--what-the-wire-actually-costs)
9. [Choosing — Match the Format to the Reader](#9-choosing--match-the-format-to-the-reader)
10. [Putting It All Together — One Payload, Three Formats, Three Outcomes](#10-putting-it-all-together--one-payload-three-formats-three-outcomes)
11. [Final Recap](#11-final-recap)
