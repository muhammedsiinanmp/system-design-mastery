# REST vs GraphQL

> **Phase:** APIs & Communication Deep Dives → **Topic:** 5 of 15 → **Read time:** ~50 minutes

---

## Before You Begin

**This document stands alone.** It assumes you have read nothing else — not the foundation series, not the topics before it. It teaches enough of both REST and GraphQL to compare them honestly, and then does the comparison. If you've only ever built one of the two, this is written for you.

Two consequences of that choice:

- **Terms get defined where they're used** — over-fetching, under-fetching, the query model, partial responses. What you already know, skim.
- **This is a comparison, not a tutorial for either side.** REST's design craft and GraphQL's internals each have their own dedicated topics in this phase. This document teaches each *only to the depth needed to weigh it against the other* — enough to choose well, not enough to build either from scratch. Where it stops short, it says so and points.

REST and GraphQL both appear in the **Top 30 Must-Know Concepts** foundation series. This is the deep-dive on the decision *between* them.

Here is the question the document answers:

> **REST vs GraphQL is argued like a rivalry with a winner. Strip away the tribalism and it's a single design tradeoff — so what is the tradeoff actually about, and which side should you land on?**

Here's the trap it disarms. The debate is usually conducted as identity ("we're a GraphQL shop," "REST is dead," "GraphQL is overkill"), which produces heat and no decision procedure. But the two are not competing products where one is simply better. They are two answers to *one specific question*, and every difference people argue about — efficiency, caching, complexity, error handling — is a downstream consequence of which answer you pick. Once you see the question, the comparison stops being a matter of allegiance and becomes a matter of tracing consequences.

> **The mindset shift:** stop asking *"which is better, REST or GraphQL?"* and start asking **"who should decide the shape of each response — the server or the client — and what does that decision cost on each side?"** That single choice is the whole disagreement. REST lets the server decide what each endpoint returns; GraphQL lets the client declare exactly what it wants. Efficiency, caching, complexity, security — none of them are independent features to score. Each is a *result* of that one inversion, and once you can trace the results, you can choose on evidence instead of taste.

---

## Table of Contents

1. [The One Question Behind the Whole Debate](#1-the-one-question-behind-the-whole-debate)
2. [Enough GraphQL to Judge It](#2-enough-graphql-to-judge-it)
3. [Fetching — Over-, Under-, and Exactly-Right](#3-fetching--over--under--and-exactly-right)
4. [Caching — Where REST Quietly Wins](#4-caching--where-rest-quietly-wins)
5. [Complexity — Who Carries the Weight](#5-complexity--who-carries-the-weight)
6. [Errors, Status, and the Partial-Response Problem](#6-errors-status-and-the-partial-response-problem)
7. [Evolving the Contract](#7-evolving-the-contract)
8. [The Security and Cost Surface](#8-the-security-and-cost-surface)
9. [Choosing — REST by Default, GraphQL When](#9-choosing--rest-by-default-graphql-when)
10. [Putting It All Together — The Same App, Both Ways](#10-putting-it-all-together--the-same-app-both-ways)
11. [Final Recap](#11-final-recap)
