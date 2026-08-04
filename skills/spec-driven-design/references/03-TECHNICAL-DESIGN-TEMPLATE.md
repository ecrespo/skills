# [COMPONENT/FEATURE NAME] — Technical Design Document

## Metadata

| Field | Value |
|---|---|
| **Author** | [Name] |
| **Status** | `DRAFT` / `IN_REVIEW` / `APPROVED` / `DEPRECATED` |
| **Version** | 1.0 |
| **Date** | YYYY-MM-DD |
| **Related PRD** | [Link to the PRD] |
| **Related API Spec** | [Link to the API Spec] |
| **Reviewers** | [Names] |

---

## 1. Context

[Description of the technical context in 2-3 paragraphs. What will be built from an engineering standpoint and why the technical decisions matter.]

## 2. Technical Goals

- **Correctness:** [E.g.: Transactions must be atomic and consistent]
- **Performance:** [E.g.: p95 < 200ms for main queries]
- **Maintainability:** [E.g.: Test coverage > 80%, modular code]
- **Operability:** [E.g.: Alerts, dashboards, runbooks]

## 3. Proposed Architecture

### 3.1 High-Level Diagram

```
┌─────────────┐     ┌──────────────┐     ┌──────────────┐
│   Client     │────▶│  API Gateway │────▶│  Service A   │
│  (React)     │     │  (FastAPI)   │     │  (Worker)    │
└─────────────┘     └──────┬───────┘     └──────┬───────┘
                           │                     │
                    ┌──────▼───────┐     ┌───────▼──────┐
                    │   MongoDB    │     │  Message     │
                    │   (Primary)  │     │  Queue       │
                    └──────────────┘     └──────────────┘
```

### 3.2 Components

| Component | Technology | Responsibility |
|---|---|---|
| API Gateway | FastAPI / Python 3.13 | Routing, auth, validation |
| Service A | Python / Worker | [Specific business logic] |
| Database | MongoDB 7.x | Primary persistence |
| Message Queue | [RabbitMQ / Redis Streams] | Asynchronous processing |
| Cache | Redis | [Sessions / rate limiting / cache] |

### 3.3 Data Flow

**Flow: [Name of the main operation]**

```
1. Client sends POST /resources with payload
2. API Gateway validates JWT and permissions
3. FastAPI validates the schema with Pydantic
4. Service creates document in MongoDB with status=PENDING
5. Service publishes event to the queue: resource.created
6. Worker consumes the event and executes business logic
7. Worker updates the status in MongoDB
8. Webhook notifies the client of the status change
```

**Error / compensation flow:**

```
1. If step 4 fails → return 400/500 to the client
2. If step 6 fails → retry with exponential backoff (3 attempts)
3. If step 7 fails after retry → mark as FAILED, alert
4. Dead letter queue captures unprocessable messages
```

## 4. Design Decisions

### DD-001: [Decision name]

- **Decision:** [What was decided]
- **Context:** [What motivated this decision]
- **Alternatives evaluated:**

| Option | Pros | Cons |
|---|---|---|
| **Option A (chosen)** | [Pro 1, Pro 2] | [Con 1] |
| Option B | [Pro 1] | [Con 1, Con 2] |
| Option C | [Pro 1] | [Con 1, Con 2] |

- **Rationale:** [Why Option A was chosen]
- **Consequences:** [What this decision implies going forward]

## 5. Patterns and Conventions

### 5.1 Code Structure

```
src/
├── api/
│   ├── routes/          # Endpoint definitions
│   ├── schemas/         # Pydantic models (request/response)
│   ├── dependencies.py  # Dependency injection
│   └── middleware.py     # Auth, logging, error handling
├── core/
│   ├── config.py        # Settings with Pydantic BaseSettings
│   └── exceptions.py    # Custom domain exceptions
├── domain/
│   ├── models/          # Domain entities
│   └── services/        # Business logic
├── infrastructure/
│   ├── database/
│   │   ├── connection.py
│   │   └── repositories/
│   ├── messaging/       # Queue publisher
│   └── external/        # External integrations
├── workers/             # Queue consumers
└── tests/
    ├── unit/
    ├── integration/
    └── e2e/
```

### 5.2 Applied Patterns

| Pattern | Where | Why |
|---|---|---|
| Repository Pattern | `infrastructure/database/` | Decouple persistence logic |
| Service Layer | `domain/services/` | Centralize business logic |
| Circuit Breaker | `infrastructure/external/` | Resilience against external services |

### 5.3 Error Handling

```python
# Domain exception hierarchy
class DomainError(Exception): ...
class ValidationError(DomainError): ...      # → 400
class NotFoundError(DomainError): ...        # → 404
class ConflictError(DomainError): ...        # → 409
class ExternalServiceError(DomainError): ... # → 502
```

## 6. Security

### 6.1 Attack Surface

| Vector | Mitigation |
|---|---|
| Injection in MongoDB queries | Strict validation with Pydantic |
| Compromised JWT | Short-lived tokens (15min), rotated refresh tokens |
| Rate limiting bypass | Rate limit per IP + per user, sliding window |
| Sensitive data in logs | Automatic sanitization of sensitive fields |

### 6.2 Sensitive Data

| Data | Classification | Storage | Access |
|---|---|---|---|
| [Data] | [Classification] | [How it is stored] | [Who accesses it] |

## 7. Observability

### 7.1 Logging

```json
{
  "timestamp": "ISO-8601",
  "level": "INFO|WARN|ERROR",
  "service": "service-name",
  "request_id": "uuid",
  "user_id": "string",
  "action": "action_name",
  "duration_ms": 45,
  "status": "success|failure",
  "metadata": {}
}
```

### 7.2 Metrics

| Metric | Type | Description |
|---|---|---|
| `api_request_duration_seconds` | Histogram | Latency per endpoint |
| `api_requests_total` | Counter | Total requests per status code |
| `queue_messages_processed` | Counter | Messages processed per type |
| `external_service_errors` | Counter | External service errors |

### 7.3 Alerts

| Alert | Condition | Severity |
|---|---|---|
| High latency | p95 > 500ms for 5 min | Warning |
| Elevated error rate | > 5% 5xx errors for 5 min | Critical |
| Queue backlog | > 1000 pending messages | Warning |
| External service down | Circuit breaker open | Critical |

## 8. Testing Strategy

| Level | Coverage Target | Tools | What it covers |
|---|---|---|---|
| Unit | > 80% | pytest, unittest.mock | Business logic, validations |
| Integration | Critical flows | pytest, testcontainers | DB, queue, services |
| E2E | Happy paths | pytest, httpx | Full API end-to-end |
| Load | Benchmarks | locust / k6 | Performance under load |

## 9. Migration / Rollout Plan

### 9.1 Deployment Strategy
- [ ] Feature flag for gradual activation
- [ ] Canary deployment (10% → 50% → 100%)
- [ ] Automatic rollback if error rate > X%

### 9.2 Backward Compatibility
- [E.g.: Existing v1 endpoints are maintained for 6 months]
- [E.g.: New fields are optional in the request]

## 10. Open Questions
- [ ] [Question 1 — Owner, Deadline]
- [ ] [Question 2 — Owner, Deadline]

---

## Change History

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.0 | YYYY-MM-DD | [Name] | Initial version |
