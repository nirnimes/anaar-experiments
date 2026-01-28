#!/usr/bin/env python3
"""
CSV Import Tool for Delhi Land Records MVP
Bulk import property records from CSV files
"""

import sqlite3
import csv
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple


# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from api.models import (
    LocalityEnum,
    EncumbranceStatus,
    PropertyType,
    DataSource,
)


class CSVImporter:
    """CSV import tool with validation and error handling"""

    REQUIRED_FIELDS = [
        'plot_number',
        'locality',
        'area_sqm',
        'encumbrance_status',
        'property_type',
        'data_source',
        'last_verified'
    ]

    OPTIONAL_FIELDS = [
        'khasra_number',
        'owner_name',
        'registration_date',
        'last_transaction_date',
        'market_value_estimate'
    ]

    VALID_LOCALITIES = {e.value for e in LocalityEnum}
    VALID_ENCUMBRANCE = {e.value for e in EncumbranceStatus}
    VALID_PROPERTY_TYPES = {e.value for e in PropertyType}
    VALID_DATA_SOURCES = {e.value for e in DataSource}

    def __init__(self, db_path: str = "database/land_records.db"):
        self.db_path = db_path
        self.conn = None
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.imported_count = 0
        self.skipped_count = 0

    def connect(self):
        """Connect to database"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        return self.conn

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()

    def validate_row(self, row: Dict, row_num: int) -> Tuple[bool, List[str]]:
        """Validate a single row"""
        errors = []

        # Check required fields
        for field in self.REQUIRED_FIELDS:
            if field not in row or not row[field].strip():
                errors.append(f"Row {row_num}: Missing required field '{field}'")

        if errors:
            return False, errors

        # Validate locality
        if row['locality'] not in self.VALID_LOCALITIES:
            errors.append(f"Row {row_num}: Invalid locality '{row['locality']}'. "
                         f"Must be one of: {', '.join(self.VALID_LOCALITIES)}")

        # Validate encumbrance status
        if row['encumbrance_status'] not in self.VALID_ENCUMBRANCE:
            errors.append(f"Row {row_num}: Invalid encumbrance status '{row['encumbrance_status']}'. "
                         f"Must be one of: {', '.join(self.VALID_ENCUMBRANCE)}")

        # Validate property type
        if row['property_type'] not in self.VALID_PROPERTY_TYPES:
            errors.append(f"Row {row_num}: Invalid property type '{row['property_type']}'. "
                         f"Must be one of: {', '.join(self.VALID_PROPERTY_TYPES)}")

        # Validate data source
        if row['data_source'] not in self.VALID_DATA_SOURCES:
            errors.append(f"Row {row_num}: Invalid data source '{row['data_source']}'. "
                         f"Must be one of: {', '.join(self.VALID_DATA_SOURCES)}")

        # Validate area
        try:
            area = float(row['area_sqm'])
            if area <= 0:
                errors.append(f"Row {row_num}: Area must be greater than 0")
        except ValueError:
            errors.append(f"Row {row_num}: Invalid area value '{row['area_sqm']}'")

        # Validate market value if present
        if row.get('market_value_estimate', '').strip():
            try:
                value = float(row['market_value_estimate'])
                if value < 0:
                    errors.append(f"Row {row_num}: Market value cannot be negative")
            except ValueError:
                errors.append(f"Row {row_num}: Invalid market value '{row['market_value_estimate']}'")

        # Validate dates
        date_fields = ['registration_date', 'last_transaction_date', 'last_verified']
        for field in date_fields:
            if row.get(field, '').strip():
                try:
                    datetime.strptime(row[field], '%Y-%m-%d')
                except ValueError:
                    errors.append(f"Row {row_num}: Invalid date format for '{field}'. Use YYYY-MM-DD")

        # Validate transaction date is not before registration date
        if (row.get('registration_date', '').strip() and
            row.get('last_transaction_date', '').strip()):
            try:
                reg_date = datetime.strptime(row['registration_date'], '%Y-%m-%d')
                trans_date = datetime.strptime(row['last_transaction_date'], '%Y-%m-%d')
                if trans_date < reg_date:
                    errors.append(f"Row {row_num}: Last transaction date cannot be before registration date")
            except ValueError:
                pass  # Already caught above

        return len(errors) == 0, errors

    def check_duplicate(self, plot_number: str, locality: str) -> bool:
        """Check if property already exists"""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT id FROM properties WHERE plot_number = ? AND locality = ?",
            (plot_number, locality)
        )
        return cursor.fetchone() is not None

    def import_row(self, row: Dict, row_num: int, skip_duplicates: bool = True) -> bool:
        """Import a single row"""
        # Check for duplicates
        if self.check_duplicate(row['plot_number'], row['locality']):
            if skip_duplicates:
                self.warnings.append(f"Row {row_num}: Duplicate property '{row['plot_number']}' "
                                   f"in '{row['locality']}' - skipped")
                self.skipped_count += 1
                return False
            else:
                self.warnings.append(f"Row {row_num}: Updating existing property '{row['plot_number']}' "
                                   f"in '{row['locality']}'")
                # TODO: Implement update logic
                return False

        # Prepare data
        try:
            cursor = self.conn.cursor()

            # Convert empty strings to None
            def to_none_if_empty(value):
                return None if not value.strip() else value

            # Parse optional float fields
            market_value = None
            if row.get('market_value_estimate', '').strip():
                market_value = float(row['market_value_estimate'])

            # Parse optional date fields
            reg_date = to_none_if_empty(row.get('registration_date', ''))
            trans_date = to_none_if_empty(row.get('last_transaction_date', ''))

            cursor.execute("""
                INSERT INTO properties (
                    plot_number, locality, khasra_number, area_sqm, owner_name,
                    registration_date, last_transaction_date, encumbrance_status,
                    property_type, market_value_estimate, data_source, last_verified
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                row['plot_number'],
                row['locality'],
                to_none_if_empty(row.get('khasra_number', '')),
                float(row['area_sqm']),
                to_none_if_empty(row.get('owner_name', '')),
                reg_date,
                trans_date,
                row['encumbrance_status'],
                row['property_type'],
                market_value,
                row['data_source'],
                row['last_verified']
            ))

            self.imported_count += 1
            return True

        except Exception as e:
            self.errors.append(f"Row {row_num}: Database error - {str(e)}")
            return False

    def import_csv(self, csv_path: str, skip_duplicates: bool = True, dry_run: bool = False):
        """Import properties from CSV file"""
        print(f"\n📥 Importing from: {csv_path}")
        print("=" * 60)

        try:
            with open(csv_path, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)

                # Validate CSV headers
                if not reader.fieldnames:
                    print("❌ Error: Empty CSV file")
                    return False

                missing_fields = set(self.REQUIRED_FIELDS) - set(reader.fieldnames)
                if missing_fields:
                    print(f"❌ Error: Missing required columns: {', '.join(missing_fields)}")
                    return False

                print(f"✅ CSV headers validated")
                print(f"📋 Fields found: {', '.join(reader.fieldnames)}\n")

                if dry_run:
                    print("🔍 DRY RUN MODE - No data will be imported\n")

                # Process each row
                for row_num, row in enumerate(reader, start=2):  # Start at 2 (header is row 1)
                    # Validate row
                    is_valid, validation_errors = self.validate_row(row, row_num)

                    if not is_valid:
                        self.errors.extend(validation_errors)
                        continue

                    # Import row (if not dry run)
                    if not dry_run:
                        self.import_row(row, row_num, skip_duplicates)

                # Commit if successful and not dry run
                if not dry_run and self.imported_count > 0:
                    self.conn.commit()
                    print(f"\n✅ Import completed!")
                elif dry_run:
                    print(f"\n✅ Validation completed!")

                # Print summary
                print("\n" + "=" * 60)
                print("IMPORT SUMMARY")
                print("=" * 60)
                if not dry_run:
                    print(f"✅ Successfully imported: {self.imported_count} properties")
                    print(f"⚠️  Skipped (duplicates):  {self.skipped_count} properties")
                else:
                    total_valid = row_num - 1 - len(self.errors)
                    print(f"✅ Valid rows:            {total_valid}")

                print(f"❌ Errors:                {len(self.errors)}")
                print(f"⚠️  Warnings:              {len(self.warnings)}")
                print("=" * 60)

                # Display errors
                if self.errors:
                    print("\n❌ ERRORS:")
                    for error in self.errors[:10]:  # Show first 10 errors
                        print(f"   {error}")
                    if len(self.errors) > 10:
                        print(f"   ... and {len(self.errors) - 10} more errors")

                # Display warnings
                if self.warnings:
                    print("\n⚠️  WARNINGS:")
                    for warning in self.warnings[:10]:  # Show first 10 warnings
                        print(f"   {warning}")
                    if len(self.warnings) > 10:
                        print(f"   ... and {len(self.warnings) - 10} more warnings")

                return len(self.errors) == 0

        except FileNotFoundError:
            print(f"❌ Error: File not found '{csv_path}'")
            return False
        except csv.Error as e:
            print(f"❌ Error: CSV parsing error - {e}")
            return False
        except Exception as e:
            print(f"❌ Error: Unexpected error - {e}")
            return False


def create_sample_csv(output_path: str = "data/sample_import_template.csv"):
    """Create a sample CSV template for reference"""
    headers = [
        'plot_number', 'locality', 'khasra_number', 'area_sqm', 'owner_name',
        'registration_date', 'last_transaction_date', 'encumbrance_status',
        'property_type', 'market_value_estimate', 'data_source', 'last_verified'
    ]

    sample_data = [
        {
            'plot_number': 'A-123',
            'locality': 'Greater Kailash I',
            'khasra_number': '567/12',
            'area_sqm': '350.5',
            'owner_name': 'Sample Owner 1',
            'registration_date': '2015-03-15',
            'last_transaction_date': '2022-08-20',
            'encumbrance_status': 'Clear',
            'property_type': 'Residential',
            'market_value_estimate': '25000000',
            'data_source': 'Manual Entry',
            'last_verified': '2026-01-27'
        },
        {
            'plot_number': 'M-45',
            'locality': 'Greater Kailash II',
            'khasra_number': '234/8',
            'area_sqm': '500.0',
            'owner_name': '',
            'registration_date': '2010-06-12',
            'last_transaction_date': '2020-11-05',
            'encumbrance_status': 'Mortgaged',
            'property_type': 'Residential',
            'market_value_estimate': '40000000',
            'data_source': 'Public Listing',
            'last_verified': '2026-01-25'
        }
    ]

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        writer.writeheader()
        writer.writerows(sample_data)

    print(f"✅ Sample CSV template created: {output_path}")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='Import properties from CSV file')
    parser.add_argument('csv_file', nargs='?', help='Path to CSV file to import')
    parser.add_argument('--dry-run', action='store_true', help='Validate without importing')
    parser.add_argument('--update-duplicates', action='store_true', help='Update existing properties')
    parser.add_argument('--create-template', action='store_true', help='Create sample CSV template')
    parser.add_argument('--db', default='database/land_records.db', help='Database path')

    args = parser.parse_args()

    # Create template
    if args.create_template:
        create_sample_csv()
        return

    # Check if CSV file provided
    if not args.csv_file:
        parser.print_help()
        return

    # Check if database exists
    db_path = Path(args.db)
    if not db_path.exists():
        print("❌ Database not found. Please run database setup first.")
        print("   Run: sqlite3 database/land_records.db < database/schema.sql")
        sys.exit(1)

    # Run import
    importer = CSVImporter(str(db_path))
    try:
        importer.connect()
        success = importer.import_csv(
            args.csv_file,
            skip_duplicates=not args.update_duplicates,
            dry_run=args.dry_run
        )
        sys.exit(0 if success else 1)
    finally:
        importer.close()


if __name__ == "__main__":
    main()
