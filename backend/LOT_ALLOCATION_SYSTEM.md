# Lot Allocation System Documentation

## 📊 **System Overview**

The Lot Allocation System manages the allocation of orders to production lots, tracking the journey from order creation to delivery. This system implements the **Partywise Detail (Red Book)** and **Lot Register** functionality as requested.

---

## 🗃️ **Database Schema**

### **New Tables Added:**

#### **1. lot_register**
```sql
CREATE TABLE lot_register (
    id SERIAL PRIMARY KEY,
    lot_number VARCHAR(50) NOT NULL UNIQUE,        -- Auto-generated (L001, L002, etc.)
    lot_date DATE NOT NULL DEFAULT CURRENT_DATE,   -- Automatic when entry is made
    party_id INTEGER REFERENCES parties(id),
    quality_id INTEGER REFERENCES qualities(id),
    total_pieces INTEGER NOT NULL DEFAULT 0,
    bill_number VARCHAR(50),                       -- Manually entered
    actual_pieces INTEGER,                         -- Manually entered
    delivery_date DATE,                            -- Manually entered
    notes TEXT,
    status VARCHAR(20) DEFAULT 'PENDING',          -- PENDING, IN_PROGRESS, COMPLETED, DELIVERED
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

#### **2. lot_allocations**
```sql
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
```

#### **3. order_item_status**
```sql
CREATE TABLE order_item_status (
    id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(id),
    design_number VARCHAR(50) NOT NULL,
    ground_color_name VARCHAR(100) NOT NULL,
    beam_color_id INTEGER REFERENCES colors(id),
    total_pieces INTEGER NOT NULL DEFAULT 0,       -- Original order quantity
    allocated_pieces INTEGER NOT NULL DEFAULT 0,   -- Pieces allocated to lots
    remaining_pieces INTEGER NOT NULL DEFAULT 0,   -- Pieces not yet allocated
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    -- Constraint: remaining_pieces = total_pieces - allocated_pieces
    CONSTRAINT check_remaining_pieces CHECK (remaining_pieces = total_pieces - allocated_pieces)
);
```

---

## 🔄 **Business Process Flow**

### **1. Order Creation**
```
Order Created → Order Items Created → Order Item Status Initialized
```

**Example:**
- Order: 10 units, 2 designs (D001, D002), 3 ground colors (aa, a, aaa)
- Creates 6 status entries (2 designs × 3 colors)
- Each status entry: total_pieces = 10, allocated_pieces = 0, remaining_pieces = 10

### **2. Lot Creation & Allocation**
```
Select Available Items → Create Lot → Allocate Pieces → Update Status
```

**Example Lot Creation:**
```json
{
  "party_id": 5,
  "quality_id": 3,
  "allocations": [
    {
      "order_id": 17,
      "design_number": "D001",
      "ground_color_name": "aa",
      "beam_color_id": 8,
      "allocated_pieces": 5
    },
    {
      "order_id": 17,
      "design_number": "D002", 
      "ground_color_name": "a",
      "beam_color_id": 6,
      "allocated_pieces": 3
    }
  ]
}
```

### **3. Automatic Updates**
```
Lot Allocation → Triggers → Update order_item_status → Recalculate remaining_pieces
```

---

## 📈 **Reports Generated**

### **1. Partywise Detail (Red Book)**

**API Endpoint:** `GET /lots/reports/partywise-detail?party_id={id}`

**Data Structure:**
```
Date | Des No. | Quality | Units (pcs) | Rate | Lot no. | Lot Date | Bill no. | Actual pcs | Delivery Date
```

**Data Sources:**
- **Date:** Order date from orders table
- **Des No.:** Design number from order_item_status
- **Quality:** Quality name from qualities table
- **Units (pcs):** remaining_pieces from order_item_status
- **Rate:** rate_per_piece from orders table
- **Lot no.:** lot_number from lot_register (if allocated)
- **Lot Date:** lot_date from lot_register
- **Bill no.:** bill_number from lot_register (manually entered)
- **Actual pcs:** actual_pieces from lot_register (manually entered)
- **Delivery Date:** delivery_date from lot_register (manually entered)

### **2. Lot Register**

**API Endpoint:** `GET /lots/reports/lot-register`

**Data Structure:**
```
Lot Date | Lot no. | Party name | Design no. | Quality | Total pieces | Bill no. | Actual pieces | Delivery date
```

**Data Sources:**
- **Lot Date:** Automatic when entry is made
- **Lot no.:** Manually entered (or auto-generated)
- **Party name:** From orders table
- **Design no.:** From orders table
- **Quality:** From orders table
- **Total pieces:** Sum of allocated_pieces for the lot
- **Bill no.:** Manually entered
- **Actual pieces:** Manually entered
- **Delivery date:** Manually entered

---

## 🔧 **API Endpoints**

### **Core Lot Management:**
```
POST   /lots                          # Create lot with allocations
GET    /lots/{id}                     # Get lot details
GET    /lots                          # List all lots (paginated)
PUT    /lots/{id}                     # Update lot
DELETE /lots/{id}                     # Delete lot
```

### **Reports:**
```
GET    /lots/reports/partywise-detail # Partywise detail (red book)
GET    /lots/reports/lot-register     # Lot register
GET    /lots/reports/beam-summary-allocation # Beam summary with allocation
```

### **Allocation Management:**
```
GET    /lots/allocation/status        # Order allocation status
GET    /lots/allocation/available     # Available items for allocation
POST   /lots/allocation/initialize/{order_id} # Initialize order status
```

---

## 💡 **Example Usage Scenarios**

### **Scenario 1: Create Lot for Sheetal Creation**

**Initial Order:**
- Party: Sheetal Creation
- Quality: 4 feeder 60/700
- Units: 10 per design per color
- Designs: D001, D002
- Colors: aa (Yellow), a (White), aaa (Yellow)
- Total: 60 pieces

**Create Lot L001 for 30 pieces:**
```json
POST /lots
{
  "party_id": 5,
  "quality_id": 3,
  "allocations": [
    {"order_id": 17, "design_number": "D001", "ground_color_name": "aa", "beam_color_id": 8, "allocated_pieces": 10},
    {"order_id": 17, "design_number": "D002", "ground_color_name": "aa", "beam_color_id": 8, "allocated_pieces": 10},
    {"order_id": 17, "design_number": "D001", "ground_color_name": "a", "beam_color_id": 6, "allocated_pieces": 10}
  ]
}
```

**Result:**
- Lot L001 created with 30 pieces total
- Order remaining: 30 pieces (60 - 30)
- Beam summary updated to show remaining quantities

### **Scenario 2: View Partywise Detail**

**Request:**
```
GET /lots/reports/partywise-detail?party_id=5
```

**Response:**
```json
{
  "parties": [
    {
      "party_name": "Sheetal Creation",
      "items": [
        {
          "date": "2025-09-11",
          "des_no": "D001", 
          "quality": "4 feeder 60/700",
          "units_pcs": 0,
          "rate": 100.00,
          "lot_no": "L001",
          "lot_no_date": "2025-09-11",
          "bill_no": null,
          "actual_pcs": null,
          "delivery_date": null
        },
        {
          "date": "2025-09-11",
          "des_no": "D002",
          "quality": "4 feeder 60/700", 
          "units_pcs": 10,
          "rate": 100.00,
          "lot_no": null,
          "lot_no_date": null,
          "bill_no": null,
          "actual_pcs": null,
          "delivery_date": null
        }
      ],
      "total_remaining_pieces": 30,
      "total_allocated_pieces": 30,
      "total_value": 3000.00
    }
  ]
}
```

---

## 🔄 **Quantity Reduction Logic**

### **Automatic Updates via Database Triggers:**

1. **When lot allocation is created/updated:**
   ```sql
   UPDATE order_item_status 
   SET allocated_pieces = (SELECT SUM(allocated_pieces) FROM lot_allocations WHERE ...),
       remaining_pieces = total_pieces - allocated_pieces
   ```

2. **Beam Summary automatically reflects:**
   - **Total Pieces:** Original order quantities
   - **Allocated Pieces:** Pieces assigned to lots
   - **Remaining Pieces:** Available for future allocation

### **Real-time Updates:**
- Order table shows remaining quantities
- Beam allocation table shows only unallocated items
- Partywise detail shows both allocated and remaining items

---

## 🎯 **Key Features Implemented**

### ✅ **Complete Lot Management System:**
1. **Lot Creation** with multiple order allocations
2. **Automatic Lot Numbering** (L001, L002, etc.)
3. **Status Tracking** (PENDING → IN_PROGRESS → COMPLETED → DELIVERED)
4. **Manual Fields** (Bill number, Actual pieces, Delivery date)

### ✅ **Partywise Detail (Red Book):**
1. **Order-based tracking** with lot allocation status
2. **Remaining quantity tracking**
3. **Party-wise grouping** and totals
4. **Integration** with lot information

### ✅ **Lot Register:**
1. **Design-wise entries** for each lot
2. **Automatic and manual fields** as specified
3. **Production tracking** capabilities
4. **Delivery management**

### ✅ **Quantity Reduction:**
1. **Real-time updates** when lots are created
2. **Automatic recalculation** of remaining quantities
3. **Beam summary updates** to reflect allocations
4. **Data consistency** through database constraints

### ✅ **Advanced Features:**
1. **Allocation validation** (prevent over-allocation)
2. **Available items tracking** for lot creation
3. **Comprehensive reporting** with pagination
4. **Status management** throughout the process

---

## 🚀 **Next Steps**

The lot allocation system is now fully implemented and ready for use. The system provides:

1. **Complete order-to-delivery tracking**
2. **Automated quantity management**
3. **Professional reporting capabilities**
4. **Real-time inventory updates**
5. **Scalable architecture** for future enhancements

**Ready for frontend integration and testing!** 🎉
