CREATE TABLE dim_payment (
payment_key  INT PRIMARY KEY,
payment_code INT,
payment_desc VARCHAR(50)
);
INSERT INTO dim_payment (payment_key, payment_code, payment_desc)
VALUES
(1, 1, 'Credit Card'),
(2, 2, 'Cash'),
(3, 3, 'No Charge'),
(4, 4, 'Dispute'),
(5, 5, 'Unknown'),
(6, 6, 'Voided Trip');