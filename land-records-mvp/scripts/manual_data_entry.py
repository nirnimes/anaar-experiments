#!/usr/bin/env python3
"""
Manual Data Entry Tool for Delhi Land Records MVP
Interactive CLI for entering property records one at a time
"""

import sqlite3
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Optional


# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from api.models import (
    LocalityEnum,
    EncumbranceStatus,
    PropertyType,
    DataSource,
)


class PropertyDataEntry:
    """Interactive property data entry system"""

    def __init__(self, db_path: str = "database/land_records.db"):
        self.db_path = db_path
        self.conn = None

    def connect(self):
        """Connect to database"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        return self.conn

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()

    def get_input(self, prompt: str, required: bool = True, default: Optional[str] = None) -> Optional[str]:
        """Get user input with validation"""
        while True:
            if default:
                value = input(f"{prompt} [{default}]: ").strip()
                if not value:
                    return default
            else:
                value = input(f"{prompt}: ").strip()

            if value or not required:
                return value if value else None

            if required:
                print("❌ This field is required. Please enter a value.")

    def get_choice(self, prompt: str, choices: list, required: bool = True) -> Optional[str]:
        """Get user choice from a list of options"""
        print(f"\n{prompt}")
        for i, choice in enumerate(choices, 1):
            print(f"  {i}. {choice}")

        while True:
            choice_input = input(f"Enter choice (1-{len(choices)}): ").strip()

            if not choice_input and not required:
                return None

            try:
                choice_num = int(choice_input)
                if 1 <= choice_num <= len(choices):
                    return choices[choice_num - 1]
                else:
                    print(f"❌ Please enter a number between 1 and {len(choices)}")
            except ValueError:
                print("❌ Please enter a valid number")

    def get_date(self, prompt: str, required: bool = True) -> Optional[date]:
        """Get date input from user"""
        while True:
            date_str = self.get_input(prompt + " (YYYY-MM-DD)", required=required)

            if not date_str:
                return None

            try:
                return datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                print("❌ Invalid date format. Please use YYYY-MM-DD (e.g., 2024-01-15)")

    def get_float(self, prompt: str, required: bool = True, min_value: float = 0) -> Optional[float]:
        """Get float input from user"""
        while True:
            value_str = self.get_input(prompt, required=required)

            if not value_str:
                return None

            try:
                value = float(value_str)
                if value >= min_value:
                    return value
                else:
                    print(f"❌ Value must be at least {min_value}")
            except ValueError:
                print("❌ Please enter a valid number")

    def check_duplicate(self, plot_number: str, locality: str) -> bool:
        """Check if property already exists"""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT id FROM properties WHERE plot_number = ? AND locality = ?",
            (plot_number, locality)
        )
        result = cursor.fetchone()
        return result is not None

    def enter_property(self):
        """Interactive property entry"""
        print("\n" + "="*60)
        print("         PROPERTY DATA ENTRY")
        print("="*60)

        # Basic information
        print("\n📍 BASIC INFORMATION")
        plot_number = self.get_input("Plot/House Number", required=True)

        locality_choices = [e.value for e in LocalityEnum]
        locality = self.get_choice("Select Locality", locality_choices, required=True)

        # Check for duplicate
        if self.check_duplicate(plot_number, locality):
            print(f"\n⚠️  WARNING: Property '{plot_number}' in '{locality}' already exists!")
            confirm = input("Do you want to continue anyway? (yes/no): ").strip().lower()
            if confirm != 'yes':
                print("❌ Entry cancelled.")
                return False

        khasra_number = self.get_input("Khasra Number (Land Parcel ID)", required=False)

        # Area and ownership
        print("\n📏 PROPERTY DETAILS")
        area_sqm = self.get_float("Area (in square meters)", required=True, min_value=0.1)
        owner_name = self.get_input("Owner Name (or 'Anonymous')", required=False, default="Anonymous")

        # Dates
        print("\n📅 DATES")
        registration_date = self.get_date("Registration Date", required=False)
        last_transaction_date = self.get_date("Last Transaction Date", required=False)

        # Validate dates
        if registration_date and last_transaction_date:
            if last_transaction_date < registration_date:
                print("❌ Last transaction date cannot be before registration date!")
                return False

        # Legal status
        print("\n⚖️  LEGAL STATUS")
        encumbrance_choices = [e.value for e in EncumbranceStatus]
        encumbrance_status = self.get_choice("Encumbrance Status", encumbrance_choices, required=True)

        property_type_choices = [e.value for e in PropertyType]
        property_type = self.get_choice("Property Type", property_type_choices, required=True)

        # Valuation
        print("\n💰 VALUATION")
        market_value = self.get_float("Estimated Market Value (INR)", required=False, min_value=0)

        # Metadata
        print("\n📊 METADATA")
        data_source_choices = [e.value for e in DataSource]
        data_source = self.get_choice("Data Source", data_source_choices, required=True)

        last_verified = self.get_date("Last Verified Date", required=True)
        if not last_verified:
            last_verified = date.today()

        # Summary
        print("\n" + "="*60)
        print("SUMMARY")
        print("="*60)
        print(f"Plot Number:         {plot_number}")
        print(f"Locality:            {locality}")
        print(f"Khasra Number:       {khasra_number or 'N/A'}")
        print(f"Area:                {area_sqm} sqm")
        print(f"Owner:               {owner_name or 'N/A'}")
        print(f"Registration Date:   {registration_date or 'N/A'}")
        print(f"Last Transaction:    {last_transaction_date or 'N/A'}")
        print(f"Encumbrance Status:  {encumbrance_status}")
        print(f"Property Type:       {property_type}")
        print(f"Market Value:        ₹{market_value:,.2f}" if market_value else "N/A")
        print(f"Data Source:         {data_source}")
        print(f"Last Verified:       {last_verified}")
        print("="*60)

        # Confirmation
        confirm = input("\n✅ Save this property? (yes/no): ").strip().lower()
        if confirm != 'yes':
            print("❌ Entry cancelled.")
            return False

        # Insert into database
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO properties (
                    plot_number, locality, khasra_number, area_sqm, owner_name,
                    registration_date, last_transaction_date, encumbrance_status,
                    property_type, market_value_estimate, data_source, last_verified
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                plot_number, locality, khasra_number, area_sqm, owner_name,
                registration_date, last_transaction_date, encumbrance_status,
                property_type, market_value, data_source, last_verified
            ))
            self.conn.commit()
            property_id = cursor.lastrowid
            print(f"\n✅ Property saved successfully! (ID: {property_id})")
            return True

        except sqlite3.IntegrityError as e:
            print(f"\n❌ Database error: {e}")
            return False
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
            return False

    def run(self):
        """Main entry loop"""
        try:
            self.connect()
            print("\n🏠 Delhi Land Records - Manual Data Entry Tool")
            print("=" * 60)

            while True:
                success = self.enter_property()

                print("\n")
                continue_input = input("Enter another property? (yes/no): ").strip().lower()
                if continue_input != 'yes':
                    break

            print("\n👋 Thank you for using the data entry tool!")

        except KeyboardInterrupt:
            print("\n\n⚠️  Entry cancelled by user.")
        finally:
            self.close()


def main():
    """Main entry point"""
    # Check if database exists
    db_path = Path("database/land_records.db")
    if not db_path.exists():
        print("❌ Database not found. Please run database setup first.")
        print("   Run: sqlite3 database/land_records.db < database/schema.sql")
        sys.exit(1)

    entry_tool = PropertyDataEntry(str(db_path))
    entry_tool.run()


if __name__ == "__main__":
    main()
