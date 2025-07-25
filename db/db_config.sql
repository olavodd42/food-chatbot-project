CREATE TABLE `food_items` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `price` decimal(6,2) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_UNIQUE` (`id`),
  UNIQUE KEY `name_UNIQUE` (`name`)
);

CREATE TABLE orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    food_id INT NOT NULL,
    quantity INT NOT NULL,
    total_price DECIMAL(8,2) NOT NULL,
    FOREIGN KEY (food_id) REFERENCES food_items(id)
);
CREATE TABLE order_tracking (
    order_id INT PRIMARY KEY,
    status VARCHAR(50) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE
);


INSERT INTO food_items (name, price) VALUES
('Cheeseburger', 8.99),
('Bacon Burger', 9.49),
('Double Burger', 10.99),
('Veggie Burger', 8.49),
('Fries', 3.99),
('Curly Fries', 4.49),
('Chicken Nuggets', 5.99),
('Hot Dog', 4.99),
('Chili Dog', 5.49),
('Grilled Cheese', 4.99),
('Mac and Cheese', 6.99),
('Chicken Wings', 9.99),
('Onion Rings', 4.99),
('Fried Chicken', 10.99),
('BBQ Ribs', 14.99),
('Tacos', 3.49),
('Burrito', 8.99),
('Nachos', 7.99),
('Cheese Pizza', 9.99),
('Pepperoni Pizza', 10.99),
('Hawaiian Pizza', 11.49),
('Supreme Pizza', 12.99),
('Milkshake', 5.49),
('Vanilla Milkshake', 5.49),
('Chocolate Milkshake', 5.49),
('Soda', 1.99),
('Iced Tea', 2.49),
('Coffee', 2.99),
('Apple Pie', 3.99),
('Brownie', 3.49),
('Ice Cream', 4.49),
('Acai Bowl', 7.99);

INSERT INTO orders (food_id, quantity, total_price)
SELECT id, 2, 2 * price FROM food_items WHERE name = 'Cheeseburger';

INSERT INTO order_tracking (order_id, status)
VALUES (1, 'In transit');

SELECT * FROM food_items;

SELECT o.id AS order_id, c.name AS food, o.quantity, o.total_price
FROM orders o
JOIN food_items c ON o.food_id = c.id;

SELECT status FROM order_tracking
WHERE order_id = 1;