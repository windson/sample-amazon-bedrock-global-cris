# RFC-2026-003: Payment Processing System Redesign

## Status: APPROVED
## Author: Platform Engineering Team
## Date: 2026-03-15
## Reviewers: Security, Compliance, Finance, SRE

---

## 1. Abstract

This RFC proposes a complete redesign of the payment processing subsystem to support multi-currency transactions, subscription billing, marketplace payouts, and regulatory compliance across 12 jurisdictions. The current system handles single-currency (USD) one-time payments only and cannot scale to support the business requirements for Q3 2026.

## 2. Motivation

### 2.1 Current Limitations

1. **Single currency:** Only USD supported. International customers pay conversion fees.
2. **No subscriptions:** Recurring billing handled by a third-party SaaS ($45K/month).
3. **Manual payouts:** Merchant payouts require manual CSV upload to banking portal.
4. **No split payments:** Cannot split a single order across multiple merchants.
5. **Weak fraud detection:** Rule-based only, 2.3% false positive rate.
6. **No 3D Secure:** Required by PSD2 (EU) and RBI (India) regulations.
7. **Single provider:** 100% Stripe dependency creates vendor lock-in risk.

### 2.2 Business Requirements

- Support 15 currencies by Q3 2026 (USD, EUR, GBP, JPY, AUD, CAD, INR, BRL, MXN, SGD, HKD, KRW, SEK, NOK, CHF)
- Subscription billing for premium memberships (monthly/annual)
- Automated marketplace payouts (T+2 settlement)
- Split payments for multi-merchant orders
- 3D Secure 2.0 for EU/India transactions
- Fraud detection with < 0.5% false positive rate
- PCI DSS Level 1 compliance maintenance
- 99.999% availability for payment processing

## 3. Proposed Architecture

### 3.1 Component Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        API Gateway                               │
│                   (Rate limiting, Auth)                           │
└─────────────────────────┬───────────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────────┐
│                   Payment Orchestrator                            │
│            (Saga coordination, idempotency)                       │
└──────┬──────────┬──────────┬──────────┬─────────────────────────┘
       │          │          │          │
┌──────▼───┐ ┌───▼────┐ ┌───▼────┐ ┌───▼──────────┐
│ Provider │ │ Fraud  │ │ Ledger │ │ Subscription │
│ Adapter  │ │ Engine │ │ Service│ │   Engine     │
└──────┬───┘ └───┬────┘ └───┬────┘ └───┬──────────┘
       │          │          │          │
┌──────▼───┐ ┌───▼────┐ ┌───▼────┐ ┌───▼──────────┐
│  Stripe  │ │   ML   │ │  DB    │ │   Scheduler  │
│  PayPal  │ │ Model  │ │(Ledger)│ │   (Cron)     │
│  Adyen   │ │        │ │        │ │              │
└──────────┘ └────────┘ └────────┘ └──────────────┘
```

### 3.2 Payment Orchestrator

The orchestrator implements the Saga pattern for complex payment flows:

**Simple Payment Flow:**
```
1. Validate request (amount, currency, merchant)
2. Check fraud score
3. Route to optimal provider
4. Create payment intent
5. Await confirmation (webhook or polling)
6. Update ledger
7. Emit event
```

**Split Payment Flow (Multi-Merchant Order):**
```
1. Validate total = sum(splits)
2. Check fraud score (once for entire order)
3. For each split:
   a. Create sub-payment intent
   b. Associate with merchant
4. Charge customer (single charge)
5. On success:
   a. Update ledger for each merchant
   b. Schedule payouts per merchant
6. On failure:
   a. Compensate any completed sub-payments
   b. Release holds
```

**Subscription Flow:**
```
1. Create subscription record
2. Schedule first billing
3. On billing date:
   a. Attempt charge
   b. On success: extend subscription, emit event
   c. On failure: retry (3 attempts over 7 days)
   d. On final failure: cancel subscription, notify user
4. Handle upgrades/downgrades (proration)
5. Handle cancellation (immediate vs end-of-period)
```

### 3.3 Provider Adapter Layer

Abstract interface for payment providers:

```go
type PaymentProvider interface {
    CreateIntent(ctx context.Context, req CreateIntentRequest) (*PaymentIntent, error)
    ConfirmIntent(ctx context.Context, intentID string, method PaymentMethod) (*PaymentIntent, error)
    CancelIntent(ctx context.Context, intentID string) error
    Refund(ctx context.Context, intentID string, amount Money) (*Refund, error)
    CreatePayout(ctx context.Context, req PayoutRequest) (*Payout, error)
    ValidateWebhook(ctx context.Context, payload []byte, signature string) (*WebhookEvent, error)
    Supports3DSecure() bool
    SupportedCurrencies() []Currency
    SupportedCountries() []Country
}
```

**Provider Routing Rules:**

| Condition | Primary | Fallback | Reason |
|-----------|---------|----------|--------|
| EUR transactions | Adyen | Stripe | Lower EU interchange fees |
| JPY transactions | Stripe Japan | Adyen | Local acquiring |
| INR transactions | Stripe India | - | RBI compliance |
| USD < $10,000 | Stripe | PayPal | Best rates |
| USD >= $10,000 | Stripe | Adyen | Higher limits |
| Subscriptions | Stripe | - | Best subscription API |
| Marketplace payouts | Stripe Connect | Adyen MarketPay | Split payment support |
| 3D Secure required | Adyen | Stripe | Better 3DS2 UX |

**Failover Logic:**
```
1. Attempt primary provider
2. If timeout (> 10s) or 5xx error:
   a. Log failure, increment circuit breaker
   b. Attempt fallback provider
3. If fallback fails:
   a. Return retriable error to client
   b. Schedule async retry (max 3, exponential backoff)
4. If circuit breaker open (> 5 failures in 60s):
   a. Route all traffic to fallback
   b. Alert on-call engineer
   c. Attempt recovery every 30s
```

### 3.4 Fraud Engine

**Feature Set (47 features):**

| Category | Features | Weight |
|----------|----------|--------|
| Velocity | Orders/hour, amount/day, new cards/week | High |
| Device | Fingerprint age, proxy detection, timezone mismatch | High |
| Behavioral | Time since last order, cart composition anomaly | Medium |
| Geographic | IP-billing distance, impossible travel, VPN | High |
| Account | Age, verification status, previous chargebacks | High |
| Transaction | Amount vs average, currency mismatch, round amounts | Medium |
| Network | Shared device/IP with known fraudsters | Critical |

**Decision Matrix:**

| Score Range | Action | 3D Secure | Manual Review |
|-------------|--------|-----------|---------------|
| 0.0 - 0.3 | Allow | No | No |
| 0.3 - 0.6 | Allow | Yes (if supported) | No |
| 0.6 - 0.8 | Hold | Yes (required) | Yes |
| 0.8 - 1.0 | Decline | N/A | Auto-flag |

**Model Training:**
- Algorithm: XGBoost ensemble + neural network
- Training data: 18 months of labeled transactions (2.1M records)
- Retraining: Weekly with latest 30 days of chargebacks
- A/B testing: Shadow mode for 7 days before promotion
- Monitoring: Precision/recall dashboard, drift detection

### 3.5 Ledger Service

Double-entry bookkeeping for all financial transactions:

```sql
CREATE TABLE ledger_accounts (
    id UUID PRIMARY KEY,
    account_type VARCHAR(20) NOT NULL, -- asset, liability, revenue, expense
    entity_type VARCHAR(20) NOT NULL,  -- platform, merchant, customer
    entity_id UUID NOT NULL,
    currency VARCHAR(3) NOT NULL,
    balance_cents BIGINT NOT NULL DEFAULT 0,
    pending_cents BIGINT NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(entity_type, entity_id, currency)
);

CREATE TABLE ledger_entries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    transaction_id UUID NOT NULL,
    account_id UUID NOT NULL REFERENCES ledger_accounts(id),
    entry_type VARCHAR(10) NOT NULL CHECK (entry_type IN ('debit', 'credit')),
    amount_cents BIGINT NOT NULL CHECK (amount_cents > 0),
    currency VARCHAR(3) NOT NULL,
    description TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Invariant: For every transaction_id, sum(debits) = sum(credits)
CREATE OR REPLACE FUNCTION verify_balanced_entry()
RETURNS TRIGGER AS $$
BEGIN
    IF (
        SELECT SUM(CASE WHEN entry_type = 'debit' THEN amount_cents ELSE -amount_cents END)
        FROM ledger_entries
        WHERE transaction_id = NEW.transaction_id
    ) != 0 THEN
        RAISE EXCEPTION 'Unbalanced ledger entry for transaction %', NEW.transaction_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
```

**Example: Customer pays $100 for order with 2 merchants (70/30 split, 5% platform fee):**

| Entry | Account | Debit | Credit |
|-------|---------|-------|--------|
| 1 | Customer Payment (asset) | $100 | |
| 2 | Merchant A Payable (liability) | | $66.50 |
| 3 | Merchant B Payable (liability) | | $28.50 |
| 4 | Platform Revenue (revenue) | | $5.00 |

### 3.6 Subscription Engine

**Billing Models:**

| Model | Description | Proration | Example |
|-------|-------------|-----------|---------|
| Fixed | Same amount every period | Yes | $9.99/month |
| Tiered | Price per unit decreases at thresholds | Yes | API calls |
| Volume | All units priced at tier reached | No | Storage |
| Metered | Pay for actual usage at period end | N/A | Compute hours |

**Lifecycle Events:**

```
subscription.created
subscription.activated
subscription.trial_started
subscription.trial_ending (3 days before)
subscription.trial_ended
subscription.invoice_created
subscription.payment_succeeded
subscription.payment_failed
subscription.payment_retry_scheduled
subscription.past_due
subscription.cancelled
subscription.expired
subscription.upgraded
subscription.downgraded
subscription.paused
subscription.resumed
```

**Retry Schedule (Dunning):**

| Attempt | Delay | Action |
|---------|-------|--------|
| 1 | Immediate | Charge card |
| 2 | +3 days | Charge card, email "payment failed" |
| 3 | +5 days | Charge card, email "action required" |
| 4 | +7 days | Cancel subscription, email "cancelled" |

---

## 4. Data Migration Plan

### 4.1 Phase 1: Shadow Mode (2 weeks)
- Deploy new system alongside existing
- Mirror all transactions to new ledger (read-only)
- Compare results, fix discrepancies
- Zero customer impact

### 4.2 Phase 2: Gradual Rollout (4 weeks)
- Week 1: 1% of new transactions → new system
- Week 2: 10% of new transactions
- Week 3: 50% of new transactions
- Week 4: 100% of new transactions
- Existing subscriptions remain on old system

### 4.3 Phase 3: Subscription Migration (3 weeks)
- Migrate subscription records (no re-billing)
- Update webhook endpoints
- Verify next billing cycle processes correctly
- Decommission old subscription SaaS

### 4.4 Rollback Plan
- Feature flag: instant rollback to old system
- Data: New ledger entries are append-only, no data loss
- Subscriptions: Old system remains active until Phase 3 complete
- Maximum rollback time: < 5 minutes

---

## 5. Security Considerations

### 5.1 PCI DSS Compliance

| Requirement | Implementation |
|-------------|---------------|
| Req 1: Firewall | VPC security groups, NACLs |
| Req 2: No defaults | Automated hardening (CIS benchmarks) |
| Req 3: Protect stored data | AES-256, tokenization for card data |
| Req 4: Encrypt transmission | TLS 1.3, certificate pinning |
| Req 5: Anti-virus | Container scanning (Trivy) |
| Req 6: Secure systems | SAST/DAST in CI, dependency scanning |
| Req 7: Restrict access | RBAC, least privilege, JIT access |
| Req 8: Identify users | SSO, MFA, audit logging |
| Req 9: Physical access | AWS managed (SOC 2 certified) |
| Req 10: Monitor access | CloudTrail, GuardDuty, SIEM |
| Req 11: Test security | Quarterly pen tests, bug bounty |
| Req 12: Security policy | Documented, trained, reviewed annually |

### 5.2 Tokenization

Card data never touches our servers:
```
Client → Stripe.js → Stripe (tokenize) → Return token
Token → Our API → Stripe API (charge with token)
```

We store only:
- Last 4 digits (for display)
- Card brand (Visa, Mastercard, etc.)
- Expiry month/year
- Stripe customer/payment method ID (token)

### 5.3 Encryption

| Data | At Rest | In Transit | Key Management |
|------|---------|------------|----------------|
| Card tokens | AES-256-GCM | TLS 1.3 | AWS KMS (CMK) |
| Bank accounts | AES-256-GCM | TLS 1.3 | AWS KMS (CMK) |
| Transaction logs | AES-256 (S3 SSE) | TLS 1.3 | AWS managed |
| PII (names, emails) | AES-256-GCM | TLS 1.3 | AWS KMS (CMK) |
| Webhook secrets | AES-256-GCM | N/A | AWS Secrets Manager |

---

## 6. Monitoring & Alerting

### 6.1 Key Metrics

| Metric | Warning | Critical | Action |
|--------|---------|----------|--------|
| Payment success rate | < 97% | < 95% | Page on-call |
| Fraud false positive rate | > 1% | > 2% | Retrain model |
| Provider latency (p99) | > 3s | > 10s | Failover |
| Refund processing time | > 24h | > 48h | Escalate |
| Payout failure rate | > 1% | > 5% | Halt payouts |
| Ledger imbalance | Any | Any | Immediate investigation |
| 3DS challenge rate | > 20% | > 30% | Review rules |
| Chargeback rate | > 0.5% | > 1% | Risk review |

### 6.2 Dashboards

1. **Real-time:** Transaction volume, success rate, provider health
2. **Financial:** Daily revenue, fees, refunds, net settlement
3. **Fraud:** Score distribution, decisions, false positives
4. **Subscriptions:** MRR, churn, trial conversions, dunning success
5. **Compliance:** Audit log completeness, encryption status, access reviews

---

## 7. Cost Analysis

### 7.1 Provider Fees

| Provider | Transaction Fee | Monthly | Notes |
|----------|----------------|---------|-------|
| Stripe | 2.9% + $0.30 | $0 | Volume discount at $1M+/month |
| Adyen | 2.5% + $0.10 | $120 | Better EU rates |
| PayPal | 3.49% + $0.49 | $0 | Higher fees, wider reach |

### 7.2 Infrastructure Costs (Estimated Monthly)

| Component | Cost | Notes |
|-----------|------|-------|
| ECS Fargate (Payment Orchestrator) | $2,400 | 4 tasks, 2 vCPU, 4GB |
| ECS Fargate (Fraud Engine) | $1,800 | 3 tasks, 2 vCPU, 8GB |
| RDS PostgreSQL (Ledger) | $3,200 | db.r6g.xlarge, Multi-AZ |
| ElastiCache Redis | $800 | cache.r6g.large, 2 nodes |
| SageMaker (Fraud ML) | $1,500 | ml.m5.xlarge endpoint |
| KMS | $100 | 10 CMKs |
| Secrets Manager | $50 | 50 secrets |
| CloudWatch | $300 | Logs, metrics, alarms |
| **Total** | **$10,150** | |

### 7.3 ROI

- Eliminate third-party subscription SaaS: -$45,000/month
- Reduce fraud losses (2.3% → 0.5%): -$35,000/month (estimated)
- Multi-currency (no conversion fees): +$12,000/month revenue
- **Net savings: $81,850/month**

---

## 8. Timeline

| Phase | Duration | Deliverable |
|-------|----------|-------------|
| Design & Review | 2 weeks | This RFC approved |
| Core Implementation | 6 weeks | Orchestrator, Ledger, Provider adapters |
| Fraud Engine | 4 weeks | ML model, scoring API |
| Subscription Engine | 4 weeks | Billing, dunning, lifecycle |
| Integration Testing | 2 weeks | End-to-end flows |
| Shadow Mode | 2 weeks | Parallel operation |
| Gradual Rollout | 4 weeks | 1% → 100% |
| Subscription Migration | 3 weeks | Move from SaaS |
| **Total** | **27 weeks** | |

---

## 9. Open Questions

1. Should we support cryptocurrency payments? (Deferred to Phase 2)
2. Buy-now-pay-later integration (Affirm, Klarna)? (Deferred)
3. Should the ledger support multi-currency natively or convert to USD? (Decision: native multi-currency)
4. How to handle disputes/chargebacks in split payment scenarios? (Decision: platform absorbs, recovers from merchant)
5. Tax calculation service — build or buy? (Decision: use TaxJar API)

---

## 10. Decision Record

| Decision | Rationale | Alternatives Considered |
|----------|-----------|------------------------|
| Go as primary language | Performance, concurrency, type safety | Java (too verbose), Rust (hiring difficulty) |
| PostgreSQL for ledger | ACID guarantees, JSON support | DynamoDB (no joins), CockroachDB (cost) |
| Stripe as primary | Best API, widest coverage | Adyen only (weaker US), Square (limited international) |
| Saga over 2PC | Availability over consistency | 2PC (blocking, single point of failure) |
| XGBoost for fraud | Interpretable, fast inference | Deep learning (black box), rules only (poor accuracy) |
| Double-entry ledger | Audit trail, reconciliation | Single-entry (error-prone), external service (cost) |
