# 🔧 **DATABASE UPDATE INSTRUCTIONS**

## **CRITICAL: Run This SQL in Supabase Before Testing**

The Lot Register now only shows **created lots** with **allocated sets**. To support this, you need to create a new table.

---

## **📋 STEP 1: Create New Table**

Open **Supabase Dashboard** → **SQL Editor** → Run this SQL:

```sql
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

-- Create indexes for faster lookups
CREATE INDEX IF NOT EXISTS idx_lot_design_allocations_lot_id ON lot_design_allocations(lot_id);
CREATE INDEX IF NOT EXISTS idx_lot_design_allocations_order_design ON lot_design_allocations(order_id, design_number);

-- Add comments
COMMENT ON TABLE lot_design_allocations IS 'Tracks set-based allocations for each design in a lot';
COMMENT ON COLUMN lot_design_allocations.allocated_sets IS 'Number of sets allocated for this design in this lot';

-- Verify table was created
SELECT 'Table created successfully!' AS status;
```

---

## **📋 STEP 2: Verify**

Run this query to check:

```sql
SELECT * FROM lot_design_allocations LIMIT 5;
```

You should see an empty table with these columns:
- `id`, `lot_id`, `order_id`, `design_number`, `allocated_sets`, `notes`, `is_active`, `created_at`, `updated_at`

---

## **✅ WHAT CHANGED:**

### **BEFORE:**
- Lot Register showed ALL designs from orders (even if no lot was created)
- Showed total sets from order (e.g., 40 sets)

### **AFTER:**
- Lot Register shows ONLY created lots
- Shows allocated sets in that specific lot (e.g., 10 sets in LOT-001)
- Formula now: `allocated_sets × ground_colors` instead of `total_sets × ground_colors`

---

## **🧪 EXAMPLE:**

**Order:** A1 has 40 sets, 4 ground colors

**Create LOT-001:** Allocate 10 sets of A1
- **Lot Register shows:** `40 pieces (10 × 4)`

**Create LOT-002:** Allocate another 10 sets of A1
- **Lot Register shows TWO entries:**
  - LOT-001: 40 pieces (10 × 4)
  - LOT-002: 40 pieces (10 × 4)

---

## **⚠️ IMPORTANT:**

After running the SQL, **restart your backend server**:

```bash
# In backend directory
python -m uvicorn main:app --reload --port 8001
```

Then **refresh your frontend** (F5)

---

## **🎯 READY TO TEST!**

Once the table is created and servers are restarted, you can test the complete flow.

