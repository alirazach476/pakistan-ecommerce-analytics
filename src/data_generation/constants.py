"""Pakistan-specific reference data for synthetic generation.

This project uses synthetic data generated to simulate a Pakistani e-commerce
marketplace. It is intended for demonstrating data engineering and analytics
skills and does not represent actual company data.
"""

from __future__ import annotations

# city, province, region, approx lat, approx lon, population weight
PAKISTAN_CITIES: list[tuple[str, str, str, float, float, float]] = [
    ("Karachi", "Sindh", "South", 24.8607, 67.0011, 16.0),
    ("Lahore", "Punjab", "Central", 31.5204, 74.3587, 13.0),
    ("Faisalabad", "Punjab", "Central", 31.4504, 73.1350, 3.5),
    ("Rawalpindi", "Punjab", "North", 33.5651, 73.0169, 2.5),
    ("Islamabad", "Islamabad Capital Territory", "North", 33.6844, 73.0479, 1.8),
    ("Multan", "Punjab", "South", 30.1575, 71.5249, 2.2),
    ("Gujranwala", "Punjab", "Central", 32.1877, 74.1945, 2.0),
    ("Peshawar", "Khyber Pakhtunkhwa", "North", 34.0151, 71.5249, 2.1),
    ("Quetta", "Balochistan", "West", 30.1798, 66.9750, 1.2),
    ("Hyderabad", "Sindh", "South", 25.3960, 68.3578, 1.8),
    ("Sialkot", "Punjab", "Central", 32.4945, 74.5229, 1.0),
    ("Bahawalpur", "Punjab", "South", 29.3956, 71.6836, 0.9),
    ("Sargodha", "Punjab", "Central", 32.0836, 72.6711, 0.8),
    ("Sukkur", "Sindh", "South", 27.7052, 68.8574, 0.6),
    ("Abbottabad", "Khyber Pakhtunkhwa", "North", 34.1688, 73.2215, 0.5),
    ("Gujrat", "Punjab", "Central", 32.5731, 74.0789, 0.6),
    ("Sheikhupura", "Punjab", "Central", 31.7167, 73.9850, 0.6),
    ("Jhelum", "Punjab", "North", 32.9425, 73.7257, 0.4),
    ("Mardan", "Khyber Pakhtunkhwa", "North", 34.1989, 72.0231, 0.5),
    ("Wah Cantt", "Punjab", "North", 33.7700, 72.7500, 0.4),
    ("Larkana", "Sindh", "South", 27.5590, 68.2120, 0.5),
    ("Mingora", "Khyber Pakhtunkhwa", "North", 34.7717, 72.3600, 0.4),
    ("Mirpur", "Azad Jammu and Kashmir", "North", 33.1478, 73.7516, 0.3),
    ("Muzaffarabad", "Azad Jammu and Kashmir", "North", 34.3700, 73.4711, 0.25),
    ("Gilgit", "Gilgit-Baltistan", "North", 35.9208, 74.3089, 0.2),
    ("Skardu", "Gilgit-Baltistan", "North", 35.2971, 75.6339, 0.15),
    ("Turbat", "Balochistan", "West", 26.0042, 63.0600, 0.2),
    ("Gwadar", "Balochistan", "West", 25.1264, 62.3225, 0.15),
]

CATEGORIES: list[tuple[str, str | None, int, int]] = [
    # name, parent, min_price_pkr, max_price_pkr
    ("Electronics", None, 2_000, 250_000),
    ("Mobile Phones", "Electronics", 50_000, 400_000),
    ("Computers & Laptops", "Electronics", 40_000, 450_000),
    ("Home Appliances", None, 5_000, 200_000),
    ("Fashion", None, 500, 25_000),
    ("Beauty", None, 200, 15_000),
    ("Grocery", None, 50, 5_000),
    ("Sports", None, 500, 50_000),
    ("Books", None, 200, 8_000),
    ("Automotive", None, 500, 80_000),
    ("Home & Kitchen", None, 300, 40_000),
    ("Furniture", None, 10_000, 300_000),
    ("Health & Personal Care", None, 200, 20_000),
    ("Toys", None, 300, 15_000),
    ("Accessories", None, 500, 20_000),
]

PRODUCT_NAME_TEMPLATES: dict[str, list[str]] = {
    "Electronics": [
        "{brand} Smart TV {size} inch",
        "{brand} Bluetooth Speaker",
        "{brand} Power Bank {cap}mAh",
        "{brand} Wireless Earbuds",
        "{brand} LED Monitor {size} inch",
    ],
    "Mobile Phones": [
        "{brand} Phone X{n}",
        "{brand} Smartphone Pro {n}",
        "{brand} Mobile {n}G",
        "{brand} Nova {n}",
        "{brand} Note {n}",
    ],
    "Computers & Laptops": [
        "{brand} Laptop {n} Core",
        "{brand} Notebook Ultra {n}",
        "{brand} Desktop PC {n}",
        "{brand} Gaming Laptop {n}",
        "{brand} Ultrabook {n}",
    ],
    "Home Appliances": [
        "{brand} Refrigerator {n}L",
        "{brand} Washing Machine {n}kg",
        "{brand} Microwave Oven",
        "{brand} Air Conditioner {n} Ton",
        "{brand} Water Dispenser",
    ],
    "Fashion": [
        "{brand} Cotton Kurta",
        "{brand} Denim Jeans",
        "{brand} Formal Shirt",
        "{brand} Winter Shawl",
        "{brand} Casual Sneakers",
    ],
    "Beauty": [
        "{brand} Face Cream",
        "{brand} Hair Oil",
        "{brand} Perfume {n}ml",
        "{brand} Lipstick Set",
        "{brand} Skincare Kit",
    ],
    "Grocery": [
        "{brand} Basmati Rice {n}kg",
        "{brand} Cooking Oil {n}L",
        "{brand} Tea {n}g",
        "{brand} Spices Pack",
        "{brand} Flour {n}kg",
    ],
    "Sports": [
        "{brand} Cricket Bat",
        "{brand} Football Size {n}",
        "{brand} Gym Dumbbells {n}kg",
        "{brand} Yoga Mat",
        "{brand} Running Shoes",
    ],
    "Books": [
        "{brand} Urdu Novel Vol {n}",
        "{brand} Exam Prep Guide",
        "{brand} Children's Storybook",
        "{brand} Business Handbook",
        "{brand} Cookbook",
    ],
    "Automotive": [
        "{brand} Car Phone Holder",
        "{brand} Engine Oil {n}L",
        "{brand} Car Floor Mats",
        "{brand} Dash Camera",
        "{brand} Tyre Inflator",
    ],
    "Home & Kitchen": [
        "{brand} Non-stick Cookware Set",
        "{brand} Electric Kettle",
        "{brand} Dinner Set {n} pcs",
        "{brand} Blender",
        "{brand} Storage Containers",
    ],
    "Furniture": [
        "{brand} Sofa Set {n} Seater",
        "{brand} Study Table",
        "{brand} Wardrobe {n} Door",
        "{brand} Dining Table Set",
        "{brand} Office Chair",
    ],
    "Health & Personal Care": [
        "{brand} Multivitamins",
        "{brand} Electric Toothbrush",
        "{brand} Blood Pressure Monitor",
        "{brand} Hand Sanitizer Pack",
        "{brand} First Aid Kit",
    ],
    "Toys": [
        "{brand} Remote Control Car",
        "{brand} Building Blocks Set",
        "{brand} Soft Teddy Bear",
        "{brand} Educational Puzzle",
        "{brand} Doll House",
    ],
    "Accessories": [
        "{brand} Leather Wallet",
        "{brand} Sunglasses",
        "{brand} Wrist Watch",
        "{brand} Phone Case",
        "{brand} Backpack",
    ],
}

BRANDS = [
    "PakTech",
    "Indus",
    "Falcon",
    "Horizon",
    "Nexa",
    "Summit",
    "Apex",
    "Crescent",
    "Royal",
    "Urban",
    "Metro",
    "Prime",
    "Vista",
    "Atlas",
    "Nova",
]

FIRST_NAMES_MALE = [
    "Ahmed", "Ali", "Hassan", "Hussain", "Bilal", "Usman", "Omar", "Hamza",
    "Zain", "Faisal", "Imran", "Shahid", "Tariq", "Kamran", "Asad", "Waqas",
    "Naveed", "Sajid", "Adnan", "Farhan", "Rizwan", "Salman", "Danish", "Junaid",
]

FIRST_NAMES_FEMALE = [
    "Ayesha", "Fatima", "Sara", "Maryam", "Hira", "Sana", "Zara", "Iqra",
    "Mehwish", "Nida", "Rabia", "Saima", "Farah", "Amna", "Laiba", "Mahnoor",
    "Kiran", "Bushra", "Nadia", "Saba", "Amina", "Hina", "Uzma", "Shazia",
]

LAST_NAMES = [
    "Khan", "Ahmed", "Ali", "Hussain", "Malik", "Sheikh", "Raza", "Butt",
    "Chaudhry", "Qureshi", "Siddiqui", "Hashmi", "Abbasi", "Mirza", "Baig",
    "Shah", "Syed", "Javed", "Iqbal", "Akhtar", "Rashid", "Nawaz", "Rehman",
]

SELLER_PREFIXES = [
    "Al", "Pak", "City", "Royal", "Super", "Mega", "Smart", "Quick",
    "Global", "Prime", "Best", "Top", "Value", "Express", "Digital",
]

SELLER_SUFFIXES = [
    "Traders", "Mart", "Store", "Shop", "Enterprises", "Solutions",
    "Wholesale", "Retail", "Hub", "Depot", "Bazaar", "Outlet",
]

CARRIERS = [
    "TCS", "Leopards", "M&P", "Call Courier", "Trax", "PostEx", "BlueEx",
]

ORDER_STATUSES = ["Pending", "Confirmed", "Shipped", "Delivered", "Cancelled", "Returned"]
# Probability weights for order status (sum ≈ 1)
ORDER_STATUS_WEIGHTS = [0.03, 0.05, 0.08, 0.72, 0.07, 0.05]

PAYMENT_METHODS = [
    "Cash on Delivery",
    "Credit Card",
    "Debit Card",
    "Bank Transfer",
    "Mobile Wallet",
]
PAYMENT_METHOD_WEIGHTS = [0.45, 0.15, 0.12, 0.08, 0.20]

PAYMENT_STATUSES = ["Pending", "Paid", "Failed", "Refunded"]

RETURN_REASONS = [
    "Damaged",
    "Wrong Product",
    "Changed Mind",
    "Product Not as Described",
    "Size Issue",
    "Late Delivery",
    "Other",
]

BUSINESS_TYPES = ["Individual", "SME", "Brand", "Distributor"]
