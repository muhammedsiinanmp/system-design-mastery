# System Design Mastery — Curriculum Roadmap

This is the single source of truth for the entire curriculum.

Every topic lives here. Use this file to:
- Know what to build next
- Avoid duplicating topics
- Track what is done, in progress, or planned
- Understand how topics connect to each other

---

## How to Read This File

| Status | Meaning |
|---|---|
| ✅ Done | Document written and reviewed |
| 🚧 In Progress | Currently being written |
| 📋 Planned | Scoped and ready to write next |
| 💡 Idea | Rough idea, not yet scoped |

---

## Module 01 — Introduction

### 01 Networking Foundations

| # | Topic | Status | File |
|---|---|---|---|
| 01 | Client–Server Model | ✅ Done | `01-introduction/01-networking-foundations/01-client-server-model/README.md` |
| 02 | IP Addresses | 📋 Planned | — |
| 03 | DNS — How Domain Names Resolve | 📋 Planned | — |
| 04 | HTTP & HTTPS | 📋 Planned | — |
| 05 | TCP vs UDP | 📋 Planned | — |
| 06 | Ports & Sockets | 📋 Planned | — |

### 02 Core Internet Concepts

| # | Topic | Status | File |
|---|---|---|---|
| 01 | Proxies & Reverse Proxies | 📋 Planned | — |
| 02 | CDNs — Content Delivery Networks | 📋 Planned | — |
| 03 | REST APIs | 📋 Planned | — |
| 04 | WebSockets | 💡 Idea | — |
| 05 | gRPC | 💡 Idea | — |

---

## Module 02 — Core Building Blocks

### 01 Storage

| # | Topic | Status | File |
|---|---|---|---|
| 01 | Databases — SQL vs NoSQL | 📋 Planned | — |
| 02 | Indexing | 📋 Planned | — |
| 03 | Caching | 📋 Planned | — |
| 04 | Object Storage | 💡 Idea | — |
| 05 | Data Replication | 💡 Idea | — |

### 02 Compute & Traffic

| # | Topic | Status | File |
|---|---|---|---|
| 01 | Load Balancers | 📋 Planned | — |
| 02 | Horizontal vs Vertical Scaling | 📋 Planned | — |
| 03 | Stateless vs Stateful Services | 📋 Planned | — |
| 04 | Rate Limiting | 💡 Idea | — |
| 05 | API Gateways | 💡 Idea | — |

---

## Module 03 — Reliability & Fault Tolerance

| # | Topic | Status | File |
|---|---|---|---|
| 01 | Availability & Uptime | 📋 Planned | — |
| 02 | Redundancy & Replication | 📋 Planned | — |
| 03 | Timeouts, Retries & Backoff | 📋 Planned | — |
| 04 | Circuit Breakers | 📋 Planned | — |
| 05 | Graceful Degradation | 💡 Idea | — |
| 06 | Health Checks & Monitoring | 💡 Idea | — |

---

## Module 04 — Distributed Systems

| # | Topic | Status | File |
|---|---|---|---|
| 01 | What is a Distributed System? | 📋 Planned | — |
| 02 | CAP Theorem | 📋 Planned | — |
| 03 | Consistency Models | 📋 Planned | — |
| 04 | Consensus & Leader Election | 💡 Idea | — |
| 05 | Distributed Caching | 💡 Idea | — |
| 06 | Message Queues | 💡 Idea | — |

---

## Module 05 — Real-World System Design

| # | Topic | Status | File |
|---|---|---|---|
| 01 | How to Approach a System Design Interview | 📋 Planned | — |
| 02 | Design a URL Shortener | 💡 Idea | — |
| 03 | Design a Chat System | 💡 Idea | — |
| 04 | Design a News Feed | 💡 Idea | — |
| 05 | Design a Video Streaming Service | 💡 Idea | — |
| 06 | Design a Ride-Sharing Service | 💡 Idea | — |

---

## Contribution Rules

To keep the repo clean, follow these rules every time you add a topic:

1. **Update this file first** — mark the topic as 🚧 In Progress before writing
2. **Follow the folder naming convention** — `{module}/{section}/{##-topic-name}/README.md`
3. **Mark ✅ Done only after review** — not when first drafted
4. **Never create a file without a row here** — this file is the source of truth

---

## Folder Naming Convention

```
{module-number}-{module-name}/
  {section-number}-{section-name}/
    {topic-number}-{topic-name}/
      README.md
```

Example:
```
01-introduction/
  01-networking-foundations/
    01-client-server-model/
      README.md
    02-ip-addresses/
      README.md
```

---

*Last updated: 2026-06-06*