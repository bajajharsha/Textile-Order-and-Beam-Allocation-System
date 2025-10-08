# 🎯 **COMPLETE SETUP GUIDE**

## **CRITICAL: Run ALL These Steps in Order**

---

## 📋 **STEP 1: Create Missing Tables in Supabase**

Open **Supabase Dashboard** → **SQL Editor** → Run:

```sql
-- Create lot_design_allocations table
CREATE TABLE IF NOT EXISTS lot_design_allocations (
    id SERIAL PRIMARY KEY,
    lot_id INTEGER REFERENCES lot_register(id) ON DELETE CASCADE,
    order_id INTEGER REFERENCES orders(id) ON DELETE CASCADE,
    design_number VARCHAR(50) NOT NULL,
    allocated_sets INTEGER NOT NULL DEFAULT 0,
    notes TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(lot_id, design_number)
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_lot_design_allocations_lot_id ON lot_design_allocations(lot_id);
CREATE INDEX IF NOT EXISTS idx_lot_design_allocations_order_design ON lot_design_allocations(order_id, design_number);

SELECT 'lot_design_allocations table created!' AS status;
```

---

## 📋 **STEP 2: Add CASCADE DELETE Constraints**

Run this to ensure data cleanup when orders are deleted:

```sql
-- Drop and recreate constraints with CASCADE DELETE

-- design_set_tracking
ALTER TABLE design_set_tracking 
DROP CONSTRAINT IF EXISTS design_set_tracking_order_id_fkey;

ALTER TABLE design_set_tracking 
ADD CONSTRAINT design_set_tracking_order_id_fkey 
FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE;

-- design_beam_config
ALTER TABLE design_beam_config 
DROP CONSTRAINT IF EXISTS design_beam_config_order_id_fkey;

ALTER TABLE design_beam_config 
ADD CONSTRAINT design_beam_config_order_id_fkey 
FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE;

-- order_items
ALTER TABLE order_items 
DROP CONSTRAINT IF EXISTS order_items_order_id_fkey;

ALTER TABLE order_items 
ADD CONSTRAINT order_items_order_id_fkey 
FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE;

-- order_item_status
ALTER TABLE order_item_status 
DROP CONSTRAINT IF EXISTS order_item_status_order_id_fkey;

ALTER TABLE order_item_status 
ADD CONSTRAINT order_item_status_order_id_fkey 
FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE;

-- lot_allocations
ALTER TABLE lot_allocations 
DROP CONSTRAINT IF EXISTS lot_allocations_order_id_fkey;

ALTER TABLE lot_allocations 
ADD CONSTRAINT lot_allocations_order_id_fkey 
FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE;

SELECT 'CASCADE DELETE constraints added!' AS status;
```

---

## 📋 **STEP 3: Clean Up Old Data (One-Time)**

Run this to remove orphaned design tracking data:

```sql
-- Remove orphaned design tracking data
DELETE FROM design_beam_config 
WHERE order_id NOT IN (SELECT id FROM orders WHERE is_active = true);

DELETE FROM design_set_tracking 
WHERE order_id NOT IN (SELECT id FROM orders WHERE is_active = true);

SELECT 'Old data cleaned!' AS status;
```

---

## 📋 **STEP 4: Initialize Design Tracking for Existing Orders (If Any)**

If you have existing orders in the database:

```bash
cd backend
python initialize_design_tracking_for_existing_orders.py
```

---

## 📋 **STEP 5: Restart Backend Server**

```bash
cd backend
python -m uvicorn main:app --reload --port 8001
```

---

## 📋 **STEP 6: Refresh Frontend**

Press **F5** or **Ctrl+R** in your browser.

---

## ✅ **VERIFICATION CHECKLIST:**

### **Test 1: Create Order**
1. Go to **Orders** tab
2. Click **"+ Create Order"**
3. Fill in:
   - Party: Harsha
   - Quality: 4 feeder 60/700
   - Sets: 40
   - Pick: 1
   - Lot Register Type: High Speed
   - Designs: A1, A2
   - Ground Colors: G1, G2, G3, G4 (with beam colors)
4. Click **"Create Order"**

### **Test 2: Check Design-Wise Allocation**
1. Go to **"Design-Wise Allocation"** tab
2. ✅ Should show A1 and A2
3. ✅ Each should show: 40 total sets, 0 allocated, 40 remaining
4. ✅ Beam columns should show pieces (B, F, RB, etc.)

### **Test 3: Create Lot from Design-Wise**
1. Click **"Create Lot"** button
2. Select Party: Harsha
3. Select Quality: 4 feeder 60/700
4. Designs A1 and A2 should appear
5. Select A1
6. Enter Lot Number: LOT-001
7. Allocate: 10 sets
8. Click **"Create Lot"**

### **Test 4: Verify Reduction**
1. Table should refresh automatically
2. ✅ A1 should now show: 40 total, 10 allocated, **30 remaining**
3. ✅ Beam pieces should be reduced (60 instead of 80 for B-2, etc.)

### **Test 5: Check Lot Register**
1. Go to **"Lot Register"** tab
2. ✅ Should show LOT-001 for design A1
3. ✅ Total Pieces: 40 (10 × 4)
4. ✅ Shows breakdown: "(10 × 4)" below the number

### **Test 6: Create Lot from Lot Register**
1. Click **"+ Create Lot"** button in Lot Register
2. Same flow as Test 3
3. Allocate 10 more sets of A1 to LOT-002
4. ✅ Lot Register should show TWO entries now

### **Test 7: Delete Order**
1. Go to **Orders** tab
2. Delete the order
3. ✅ Design-Wise Allocation should become empty
4. ✅ Lot Register should become empty
5. ✅ All related data automatically deleted (CASCADE)

---

## 🎯 **FEATURES IMPLEMENTED:**

### **1. Design-Wise Beam Allocation Table:**
- ✅ Shows all designs immediately after order creation
- ✅ Displays: Total Sets / Allocated Sets / Remaining Sets
- ✅ Beam color columns (R, F, G, RB, B, W, Y, GR, P, O)
- ✅ Real-time reduction as lots are created
- ✅ Grouped by order (expandable)
- ✅ Summary cards at top
- ✅ "Create Lot" button

### **2. Set-Based Lot Creation Form:**
- ✅ Manual lot number entry
- ✅ Party & quality selection
- ✅ Shows available designs with remaining sets
- ✅ Allocate sets per design
- ✅ Optional fields: Bill#, Actual Pieces, Delivery Date
- ✅ Real-time validation
- ✅ Accessible from both Design-Wise and Lot Register

### **3. Lot Register Table:**
- ✅ Shows ONLY created lots
- ✅ Total Pieces = allocated_sets × ground_colors
- ✅ Shows formula breakdown: "40 (10 × 4)"
- ✅ In-place editing for Bill#, Actual Pieces, Delivery Date
- ✅ "Create Lot" button
- ✅ Filter by lot register type

### **4. Data Management:**
- ✅ Automatic design tracking initialization on order creation
- ✅ CASCADE DELETE - deleting order removes all related data
- ✅ Set-based allocation tracking
- ✅ Reduction mechanism

---

## 🚀 **YOU'RE READY!**

Follow all steps above, then test the complete flow. Everything should work seamlessly!

