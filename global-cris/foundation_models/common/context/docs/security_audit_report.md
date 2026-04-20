# Security Audit Report — AnyCompany E-Commerce Platform

## Audit Period: 2026-Q1
## Classification: CONFIDENTIAL
## Auditor: Internal Security Team
## Status: 14 findings (4 Critical, 5 High, 3 Medium, 2 Low)

---

## Executive Summary

This report documents the findings from the Q1 2026 security audit of the e-commerce platform. The audit covered application security, infrastructure security, data protection, access controls, and compliance posture. Testing included automated scanning (SAST, DAST, SCA), manual penetration testing, architecture review, and configuration audit.

**Overall Risk Rating: HIGH** — 4 critical findings require immediate remediation.

---

## 1. Critical Findings

### FINDING-001: SQL Injection in Product Search (CRITICAL)

**Component:** Product Catalog Service (`/api/v1/products?search=`)
**CVSS Score:** 9.8 (Critical)
**Status:** OPEN — Remediation deadline: 2026-04-01

**Description:**
The product search endpoint constructs SQL queries using string concatenation for the `sort_by` parameter. While the `search` parameter uses parameterized queries correctly, the `sort_by` field is directly interpolated into the ORDER BY clause without validation.

**Vulnerable Code:**
```python
# product_service/search.py line 142
async def search_products(query: str, sort_by: str = "created_at", order: str = "desc"):
    # VULNERABLE: sort_by is user-controlled and not validated
    sql = f"""
        SELECT * FROM products 
        WHERE to_tsvector('english', name || ' ' || description) @@ plainto_tsquery($1)
        ORDER BY {sort_by} {order}
        LIMIT $2 OFFSET $3
    """
    return await db.fetch(sql, query, limit, offset)
```

**Proof of Concept:**
```
GET /api/v1/products?search=laptop&sort_by=created_at;DROP TABLE products;--
GET /api/v1/products?search=laptop&sort_by=(SELECT password_hash FROM users LIMIT 1)
```

**Impact:**
- Full database read access (all user data, payment tokens, orders)
- Database modification/deletion
- Potential RCE via PostgreSQL `COPY TO PROGRAM`
- Affects all 50,000+ users

**Remediation:**
1. Implement allowlist validation for `sort_by` parameter
2. Use parameterized queries for all dynamic SQL
3. Add input validation middleware
4. Deploy WAF rule to block SQL injection patterns

```python
# FIXED version
ALLOWED_SORT_FIELDS = {"created_at", "updated_at", "name", "price_cents", "rating"}
ALLOWED_ORDERS = {"asc", "desc"}

async def search_products(query: str, sort_by: str = "created_at", order: str = "desc"):
    if sort_by not in ALLOWED_SORT_FIELDS:
        raise ValidationError(f"Invalid sort field. Allowed: {ALLOWED_SORT_FIELDS}")
    if order not in ALLOWED_ORDERS:
        raise ValidationError("Order must be 'asc' or 'desc'")
    
    sql = f"""
        SELECT * FROM products 
        WHERE to_tsvector('english', name || ' ' || description) @@ plainto_tsquery($1)
        ORDER BY {sort_by} {order}
        LIMIT $2 OFFSET $3
    """
    return await db.fetch(sql, query, limit, offset)
```

---

### FINDING-002: Broken Object-Level Authorization (CRITICAL)

**Component:** Order Service (`/api/v1/orders/{id}`)
**CVSS Score:** 9.1 (Critical)
**Status:** OPEN — Remediation deadline: 2026-04-01

**Description:**
The order detail endpoint validates that the requesting user is authenticated but does not verify that the user owns the requested order. Any authenticated user can access any order by ID.

**Vulnerable Code:**
```java
// OrderController.java line 87
@GetMapping("/api/v1/orders/{id}")
@PreAuthorize("isAuthenticated()")  // Only checks authentication, not authorization
public ResponseEntity<OrderDTO> getOrder(@PathVariable UUID id) {
    Order order = orderRepository.findById(id)
        .orElseThrow(() -> new NotFoundException("Order not found"));
    return ResponseEntity.ok(orderMapper.toDTO(order));
}
```

**Proof of Concept:**
```bash
# User A's token accessing User B's order
curl -H "Authorization: Bearer <user_a_token>" \
     https://api.example.com/api/v1/orders/b7f3a2d1-user-b-order-id
# Returns full order details including shipping address, payment info
```

**Impact:**
- Any authenticated user can view any order (PII exposure)
- Shipping addresses, payment method last-4, order contents exposed
- Affects all 2M+ orders in the system
- GDPR/CCPA violation (unauthorized data access)

**Remediation:**
```java
// FIXED version
@GetMapping("/api/v1/orders/{id}")
@PreAuthorize("isAuthenticated()")
public ResponseEntity<OrderDTO> getOrder(
    @PathVariable UUID id, 
    @AuthenticationPrincipal UserDetails user
) {
    Order order = orderRepository.findById(id)
        .orElseThrow(() -> new NotFoundException("Order not found"));
    
    // Verify ownership or admin role
    if (!order.getUserId().equals(user.getId()) && !user.hasRole("ADMIN")) {
        throw new ForbiddenException("Access denied");
    }
    
    return ResponseEntity.ok(orderMapper.toDTO(order));
}
```

---

### FINDING-003: Hardcoded Secrets in Container Image (CRITICAL)

**Component:** Notification Service Docker image
**CVSS Score:** 9.0 (Critical)
**Status:** REMEDIATED — Fixed 2026-02-28

**Description:**
The notification service Docker image contains hardcoded AWS credentials and API keys in environment variables baked into the image layer. These credentials have broad permissions including S3 read/write, SES send, and SNS publish.

**Evidence:**
```dockerfile
# Dockerfile (VULNERABLE - found in image layer history)
ENV AWS_ACCESS_KEY_ID=AKIA...REDACTED
ENV AWS_SECRET_ACCESS_KEY=wJal...REDACTED
ENV SENDGRID_API_KEY=SG...REDACTED
ENV FIREBASE_SERVER_KEY=AAAA...REDACTED
```

**Impact:**
- Anyone with access to the container registry can extract credentials
- Credentials grant access to: S3 buckets (customer data), SES (send emails as platform), SNS (send SMS)
- Credentials were 18 months old with no rotation

**Remediation Applied:**
1. Rotated all exposed credentials immediately
2. Migrated to AWS Secrets Manager with IAM role-based access
3. Added container image scanning (Trivy) to CI pipeline
4. Implemented secret detection pre-commit hook (gitleaks)
5. Reduced IAM permissions to least privilege

---

### FINDING-004: Server-Side Request Forgery via Webhook URL (CRITICAL)

**Component:** Notification Service (`/api/v1/webhooks`)
**CVSS Score:** 8.6 (Critical)
**Status:** OPEN — Remediation deadline: 2026-04-15

**Description:**
The webhook registration endpoint accepts arbitrary URLs without validation. When events trigger, the notification service makes HTTP requests to these URLs from within the VPC, allowing access to internal services and cloud metadata.

**Vulnerable Code:**
```python
# webhook_handler.py line 56
async def deliver_webhook(webhook_url: str, payload: dict):
    # No URL validation — accepts any scheme, host, port
    async with httpx.AsyncClient() as client:
        response = await client.post(
            webhook_url,  # User-controlled URL
            json=payload,
            timeout=10.0
        )
    return response.status_code
```

**Proof of Concept:**
```bash
# Register webhook pointing to AWS metadata service
curl -X POST https://api.example.com/api/v1/webhooks \
  -H "Authorization: Bearer <token>" \
  -d '{"url": "http://169.254.169.254/latest/meta-data/iam/security-credentials/", "events": ["order.created"]}'

# Register webhook pointing to internal Redis
curl -X POST https://api.example.com/api/v1/webhooks \
  -d '{"url": "http://redis.internal:6379/", "events": ["order.created"]}'
```

**Impact:**
- AWS IAM credentials theft via IMDS
- Internal service discovery and access
- Data exfiltration from internal databases
- Potential lateral movement within VPC

**Remediation:**
```python
# FIXED version
import ipaddress
from urllib.parse import urlparse

BLOCKED_NETWORKS = [
    ipaddress.ip_network("169.254.0.0/16"),   # Link-local (IMDS)
    ipaddress.ip_network("10.0.0.0/8"),        # Private
    ipaddress.ip_network("172.16.0.0/12"),     # Private
    ipaddress.ip_network("192.168.0.0/16"),    # Private
    ipaddress.ip_network("127.0.0.0/8"),       # Loopback
]

def validate_webhook_url(url: str) -> bool:
    parsed = urlparse(url)
    if parsed.scheme not in ("https",):
        raise ValidationError("Only HTTPS URLs are allowed")
    
    # Resolve DNS and check against blocklist
    resolved_ips = socket.getaddrinfo(parsed.hostname, parsed.port or 443)
    for _, _, _, _, sockaddr in resolved_ips:
        ip = ipaddress.ip_address(sockaddr[0])
        for network in BLOCKED_NETWORKS:
            if ip in network:
                raise ValidationError(f"URL resolves to blocked network")
    
    return True
```

---

## 2. High Findings

### FINDING-005: Insufficient Rate Limiting on Authentication (HIGH)

**Component:** User Service (`/api/v1/users/login`)
**CVSS Score:** 7.5

**Description:**
The login endpoint has rate limiting per IP (5 attempts/minute) but no per-account rate limiting. An attacker can distribute brute-force attempts across multiple IPs (botnet) to bypass the IP-based limit.

**Current Implementation:**
```python
@rate_limit(key="ip", limit=5, period=60)  # Only IP-based
async def login(request: LoginRequest):
    ...
```

**Remediation:**
```python
@rate_limit(key="ip", limit=5, period=60)
@rate_limit(key="email", limit=10, period=300)  # Add per-account limit
@rate_limit(key="ip", limit=100, period=3600)   # Add hourly IP limit
async def login(request: LoginRequest):
    ...
```

Additionally:
- Implement progressive delays (1s, 2s, 4s, 8s...)
- CAPTCHA after 3 failed attempts
- Account lockout after 10 failures (30-minute cooldown)
- Notify user of failed login attempts via email

---

### FINDING-006: Missing TLS Certificate Validation in Service-to-Service Calls (HIGH)

**Component:** All internal service communication
**CVSS Score:** 7.4

**Description:**
Internal HTTP clients disable TLS certificate verification for service-to-service calls within the VPC. This was done to avoid certificate management complexity but enables man-in-the-middle attacks if an attacker gains network access.

**Vulnerable Configuration:**
```python
# shared/http_client.py
client = httpx.AsyncClient(verify=False)  # INSECURE
```

```java
// RestTemplateConfig.java
@Bean
public RestTemplate restTemplate() {
    // Disables all certificate checks
    TrustManager[] trustAll = new TrustManager[]{new X509TrustManager() {
        public void checkClientTrusted(X509Certificate[] certs, String type) {}
        public void checkServerTrusted(X509Certificate[] certs, String type) {}
        public X509Certificate[] getAcceptedIssuers() { return new X509Certificate[0]; }
    }};
    ...
}
```

**Remediation:**
- Deploy AWS Private CA for internal certificates
- Use AWS App Mesh with mTLS enforcement
- Remove all `verify=False` / trust-all configurations
- Implement certificate rotation (90-day lifecycle)

---

### FINDING-007: Excessive IAM Permissions (HIGH)

**Component:** ECS Task Roles
**CVSS Score:** 7.2

**Description:**
Several ECS task roles have overly broad permissions. The Product Service role has `s3:*` on all buckets, and the Order Service role has `sqs:*` on all queues.

**Current Permissions (Product Service):**
```json
{
    "Effect": "Allow",
    "Action": "s3:*",
    "Resource": "*"
}
```

**Remediation (Least Privilege):**
```json
{
    "Effect": "Allow",
    "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:DeleteObject"
    ],
    "Resource": [
        "arn:aws:s3:::product-images-prod/*",
        "arn:aws:s3:::product-imports-prod/*"
    ]
}
```

---

### FINDING-008: Unencrypted PII in Elasticsearch (HIGH)

**Component:** Product Catalog Service (Elasticsearch cluster)
**CVSS Score:** 7.0

**Description:**
The Elasticsearch cluster used for product search also indexes user review data including reviewer names and email addresses. The cluster does not have encryption at rest enabled, and the data is accessible without authentication from within the VPC.

**Remediation:**
1. Enable encryption at rest (AWS managed key)
2. Enable node-to-node encryption
3. Enable fine-grained access control (FGAC)
4. Remove PII from search index (use user_id reference instead)
5. Implement field-level security to restrict PII access

---

### FINDING-009: Dependency Vulnerabilities (HIGH)

**Component:** All services
**CVSS Score:** Variable (up to 9.8)

**Description:**
Automated dependency scanning identified 23 vulnerabilities across all services:

| Severity | Count | Notable |
|----------|-------|---------|
| Critical | 3 | log4j 2.17.0 (CVE-2021-44832), jackson-databind (CVE-2022-42003) |
| High | 8 | Various npm packages with prototype pollution |
| Medium | 7 | Information disclosure in debug endpoints |
| Low | 5 | Cosmetic/informational |

**Remediation:**
- Immediate: Upgrade log4j to 2.23.0, jackson to 2.17.0
- Short-term: Enable Dependabot/Renovate for automated PRs
- Long-term: Implement SCA gate in CI (block merge on critical/high)

---

## 3. Medium Findings

### FINDING-010: Missing Security Headers (MEDIUM)

**Component:** API Gateway responses
**CVSS Score:** 5.3

**Missing Headers:**
- `Strict-Transport-Security` (HSTS)
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `Content-Security-Policy`
- `Referrer-Policy: strict-origin-when-cross-origin`
- `Permissions-Policy`

---

### FINDING-011: Verbose Error Messages in Production (MEDIUM)

**Component:** All services
**CVSS Score:** 5.0

**Description:**
Production error responses include stack traces, internal file paths, and database query details. This information aids attackers in understanding the system architecture.

**Example Response (Production):**
```json
{
    "error": "DatabaseError",
    "message": "relation \"users\" does not exist",
    "stack": "File \"/app/services/user_service.py\", line 42, in get_user\n    ...",
    "query": "SELECT * FROM users WHERE id = $1",
    "connection": "postgresql://app_user:***@db-primary.internal:5432/ecommerce"
}
```

---

### FINDING-012: Session Tokens Not Invalidated on Password Change (MEDIUM)

**Component:** User Service
**CVSS Score:** 6.5

**Description:**
When a user changes their password, existing sessions (refresh tokens) remain valid. If an account is compromised, changing the password does not revoke the attacker's session.

---

## 4. Low Findings

### FINDING-013: CORS Wildcard in Development Leaked to Staging (LOW)

**Component:** API Gateway (staging environment)
**CVSS Score:** 3.5

**Description:**
The staging environment has `Access-Control-Allow-Origin: *` configured, which was intended only for local development. While staging doesn't contain production data, it shares the same authentication system.

---

### FINDING-014: Unused Admin Endpoints Exposed (LOW)

**Component:** All services
**CVSS Score:** 3.0

**Description:**
Debug/admin endpoints (`/health/detailed`, `/metrics`, `/debug/pprof`) are accessible without authentication. While they don't expose sensitive data directly, they reveal internal system state.

---

## 5. Recommendations Summary

### Immediate (< 1 week)
1. Fix SQL injection (FINDING-001)
2. Add object-level authorization (FINDING-002)
3. Block SSRF in webhooks (FINDING-004)
4. Upgrade critical dependencies (FINDING-009)

### Short-term (< 1 month)
5. Implement per-account rate limiting (FINDING-005)
6. Enable mTLS for internal communication (FINDING-006)
7. Reduce IAM permissions to least privilege (FINDING-007)
8. Encrypt Elasticsearch and remove PII (FINDING-008)

### Medium-term (< 3 months)
9. Add security headers (FINDING-010)
10. Implement structured error handling (FINDING-011)
11. Invalidate sessions on password change (FINDING-012)
12. Fix CORS and restrict admin endpoints (FINDING-013, FINDING-014)

---

## 6. Compliance Status

| Framework | Status | Gap |
|-----------|--------|-----|
| PCI DSS Level 1 | AT RISK | FINDING-001, 003, 008 |
| SOC 2 Type II | COMPLIANT | Minor observations |
| GDPR | AT RISK | FINDING-002 (unauthorized access to PII) |
| CCPA | AT RISK | FINDING-002 |
| ISO 27001 | COMPLIANT | Surveillance audit passed |
| HIPAA | N/A | Not in scope |

---

## 7. Next Steps

1. Security team to track remediation via JIRA (project: SEC-2026-Q1)
2. Re-test critical findings after remediation (target: 2026-04-15)
3. Schedule Q2 audit (focus: payment system redesign per RFC-2026-003)
4. Update threat model with new payment architecture
5. Conduct tabletop exercise for incident response (ransomware scenario)
