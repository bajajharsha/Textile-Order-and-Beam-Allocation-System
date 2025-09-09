-- Textile Order and Beam Allocation System Database Schema
-- Execute these SQL commands in Supabase SQL Editor

-- 1. Parties Table
CREATE TABLE parties (
    id SERIAL PRIMARY KEY,
    party_name VARCHAR(255) NOT NULL UNIQUE,
    contact_number VARCHAR(20) NOT NULL,
    broker_name VARCHAR(255),
    gst VARCHAR(20) UNIQUE,
    address TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 2. Colors Table (Master Data)
CREATE TABLE colors (
    id SERIAL PRIMARY KEY,
    color_code VARCHAR(10) NOT NULL UNIQUE,
    color_name VARCHAR(100) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 3. Qualities Table (Master Data)
CREATE TABLE qualities (
    id SERIAL PRIMARY KEY,
    quality_name VARCHAR(255) NOT NULL UNIQUE,
    feeder_count INTEGER NOT NULL,
    specification VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 4. Cuts Table (Master Data)
CREATE TABLE cuts (
    id SERIAL PRIMARY KEY,
    cut_value VARCHAR(20) NOT NULL UNIQUE,
    description VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 5. Orders Table
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    order_number VARCHAR(50) NOT NULL UNIQUE,
    party_id INTEGER REFERENCES parties(id),
    quality_id INTEGER REFERENCES qualities(id),
    order_date DATE DEFAULT CURRENT_DATE,
    rate_per_piece DECIMAL(10,2) NOT NULL,
    total_designs INTEGER DEFAULT 0,
    total_pieces INTEGER DEFAULT 0,
    total_value DECIMAL(12,2) DEFAULT 0,
    notes TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 6. Order Cuts Table (Multiple cuts per order)
CREATE TABLE order_cuts (
    id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(id) ON DELETE CASCADE,
    cut_value VARCHAR(20) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 7. Order Items Table (Design numbers with ground/beam colors)
CREATE TABLE order_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(id) ON DELETE CASCADE,
    design_number VARCHAR(50) NOT NULL,
    ground_color_id INTEGER REFERENCES colors(id),
    beam_color_id INTEGER REFERENCES colors(id),
    pieces_per_color INTEGER NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX idx_parties_active ON parties(is_active);
CREATE INDEX idx_colors_active ON colors(is_active);
CREATE INDEX idx_qualities_active ON qualities(is_active);
CREATE INDEX idx_cuts_active ON cuts(is_active);
CREATE INDEX idx_orders_active ON orders(is_active);
CREATE INDEX idx_orders_party ON orders(party_id);
CREATE INDEX idx_orders_quality ON orders(quality_id);
CREATE INDEX idx_order_cuts_order ON order_cuts(order_id);
CREATE INDEX idx_order_items_order ON order_items(order_id);
CREATE INDEX idx_order_items_design ON order_items(design_number);

-- Insert sample master data
-- Colors
INSERT INTO colors (color_code, color_name) VALUES
('R', 'Red'),
('B', 'Black'),
('F', 'Firozi'),
('G', 'Gold'),
('RB', 'Royal Blue'),
('W', 'White'),
('GR', 'Green'),
('Y', 'Yellow'),
('P', 'Purple'),
('O', 'Orange');

-- Qualities
INSERT INTO qualities (quality_name, feeder_count, specification) VALUES
('2 feeder 50/600', 2, 'Standard 2 feeder quality'),
('3 feeder 40/500', 3, 'Premium 3 feeder quality'),
('4 feeder 60/700', 4, 'Heavy duty 4 feeder quality'),
('2 feeder 45/550', 2, 'Light weight 2 feeder quality');

-- Cuts
INSERT INTO cuts (cut_value, description) VALUES
('4.10', 'Standard cut 4.10 meters'),
('6.10', 'Long cut 6.10 meters'),
('5.50', 'Medium cut 5.50 meters'),
('3.75', 'Short cut 3.75 meters');

-- Sample Party (for testing)
INSERT INTO parties (party_name, contact_number, broker_name, gst, address) VALUES
('Agarwal Fabrics', '9876543210', 'Rajesh Broker', 'GST123456789', 'Mumbai, Maharashtra'),
('Sheetal Creation', '9876543211', 'Suresh Broker', 'GST123456790', 'Surat, Gujarat'),
('Modern Textiles', '9876543212', 'Ramesh Broker', 'GST123456791', 'Ahmedabad, Gujarat');
