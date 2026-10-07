"""Tests for raw data validation rules."""

from __future__ import annotations

import pandas as pd

from src.validation.validate_raw import validate_table


def _base_datasets():
    locations = pd.DataFrame(
        {"location_id": [1], "city": ["Lahore"], "province": ["Punjab"], "region": ["Central"], "country": ["Pakistan"]}
    )
    categories = pd.DataFrame({"category_id": [1], "category_name": ["Fashion"]})
    sellers = pd.DataFrame(
        {
            "seller_id": [1],
            "seller_name": ["Test Seller"],
            "location_id": [1],
            "registration_date": ["2020-01-01"],
        }
    )
    customers = pd.DataFrame(
        {
            "customer_id": [1],
            "first_name": ["Ali"],
            "last_name": ["Khan"],
            "email": ["ali@example.pk"],
            "location_id": [1],
        }
    )
    products = pd.DataFrame(
        {
            "product_id": [1],
            "product_name": ["Shirt"],
            "category_id": [1],
            "seller_id": [1],
            "unit_price": [1000],
        }
    )
    orders = pd.DataFrame(
        {
            "order_id": [1],
            "customer_id": [1],
            "order_date": ["2024-01-01"],
            "order_status": ["Delivered"],
            "total_amount": [1000],
        }
    )
    order_items = pd.DataFrame(
        {
            "order_item_id": [1],
            "order_id": [1],
            "product_id": [1],
            "quantity": [1],
            "unit_price": [1000],
        }
    )
    return {
        "locations": locations,
        "categories": categories,
        "sellers": sellers,
        "customers": customers,
        "products": products,
        "orders": orders,
        "order_items": order_items,
        "payments": pd.DataFrame(
            {
                "payment_id": [1],
                "order_id": [1],
                "payment_method": ["Cash on Delivery"],
                "payment_status": ["Paid"],
                "payment_amount": [1000],
            }
        ),
        "shipments": pd.DataFrame(
            {
                "shipment_id": [1],
                "order_id": [1],
                "delivery_status": ["Delivered"],
                "shipment_date": ["2024-01-02"],
                "delivery_date": ["2024-01-05"],
            }
        ),
        "returns": pd.DataFrame(
            {
                "return_id": [1],
                "order_id": [1],
                "order_item_id": [1],
                "return_reason": ["Damaged"],
                "refund_amount": [500],
            }
        ),
    }


def test_valid_orders_pass():
    ds = _base_datasets()
    report = validate_table("orders", ds["orders"], ds)
    assert report.ok


def test_invalid_order_status_fails():
    ds = _base_datasets()
    ds["orders"].loc[0, "order_status"] = "Unknown"
    report = validate_table("orders", ds["orders"], ds)
    assert not report.ok


def test_duplicate_customer_id_fails():
    ds = _base_datasets()
    ds["customers"] = pd.concat([ds["customers"], ds["customers"]], ignore_index=True)
    report = validate_table("customers", ds["customers"], ds)
    assert not report.ok


def test_negative_quantity_fails():
    ds = _base_datasets()
    ds["order_items"].loc[0, "quantity"] = 0
    report = validate_table("order_items", ds["order_items"], ds)
    assert not report.ok
