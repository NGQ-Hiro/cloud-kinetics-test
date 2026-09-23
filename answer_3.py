import pandas as pd

DATA_PATH = "./data/orders_sample.csv"

# 1. Load
df = pd.read_csv(DATA_PATH)

# 2. Remove exact duplicate rows
df = df.drop_duplicates()

# 3. Remove rows missing quantity or unit_price
df = df.dropna(subset=["quantity", "unit_price"])

# 4. line_revenue
df["line_revenue"] = df["quantity"] * df["unit_price"]

# 5a. Total revenue by day
revenue_by_day = df.groupby("order_date")["line_revenue"].sum()

# 5b. Orders per customer (unique orders, not line items)
orders_per_customer = df.drop_duplicates("order_id").groupby("customer_id")["order_id"].count()

# 5c. Payment success rate (paid orders / total orders, at order level)
orders_status = df.drop_duplicates("order_id")[["order_id", "payment_status"]]
success_rate = (orders_status["payment_status"] == "paid").mean()

# 6. Print
print("Revenue by day:\n", revenue_by_day, "\n")
print("Orders per customer:\n", orders_per_customer, "\n")
print(f"Payment success rate: {success_rate:.2%}")
