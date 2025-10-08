-- =====================================================
-- Add table to track set-based lot allocations per design
-- =====================================================

-- Create lot_design_allocations table to track which designs and how many sets were allocated to each lot
CREATE TABLE IF NOT EXISTS lot_design_allocations (
    id SERIAL PRIMARY KEY,
    lot_id INTEGER REFERENCES lot_register(id) ON DELETE CASCADE,
    order_id INTEGER REFERENCES orders(id),
    design_number VARCHAR(50) NOT NULL,
    allocated_sets INTEGER NOT NULL DEFAULT 0,
    notes TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    -- Ensure unique lot + design combination
    UNIQUE(lot_id, design_number)
);

-- Create index for faster lookups
CREATE INDEX IF NOT EXISTS idx_lot_design_allocations_lot_id ON lot_design_allocations(lot_id);
CREATE INDEX IF NOT EXISTS idx_lot_design_allocations_order_design ON lot_design_allocations(order_id, design_number);

-- Add comment
COMMENT ON TABLE lot_design_allocations IS 'Tracks set-based allocations for each design in a lot';
COMMENT ON COLUMN lot_design_allocations.allocated_sets IS 'Number of sets allocated for this design in this lot';

