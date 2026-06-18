# QuickBite Analytics — SQL Findings Summary

**Analyst:** [Your Name]
**Dataset:** 75,000 orders, Bangladesh food-delivery market, Jan–Dec 2025 (synthetic, market-modeled)
**Tool:** SQLite via DB Browser for SQLite
**Companion file:** `quickbite_analysis.sql` (12 queries)

This document summarizes what each query revealed. It is the source material for the final insights report (Step 7) and the narrative for dashboard design (Steps 4–6).

---

## Batch 1 — Data Quality (Queries 1–3)

Before any analysis, I validated the data on three dimensions: completeness, coverage, and missingness.

- **Completeness:** All five tables loaded with expected counts — 75,000 orders, 500 restaurants, 8,000 customers, 12 campaigns, 600 riders.
- **Coverage:** Orders span the full year with 365 distinct days — no calendar gaps.
- **Missingness:** 9,079 orders (12.1%) have no customer rating (customers who skipped rating — legitimate, left as NULL). 54,604 orders fall outside any campaign window (expected; campaigns run only on specific dates).

**Takeaway:** Data passed all integrity checks and is safe for analysis.

---

## Batch 2 — Revenue & Growth (Queries 4–7)

- **Monthly revenue** holds in the 5.7M–6.9M BDT range per month, averaging ~1,000–1,070 BDT per order.
- **Month-over-month growth** is noisy (+11.6% in May, −10.4% in June) driven by campaign timing and weekend counts — no clear trend at the aggregate level. *This noise is itself a lesson: the aggregate hides the city-level story below.*
- **City mix:** Dhaka dominates with ~48,500 orders (≈60%), followed by Chittagong (~10,800), Sylhet, Khulna, Rajshahi.
- **Payment mix:** bKash leads at 42.1%, then Cash 30.9%, Nagad 14.1%, Card 8.9%, Rocket 3.9%. Mobile financial services together account for ~60% of orders — consistent with the real Bangladesh market.

**Takeaway:** Headline numbers look stable and healthy — which, as Batch 3 shows, is misleading.

---

## Batch 3 — Key Business Insights (Queries 8–12)

### Insight 1 — Chittagong order collapse (Query 8)
*Answers: "Why are orders dropping in a certain city?"*

Chittagong held steady at **~1,122 orders/month** (Jan–Jul), then collapsed to **~522 orders/month** (Sep–Dec) — a **53% decline**. The drop begins in August and stabilizes at the lower level.

| Period | Avg orders/month |
|--------|------------------|
| Jan–Jul | 1,122 |
| Sep–Dec | 522 |

**Critical context:** The annual city totals (Query 6) showed Chittagong as completely healthy. The decline was only visible once orders were disaggregated by month. This is the project's signature lesson — *always disaggregate before declaring a market healthy.* The pattern (sudden, sustained, single-city) is consistent with a competitor entering the Chittagong market.

**Recommendation:** Investigate Chittagong competitive activity from August onward; consider targeted win-back promotions and restaurant-partner retention there.

### Insight 2 — Weekend cuisine winners (Query 9)
*Answers: "Which restaurants/cuisines perform best on weekends?"*

Using the Bangladesh weekend (Friday–Saturday), average order value rises sharply for certain cuisines:

| Cuisine | Weekend lift |
|---------|--------------|
| Biryani & Kebab | +53% |
| Desserts | +43% |
| Bangladeshi | +35% |
| Pizza | +28% |

**Recommendation:** On Fri–Sat, prioritize Biryani & Kebab partners in app placement and marketing, and ensure rider capacity matches the weekend demand surge.

### Insight 3 — Campaign ROI (Query 10)
*Answers: "Which discount campaign gives the best ROI?"*

Ranking campaigns by net revenue per order reveals that discount depth does **not** equal success:

| Campaign | Discount | Net rev/order | Verdict |
|----------|----------|---------------|---------|
| Monsoon Munchies | 40% | 635 BDT | Worst — burned ~1.03M BDT in discounts |
| Eid-ul-Fitr Bonanza | 35% | 718 BDT | Weak |
| First Order Free Delivery | 0% | 1,064 BDT | Best — 4,915 orders, zero discount cost |

**Recommendation:** Cap discount depth around 20–25%. The 40% "Monsoon Munchies" promo destroyed margin without proportionate volume. Free-delivery acquisition offers (0% discount) delivered the strongest per-order economics.

### Insight 4 — Old Dhaka evening delivery bottleneck (Query 11)

Old Dhaka delivery times sit at **~38 minutes** most of the day but spike to **~59 minutes during 7–9 PM** — a 55% slowdown during dinner rush, almost certainly evening traffic congestion in the old city.

**Recommendation:** Add rider capacity in Old Dhaka for the 7–9 PM window and widen customer-facing delivery-time estimates during those hours to protect ratings.

### Insight 5 — Top restaurants per city (Query 12)

Top-3 revenue restaurants per city are dominated by **high-AOV cuisines (especially Pizza)** — these generate the most revenue even without the highest order counts, because ticket size outweighs volume.

**Recommendation:** Protect relationships with top-3 partners per city (they are disproportionately valuable); recruit more high-AOV cuisine partners in under-served areas.

---

## SQL Techniques Demonstrated

GROUP BY aggregation · conditional aggregation (CASE WHEN) · subqueries · INNER JOIN · CTEs · chained CTEs · window functions (LAG for month-over-month, RANK with PARTITION BY for top-N-per-group) · date functions (STRFTIME) · type casting (CAST).

---

## How these feed the dashboards (Steps 4–6)

- **Revenue dashboard:** Queries 4, 5, 6 → KPI cards + monthly trend + city map.
- **Restaurant dashboard:** Queries 9, 12 → cuisine performance + top-partner leaderboard.
- **Campaign dashboard:** Query 10 → ROI waterfall / ranking.
- **Operations dashboard:** Queries 8, 11 → city decline alert + delivery heatmap by hour.
