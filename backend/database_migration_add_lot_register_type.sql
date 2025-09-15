-- Migration script to add lot_register_type column to orders table
-- Execute these SQL commands in Supabase SQL Editor

-- Step 1: Add the new 'lot_register_type' column (if it doesn't exist)
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'orders' AND column_name = 'lot_register_type') THEN
        ALTER TABLE orders ADD COLUMN lot_register_type VARCHAR(20) NOT NULL DEFAULT 'High Speed';
    END IF;
END $$;

-- Step 2: Add constraint to ensure lot_register_type is one of the valid values (if it doesn't exist)
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.table_constraints 
                   WHERE constraint_name = 'check_lot_register_type' AND table_name = 'orders') THEN
        ALTER TABLE orders ADD CONSTRAINT check_lot_register_type 
        CHECK (lot_register_type IN ('High Speed', 'Slow Speed', 'K1K2'));
    END IF;
END $$;

-- Step 3: Update any existing records to have a default lot register type
UPDATE orders SET lot_register_type = 'High Speed' WHERE lot_register_type = '' OR lot_register_type IS NULL;

-- Verification queries (optional - run these to check the changes)
-- SELECT column_name, data_type, is_nullable, column_default 
-- FROM information_schema.columns 
-- WHERE table_name = 'orders' 
-- ORDER BY ordinal_position;

-- SELECT id, order_number, lot_register_type FROM orders LIMIT 5;
