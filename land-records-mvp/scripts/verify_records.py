#!/usr/bin/env python3
"""
Record Verification Tool for Delhi Land Records MVP
Check for incomplete records, data quality issues, and flag records needing updates
"""

import sqlite3
import sys
from datetime import date, timedelta
from pathlib import Path
from typing import List, Dict, Tuple
from collections import defaultdict


class RecordVerifier:
    """Tool for verifying data quality and completeness"""

    def __init__(self, db_path: str = "database/land_records.db"):
        self.db_path = db_path
        self.conn = None
        self.issues: Dict[str, List[str]] = defaultdict(list)

    def connect(self):
        """Connect to database"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        return self.conn

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()

    def check_missing_fields(self):
        """Check for properties with missing optional but important fields"""
        cursor = self.conn.cursor()

        # Missing khasra number
        cursor.execute("""
            SELECT id, plot_number, locality
            FROM properties
            WHERE khasra_number IS NULL OR khasra_number = ''
        """)
        missing_khasra = cursor.fetchall()
        if missing_khasra:
            self.issues['Missing Khasra Number'].extend([
                f"ID {row['id']}: {row['plot_number']}, {row['locality']}"
                for row in missing_khasra
            ])

        # Missing owner name
        cursor.execute("""
            SELECT id, plot_number, locality
            FROM properties
            WHERE owner_name IS NULL OR owner_name = '' OR owner_name = 'Anonymous'
        """)
        missing_owner = cursor.fetchall()
        if missing_owner:
            self.issues['Missing/Anonymous Owner'].extend([
                f"ID {row['id']}: {row['plot_number']}, {row['locality']}"
                for row in missing_owner
            ])

        # Missing registration date
        cursor.execute("""
            SELECT id, plot_number, locality
            FROM properties
            WHERE registration_date IS NULL
        """)
        missing_reg_date = cursor.fetchall()
        if missing_reg_date:
            self.issues['Missing Registration Date'].extend([
                f"ID {row['id']}: {row['plot_number']}, {row['locality']}"
                for row in missing_reg_date
            ])

        # Missing market value
        cursor.execute("""
            SELECT id, plot_number, locality
            FROM properties
            WHERE market_value_estimate IS NULL OR market_value_estimate = 0
        """)
        missing_value = cursor.fetchall()
        if missing_value:
            self.issues['Missing Market Value'].extend([
                f"ID {row['id']}: {row['plot_number']}, {row['locality']}"
                for row in missing_value
            ])

    def check_outdated_records(self):
        """Check for records that need re-verification"""
        cursor = self.conn.cursor()

        # Records older than 3 months
        three_months_ago = date.today() - timedelta(days=90)
        cursor.execute("""
            SELECT id, plot_number, locality, last_verified
            FROM properties
            WHERE last_verified < ?
        """, (three_months_ago,))

        outdated = cursor.fetchall()
        if outdated:
            self.issues['Needs Re-verification (>3 months)'].extend([
                f"ID {row['id']}: {row['plot_number']}, {row['locality']} "
                f"(last verified: {row['last_verified']})"
                for row in outdated
            ])

        # Records older than 6 months
        six_months_ago = date.today() - timedelta(days=180)
        cursor.execute("""
            SELECT id, plot_number, locality, last_verified
            FROM properties
            WHERE last_verified < ?
        """, (six_months_ago,))

        very_outdated = cursor.fetchall()
        if very_outdated:
            self.issues['URGENT: Re-verification Required (>6 months)'].extend([
                f"ID {row['id']}: {row['plot_number']}, {row['locality']} "
                f"(last verified: {row['last_verified']})"
                for row in very_outdated
            ])

    def check_data_anomalies(self):
        """Check for suspicious or unusual data"""
        cursor = self.conn.cursor()

        # Unusually small properties (< 50 sqm)
        cursor.execute("""
            SELECT id, plot_number, locality, area_sqm
            FROM properties
            WHERE area_sqm < 50
        """)
        small_properties = cursor.fetchall()
        if small_properties:
            self.issues['Unusually Small Area (<50 sqm)'].extend([
                f"ID {row['id']}: {row['plot_number']}, {row['locality']} ({row['area_sqm']} sqm)"
                for row in small_properties
            ])

        # Unusually large properties (> 2000 sqm)
        cursor.execute("""
            SELECT id, plot_number, locality, area_sqm
            FROM properties
            WHERE area_sqm > 2000
        """)
        large_properties = cursor.fetchall()
        if large_properties:
            self.issues['Unusually Large Area (>2000 sqm)'].extend([
                f"ID {row['id']}: {row['plot_number']}, {row['locality']} ({row['area_sqm']} sqm)"
                for row in large_properties
            ])

        # Very high price per sqm (potential error)
        cursor.execute("""
            SELECT id, plot_number, locality, area_sqm, market_value_estimate,
                   (market_value_estimate / area_sqm) as price_per_sqm
            FROM properties
            WHERE market_value_estimate IS NOT NULL
              AND market_value_estimate > 0
              AND (market_value_estimate / area_sqm) > 200000
        """)
        high_price = cursor.fetchall()
        if high_price:
            self.issues['Very High Price per Sqm (>₹2L)'].extend([
                f"ID {row['id']}: {row['plot_number']}, {row['locality']} "
                f"(₹{row['price_per_sqm']:,.0f}/sqm)"
                for row in high_price
            ])

        # Very low price per sqm (potential error)
        cursor.execute("""
            SELECT id, plot_number, locality, area_sqm, market_value_estimate,
                   (market_value_estimate / area_sqm) as price_per_sqm
            FROM properties
            WHERE market_value_estimate IS NOT NULL
              AND market_value_estimate > 0
              AND (market_value_estimate / area_sqm) < 30000
        """)
        low_price = cursor.fetchall()
        if low_price:
            self.issues['Very Low Price per Sqm (<₹30K)'].extend([
                f"ID {row['id']}: {row['plot_number']}, {row['locality']} "
                f"(₹{row['price_per_sqm']:,.0f}/sqm)"
                for row in low_price
            ])

        # Old transactions (last transaction > 10 years ago)
        ten_years_ago = date.today() - timedelta(days=3650)
        cursor.execute("""
            SELECT id, plot_number, locality, last_transaction_date
            FROM properties
            WHERE last_transaction_date IS NOT NULL
              AND last_transaction_date < ?
        """, (ten_years_ago,))
        old_transactions = cursor.fetchall()
        if old_transactions:
            self.issues['No Recent Transactions (>10 years)'].extend([
                f"ID {row['id']}: {row['plot_number']}, {row['locality']} "
                f"(last: {row['last_transaction_date']})"
                for row in old_transactions
            ])

    def check_data_consistency(self):
        """Check for data consistency issues"""
        cursor = self.conn.cursor()

        # Transaction date before registration
        cursor.execute("""
            SELECT id, plot_number, locality, registration_date, last_transaction_date
            FROM properties
            WHERE registration_date IS NOT NULL
              AND last_transaction_date IS NOT NULL
              AND last_transaction_date < registration_date
        """)
        invalid_dates = cursor.fetchall()
        if invalid_dates:
            self.issues['Invalid Date Order (Transaction < Registration)'].extend([
                f"ID {row['id']}: {row['plot_number']}, {row['locality']} "
                f"(reg: {row['registration_date']}, trans: {row['last_transaction_date']})"
                for row in invalid_dates
            ])

        # Future dates
        cursor.execute("""
            SELECT id, plot_number, locality, registration_date
            FROM properties
            WHERE registration_date IS NOT NULL
              AND registration_date > date('now')
        """)
        future_reg = cursor.fetchall()
        if future_reg:
            self.issues['Future Registration Date'].extend([
                f"ID {row['id']}: {row['plot_number']}, {row['locality']} "
                f"({row['registration_date']})"
                for row in future_reg
            ])

        cursor.execute("""
            SELECT id, plot_number, locality, last_transaction_date
            FROM properties
            WHERE last_transaction_date IS NOT NULL
              AND last_transaction_date > date('now')
        """)
        future_trans = cursor.fetchall()
        if future_trans:
            self.issues['Future Transaction Date'].extend([
                f"ID {row['id']}: {row['plot_number']}, {row['locality']} "
                f"({row['last_transaction_date']})"
                for row in future_trans
            ])

    def check_duplicate_plots(self):
        """Check for potential duplicate entries"""
        cursor = self.conn.cursor()

        cursor.execute("""
            SELECT plot_number, locality, COUNT(*) as count
            FROM properties
            GROUP BY plot_number, locality
            HAVING count > 1
        """)
        duplicates = cursor.fetchall()
        if duplicates:
            self.issues['Duplicate Plot Numbers'].extend([
                f"{row['plot_number']}, {row['locality']} ({row['count']} entries)"
                for row in duplicates
            ])

    def get_statistics(self) -> Dict[str, any]:
        """Get database statistics"""
        cursor = self.conn.cursor()

        stats = {}

        # Total properties
        cursor.execute("SELECT COUNT(*) as count FROM properties")
        stats['total_properties'] = cursor.fetchone()['count']

        # By locality
        cursor.execute("""
            SELECT locality, COUNT(*) as count
            FROM properties
            GROUP BY locality
            ORDER BY locality
        """)
        stats['by_locality'] = {row['locality']: row['count'] for row in cursor.fetchall()}

        # By encumbrance status
        cursor.execute("""
            SELECT encumbrance_status, COUNT(*) as count
            FROM properties
            GROUP BY encumbrance_status
            ORDER BY encumbrance_status
        """)
        stats['by_encumbrance'] = {row['encumbrance_status']: row['count'] for row in cursor.fetchall()}

        # By property type
        cursor.execute("""
            SELECT property_type, COUNT(*) as count
            FROM properties
            GROUP BY property_type
            ORDER BY property_type
        """)
        stats['by_type'] = {row['property_type']: row['count'] for row in cursor.fetchall()}

        # By data source
        cursor.execute("""
            SELECT data_source, COUNT(*) as count
            FROM properties
            GROUP BY data_source
            ORDER BY data_source
        """)
        stats['by_source'] = {row['data_source']: row['count'] for row in cursor.fetchall()}

        # Data completeness
        cursor.execute("""
            SELECT
                COUNT(*) as total,
                SUM(CASE WHEN khasra_number IS NOT NULL AND khasra_number != '' THEN 1 ELSE 0 END) as has_khasra,
                SUM(CASE WHEN owner_name IS NOT NULL AND owner_name != '' AND owner_name != 'Anonymous' THEN 1 ELSE 0 END) as has_owner,
                SUM(CASE WHEN registration_date IS NOT NULL THEN 1 ELSE 0 END) as has_reg_date,
                SUM(CASE WHEN market_value_estimate IS NOT NULL AND market_value_estimate > 0 THEN 1 ELSE 0 END) as has_value
            FROM properties
        """)
        completeness = cursor.fetchone()
        total = completeness['total']
        stats['completeness'] = {
            'khasra_number': f"{completeness['has_khasra']}/{total} ({100*completeness['has_khasra']//total if total > 0 else 0}%)",
            'owner_name': f"{completeness['has_owner']}/{total} ({100*completeness['has_owner']//total if total > 0 else 0}%)",
            'registration_date': f"{completeness['has_reg_date']}/{total} ({100*completeness['has_reg_date']//total if total > 0 else 0}%)",
            'market_value': f"{completeness['has_value']}/{total} ({100*completeness['has_value']//total if total > 0 else 0}%)",
        }

        return stats

    def run_verification(self, verbose: bool = True):
        """Run all verification checks"""
        print("\n🔍 Running Data Verification...")
        print("=" * 60)

        self.check_missing_fields()
        self.check_outdated_records()
        self.check_data_anomalies()
        self.check_data_consistency()
        self.check_duplicate_plots()

        # Print results
        print("\n📊 VERIFICATION RESULTS")
        print("=" * 60)

        if not self.issues:
            print("✅ No issues found! All records look good.")
        else:
            total_issues = sum(len(issues) for issues in self.issues.values())
            print(f"⚠️  Found {total_issues} potential issues across {len(self.issues)} categories:\n")

            for category, items in self.issues.items():
                print(f"\n{category} ({len(items)}):")
                if verbose:
                    for item in items[:5]:  # Show first 5
                        print(f"  • {item}")
                    if len(items) > 5:
                        print(f"  ... and {len(items) - 5} more")
                else:
                    print(f"  {len(items)} issues")

        # Print statistics
        print("\n\n📈 DATABASE STATISTICS")
        print("=" * 60)

        stats = self.get_statistics()

        print(f"\nTotal Properties: {stats['total_properties']}")

        print("\nBy Locality:")
        for locality, count in stats['by_locality'].items():
            print(f"  {locality}: {count}")

        print("\nBy Encumbrance Status:")
        for status, count in stats['by_encumbrance'].items():
            print(f"  {status}: {count}")

        print("\nBy Property Type:")
        for ptype, count in stats['by_type'].items():
            print(f"  {ptype}: {count}")

        print("\nBy Data Source:")
        for source, count in stats['by_source'].items():
            print(f"  {source}: {count}")

        print("\nData Completeness:")
        for field, completion in stats['completeness'].items():
            print(f"  {field}: {completion}")

        print("\n" + "=" * 60)

        return len(self.issues) == 0


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='Verify property records quality')
    parser.add_argument('--db', default='database/land_records.db', help='Database path')
    parser.add_argument('--summary', action='store_true', help='Show summary only (not verbose)')

    args = parser.parse_args()

    # Check if database exists
    db_path = Path(args.db)
    if not db_path.exists():
        print("❌ Database not found. Please run database setup first.")
        sys.exit(1)

    # Run verification
    verifier = RecordVerifier(str(db_path))
    try:
        verifier.connect()
        success = verifier.run_verification(verbose=not args.summary)
        sys.exit(0 if success else 1)
    finally:
        verifier.close()


if __name__ == "__main__":
    main()
