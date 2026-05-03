# 🕒 Workforce Presence & Absence Analytics

## 🎯 Business Context
This project enables accurate monitoring of workforce presence, absence,
lateness, and adherence by analyzing **planning vs realised activity**.

A major constraint was that **both planning and realised data contained multiple
rows per agent per day**, making direct relationships unreliable.

---

## ✅ Solution Design
To guarantee correct analytics:
- A **Matricule–Date bridge table** was implemented
- The bridge normalizes the grain to **1 agent × 1 day**
- Planning and realised facts are linked through this bridge
- All KPIs are computed safely without double counting

---

## 📊 Key KPIs
- Presence (hours)
- Absence (hours)
- Lateness (hours)
- Presence / Absence / Lateness rates
- Number of agents
- Absence & lateness by structure and week

---

## 🛠 Tools & Skills
- Power BI
- DAX (bridge tables, aggregation logic)
- Data modeling (many-to-many resolution)
- HR & workforce analytics
- Operational dashboard design
