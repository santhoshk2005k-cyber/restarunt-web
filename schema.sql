-- ============================================================
--  Saffron & Smoke — MySQL Schema
--  Run this once: mysql -u root -p < schema.sql
-- ============================================================

CREATE DATABASE IF NOT EXISTS saffron_smoke CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE saffron_smoke;

-- ----------------------------
--  MENU ITEMS
-- ----------------------------
CREATE TABLE IF NOT EXISTS menu_items (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(120)  NOT NULL,
    chef        VARCHAR(100)  NOT NULL,
    cuisine     VARCHAR(60)   NOT NULL,
    price       DECIMAL(10,2) NOT NULL,
    description TEXT,
    emoji       VARCHAR(10)   DEFAULT '🍽️',
    available   TINYINT(1)    DEFAULT 1,
    created_at  DATETIME      DEFAULT CURRENT_TIMESTAMP
);

-- ----------------------------
--  RESERVATIONS
-- ----------------------------
CREATE TABLE IF NOT EXISTS reservations (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    first_name   VARCHAR(80)  NOT NULL,
    last_name    VARCHAR(80)  NOT NULL,
    phone        VARCHAR(20)  NOT NULL,
    res_date     DATE         NOT NULL,
    res_time     VARCHAR(20)  NOT NULL,
    guests       VARCHAR(10)  NOT NULL,
    table_number INT          NOT NULL,
    note         TEXT,
    status       VARCHAR(20)  DEFAULT 'Confirmed',
    created_at   DATETIME     DEFAULT CURRENT_TIMESTAMP
);

-- ----------------------------
--  ORDERS
-- ----------------------------
CREATE TABLE IF NOT EXISTS orders (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    total      DECIMAL(10,2) NOT NULL,
    status     VARCHAR(20)   DEFAULT 'Pending',
    created_at DATETIME      DEFAULT CURRENT_TIMESTAMP
);

-- ----------------------------
--  ORDER ITEMS  (linked to orders)
-- ----------------------------
CREATE TABLE IF NOT EXISTS order_items (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    order_id    INT           NOT NULL,
    item_name   VARCHAR(120)  NOT NULL,
    chef        VARCHAR(100),
    cuisine     VARCHAR(60),
    emoji       VARCHAR(10),
    price       DECIMAL(10,2) NOT NULL,
    quantity    INT           NOT NULL DEFAULT 1,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE
);
