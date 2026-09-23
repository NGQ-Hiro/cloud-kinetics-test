# Answer 2 — Data Modeling

## Question

You are designing a simple analytics data model for an online store. The business wants to answer these questions:

- What is total revenue by day?
- What are the top-selling products each week?
- How many orders does each customer place?
- What is the payment success rate?

**Available business objects:**

- customers
- products
- orders
- payments

**Please answer in this format:**

1. What tables would you create?
2. What would be the grain of your main fact table?
3. Why would you include or not include an order_items table?
4. What problems would happen if product information were stored directly inside the orders table?

## Answer

### 1. Tables

```
dim_customer
  customer_id (PK)
  full_name
  email
  signup_date
  segment / tier          -- optional, if business tracks it

dim_product
  product_id (PK)
  product_name
  category
  unit_price

dim_date
  date_id (PK)
  full_date
  day
  week
  month
  quarter
  year
  day_of_week
  is_weekend

dim_payment_method
  payment_method_id (PK)
  method_name              -- card, bank_transfer, wallet, cash_on_delivery, ...
  provider                 -- optional, e.g. Stripe/PayPal

fact_order_lines
  order_line_id (PK)       -- surrogate key = hash/concat(order_id, product_id)
  order_id                 -- degenerate dim, groups lines of the same order
  customer_id  FK -> dim_customer
  product_id   FK -> dim_product
  date_id      FK -> dim_date       -- order date
  quantity
  unit_price                        -- price at time of sale (snapshot, not from dim_product)
  line_amount                       -- quantity * unit_price

fact_payments
  payment_id (PK)
  order_id                  -- degenerate dim, same order_id, no FK to fact_order_lines
  customer_id    FK -> dim_customer
  payment_method_id FK -> dim_payment_method
  date_id        FK -> dim_date     -- payment date
  amount                    -- order total charged
  status                    -- pending / success / failed
  status_updated_at
```

Payment gets its own fact table because it has its own lifecycle (pending → success/failed, status changes over time, potentially multiple attempts) — it isn't a fixed 1:1 attribute of an order the way a dimension should be.

`order_id` is kept as a plain (degenerate) column in both facts rather than a FK from one fact to the other, since `fact_order_lines` and `fact_payments` have different grains (order line vs. payment) and a fact should never join to another fact directly. Both facts instead share the same conformed dimensions (`dim_customer`, `dim_date`) directly.

A separate `dim_order` table isn't needed unless orders gain their own attributes beyond customer + date (e.g. order channel, shipping address) — until then it would be an unused abstraction.

### 2. Grain of the main fact table (`fact_order_lines`)

One row per order line = one product within one order:

```
order_id | line_id | product_id | quantity | unit_price | line_amount
1001     | 1       | A          | 2        | 15         | 30
1001     | 2       | B          | 1        | 20         | 20
```

This is the smallest useful grain: an order can contain many products each with its own quantity, so order-level grain would lose per-product detail (breaking "top-selling products"). There's no finer grain available in the source data.

How each business question maps to this design:

| Question | Query shape |
|---|---|
| Revenue by day | `SUM(line_amount)` from `fact_order_lines` joined to `dim_date`, grouped by day |
| Top products/week | `SUM(quantity)` grouped by week + `product_id`, ordered desc |
| Orders per customer | `COUNT(DISTINCT order_id)` from `fact_order_lines` grouped by `customer_id` |
| Payment success rate | `COUNT(status='success') / COUNT(*)` from `fact_payments` |

### 3. Why include an order_items table (here, `fact_order_lines`)

Because 1 order can contain many products, each with its own quantity. Without it, an order-grain fact would need to cram a list of (product, quantity) pairs into one row, which SQL can't aggregate cleanly (can't sum quantity per product, can't filter by product). Splitting into one row per order line makes both order-level and product-level aggregation trivial.

### 4. Problems with storing product info directly inside the orders table

- Denormalization/duplication: product name, price, etc. repeated on every order row — wastes space and risks inconsistency if a product's details change.
- Update anomalies: renaming a product means updating every historical order row instead of one row in `dim_product`.
- Loses history: if price is only stored on the product (not the order line), you can't tell what the customer actually paid at purchase time — the fact table needs its own `unit_price`/`line_amount` snapshot at the time of sale.
- Can't represent multiple products per order without repeating columns (product_1, qty_1, product_2, qty_2, ...) or JSON blobs — neither aggregates well in SQL.
