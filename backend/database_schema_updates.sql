-- FILE: database_schema_updates.sql
-- This file outlines the necessary SQL changes to support the detailed product hierarchy.
-- We are moving from a single 'products' table to a more granular structure.

-- 1. Create a table for the highest-level categories.
CREATE TABLE `categories` (
    `id` INT NOT NULL AUTO_INCREMENT,
    `name` VARCHAR(255) NOT NULL,
    `description` TEXT,
    `deleted_at` TIMESTAMP NULL,
    PRIMARY KEY (`id`)
);

-- 2. Create the main products table. A 'Product' is a conceptual item.
--    e.g., "Olive Oil with Truffle"
CREATE TABLE `products` (
    `id` INT NOT NULL AUTO_INCREMENT,
    `category_id` INT NOT NULL,
    `name` VARCHAR(255) NOT NULL,
    `description` TEXT,
    `collection` VARCHAR(255), -- e.g., "Winter 2025 Collection"
    `deleted_at` TIMESTAMP NULL,
    PRIMARY KEY (`id`),
    FOREIGN KEY (`category_id`) REFERENCES `categories`(`id`)
);

-- 3. Create product variants. This is the purchasable entity (the SKU).
--    e.g., "Olive Oil with Truffle - 250ml bottle"
CREATE TABLE `product_variants` (
    `id` INT NOT NULL AUTO_INCREMENT,
    `product_id` INT NOT NULL,
    `sku` VARCHAR(100) UNIQUE NOT NULL, -- The actual Stock Keeping Unit identifier
    `price` DECIMAL(10, 2) NOT NULL,
    `attributes` JSON, -- e.g., {"volume": "250ml", "container": "glass bottle"}
    `inventory_count` INT NOT NULL DEFAULT 0,
    `deleted_at` TIMESTAMP NULL,
    PRIMARY KEY (`id`),
    FOREIGN KEY (`product_id`) REFERENCES `products`(`id`)
);

-- 4. Create product items. These are the individual, serialized instances of a variant.
--    This table holds the "Product Passport".
CREATE TABLE `product_items` (
    `id` INT NOT NULL AUTO_INCREMENT,
    `product_variant_id` INT NOT NULL,
    `serial_number` VARCHAR(255) UNIQUE,
    `status` ENUM('in_stock', 'allocated', 'sold', 'recalled') NOT NULL DEFAULT 'in_stock',
    `passport_data` JSON, -- The Product Passport, e.g., {"origin": "Farm X", "bottled_date": "..."}
    `order_item_id` INT NULL, -- Link to an order once sold
    `deleted_at` TIMESTAMP NULL,
    PRIMARY KEY (`id`),
    FOREIGN KEY (`product_variant_id`) REFERENCES `product_variants`(`id`)
);



-- One-Time Password (TOTP) multi-factor authentication.

-- 1. Add a boolean flag to track if MFA is enabled for a user.
--    We default it to FALSE. It's only set to TRUE after successful setup and verification.
ALTER TABLE `users`
ADD COLUMN `is_mfa_enabled` BOOLEAN NOT NULL DEFAULT FALSE;

-- 2. Add a column to store the user's encrypted MFA secret.
--    This should always be stored encrypted at rest. The application will decrypt it
--    in memory only when needed for verification.
ALTER TABLE `users`
ADD COLUMN `mfa_secret` VARCHAR(255) NULL;

-- 3. Add a table to store single-use recovery codes.
--    This allows users who lose their MFA device to regain access.
CREATE TABLE `mfa_recovery_codes` (
    `id` INT NOT NULL AUTO_INCREMENT,
    `user_id` INT NOT NULL,
    `code_hash` VARCHAR(255) NOT NULL, -- Store a hash of the code, not the code itself
    `is_used` BOOLEAN NOT NULL DEFAULT FALSE,
    PRIMARY KEY (`id`),
    FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE
);


CREATE TABLE `invoices` (
    `id` INT NOT NULL AUTO_INCREMENT,
    `order_id` INT NOT NULL,
    `user_id` INT NOT NULL,
    `invoice_number` VARCHAR(255) UNIQUE NOT NULL,
    `file_path` VARCHAR(1024) NOT NULL, -- Path to the invoice file in secure storage (e.g., S3 key)
    `generated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `deleted_at` TIMESTAMP NULL,
    PRIMARY KEY (`id`),
    FOREIGN KEY (`order_id`) REFERENCES `orders`(`id`),
    FOREIGN KEY (`user_id`) REFERENCES `users`(`id`)
);

-- It's also a good idea to add an index on user_id for fast lookups.
CREATE INDEX idx_invoices_user_id ON `invoices` (`user_id`);

