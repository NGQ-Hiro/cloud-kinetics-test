# Answer 4 — SQL

Using the model from [answer_2.md](answer_2.md): `fact_order_lines`, `fact_payments`, `dim_customer`, `dim_product`, `dim_date`, `dim_payment_method`.

## 1. Total revenue by day

```sql
SELECT d.full_date, SUM(fp.amount) AS revenue
FROM fact_payments fp
JOIN dim_date d ON fp.date_id = d.date_id
WHERE fp.status = 'success'
GROUP BY d.full_date
ORDER BY d.full_date;
```

Revenue only counts orders with a successful payment, so it sums `amount` from `fact_payments` grouped by day — not `fact_order_lines`, to avoid counting pending/failed orders as revenue.

## 2. Top 3 best-selling products each week (by quantity sold)

```sql
SELECT week, product_id, total_qty
FROM (
  SELECT d.week, fo.product_id, SUM(fo.quantity) AS total_qty,
         ROW_NUMBER() OVER (PARTITION BY d.week ORDER BY SUM(fo.quantity) DESC) AS rnk
  FROM fact_order_lines fo
  JOIN dim_date d ON fo.date_id = d.date_id
  GROUP BY d.week, fo.product_id
) ranked
WHERE rnk <= 3
ORDER BY week, total_qty DESC;
```

Sums quantity per product per week from `fact_order_lines` (the only table with per-product detail), then uses `ROW_NUMBER()` to keep the top 3 per week.

## 3. Payment success rate (paid orders / total orders)

```sql
SELECT
  COUNT(*) FILTER (WHERE status = 'success')::FLOAT / COUNT(*) AS success_rate
FROM fact_payments;
```

Success rate = successful payments divided by all payments (success + failed + pending). Assumption: pending counts as "not yet successful" in the denominator — if you want to exclude pending entirely, add `WHERE status IN ('success','failed')`.
