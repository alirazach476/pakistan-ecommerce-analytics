"""
Generate synthetic Pakistani e-commerce datasets.

This project uses synthetic data generated to simulate a Pakistani e-commerce
marketplace. It is intended for demonstrating data engineering and analytics
skills and does not represent actual company data.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from src.data_generation.constants import (
    BRANDS,
    BUSINESS_TYPES,
    CARRIERS,
    CATEGORIES,
    FIRST_NAMES_FEMALE,
    FIRST_NAMES_MALE,
    LAST_NAMES,
    ORDER_STATUS_WEIGHTS,
    ORDER_STATUSES,
    PAKISTAN_CITIES,
    PAYMENT_METHOD_WEIGHTS,
    PAYMENT_METHODS,
    PRODUCT_NAME_TEMPLATES,
    RETURN_REASONS,
    SELLER_PREFIXES,
    SELLER_SUFFIXES,
)
from src.utils.config import get_settings
from src.utils.logging_config import setup_logging

logger = setup_logging(__name__)


def _rng(seed: int) -> np.random.Generator:
    return np.random.default_rng(seed)


def generate_locations() -> pd.DataFrame:
    rows = []
    for idx, (city, province, region, lat, lon, _weight) in enumerate(PAKISTAN_CITIES, start=1):
        rows.append(
            {
                "location_id": idx,
                "city": city,
                "province": province,
                "region": region,
                "country": "Pakistan",
                "latitude": lat,
                "longitude": lon,
            }
        )
    return pd.DataFrame(rows)


def generate_categories() -> pd.DataFrame:
    rows = []
    for idx, (name, parent, min_price, max_price) in enumerate(CATEGORIES, start=1):
        rows.append(
            {
                "category_id": idx,
                "category_name": name,
                "parent_category": parent,
                "min_price_pkr": min_price,
                "max_price_pkr": max_price,
            }
        )
    return pd.DataFrame(rows)


def generate_sellers(n: int, locations: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    location_ids = locations["location_id"].to_numpy()
    weights = np.array([c[5] for c in PAKISTAN_CITIES], dtype=float)
    weights = weights / weights.sum()

    seller_names = [
        f"{rng.choice(SELLER_PREFIXES)} {rng.choice(SELLER_SUFFIXES)} {i}"
        for i in range(1, n + 1)
    ]
    start = np.datetime64("2018-01-01")
    end = np.datetime64("2023-12-31")
    days = (end - start).astype(int)
    reg_offsets = rng.integers(0, days + 1, size=n)

    return pd.DataFrame(
        {
            "seller_id": np.arange(1, n + 1),
            "seller_name": seller_names,
            "business_type": rng.choice(BUSINESS_TYPES, size=n, p=[0.35, 0.40, 0.15, 0.10]),
            "location_id": rng.choice(location_ids, size=n, p=weights),
            "registration_date": (start + reg_offsets).astype("datetime64[D]"),
            "is_active": rng.random(n) > 0.05,
            "rating": np.round(rng.uniform(3.0, 5.0, size=n), 2),
        }
    )


def generate_customers(
    n: int, locations: pd.DataFrame, rng: np.random.Generator, seed: int = 42
) -> pd.DataFrame:
    _ = seed  # reserved for deterministic external faker seeding if re-enabled
    location_ids = locations["location_id"].to_numpy()
    weights = np.array([c[5] for c in PAKISTAN_CITIES], dtype=float)
    weights = weights / weights.sum()

    genders = rng.choice(["Male", "Female", "Other"], size=n, p=[0.52, 0.46, 0.02])
    first_names = []
    for g in genders:
        if g == "Female":
            first_names.append(str(rng.choice(FIRST_NAMES_FEMALE)))
        else:
            first_names.append(str(rng.choice(FIRST_NAMES_MALE)))

    last_names = [str(rng.choice(LAST_NAMES)) for _ in range(n)]
    # Pakistani mobile: +92-3XX-XXXXXXX
    phones = [
        f"+92-3{rng.integers(0, 10)}{rng.integers(0, 10)}-{rng.integers(1000000, 9999999)}"
        for _ in range(n)
    ]
    emails = [
        f"{fn.lower()}.{ln.lower()}{i}@example.pk"
        for i, (fn, ln) in enumerate(zip(first_names, last_names), start=1)
    ]

    start = np.datetime64("2019-01-01")
    end = np.datetime64("2025-06-30")
    days = (end - start).astype(int)
    reg_offsets = rng.integers(0, days + 1, size=n)

    birth_start = np.datetime64("1965-01-01")
    birth_days = (np.datetime64("2005-12-31") - birth_start).astype(int)
    birth_offsets = rng.integers(0, birth_days + 1, size=n)

    return pd.DataFrame(
        {
            "customer_id": np.arange(1, n + 1),
            "first_name": first_names,
            "last_name": last_names,
            "email": emails,
            "phone": phones,
            "gender": genders,
            "birth_date": (birth_start + birth_offsets).astype("datetime64[D]"),
            "location_id": rng.choice(location_ids, size=n, p=weights),
            "registration_date": (start + reg_offsets).astype("datetime64[D]"),
            "is_active": rng.random(n) > 0.08,
        }
    )


def generate_products(
    n: int,
    categories: pd.DataFrame,
    sellers: pd.DataFrame,
    rng: np.random.Generator,
) -> pd.DataFrame:
    cat_ids = categories["category_id"].to_numpy()
    # Bias toward popular categories
    cat_weights = np.array(
        [0.06, 0.14, 0.08, 0.08, 0.12, 0.07, 0.10, 0.05, 0.03, 0.04, 0.07, 0.05, 0.05, 0.03, 0.03]
    )
    cat_weights = cat_weights / cat_weights.sum()
    chosen_cats = rng.choice(cat_ids, size=n, p=cat_weights)
    seller_ids = sellers.loc[sellers["is_active"], "seller_id"].to_numpy()
    if len(seller_ids) == 0:
        seller_ids = sellers["seller_id"].to_numpy()

    price_lookup = {
        row.category_id: (row.min_price_pkr, row.max_price_pkr)
        for row in categories.itertuples()
    }
    name_lookup = {
        row.category_id: row.category_name for row in categories.itertuples()
    }

    names = []
    prices = []
    brands = []
    for i, cat_id in enumerate(chosen_cats, start=1):
        cat_name = name_lookup[cat_id]
        brand = str(rng.choice(BRANDS))
        brands.append(brand)
        template = str(rng.choice(PRODUCT_NAME_TEMPLATES[cat_name]))
        names.append(
            template.format(
                brand=brand,
                n=int(rng.integers(1, 99)),
                size=int(rng.choice([32, 43, 55, 65])),
                cap=int(rng.choice([10000, 20000, 30000])),
            )
        )
        lo, hi = price_lookup[cat_id]
        # Log-uniform within category range for realism
        price = float(np.exp(rng.uniform(np.log(lo), np.log(hi))))
        prices.append(round(price, 2))

    unit_prices = np.array(prices)
    cost_prices = np.round(unit_prices * rng.uniform(0.55, 0.82, size=n), 2)

    return pd.DataFrame(
        {
            "product_id": np.arange(1, n + 1),
            "product_name": names,
            "category_id": chosen_cats,
            "seller_id": rng.choice(seller_ids, size=n),
            "brand": brands,
            "unit_price": unit_prices,
            "cost_price": cost_prices,
            "weight_kg": np.round(rng.uniform(0.05, 40.0, size=n), 3),
            "is_active": rng.random(n) > 0.06,
        }
    )


def _random_timestamps(
    n: int,
    start: str,
    end: str,
    rng: np.random.Generator,
) -> np.ndarray:
    start_ts = np.datetime64(start)
    end_ts = np.datetime64(end)
    seconds = int((end_ts - start_ts) / np.timedelta64(1, "s"))
    offsets = rng.integers(0, seconds + 1, size=n)
    return start_ts + offsets.astype("timedelta64[s]")


def generate_orders_and_children(
    num_orders: int,
    num_returns: int,
    customers: pd.DataFrame,
    products: pd.DataFrame,
    locations: pd.DataFrame,
    start_date: str,
    end_date: str,
    rng: np.random.Generator,
) -> dict[str, pd.DataFrame]:
    """Generate orders, items, payments, shipments, and returns with referential integrity."""
    active_customers = customers.loc[customers["is_active"], "customer_id"].to_numpy()
    if len(active_customers) < 1000:
        active_customers = customers["customer_id"].to_numpy()

    # Power-law-ish customer activity: some customers order more
    cust_weights = rng.pareto(1.5, size=len(active_customers)) + 0.1
    cust_weights = cust_weights / cust_weights.sum()
    order_customer_ids = rng.choice(active_customers, size=num_orders, p=cust_weights)

    order_dates = _random_timestamps(num_orders, start_date, end_date, rng)
    # Slight upward trend: more recent dates more likely — re-sample with bias
    days_span = max(
        1, int((np.datetime64(end_date) - np.datetime64(start_date)) / np.timedelta64(1, "D"))
    )
    day_offsets = rng.beta(2.2, 1.4, size=num_orders)
    order_dates = (
        np.datetime64(start_date)
        + (day_offsets * days_span * 24 * 3600).astype(int).astype("timedelta64[s]")
    )

    statuses = rng.choice(ORDER_STATUSES, size=num_orders, p=ORDER_STATUS_WEIGHTS)
    loc_ids = locations["location_id"].to_numpy()
    loc_weights = np.array([c[5] for c in PAKISTAN_CITIES], dtype=float)
    loc_weights = loc_weights / loc_weights.sum()
    # Prefer customer's home city ~70% of the time (vectorized)
    cust_loc_map = customers.set_index("customer_id")["location_id"]
    home_locations = cust_loc_map.loc[order_customer_ids].to_numpy()
    random_locations = rng.choice(loc_ids, size=num_orders, p=loc_weights)
    use_home = rng.random(num_orders) < 0.7
    order_locations = np.where(use_home, home_locations, random_locations)

    order_ids = np.arange(1_000_001, 1_000_001 + num_orders)
    shipping_fees = np.round(rng.choice([0, 150, 200, 250, 300, 350], size=num_orders, p=[0.25, 0.15, 0.25, 0.15, 0.12, 0.08]), 2)

    # ---- Order items (vectorized chunks) ----
    active_products = products.loc[products["is_active"]].copy()
    if active_products.empty:
        active_products = products.copy()
    product_ids = active_products["product_id"].to_numpy()
    product_prices = active_products.set_index("product_id")["unit_price"]
    product_sellers = active_products.set_index("product_id")["seller_id"]

    items_per_order = rng.integers(1, 6, size=num_orders)
    total_items = int(items_per_order.sum())
    logger.info("Generating %s order items...", f"{total_items:,}")

    item_order_ids = np.repeat(order_ids, items_per_order)
    item_product_ids = rng.choice(product_ids, size=total_items)
    quantities = rng.integers(1, 5, size=total_items)
    unit_prices = product_prices.loc[item_product_ids].to_numpy(dtype=float)
    seller_ids = product_sellers.loc[item_product_ids].to_numpy()
    # Discount 0–25% on ~30% of lines
    discount_flags = rng.random(total_items) < 0.30
    discount_pct = np.where(discount_flags, rng.uniform(0.05, 0.25, size=total_items), 0.0)
    discount_amount = np.round(unit_prices * quantities * discount_pct, 2)
    line_total = np.round(unit_prices * quantities - discount_amount, 2)

    order_items = pd.DataFrame(
        {
            "order_item_id": np.arange(1, total_items + 1),
            "order_id": item_order_ids,
            "product_id": item_product_ids,
            "seller_id": seller_ids,
            "quantity": quantities,
            "unit_price": unit_prices,
            "discount_amount": discount_amount,
            "line_total": line_total,
        }
    )

    # Aggregate order totals from items
    item_agg = (
        order_items.groupby("order_id", as_index=False)
        .agg(items_subtotal=("line_total", "sum"), items_discount=("discount_amount", "sum"))
    )
    orders = pd.DataFrame(
        {
            "order_id": order_ids,
            "customer_id": order_customer_ids,
            "order_date": order_dates,
            "order_status": statuses,
            "location_id": order_locations,
            "shipping_fee": shipping_fees,
        }
    )
    orders = orders.merge(item_agg, on="order_id", how="left")
    orders["discount_amount"] = orders["items_discount"].fillna(0)
    orders["total_amount"] = np.round(
        orders["items_subtotal"].fillna(0) + orders["shipping_fee"], 2
    )
    orders["currency"] = "PKR"
    orders = orders.drop(columns=["items_subtotal", "items_discount"])

    # Cancelled orders: zero shipping sometimes already set; keep totals for analytics
    # Returned / cancelled still retain historical amounts

    # ---- Payments (vectorized status assignment) ----
    payment_methods = rng.choice(PAYMENT_METHODS, size=num_orders, p=PAYMENT_METHOD_WEIGHTS)
    payment_statuses = np.full(num_orders, "Pending", dtype=object)

    cancelled_mask = statuses == "Cancelled"
    returned_mask = statuses == "Returned"
    pending_mask = statuses == "Pending"
    active_mask = np.isin(statuses, ["Delivered", "Shipped", "Confirmed"])

    n_cancelled = int(cancelled_mask.sum())
    if n_cancelled:
        payment_statuses[cancelled_mask] = rng.choice(
            ["Failed", "Refunded", "Pending"], size=n_cancelled, p=[0.5, 0.3, 0.2]
        )
    payment_statuses[returned_mask] = "Refunded"

    cod_not_delivered = active_mask & (payment_methods == "Cash on Delivery") & (
        statuses != "Delivered"
    )
    pay_now = active_mask & ~cod_not_delivered
    n_pay = int(pay_now.sum())
    if n_pay:
        payment_statuses[pay_now] = np.where(
            rng.random(n_pay) > 0.03, "Paid", "Failed"
        )
    payment_statuses[cod_not_delivered] = "Pending"
    payment_statuses[pending_mask] = "Pending"

    payment_dates = order_dates + rng.integers(0, 3 * 24 * 3600, size=num_orders).astype(
        "timedelta64[s]"
    )
    payments = pd.DataFrame(
        {
            "payment_id": np.arange(1, num_orders + 1),
            "order_id": order_ids,
            "payment_method": payment_methods,
            "payment_status": payment_statuses,
            "payment_amount": orders["total_amount"].to_numpy(),
            "payment_date": payment_dates,
            "transaction_ref": [f"TXN-{oid}" for oid in order_ids],
        }
    )

    # ---- Shipments (vectorized) ----
    ship_delay_days = rng.integers(1, 4, size=num_orders)
    deliv_delay_days = rng.integers(1, 10, size=num_orders)
    promise_days_early = rng.integers(3, 8, size=num_orders)
    promise_days_late = rng.integers(3, 7, size=num_orders)

    not_shipped_mask = np.isin(statuses, ["Pending", "Confirmed", "Cancelled"])
    shipped_only_mask = statuses == "Shipped"
    completed_mask = np.isin(statuses, ["Delivered", "Returned"])

    shipment_dates = np.full(num_orders, np.datetime64("NaT"), dtype="datetime64[s]")
    delivery_dates = np.full(num_orders, np.datetime64("NaT"), dtype="datetime64[s]")

    shipment_dates[shipped_only_mask | completed_mask] = (
        order_dates[shipped_only_mask | completed_mask]
        + ship_delay_days[shipped_only_mask | completed_mask].astype("timedelta64[D]")
    )
    delivery_dates[completed_mask] = (
        shipment_dates[completed_mask]
        + deliv_delay_days[completed_mask].astype("timedelta64[D]")
    )

    promised = (order_dates + np.timedelta64(5, "D")).astype("datetime64[D]")
    promised[shipped_only_mask] = (
        order_dates[shipped_only_mask]
        + promise_days_early[shipped_only_mask].astype("timedelta64[D]")
    ).astype("datetime64[D]")
    promised[completed_mask] = (
        order_dates[completed_mask]
        + promise_days_late[completed_mask].astype("timedelta64[D]")
    ).astype("datetime64[D]")

    delivery_status = np.full(num_orders, "Not Shipped", dtype=object)
    delivery_status[statuses == "Cancelled"] = "Cancelled"
    delivery_status[shipped_only_mask] = "In Transit"
    delivery_status[completed_mask] = "Delivered"

    shipments = pd.DataFrame(
        {
            "shipment_id": np.arange(1, num_orders + 1),
            "order_id": order_ids,
            "carrier": rng.choice(CARRIERS, size=num_orders),
            "shipment_date": shipment_dates,
            "delivery_date": delivery_dates,
            "promised_delivery_date": promised,
            "delivery_status": delivery_status,
            "tracking_number": [f"PK{oid}" for oid in order_ids],
        }
    )

    # ---- Returns ----
    delivered_returned_mask = np.isin(statuses, ["Delivered", "Returned"])
    eligible_order_ids = order_ids[delivered_returned_mask]
    # Prefer orders marked Returned, then sample Delivered
    returned_status_ids = order_ids[statuses == "Returned"]
    delivered_ids = order_ids[statuses == "Delivered"]

    target_returns = min(num_returns, len(eligible_order_ids))
    chosen_orders = list(returned_status_ids)
    remaining = target_returns - len(chosen_orders)
    if remaining > 0 and len(delivered_ids) > 0:
        extra = rng.choice(
            delivered_ids,
            size=min(remaining, len(delivered_ids)),
            replace=False,
        )
        chosen_orders.extend(extra.tolist())

    chosen_orders = chosen_orders[:target_returns]
    items_by_order = order_items.groupby("order_id")["order_item_id"].apply(list).to_dict()
    order_date_map = dict(zip(order_ids, order_dates))
    delivery_map = dict(zip(order_ids, delivery_dates))
    item_line_map = order_items.set_index("order_item_id")["line_total"].to_dict()

    return_rows = []
    rid = 1
    for oid in chosen_orders:
        item_list = items_by_order.get(oid, [])
        if not item_list:
            continue
        item_id = int(rng.choice(item_list))
        deliv = delivery_map.get(oid)
        base = deliv if not pd.isna(deliv) else order_date_map[oid]
        ret_date = base + np.timedelta64(int(rng.integers(1, 15)), "D")
        refund = round(float(item_line_map[item_id]) * float(rng.uniform(0.5, 1.0)), 2)
        return_rows.append(
            {
                "return_id": rid,
                "order_id": oid,
                "order_item_id": item_id,
                "return_date": ret_date,
                "return_reason": str(rng.choice(RETURN_REASONS)),
                "refund_amount": refund,
                "return_status": str(rng.choice(["Approved", "Completed", "Pending"], p=[0.2, 0.7, 0.1])),
            }
        )
        rid += 1

    returns = pd.DataFrame(return_rows)
    logger.info("Generated %s returns", f"{len(returns):,}")

    return {
        "orders": orders,
        "order_items": order_items,
        "payments": payments,
        "shipments": shipments,
        "returns": returns,
    }


def _write_csv(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    logger.info("Wrote %s rows -> %s", f"{len(df):,}", path.name)


def generate_all(output_dir: Path | None = None) -> dict[str, int]:
    """Generate all synthetic datasets and write CSV files to data/raw."""
    settings = get_settings()
    rng = _rng(settings.random_seed)
    out = output_dir or settings.raw_path
    out.mkdir(parents=True, exist_ok=True)

    logger.info("Pipeline started — synthetic data generation")
    logger.info(
        "Targets: customers=%s products=%s sellers=%s orders=%s returns=%s",
        f"{settings.num_customers:,}",
        f"{settings.num_products:,}",
        f"{settings.num_sellers:,}",
        f"{settings.num_orders:,}",
        f"{settings.num_returns:,}",
    )

    locations = generate_locations()
    categories = generate_categories()
    # Persist price bounds only in generator metadata; raw.categories omits them in load
    categories_out = categories[["category_id", "category_name", "parent_category"]].copy()

    sellers = generate_sellers(settings.num_sellers, locations, rng)
    customers = generate_customers(
        settings.num_customers, locations, rng, settings.random_seed
    )
    products = generate_products(settings.num_products, categories, sellers, rng)

    children = generate_orders_and_children(
        num_orders=settings.num_orders,
        num_returns=settings.num_returns,
        customers=customers,
        products=products,
        locations=locations,
        start_date=settings.data_start_date,
        end_date=settings.data_end_date,
        rng=rng,
    )

    datasets = {
        "locations": locations,
        "categories": categories_out,
        "sellers": sellers,
        "customers": customers,
        "products": products,
        "orders": children["orders"],
        "order_items": children["order_items"],
        "payments": children["payments"],
        "shipments": children["shipments"],
        "returns": children["returns"],
    }

    for name, df in datasets.items():
        # Normalize datetime columns to ISO strings for CSV stability
        for col in df.columns:
            if np.issubdtype(df[col].dtype, np.datetime64):
                df[col] = pd.to_datetime(df[col]).astype(str).replace("NaT", "")
        _write_csv(df, out / f"{name}.csv")

    stats = {name: len(df) for name, df in datasets.items()}
    meta = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "synthetic": True,
        "disclaimer": (
            "This project uses synthetic data generated to simulate a Pakistani "
            "e-commerce marketplace. It is intended for demonstrating data engineering "
            "and analytics skills and does not represent actual company data."
        ),
        "random_seed": settings.random_seed,
        "date_range": {
            "start": settings.data_start_date,
            "end": settings.data_end_date,
        },
        "row_counts": stats,
        "currency": "PKR",
    }
    meta_path = out / "generation_metadata.json"
    meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
    logger.info("Wrote metadata -> %s", meta_path.name)

    logger.info("=== Generation Statistics ===")
    for name, count in stats.items():
        logger.info("  %s: %s", name, f"{count:,}")
    logger.info("Pipeline completed — data generation")
    return stats


def main() -> None:
    stats = generate_all()
    print("\nSynthetic data generation complete:")
    for name, count in stats.items():
        print(f"  {name:15s} {count:,}")


if __name__ == "__main__":
    main()
