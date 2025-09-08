"""
Base repository for data access operations
Layer 3: Data Access Layer
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, List, Optional, Tuple, TypeVar

from config.database import get_supabase_client
from config.logging import get_logger
from supabase import Client

T = TypeVar("T")
logger = get_logger("repositories")


class BaseRepository(ABC, Generic[T]):
    """Base repository with common CRUD operations"""

    def __init__(self, table_name: str):
        self.table_name = table_name
        self.supabase: Client = get_supabase_client()
        self.logger = get_logger(f"repositories.{table_name}")

    async def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new record"""
        try:
            self.logger.info(f"Creating new record in {self.table_name}")

            # Add timestamps
            from datetime import datetime

            now = datetime.utcnow().isoformat()
            data.update({"created_at": now, "updated_at": now})

            result = self.supabase.table(self.table_name).insert(data).execute()

            if not result.data:
                raise ValueError("Failed to create record - no data returned")

            created_record = result.data[0]
            self.logger.info(
                f"Successfully created record with ID: {created_record.get('id')}"
            )

            return created_record

        except Exception as e:
            self.logger.error(f"Error creating record in {self.table_name}: {str(e)}")
            raise

    async def get_by_id(self, record_id: int) -> Optional[Dict[str, Any]]:
        """Get record by ID"""
        try:
            self.logger.debug(f"Fetching record {record_id} from {self.table_name}")

            result = (
                self.supabase.table(self.table_name)
                .select("*")
                .eq("id", record_id)
                .execute()
            )

            if not result.data:
                self.logger.debug(f"Record {record_id} not found in {self.table_name}")
                return None

            return result.data[0]

        except Exception as e:
            self.logger.error(
                f"Error fetching record {record_id} from {self.table_name}: {str(e)}"
            )
            raise

    async def get_all(
        self,
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[str] = None,
        order_desc: bool = False,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """Get all records with optional filtering and pagination"""
        try:
            self.logger.debug(
                f"Fetching records from {self.table_name} with filters: {filters}"
            )

            query = self.supabase.table(self.table_name).select("*")

            # Apply filters
            if filters:
                for key, value in filters.items():
                    if value is not None:
                        query = query.eq(key, value)

            # Apply ordering
            if order_by:
                query = query.order(order_by, desc=order_desc)
            else:
                query = query.order("created_at", desc=True)

            # Apply pagination
            if limit:
                query = query.limit(limit)

            if offset:
                query = query.offset(offset)

            result = query.execute()

            self.logger.debug(
                f"Found {len(result.data or [])} records in {self.table_name}"
            )

            return result.data or []

        except Exception as e:
            self.logger.error(
                f"Error fetching records from {self.table_name}: {str(e)}"
            )
            raise

    async def update(
        self, record_id: int, data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Update record by ID"""
        try:
            self.logger.info(f"Updating record {record_id} in {self.table_name}")

            # Add updated timestamp
            from datetime import datetime

            data["updated_at"] = datetime.utcnow().isoformat()

            result = (
                self.supabase.table(self.table_name)
                .update(data)
                .eq("id", record_id)
                .execute()
            )

            if not result.data:
                self.logger.warning(
                    f"No record updated for ID {record_id} in {self.table_name}"
                )
                return None

            updated_record = result.data[0]
            self.logger.info(
                f"Successfully updated record {record_id} in {self.table_name}"
            )

            return updated_record

        except Exception as e:
            self.logger.error(
                f"Error updating record {record_id} in {self.table_name}: {str(e)}"
            )
            raise

    async def delete(self, record_id: int, soft_delete: bool = True) -> bool:
        """Delete record by ID (soft delete by default)"""
        try:
            self.logger.info(
                f"Deleting record {record_id} from {self.table_name} (soft={soft_delete})"
            )

            if soft_delete and await self._has_is_active_field():
                # Soft delete - set is_active to False
                result = await self.update(record_id, {"is_active": False})
                success = result is not None
            else:
                # Hard delete
                result = (
                    self.supabase.table(self.table_name)
                    .delete()
                    .eq("id", record_id)
                    .execute()
                )
                success = len(result.data or []) > 0

            if success:
                self.logger.info(
                    f"Successfully deleted record {record_id} from {self.table_name}"
                )
            else:
                self.logger.warning(
                    f"No record deleted for ID {record_id} in {self.table_name}"
                )

            return success

        except Exception as e:
            self.logger.error(
                f"Error deleting record {record_id} from {self.table_name}: {str(e)}"
            )
            raise

    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count records with optional filters"""
        try:
            query = self.supabase.table(self.table_name).select("id", count="exact")

            if filters:
                for key, value in filters.items():
                    if value is not None:
                        query = query.eq(key, value)

            result = query.execute()
            return result.count or 0

        except Exception as e:
            self.logger.error(f"Error counting records in {self.table_name}: {str(e)}")
            raise

    async def exists(self, record_id: int) -> bool:
        """Check if record exists"""
        try:
            record = await self.get_by_id(record_id)
            return record is not None
        except Exception as e:
            self.logger.error(
                f"Error checking existence of record {record_id} in {self.table_name}: {str(e)}"
            )
            raise

    async def search(
        self,
        search_term: str,
        search_fields: List[str],
        filters: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """Search records in specified fields"""
        try:
            self.logger.debug(
                f"Searching '{search_term}' in {search_fields} within {self.table_name}"
            )

            query = self.supabase.table(self.table_name).select("*")

            # Apply text search using ilike (case-insensitive)
            if len(search_fields) == 1:
                query = query.ilike(search_fields[0], f"%{search_term}%")
            else:
                # For multiple fields, we'll need to use or conditions
                # This is a simplified version - complex OR queries might need raw SQL
                for field in search_fields:
                    query = query.ilike(field, f"%{search_term}%")

            # Apply additional filters
            if filters:
                for key, value in filters.items():
                    if value is not None:
                        query = query.eq(key, value)

            if limit:
                query = query.limit(limit)

            result = query.execute()

            self.logger.debug(
                f"Search found {len(result.data or [])} records in {self.table_name}"
            )

            return result.data or []

        except Exception as e:
            self.logger.error(f"Error searching in {self.table_name}: {str(e)}")
            raise

    async def get_paginated(
        self,
        page: int = 1,
        page_size: int = 20,
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[str] = None,
        order_desc: bool = False,
    ) -> Tuple[List[Dict[str, Any]], int]:
        """Get paginated records with total count"""
        try:
            # Calculate offset
            offset = (page - 1) * page_size

            # Get total count
            total_count = await self.count(filters)

            # Get paginated records
            records = await self.get_all(
                filters=filters,
                order_by=order_by,
                order_desc=order_desc,
                limit=page_size,
                offset=offset,
            )

            return records, total_count

        except Exception as e:
            self.logger.error(
                f"Error getting paginated records from {self.table_name}: {str(e)}"
            )
            raise

    async def _has_is_active_field(self) -> bool:
        """Check if table has is_active field for soft deletes"""
        try:
            # Try to get table structure (this is a simple check)
            # In a real scenario, you might want to cache this information
            result = (
                self.supabase.table(self.table_name)
                .select("is_active")
                .limit(1)
                .execute()
            )
            return True
        except:
            return False

    # Abstract methods for custom repository implementations
    @abstractmethod
    def _get_search_fields(self) -> List[str]:
        """Return list of fields that can be searched in this repository"""
        pass

    @abstractmethod
    def _get_default_order_field(self) -> str:
        """Return default field for ordering records"""
        pass
