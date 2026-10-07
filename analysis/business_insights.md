# Business Insights — Pakistan E-commerce Analytics Platform

> Generated from the **analytics** schema in PostgreSQL. Figures reflect **synthetic** marketplace data, not a real company.

_Generated at: 2026-10-07T07:48:06.698944+00:00_

## Executive snapshot

- **Total orders:** 300,000
- **Customers with orders:** 59,807
- **Gross revenue:** PKR 121,793,639,155.27
- **Net revenue:** PKR 113,376,438,051.32
- **Average order value (AOV):** PKR 387,810.60
- **Cancellation rate:** 7.09%
- **Return-related order rate:** 10.00%

## 1. Which cities contribute most to revenue?

| city       | province                    |     revenue |   orders |   return_rate |   avg_delivery_days |
|:-----------|:----------------------------|------------:|---------:|--------------:|--------------------:|
| Karachi    | Sindh                       | 3.58353e+10 |    87802 |     0.100909  |             6.98302 |
| Lahore     | Punjab                      | 2.89645e+10 |    71409 |     0.098391  |             7.00231 |
| Faisalabad | Punjab                      | 7.82402e+09 |    19188 |     0.0977694 |             6.99614 |
| Rawalpindi | Punjab                      | 5.67803e+09 |    14042 |     0.102122  |             7.02117 |
| Multan     | Punjab                      | 4.76884e+09 |    11825 |     0.100211  |             7.04011 |
| Gujranwala | Punjab                      | 4.62175e+09 |    11352 |     0.10333   |             7.02952 |
| Peshawar   | Khyber Pakhtunkhwa          | 4.35719e+09 |    10822 |     0.0985955 |             7.02188 |
| Islamabad  | Islamabad Capital Territory | 4.11235e+09 |    10297 |     0.0992522 |             7.0138  |
| Hyderabad  | Sindh                       | 3.8442e+09  |     9444 |     0.102605  |             6.96922 |
| Quetta     | Balochistan                 | 2.64056e+09 |     6526 |     0.101594  |             7.01953 |

## 2. Which categories have high revenue and elevated return rates?

| category_name          |     revenue |   return_rate |   units_sold |
|:-----------------------|------------:|--------------:|-------------:|
| Mobile Phones          | 5.67569e+10 |     0.0307759 |       336511 |
| Computers & Laptops    | 2.91654e+10 |     0.0324819 |       175077 |
| Furniture              | 1.10624e+10 |     0.0320651 |       120247 |
| Home Appliances        | 1.06558e+10 |     0.0322083 |       179323 |
| Electronics            | 6.77758e+09 |     0.0313243 |       132969 |
| Fashion                | 1.82547e+09 |     0.0311741 |       279645 |
| Home & Kitchen         | 1.37445e+09 |     0.0307581 |       167839 |
| Sports                 | 1.1248e+09  |     0.0311681 |       108772 |
| Automotive             | 1.08233e+09 |     0.0296274 |        83026 |
| Health & Personal Care | 4.91477e+08 |     0.0305812 |       113540 |
| Beauty                 | 4.63426e+08 |     0.0305801 |       144763 |
| Accessories            | 4.01717e+08 |     0.0322337 |        73527 |
| Toys                   | 2.62438e+08 |     0.0331182 |        64412 |
| Grocery                | 2.19767e+08 |     0.0313072 |       205560 |
| Books                  | 1.29626e+08 |     0.0318949 |        66936 |

## 3. Which sellers have high sales (fulfillment risk signals)?

Top sellers by revenue with return/cancellation rates (synthetic):

| seller_name            |   seller_revenue |   seller_return_rate |   seller_cancellation_rate | seller_tier   |
|:-----------------------|-----------------:|---------------------:|---------------------------:|:--------------|
| Value Hub 616          |      5.61944e+08 |            0.0293675 |                  0.0722892 | Gold          |
| Mega Mart 99           |      5.58e+08    |            0.031695  |                  0.0744143 | Gold          |
| Al Depot 185           |      5.42074e+08 |            0.0373178 |                  0.0798834 | Gold          |
| Mega Solutions 27      |      5.17489e+08 |            0.0332023 |                  0.0698995 | Gold          |
| Quick Enterprises 499  |      4.8896e+08  |            0.0282443 |                  0.0641221 | Gold          |
| Mega Solutions 856     |      4.63942e+08 |            0.0296767 |                  0.0699523 | Gold          |
| Mega Retail 929        |      4.45352e+08 |            0.0316921 |                  0.0667799 | Gold          |
| Al Mart 409            |      4.39036e+08 |            0.0283109 |                  0.071977  | Gold          |
| Global Enterprises 515 |      4.29969e+08 |            0.0276959 |                  0.0636417 | Gold          |
| Global Mart 339        |      4.26777e+08 |            0.033419  |                  0.0634105 | Gold          |
| Super Retail 578       |      4.26314e+08 |            0.0412518 |                  0.0744429 | Gold          |
| Quick Outlet 340       |      4.26016e+08 |            0.0331575 |                  0.0670686 | Gold          |
| Mega Outlet 850        |      4.20737e+08 |            0.0298507 |                  0.0746269 | Gold          |
| City Shop 615          |      4.20156e+08 |            0.0357143 |                  0.070911  | Gold          |
| Digital Retail 559     |      3.98457e+08 |            0.0375276 |                  0.0706402 | Gold          |

## 4. What is the monthly growth trend?

|   year |   month |   net_revenue |   orders |   net_revenue_growth_pct |
|-------:|--------:|--------------:|---------:|-------------------------:|
|   2023 |       1 |   7.88368e+07 |      223 |              nan         |
|   2023 |       2 |   2.2356e+08  |      582 |              183.573     |
|   2023 |       3 |   4.78415e+08 |     1227 |              113.999     |
|   2023 |       4 |   7.04438e+08 |     1817 |               47.244     |
|   2023 |       5 |   9.75561e+08 |     2582 |               38.4878    |
|   2023 |       6 |   1.11907e+09 |     3008 |               14.7105    |
|   2023 |       7 |   1.53049e+09 |     3873 |               36.764     |
|   2023 |       8 |   1.66706e+09 |     4391 |                8.92373   |
|   2023 |       9 |   1.83181e+09 |     4996 |                9.88263   |
|   2023 |      10 |   2.10041e+09 |     5749 |               14.6629    |
|   2023 |      11 |   2.32967e+09 |     6113 |               10.915     |
|   2023 |      12 |   2.64514e+09 |     6951 |               13.5415    |
|   2024 |       1 |   2.90547e+09 |     7521 |                9.84176   |
|   2024 |       2 |   2.91524e+09 |     7775 |                0.336547  |
|   2024 |       3 |   3.37218e+09 |     8879 |               15.674     |
|   2024 |       4 |   3.45924e+09 |     9184 |                2.58157   |
|   2024 |       5 |   3.65995e+09 |     9834 |                5.80234   |
|   2024 |       6 |   3.75839e+09 |     9998 |                2.68961   |
|   2024 |       7 |   4.15105e+09 |    10940 |               10.4476    |
|   2024 |       8 |   4.2839e+09  |    11281 |                3.20037   |
|   2024 |       9 |   4.3762e+09  |    11380 |                2.15453   |
|   2024 |      10 |   4.51768e+09 |    12017 |                3.23298   |
|   2024 |      11 |   4.53237e+09 |    12027 |                0.325204  |
|   2024 |      12 |   4.856e+09   |    12748 |                7.14031   |
|   2025 |       1 |   4.87479e+09 |    12911 |                0.386889  |
|   2025 |       2 |   4.50691e+09 |    11941 |               -7.54657   |
|   2025 |       3 |   4.90497e+09 |    12887 |                8.83232   |
|   2025 |       4 |   4.90979e+09 |    12896 |                0.0983383 |
|   2025 |       5 |   4.92052e+09 |    13118 |                0.218546  |
|   2025 |       6 |   4.66989e+09 |    12375 |               -5.09366   |
|   2025 |       7 |   4.56794e+09 |    12419 |               -2.18303   |
|   2025 |       8 |   4.5769e+09  |    11951 |                0.196023  |
|   2025 |       9 |   4.06263e+09 |    10717 |              -11.2362    |
|   2025 |      10 |   3.77084e+09 |    10106 |               -7.1823    |
|   2025 |      11 |   3.16793e+09 |     8330 |              -15.9888    |
|   2025 |      12 |   1.97121e+09 |     5253 |              -37.776     |

## 5. What percentage of customers are repeat customers?

- **Repeat customer rate:** 63.94%
- **Spend from repeat customers:** PKR 107,958,454,839.89 of PKR 116,343,178,860.04

## 6. Which payment methods dominate?

| payment_method   |   transactions |   success_rate |      amount |
|:-----------------|---------------:|---------------:|------------:|
| Cash on Delivery |         134994 |       0.698913 | 5.24423e+10 |
| Mobile Wallet    |          59980 |       0.823791 | 2.31779e+10 |
| Credit Card      |          45076 |       0.824297 | 1.73794e+10 |
| Debit Card       |          36002 |       0.823732 | 1.39224e+10 |
| Bank Transfer    |          23948 |       0.82391  | 9.42114e+09 |

## 7. Which cities have delivery problems?

Highest average delivery days:

| city         |   avg_delivery_days |   on_time_delivery_rate |   orders |
|:-------------|--------------------:|------------------------:|---------:|
| Muzaffarabad |             7.10811 |                0.278658 |     1396 |
| Sukkur       |             7.10482 |                0.270499 |     3069 |
| Larkana      |             7.10266 |                0.26859  |     2351 |
| Wah Cantt    |             7.09709 |                0.264278 |     2495 |
| Sargodha     |             7.04292 |                0.271309 |     4351 |
| Multan       |             7.04011 |                0.277055 |    11825 |
| Sheikhupura  |             7.03535 |                0.279813 |     3114 |
| Gujrat       |             7.03239 |                0.276923 |     3213 |
| Gwadar       |             7.03066 |                0.274453 |      883 |
| Gujranwala   |             7.02952 |                0.276029 |    11352 |

## 8. Which customer segments contribute most revenue?

| customer_segment   |   customers |       spend |
|:-------------------|------------:|------------:|
| High Value         |       11962 | 8.20687e+10 |
| Inactive           |       47845 | 3.42745e+10 |

## 9. Which products have high sales and high return rates?

| product_name              | category_name       |          revenue |   return_rate |   units_sold |
|:--------------------------|:--------------------|-----------------:|--------------:|-------------:|
| Summit Doll House         | Toys                | 798998           |     0.0853659 |          395 |
| Royal Educational Puzzle  | Toys                |      1.74773e+06 |     0.0851064 |          436 |
| Atlas Urdu Novel Vol 85   | Books               |      1.87949e+06 |     0.0846561 |          439 |
| Atlas Cooking Oil 93L     | Grocery             |  61517.9         |     0.0828729 |          467 |
| Indus Spices Pack         | Grocery             |      2.50499e+06 |     0.0821256 |          516 |
| Horizon Office Chair      | Furniture           |      1.15955e+07 |     0.08      |          425 |
| Falcon Electric Kettle    | Home & Kitchen      | 206420           |     0.0769231 |          428 |
| Metro LED Monitor 65 inch | Electronics         |      2.41662e+06 |     0.076087  |          438 |
| Urban Gaming Laptop 12    | Computers & Laptops |      6.79474e+07 |     0.0756757 |          427 |
| Prime Gaming Laptop 79    | Computers & Laptops |      3.56872e+07 |     0.0748663 |          467 |
| Falcon Cookbook           | Books               | 281570           |     0.0747126 |          441 |
| Crescent Skincare Kit     | Beauty              | 691777           |     0.0744681 |          455 |
| Indus Spices Pack         | Grocery             | 178782           |     0.0742857 |          404 |
| Atlas Microwave Oven      | Home Appliances     |      6.74582e+06 |     0.0742574 |          478 |
| Vista Cooking Oil 51L     | Grocery             | 110151           |     0.0740741 |          493 |

## 10. Operational patterns observed

- Payment mix is dominated by methods with the highest transaction counts in the table above (expected Cash on Delivery weight in a Pakistani marketplace simulation).
- Revenue concentrates in a small set of large cities — see city ranking.
- Category return rates vary; categories with both high revenue and higher return rates are priority quality-review candidates.
- Seller tiers (`Platinum`/`Gold`/`Silver`/`Bronze`) encode documented revenue and quality thresholds in `config/settings.yaml` — not universal industry standards.

## Methodology notes

- **Gross revenue** = sum of `quantity * unit_price` at order-item grain.
- **Net revenue** = gross − item discounts − refunds (order-level aggregation in `int_order_metrics`).
- **CLV** in this project is historical net revenue per customer (not a predictive LTV model).
