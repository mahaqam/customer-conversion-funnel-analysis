-- PostgreSQL-style funnel queries. Load the source CSV into ecommerce_events.
WITH user_stages AS (
 SELECT user_id,
 MAX(CASE WHEN event_type='view' THEN 1 ELSE 0 END) viewed,
 MAX(CASE WHEN event_type='cart' THEN 1 ELSE 0 END) carted,
 MAX(CASE WHEN event_type='purchase' THEN 1 ELSE 0 END) purchased
 FROM ecommerce_events GROUP BY user_id
)
SELECT COUNT(*) FILTER (WHERE viewed=1) viewers,
 COUNT(*) FILTER (WHERE carted=1) cart_users,
 COUNT(*) FILTER (WHERE purchased=1) purchasers,
 ROUND(100.0*COUNT(*) FILTER (WHERE carted=1)/NULLIF(COUNT(*) FILTER (WHERE viewed=1),0),2) view_to_cart_pct,
 ROUND(100.0*COUNT(*) FILTER (WHERE purchased=1)/NULLIF(COUNT(*) FILTER (WHERE viewed=1),0),2) view_to_purchase_pct
FROM user_stages;

SELECT category_code,
 COUNT(DISTINCT CASE WHEN event_type='view' THEN user_id END) viewers,
 COUNT(DISTINCT CASE WHEN event_type='purchase' THEN user_id END) purchasers,
 ROUND(100.0*COUNT(DISTINCT CASE WHEN event_type='purchase' THEN user_id END)/
 NULLIF(COUNT(DISTINCT CASE WHEN event_type='view' THEN user_id END),0),2) conversion_pct
FROM ecommerce_events WHERE category_code IS NOT NULL
GROUP BY category_code
HAVING COUNT(DISTINCT CASE WHEN event_type='view' THEN user_id END)>=100
ORDER BY conversion_pct DESC;
