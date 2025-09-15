-- Migration script to rename 'units' to 'sets' and add 'pick' column
-- Execute these SQL commands in Supabase SQL Editor

-- Step 1: Add the new 'pick' column with default value 1
ALTER TABLE orders ADD COLUMN pick INTEGER NOT NULL DEFAULT 1;

-- Step 2: Rename 'units' column to 'sets'
ALTER TABLE orders RENAME COLUMN units TO sets;

-- Step 3: Add constraint to ensure pick is greater than 0
ALTER TABLE orders ADD CONSTRAINT check_pick_positive CHECK (pick > 0);

-- Step 4: Add constraint to ensure sets is greater than 0 (if not already exists)
ALTER TABLE orders ADD CONSTRAINT check_sets_positive CHECK (sets > 0);

-- Verification queries (optional - run these to check the changes)
-- SELECT column_name, data_type, is_nullable, column_default 
-- FROM information_schema.columns 
-- WHERE table_name = 'orders' 
-- ORDER BY ordinal_position;

-- SELECT id, order_number, sets, pick FROM orders LIMIT 5;
