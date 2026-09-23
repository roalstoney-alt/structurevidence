# Customer Intake Data Model

Status: **PROPOSED — NOT CREATED**
Blocker: `AUTH_REQUIRED`

This model is recorded for human review only. No production schema or database binding was created.

## Storage boundary

Recommended minimal runtime after authentication approval: Cloudflare Worker + D1. Customer-private tables must be isolated from public evidence artifacts and must never write into CML/RDL/evidence/timeline directories.

## Tables

### `customers`

| Field | Type | Rule |
|---|---|---|
| `customer_id` | TEXT | Primary key, server-generated UUID |
| `created_at` | TEXT | UTC ISO-8601 |
| `updated_at` | TEXT | UTC ISO-8601 |
| `company` | TEXT | Optional, length-limited |
| `contact_name` | TEXT | Optional, length-limited |
| `email` | TEXT | Required, normalized and validated |
| `privacy_class` | TEXT | Default `CUSTOMER_PRIVATE` |

### `requests`

| Field | Type | Rule |
|---|---|---|
| `request_id` | TEXT | Primary key, server-generated UUID |
| `created_at` | TEXT | UTC ISO-8601 |
| `updated_at` | TEXT | UTC ISO-8601 |
| `request_type` | TEXT | `VERIFY` or `CONTEXT` |
| `customer_id` | TEXT | Foreign key → `customers.customer_id` |
| `company` | TEXT | Optional snapshot of submitted context |
| `contact_name` | TEXT | Optional |
| `email` | TEXT | Required |
| `decision` | TEXT | Required for Context; decision affected for Verify |
| `claim_or_question` | TEXT | Required for Verify |
| `technical_object` | TEXT | Optional |
| `current_dependency` | TEXT | Optional |
| `alternative_considered` | TEXT | Optional |
| `decision_deadline` | TEXT | Optional ISO date |
| `case_reference` | TEXT | Optional, length-limited |
| `requested_output` | TEXT | Optional |
| `status` | TEXT | Default `SUBMITTED`; constrained vocabulary |
| `privacy_class` | TEXT | Default `CUSTOMER_PRIVATE` |
| `human_owner` | TEXT | Nullable; authenticated actor identifier |
| `research_authorization_status` | TEXT | Default `NOT_AUTHORIZED` |

Allowed request statuses: `SUBMITTED`, `UNDER_REVIEW`, `SCOPE_PROPOSED`, `AWAITING_CUSTOMER`, `AUTHORIZED`, `IN_PROGRESS`, `DELIVERED`, `CLOSED`.

Research authorization must be a separate field and human action. Request status must never implicitly authorize research.

### `request_events`

| Field | Type | Rule |
|---|---|---|
| `event_id` | TEXT | Primary key, server-generated UUID |
| `request_id` | TEXT | Foreign key → `requests.request_id` |
| `event_type` | TEXT | Constrained vocabulary |
| `event_at` | TEXT | UTC ISO-8601 |
| `actor` | TEXT | Authenticated identity or `PUBLIC_SUBMITTER` |
| `previous_state` | TEXT | JSON snapshot or null |
| `new_state` | TEXT | JSON snapshot |
| `note` | TEXT | Optional, sanitized, length-limited |

Allowed events: `REQUEST_SUBMITTED`, `STATUS_CHANGED`, `OWNER_ASSIGNED`, `SCOPE_PROPOSED`, `CUSTOMER_RESPONSE_RECEIVED`, `RESEARCH_AUTHORIZED`, `RESEARCH_STARTED`, `DELIVERABLE_SENT`, `CASE_CLOSED`.

Events are insert-only. Application code must not expose update/delete operations for this table. Material request changes and event insertion must occur in one transaction.

### `request_files`

Status: deferred. No file endpoint should be created until private object storage, authenticated access, malware/content controls, size/type limits, retention, and deletion policy are approved.

Proposed metadata only:

- `file_id`
- `request_id`
- `created_at`
- `storage_key`
- `original_name`
- `content_type`
- `byte_size`
- `sha256`
- `privacy_class = CUSTOMER_PRIVATE`
- `uploaded_by`

## API boundary after resumption

Public:

- `POST /api/requests` returns only `request_id`, `status`, and `created_at`.

Authenticated administrator:

- `GET /api/admin/requests`
- `GET /api/admin/requests/{request_id}`
- `PATCH /api/admin/requests/{request_id}`
- `POST /api/admin/requests/{request_id}/events`

Inputs require strict allowlists, size limits, normalized email/date validation, prepared statements, JSON response hardening, rate limiting, and redacted operational logging.
