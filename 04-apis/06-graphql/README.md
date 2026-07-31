# GraphQL

> **Phase:** APIs & Communication Deep Dives → **Topic:** 6 of 15 → **Read time:** ~55 minutes

---

## Before You Begin

**This document stands alone.** It assumes you have read nothing else — not the foundation series, not the topics before it. It builds GraphQL from zero: what the schema actually is, how a query runs, where the data comes from, and every capability and cost that follows. If you've heard GraphQL is "REST but you pick the fields," this is written to replace that picture with a working one.

Two consequences of that choice:

- **Terms get defined where they're used** — schema, type, field, resolver, the N+1 problem, batching, subscription. Skim what you know.
- **Neighbouring topics are named, not taught.** When to choose GraphQL over REST is a comparison of its own; the persistent-connection transport that subscriptions ride on, and general authentication and rate limiting, each belong to their own topics. This document is about how GraphQL itself works.

GraphQL appears in the **Top 30 Must-Know Concepts** foundation series. This is the deep-dive on its machinery.

Here is the question the document answers:

> **A GraphQL query looks like you're just listing the fields you want. What is actually happening on the server to turn that list into data — and why do the hard parts (performance, caching, safety) all show up at once?**

Here's the trap it disarms. GraphQL is usually first met as *syntax* — a curly-brace query where you name fields, apparently "REST where you choose the response." Learn the syntax and you feel done. But the syntax is the easy ten percent. The actual subject is what the server does with that query: it is walking a **graph**, node by node, along a path the client drew — and schema design, the resolver model, the notorious performance traps, and the caching and safety problems are all consequences of that one fact. Miss it and GraphQL is a bag of disconnected features and gotchas; see it and they're one idea.

> **The mindset shift:** stop reading a GraphQL query as *a list of fields you want* and start reading it as **a path through a graph that the server walks one node at a time.** The schema defines a graph — types are nodes, fields are edges. A query is a traversal the client specifies. A resolver is how the server steps across a single edge. Once you hold that, everything else falls out of it: the N+1 problem is a naive traversal, batching is a smarter one, cost limits bound the traversal, caching remembers visited nodes, mutations are traversals that write, and subscriptions are traversals that re-run. The graph isn't a metaphor in the name — it's the execution model.

---

## Table of Contents

1. [GraphQL Is a Graph You Can Query](#1-graphql-is-a-graph-you-can-query)
2. [The Schema — Defining the Graph](#2-the-schema--defining-the-graph)
3. [Resolvers — Walking the Graph](#3-resolvers--walking-the-graph)
4. [The N+1 Problem — Naive Traversal](#4-the-n1-problem--naive-traversal)
5. [Mutations — Traversals That Change State](#5-mutations--traversals-that-change-state)
6. [Subscriptions — Traversals That Re-Run on Events](#6-subscriptions--traversals-that-re-run-on-events)
7. [Caching Without Free HTTP Caching](#7-caching-without-free-http-caching)
8. [Cost, Depth, and Keeping the Graph Safe](#8-cost-depth-and-keeping-the-graph-safe)
9. [GraphQL Across Many Teams — A Survey](#9-graphql-across-many-teams--a-survey)
10. [Putting It All Together — Building a Small GraphQL API](#10-putting-it-all-together--building-a-small-graphql-api)
11. [Final Recap](#11-final-recap)
