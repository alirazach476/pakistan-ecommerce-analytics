"""Tests for synthetic data generation (small scale)."""

from __future__ import annotations

import numpy as np
import pandas as pd

from src.data_generation.generate import (
    generate_categories,
    generate_customers,
    generate_locations,
    generate_orders_and_children,
    generate_products,
    generate_sellers,
)


def test_locations_cover_major_provinces():
    locs = generate_locations()
    provinces = set(locs["province"])
    assert "Punjab" in provinces
    assert "Sindh" in provinces
    assert "Khyber Pakhtunkhwa" in provinces
    assert len(locs) >= 20


def test_referential_integrity_small_batch(tmp_path):
    rng = np.random.default_rng(0)
    locations = generate_locations()
    categories = generate_categories()
    sellers = generate_sellers(50, locations, rng)
    customers = generate_customers(200, locations, rng, seed=0)
    products = generate_products(100, categories, sellers, rng)
    children = generate_orders_and_children(
        num_orders=500,
        num_returns=40,
        customers=customers,
        products=products,
        locations=locations,
        start_date="2024-01-01",
        end_date="2024-06-30",
        rng=rng,
    )

    orders = children["orders"]
    items = children["order_items"]
    payments = children["payments"]
    returns = children["returns"]

    assert orders["customer_id"].isin(customers["customer_id"]).all()
    assert items["order_id"].isin(orders["order_id"]).all()
    assert items["product_id"].isin(products["product_id"]).all()
    assert payments["order_id"].isin(orders["order_id"]).all()
    assert returns["order_item_id"].isin(items["order_item_id"]).all()
    assert (items["quantity"] > 0).all()
    assert (orders["total_amount"] >= 0).all()
    assert len(items) >= 500
