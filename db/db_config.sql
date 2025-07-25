-- Drop existing tables to start clean
DROP TABLE IF EXISTS order_tracking;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS order_header;
DROP TABLE IF EXISTS food_items;

-- 1) Tabela de itens de comida
CREATE TABLE food_items (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100) NOT NULL UNIQUE,
  price DECIMAL(6,2) NOT NULL
);

-- 2) Tabela de cabeçalho de pedidos
CREATE TABLE order_header (
  id INT AUTO_INCREMENT PRIMARY KEY,
  session_id VARCHAR(200),
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 3) Tabela de itens do pedido, referenciando header
CREATE TABLE orders (
  id INT AUTO_INCREMENT PRIMARY KEY,
  header_id INT NOT NULL,
  food_id INT NOT NULL,
  quantity INT NOT NULL,
  total_price DECIMAL(8,2) NOT NULL,
  FOREIGN KEY (header_id) REFERENCES order_header(id) ON DELETE CASCADE,
  FOREIGN KEY (food_id) REFERENCES food_items(id)
);

-- 4) Tabela de rastreamento de pedidos, referenciando header
CREATE TABLE order_tracking (
  order_id INT PRIMARY KEY,
  status VARCHAR(50) NOT NULL,
  FOREIGN KEY (order_id) REFERENCES order_header(id) ON DELETE CASCADE
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
('Pizza', 9.99),
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

SELECT 
  oh.id   AS pedido_id,
  oh.session_id,
  fi.name AS item,
  o.quantity AS quantidade,
  o.total_price AS total
FROM order_header AS oh
JOIN orders AS o 
  ON o.header_id = oh.id
JOIN food_items AS fi 
  ON fi.id = o.food_id
ORDER BY oh.id DESC;