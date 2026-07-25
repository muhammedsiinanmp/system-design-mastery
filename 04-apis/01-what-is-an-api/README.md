# What Is an API?

> **Phase:** APIs & Communication Deep Dives → **Topic:** 1 of 15 → **Read time:** ~50 minutes

---

## Before You Begin

**This document stands alone.** It assumes you have read nothing else — not the foundation series, not the phases before it. Everything is built here from zero: what an API is, what a contract actually consists of, and — the heart of it — what changes the moment that contract is served across a network instead of called inside one program.

Two consequences of that choice:

- **Terms get defined where they're used** — interface, implementation, contract, encapsulation, backward compatibility, idempotency. Skim past what you already know.
- **Neighbouring topics are named, not taught.** The specific *styles* an API can take (REST, GraphQL, gRPC, WebSockets, webhooks), the *formats* it serializes to (JSON, Protobuf), and the *mechanisms* it relies on (versioning, idempotency, rate limiting, gateways) each have their own full treatment later in this phase. This document is about what all of them have in common — the thing they are all versions of.

APIs are one of the concepts in the **Top 30 Must-Know Concepts** foundation series, where they get a short introduction. This is the deep-dive.

Here is the question the document answers:

> **Everyone knows an API is "the thing you call to get data." So why is designing one hard enough to have an entire phase of this curriculum devoted to it?**

Here's the trap it disarms. The word "API" feels fully understood the moment you've used one — you send a request, you get JSON back, done. That familiarity is exactly what hides the subject. Calling an API *looks* identical to calling a function in your own code: a name, some arguments, a return value. It reads the same on the page.

It is not the same, and the entire difficulty of APIs lives in the difference. The function in your code shares your fate — if it's there, it runs; if it's broken, your program is broken with it, immediately and obviously. The API across the network shares nothing with you. It belongs to someone else, runs on a machine you don't control, and can be slow, absent, overloaded, or a version you've never seen — while your code keeps running and has to somehow cope.

> **The mindset shift:** stop picturing an API as *a thing you call to get data* and start seeing it as **a contract between two parties who fail independently.** A local function call has one fate, shared between caller and callee. A network call splits that fate in two: the other side can vanish while you continue, and now every hard thing about APIs — timeouts, retries, duplicate requests, versioning, backward compatibility — becomes unavoidable. None of them are about the data or the format. All of them are consequences of the two sides being able to fail apart from each other.

---

## Table of Contents

1. [What an API Actually Is](#1-what-an-api-actually-is)
2. [The Leap — Local Calls vs Remote Calls](#2-the-leap--local-calls-vs-remote-calls)
3. [The Contract and Its Parts](#3-the-contract-and-its-parts)
4. [Encapsulation — The Whole Point](#4-encapsulation--the-whole-point)
5. [The Contract Must Survive Change](#5-the-contract-must-survive-change)
6. [Failure Is Now a First-Class Case](#6-failure-is-now-a-first-class-case)
7. [Boundaries Are Control Points](#7-boundaries-are-control-points)
8. [Public, Private, and Partner APIs](#8-public-private-and-partner-apis)
9. [The Shapes a Contract Can Take](#9-the-shapes-a-contract-can-take)
10. [Putting It All Together — Turning an Internal Function Into a Public API](#10-putting-it-all-together--turning-an-internal-function-into-a-public-api)
11. [Final Recap](#11-final-recap)
