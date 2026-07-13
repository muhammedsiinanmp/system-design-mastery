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
| 💡 Idea | Exists in base curriculum — not yet scoped |

---

## Contribution Rules

Follow these every time you add a topic:

1. **Update this file first** — mark the topic 🚧 In Progress before writing
2. **Follow the folder naming convention** — `{phase}/{section}/{##-topic-name}/README.md`
3. **Mark ✅ Done only after review** — not when first drafted
4. **Never create a file without a row here** — this is the source of truth

### Folder Naming Convention

```
{phase-number}-{phase-name}/
  {group-number}-{group-name}/
    README.md                  ← for group docs (Top 30)
    {topic-number}-{topic-name}/
      README.md                ← for standalone deep-dive docs
```

---

## Phase 01 — Introduction

> Goal: Build the mental model before touching any technical concept.
> Two parts: one document that sets the stage, then 6 group mini-lessons covering the 30 foundational concepts.

| # | Topic | Status | File |
|---|---|---|---|
| 01 | What is System Design? | ✅ Done | `01-introduction/00-what-is-system-design/README.md` |

### Top 30 Must-Know Concepts — 6 Group Documents

> Each group is a self-contained mini-lesson at calibrated depth.
> Concepts that receive full deep-dives later are introduced lightly here — just enough intuition to move forward.

| Group | Topic | Status | File |
|---|---|---|---|
| 01 | Networking Foundations | ✅ Done | `01-introduction/01-networking-foundations/README.md` |
| 02 | APIs & Communication | ✅ Done | `01-introduction/02-apis-and-communication/README.md` |
| 03 | Data Storage | ✅ Done | `01-introduction/03-data-storage/README.md` |
| 04 | Scaling | ✅ Done | `01-introduction/04-scaling/README.md` |
| 05 | Distributed Systems | ✅ Done | `01-introduction/05-distributed-systems/README.md` |
| 06 | Architecture Patterns | ✅ Done | `01-introduction/06-architecture-patterns/README.md` |

---

## Phase 02 — Core System Properties

> Goal: Establish the vocabulary every system design conversation uses.
> These are the properties engineers evaluate every design decision against.
> No solutions yet — just the language and the intuition.

| # | Topic | Status | File |
|---|---|---|---|
| 01 | Latency vs Throughput | ✅ Done | `02-core-properties/01-latency-vs-throughput/README.md` |
| 02 | Availability | 🚧 In Progress | `02-core-properties/02-availability/README.md` |
| 03 | Reliability | 📋 Planned | `02-core-properties/03-reliability/README.md` |
| 04 | Scalability | 📋 Planned | `02-core-properties/04-scalability/README.md` |
| 05 | Single Point of Failure (SPOF) | 📋 Planned | `02-core-properties/05-single-point-of-failure/README.md` |

---

## Phase 03 — Networking Deep Dives

> Goal: Full treatment of the wire-level concepts introduced in Group 1.
> Each topic here expands on the intuition already built — no cold starts.

| # | Topic | Status | File |
|---|---|---|---|
| 01 | DNS — Domain Name System | 📋 Planned | `03-networking/01-dns/README.md` |
| 02 | HTTP & HTTPS | 📋 Planned | `03-networking/02-http-https/README.md` |
| 03 | TCP vs UDP | 📋 Planned | `03-networking/03-tcp-vs-udp/README.md` |
| 04 | Proxy vs Reverse Proxy | 📋 Planned | `03-networking/04-proxy-vs-reverse-proxy/README.md` |
| 05 | Load Balancers | 📋 Planned | `03-networking/05-load-balancers/README.md` |
| 06 | Load Balancing Algorithms | 📋 Planned | `03-networking/06-load-balancing-algorithms/README.md` |
| 07 | Checksums | 💡 Idea | `03-networking/07-checksums/README.md` |

---

## Phase 04 — APIs & Communication Deep Dives

> Goal: Full treatment of the communication patterns introduced in Group 2.
> REST design principles, GraphQL internals, WebSocket architecture, and API infrastructure.

| # | Topic | Status | File |
|---|---|---|---|
| 01 | What is an API? | 📋 Planned | `04-apis/01-what-is-an-api/README.md` |
| 02 | Data Formats (JSON, XML, Protobuf) | 📋 Planned | `04-apis/02-data-formats/README.md` |
| 03 | API Architectural Styles | 📋 Planned | `04-apis/03-api-architectural-styles/README.md` |
| 04 | REST API Design | 📋 Planned | `04-apis/04-rest-api-design/README.md` |
| 05 | REST vs GraphQL | 📋 Planned | `04-apis/05-rest-vs-graphql/README.md` |
| 06 | GraphQL | 📋 Planned | `04-apis/06-graphql/README.md` |
| 07 | WebSockets | 📋 Planned | `04-apis/07-websockets/README.md` |
| 08 | WebSocket Use Cases | 📋 Planned | `04-apis/08-websocket-use-cases/README.md` |
| 09 | Webhooks | 📋 Planned | `04-apis/09-webhooks/README.md` |
| 10 | gRPC | 📋 Planned | `04-apis/10-grpc/README.md` |
| 11 | API Gateways | 📋 Planned | `04-apis/11-api-gateways/README.md` |
| 12 | Rate Limiting | 📋 Planned | `04-apis/12-rate-limiting/README.md` |
| 13 | Idempotency | 📋 Planned | `04-apis/13-idempotency/README.md` |
| 14 | API Versioning | 📋 Planned | `04-apis/14-api-versioning/README.md` |
| 15 | WebRTC | 💡 Idea | `04-apis/15-webrtc/README.md` |

---

## Phase 05 — Storage & Databases

> Goal: Understand where data lives and how to keep it accessible as it grows.
> Foundations first, scaling techniques second — in the order a learner needs them.

### 01 — Foundations

| # | Topic | Status | File |
|---|---|---|---|
| 01 | Database Types | 📋 Planned | `05-storage/01-foundations/01-database-types/README.md` |
| 02 | SQL vs NoSQL | 📋 Planned | `05-storage/01-foundations/02-sql-vs-nosql/README.md` |
| 03 | Data Modeling Fundamentals | 📋 Planned | `05-storage/01-foundations/03-data-modeling/README.md` |
| 04 | Database Transactions | 📋 Planned | `05-storage/01-foundations/04-database-transactions/README.md` |
| 05 | ACID Transactions | 📋 Planned | `05-storage/01-foundations/05-acid-transactions/README.md` |
| 06 | Indexing | 📋 Planned | `05-storage/01-foundations/06-indexing/README.md` |
| 07 | Query Optimization | 📋 Planned | `05-storage/01-foundations/07-query-optimization/README.md` |
| 08 | How Databases Guarantee Durability | 📋 Planned | `05-storage/01-foundations/08-durability/README.md` |
| 09 | Object Storage | 📋 Planned | `05-storage/01-foundations/09-object-storage/README.md` |
| 10 | Connection Pooling | 📋 Planned | `05-storage/01-foundations/10-connection-pooling/README.md` |
| 11 | PostgreSQL Internal Architecture | 💡 Idea | `05-storage/01-foundations/11-postgresql-internals/README.md` |

### 02 — Scaling Techniques

| # | Topic | Status | File |
|---|---|---|---|
| 01 | Replication | 📋 Planned | `05-storage/02-scaling/01-replication/README.md` |
| 02 | Sharding | 📋 Planned | `05-storage/02-scaling/02-sharding/README.md` |
| 03 | Vertical Partitioning | 📋 Planned | `05-storage/02-scaling/03-vertical-partitioning/README.md` |
| 04 | Sharding vs Partitioning | 📋 Planned | `05-storage/02-scaling/04-sharding-vs-partitioning/README.md` |
| 05 | Denormalization | 📋 Planned | `05-storage/02-scaling/05-denormalization/README.md` |
| 06 | Data Compression | 📋 Planned | `05-storage/02-scaling/06-data-compression/README.md` |
| 07 | Change Data Capture (CDC) | 💡 Idea | `05-storage/02-scaling/07-cdc/README.md` |
| 08 | Bloom Filters | 💡 Idea | `05-storage/02-scaling/08-bloom-filters/README.md` |
| 09 | Quad Tree | 💡 Idea | `05-storage/02-scaling/09-quad-tree/README.md` |
| 10 | Redis Use Cases | 💡 Idea | `05-storage/02-scaling/10-redis-use-cases/README.md` |
| 11 | Data Structures in Distributed Databases | 💡 Idea | `05-storage/02-scaling/11-distributed-db-data-structures/README.md` |
| 12 | Top 15 Database Scaling Techniques | 💡 Idea | `05-storage/02-scaling/12-top-15-scaling-techniques/README.md` |

### 03 — Search Systems

| # | Topic | Status | File |
|---|---|---|---|
| 01 | Search Systems Fundamentals | 📋 Planned | `05-storage/03-search/01-search-fundamentals/README.md` |
| 02 | Full-Text Search & Inverted Index | 📋 Planned | `05-storage/03-search/02-full-text-search/README.md` |
| 03 | Elasticsearch Fundamentals | 💡 Idea | `05-storage/03-search/03-elasticsearch/README.md` |

---

## Phase 06 — Scaling & Performance

> Goal: Understand how systems grow without breaking.
> Caching and CDN land here — after storage foundations give them proper context.

| # | Topic | Status | File |
|---|---|---|---|
| 01 | Vertical vs Horizontal Scaling | 📋 Planned | `06-scaling/01-vertical-vs-horizontal/README.md` |
| 02 | Consistent Hashing | 📋 Planned | `06-scaling/02-consistent-hashing/README.md` |
| 03 | Caching | 📋 Planned | `06-scaling/03-caching/README.md` |
| 04 | Caching Strategies | 📋 Planned | `06-scaling/04-caching-strategies/README.md` |
| 05 | Read-Through vs Write-Through Cache | 📋 Planned | `06-scaling/05-read-write-through-cache/README.md` |
| 06 | Cache Eviction Policies | 📋 Planned | `06-scaling/06-cache-eviction-policies/README.md` |
| 07 | Distributed Caching | 📋 Planned | `06-scaling/07-distributed-caching/README.md` |
| 08 | Content Delivery Network (CDN) | 📋 Planned | `06-scaling/08-cdn/README.md` |
| 09 | Stateful vs Stateless Architecture | 📋 Planned | `06-scaling/09-stateful-vs-stateless/README.md` |
| 10 | Load Shedding & Backpressure | 📋 Planned | `06-scaling/10-load-shedding-backpressure/README.md` |

---

## Phase 07 — Async Communication & Events

> Goal: Learn how services decouple and communicate without waiting on each other.
> Essential foundation before microservices and distributed systems.

| # | Topic | Status | File |
|---|---|---|---|
| 01 | Synchronous vs Asynchronous Communication | 📋 Planned | `07-async/01-sync-vs-async/README.md` |
| 02 | Message Queues | 📋 Planned | `07-async/02-message-queues/README.md` |
| 03 | Producer / Consumer Pattern | 📋 Planned | `07-async/03-producer-consumer/README.md` |
| 04 | Dead-Letter Queues | 📋 Planned | `07-async/04-dead-letter-queues/README.md` |
| 05 | Pub/Sub Pattern | 📋 Planned | `07-async/05-pub-sub/README.md` |
| 06 | Fanout Pattern | 📋 Planned | `07-async/06-fanout/README.md` |
| 07 | Push vs Pull Architecture | 📋 Planned | `07-async/07-push-vs-pull/README.md` |
| 08 | Long Polling vs WebSockets | 📋 Planned | `07-async/08-long-polling-vs-websockets/README.md` |
| 09 | Event-Driven Architecture | 📋 Planned | `07-async/09-event-driven-architecture/README.md` |
| 10 | Delivery Guarantees (At-most, At-least, Exactly-once) | 📋 Planned | `07-async/10-delivery-guarantees/README.md` |
| 11 | Kafka Use Cases | 💡 Idea | `07-async/11-kafka-use-cases/README.md` |
| 12 | Batch vs Stream Processing | 📋 Planned | `07-async/12-batch-vs-stream/README.md` |
| 13 | ETL Pipelines | 📋 Planned | `07-async/13-etl-pipelines/README.md` |

---

## Phase 08 — Distributed Systems & Reliability

> Goal: Understand what happens when systems are spread across machines.
> The hardest phase — lands here because it requires everything before it.

### 01 — Consistency & Theory

| # | Topic | Status | File |
|---|---|---|---|
| 01 | What is a Distributed System? | 📋 Planned | `08-distributed/01-consistency/01-what-is-distributed/README.md` |
| 02 | Consistency Models | 📋 Planned | `08-distributed/01-consistency/02-consistency-models/README.md` |
| 03 | CAP Theorem | 📋 Planned | `08-distributed/01-consistency/03-cap-theorem/README.md` |
| 04 | PACELC Theorem | 📋 Planned | `08-distributed/01-consistency/04-pacelc-theorem/README.md` |
| 05 | Strong vs Eventual Consistency | 📋 Planned | `08-distributed/01-consistency/05-strong-vs-eventual/README.md` |

### 02 — Distributed Patterns

| # | Topic | Status | File |
|---|---|---|---|
| 01 | Heartbeats | 📋 Planned | `08-distributed/02-patterns/01-heartbeats/README.md` |
| 02 | Leader Election | 📋 Planned | `08-distributed/02-patterns/02-leader-election/README.md` |
| 03 | Gossip Protocol | 📋 Planned | `08-distributed/02-patterns/03-gossip-protocol/README.md` |
| 04 | Distributed Locking | 📋 Planned | `08-distributed/02-patterns/04-distributed-locking/README.md` |
| 05 | Distributed Transactions | 📋 Planned | `08-distributed/02-patterns/05-distributed-transactions/README.md` |
| 06 | Two-Phase Commit Protocol | 📋 Planned | `08-distributed/02-patterns/06-two-phase-commit/README.md` |
| 07 | Unique ID Generation | 📋 Planned | `08-distributed/02-patterns/07-unique-id-generation/README.md` |
| 08 | Consensus Algorithms | 💡 Idea | `08-distributed/02-patterns/08-consensus-algorithms/README.md` |
| 09 | Three-Phase Commit (3PC) | 💡 Idea | `08-distributed/02-patterns/09-three-phase-commit/README.md` |
| 10 | Vector Clocks | 💡 Idea | `08-distributed/02-patterns/10-vector-clocks/README.md` |
| 11 | CRDTs | 💡 Idea | `08-distributed/02-patterns/11-crdts/README.md` |

### 03 — Reliability Patterns

| # | Topic | Status | File |
|---|---|---|---|
| 01 | Timeouts, Retries & Backoff | 📋 Planned | `08-distributed/03-reliability/01-timeouts-retries-backoff/README.md` |
| 02 | Circuit Breaker Pattern | 📋 Planned | `08-distributed/03-reliability/02-circuit-breaker/README.md` |
| 03 | Graceful Degradation | 📋 Planned | `08-distributed/03-reliability/03-graceful-degradation/README.md` |
| 04 | Handling Failures in Distributed Systems | 💡 Idea | `08-distributed/03-reliability/04-handling-failures/README.md` |

---

## Phase 09 — Architecture & Microservices

> Goal: Bring everything together into real architectural patterns.
> Monolith vs microservices lands here — with full context from every prior phase.

| # | Topic | Status | File |
|---|---|---|---|
| 01 | Monolith vs Microservices | 📋 Planned | `09-architecture/01-monolith-vs-microservices/README.md` |
| 02 | Microservices Architecture | 📋 Planned | `09-architecture/02-microservices-architecture/README.md` |
| 03 | Service Discovery | 📋 Planned | `09-architecture/03-service-discovery/README.md` |
| 04 | SAGA Pattern | 📋 Planned | `09-architecture/04-saga-pattern/README.md` |
| 05 | Serverless Architecture | 📋 Planned | `09-architecture/05-serverless/README.md` |
| 06 | Peer-to-Peer (P2P) Architecture | 📋 Planned | `09-architecture/06-p2p-architecture/README.md` |
| 07 | Event-Driven Architecture (Advanced) | 📋 Planned | `09-architecture/07-event-driven-advanced/README.md` |
| 08 | Concurrency vs Parallelism | 💡 Idea | `09-architecture/08-concurrency-vs-parallelism/README.md` |
| 09 | Sidecar Pattern | 💡 Idea | `09-architecture/09-sidecar-pattern/README.md` |
| 10 | Service Mesh | 💡 Idea | `09-architecture/10-service-mesh/README.md` |
| 11 | MapReduce | 💡 Idea | `09-architecture/11-mapreduce/README.md` |
| 12 | Data Lakes | 💡 Idea | `09-architecture/12-data-lakes/README.md` |
| 13 | Data Warehousing | 💡 Idea | `09-architecture/13-data-warehousing/README.md` |

---

## Phase 10 — Observability & Security

> Goal: Understand how engineers watch, protect, and trust production systems.
> Observability teaches how engineers investigate "something is slow or broken."
> Security is progressive — not bolted on at the end.

### 01 — Observability

| # | Topic | Status | File |
|---|---|---|---|
| 01 | Logging | 📋 Planned | `10-observability-security/01-observability/01-logging/README.md` |
| 02 | Metrics & Monitoring | 📋 Planned | `10-observability-security/01-observability/02-metrics-monitoring/README.md` |
| 03 | Distributed Tracing | 📋 Planned | `10-observability-security/01-observability/03-distributed-tracing/README.md` |
| 04 | Alerting | 📋 Planned | `10-observability-security/01-observability/04-alerting/README.md` |
| 05 | Chaos Engineering | 💡 Idea | `10-observability-security/01-observability/05-chaos-engineering/README.md` |

### 02 — Security

| # | Topic | Status | File |
|---|---|---|---|
| 01 | Authentication & Authorization | 📋 Planned | `10-observability-security/02-security/01-auth/README.md` |
| 02 | OAuth & OAuth2 | 📋 Planned | `10-observability-security/02-security/02-oauth/README.md` |
| 03 | JWT | 📋 Planned | `10-observability-security/02-security/03-jwt/README.md` |
| 04 | SSL / TLS | 📋 Planned | `10-observability-security/02-security/04-ssl-tls/README.md` |
| 05 | HTTPS & Certificate Authorities | 📋 Planned | `10-observability-security/02-security/05-https-ca/README.md` |
| 06 | API Security (Keys, HMAC, Signing) | 📋 Planned | `10-observability-security/02-security/06-api-security/README.md` |
| 07 | Abuse Prevention & Threat Modeling | 📋 Planned | `10-observability-security/02-security/07-abuse-prevention/README.md` |
| 08 | RBAC | 💡 Idea | `10-observability-security/02-security/08-rbac/README.md` |

---

## Phase 11 — Interview Preparation

> Goal: Apply everything learned to real interview scenarios and system design questions.

### 01 — Tips & Strategy

| # | Topic | Status | File |
|---|---|---|---|
| 01 | How to Answer a System Design Interview Problem | 📋 Planned | `11-interview/01-tips/01-how-to-answer/README.md` |
| 02 | How to Estimate Scale (Back-of-envelope) | 📋 Planned | `11-interview/01-tips/02-scale-estimation/README.md` |
| 03 | How to Choose the Right Database | 📋 Planned | `11-interview/01-tips/03-choosing-databases/README.md` |
| 04 | 15 Golden System Design Interview Tips | 📋 Planned | `11-interview/01-tips/04-golden-tips/README.md` |

### 02 — Interview Questions

| # | Topic | Status | File |
|---|---|---|---|
| 01 | Design a URL Shortener | 💡 Idea | `11-interview/02-questions/01-url-shortener/README.md` |
| 02 | Design WhatsApp | 💡 Idea | `11-interview/02-questions/02-whatsapp/README.md` |
| 03 | Design Instagram | 💡 Idea | `11-interview/02-questions/03-instagram/README.md` |
| 04 | Design Spotify | 💡 Idea | `11-interview/02-questions/04-spotify/README.md` |
| 05 | Design YouTube | 💡 Idea | `11-interview/02-questions/05-youtube/README.md` |
| 06 | Design Uber | 💡 Idea | `11-interview/02-questions/06-uber/README.md` |
| 07 | Design Google Docs | 💡 Idea | `11-interview/02-questions/07-google-docs/README.md` |
| 08 | Design a Social Media News Feed | 💡 Idea | `11-interview/02-questions/08-news-feed/README.md` |
| 09 | Design a Proximity Service (like Yelp) | 💡 Idea | `11-interview/02-questions/09-proximity-service/README.md` |
| 10 | Design a Distributed Rate Limiter | 💡 Idea | `11-interview/02-questions/10-rate-limiter/README.md` |
| 11 | Design a Real-Time Gaming Leaderboard | 💡 Idea | `11-interview/02-questions/11-leaderboard/README.md` |
| 12 | Design a Web Crawler | 💡 Idea | `11-interview/02-questions/12-web-crawler/README.md` |
| 13 | Design a Scalable Notification Service | 💡 Idea | `11-interview/02-questions/13-notification-service/README.md` |
| 14 | Design a Distributed Key-Value Store | 💡 Idea | `11-interview/02-questions/14-key-value-store/README.md` |
| 15 | Design a Scalable Likes Counting System | 💡 Idea | `11-interview/02-questions/15-likes-counting/README.md` |
| 16 | Design a Distributed Job Scheduler | 💡 Idea | `11-interview/02-questions/16-job-scheduler/README.md` |
| 17 | Design a Unique ID Generator | 💡 Idea | `11-interview/02-questions/17-unique-id-generator/README.md` |

---

## Progress Summary

| Phase | Name | Total | ✅ Done | 🚧 In Progress | 📋 Planned | 💡 Idea |
|---|---|---|---|---|---|---|
| 01 | Introduction | 7 | 7 | 0 | 0 | 0 |
| 02 | Core System Properties | 5 | 1 | 1 | 3 | 0 |
| 03 | Networking | 7 | 0 | 0 | 6 | 1 |
| 04 | APIs & Communication | 15 | 0 | 0 | 14 | 1 |
| 05 | Storage & Databases | 27 | 0 | 0 | 19 | 8 |
| 06 | Scaling & Performance | 10 | 0 | 0 | 10 | 0 |
| 07 | Async & Events | 13 | 0 | 0 | 12 | 1 |
| 08 | Distributed Systems | 19 | 0 | 0 | 15 | 4 |
| 09 | Architecture & Microservices | 13 | 0 | 0 | 7 | 6 |
| 10 | Observability & Security | 13 | 0 | 0 | 11 | 2 |
| 11 | Interview Preparation | 21 | 0 | 0 | 4 | 17 |
| **Total** | | **150** | **8** | **1** | **101** | **40** |

---

*Last updated: 2026-07-13*