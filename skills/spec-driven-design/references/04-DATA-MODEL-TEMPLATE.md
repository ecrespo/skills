# [DOMAIN NAME] — Data Model Specification

## Metadata

| Field | Value |
|---|---|
| **Author** | [Name] |
| **Status** | `DRAFT` / `IN_REVIEW` / `APPROVED` / `DEPRECATED` |
| **Version** | 1.0 |
| **Date** | YYYY-MM-DD |
| **Database** | [MongoDB 7.x / PostgreSQL 16 / etc.] |
| **Related Tech Design** | [Link to the Tech Design] |

---

## 1. Model Overview

[Description of the data domain: which entities exist, how they relate, and which access patterns take priority.]

### Relationship Diagram

```
┌──────────────┐       ┌──────────────┐       ┌──────────────┐
│    User      │──1:N─▶│   Resource   │──1:N─▶│  Transaction │
└──────────────┘       └──────┬───────┘       └──────────────┘
                              │ N:1
                       ┌──────▼───────┐
                       │   Category   │
                       └──────────────┘
```

## 2. Collections / Tables

### 2.1 `resources`

**Purpose:** [Description]
**Estimated volume:** [E.g.: ~100K documents initially, growth ~5K/month]
**Primary access pattern:** [E.g.: Frequent reads by ID and by user_id]

#### Schema

```json
{
  "_id": "ObjectId",
  "resource_id": "string (unique, format: res_xxxxx)",
  "user_id": "string (reference to users)",
  "category_id": "string (reference to categories)",
  "name": "string (required, 3-100 chars)",
  "type": "string (enum: 'TYPE_A' | 'TYPE_B' | 'TYPE_C')",
  "status": "string (enum: 'PENDING' | 'APPROVED' | 'PROCESSING' | 'COMPLETED' | 'REJECTED' | 'CANCELLED')",
  "amount": {
    "value": "Decimal128 (required, > 0)",
    "currency": "string (ISO 4217, default: 'VES')"
  },
  "metadata": {
    "source": "string (optional)",
    "reference_number": "string (optional)",
    "custom_fields": "object (flexible, max 10 keys)"
  },
  "status_history": [
    {
      "status": "string",
      "changed_at": "ISODate",
      "changed_by": "string (user_id or 'system')",
      "reason": "string (optional)"
    }
  ],
  "created_at": "ISODate",
  "updated_at": "ISODate",
  "deleted_at": "ISODate | null (soft delete)"
}
```

#### Fields: Detail

| Field | Type | Required | Default | Description |
|---|---|---|---|---|
| `_id` | ObjectId | Auto | Auto | Internal MongoDB ID |
| `resource_id` | string | Yes | Generated | Public ID, format `res_` + nanoid(12) |
| `user_id` | string | Yes | — | Reference to the owning user |
| `name` | string | Yes | — | Human-readable name, 3-100 characters |
| `type` | string | Yes | — | Resource type (defined enum) |
| `status` | string | Yes | `PENDING` | Current lifecycle state |
| `amount.value` | Decimal128 | Yes | — | Numeric amount with decimal precision |
| `amount.currency` | string | Yes | `VES` | ISO 4217 currency code |

#### Indexes

| Name | Fields | Type | Justification |
|---|---|---|---|
| `idx_resource_id` | `{ resource_id: 1 }` | Unique | Lookup by public ID |
| `idx_user_status` | `{ user_id: 1, status: 1 }` | Compound | Query: "resources of user X with status Y" |
| `idx_created_at` | `{ created_at: -1 }` | Single | Pagination and sorting by date |
| `idx_type_status` | `{ type: 1, status: 1, created_at: -1 }` | Compound | Dashboard: filters by type + status |

**Note on indexes:** Field order in a compound index matters. Put equality fields first, then range, then sort.

#### Database-Level Validations

```javascript
db.createCollection("resources", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["resource_id", "user_id", "name", "type", "status", "amount", "created_at"],
      properties: {
        resource_id: { bsonType: "string", pattern: "^res_[a-zA-Z0-9]{12}$" },
        status: { enum: ["PENDING", "APPROVED", "PROCESSING", "COMPLETED", "REJECTED", "CANCELLED"] },
        "amount.value": { bsonType: "decimal" },
        "amount.currency": { bsonType: "string", minLength: 3, maxLength: 3 }
      }
    }
  }
});
```

---

## 3. Entity Relationships

| From | To | Type | FK Field | Description |
|---|---|---|---|---|
| `resources` | `users` | N:1 | `user_id` | Each resource belongs to a user |
| `transactions` | `resources` | N:1 | `resource_id` | Each transaction operates on a resource |

**Note:** MongoDB does not natively enforce foreign keys. Integrity is guaranteed at the application level.

## 4. Critical Queries

### Q1: Get resource by public ID

```javascript
db.resources.findOne({ resource_id: "res_abc123", deleted_at: null })
// Index: idx_resource_id | Frequency: ~10K/day | Target: < 5ms
```

### Q2: List a user's resources with filters

```javascript
db.resources.find({ user_id: "usr_xyz", status: "PENDING", deleted_at: null })
  .sort({ created_at: -1 }).limit(20)
// Index: idx_user_status | Frequency: ~5K/day | Target: < 20ms
```

### Q3: Dashboard — aggregation by type and status

```javascript
db.resources.aggregate([
  { $match: { deleted_at: null, created_at: { $gte: ISODate("2026-03-01") } } },
  { $group: { _id: { type: "$type", status: "$status" }, count: { $sum: 1 }, total: { $sum: "$amount.value" } } }
])
// Index: idx_type_status | Frequency: ~100/day | Target: < 500ms
```

## 5. Data Migration

### 5.1 Migration Scripts

Scripts live in `scripts/migrations/` with format: `YYYY-MM-DD_description.js`

Each script has `up()` and `down()` functions.

### 5.2 Migration Rollback

Always document the reverse script for each migration.

## 6. Archiving Strategies

| Collection | Archiving Criterion | Destination | Frequency |
|---|---|---|---|
| `transactions` | `completed_at` > 90 days | `transactions_archive` | Monthly |
| `resources` | COMPLETED + `updated_at` > 1 year | Cold storage | Quarterly |

## 7. Backup and Recovery

| Aspect | Configuration |
|---|---|
| **Full backup** | [E.g.: Daily, mongodump to S3] |
| **Incremental backup** | [E.g.: Continuous oplog] |
| **Retention** | [E.g.: 30 days full, 7 days incremental] |
| **RPO** | [E.g.: < 1 hour] |
| **RTO** | [E.g.: < 4 hours] |

---

## Change History

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.0 | YYYY-MM-DD | [Name] | Initial version |
