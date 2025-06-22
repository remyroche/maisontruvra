-- FILE: database_schema_updates.sql
-- This file outlines the necessary SQL changes to support the detailed product hierarchy,
-- using PostgreSQL syntax.

-- 1. Create a table for the highest-level categories.
CREATE TABLE "categories" (
    "id" SERIAL PRIMARY KEY,
    "name" VARCHAR(255) NOT NULL,
    "description" TEXT,
    "deleted_at" TIMESTAMP WITH TIME ZONE NULL
);

-- 2. Create the main products table.
CREATE TABLE "products" (
    "id" SERIAL PRIMARY KEY,
    "category_id" INTEGER NOT NULL,
    "name" VARCHAR(255) NOT NULL,
    "description" TEXT,
    "collection" VARCHAR(255),
    "deleted_at" TIMESTAMP WITH TIME ZONE NULL,
    FOREIGN KEY ("category_id") REFERENCES "categories"("id")
);

-- 3. Create product variants (SKUs).
CREATE TABLE "product_variants" (
    "id" SERIAL PRIMARY KEY,
    "product_id" INTEGER NOT NULL,
    "sku" VARCHAR(100) UNIQUE NOT NULL,
    "price" DECIMAL(10, 2) NOT NULL,
    "attributes" JSONB, -- JSONB is generally preferred over JSON in PostgreSQL
    "inventory_count" INTEGER NOT NULL DEFAULT 0,
    "deleted_at" TIMESTAMP WITH TIME ZONE NULL,
    FOREIGN KEY ("product_id") REFERENCES "products"("id")
);

-- 4. Create an ENUM type for the status of product items.
CREATE TYPE product_item_status AS ENUM('in_stock', 'allocated', 'sold', 'recalled');

-- 5. Create product items (serialized instances with Product Passport).
CREATE TABLE "product_items" (
    "id" SERIAL PRIMARY KEY,
    "product_variant_id" INTEGER NOT NULL,
    "serial_number" VARCHAR(255) UNIQUE,
    "status" product_item_status NOT NULL DEFAULT 'in_stock',
    "passport_data" JSONB,
    "order_item_id" INTEGER NULL,
    "deleted_at" TIMESTAMP WITH TIME ZONE NULL,
    FOREIGN KEY ("product_variant_id") REFERENCES "product_variants"("id")
);

