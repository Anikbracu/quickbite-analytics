-- ============================================================
-- QuickBite Analytics — SQL Analysis Script
-- Bangladesh Food Delivery Performance Intelligence
-- ------------------------------------------------------------
-- Author:   [Your Name]
-- Database: quickbite.db (SQLite)
-- Dataset:  75,000 orders, Jan–Dec 2025, synthetic Bangladesh
--           food-delivery data (5 tables: orders, restaurants,
--           customers, campaigns, riders)
-- Note:     Numeric columns imported as TEXT, so monetary and
--           time fields are wrapped in CAST(... AS REAL).
-- ============================================================


-- ============================================================
-- BATCH 1: DATA SANITY CHECKS
-- ============================================================

-- Query 1: Row counts per table (data completeness check)
SELECT 'orders'      AS table_name, COUNT(*) AS row_count FROM orders
UNION ALL
SELECT 'restaurants', COUNT(*) FROM restaurants
UNION ALL
SELECT 'customers',   COUNT(*) FROM customers
UNION ALL
SELECT 'campaigns',   COUNT(*) FROM campaigns
UNION ALL
SELECT 'riders',      COUNT(*) FROM riders;
-- Result: orders 75,000 | restaurants 500 | customers 8,000 | campaigns 12 | riders 600


-- Query 2: Date range coverage (confirm full-year data, no gaps)
SELECT
    MIN(order_datetime)                  AS earliest_order,
    MAX(order_datetime)                  AS latest_order,
    COUNT(DISTINCT DATE(order_datetime)) AS distinct_days
FROM orders;
-- Result: full year coverage, 365 distinct days.


-- Query 3: Missing data audit (ratings and campaigns expected to have blanks)
SELECT
    COUNT(*)                                                                 AS total_orders,
    SUM(CASE WHEN rating = '' OR rating IS NULL THEN 1 ELSE 0 END)           AS missing_ratings,
    SUM(CASE WHEN campaign_id = '' OR campaign_id IS NULL THEN 1 ELSE 0 END) AS no_campaign,
    ROUND(100.0 * SUM(CASE WHEN rating = '' OR rating IS NULL THEN 1 ELSE 0 END)
          / COUNT(*), 1)                                                     AS pct_missing_ratings
FROM orders;
-- Result: 9,079 missing ratings (12.1%); 54,604 orders outside any campaign.


-- ============================================================
-- BATCH 2: REVENUE & GROWTH ANALYSIS
-- ============================================================

-- Query 4: Monthly revenue trend
SELECT
    STRFTIME('%Y-%m', order_datetime)          AS month,
    COUNT(*)                                   AS total_orders,
    ROUND(SUM(CAST(net_value_bdt AS REAL)), 0) AS net_revenue_bdt,
    ROUND(AVG(CAST(net_value_bdt AS REAL)), 0) AS avg_order_value
FROM orders
GROUP BY month
ORDER BY month;


-- Query 5: Month-over-month revenue growth (window function LAG)
WITH monthly AS (
    SELECT
        STRFTIME('%Y-%m', order_datetime)          AS month,
        ROUND(SUM(CAST(net_value_bdt AS REAL)), 0) AS net_revenue
    FROM orders
    GROUP BY month
)
SELECT
    month,
    net_revenue,
    LAG(net_revenue) OVER (ORDER BY month) AS prev_month_revenue,
    ROUND(100.0 * (net_revenue - LAG(net_revenue) OVER (ORDER BY month))
          / LAG(net_revenue) OVER (ORDER BY month), 1) AS mom_growth_pct
FROM monthly
ORDER BY month;


-- Query 6: Revenue and orders by city
SELECT
    city,
    COUNT(*)                                           AS total_orders,
    ROUND(SUM(CAST(net_value_bdt AS REAL)), 0)         AS net_revenue_bdt,
    ROUND(AVG(CAST(net_value_bdt AS REAL)), 0)         AS avg_order_value,
    ROUND(AVG(CAST(delivery_time_minutes AS REAL)), 1) AS avg_delivery_min
FROM orders
GROUP BY city
ORDER BY net_revenue_bdt DESC;


-- Query 7: Payment method breakdown
SELECT
    payment_method,
    COUNT(*)                                                  AS total_orders,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM orders), 1) AS pct_of_orders,
    ROUND(SUM(CAST(net_value_bdt AS REAL)), 0)                AS net_revenue_bdt
FROM orders
GROUP BY payment_method
ORDER BY total_orders DESC;
-- Insight: Mobile financial services (bKash 42% + Nagad 14% + Rocket 4%) = ~60% of orders.


-- ============================================================
-- BATCH 3: KEY BUSINESS INSIGHTS
-- ============================================================

-- Query 8: Monthly orders by city (exposes the Chittagong decline)
-- Answers job-spec question: "Why are orders dropping in a certain city?"
SELECT
    STRFTIME('%Y-%m', order_datetime) AS month,
    SUM(CASE WHEN city = 'Dhaka'      THEN 1 ELSE 0 END) AS dhaka,
    SUM(CASE WHEN city = 'Chittagong' THEN 1 ELSE 0 END) AS chittagong,
    SUM(CASE WHEN city = 'Sylhet'     THEN 1 ELSE 0 END) AS sylhet,
    SUM(CASE WHEN city = 'Khulna'     THEN 1 ELSE 0 END) AS khulna,
    SUM(CASE WHEN city = 'Rajshahi'   THEN 1 ELSE 0 END) AS rajshahi
FROM orders
GROUP BY month
ORDER BY month;
-- Insight: Chittagong steady ~1,100/mo Jan–Jul, then collapses to ~500/mo from Sep
--          (≈55% decline). Annual totals (Query 6) completely masked this.


-- Query 9: Weekend vs weekday performance by cuisine (Bangladesh weekend = Fri/Sat)
-- Answers job-spec question: "Which restaurants perform best during weekends?"
WITH tagged AS (
    SELECT
        cuisine_type,
        CAST(order_value_bdt AS REAL) AS order_value,
        CASE
            WHEN STRFTIME('%w', order_datetime) IN ('5','6') THEN 'Weekend'
            ELSE 'Weekday'
        END AS day_type
    FROM orders
)
SELECT
    cuisine_type,
    ROUND(AVG(CASE WHEN day_type='Weekday' THEN order_value END), 0) AS weekday_aov,
    ROUND(AVG(CASE WHEN day_type='Weekend' THEN order_value END), 0) AS weekend_aov,
    ROUND(100.0 * (AVG(CASE WHEN day_type='Weekend' THEN order_value END)
        - AVG(CASE WHEN day_type='Weekday' THEN order_value END))
        / AVG(CASE WHEN day_type='Weekday' THEN order_value END), 1) AS weekend_lift_pct
FROM tagged
GROUP BY cuisine_type
ORDER BY weekend_lift_pct DESC;
-- Insight: Biryani & Kebab +53% weekend lift (highest); Desserts +43%; Bangladeshi +35%.
-- Note: STRFTIME('%w') => Sun=0 .. Fri=5, Sat=6, so IN ('5','6') = Bangladesh weekend.


-- Query 10: Campaign ROI ranking (INNER JOIN orders to campaigns)
-- Answers job-spec question: "Which discount campaign gives the best ROI?"
SELECT
    c.campaign_name,
    c.discount_percent,
    COUNT(o.order_id)                              AS orders_driven,
    ROUND(SUM(CAST(o.order_value_bdt AS REAL)), 0) AS gross_revenue,
    ROUND(SUM(CAST(o.discount_bdt AS REAL)), 0)    AS discount_cost,
    ROUND(SUM(CAST(o.net_value_bdt AS REAL)), 0)   AS net_revenue,
    ROUND(SUM(CAST(o.net_value_bdt AS REAL)) / COUNT(o.order_id), 0) AS net_rev_per_order
FROM orders o
JOIN campaigns c ON o.campaign_id = c.campaign_id
GROUP BY c.campaign_id, c.campaign_name, c.discount_percent
ORDER BY discount_cost DESC;
-- Insight: "Monsoon Munchies" (40% off) spent ~1.03M BDT in discounts for the LOWEST
--          net revenue per order (635 BDT). Lower-discount campaigns netted ~860/order.
--          Discount depth != ROI.


-- Query 11: Old Dhaka delivery time by hour (exposes evening bottleneck)
SELECT
    CAST(STRFTIME('%H', order_datetime) AS INTEGER)    AS hour_of_day,
    COUNT(*)                                           AS orders,
    ROUND(AVG(CAST(delivery_time_minutes AS REAL)), 1) AS avg_delivery_min
FROM orders
WHERE area = 'Old Dhaka'
GROUP BY hour_of_day
ORDER BY hour_of_day;
-- Insight: ~38 min most hours, spiking to ~59 min during 19:00–21:00 dinner rush
--          (≈55% slower). Points to evening traffic congestion in the old city.


-- Query 12: Top 3 restaurants per city by revenue (RANK window function + chained CTEs)
WITH restaurant_revenue AS (
    SELECT
        r.city,
        r.restaurant_name,
        r.cuisine_type,
        COUNT(o.order_id)                            AS total_orders,
        ROUND(SUM(CAST(o.net_value_bdt AS REAL)), 0) AS net_revenue
    FROM orders o
    JOIN restaurants r ON o.restaurant_id = r.restaurant_id
    GROUP BY r.restaurant_id, r.city, r.restaurant_name, r.cuisine_type
),
ranked AS (
    SELECT
        *,
        RANK() OVER (PARTITION BY city ORDER BY net_revenue DESC) AS city_rank
    FROM restaurant_revenue
)
SELECT city, city_rank, restaurant_name, cuisine_type, total_orders, net_revenue
FROM ranked
WHERE city_rank <= 3
ORDER BY city, city_rank;
-- Insight: High-AOV cuisines (esp. Pizza) dominate top revenue ranks even without the
--          highest order counts. PARTITION BY restarts ranking per city (top-N-per-group).

-- ============================================================
-- END OF ANALYSIS
-- Techniques demonstrated: GROUP BY aggregation, conditional
-- aggregation (CASE WHEN), subqueries, INNER JOIN, CTEs,
-- chained CTEs, window functions (LAG, RANK + PARTITION BY),
-- date functions (STRFTIME), type casting (CAST).
-- ============================================================
