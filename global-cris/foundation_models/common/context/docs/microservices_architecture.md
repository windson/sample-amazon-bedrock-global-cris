# Microservices Architecture Design Document

## 1. Overview

This document describes the architecture for a distributed e-commerce platform built on microservices. The system handles 50,000 concurrent users, processes 2 million orders per day, and maintains 99.99% uptime SLA across 3 geographic regions.

## 2. Service Decomposition

### 2.1 User Service

**Responsibility:** User registration, authentication, profile management, preferences.

**Technology Stack:**
- Runtime: Node.js 20 LTS
- Database: PostgreSQL 16 (primary), Redis 7 (sessions)
- Authentication: OAuth 2.0 + OIDC with PKCE flow
- API: REST (JSON:API spec)

**Endpoints:**

| Method | Path | Description | Auth Required |
|--------|------|-------------|---------------|
| POST | /api/v1/users | Register new user | No |
| POST | /api/v1/users/login | Authenticate user | No |
| POST | /api/v1/users/refresh | Refresh access token | Yes (refresh token) |
| GET | /api/v1/users/{id} | Get user profile | Yes |
| PATCH | /api/v1/users/{id} | Update user profile | Yes (owner or admin) |
| DELETE | /api/v1/users/{id} | Soft-delete user | Yes (admin) |
| GET | /api/v1/users/{id}/preferences | Get user preferences | Yes (owner) |
| PUT | /api/v1/users/{id}/preferences | Update preferences | Yes (owner) |
| POST | /api/v1/users/{id}/verify-email | Send verification email | Yes |
| POST | /api/v1/users/{id}/reset-password | Initiate password reset | No |
| GET | /api/v1/users/{id}/sessions | List active sessions | Yes (owner) |
| DELETE | /api/v1/users/{id}/sessions/{sid} | Revoke session | Yes (owner) |

**Data Model:**

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    email_verified BOOLEAN DEFAULT FALSE,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    phone VARCHAR(20),
    avatar_url TEXT,
    role VARCHAR(20) DEFAULT 'customer' CHECK (role IN ('customer', 'merchant', 'admin', 'support')),
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'suspended', 'deleted')),
    mfa_enabled BOOLEAN DEFAULT FALSE,
    mfa_secret VARCHAR(255),
    last_login_at TIMESTAMPTZ,
    login_attempts INTEGER DEFAULT 0,
    locked_until TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    deleted_at TIMESTAMPTZ
);

CREATE TABLE user_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    refresh_token_hash VARCHAR(255) NOT NULL,
    device_fingerprint VARCHAR(255),
    ip_address INET,
    user_agent TEXT,
    expires_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    revoked_at TIMESTAMPTZ
);

CREATE TABLE user_preferences (
    user_id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    locale VARCHAR(10) DEFAULT 'en-US',
    timezone VARCHAR(50) DEFAULT 'UTC',
    currency VARCHAR(3) DEFAULT 'USD',
    notifications_email BOOLEAN DEFAULT TRUE,
    notifications_push BOOLEAN DEFAULT TRUE,
    notifications_sms BOOLEAN DEFAULT FALSE,
    theme VARCHAR(10) DEFAULT 'system',
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

**Security Considerations:**
- Passwords hashed with Argon2id (memory: 64MB, iterations: 3, parallelism: 4)
- JWT access tokens: 15-minute TTL, RS256 signed
- Refresh tokens: 7-day TTL, rotating, stored hashed
- Rate limiting: 5 login attempts per minute per IP, account lock after 10 failures
- MFA: TOTP (RFC 6238) with backup codes

**Event Publishing:**
- `user.registered` → triggers welcome email, analytics
- `user.verified` → unlocks full platform features
- `user.login` → audit log, anomaly detection
- `user.password_changed` → revoke all sessions
- `user.deleted` → GDPR data purge pipeline

---

### 2.2 Product Catalog Service

**Responsibility:** Product CRUD, categories, search indexing, inventory sync.

**Technology Stack:**
- Runtime: Python 3.12 (FastAPI)
- Database: PostgreSQL 16 (catalog), Elasticsearch 8 (search)
- Cache: Redis 7 (product pages, category trees)
- Storage: S3 (product images, videos)

**Endpoints:**

| Method | Path | Description | Auth Required |
|--------|------|-------------|---------------|
| GET | /api/v1/products | List/search products | No |
| GET | /api/v1/products/{id} | Get product details | No |
| POST | /api/v1/products | Create product | Yes (merchant) |
| PUT | /api/v1/products/{id} | Update product | Yes (merchant owner) |
| DELETE | /api/v1/products/{id} | Archive product | Yes (merchant owner) |
| POST | /api/v1/products/{id}/images | Upload product image | Yes (merchant owner) |
| DELETE | /api/v1/products/{id}/images/{img_id} | Remove image | Yes (merchant owner) |
| GET | /api/v1/products/{id}/reviews | Get product reviews | No |
| POST | /api/v1/products/{id}/reviews | Submit review | Yes (verified purchaser) |
| GET | /api/v1/categories | List category tree | No |
| GET | /api/v1/categories/{id}/products | Products in category | No |
| POST | /api/v1/products/bulk-import | Bulk import via CSV | Yes (merchant) |
| GET | /api/v1/products/{id}/variants | List product variants | No |
| POST | /api/v1/products/{id}/variants | Create variant | Yes (merchant owner) |

**Data Model:**

```sql
CREATE TABLE products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    merchant_id UUID NOT NULL REFERENCES merchants(id),
    sku VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(500) NOT NULL,
    slug VARCHAR(500) UNIQUE NOT NULL,
    description TEXT,
    short_description VARCHAR(1000),
    price_cents BIGINT NOT NULL CHECK (price_cents >= 0),
    compare_at_price_cents BIGINT,
    cost_cents BIGINT,
    currency VARCHAR(3) DEFAULT 'USD',
    category_id UUID REFERENCES categories(id),
    brand VARCHAR(200),
    weight_grams INTEGER,
    dimensions_cm JSONB,
    tags TEXT[],
    attributes JSONB DEFAULT '{}',
    status VARCHAR(20) DEFAULT 'draft' CHECK (status IN ('draft', 'active', 'archived', 'out_of_stock')),
    visibility VARCHAR(20) DEFAULT 'public' CHECK (visibility IN ('public', 'private', 'unlisted')),
    seo_title VARCHAR(200),
    seo_description VARCHAR(500),
    featured BOOLEAN DEFAULT FALSE,
    digital BOOLEAN DEFAULT FALSE,
    taxable BOOLEAN DEFAULT TRUE,
    tax_code VARCHAR(50),
    inventory_quantity INTEGER DEFAULT 0,
    inventory_policy VARCHAR(20) DEFAULT 'deny' CHECK (inventory_policy IN ('deny', 'allow_backorder')),
    low_stock_threshold INTEGER DEFAULT 5,
    published_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE product_variants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    sku VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    price_cents BIGINT NOT NULL,
    compare_at_price_cents BIGINT,
    inventory_quantity INTEGER DEFAULT 0,
    weight_grams INTEGER,
    attributes JSONB NOT NULL DEFAULT '{}',
    image_id UUID REFERENCES product_images(id),
    position INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    parent_id UUID REFERENCES categories(id),
    name VARCHAR(200) NOT NULL,
    slug VARCHAR(200) UNIQUE NOT NULL,
    description TEXT,
    image_url TEXT,
    position INTEGER DEFAULT 0,
    level INTEGER DEFAULT 0,
    path LTREE,
    product_count INTEGER DEFAULT 0,
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE product_images (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    url TEXT NOT NULL,
    alt_text VARCHAR(500),
    width INTEGER,
    height INTEGER,
    size_bytes BIGINT,
    position INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE product_reviews (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id),
    order_id UUID NOT NULL REFERENCES orders(id),
    rating INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 5),
    title VARCHAR(200),
    body TEXT,
    verified_purchase BOOLEAN DEFAULT TRUE,
    helpful_count INTEGER DEFAULT 0,
    reported BOOLEAN DEFAULT FALSE,
    status VARCHAR(20) DEFAULT 'published' CHECK (status IN ('pending', 'published', 'rejected', 'flagged')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(product_id, user_id, order_id)
);
```

**Search Architecture:**
- Elasticsearch index with custom analyzers for product names, descriptions
- Faceted search: category, price range, brand, rating, attributes
- Autocomplete with edge-ngram tokenizer
- Synonym expansion (e.g., "laptop" → "notebook", "portable computer")
- Personalized ranking based on user purchase history and browsing behavior
- Real-time inventory status in search results via Redis cache

**Caching Strategy:**
- Product detail pages: Redis, 5-minute TTL, invalidate on update
- Category tree: Redis, 1-hour TTL, invalidate on category change
- Search results: Elasticsearch query cache, 30-second TTL
- Product images: CloudFront CDN, 24-hour TTL

---

### 2.3 Order Service

**Responsibility:** Order lifecycle management, checkout, fulfillment coordination.

**Technology Stack:**
- Runtime: Java 21 (Spring Boot 3.2)
- Database: PostgreSQL 16 (orders), Redis 7 (cart)
- Message Queue: Amazon SQS (order events)
- State Machine: AWS Step Functions (order workflow)

**Endpoints:**

| Method | Path | Description | Auth Required |
|--------|------|-------------|---------------|
| POST | /api/v1/cart/items | Add item to cart | Yes |
| GET | /api/v1/cart | Get current cart | Yes |
| PATCH | /api/v1/cart/items/{id} | Update cart item quantity | Yes |
| DELETE | /api/v1/cart/items/{id} | Remove from cart | Yes |
| POST | /api/v1/orders | Create order (checkout) | Yes |
| GET | /api/v1/orders | List user's orders | Yes |
| GET | /api/v1/orders/{id} | Get order details | Yes (owner or admin) |
| POST | /api/v1/orders/{id}/cancel | Cancel order | Yes (owner, if cancellable) |
| POST | /api/v1/orders/{id}/return | Initiate return | Yes (owner) |
| GET | /api/v1/orders/{id}/tracking | Get shipment tracking | Yes (owner) |
| POST | /api/v1/orders/{id}/refund | Process refund | Yes (admin or support) |
| GET | /api/v1/merchants/{id}/orders | Merchant order dashboard | Yes (merchant) |
| PATCH | /api/v1/orders/{id}/status | Update order status | Yes (merchant or admin) |
| POST | /api/v1/orders/{id}/notes | Add internal note | Yes (support or admin) |

**Order State Machine:**

```
┌─────────┐     ┌──────────┐     ┌────────────┐     ┌─────────┐     ┌───────────┐
│ PENDING │────▶│ CONFIRMED│────▶│ PROCESSING │────▶│ SHIPPED │────▶│ DELIVERED │
└─────────┘     └──────────┘     └────────────┘     └─────────┘     └───────────┘
     │               │                  │                 │                │
     │               │                  │                 │                │
     ▼               ▼                  ▼                 ▼                ▼
┌──────────┐   ┌──────────┐      ┌──────────┐     ┌──────────┐    ┌──────────┐
│CANCELLED │   │CANCELLED │      │CANCELLED │     │ RETURNED │    │ RETURNED │
└──────────┘   └──────────┘      └──────────┘     └──────────┘    └──────────┘
                                                                         │
                                                                         ▼
                                                                   ┌──────────┐
                                                                   │ REFUNDED │
                                                                   └──────────┘
```

**Data Model:**

```sql
CREATE TABLE orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_number VARCHAR(20) UNIQUE NOT NULL,
    user_id UUID NOT NULL REFERENCES users(id),
    merchant_id UUID NOT NULL REFERENCES merchants(id),
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    subtotal_cents BIGINT NOT NULL,
    tax_cents BIGINT NOT NULL DEFAULT 0,
    shipping_cents BIGINT NOT NULL DEFAULT 0,
    discount_cents BIGINT NOT NULL DEFAULT 0,
    total_cents BIGINT NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    shipping_address JSONB NOT NULL,
    billing_address JSONB NOT NULL,
    shipping_method VARCHAR(50),
    tracking_number VARCHAR(100),
    carrier VARCHAR(50),
    estimated_delivery DATE,
    payment_intent_id VARCHAR(255),
    payment_method VARCHAR(50),
    paid_at TIMESTAMPTZ,
    shipped_at TIMESTAMPTZ,
    delivered_at TIMESTAMPTZ,
    cancelled_at TIMESTAMPTZ,
    cancellation_reason TEXT,
    notes TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE order_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id UUID NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    product_id UUID NOT NULL,
    variant_id UUID,
    sku VARCHAR(100) NOT NULL,
    name VARCHAR(500) NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price_cents BIGINT NOT NULL,
    total_cents BIGINT NOT NULL,
    tax_cents BIGINT DEFAULT 0,
    discount_cents BIGINT DEFAULT 0,
    weight_grams INTEGER,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE order_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id UUID NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    event_type VARCHAR(50) NOT NULL,
    from_status VARCHAR(20),
    to_status VARCHAR(20),
    actor_id UUID,
    actor_type VARCHAR(20),
    description TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

**Concurrency Control:**
- Optimistic locking with version column on orders
- Inventory reservation with TTL (15 minutes during checkout)
- Idempotency keys on order creation (prevent duplicate charges)
- Distributed locks (Redis) for inventory decrement

---

### 2.4 Payment Service

**Responsibility:** Payment processing, refunds, payouts, fraud detection.

**Technology Stack:**
- Runtime: Go 1.22
- Database: PostgreSQL 16 (transactions), Redis 7 (idempotency)
- Payment Providers: Stripe (primary), PayPal (secondary)
- Fraud: Custom ML model + Stripe Radar

**Endpoints:**

| Method | Path | Description | Auth Required |
|--------|------|-------------|---------------|
| POST | /api/v1/payments/intents | Create payment intent | Yes (internal) |
| POST | /api/v1/payments/intents/{id}/confirm | Confirm payment | Yes (internal) |
| POST | /api/v1/payments/intents/{id}/cancel | Cancel payment | Yes (internal) |
| GET | /api/v1/payments/intents/{id} | Get payment status | Yes (internal) |
| POST | /api/v1/payments/refunds | Process refund | Yes (admin) |
| GET | /api/v1/payments/refunds/{id} | Get refund status | Yes (admin) |
| POST | /api/v1/payments/webhooks/stripe | Stripe webhook handler | Webhook signature |
| POST | /api/v1/payments/webhooks/paypal | PayPal webhook handler | Webhook signature |
| GET | /api/v1/merchants/{id}/payouts | List merchant payouts | Yes (merchant) |
| POST | /api/v1/merchants/{id}/payouts | Trigger manual payout | Yes (admin) |
| GET | /api/v1/payments/methods | List saved payment methods | Yes |
| DELETE | /api/v1/payments/methods/{id} | Remove payment method | Yes |

**Payment Flow:**

```
1. Order Service → POST /payments/intents (amount, currency, metadata)
2. Payment Service → Stripe: Create PaymentIntent
3. Client → Stripe.js: Confirm with card details (PCI compliant)
4. Stripe → Webhook → Payment Service: payment_intent.succeeded
5. Payment Service → Event: payment.completed
6. Order Service → Update order status to CONFIRMED
```

**Fraud Detection Rules:**
- Velocity check: Max 3 orders per hour per user
- Amount threshold: Orders > $5,000 require manual review
- Address mismatch: Billing ≠ Shipping for new accounts → flag
- Device fingerprint: New device + high value → 3D Secure required
- ML model: Real-time scoring based on 47 features (accuracy: 99.2%)

**Data Model:**

```sql
CREATE TABLE payment_intents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    external_id VARCHAR(255) UNIQUE,
    order_id UUID NOT NULL,
    user_id UUID NOT NULL,
    amount_cents BIGINT NOT NULL,
    currency VARCHAR(3) NOT NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'created',
    provider VARCHAR(20) NOT NULL DEFAULT 'stripe',
    payment_method_type VARCHAR(30),
    last_four VARCHAR(4),
    card_brand VARCHAR(20),
    fraud_score DECIMAL(5,4),
    fraud_decision VARCHAR(20) DEFAULT 'allow',
    three_d_secure BOOLEAN DEFAULT FALSE,
    idempotency_key VARCHAR(255) UNIQUE,
    metadata JSONB DEFAULT '{}',
    error_code VARCHAR(50),
    error_message TEXT,
    confirmed_at TIMESTAMPTZ,
    failed_at TIMESTAMPTZ,
    cancelled_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE refunds (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    payment_intent_id UUID NOT NULL REFERENCES payment_intents(id),
    external_id VARCHAR(255) UNIQUE,
    amount_cents BIGINT NOT NULL,
    reason VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    initiated_by UUID NOT NULL,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

CREATE TABLE merchant_payouts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    merchant_id UUID NOT NULL,
    amount_cents BIGINT NOT NULL,
    currency VARCHAR(3) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    payout_method VARCHAR(30) NOT NULL,
    bank_account_last_four VARCHAR(4),
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    order_count INTEGER NOT NULL,
    fees_cents BIGINT DEFAULT 0,
    initiated_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    failed_at TIMESTAMPTZ,
    failure_reason TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

---

### 2.5 Notification Service

**Responsibility:** Multi-channel notifications (email, push, SMS, in-app).

**Technology Stack:**
- Runtime: Python 3.12 (Celery workers)
- Database: PostgreSQL 16 (templates, preferences), Redis 7 (queue)
- Email: Amazon SES
- Push: Firebase Cloud Messaging
- SMS: Amazon SNS

**Notification Types:**

| Event | Channels | Priority | Template |
|-------|----------|----------|----------|
| Order confirmed | Email, Push | High | order_confirmed |
| Order shipped | Email, Push, SMS | High | order_shipped |
| Order delivered | Email, Push | Medium | order_delivered |
| Payment failed | Email, Push | Critical | payment_failed |
| Password reset | Email | Critical | password_reset |
| Welcome | Email | Low | welcome |
| Review request | Email | Low | review_request |
| Price drop alert | Email, Push | Medium | price_drop |
| Back in stock | Email, Push | Medium | back_in_stock |
| Merchant payout | Email | High | merchant_payout |

**Rate Limiting:**
- Email: 100/hour per user, 10,000/hour global
- Push: 50/hour per user
- SMS: 10/day per user, 1,000/day global
- Critical notifications bypass rate limits

---

## 3. Inter-Service Communication

### 3.1 Synchronous (REST)

Used for: User authentication validation, real-time inventory checks, payment processing.

**Circuit Breaker Configuration:**
- Failure threshold: 5 failures in 30 seconds
- Recovery timeout: 60 seconds
- Half-open: Allow 3 test requests
- Fallback: Cached response or graceful degradation

### 3.2 Asynchronous (Events)

Used for: Order state changes, inventory updates, notifications, analytics.

**Event Bus: Amazon EventBridge**

```json
{
    "source": "order-service",
    "detail-type": "order.confirmed",
    "detail": {
        "order_id": "uuid",
        "user_id": "uuid",
        "merchant_id": "uuid",
        "total_cents": 15999,
        "items": [...],
        "timestamp": "2026-04-20T10:30:00Z"
    }
}
```

**Dead Letter Queue:**
- Failed events → DLQ after 3 retries with exponential backoff
- DLQ retention: 14 days
- Alerting: PagerDuty if DLQ depth > 100

---

## 4. Infrastructure

### 4.1 Deployment

- Container orchestration: Amazon ECS Fargate
- Service mesh: AWS App Mesh (Envoy sidecar)
- CI/CD: GitHub Actions → ECR → ECS Blue/Green deployment
- Infrastructure as Code: AWS CDK (TypeScript)

### 4.2 Observability

- Metrics: CloudWatch + Prometheus + Grafana
- Tracing: AWS X-Ray (distributed tracing across all services)
- Logging: CloudWatch Logs → OpenSearch (structured JSON logs)
- Alerting: CloudWatch Alarms → SNS → PagerDuty

**Key SLIs:**
- Availability: 99.99% (measured at load balancer)
- Latency: p50 < 100ms, p99 < 500ms (per service)
- Error rate: < 0.1% (5xx responses)
- Throughput: 10,000 requests/second (peak)

### 4.3 Security

- Network: VPC with private subnets, NAT gateway for outbound
- Secrets: AWS Secrets Manager (rotated every 30 days)
- Encryption: TLS 1.3 in transit, AES-256 at rest
- WAF: AWS WAF with OWASP Top 10 rules
- DDoS: AWS Shield Advanced
- Compliance: SOC 2 Type II, PCI DSS Level 1

---

## 5. Data Consistency

### 5.1 Saga Pattern (Order Creation)

```
1. Reserve inventory (Product Service)
2. Create payment intent (Payment Service)
3. Confirm payment (Payment Service)
4. Decrement inventory (Product Service)
5. Create order record (Order Service)
6. Send confirmation (Notification Service)

Compensation (on failure at step N):
- Step 5 fails → Refund payment, release inventory
- Step 3 fails → Release inventory
- Step 2 fails → Release inventory
```

### 5.2 Eventual Consistency

- Product search index: ~2 second lag from write to searchable
- Analytics aggregations: 5-minute batch windows
- Recommendation model: Daily retraining
- Inventory counts: Real-time for checkout, eventual for display

---

## 6. Scaling Strategy

| Service | Scaling Trigger | Min | Max | Scale-up | Scale-down |
|---------|----------------|-----|-----|----------|------------|
| User | CPU > 60% | 3 | 20 | 60s | 300s |
| Product | CPU > 70% | 3 | 30 | 60s | 300s |
| Order | Queue depth > 100 | 5 | 50 | 30s | 300s |
| Payment | CPU > 50% | 3 | 15 | 30s | 600s |
| Notification | Queue depth > 500 | 2 | 20 | 60s | 300s |

**Database Scaling:**
- Read replicas: 2 per region (auto-failover)
- Connection pooling: PgBouncer (max 200 connections per service)
- Sharding: Not needed at current scale (< 1TB per database)
- Caching: Redis cluster (3 nodes, 6 replicas)
