#!/usr/bin/env python3
"""
Script to clean up duplicate order items created by the old logic.
This script removes duplicate order items and keeps only one per ground color per order.
"""

import asyncio
import os
import sys

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.database import database


async def cleanup_duplicate_order_items():
    """Clean up duplicate order items"""
    client = await database.get_client()

    print("Starting cleanup of duplicate order items...")

    try:
        # Get all orders
        orders_result = (
            client.table("orders").select("id").eq("is_active", True).execute()
        )
        orders = orders_result.data

        print(f"Found {len(orders)} active orders to process...")

        for order in orders:
            order_id = order["id"]

            # Get all order items for this order
            items_result = (
                client.table("order_items")
                .select("*")
                .eq("order_id", order_id)
                .eq("is_active", True)
                .execute()
            )
            items = items_result.data

            if not items:
                continue

            print(f"Processing order {order_id} with {len(items)} items...")

            # Group items by ground_color_name and beam_color_id
            unique_items = {}
            items_to_deactivate = []

            for item in items:
                key = (item["ground_color_name"], item["beam_color_id"])

                if key in unique_items:
                    # This is a duplicate, mark for deactivation
                    items_to_deactivate.append(item["id"])
                    print(
                        f"  Found duplicate item: {item['design_number']} - {item['ground_color_name']} - beam_color_id: {item['beam_color_id']}"
                    )
                else:
                    # Keep this item and update design_number to "ALL"
                    unique_items[key] = item

                    # Update the design_number to comma-separated format if it's not already
                    if item["design_number"] == "ALL":
                        # For existing "ALL" entries, we'll keep them as is since we don't have the original design numbers
                        print(
                            f"  Keeping existing 'ALL' design_number: {item['ground_color_name']} - beam_color_id: {item['beam_color_id']}"
                        )

            # Deactivate duplicate items
            if items_to_deactivate:
                client.table("order_items").update({"is_active": False}).in_(
                    "id", items_to_deactivate
                ).execute()
                print(f"  Deactivated {len(items_to_deactivate)} duplicate items")

            print(
                f"  Order {order_id} cleanup complete. Kept {len(unique_items)} unique items."
            )

        print("Cleanup completed successfully!")

    except Exception as e:
        print(f"Error during cleanup: {str(e)}")
        raise


if __name__ == "__main__":
    asyncio.run(cleanup_duplicate_order_items())
