-- Migration script to ensure lot-related tables exist
-- Execute these SQL commands in Supabase SQL Editor

-- Note: This script assumes the database_extensions.sql has been executed
-- If not, please run database_extensions.sql first

-- Step 1: Ensure lot_register table exists
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'lot_register') THEN
        CREATE TABLE lot_register (
            id SERIAL PRIMARY KEY,
            lot_number VARCHAR(50) NOT NULL UNIQUE,
            lot_date DATE NOT NULL DEFAULT CURRENT_DATE,
            party_id INTEGER REFERENCES parties(id),
            quality_id INTEGER REFERENCES qualities(id),
            total_pieces INTEGER NOT NULL DEFAULT 0,
            bill_number VARCHAR(50),
            actual_pieces INTEGER,
            delivery_date DATE,
            notes TEXT,
            status VARCHAR(20) DEFAULT 'PENDING',
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW()
        );
    END IF;
END $$;

-- Step 2: Ensure lot_allocations table exists
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'lot_allocations') THEN
        CREATE TABLE lot_allocations (
            id SERIAL PRIMARY KEY,
            lot_id INTEGER REFERENCES lot_register(id) ON DELETE CASCADE,
            order_id INTEGER REFERENCES orders(id),
            design_number VARCHAR(50) NOT NULL,
            ground_color_name VARCHAR(100) NOT NULL,
            beam_color_id INTEGER REFERENCES colors(id),
            allocated_pieces INTEGER NOT NULL DEFAULT 0,
            notes TEXT,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW()
        );
    END IF;
END $$;

-- Step 3: Ensure order_item_status table exists
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'order_item_status') THEN
        CREATE TABLE order_item_status (
            id SERIAL PRIMARY KEY,
            order_id INTEGER REFERENCES orders(id),
            design_number VARCHAR(50) NOT NULL,
            ground_color_name VARCHAR(100) NOT NULL,
            beam_color_id INTEGER REFERENCES colors(id),
            total_pieces INTEGER NOT NULL DEFAULT 0,
            allocated_pieces INTEGER NOT NULL DEFAULT 0,
            remaining_pieces INTEGER NOT NULL DEFAULT 0,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW()
        );
    END IF;
END $$;

-- Step 4: Create indexes for better performance
DO $$ 
BEGIN
    -- Lot register table indexes
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_lot_register_party') THEN
        CREATE INDEX idx_lot_register_party ON lot_register(party_id);
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_lot_register_quality') THEN
        CREATE INDEX idx_lot_register_quality ON lot_register(quality_id);
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_lot_register_date') THEN
        CREATE INDEX idx_lot_register_date ON lot_register(lot_date);
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_lot_register_status') THEN
        CREATE INDEX idx_lot_register_status ON lot_register(status);
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_lot_register_active') THEN
        CREATE INDEX idx_lot_register_active ON lot_register(is_active);
    END IF;
    
    -- Lot allocations table indexes
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_lot_allocations_lot') THEN
        CREATE INDEX idx_lot_allocations_lot ON lot_allocations(lot_id);
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_lot_allocations_order') THEN
        CREATE INDEX idx_lot_allocations_order ON lot_allocations(order_id);
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_lot_allocations_design') THEN
        CREATE INDEX idx_lot_allocations_design ON lot_allocations(design_number);
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_lot_allocations_color') THEN
        CREATE INDEX idx_lot_allocations_color ON lot_allocations(beam_color_id);
    END IF;
    
    -- Order item status table indexes
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_order_item_status_order') THEN
        CREATE INDEX idx_order_item_status_order ON order_item_status(order_id);
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_order_item_status_design') THEN
        CREATE INDEX idx_order_item_status_design ON order_item_status(design_number);
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_order_item_status_remaining') THEN
        CREATE INDEX idx_order_item_status_remaining ON order_item_status(remaining_pieces);
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_order_item_status_active') THEN
        CREATE INDEX idx_order_item_status_active ON order_item_status(is_active);
    END IF;
END $$;

-- Step 5: Add constraints
DO $$
BEGIN
    -- Add constraint to ensure remaining_pieces is not negative
    IF NOT EXISTS (SELECT 1 FROM information_schema.table_constraints 
                   WHERE constraint_name = 'check_remaining_pieces_positive' AND table_name = 'order_item_status') THEN
        ALTER TABLE order_item_status ADD CONSTRAINT check_remaining_pieces_positive 
        CHECK (remaining_pieces >= 0);
    END IF;
    
    -- Add constraint to ensure total_pieces is not negative
    IF NOT EXISTS (SELECT 1 FROM information_schema.table_constraints 
                   WHERE constraint_name = 'check_total_pieces_positive' AND table_name = 'order_item_status') THEN
        ALTER TABLE order_item_status ADD CONSTRAINT check_total_pieces_positive 
        CHECK (total_pieces >= 0);
    END IF;
    
    -- Add constraint to ensure allocated_pieces is not negative
    IF NOT EXISTS (SELECT 1 FROM information_schema.table_constraints 
                   WHERE constraint_name = 'check_allocated_pieces_positive' AND table_name = 'order_item_status') THEN
        ALTER TABLE order_item_status ADD CONSTRAINT check_allocated_pieces_positive 
        CHECK (allocated_pieces >= 0);
    END IF;
    
    -- Add constraint to ensure lot_register total_pieces is not negative
    IF NOT EXISTS (SELECT 1 FROM information_schema.table_constraints 
                   WHERE constraint_name = 'check_lot_register_total_pieces_positive' AND table_name = 'lot_register') THEN
        ALTER TABLE lot_register ADD CONSTRAINT check_lot_register_total_pieces_positive 
        CHECK (total_pieces >= 0);
    END IF;
    
    -- Add constraint to ensure lot_allocations allocated_pieces is not negative
    IF NOT EXISTS (SELECT 1 FROM information_schema.table_constraints 
                   WHERE constraint_name = 'check_lot_allocations_allocated_pieces_positive' AND table_name = 'lot_allocations') THEN
        ALTER TABLE lot_allocations ADD CONSTRAINT check_lot_allocations_allocated_pieces_positive 
        CHECK (allocated_pieces >= 0);
    END IF;
END $$;

-- Verification queries (optional - run these to check the changes)
-- SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_name LIKE '%lot%' ORDER BY table_name;
-- SELECT column_name, data_type, is_nullable FROM information_schema.columns WHERE table_name = 'lot_register' ORDER BY ordinal_position;
-- SELECT column_name, data_type, is_nullable FROM information_schema.columns WHERE table_name = 'order_item_status' ORDER BY ordinal_position;
