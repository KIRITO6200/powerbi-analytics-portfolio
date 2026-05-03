# 🧱 Data Model – Presence & Absence

## Problem
Planning and realised tables both contain **multiple records per agent per date**
(planning slots, multiple realised events).

Direct relationships would result in:
- Overcounting
- Incorrect totals
- Ambiguous filter propagation

---

## Solution: Matricule–Date Bridge Table

The bridge table contains all distinct combinations of:
- Matricule
- Date

It is built using a UNION of both fact tables and deduplicated.

---

## Relationship Design
- Bridge (1) → Planning (many)
- Bridge (1) → Réalisé (many)
- Calendar filters the bridge
- Facts never filter each other directly

This guarantees:
- Correct aggregation
- Stable KPIs
- Accurate presence & absence calculations
