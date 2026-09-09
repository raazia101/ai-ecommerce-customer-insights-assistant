import csv
import json
import random
from datetime import datetime, timedelta
from pathlib import Path

# Reproducible dataset
random.seed(42)

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)

# --------------------------------------------------
# Configuration
# --------------------------------------------------

NUM_CUSTOMERS = 100
NUM_PRODUCTS = 50
NUM_ORDERS = 500
NUM_TRANSACTIONS = 500
NUM_EVENTS = 1000

START_DATE = datetime(2025, 1, 1)


def random_date(start=START_DATE, days=600):
    return start + timedelta(
        days=random.randint(0, days),
        hours=random.randint(0, 23),
        minutes=random.randint(0, 59),
    )


def write_csv(filename, rows, fieldnames):
    path = RAW_DIR / filename

    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Created {path} ({len(rows)} rows)")


# --------------------------------------------------
# Customers
# --------------------------------------------------

customers = []

first_names = [
    "Aarav", "Maya", "Noah", "Sophia", "Liam",
    "Emma", "Ethan", "Olivia", "Arjun", "Zara",
    "Daniel", "Aisha", "Ryan", "Mia", "Adam"
]

last_names = [
    "Smith", "Patel", "Khan", "Johnson", "Brown",
    "Williams", "Taylor", "Anderson", "Thomas", "Martin"
]

countries = ["UAE", "India", "USA", "UK", "Canada"]

for i in range(1, NUM_CUSTOMERS + 1):
    first = random.choice(first_names)
    last = random.choice(last_names)

    customers.append({
        "customer_id": f"CUST-{i:04d}",
        "first_name": first,
        "last_name": last,
        "email": f"{first.lower()}.{last.lower()}{i}@example.com",
        "country": random.choice(countries),
        "signup_date": random_date().date().isoformat(),
        "status": random.choice(["active", "active", "active", "inactive"]),
    })

write_csv(
    "customers.csv",
    customers,
    [
        "customer_id",
        "first_name",
        "last_name",
        "email",
        "country",
        "signup_date",
        "status",
    ],
)


# --------------------------------------------------
# Products
# --------------------------------------------------

product_names = [
    "Wireless Headphones",
    "Mechanical Keyboard",
    "USB-C Hub",
    "Laptop Stand",
    "Wireless Mouse",
    "Smart Watch",
    "Portable SSD",
    "Webcam",
    "Bluetooth Speaker",
    "Power Bank",
    "Phone Stand",
    "Monitor Arm",
    "Desk Lamp",
    "USB Microphone",
    "Tablet Stand",
]

categories = [
    "Electronics",
    "Computer Accessories",
    "Mobile Accessories",
    "Office",
]

products = []

for i in range(1, NUM_PRODUCTS + 1):
    products.append({
        "product_id": f"PROD-{i:04d}",
        "product_name": f"{random.choice(product_names)} {i}",
        "category": random.choice(categories),
        "price": round(random.uniform(15, 500), 2),
        "stock_quantity": random.randint(0, 250),
        "status": random.choice(["active", "active", "active", "discontinued"]),
    })

write_csv(
    "products.csv",
    products,
    [
        "product_id",
        "product_name",
        "category",
        "price",
        "stock_quantity",
        "status",
    ],
)


# --------------------------------------------------
# Orders and Order Items
# --------------------------------------------------

orders = []
order_items = []

order_statuses = [
    "pending",
    "confirmed",
    "shipped",
    "delivered",
    "cancelled",
]

for i in range(1, NUM_ORDERS + 1):
    order_id = f"ORD-{i:05d}"
    customer = random.choice(customers)
    order_date = random_date()

    orders.append({
        "order_id": order_id,
        "customer_id": customer["customer_id"],
        "order_date": order_date.isoformat(),
        "status": random.choice(order_statuses),
        "currency": "AED",
    })

    number_of_items = random.randint(1, 5)
    selected_products = random.sample(products, number_of_items)

    for line_number, product in enumerate(selected_products, start=1):
        quantity = random.randint(1, 3)

        order_items.append({
            "order_item_id": f"ITEM-{i:05d}-{line_number:02d}",
            "order_id": order_id,
            "product_id": product["product_id"],
            "quantity": quantity,
            "unit_price": product["price"],
        })

write_csv(
    "orders.csv",
    orders,
    [
        "order_id",
        "customer_id",
        "order_date",
        "status",
        "currency",
    ],
)

write_csv(
    "order_items.csv",
    order_items,
    [
        "order_item_id",
        "order_id",
        "product_id",
        "quantity",
        "unit_price",
    ],
)


# --------------------------------------------------
# Transactions
# --------------------------------------------------

transactions = []

payment_methods = [
    "card",
    "bank_transfer",
    "wallet",
]

transaction_statuses = [
    "completed",
    "completed",
    "completed",
    "failed",
    "refunded",
]

for i, order in enumerate(orders, start=1):
    items = [
        item
        for item in order_items
        if item["order_id"] == order["order_id"]
    ]

    amount = sum(
        item["quantity"] * item["unit_price"]
        for item in items
    )

    transactions.append({
        "transaction_id": f"TXN-{i:05d}",
        "order_id": order["order_id"],
        "customer_id": order["customer_id"],
        "amount": round(amount, 2),
        "currency": "AED",
        "payment_method": random.choice(payment_methods),
        "status": random.choice(transaction_statuses),
        "transaction_date": order["order_date"],
    })

write_csv(
    "transactions.csv",
    transactions,
    [
        "transaction_id",
        "order_id",
        "customer_id",
        "amount",
        "currency",
        "payment_method",
        "status",
        "transaction_date",
    ],
)


# --------------------------------------------------
# Events
# --------------------------------------------------

event_types = [
    "page_view",
    "product_view",
    "search",
    "add_to_cart",
    "remove_from_cart",
    "checkout_started",
    "purchase",
    "login",
    "logout",
]

events = []

for i in range(1, NUM_EVENTS + 1):
    customer = random.choice(customers)

    event_type = random.choice(event_types)

    event = {
        "event_id": f"EVT-{i:06d}",
        "customer_id": customer["customer_id"],
        "event_type": event_type,
        "timestamp": random_date().isoformat(),
        "source": random.choice([
            "web",
            "mobile",
            "api",
        ]),
    }

    if event_type in ["product_view", "add_to_cart", "remove_from_cart"]:
        event["product_id"] = random.choice(products)["product_id"]

    if event_type == "purchase":
        event["order_id"] = random.choice(orders)["order_id"]

    events.append(event)

with (RAW_DIR / "events.json").open(
    "w",
    encoding="utf-8"
) as file:
    json.dump(events, file, indent=2)

print(f"Created {RAW_DIR / 'events.json'} ({len(events)} events)")


# --------------------------------------------------
# FAQ documents
# --------------------------------------------------

faq_documents = [
    {
        "document_id": "FAQ-001",
        "type": "faq",
        "title": "How can I track my order?",
        "content": (
            "Customers can track their order from the Orders section "
            "of their account. Once an order has shipped, the tracking "
            "number will be displayed."
        ),
        "tags": ["orders", "shipping", "tracking"],
    },
    {
        "document_id": "FAQ-002",
        "type": "faq",
        "title": "What is the return period?",
        "content": (
            "Eligible products can be returned within 30 days of "
            "delivery, provided they meet the applicable return "
            "conditions."
        ),
        "tags": ["returns", "refunds"],
    },
    {
        "document_id": "FAQ-003",
        "type": "faq",
        "title": "How long do refunds take?",
        "content": (
            "Approved refunds are normally processed within 5 to 10 "
            "business days depending on the payment provider."
        ),
        "tags": ["refunds", "payments"],
    },
    {
        "document_id": "FAQ-004",
        "type": "faq",
        "title": "How can I contact customer support?",
        "content": (
            "Customers can contact support through the support portal "
            "or the contact options provided in their account."
        ),
        "tags": ["support", "contact"],
    },
    {
        "document_id": "FAQ-005",
        "type": "faq",
        "title": "Can I cancel an order?",
        "content": (
            "Orders can be cancelled while they are still in a "
            "cancellable processing state. Orders that have already "
            "shipped may need to follow the return process."
        ),
        "tags": ["orders", "cancellation"],
    },
]


# --------------------------------------------------
# Promotion and Policy documents
# --------------------------------------------------

policy_documents = [
    {
        "document_id": "POLICY-001",
        "type": "promotion_policy",
        "title": "New Customer Promotion",
        "content": (
            "New customers may receive a 10 percent discount on their "
            "first eligible purchase. The promotion cannot be combined "
            "with certain other promotional offers."
        ),
        "tags": ["promotion", "new customer", "discount"],
    },
    {
        "document_id": "POLICY-002",
        "type": "promotion_policy",
        "title": "Seasonal Promotion",
        "content": (
            "Selected products may be discounted during seasonal "
            "promotional periods. Product eligibility and discount "
            "levels may vary."
        ),
        "tags": ["promotion", "seasonal", "discount"],
    },
    {
        "document_id": "POLICY-003",
        "type": "return_policy",
        "title": "Standard Return Policy",
        "content": (
            "Products must satisfy the applicable return conditions "
            "and normally must be returned within 30 days of delivery."
        ),
        "tags": ["returns", "policy"],
    },
]


documents = faq_documents + policy_documents

with (RAW_DIR / "documents.json").open(
    "w",
    encoding="utf-8"
) as file:
    json.dump(documents, file, indent=2)

print(
    f"Created {RAW_DIR / 'documents.json'} "
    f"({len(documents)} documents)"
)

print("\nStarter data generation complete.")