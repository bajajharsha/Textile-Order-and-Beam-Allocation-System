-- Lot Register and Allocation System Extensions
-- Execute these SQL commands after the main schema

-- 1. Lot Register Table
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
    status VARCHAR(20) DEFAULT 'PENDING', -- PENDING, IN_PROGRESS, COMPLETED, DELIVERED
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 2. Lot Allocations Table (tracks which order items are allocated to which lots)
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

-- 3. Order Item Status Table (tracks allocated vs remaining quantities)
CREATE TABLE order_item_status (
    id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(id),
    design_number VARCHAR(50) NOT NULL,
    ground_color_name VARCHAR(100) NOT NULL,
    beam_color_id INTEGER REFERENCES colors(id),
    total_pieces INTEGER NOT NULL DEFAULT 0, -- Original order quantity
    allocated_pieces INTEGER NOT NULL DEFAULT 0, -- Pieces allocated to lots
    remaining_pieces INTEGER NOT NULL DEFAULT 0, -- Pieces not yet allocated
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    -- Ensure remaining_pieces = total_pieces - allocated_pieces
    CONSTRAINT check_remaining_pieces CHECK (remaining_pieces = total_pieces - allocated_pieces)
);

-- Create indexes for better performance
CREATE INDEX idx_lot_register_party ON lot_register(party_id);
CREATE INDEX idx_lot_register_quality ON lot_register(quality_id);
CREATE INDEX idx_lot_register_date ON lot_register(lot_date);
CREATE INDEX idx_lot_register_status ON lot_register(status);

CREATE INDEX idx_lot_allocations_lot ON lot_allocations(lot_id);
CREATE INDEX idx_lot_allocations_order ON lot_allocations(order_id);
CREATE INDEX idx_lot_allocations_design ON lot_allocations(design_number);

CREATE INDEX idx_order_item_status_order ON order_item_status(order_id);
CREATE INDEX idx_order_item_status_design ON order_item_status(design_number);
CREATE INDEX idx_order_item_status_remaining ON order_item_status(remaining_pieces);

-- Views for easier reporting

-- 1. Partywise Detail (Red Book) View
CREATE VIEW partywise_detail_view AS
SELECT 
    o.order_date as date,
    ois.design_number as des_no,
    q.quality_name as quality,
    ois.remaining_pieces as units_pcs,
    o.rate_per_piece as rate,
    la.lot_id,
    lr.lot_number as lot_no,
    lr.lot_date as lot_no_date,
    lr.bill_number as bill_no,
    lr.actual_pieces,
    lr.delivery_date,
    p.party_name,
    o.id as order_id,
    ois.id as status_id
FROM order_item_status ois
JOIN orders o ON ois.order_id = o.id
JOIN parties p ON o.party_id = p.id
JOIN qualities q ON o.quality_id = q.id
LEFT JOIN lot_allocations la ON (
    ois.order_id = la.order_id 
    AND ois.design_number = la.design_number 
    AND ois.ground_color_name = la.ground_color_name
)
LEFT JOIN lot_register lr ON la.lot_id = lr.id
WHERE ois.is_active = TRUE 
    AND o.is_active = TRUE
ORDER BY o.order_date DESC, ois.design_number;

-- 2. Lot Register View
CREATE VIEW lot_register_view AS
SELECT 
    lr.lot_date,
    lr.lot_number as lot_no,
    p.party_name,
    la.design_number as design_no,
    q.quality_name as quality,
    SUM(la.allocated_pieces) as total_pieces,
    lr.bill_number as bill_no,
    lr.actual_pieces,
    lr.delivery_date,
    lr.status,
    lr.id as lot_id
FROM lot_register lr
JOIN parties p ON lr.party_id = p.id
JOIN qualities q ON lr.quality_id = q.id
LEFT JOIN lot_allocations la ON lr.id = la.lot_id
WHERE lr.is_active = TRUE
GROUP BY lr.id, lr.lot_date, lr.lot_number, p.party_name, 
         la.design_number, q.quality_name, lr.bill_number, 
         lr.actual_pieces, lr.delivery_date, lr.status
ORDER BY lr.lot_date DESC, lr.lot_number;

-- 3. Updated Beam Summary View (with allocated vs remaining)
CREATE VIEW beam_summary_with_allocation AS
SELECT 
    o.id as order_id,
    p.party_name,
    q.quality_name,
    c.color_code,
    c.color_name as beam_color_name,
    SUM(ois.total_pieces) as total_pieces,
    SUM(ois.allocated_pieces) as allocated_pieces,
    SUM(ois.remaining_pieces) as remaining_pieces,
    COUNT(DISTINCT ois.design_number) as design_count
FROM order_item_status ois
JOIN orders o ON ois.order_id = o.id
JOIN parties p ON o.party_id = p.id
JOIN qualities q ON o.quality_id = q.id
JOIN colors c ON ois.beam_color_id = c.id
WHERE ois.is_active = TRUE 
    AND o.is_active = TRUE
    AND ois.remaining_pieces > 0  -- Only show unallocated items
GROUP BY o.id, p.party_name, q.quality_name, c.color_code, c.color_name
ORDER BY q.quality_name, p.party_name;

-- Functions for automatic calculations

-- Function to generate lot number
CREATE OR REPLACE FUNCTION generate_lot_number()
RETURNS VARCHAR(50) AS $$
DECLARE
    next_number INTEGER;
    lot_number VARCHAR(50);
BEGIN
    -- Get the next sequence number
    SELECT COALESCE(MAX(CAST(SUBSTRING(lot_number FROM 2) AS INTEGER)), 0) + 1
    INTO next_number
    FROM lot_register
    WHERE lot_number ~ '^L[0-9]+$';
    
    -- Format as L001, L002, etc.
    lot_number := 'L' || LPAD(next_number::TEXT, 3, '0');
    
    RETURN lot_number;
END;
$$ LANGUAGE plpgsql;

-- Trigger to auto-generate lot number
CREATE OR REPLACE FUNCTION set_lot_number()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.lot_number IS NULL OR NEW.lot_number = '' THEN
        NEW.lot_number := generate_lot_number();
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_set_lot_number
    BEFORE INSERT ON lot_register
    FOR EACH ROW
    EXECUTE FUNCTION set_lot_number();

-- Trigger to update order_item_status when lot_allocations change
CREATE OR REPLACE FUNCTION update_order_item_status()
RETURNS TRIGGER AS $$
BEGIN
    -- Update allocated and remaining pieces
    UPDATE order_item_status 
    SET 
        allocated_pieces = COALESCE((
            SELECT SUM(allocated_pieces) 
            FROM lot_allocations 
            WHERE order_id = NEW.order_id 
                AND design_number = NEW.design_number 
                AND ground_color_name = NEW.ground_color_name
                AND is_active = TRUE
        ), 0),
        remaining_pieces = total_pieces - COALESCE((
            SELECT SUM(allocated_pieces) 
            FROM lot_allocations 
            WHERE order_id = NEW.order_id 
                AND design_number = NEW.design_number 
                AND ground_color_name = NEW.ground_color_name
                AND is_active = TRUE
        ), 0),
        updated_at = NOW()
    WHERE order_id = NEW.order_id 
        AND design_number = NEW.design_number 
        AND ground_color_name = NEW.ground_color_name;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_order_item_status
    AFTER INSERT OR UPDATE OR DELETE ON lot_allocations
    FOR EACH ROW
    EXECUTE FUNCTION update_order_item_status();
