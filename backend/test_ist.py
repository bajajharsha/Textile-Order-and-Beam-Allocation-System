"""
Test IST timestamp functionality
"""

from config.database import get_ist_datetime, get_ist_timestamp


def test_ist_timestamps():
    """Test IST timestamp functions"""
    print("Testing IST Timestamps:")
    print(f"IST Timestamp (string): {get_ist_timestamp()}")
    print(f"IST Datetime (object): {get_ist_datetime()}")
    print(f"IST Timezone: {get_ist_datetime().tzinfo}")


if __name__ == "__main__":
    test_ist_timestamps()
