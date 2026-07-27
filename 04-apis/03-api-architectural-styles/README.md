# API Architectural Styles

> **Phase:** APIs & Communication Deep Dives → **Topic:** 3 of 15 → **Read time:** ~50 minutes

---

## Before You Begin

**This document stands alone.** It assumes you have read nothing else — not the foundation series, not the topics before it. Everything is built here from zero: what an architectural style is, the small set of styles that dominate real systems, what each one fundamentally organizes an API *around*, and how to choose between them.

Two consequences of that choice:

- **Terms get defined where they're used** — style, resource, procedure, query, persistent channel, callback. Skim past what you already know.
- **Neighbouring topics are named, not taught.** REST design, the REST-versus-GraphQL comparison, GraphQL internals, gRPC, WebSockets, and webhooks each have their own full treatment later in this phase. This document is the **map** — enough of each style to choose a direction, and a pointer to the topic that goes deep. It deliberately teaches none of them in full.

API styles are part of the APIs concept in the **Top 30 Must-Know Concepts** foundation series. This is the deep-dive on the question that comes *before* picking any specific technology.

Here is the question the document answers:

> **REST, gRPC, GraphQL, WebSockets, webhooks — these get argued about like sports teams. Underneath the tribalism, what actually distinguishes them, and how would you choose without already having a favorite?**

Here's the trap it disarms. Architectural style is usually inherited, not chosen. A team is "a REST shop" or "a gRPC shop," and every new API gets the house style regardless of what it's for. That works until it doesn't — a REST API contorted into carrying real-time updates, a gRPC service that a browser can't call, a resource model bent around an operation that was never a resource. The style was picked by habit, and the mismatch shows up as friction in every later decision.

The styles aren't competing products where one wins. They're different answers to a single design question, and the answer that's obviously right for one interaction is obviously wrong for another.

> **The mindset shift:** stop asking *"which API style is best?"* and start asking **"what is the natural unit of this interaction?"** Every style is organized around a different unit — a *thing* you act on, an *action* you invoke, a *question* you pose, a *conversation* you hold open, a *notification* you send. Name the unit the interaction actually wants, and the style stops being a matter of taste and becomes a matter of fit. Pick the unit wrong and no amount of good implementation rescues it; pick it right and the style falls out on its own.

---

## Table of Contents

1. [What a "Style" Actually Is](#1-what-a-style-actually-is)
2. [The Request-Response Family — One Shape, Three Paradigms](#2-the-request-response-family--one-shape-three-paradigms)
3. [Resource-Oriented — Acting on Things](#3-resource-oriented--acting-on-things)
4. [Procedure-Oriented — Calling Functions](#4-procedure-oriented--calling-functions)
5. [Query-Oriented — Describing What You Want](#5-query-oriented--describing-what-you-want)
6. [Beyond Request-Response — Persistent and Inverted](#6-beyond-request-response--persistent-and-inverted)
7. [The Orthogonal Choices — Transport, Format, Contract](#7-the-orthogonal-choices--transport-format-contract)
8. [Public vs Internal — The Audience Bends the Choice](#8-public-vs-internal--the-audience-bends-the-choice)
9. [Choosing — Match the Style to the Unit](#9-choosing--match-the-style-to-the-unit)
10. [Putting It All Together — One System, Several Styles](#10-putting-it-all-together--one-system-several-styles)
11. [Final Recap](#11-final-recap)
