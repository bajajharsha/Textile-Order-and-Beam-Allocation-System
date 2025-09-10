"""
Calculation service for beam allocation and order calculations
Layer 2: Business Logic Layer
"""

from decimal import Decimal
from typing import Any, Dict, List

from config.logging import get_logger


class CalculationService:
    """Service for handling all calculations related to orders and beams"""

    def __init__(self):
        self.logger = get_logger("services.calculation")

    def calculate_beam_pieces(
        self, pieces_per_color: int, designs_per_beam: int, total_designs: int
    ) -> int:
        """
        Calculate pieces for beam allocation
        Formula: pieces_per_color × designs_per_beam × total_designs
        """
        try:
            if pieces_per_color <= 0 or designs_per_beam <= 0 or total_designs <= 0:
                self.logger.warning(
                    f"Invalid calculation parameters: pieces={pieces_per_color}, "
                    f"designs_per_beam={designs_per_beam}, total_designs={total_designs}"
                )
                return 0

            calculated_pieces = pieces_per_color * designs_per_beam * total_designs

            self.logger.debug(
                f"Beam calculation: {pieces_per_color} × {designs_per_beam} × {total_designs} = {calculated_pieces}"
            )

            return calculated_pieces

        except Exception as e:
            self.logger.error(f"Error calculating beam pieces: {str(e)}")
            return 0

    def calculate_order_totals(
        self, order_items: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Calculate total pieces, designs, and value for an order
        """
        try:
            if not order_items:
                return {
                    "total_pieces": 0,
                    "total_designs": 0,
                    "total_value": Decimal("0"),
                }

            # Calculate total pieces
            total_pieces = sum(item.get("calculated_pieces", 0) for item in order_items)

            # Calculate total unique designs
            design_numbers = {
                item.get("design_number", "")
                for item in order_items
                if item.get("design_number")
            }
            total_designs = len(design_numbers)

            # Total value calculation (would need rate per piece from order)
            total_value = Decimal("0")  # This would be calculated with rate

            result = {
                "total_pieces": total_pieces,
                "total_designs": total_designs,
                "total_value": total_value,
            }

            self.logger.debug(f"Order totals calculated: {result}")

            return result

        except Exception as e:
            self.logger.error(f"Error calculating order totals: {str(e)}")
            return {"total_pieces": 0, "total_designs": 0, "total_value": Decimal("0")}

    def suggest_beam_color(self, ground_color_name: str) -> int:
        """
        Auto-suggest beam color based on ground color name
        Simple logic: suggest Red color (ID=1) as default
        Can be enhanced with business rules later
        """
        try:
            # Simple mapping based on color name keywords
            color_mapping = {
                "red": 1,  # Red
                "black": 2,  # Black
                "blue": 5,  # Royal Blue
                "green": 7,  # Green
                "white": 6,  # White
                "gold": 4,  # Gold
            }

            ground_color_lower = ground_color_name.lower()
            for keyword, color_id in color_mapping.items():
                if keyword in ground_color_lower:
                    return color_id

            # Default to Red if no match found
            suggested_color = 1  # Red

            self.logger.debug(
                f"Beam color suggestion: ground_color_name={ground_color_name} -> beam_color_id={suggested_color}"
            )

            return suggested_color

        except Exception as e:
            self.logger.error(f"Error suggesting beam color: {str(e)}")
            return 1  # Fallback to Red

    def generate_quality_wise_summary(
        self, orders_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate quality-wise beam summary for reporting
        """
        try:
            quality_summary = {}

            for order in orders_data:
                quality_name = order.get("quality_name", "Unknown")

                if quality_name not in quality_summary:
                    quality_summary[quality_name] = {
                        "quality_name": quality_name,
                        "total_orders": 0,
                        "beam_colors": {},
                        "total_pieces": 0,
                    }

                quality_summary[quality_name]["total_orders"] += 1

                for item in order.get("order_items", []):
                    beam_color_name = item.get("beam_color_name", "Unknown")
                    calculated_pieces = item.get("calculated_pieces", 0)

                    if (
                        beam_color_name
                        not in quality_summary[quality_name]["beam_colors"]
                    ):
                        quality_summary[quality_name]["beam_colors"][
                            beam_color_name
                        ] = {
                            "color_name": beam_color_name,
                            "total_pieces": 0,
                            "orders_count": 0,
                        }

                    quality_summary[quality_name]["beam_colors"][beam_color_name][
                        "total_pieces"
                    ] += calculated_pieces
                    quality_summary[quality_name]["beam_colors"][beam_color_name][
                        "orders_count"
                    ] += 1
                    quality_summary[quality_name]["total_pieces"] += calculated_pieces

            # Convert to list format for easier consumption
            formatted_summary = {
                "report_date": self._get_current_datetime_iso(),
                "qualities": [],
                "grand_total_pieces": 0,
                "grand_total_orders": 0,
            }

            for quality_name, quality_data in quality_summary.items():
                beam_colors = []
                for color_name, color_data in quality_data["beam_colors"].items():
                    beam_colors.append(
                        {
                            "color_name": color_name,
                            "total_pieces": color_data["total_pieces"],
                            "orders_count": color_data["orders_count"],
                        }
                    )

                # Sort beam colors by total pieces (descending)
                beam_colors.sort(key=lambda x: x["total_pieces"], reverse=True)

                quality_summary_item = {
                    "quality_name": quality_name,
                    "beam_colors": beam_colors,
                    "total_pieces": quality_data["total_pieces"],
                    "total_orders": quality_data["total_orders"],
                }

                formatted_summary["qualities"].append(quality_summary_item)
                formatted_summary["grand_total_pieces"] += quality_data["total_pieces"]
                formatted_summary["grand_total_orders"] += quality_data["total_orders"]

            # Sort qualities by total pieces (descending)
            formatted_summary["qualities"].sort(
                key=lambda x: x["total_pieces"], reverse=True
            )

            self.logger.info(
                f"Generated quality-wise summary: {len(formatted_summary['qualities'])} qualities, "
                f"{formatted_summary['grand_total_pieces']} total pieces"
            )

            return formatted_summary

        except Exception as e:
            self.logger.error(f"Error generating quality-wise summary: {str(e)}")
            return {
                "report_date": self._get_current_datetime_iso(),
                "qualities": [],
                "grand_total_pieces": 0,
                "grand_total_orders": 0,
            }

    def calculate_order_value(
        self, total_pieces: int, rate_per_piece: Decimal
    ) -> Decimal:
        """Calculate total order value"""
        try:
            if total_pieces <= 0 or rate_per_piece <= 0:
                return Decimal("0")

            total_value = Decimal(str(total_pieces)) * rate_per_piece

            self.logger.debug(
                f"Order value calculation: {total_pieces} × {rate_per_piece} = {total_value}"
            )

            return round(total_value, 2)

        except Exception as e:
            self.logger.error(f"Error calculating order value: {str(e)}")
            return Decimal("0")

    def validate_order_calculations(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate order calculations and return validation results"""
        try:
            validation_result = {"is_valid": True, "errors": [], "warnings": []}

            order_items = order_data.get("order_items", [])
            if not order_items:
                validation_result["is_valid"] = False
                validation_result["errors"].append("Order must have at least one item")
                return validation_result

            total_designs = order_data.get("total_designs", 0)
            if total_designs <= 0:
                validation_result["is_valid"] = False
                validation_result["errors"].append("Total designs must be positive")

            rate_per_piece = order_data.get("rate_per_piece", 0)
            if rate_per_piece <= 0:
                validation_result["is_valid"] = False
                validation_result["errors"].append("Rate per piece must be positive")

            # Validate each item
            for i, item in enumerate(order_items):
                pieces_per_color = item.get("pieces_per_color", 0)
                designs_per_beam = item.get("designs_per_beam", 0)

                if pieces_per_color <= 0:
                    validation_result["errors"].append(
                        f"Item {i + 1}: Pieces per color must be positive"
                    )
                    validation_result["is_valid"] = False

                if designs_per_beam <= 0:
                    validation_result["errors"].append(
                        f"Item {i + 1}: Designs per beam must be positive"
                    )
                    validation_result["is_valid"] = False

            # Add warnings for unusual values
            if rate_per_piece > 1000:
                validation_result["warnings"].append("Rate per piece seems very high")

            total_calculated_pieces = sum(
                self.calculate_beam_pieces(
                    item.get("pieces_per_color", 0),
                    item.get("designs_per_beam", 0),
                    total_designs,
                )
                for item in order_items
            )

            if total_calculated_pieces > 10000:
                validation_result["warnings"].append("Total pieces is very high")

            self.logger.debug(f"Order validation result: {validation_result}")

            return validation_result

        except Exception as e:
            self.logger.error(f"Error validating order calculations: {str(e)}")
            return {
                "is_valid": False,
                "errors": [f"Validation error: {str(e)}"],
                "warnings": [],
            }

    def generate_order_calculation_details(
        self, order_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate detailed calculation breakdown for each order item"""
        try:
            calculation_details = []

            order_items = order_data.get("order_items", [])
            total_designs = order_data.get("total_designs", 1)

            for item in order_items:
                pieces_per_color = item.get("pieces_per_color", 0)
                designs_per_beam = item.get("designs_per_beam", 1)
                calculated_pieces = self.calculate_beam_pieces(
                    pieces_per_color, designs_per_beam, total_designs
                )

                detail = {
                    "design_number": item.get("design_number", ""),
                    "ground_color_name": item.get("ground_color_name", "Unknown"),
                    "beam_color_name": item.get("beam_color_name", "Unknown"),
                    "pieces_per_color": pieces_per_color,
                    "designs_per_beam": designs_per_beam,
                    "total_designs": total_designs,
                    "calculated_pieces": calculated_pieces,
                    "formula": f"{pieces_per_color} × {designs_per_beam} × {total_designs} = {calculated_pieces}",
                }

                calculation_details.append(detail)

            self.logger.debug(
                f"Generated calculation details for {len(calculation_details)} items"
            )

            return calculation_details

        except Exception as e:
            self.logger.error(f"Error generating calculation details: {str(e)}")
            return []

    def _get_current_datetime_iso(self) -> str:
        """Get current datetime in ISO format"""
        from datetime import datetime

        return datetime.utcnow().isoformat()
