"""
Database configuration and connection management
Layer 4: Infrastructure Layer
"""

from datetime import datetime
from typing import Optional

import pytz
from supabase import Client, create_client

from config.settings import settings


class SupabaseDB:
    def __init__(self):
        self.client: Optional[Client] = None

    async def connect(self):
        """Initialize Supabase client connection"""
        try:
            self.client = create_client(
                supabase_url=settings.SUPABASE_URL,
                supabase_key=settings.SUPABASE_ANON_KEY,
            )
            print("Supabase client connected successfully")
        except Exception as e:
            print(f"Failed to connect to Supabase: {str(e)}")
            raise

    async def get_client(self) -> Client:
        """Get Supabase client instance"""
        if not self.client:
            raise Exception("Supabase client is not connected")
        return self.client

    async def disconnect(self):
        """Close database connection"""
        try:
            if self.client:
                # Supabase client doesn't need explicit closing
                self.client = None
                print("Database connection closed")
        except Exception as e:
            print(f"Error closing database connection: {e}")


# Global database instance
database = SupabaseDB()


async def get_supabase_client() -> Client:
    """Get Supabase client instance"""
    return await database.get_client()


def get_ist_timestamp() -> str:
    """Get current timestamp in IST format"""
    ist = pytz.timezone("Asia/Kolkata")
    now = datetime.now(ist)
    return now.strftime("%Y-%m-%d %H:%M:%S")


def get_ist_datetime() -> datetime:
    """Get current datetime in IST timezone"""
    ist = pytz.timezone("Asia/Kolkata")
    return datetime.now(ist)
