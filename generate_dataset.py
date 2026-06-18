"""
QuickBite Analytics - Synthetic Dataset Generator
Modeled on the Bangladesh food delivery market (Pathao Food / Foodpanda style)

Generates 5 CSV files:
  1. restaurants.csv      ~500 restaurants
  2. customers.csv        ~8,000 customers
  3. campaigns.csv        ~12 marketing campaigns
  4. riders.csv           ~600 delivery riders
  5. orders.csv           ~75,000 orders over 12 months

Includes deliberately planted business patterns for analytical discovery:
  - One city showing order decline after month 8 (Chittagong - competitor entry)
  - Weekend (Fri-Sat in Bangladesh) spike in biryani/kebab orders
  - One campaign with negative ROI, one with stellar ROI
  - Delivery time issues in Old Dhaka during 7-9 PM
  - High churn in customers acquired during the loss-making campaign
"""

import csv
import random
from datetime import datetime, timedelta
from pathlib import Path

random.seed(42)

OUTPUT_DIR = Path("/home/claude/quickbite/data")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================
# BANGLADESH MARKET REFERENCE DATA
# ============================================================

CITIES = {
    "Dhaka":      {"weight": 0.62, "areas": [
        "Dhanmondi", "Gulshan", "Banani", "Uttara", "Mirpur", "Mohammadpur",
        "Bashundhara", "Old Dhaka", "Motijheel", "Tejgaon", "Khilgaon",
        "Wari", "Lalmatia", "Farmgate", "Shantinagar"
    ]},
    "Chittagong": {"weight": 0.18, "areas": [
        "Agrabad", "GEC Circle", "Nasirabad", "Khulshi", "Panchlaish",
        "Halishahar", "Chawkbazar"
    ]},
    "Sylhet":     {"weight": 0.08, "areas": [
        "Zindabazar", "Subid Bazar", "Amberkhana", "Bandarbazar", "Uposhohor"
    ]},
    "Rajshahi":   {"weight": 0.06, "areas": [
        "Shaheb Bazar", "Kazla", "Boalia", "Motihar"
    ]},
    "Khulna":     {"weight": 0.06, "areas": [
        "Khalishpur", "Daulatpur", "Sonadanga", "Khan Jahan Ali Road"
    ]},
}

CUISINES = {
    "Bangladeshi":    {"weight": 0.28, "avg_price": 280, "weekend_boost": 1.35},
    "Biryani & Kebab":{"weight": 0.18, "avg_price": 380, "weekend_boost": 1.55},
    "Fast Food":      {"weight": 0.16, "avg_price": 220, "weekend_boost": 1.10},
    "Chinese":        {"weight": 0.10, "avg_price": 420, "weekend_boost": 1.25},
    "Indian":         {"weight": 0.08, "avg_price": 450, "weekend_boost": 1.20},
    "Pizza":          {"weight": 0.07, "avg_price": 650, "weekend_boost": 1.30},
    "Burger":         {"weight": 0.06, "avg_price": 320, "weekend_boost": 1.15},
    "Thai":           {"weight": 0.03, "avg_price": 580, "weekend_boost": 1.20},
    "Desserts":       {"weight": 0.02, "avg_price": 180, "weekend_boost": 1.40},
    "Coffee & Bakery":{"weight": 0.02, "avg_price": 260, "weekend_boost": 1.10},
}

# Realistic-style restaurant name components for Bangladesh market
BD_RESTAURANT_PREFIXES = [
    "Kacchi", "Star", "Royal", "Sultan's", "Nawabi", "Haji", "Dhaka",
    "Chittagong", "Sylheti", "Bengal", "Padma", "Meghna", "Jamuna",
    "Golden", "Silver", "Tasty", "Spicy", "Hot", "Crispy", "Fresh"
]
BD_RESTAURANT_SUFFIXES = [
    "Bhai", "House", "Kitchen", "Restaurant", "Dhaba", "Hut", "Corner",
    "Express", "Palace", "Garden", "Cafe", "Biryani", "Hotel", "Diner"
]

PAYMENT_METHODS = [
    ("bKash",   0.42),
    ("Cash",    0.31),
    ("Nagad",   0.14),
    ("Card",    0.09),
    ("Rocket",  0.04),
]

AGE_GROUPS = [
    ("18-24", 0.28),
    ("25-34", 0.41),
    ("35-44", 0.19),
    ("45-54", 0.08),
    ("55+",   0.04),
]

# ============================================================
# HELPERS
# ============================================================

def weighted_choice(items, weight_key="weight"):
    """Pick from a list of (key, weight) tuples or dict with weights."""
    if isinstance(items, dict):
        keys = list(items.keys())
        weights = [items[k][weight_key] for k in keys]
        return random.choices(keys, weights=weights, k=1)[0]
    keys = [x[0] for x in items]
    weights = [x[1] for x in items]
    return random.choices(keys, weights=weights, k=1)[0]


def random_date_between(start, end):
    delta = end - start
    seconds = random.randint(0, int(delta.total_seconds()))
    return start + timedelta(seconds=seconds)


# ============================================================
# 1. RESTAURANTS
# ============================================================

def generate_restaurants(n=500):
    restaurants = []
    used_names = set()

    for i in range(1, n + 1):
        city = weighted_choice(CITIES)
        area = random.choice(CITIES[city]["areas"])
        cuisine = weighted_choice(CUISINES)

        # Generate non-duplicate name, with fallback numbering
        attempt = 0
        while True:
            name = f"{random.choice(BD_RESTAURANT_PREFIXES)} {random.choice(BD_RESTAURANT_SUFFIXES)}"
            if attempt > 30:
                name = f"{name} {i}"  # guarantee uniqueness
            if name not in used_names:
                used_names.add(name)
                break
            attempt += 1

        # Partner-since date between Jan 2022 and Jun 2024
        partner_since = random_date_between(
            datetime(2022, 1, 1), datetime(2024, 6, 30)
        ).strftime("%Y-%m-%d")

        # Quality tier - affects rating distribution
        tier = random.choices(["Premium", "Standard", "Budget"],
                              weights=[0.20, 0.55, 0.25], k=1)[0]
        base_rating = {"Premium": 4.4, "Standard": 4.0, "Budget": 3.5}[tier]
        avg_rating = round(min(5.0, max(2.5, random.gauss(base_rating, 0.35))), 1)

        restaurants.append({
            "restaurant_id":     f"R{i:04d}",
            "restaurant_name":   name,
            "city":              city,
            "area":              area,
            "cuisine_type":      cuisine,
            "tier":              tier,
            "avg_rating":        avg_rating,
            "partner_since":     partner_since,
        })

    return restaurants


# ============================================================
# 2. CUSTOMERS
# ============================================================

def generate_customers(n=8000):
    customers = []
    for i in range(1, n + 1):
        city = weighted_choice(CITIES)
        age_group = weighted_choice(AGE_GROUPS)

        # Signup date between Jan 2024 and Oct 2025
        signup_date = random_date_between(
            datetime(2024, 1, 1), datetime(2025, 10, 31)
        ).strftime("%Y-%m-%d")

        # Customer segment - affects order frequency
        segment = random.choices(["High Value", "Regular", "Occasional"],
                                 weights=[0.15, 0.50, 0.35], k=1)[0]

        customers.append({
            "customer_id":  f"C{i:05d}",
            "city":         city,
            "age_group":    age_group,
            "segment":      segment,
            "signup_date":  signup_date,
        })

    return customers


# ============================================================
# 3. CAMPAIGNS
# ============================================================

def generate_campaigns():
    """
    12 campaigns over the year. Some deliberately good, some deliberately bad.
    """
    campaigns = [
        # name, start, end, discount_pct, target_cities, planted_quality
        ("New Year Feast 2025",      "2025-01-01", "2025-01-10", 25, "All",                          "good"),
        ("Pohela Boishakh Special",  "2025-04-12", "2025-04-15", 30, "Dhaka,Chittagong",             "stellar"),
        ("Summer Cooler",            "2025-05-01", "2025-05-15", 15, "All",                          "neutral"),
        ("Eid-ul-Fitr Bonanza",      "2025-03-28", "2025-04-02", 35, "All",                          "stellar"),
        ("Student Discount Week",    "2025-06-10", "2025-06-20", 20, "Dhaka",                        "good"),
        ("Monsoon Munchies",         "2025-07-15", "2025-07-31", 40, "All",                          "bad"),     # too deep discount
        ("Independence Day Treat",   "2025-08-15", "2025-08-17", 25, "All",                          "good"),
        ("Eid-ul-Azha Special",      "2025-06-06", "2025-06-09", 30, "All",                          "good"),
        ("Weekend Warrior",          "2025-09-01", "2025-09-30", 18, "Dhaka,Chittagong,Sylhet",      "good"),
        ("First Order Free Delivery","2025-02-01", "2025-02-28", 0,  "All",                          "stellar"), # acquisition
        ("Late Night Cravings",      "2025-10-01", "2025-10-31", 22, "Dhaka",                        "neutral"),
        ("Winter Warmers",           "2025-11-15", "2025-12-15", 20, "All",                          "good"),
    ]

    out = []
    for i, c in enumerate(campaigns, 1):
        out.append({
            "campaign_id":     f"CMP{i:03d}",
            "campaign_name":   c[0],
            "start_date":      c[1],
            "end_date":        c[2],
            "discount_percent":c[3],
            "target_cities":   c[4],
            "planted_quality": c[5],   # used internally for order generation
        })
    return out


# ============================================================
# 4. RIDERS
# ============================================================

def generate_riders(n=600):
    riders = []
    for i in range(1, n + 1):
        city = weighted_choice(CITIES)
        joining_date = random_date_between(
            datetime(2023, 1, 1), datetime(2025, 8, 31)
        ).strftime("%Y-%m-%d")

        riders.append({
            "rider_id":     f"D{i:04d}",
            "city":         city,
            "joining_date": joining_date,
            "vehicle_type": random.choices(["Motorbike", "Bicycle"],
                                           weights=[0.85, 0.15], k=1)[0],
        })
    return riders


# ============================================================
# 5. ORDERS  (the big one - with planted patterns)
# ============================================================

def generate_orders(restaurants, customers, campaigns, riders, n=75000):
    orders = []

    # Index lookups
    rest_by_city = {}
    for r in restaurants:
        rest_by_city.setdefault(r["city"], []).append(r)

    cust_by_city = {}
    for c in customers:
        cust_by_city.setdefault(c["city"], []).append(c)

    rider_by_city = {}
    for d in riders:
        rider_by_city.setdefault(d["city"], []).append(d)

    # Order window: Jan 1 2025 to Dec 31 2025
    start = datetime(2025, 1, 1)
    end   = datetime(2025, 12, 31, 23, 59, 59)
    total_seconds = int((end - start).total_seconds())

    # Build campaign lookup BY DATE for O(1) access -- key insight to speed this up
    # Map date -> list of (campaign_dict, target_cities_set_or_None, use_prob)
    campaign_by_date = {}
    for camp in campaigns:
        cs = datetime.strptime(camp["start_date"], "%Y-%m-%d").date()
        ce = datetime.strptime(camp["end_date"], "%Y-%m-%d").date()
        targets = set(camp["target_cities"].split(",")) if camp["target_cities"] != "All" else None
        use_prob = {"stellar": 0.85, "good": 0.55, "neutral": 0.30, "bad": 0.70}[camp["planted_quality"]]
        d = cs
        while d <= ce:
            campaign_by_date.setdefault(d, []).append((camp, targets, use_prob))
            d += timedelta(days=1)

    # Precompute weight list for cities once
    city_keys = list(CITIES.keys())
    city_weights = [CITIES[c]["weight"] for c in city_keys]
    other_cities = [c for c in city_keys if c != "Chittagong"]
    other_weights = [CITIES[c]["weight"] for c in other_cities]
    competitor_cutoff = datetime(2025, 8, 15)

    for i in range(1, n + 1):
        # ---- Order datetime ----
        order_dt = start + timedelta(seconds=random.randint(0, total_seconds))

        # ---- Pick city with planted Chittagong decline pattern ----
        city = random.choices(city_keys, weights=city_weights, k=1)[0]
        if city == "Chittagong" and order_dt >= competitor_cutoff:
            if random.random() < 0.55:
                city = random.choices(other_cities, weights=other_weights, k=1)[0]

        # Pick restaurant in that city
        if city not in rest_by_city or not rest_by_city[city]:
            city = "Dhaka"
        restaurant = random.choice(rest_by_city[city])

        # Pick customer in that city
        if city in cust_by_city and cust_by_city[city]:
            customer = random.choice(cust_by_city[city])
        else:
            customer = random.choice(customers)

        # Pick rider in that city
        if city in rider_by_city and rider_by_city[city]:
            rider = random.choice(rider_by_city[city])
        else:
            rider = random.choice(riders)

        # ---- Order value ----
        cuisine_info = CUISINES[restaurant["cuisine_type"]]
        base_price = cuisine_info["avg_price"]
        is_weekend = order_dt.weekday() in (4, 5)  # Fri & Sat
        weekend_mult = cuisine_info["weekend_boost"] if is_weekend else 1.0
        n_items = random.choices([1, 2, 3, 4, 5], weights=[0.15, 0.35, 0.28, 0.15, 0.07], k=1)[0]
        order_value = round(base_price * n_items * weekend_mult * random.uniform(0.75, 1.40), 0)

        # ---- Campaign / discount (O(1) lookup now) ----
        discount_amount = 0
        campaign_id = ""
        active = campaign_by_date.get(order_dt.date())
        if active:
            for camp, targets, use_prob in active:
                if (targets is None or city in targets) and random.random() < use_prob:
                    campaign_id = camp["campaign_id"]
                    discount_amount = round(order_value * camp["discount_percent"] / 100, 0)
                    break

        net_value = order_value - discount_amount

        # ---- Delivery time ----
        hour = order_dt.hour
        base_delivery = random.gauss(38, 8)
        if restaurant["area"] == "Old Dhaka" and 19 <= hour <= 21:
            base_delivery += random.gauss(22, 6)
        if is_weekend and 13 <= hour <= 15:
            base_delivery += random.gauss(8, 3)
        delivery_time_minutes = max(12, int(base_delivery))

        # ---- Rating ----
        rating_base = restaurant["avg_rating"]
        if delivery_time_minutes > 55:
            rating_base -= 0.7
        elif delivery_time_minutes > 45:
            rating_base -= 0.3
        rating = max(1, min(5, round(random.gauss(rating_base, 0.5))))
        if random.random() < 0.12:
            rating = ""

        payment = weighted_choice(PAYMENT_METHODS)

        orders.append({
            "order_id":              f"O{i:07d}",
            "order_datetime":        order_dt.strftime("%Y-%m-%d %H:%M:%S"),
            "customer_id":           customer["customer_id"],
            "restaurant_id":         restaurant["restaurant_id"],
            "rider_id":              rider["rider_id"],
            "city":                  city,
            "area":                  restaurant["area"],
            "cuisine_type":          restaurant["cuisine_type"],
            "items_count":           n_items,
            "order_value_bdt":       order_value,
            "discount_bdt":          discount_amount,
            "net_value_bdt":         net_value,
            "campaign_id":           campaign_id,
            "payment_method":        payment,
            "delivery_time_minutes": delivery_time_minutes,
            "rating":                rating,
        })

    # Sort orders by datetime for realism
    orders.sort(key=lambda x: x["order_datetime"])
    # Re-id sequentially after sort
    for idx, o in enumerate(orders, 1):
        o["order_id"] = f"O{idx:07d}"

    return orders


# ============================================================
# WRITE TO CSV
# ============================================================

def write_csv(filename, rows, fieldnames=None):
    if not rows:
        return
    if fieldnames is None:
        fieldnames = list(rows[0].keys())
    path = OUTPUT_DIR / filename
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"  Wrote {len(rows):>6,} rows  ->  {path.name}")


def main():
    print("\n=== QuickBite Dataset Generator ===\n")

    print("Generating restaurants...")
    restaurants = generate_restaurants(500)
    write_csv("restaurants.csv", restaurants)

    print("Generating customers...")
    customers = generate_customers(8000)
    write_csv("customers.csv", customers)

    print("Generating campaigns...")
    campaigns = generate_campaigns()
    # Drop the internal 'planted_quality' column before writing
    public_campaigns = [{k: v for k, v in c.items() if k != "planted_quality"}
                        for c in campaigns]
    write_csv("campaigns.csv", public_campaigns)

    print("Generating riders...")
    riders = generate_riders(600)
    write_csv("riders.csv", riders)

    print("Generating orders (this takes ~30 seconds)...")
    orders = generate_orders(restaurants, customers, campaigns, riders, 75000)
    write_csv("orders.csv", orders)

    print("\n=== Done ===")
    print(f"All files saved to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
