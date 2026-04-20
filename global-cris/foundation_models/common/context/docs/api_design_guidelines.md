# API Design Guidelines & Standards

## Version: 3.0
## Last Updated: 2026-03-01
## Owner: Platform Architecture Team

---

## 1. General Principles

### 1.1 RESTful Design

All APIs MUST follow REST architectural constraints:
- **Client-Server:** Clear separation of concerns
- **Stateless:** Each request contains all information needed to process it
- **Cacheable:** Responses must define themselves as cacheable or non-cacheable
- **Uniform Interface:** Consistent resource identification and manipulation
- **Layered System:** Client cannot tell whether connected directly to server

### 1.2 API-First Development

1. Design the API contract (OpenAPI 3.1 spec) before implementation
2. Review API design with consumers before coding
3. Generate server stubs and client SDKs from the spec
4. Validate implementation against spec in CI (spectral linting)

### 1.3 Versioning Strategy

- **URL path versioning:** `/api/v1/resources`, `/api/v2/resources`
- Major version in URL path (breaking changes only)
- Minor/patch versions via response headers (`X-API-Version: 1.3.2`)
- Deprecation: 6-month notice via `Sunset` header (RFC 8594)
- Maximum 2 major versions supported simultaneously

---

## 2. URL Design

### 2.1 Resource Naming

| Rule | Good | Bad |
|------|------|-----|
| Use nouns, not verbs | `/api/v1/orders` | `/api/v1/getOrders` |
| Use plural nouns | `/api/v1/users` | `/api/v1/user` |
| Use kebab-case | `/api/v1/order-items` | `/api/v1/orderItems` |
| Nest for relationships | `/api/v1/users/{id}/orders` | `/api/v1/user-orders` |
| Max 3 levels deep | `/api/v1/users/{id}/orders` | `/api/v1/users/{id}/orders/{oid}/items/{iid}/reviews` |
| Use query params for filtering | `/api/v1/orders?status=shipped` | `/api/v1/shipped-orders` |

### 2.2 Standard URL Patterns

```
GET    /api/v1/{resources}              → List (with pagination, filtering)
POST   /api/v1/{resources}              → Create
GET    /api/v1/{resources}/{id}         → Read
PUT    /api/v1/{resources}/{id}         → Replace (full update)
PATCH  /api/v1/{resources}/{id}         → Partial update
DELETE /api/v1/{resources}/{id}         → Delete

GET    /api/v1/{resources}/{id}/{sub}   → List sub-resources
POST   /api/v1/{resources}/{id}/{sub}   → Create sub-resource

POST   /api/v1/{resources}/{id}/actions/{action}  → Custom action (RPC-style)
```

### 2.3 Query Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `page` | integer | Page number (1-indexed) | `?page=3` |
| `per_page` | integer | Items per page (max 100) | `?per_page=50` |
| `sort` | string | Sort field with direction | `?sort=-created_at` (desc) |
| `filter[field]` | string | Filter by field value | `?filter[status]=active` |
| `filter[field][op]` | string | Filter with operator | `?filter[price][gte]=1000` |
| `fields` | string | Sparse fieldset | `?fields=id,name,status` |
| `include` | string | Related resources | `?include=author,comments` |
| `search` | string | Full-text search | `?search=laptop` |

**Filter Operators:**
- `eq` (default): Equal
- `neq`: Not equal
- `gt`, `gte`: Greater than (or equal)
- `lt`, `lte`: Less than (or equal)
- `in`: In list (`?filter[status][in]=active,pending`)
- `nin`: Not in list
- `like`: Pattern match (`?filter[name][like]=*phone*`)
- `exists`: Field exists (`?filter[deleted_at][exists]=false`)

---

## 3. Request Format

### 3.1 Headers

**Required Headers:**
```
Content-Type: application/json
Accept: application/json
Authorization: Bearer <token>
X-Request-ID: <uuid>          # Client-generated, for tracing
X-Idempotency-Key: <uuid>     # Required for POST/PUT/PATCH
```

**Optional Headers:**
```
Accept-Language: en-US         # Localization
X-Tenant-ID: <uuid>           # Multi-tenant routing
If-None-Match: "<etag>"       # Conditional GET (caching)
If-Match: "<etag>"            # Conditional PUT/PATCH (optimistic locking)
Prefer: return=minimal        # Skip response body on write
```

### 3.2 Request Body

**JSON:API-inspired envelope:**
```json
{
    "data": {
        "type": "orders",
        "attributes": {
            "shipping_address": {...},
            "items": [...]
        },
        "relationships": {
            "customer": {"data": {"type": "users", "id": "uuid"}},
            "merchant": {"data": {"type": "merchants", "id": "uuid"}}
        }
    }
}
```

**Simplified format (for simpler APIs):**
```json
{
    "name": "Product Name",
    "price_cents": 2999,
    "category_id": "uuid"
}
```

Decision: Use simplified format unless the API has complex relationships.

### 3.3 Validation Rules

| Rule | Implementation | Error Code |
|------|---------------|------------|
| Required fields | Schema validation | `FIELD_REQUIRED` |
| Type checking | Schema validation | `FIELD_TYPE_INVALID` |
| String length | min/max in schema | `FIELD_TOO_SHORT` / `FIELD_TOO_LONG` |
| Numeric range | min/max in schema | `FIELD_OUT_OF_RANGE` |
| Pattern match | regex in schema | `FIELD_FORMAT_INVALID` |
| Enum values | enum in schema | `FIELD_VALUE_INVALID` |
| Unique constraint | Database | `RESOURCE_ALREADY_EXISTS` |
| Foreign key | Database/service call | `RELATED_RESOURCE_NOT_FOUND` |
| Business rules | Application logic | `BUSINESS_RULE_VIOLATION` |

---

## 4. Response Format

### 4.1 Success Responses

**Single Resource (200 OK / 201 Created):**
```json
{
    "data": {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "type": "orders",
        "attributes": {
            "order_number": "ORD-2026-001234",
            "status": "confirmed",
            "total_cents": 15999,
            "created_at": "2026-04-20T10:30:00Z"
        },
        "relationships": {
            "customer": {"data": {"type": "users", "id": "uuid"}},
            "items": {"data": [{"type": "order_items", "id": "uuid"}]}
        },
        "links": {
            "self": "/api/v1/orders/550e8400-e29b-41d4-a716-446655440000"
        }
    },
    "meta": {
        "request_id": "req_abc123",
        "processing_time_ms": 45
    }
}
```

**Collection (200 OK):**
```json
{
    "data": [...],
    "meta": {
        "total_count": 1234,
        "page": 3,
        "per_page": 20,
        "total_pages": 62,
        "request_id": "req_abc123"
    },
    "links": {
        "self": "/api/v1/orders?page=3&per_page=20",
        "first": "/api/v1/orders?page=1&per_page=20",
        "prev": "/api/v1/orders?page=2&per_page=20",
        "next": "/api/v1/orders?page=4&per_page=20",
        "last": "/api/v1/orders?page=62&per_page=20"
    }
}
```

**No Content (204):**
Used for successful DELETE or when `Prefer: return=minimal` is set.

### 4.2 Error Responses

**Standard Error Format (RFC 7807 Problem Details):**
```json
{
    "type": "https://api.example.com/errors/validation-error",
    "title": "Validation Failed",
    "status": 422,
    "detail": "Request body has 2 invalid fields.",
    "instance": "/api/v1/orders",
    "request_id": "req_abc123",
    "errors": [
        {
            "field": "shipping_address.postal_code",
            "code": "FIELD_FORMAT_INVALID",
            "message": "Postal code must be 5 or 9 digits",
            "meta": {"pattern": "^\\d{5}(-\\d{4})?$"}
        },
        {
            "field": "items[0].quantity",
            "code": "FIELD_OUT_OF_RANGE",
            "message": "Quantity must be between 1 and 999",
            "meta": {"min": 1, "max": 999, "actual": 0}
        }
    ],
    "documentation_url": "https://docs.example.com/errors/validation-error"
}
```

### 4.3 HTTP Status Codes

| Code | Meaning | When to Use |
|------|---------|-------------|
| 200 | OK | Successful GET, PUT, PATCH |
| 201 | Created | Successful POST (resource created) |
| 202 | Accepted | Async operation started |
| 204 | No Content | Successful DELETE |
| 207 | Multi-Status | Batch operations with mixed results |
| 301 | Moved Permanently | Resource URL changed permanently |
| 304 | Not Modified | Conditional GET, resource unchanged |
| 400 | Bad Request | Malformed request syntax |
| 401 | Unauthorized | Missing or invalid authentication |
| 403 | Forbidden | Authenticated but insufficient permissions |
| 404 | Not Found | Resource doesn't exist |
| 405 | Method Not Allowed | HTTP method not supported for resource |
| 409 | Conflict | Resource state conflict (duplicate, version mismatch) |
| 410 | Gone | Resource permanently deleted |
| 412 | Precondition Failed | If-Match ETag mismatch |
| 413 | Payload Too Large | Request body exceeds limit |
| 415 | Unsupported Media Type | Wrong Content-Type |
| 422 | Unprocessable Entity | Semantic validation error |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Unexpected server error |
| 502 | Bad Gateway | Upstream service failure |
| 503 | Service Unavailable | Maintenance or overload |
| 504 | Gateway Timeout | Upstream service timeout |

---

## 5. Authentication & Authorization

### 5.1 Authentication Schemes

| Scheme | Use Case | Token Lifetime |
|--------|----------|----------------|
| Bearer (JWT) | User sessions | 15 minutes |
| API Key | Service-to-service, CI/CD | 90 days (rotatable) |
| OAuth 2.0 Client Credentials | Third-party integrations | 1 hour |
| Webhook Signature (HMAC-SHA256) | Inbound webhooks | Per-request |

### 5.2 JWT Claims

```json
{
    "iss": "https://auth.example.com",
    "sub": "user_uuid",
    "aud": "https://api.example.com",
    "exp": 1713600000,
    "iat": 1713599100,
    "jti": "unique_token_id",
    "scope": "orders:read orders:write products:read",
    "roles": ["customer"],
    "tenant_id": "tenant_uuid",
    "email": "user@example.com",
    "email_verified": true
}
```

### 5.3 Permission Model

**RBAC + Resource-Based:**
```
Permission = Role × Action × Resource Type × Ownership

Examples:
- customer:read:orders:own        → Can read own orders
- customer:create:reviews:own     → Can create reviews for purchased products
- merchant:read:orders:own        → Can read orders for own products
- merchant:update:products:own    → Can update own products
- admin:*:*:*                     → Full access
- support:read:orders:*           → Can read any order
- support:update:orders:*         → Can update any order status
```

---

## 6. Rate Limiting

### 6.1 Limits by Tier

| Tier | Requests/minute | Requests/hour | Burst |
|------|----------------|---------------|-------|
| Free | 60 | 1,000 | 10 |
| Basic | 300 | 10,000 | 50 |
| Professional | 1,000 | 50,000 | 100 |
| Enterprise | 5,000 | 200,000 | 500 |

### 6.2 Rate Limit Headers

```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 847
X-RateLimit-Reset: 1713600060
X-RateLimit-Policy: "1000;w=60"
Retry-After: 23                    # Only on 429 responses
```

### 6.3 Cost-Based Limiting

| Operation | Cost (tokens) |
|-----------|---------------|
| GET (single) | 1 |
| GET (list, no include) | 2 |
| GET (list, with include) | 5 |
| POST/PUT/PATCH | 3 |
| DELETE | 2 |
| Bulk operations | 10 per item |
| Search (full-text) | 5 |
| File upload | 10 |

---

## 7. Pagination

### 7.1 Offset-Based (Default)

```
GET /api/v1/products?page=3&per_page=20

Response:
{
    "meta": {
        "total_count": 1234,
        "page": 3,
        "per_page": 20,
        "total_pages": 62
    }
}
```

**Limitations:** Expensive for large offsets (O(N) in database).

### 7.2 Cursor-Based (Recommended for Large Datasets)

```
GET /api/v1/audit-logs?limit=50&cursor=eyJpZCI6MTIzLCJ0cyI6MTcwNTMyfQ==

Response:
{
    "data": [...],
    "meta": {
        "has_more": true,
        "next_cursor": "eyJpZCI6MTczLCJ0cyI6MTcwNTMyfQ=="
    },
    "links": {
        "next": "/api/v1/audit-logs?limit=50&cursor=eyJpZCI6MTczLi4u"
    }
}
```

**When to use cursor-based:**
- Datasets > 10,000 records
- Real-time feeds (audit logs, notifications, events)
- When total_count is expensive to compute
- When data changes frequently (offset pagination can skip/duplicate)

---

## 8. Caching

### 8.1 Cache-Control Directives

| Resource Type | Cache-Control | ETag | Notes |
|---------------|---------------|------|-------|
| Product detail | `private, max-age=60, stale-while-revalidate=30` | Yes | Invalidate on update |
| Product list | `private, max-age=30` | No | Too dynamic for ETag |
| Category tree | `public, max-age=3600` | Yes | Rarely changes |
| User profile | `private, no-cache` | Yes | Always revalidate |
| Order detail | `private, no-store` | No | Sensitive, never cache |
| Static assets | `public, max-age=31536000, immutable` | No | Fingerprinted URLs |

### 8.2 Conditional Requests

**ETag-based:**
```
GET /api/v1/products/123
→ 200 OK
   ETag: "a3f9c2d1"

GET /api/v1/products/123
   If-None-Match: "a3f9c2d1"
→ 304 Not Modified (no body)
```

**Last-Modified-based:**
```
GET /api/v1/products/123
→ 200 OK
   Last-Modified: Wed, 20 Apr 2026 10:30:00 GMT

GET /api/v1/products/123
   If-Modified-Since: Wed, 20 Apr 2026 10:30:00 GMT
→ 304 Not Modified
```

---

## 9. Async Operations

### 9.1 Long-Running Operations Pattern

For operations that take > 5 seconds:

```
POST /api/v1/reports
→ 202 Accepted
   Location: /api/v1/jobs/job_abc123
   Retry-After: 5

GET /api/v1/jobs/job_abc123
→ 200 OK
{
    "id": "job_abc123",
    "status": "running",        // queued | running | succeeded | failed
    "progress": 0.45,
    "created_at": "2026-04-20T10:30:00Z",
    "estimated_completion": "2026-04-20T10:31:00Z",
    "result_url": null,         // Populated when succeeded
    "error": null               // Populated when failed
}

GET /api/v1/jobs/job_abc123    (after completion)
→ 200 OK
{
    "id": "job_abc123",
    "status": "succeeded",
    "progress": 1.0,
    "result_url": "/api/v1/reports/rpt_xyz789",
    "completed_at": "2026-04-20T10:30:45Z"
}
```

### 9.2 Webhook Delivery

For event-driven notifications:

```json
POST https://customer-webhook-url.com/events
Content-Type: application/json
X-Webhook-ID: evt_abc123
X-Webhook-Timestamp: 1713600000
X-Webhook-Signature: sha256=base64(HMAC-SHA256(secret, timestamp.body))

{
    "id": "evt_abc123",
    "type": "order.shipped",
    "created_at": "2026-04-20T10:30:00Z",
    "data": {
        "order_id": "uuid",
        "tracking_number": "1Z999AA10123456784",
        "carrier": "ups"
    }
}
```

**Retry Policy:**
- Attempt 1: Immediate
- Attempt 2: +1 minute
- Attempt 3: +5 minutes
- Attempt 4: +30 minutes
- Attempt 5: +2 hours
- After 5 failures: Disable webhook, notify owner

---

## 10. Security Standards

### 10.1 Input Validation

- Validate ALL input (path params, query params, headers, body)
- Use schema validation (JSON Schema / OpenAPI)
- Set maximum sizes: body (1MB), string fields (varies), arrays (100 items)
- Sanitize for XSS if rendering in HTML contexts
- Reject unexpected fields (`additionalProperties: false`)

### 10.2 Output Encoding

- Always set `Content-Type: application/json; charset=utf-8`
- Never reflect user input without encoding
- Strip internal fields from responses (stack traces, SQL, internal IDs)

### 10.3 CORS Configuration

```
Access-Control-Allow-Origin: https://app.example.com
Access-Control-Allow-Methods: GET, POST, PUT, PATCH, DELETE, OPTIONS
Access-Control-Allow-Headers: Authorization, Content-Type, X-Request-ID
Access-Control-Max-Age: 86400
Access-Control-Allow-Credentials: true
```

**Never use `Access-Control-Allow-Origin: *` with credentials.**

### 10.4 Security Headers

```
Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
Content-Security-Policy: default-src 'none'; frame-ancestors 'none'
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: camera=(), microphone=(), geolocation=()
```

---

## 11. Error Handling Best Practices

### 11.1 Error Categories

| Category | HTTP Range | Retryable | Client Action |
|----------|-----------|-----------|---------------|
| Client errors | 4xx | No (except 429) | Fix request |
| Rate limiting | 429 | Yes (after delay) | Back off, retry |
| Server errors | 5xx | Yes (with backoff) | Retry with exponential backoff |
| Timeout | 504 | Yes | Retry (check idempotency) |

### 11.2 Retry Strategy

```
max_retries = 3
base_delay = 1.0  # seconds
max_delay = 30.0

for attempt in range(max_retries):
    response = make_request()
    if response.status_code < 500 and response.status_code != 429:
        return response
    
    delay = min(base_delay * (2 ** attempt) + random(0, 0.5), max_delay)
    if response.status_code == 429:
        delay = max(delay, parse_retry_after(response))
    
    sleep(delay)

raise MaxRetriesExceeded()
```

### 11.3 Circuit Breaker

```
States: CLOSED → OPEN → HALF_OPEN → CLOSED

CLOSED: Normal operation, track failures
  → If failures > threshold (5 in 30s): transition to OPEN

OPEN: All requests fail immediately (fast-fail)
  → After timeout (60s): transition to HALF_OPEN

HALF_OPEN: Allow limited requests (3) to test recovery
  → If all succeed: transition to CLOSED
  → If any fail: transition to OPEN
```

---

## 12. Documentation Standards

### 12.1 OpenAPI Specification Requirements

Every API MUST have:
- Complete OpenAPI 3.1 spec in `openapi.yaml`
- All endpoints documented with request/response schemas
- Example values for all fields
- Error response schemas for each endpoint
- Authentication requirements per endpoint
- Rate limit documentation

### 12.2 Changelog

Maintain `CHANGELOG.md` with:
- Version number and date
- Breaking changes (with migration guide)
- New features
- Bug fixes
- Deprecations

### 12.3 SDK Generation

- Generate client SDKs from OpenAPI spec (openapi-generator)
- Supported languages: Python, TypeScript, Java, Go
- Publish to package registries (PyPI, npm, Maven, Go modules)
- Version SDKs in sync with API versions
