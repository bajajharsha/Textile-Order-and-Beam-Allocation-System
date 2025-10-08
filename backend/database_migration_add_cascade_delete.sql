-- =====================================================
-- ADD CASCADE DELETE CONSTRAINTS
-- =====================================================
-- This ensures that when an order is deleted, all related data is automatically removed

-- 1. Drop existing foreign key constraints that don't cascade
ALTER TABLE design_set_tracking 
DROP CONSTRAINT IF EXISTS design_set_tracking_order_id_fkey;

ALTER TABLE design_beam_config 
DROP CONSTRAINT IF EXISTS design_beam_config_order_id_fkey;

ALTER TABLE lot_design_allocations 
DROP CONSTRAINT IF EXISTS lot_design_allocations_order_id_fkey;

ALTER TABLE order_items 
DROP CONSTRAINT IF EXISTS order_items_order_id_fkey;

ALTER TABLE order_item_status 
DROP CONSTRAINT IF EXISTS order_item_status_order_id_fkey;

ALTER TABLE lot_allocations 
DROP CONSTRAINT IF EXISTS lot_allocations_order_id_fkey;

-- 2. Add CASCADE DELETE constraints
ALTER TABLE design_set_tracking 
ADD CONSTRAINT design_set_tracking_order_id_fkey 
FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE;

ALTER TABLE design_beam_config 
ADD CONSTRAINT design_beam_config_order_id_fkey 
FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE;

ALTER TABLE lot_design_allocations 
ADD CONSTRAINT lot_design_allocations_order_id_fkey 
FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE;

ALTER TABLE order_items 
ADD CONSTRAINT order_items_order_id_fkey 
FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE;

ALTER TABLE order_item_status 
ADD CONSTRAINT order_item_status_order_id_fkey 
FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE;

ALTER TABLE lot_allocations 
ADD CONSTRAINT lot_allocations_order_id_fkey 
FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE;

-- 3. Verify constraints
SELECT 
    tc.table_name, 
    tc.constraint_name, 
    rc.delete_rule
FROM information_schema.table_constraints tc
JOIN information_schema.referential_constraints rc 
    ON tc.constraint_name = rc.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY'
    AND tc.table_schema = 'public'
    AND (tc.table_name IN ('design_set_tracking', 'design_beam_config', 'lot_design_allocations', 
                           'order_items', 'order_item_status', 'lot_allocations'))
ORDER BY tc.table_name;

SELECT 'CASCADE DELETE constraints added successfully!' AS status;

