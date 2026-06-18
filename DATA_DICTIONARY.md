# QuickBite Analytics — Dataset Documentation

**Project:** Bangladesh Food Delivery Performance Intelligence Platform
**Dataset type:** Synthetic, modeled on the Bangladesh food delivery market
**Date range:** January 1, 2025 — December 31, 2025
**Currency:** Bangladeshi Taka (BDT)

> ⚠️ **Honesty note for your portfolio README:** This is synthetic data generated to reflect publicly observable characteristics of the Bangladesh food delivery market (real cities, real Dhaka area names, BDT pricing tiers, local payment methods, Friday–Saturday weekend behavior, Eid/Pohela Boishakh campaign timing). It is **not** real Pathao or Foodpanda data. Frame the project as a market-realistic simulation, not as scraped or leaked operational data.

---

## Files

| File | Rows | Description |
|------|------|-------------|
| `restaurants.csv` | 500 | Restaurant master data |
| `customers.csv` | 8,000 | Customer master data |
| `campaigns.csv` | 12 | Marketing campaigns over the year |
| `riders.csv` | 600 | Delivery rider master data |
| `orders.csv` | 75,000 | Transactional order data (the main fact table) |

---

## Schema

### `restaurants.csv`
| Column | Type | Notes |
|---|---|---|
| restaurant_id | string | PK, format `R0001` |
| restaurant_name | string | Bengali-flavored fictional names |
| city | string | Dhaka, Chittagong, Sylhet, Rajshahi, Khulna |
| area | string | Real area names per city (Dhanmondi, Agrabad, etc.) |
| cuisine_type | string | 10 categories |
| tier | string | Premium / Standard / Budget |
| avg_rating | float | 2.5–5.0 |
| partner_since | date | When restaurant joined the platform |

### `customers.csv`
| Column | Type | Notes |
|---|---|---|
| customer_id | string | PK, format `C00001` |
| city | string | Home city |
| age_group | string | 18-24, 25-34, 35-44, 45-54, 55+ |
| segment | string | High Value / Regular / Occasional |
| signup_date | date | Signup date (Jan 2024 – Oct 2025) |

### `campaigns.csv`
| Column | Type | Notes |
|---|---|---|
| campaign_id | string | PK, format `CMP001` |
| campaign_name | string | E.g. "Pohela Boishakh Special", "Eid-ul-Fitr Bonanza" |
| start_date / end_date | date | Campaign window |
| discount_percent | int | 0–40 |
| target_cities | string | "All" or comma-separated list |

### `riders.csv`
| Column | Type | Notes |
|---|---|---|
| rider_id | string | PK, format `D0001` |
| city | string | Operating city |
| joining_date | date | When rider joined |
| vehicle_type | string | Motorbike (85%) / Bicycle (15%) |

### `orders.csv` *(fact table — the one you'll spend most time on)*
| Column | Type | Notes |
|---|---|---|
| order_id | string | PK, format `O0000001` |
| order_datetime | timestamp | When order was placed |
| customer_id | FK | → customers |
| restaurant_id | FK | → restaurants |
| rider_id | FK | → riders |
| city | string | Order city (may differ from customer's home city) |
| area | string | Restaurant's area |
| cuisine_type | string | Denormalized from restaurant |
| items_count | int | 1–5 |
| order_value_bdt | float | Gross order value |
| discount_bdt | float | Discount applied (0 if no campaign) |
| net_value_bdt | float | order_value_bdt − discount_bdt |
| campaign_id | string | FK → campaigns (blank if no campaign) |
| payment_method | string | bKash, Cash, Nagad, Card, Rocket |
| delivery_time_minutes | int | Total delivery time |
| rating | int or blank | 1–5 stars (12% missing — customer didn't rate) |

---

## 🎯 Planted Business Patterns (the "insights" your analysis should surface)

These are deliberately built into the data so you can show off discovery work in your final report. **Don't look at this section while doing your SQL analysis — find them yourself, then circle back to confirm.**

### Pattern 1: Chittagong order decline after August 2025
Monthly orders in Chittagong drop from ~1,100/month (Jan–Jul) to ~500/month (Sep–Dec). This simulates a competitor entering the market. **Verified in data:** confirmed.
> *Business question this answers:* "Why are orders dropping in Chittagong?"

### Pattern 2: Weekend (Fri–Sat) order value spike — strongest in Biryani & Kebab
Biryani & Kebab AOV is **+53% on weekends** vs weekdays. Bangladeshi cuisine is +35%. Desserts +43%. **Verified in data:** confirmed.
> *Business question this answers:* "Which cuisines perform best on weekends?"

### Pattern 3: Campaigns vary wildly in ROI
- `CMP006 Monsoon Munchies` — 40% discount, gave away **1.02M BDT** in discounts (worst).
- `CMP010 First Order Free Delivery` — 0% discount but drove **4,915 orders** (best acquisition).
- `CMP002 Pohela Boishakh` — premium small campaign with high discount per order.
> *Business question this answers:* "Which discount campaign gives the best ROI?"

### Pattern 4: Old Dhaka has bad delivery times during 7–9 PM
Old Dhaka avg delivery jumps from ~38 min off-peak to **~59 min during 19:00–21:00** (evening traffic). All other hours are normal. **Verified in data:** confirmed.
> *Business question this answers:* "Where do we have operational delivery issues?"

---

## Data quality notes (for your "Data Cleaning Log" in Step 2)

Things to clean / handle in Excel during Step 2:
1. **Missing ratings** — ~12% of orders have blank ratings (legitimate; customer skipped). Don't impute; use IFERROR or filter.
2. **Mixed weekend definition** — In Bangladesh, weekend = **Friday & Saturday**, not Sat–Sun. If you use Excel's `WEEKDAY()`, remember Friday = 6 and Saturday = 7 with default settings.
3. **Currency** — All values are in BDT. Format columns as `#,##0 "BDT"` for readability.
4. **Date format** — `order_datetime` is `YYYY-MM-DD HH:MM:SS`. Split into date and time columns if needed for pivots.
5. **No nulls in FK columns** — all customer_id, restaurant_id, rider_id are populated. Campaign_id is intentionally blank for non-campaign orders.

---

## Next steps (per your project plan)

✅ **Step 1 — DONE.** You have a clean, realistic, market-accurate dataset with discoverable insights.

➡️ **Step 2 — Data Cleaning in Excel/Google Sheets.** Open `orders.csv`, build a cleaning log, fix the issues noted above.

➡️ **Step 3 — Load into SQL** (SQLite recommended for simplicity). Write the 15–20 analytical queries.

➡️ **Step 4–6 — Dashboards** in Google Sheets, Power BI, Tableau.

➡️ **Step 7 — Insights report** that walks through all four patterns above as discovered findings.
