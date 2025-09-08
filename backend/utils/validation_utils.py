"""
Validation utilities for data validation
"""

import re


def validate_party_data(data: dict, is_update: bool = False) -> dict:
    """Validate party data"""
    validated = {}

    # Party name validation
    if "party_name" in data:
        party_name = data["party_name"].strip() if data["party_name"] else ""
        if not party_name:
            raise ValueError("Party name is required")
        if len(party_name) < 2:
            raise ValueError("Party name must be at least 2 characters")
        validated["party_name"] = party_name.title()
    elif not is_update:
        raise ValueError("Party name is required")

    # Contact number validation (10 digits only)
    if "contact_number" in data:
        contact = data["contact_number"].strip() if data["contact_number"] else ""
        if not contact:
            if not is_update:
                raise ValueError("Contact number is required")
        else:
            # Remove all non-digits
            clean_contact = re.sub(r"\D", "", contact)
            if len(clean_contact) != 10 or not clean_contact.startswith(
                ("6", "7", "8", "9")
            ):
                raise ValueError(
                    "Contact number must be a valid 10-digit Indian mobile number"
                )
            validated["contact_number"] = clean_contact

    # Optional fields
    if "broker_name" in data and data["broker_name"]:
        validated["broker_name"] = data["broker_name"].strip().title()

    if "gst" in data and data["gst"]:
        gst = validate_gst_format(data["gst"])
        validated["gst"] = gst

    if "address" in data and data["address"]:
        validated["address"] = data["address"].strip()

    return validated


def validate_gst_format(gst: str) -> str:
    """Validate GST format"""
    if not gst:
        return None

    gst_clean = gst.replace(" ", "").upper()

    # GST format: 22AAAAA0000A1Z5 (15 characters)
    gst_pattern = r"^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$"

    if not re.match(gst_pattern, gst_clean):
        raise ValueError("Invalid GST format")

    return gst_clean
