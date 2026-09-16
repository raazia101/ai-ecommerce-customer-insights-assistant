from pymongo import MongoClient

MONGO_URI = "mongodb://localhost:27017/"
MONGO_DB = "intern_db"


def main():
    client = MongoClient(MONGO_URI)

    # Verify connection
    client.admin.command("ping")
    print("MongoDB connection successful.")

    db = client[MONGO_DB]

    customers = db["customers"]

    print("Customer collection connected.")

    # READ: Find one customer
    customer = customers.find_one(
        {"customer_id": "CUST-0001"}
    )

    print("Customer found:")
    print(customer)

    # CREATE: Insert a practice customer
    practice_customer = {
        "customer_id": "CUST-TEST-001",
        "first_name": "Test",
        "last_name": "Customer",
        "email": "test.customer@example.com",
        "country": "UAE",
        "signup_date": "2026-09-14",
        "status": "active",
    }

    result = customers.insert_one(practice_customer)

    print("Inserted customer ID:")
    print(result.inserted_id)

    # UPDATE: Change the practice customer's status
    update_result = customers.update_one(
        {"customer_id": "CUST-TEST-001"},
        {"$set": {"status": "inactive"}}
    )

    print("Documents updated:")
    print(update_result.modified_count)
    # DELETE: Remove the practice customer
    delete_result = customers.delete_one(
    {"customer_id": "CUST-TEST-001"}
)

    print("Documents deleted:")
    print(delete_result.deleted_count)

    client.close()


if __name__ == "__main__":
    main()