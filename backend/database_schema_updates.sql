-- FILE: database_schema_updates.sql
-- This file outlines the necessary SQL changes to support the detailed product hierarchy,
-- using PostgreSQL syntax.

-- Add indexes to foreign keys and frequently queried columns for performance
CREATE INDEX IF NOT EXISTS idx_user_loyalty_user_id ON user_loyalty(user_id);
CREATE INDEX IF NOT EXISTS idx_user_loyalty_tier_id ON user_loyalty(tier_id);
CREATE INDEX IF NOT EXISTS idx_loyalty_point_logs_user_id ON loyalty_point_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_referrals_referrer_id ON referrals(referrer_id);
CREATE INDEX IF NOT EXISTS idx_point_vouchers_user_id ON point_vouchers(user_id);
CREATE INDEX IF NOT EXISTS idx_exclusive_rewards_tier_id ON exclusive_rewards(tier_id);
CREATE INDEX IF NOT EXISTS idx_orders_user_id ON orders(user_id);
CREATE INDEX IF NOT EXISTS idx_order_items_order_id ON order_items(order_id);
CREATE INDEX IF NOT EXISTS idx_order_items_product_id ON order_items(product_id);
CREATE INDEX IF NOT EXISTS idx_cart_items_cart_id ON cart_items(cart_id);
CREATE INDEX IF NOT EXISTS idx_cart_items_product_id ON cart_items(product_id);
CREATE INDEX IF NOT EXISTS idx_products_category_id ON products(category_id);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);


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


CREATE TABLE loyalty_tiers (
    id UUID PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    min_spend FLOAT NOT NULL,
    points_per_euro FLOAT NOT NULL,
    benefits TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE user_loyalty (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE UNIQUE,
    tier_id UUID NOT NULL REFERENCES loyalty_tiers(id) ON DELETE RESTRICT,
    points INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE loyalty_point_logs (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    points_change INTEGER NOT NULL,
    reason VARCHAR(255) NOT NULL,
    order_id UUID REFERENCES orders(id),
    changed_by_admin_id UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE referrals (
    id UUID PRIMARY KEY,
    referrer_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    referred_id UUID REFERENCES users(id) ON DELETE SET NULL,
    referral_code VARCHAR(50) NOT NULL UNIQUE,
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE referral_rewards (
    id UUID PRIMARY KEY,
    referral_count INTEGER NOT NULL UNIQUE,
    reward_description VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE point_vouchers (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    voucher_code VARCHAR(50) NOT NULL UNIQUE,
    points_cost INTEGER NOT NULL,
    discount_amount FLOAT NOT NULL,
    is_used BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE exclusive_rewards (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    points_cost INTEGER NOT NULL,
    reward_type VARCHAR(50) NOT NULL,
    tier_id UUID NOT NULL REFERENCES loyalty_tiers(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

