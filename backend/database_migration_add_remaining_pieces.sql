-- Migration script to add remaining_pieces column to order_item_status table
-- Execute these SQL commands in Supabase SQL Editor

-- Step 1: Add the new 'remaining_pieces' column to order_item_status table
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'order_item_status' AND column_name = 'remaining_pieces') THEN
        ALTER TABLE order_item_status ADD COLUMN remaining_pieces INTEGER;
    END IF;
END $$;

-- Step 2: Initialize remaining_pieces with current total_pieces values
UPDATE order_item_status SET remaining_pieces = total_pieces WHERE remaining_pieces IS NULL;

-- Step 3: Add constraint to ensure remaining_pieces is not negative
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.table_constraints 
                   WHERE constraint_name = 'check_remaining_pieces_positive' AND table_name = 'order_item_status') THEN
        ALTER TABLE order_item_status ADD CONSTRAINT check_remaining_pieces_positive 
        CHECK (remaining_pieces >= 0);
    END IF;
END $$;

-- Verification queries (optional - run these to check the changes)
-- SELECT column_name, data_type, is_nullable, column_default 
-- FROM information_schema.columns 
-- WHERE table_name = 'order_item_status' 
-- ORDER BY ordinal_position;

-- SELECT id, design_number, total_pieces, remaining_pieces FROM order_item_status LIMIT 5;
