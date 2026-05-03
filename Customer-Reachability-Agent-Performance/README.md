# 📞 Customer Reachability, Agent Productivity & Delta SAT

## 🎯 Business Context
This project was built on top of **automated data exports from an operational database mirror**.

The organization required:
- Reliable, recurring data extraction
- Stable indicators for customer reachability
- Agent productivity monitoring
- Quality tracking through Delta SAT metrics

Thanks to the database mirror and automated exports, the data pipeline provides
**consistent, refreshable datasets** without manual intervention.

---

## ✅ Objectives
- Measure **customer reachability rate** across multiple contact attempts
- Identify the **optimal number of contact attempts**
- Monitor **agent productivity and workload**
- Analyze **Delta SAT (satisfaction) trends** for joined vs non‑joined customers
- Support operational and quality decision‑making

---

## 🏗 Data Architecture & Pipeline

### Data Source
- Automated exports generated from a **database mirror**
- Data refreshed on a recurring basis
- No manual manipulation of source data

### Processing & Modeling
- Data cleaning and normalization
- Business logic implemented via DAX
- Star‑schema inspired Power BI data model
- Performance‑optimized measures for large volumes

### Analytics Layer
- Customer reachability metrics (multi‑attempt logic)
- Agent productivity KPIs
- Delta SAT and quality indicators
- Time‑based and hierarchical analysis

This architecture ensures **data reliability, scalability, and reproducibility**.

----

## 📊 Analytical Scopes Covered

### 1️⃣ Customer Reachability
- Stock vs joined clients
- Reachability rate (global & weekly)
- Reachability by attempt:
  - 1st attempt
  - 2nd attempt
  - 3rd attempt
  - 4+ attempts
- Average number of attempts per client

### 2️⃣ Agent Productivity
- Tickets closed (distinct)
- Ticket MEA
- Notes handled
- Dossiers processed
- Productivity by hour
- Performance ranking by agent

### 3️⃣ Delta SAT & Quality
- Delta SAT overall
- Delta SAT by week
- Comparison:
  - Joined customers
  - Non‑joined customers
- Quality evolution trends

---

## 🛠 Tools & Skills
- Power BI
- DAX (rate calculation, attempt logic, productivity KPIs)
- Data modeling
- Operational KPI design
- Workforce & quality analytics
