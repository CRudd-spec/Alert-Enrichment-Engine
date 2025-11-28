# ALERT-ENRICHMENT-ENGINE (v0)

## What this does
This script ingests raw monitoring alerts (JSON), normalizes vendor-specific fields, and produces a standardized **incident candidate** suitable for automation such as ticket creation, and routing.
It implements a minimal but real **alert -> incident decision engine**.

---

## Core behavior
`enrich.py` performs the following steps:

### 1. Ingest
- Reads a JSON alert payload from disk
- Treats input alerts as stateless events

### 2. Normalize
- Maps vendor severity values to a standard internal severity
- Classifies alerts into problem categories (e.g. reachability, performance)
- Determines operational impact from severity

### 3. Deduplicate
- Generates a deterministic deduplication key based on incident identity  
  (device + metric + normalized severity)
- Uses this key to correlate repeated alerts for the same underlying issue

### 4. Incident lifecycle
- Creates a new incident when a dedup key is first seen
- Suppresses duplicate alerts while an incident is active
- Resolves an incident when a clear signal is received

### 5. Persistence
- Stores incident state in a JSON-backed incident store
- Behavior is idempotent across multiple script executions

---

## Deduplication model
Deduplication is **identity-based**, not time-based.

- Repeated alerts for the same active incident are suppressed
- The same dedup key is reused across executions
- Persistence ensures suppression behavior survives restarts

### Known limitation
If a resource goes down, recovers, and later fails again, the dedup key will match the previous incident.

In a production system, this could also be addressed as:
- Scoping deduplication to **active incidents only**
- Applying a **time window** to deduplication
- Incorporating incident state transitions into key reuse logic

This limitation is intentional in v0 to keep the engine focused on identity correlation and lifecycle.

---

## Why this exists
This project demonstrates:
- Alert normalization and schema control
- Deterministic deduplication
- Incident lifecycle handling
- Separation of event input from system state

It is intentionally minimal and designed to be extended to an ITSM API or event pipeline.

---
