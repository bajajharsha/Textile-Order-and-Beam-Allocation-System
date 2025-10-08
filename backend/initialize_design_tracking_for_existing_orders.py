"""
Initialize design tracking for existing orders that don't have it yet
Run this ONCE to backfill design tracking data
"""

import asyncio

from config.database import database, get_ist_timestamp


async def initialize_design_tracking():
    await database.connect()
    client = await database.get_client()

    print("=" * 60)
    print("INITIALIZING DESIGN TRACKING FOR EXISTING ORDERS")
    print("=" * 60)

    # Get all orders
    orders_result = client.table("orders").select("id, sets").execute()
    orders = orders_result.data

    print(f"\nFound {len(orders)} orders")

    # Get all order items to extract designs and beam config
    items_result = client.table("order_items").select("*").execute()
    items = items_result.data

    # Group items by order_id
    orders_dict = {}
    for item in items:
        order_id = item["order_id"]
        if order_id not in orders_dict:
            orders_dict[order_id] = {"designs": set(), "beam_config": {}}

        design = item["design_number"]
        beam_id = item["beam_color_id"]

        # Split if comma-separated (e.g., "A1,A2" -> ["A1", "A2"])
        design_list = []
        if "," in design:
            design_list = [d.strip() for d in design.split(",")]
        else:
            design_list = [design]

        # Add all designs and their beam configs
        for d in design_list:
            orders_dict[order_id]["designs"].add(d)

            # Track beam colors per design
            if d not in orders_dict[order_id]["beam_config"]:
                orders_dict[order_id]["beam_config"][d] = {}

            if beam_id in orders_dict[order_id]["beam_config"][d]:
                orders_dict[order_id]["beam_config"][d][beam_id] += 1
            else:
                orders_dict[order_id]["beam_config"][d][beam_id] = 1

    # Get sets for each order
    sets_dict = {o["id"]: o["sets"] for o in orders}

    # Create design tracking entries
    for order_id, data in orders_dict.items():
        sets = sets_dict.get(order_id, 0)

        print(f"\n📦 Order {order_id}: {sets} sets, {len(data['designs'])} designs")

        for design in data["designs"]:
            # Check if already exists
            existing = (
                client.table("design_set_tracking")
                .select("*")
                .eq("order_id", order_id)
                .eq("design_number", design)
                .execute()
            )

            if existing.data:
                print(f"  ⏭️  Design {design} already has tracking, skipping")
                continue

            # Create design set tracking
            tracking_data = {
                "order_id": order_id,
                "design_number": design,
                "total_sets": sets,
                "allocated_sets": 0,
                "remaining_sets": sets,
                "is_active": True,
                "created_at": get_ist_timestamp(),
                "updated_at": get_ist_timestamp(),
            }

            result = client.table("design_set_tracking").insert(tracking_data).execute()
            print(f"  ✅ Created tracking for design {design}: {sets} sets")

            # Create beam configurations
            if design in data["beam_config"]:
                for beam_id, multiplier in data["beam_config"][design].items():
                    beam_data = {
                        "order_id": order_id,
                        "design_number": design,
                        "beam_color_id": beam_id,
                        "beam_multiplier": multiplier,
                        "is_active": True,
                        "created_at": get_ist_timestamp(),
                    }

                    client.table("design_beam_config").insert(beam_data).execute()
                    print(f"     🎨 Beam config: Color {beam_id} × {multiplier}")

    print("\n" + "=" * 60)
    print("✅ INITIALIZATION COMPLETE!")
    print("=" * 60)

    # Verify
    tracking_count = len(client.table("design_set_tracking").select("*").execute().data)
    beam_count = len(client.table("design_beam_config").select("*").execute().data)

    print("\n📊 Summary:")
    print(f"  - Design Set Tracking entries: {tracking_count}")
    print(f"  - Design Beam Config entries: {beam_count}")


asyncio.run(initialize_design_tracking())
