# [API NAME] — API Specification

## Metadata

| Field               | Value                                             |
| ------------------- | ------------------------------------------------- |
| **Author**          | [Name]                                            |
| **Status**          | `DRAFT` / `IN_REVIEW` / `APPROVED` / `DEPRECATED` |
| **API Version**     | v1.0                                              |
| **Date**            | YYYY-MM-DD                                        |
| **Related PRD**     | [Link to the PRD]                                 |
| **Base URL**        | `https://api.example.com/v1`                      |

---

## 1. Overview

[Description of the API's purpose and its main consumers]

## 2. Authentication and Authorization

### Authentication Method

```
Authorization: Bearer <token>
```

### Roles and Permissions

| Role       | Description   | Allowed Endpoints    |
| ---------- | ------------- | -------------------- |
| `admin`    | [Description] | All                  |
| `operator` | [Description] | [List of endpoints]  |
| `viewer`   | [Description] | GET only             |

### Obtaining a Token

```http
POST /auth/token
Content-Type: application/json

{
  "client_id": "string",
  "client_secret": "string",
  "grant_type": "client_credentials"
}
```

**Successful response (200):**

```json
{
  "access_token": "eyJhbG...",
  "token_type": "Bearer",
  "expires_in": 3600
}
```

## 3. General Conventions

### Response Format

```json
{
  "success": true,
  "data": { },
  "meta": {
    "request_id": "uuid-v4",
    "timestamp": "ISO-8601"
  }
}
```

### Error Format

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE_DOMAIN",
    "message": "Developer-readable description",
    "details": [
      {
        "field": "field_name",
        "issue": "Description of the problem"
      }
    ]
  },
  "meta": {
    "request_id": "uuid-v4",
    "timestamp": "ISO-8601"
  }
}
```

### Domain Error Codes

| Code                 | HTTP Status | Description                                 |
| -------------------- | ----------- | ------------------------------------------- |
| `VALIDATION_ERROR`   | 400         | Invalid input data                          |
| `UNAUTHORIZED`       | 401         | Invalid or expired token                    |
| `FORBIDDEN`          | 403         | Insufficient permissions                    |
| `RESOURCE_NOT_FOUND` | 404         | Resource not found                          |
| `CONFLICT`           | 409         | Conflicting state (e.g.: duplicate payment) |
| `RATE_LIMITED`       | 429         | Too many requests                           |
| `INTERNAL_ERROR`     | 500         | Internal server error                       |

### Pagination

```http
GET /resources?page=1&page_size=20&sort_by=created_at&sort_order=desc
```

**Response:**

```json
{
  "data": [...],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total_items": 150,
    "total_pages": 8,
    "has_next": true,
    "has_prev": false
  }
}
```

### Required Headers

| Header             | Value                  | Required    |
| ------------------ | ---------------------- | ----------- |
| `Content-Type`     | `application/json`     | Yes         |
| `Authorization`    | `Bearer <token>`       | Yes         |
| `X-Request-ID`     | UUID v4 (idempotency)  | Recommended |
| `X-Client-Version` | Client version         | Optional    |

## 4. Endpoints

---

### 4.1 `POST /resources`

**Description:** Creates a new resource.

**Required roles:** `admin`, `operator`

**Request Body:**

```json
{
  "name": "string (required, 3-100 chars)",
  "type": "string (enum: 'TYPE_A' | 'TYPE_B' | 'TYPE_C')",
  "amount": "number (required, > 0, max 2 decimal places)",
  "metadata": {
    "key": "string (optional)"
  }
}
```

**Validations:**

| Field | Rule | Error on failure |
|---|---|---|
| `name` | Required, 3-100 characters | `VALIDATION_ERROR` |
| `type` | Must be one of the defined enum values | `VALIDATION_ERROR` |
| `amount` | Required, positive, max 2 decimal places | `VALIDATION_ERROR` |

**Successful response (201):**

```json
{
  "success": true,
  "data": {
    "id": "res_abc123",
    "name": "Example",
    "type": "TYPE_A",
    "amount": 150.50,
    "status": "PENDING",
    "created_at": "2026-03-01T10:00:00Z",
    "updated_at": "2026-03-01T10:00:00Z"
  }
}
```

**Possible errors:**

| Status | Code | When |
|---|---|---|
| 400 | `VALIDATION_ERROR` | Invalid fields |
| 401 | `UNAUTHORIZED` | Invalid token |
| 409 | `CONFLICT` | Duplicate resource |

**cURL example:**

```bash
curl -X POST https://api.example.com/v1/resources \
  -H "Authorization: Bearer eyJhbG..." \
  -H "Content-Type: application/json" \
  -H "X-Request-ID: 550e8400-e29b-41d4-a716-446655440000" \
  -d '{
    "name": "Example",
    "type": "TYPE_A",
    "amount": 150.50
  }'
```

---

### 4.2 `GET /resources`

**Description:** Lists resources with filters and pagination.

**Required roles:** `admin`, `operator`, `viewer`

**Query Parameters:**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `page` | integer | 1 | Page number |
| `page_size` | integer | 20 | Items per page (max 100) |
| `status` | string | — | Filter by status |
| `type` | string | — | Filter by type |
| `created_after` | ISO-8601 | — | Filter by creation date |
| `created_before` | ISO-8601 | — | Filter by creation date |
| `sort_by` | string | `created_at` | Sort field |
| `sort_order` | string | `desc` | `asc` or `desc` |
| `search` | string | — | Text search on name |

---

### 4.3 `GET /resources/{id}`

**Description:** Retrieves a resource by its ID.

**Path Parameters:**

| Parameter | Type | Description |
|---|---|---|
| `id` | string | Unique resource ID (format: `res_xxxxx`) |

---

### 4.4 `PATCH /resources/{id}`

**Description:** Partially updates a resource.

**Note:** The `type`, `amount`, and `status` fields are not directly editable. Status changes happen through specific actions.

---

### 4.5 `POST /resources/{id}/actions/{action}`

**Description:** Executes an action that changes the resource's state.

**Available actions:**

| Action | Description | Required Status | Resulting Status | Minimum Role |
|---|---|---|---|---|
| `approve` | Approves the resource | `PENDING` | `APPROVED` | `admin` |
| `reject` | Rejects the resource | `PENDING` | `REJECTED` | `admin` |
| `process` | Starts processing | `APPROVED` | `PROCESSING` | `operator` |
| `complete` | Marks as completed | `PROCESSING` | `COMPLETED` | `system` |
| `cancel` | Cancels the resource | `PENDING`, `APPROVED` | `CANCELLED` | `operator` |

**State Diagram:**

```
                 ┌──────────┐
                 │ PENDING  │
                 └────┬─────┘
              ┌───────┼───────┐
              ▼       │       ▼
        ┌──────────┐  │  ┌──────────┐
        │ APPROVED │  │  │ REJECTED │
        └────┬─────┘  │  └──────────┘
             │        │
             ▼        ▼
       ┌───────────┐ ┌───────────┐
       │PROCESSING │ │ CANCELLED │
       └─────┬─────┘ └───────────┘
             │
             ▼
       ┌───────────┐
       │ COMPLETED │
       └───────────┘
```

---

## 5. Webhooks (if applicable)

| Event | Description | Payload |
|---|---|---|
| `resource.created` | Resource created | Full resource object |
| `resource.status_changed` | Status change | Object with old/new status |
| `resource.completed` | Resource completed | Full resource object |

## 6. Rate Limiting

| Tier | Limit | Window |
|---|---|---|
| Standard | 100 requests | Per minute |
| Premium | 1000 requests | Per minute |
| Burst | 10 requests | Per second |

## 7. Versioning

The API uses URL-path versioning: `/v1/`, `/v2/`.

Deprecation policy: previous versions are maintained for 12 months after a new major version is published.

---

## Change History

| Version | Date | Changes |
|---|---|---|
| 1.0 | YYYY-MM-DD | Initial version |
