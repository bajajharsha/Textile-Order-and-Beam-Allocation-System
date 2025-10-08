-- =====================================================
-- CLEAR ALL TRANSACTIONAL DATA (Keep Master Data)
-- =====================================================
-- This script clears orders, lots, and design tracking
-- while keeping parties, colors, qualities, and cuts

-- Step 1: Clear lot allocations (foreign key dependent)
TRUNCATE TABLE lot_allocations CASCADE;

-- Step 2: Clear lot register
TRUNCATE TABLE lot_register CASCADE;

-- Step 3: Clear design tracking tables (NEW system)
TRUNCATE TABLE design_beam_config CASCADE;
TRUNCATE TABLE design_set_tracking CASCADE;

-- Step 4: Clear order item status
TRUNCATE TABLE order_item_status CASCADE;

-- Step 5: Clear order items
TRUNCATE TABLE order_items CASCADE;

-- Step 6: Clear orders
TRUNCATE TABLE orders CASCADE;

-- Step 7: Reset sequences to start fresh
ALTER SEQUENCE orders_id_seq RESTART WITH 1;
ALTER SEQUENCE order_items_id_seq RESTART WITH 1;
ALTER SEQUENCE order_item_status_id_seq RESTART WITH 1;
ALTER SEQUENCE lot_register_id_seq RESTART WITH 1;
ALTER SEQUENCE lot_allocations_id_seq RESTART WITH 1;
ALTER SEQUENCE design_set_tracking_id_seq RESTART WITH 1;
ALTER SEQUENCE design_beam_config_id_seq RESTART WITH 1;

-- Confirmation message
SELECT 'Database cleared successfully! All orders, lots, and design tracking removed.' AS status;
SELECT 'Master data (parties, colors, qualities, cuts) preserved.' AS note;

