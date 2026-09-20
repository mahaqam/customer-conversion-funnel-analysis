-- PostgreSQL-style funnel queries for Retailrocket events.csv.
-- Load the CSV into a table named retailrocket_events with columns:
-- timestamp BIGINT, visitorid BIGINT, event TEXT, itemid BIGINT, transactionid BIGINT NULL.

WITH first_events AS (
  SELECT
    visitorid,
    MIN(CASE WHEN event = 'view' THEN timestamp END) AS first_view,
    MIN(CASE WHEN event = 'addtocart' THEN timestamp END) AS first_cart,
    MIN(CASE WHEN event = 'transaction' THEN timestamp END) AS first_transaction
  FROM retailrocket_events
  GROUP BY visitorid
), sequential_funnel AS (
  SELECT
    visitorid,
    first_view IS NOT NULL AS viewed,
    first_cart IS NOT NULL
      AND first_view IS NOT NULL
      AND first_cart >= first_view AS carted_after_view,
    first_transaction IS NOT NULL
      AND first_cart IS NOT NULL
      AND first_view IS NOT NULL
      AND first_cart >= first_view
      AND first_transaction >= first_cart AS transacted_after_cart
  FROM first_events
)
SELECT
  COUNT(*) FILTER (WHERE viewed) AS viewers,
  COUNT(*) FILTER (WHERE carted_after_view) AS cart_users,
  COUNT(*) FILTER (WHERE transacted_after_cart) AS purchasers,
  ROUND(100.0 * COUNT(*) FILTER (WHERE carted_after_view)
    / NULLIF(COUNT(*) FILTER (WHERE viewed), 0), 3) AS view_to_cart_pct,
  ROUND(100.0 * COUNT(*) FILTER (WHERE transacted_after_cart)
    / NULLIF(COUNT(*) FILTER (WHERE carted_after_view), 0), 3) AS cart_to_transaction_pct,
  ROUND(100.0 * COUNT(*) FILTER (WHERE transacted_after_cart)
    / NULLIF(COUNT(*) FILTER (WHERE viewed), 0), 3) AS view_to_transaction_pct
FROM sequential_funnel;

-- Item-level view-to-transaction conversion.
SELECT
  itemid,
  COUNT(DISTINCT CASE WHEN event = 'view' THEN visitorid END) AS viewers,
  COUNT(DISTINCT CASE WHEN event = 'transaction' THEN visitorid END) AS purchasers,
  ROUND(
    100.0 * COUNT(DISTINCT CASE WHEN event = 'transaction' THEN visitorid END)
    / NULLIF(COUNT(DISTINCT CASE WHEN event = 'view' THEN visitorid END), 0),
    3
  ) AS view_to_transaction_pct
FROM retailrocket_events
GROUP BY itemid
HAVING COUNT(DISTINCT CASE WHEN event = 'view' THEN visitorid END) >= 100
ORDER BY view_to_transaction_pct DESC, viewers DESC;
