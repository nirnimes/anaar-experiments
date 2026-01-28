"""
Database connection and query functions for Delhi Land Records MVP
SQLite database operations with connection pooling
"""

import sqlite3
from contextlib import contextmanager
from typing import List, Optional, Dict, Any, Tuple
from datetime import date, datetime
from pathlib import Path

from .models import (
    Property,
    PropertyCreate,
    PropertySearchFilters,
    LocalityEnum,
    EncumbranceStatus,
    PropertyType,
)


class Database:
    """Database manager for land records"""

    def __init__(self, db_path: str = "database/land_records.db"):
        self.db_path = db_path
        self._ensure_database_exists()

    def _ensure_database_exists(self):
        """Ensure database file and schema exist"""
        db_file = Path(self.db_path)
        if not db_file.exists():
            # Create database directory if needed
            db_file.parent.mkdir(parents=True, exist_ok=True)

            # Initialize database with schema
            schema_file = db_file.parent / "schema.sql"
            if schema_file.exists():
                conn = sqlite3.connect(self.db_path)
                with open(schema_file, 'r') as f:
                    conn.executescript(f.read())
                conn.close()

    @contextmanager
    def get_connection(self):
        """Get database connection with context manager"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        try:
            yield conn
        finally:
            conn.close()

    def _row_to_property(self, row: sqlite3.Row) -> Property:
        """Convert database row to Property model"""
        return Property(
            id=row['id'],
            plot_number=row['plot_number'],
            locality=row['locality'],
            khasra_number=row['khasra_number'],
            area_sqm=row['area_sqm'],
            owner_name=row['owner_name'],
            registration_date=row['registration_date'],
            last_transaction_date=row['last_transaction_date'],
            encumbrance_status=row['encumbrance_status'],
            property_type=row['property_type'],
            market_value_estimate=row['market_value_estimate'],
            data_source=row['data_source'],
            last_verified=row['last_verified'],
            created_at=datetime.fromisoformat(row['created_at']) if isinstance(row['created_at'], str) else row['created_at']
        )

    def create_property(self, property_data: PropertyCreate) -> Property:
        """Create a new property record"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO properties (
                    plot_number, locality, khasra_number, area_sqm, owner_name,
                    registration_date, last_transaction_date, encumbrance_status,
                    property_type, market_value_estimate, data_source, last_verified
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                property_data.plot_number,
                property_data.locality,
                property_data.khasra_number,
                property_data.area_sqm,
                property_data.owner_name,
                property_data.registration_date,
                property_data.last_transaction_date,
                property_data.encumbrance_status,
                property_data.property_type,
                property_data.market_value_estimate,
                property_data.data_source,
                property_data.last_verified
            ))

            conn.commit()
            property_id = cursor.lastrowid

            # Fetch and return created property
            return self.get_property_by_id(property_id)

    def get_property_by_id(self, property_id: int) -> Optional[Property]:
        """Get property by ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM properties WHERE id = ?", (property_id,))
            row = cursor.fetchone()

            if row:
                return self._row_to_property(row)
            return None

    def search_properties(
        self,
        filters: PropertySearchFilters,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[Property], int]:
        """Search properties with filters and pagination"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Build WHERE clause
            where_clauses = []
            params = []

            if filters.locality:
                where_clauses.append("locality = ?")
                params.append(filters.locality)

            if filters.plot_number:
                where_clauses.append("plot_number LIKE ?")
                params.append(f"%{filters.plot_number}%")

            if filters.khasra_number:
                where_clauses.append("khasra_number LIKE ?")
                params.append(f"%{filters.khasra_number}%")

            if filters.min_area is not None:
                where_clauses.append("area_sqm >= ?")
                params.append(filters.min_area)

            if filters.max_area is not None:
                where_clauses.append("area_sqm <= ?")
                params.append(filters.max_area)

            if filters.min_price is not None:
                where_clauses.append("market_value_estimate >= ?")
                params.append(filters.min_price)

            if filters.max_price is not None:
                where_clauses.append("market_value_estimate <= ?")
                params.append(filters.max_price)

            if filters.encumbrance_status:
                where_clauses.append("encumbrance_status = ?")
                params.append(filters.encumbrance_status)

            if filters.property_type:
                where_clauses.append("property_type = ?")
                params.append(filters.property_type)

            if filters.verified_after:
                where_clauses.append("last_verified >= ?")
                params.append(filters.verified_after)

            where_clause = " AND ".join(where_clauses) if where_clauses else "1=1"

            # Get total count
            count_query = f"SELECT COUNT(*) as count FROM properties WHERE {where_clause}"
            cursor.execute(count_query, params)
            total = cursor.fetchone()['count']

            # Get paginated results
            offset = (page - 1) * page_size
            query = f"""
                SELECT * FROM properties
                WHERE {where_clause}
                ORDER BY last_verified DESC, created_at DESC
                LIMIT ? OFFSET ?
            """
            cursor.execute(query, params + [page_size, offset])

            properties = [self._row_to_property(row) for row in cursor.fetchall()]

            return properties, total

    def get_properties_by_ids(self, property_ids: List[int]) -> List[Property]:
        """Get multiple properties by IDs"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            placeholders = ','.join('?' * len(property_ids))
            query = f"SELECT * FROM properties WHERE id IN ({placeholders})"
            cursor.execute(query, property_ids)

            return [self._row_to_property(row) for row in cursor.fetchall()]

    def get_locality_statistics(self, locality: LocalityEnum) -> Dict[str, Any]:
        """Get statistics for a locality"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Basic stats
            cursor.execute("""
                SELECT
                    COUNT(*) as total_properties,
                    AVG(area_sqm) as avg_area_sqm,
                    AVG(CASE WHEN market_value_estimate > 0 THEN market_value_estimate / area_sqm END) as avg_price_per_sqm,
                    MIN(market_value_estimate) as min_price,
                    MAX(market_value_estimate) as max_price
                FROM properties
                WHERE locality = ? AND market_value_estimate IS NOT NULL
            """, (locality,))

            stats_row = cursor.fetchone()

            # Encumbrance distribution
            cursor.execute("""
                SELECT encumbrance_status, COUNT(*) as count
                FROM properties
                WHERE locality = ?
                GROUP BY encumbrance_status
            """, (locality,))

            encumbrance_dist = {row['encumbrance_status']: row['count'] for row in cursor.fetchall()}

            # Property type distribution
            cursor.execute("""
                SELECT property_type, COUNT(*) as count
                FROM properties
                WHERE locality = ?
                GROUP BY property_type
            """, (locality,))

            type_dist = {row['property_type']: row['count'] for row in cursor.fetchall()}

            # Recent transactions (last 6 months)
            cursor.execute("""
                SELECT COUNT(*) as count
                FROM properties
                WHERE locality = ?
                  AND last_transaction_date >= date('now', '-6 months')
            """, (locality,))

            recent_transactions = cursor.fetchone()['count']

            # Median price calculation
            cursor.execute("""
                SELECT market_value_estimate
                FROM properties
                WHERE locality = ? AND market_value_estimate IS NOT NULL
                ORDER BY market_value_estimate
            """, (locality,))

            prices = [row['market_value_estimate'] for row in cursor.fetchall()]
            median_price = None
            if prices:
                mid = len(prices) // 2
                median_price = prices[mid] if len(prices) % 2 else (prices[mid-1] + prices[mid]) / 2

            return {
                'locality': locality,
                'total_properties': stats_row['total_properties'],
                'avg_area_sqm': stats_row['avg_area_sqm'],
                'avg_price_per_sqm': stats_row['avg_price_per_sqm'],
                'median_price': median_price,
                'price_range': {
                    'min': stats_row['min_price'],
                    'max': stats_row['max_price']
                },
                'encumbrance_distribution': encumbrance_dist,
                'property_type_distribution': type_dist,
                'recent_transactions_count': recent_transactions,
                'last_updated': datetime.now()
            }

    def full_text_search(self, query: str, limit: int = 20) -> List[Property]:
        """Full-text search across properties"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT p.* FROM properties p
                JOIN properties_fts fts ON p.id = fts.rowid
                WHERE properties_fts MATCH ?
                LIMIT ?
            """, (query, limit))

            return [self._row_to_property(row) for row in cursor.fetchall()]

    def get_total_count(self) -> int:
        """Get total number of properties"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as count FROM properties")
            return cursor.fetchone()['count']

    def get_last_update_time(self) -> Optional[datetime]:
        """Get timestamp of most recent update"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT MAX(updated_at) as last_update FROM properties")
            result = cursor.fetchone()['last_update']

            if result:
                return datetime.fromisoformat(result) if isinstance(result, str) else result
            return None


# Singleton instance
_db_instance: Optional[Database] = None


def get_database() -> Database:
    """Get database singleton instance"""
    global _db_instance
    if _db_instance is None:
        _db_instance = Database()
    return _db_instance
