"""
Pydantic models for Delhi Land Records MVP
Defines data structures for properties, search filters, and API responses
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import date, datetime
from enum import Enum


class LocalityEnum(str, Enum):
    """Valid localities for MVP scope"""
    GK_I = "Greater Kailash I"
    GK_II = "Greater Kailash II"
    GK_III = "Greater Kailash III"
    CR_PARK = "Chitranjan Park"


class EncumbranceStatus(str, Enum):
    """Property encumbrance status"""
    CLEAR = "Clear"
    MORTGAGED = "Mortgaged"
    DISPUTED = "Disputed"
    UNKNOWN = "Unknown"


class PropertyType(str, Enum):
    """Type of property"""
    RESIDENTIAL = "Residential"
    COMMERCIAL = "Commercial"
    MIXED_USE = "Mixed-use"


class DataSource(str, Enum):
    """Source of property data"""
    MANUAL_ENTRY = "Manual Entry"
    PUBLIC_LISTING = "Public Listing"
    CROWDSOURCED = "Crowdsourced"
    MANUAL_PORTAL_QUERY = "Manual Portal Query"
    USER_CONTRIBUTED = "User Contributed"


class VerificationLevel(str, Enum):
    """Data verification confidence level"""
    VERIFIED = "Official portal verified"
    CROWDSOURCED = "Community contributed"
    ESTIMATED = "Based on similar properties"
    UNVERIFIED = "Not yet verified"


# Base property model
class PropertyBase(BaseModel):
    """Base property information"""
    plot_number: str = Field(..., description="Plot/house number")
    locality: LocalityEnum = Field(..., description="Locality in Delhi")
    khasra_number: Optional[str] = Field(None, description="Land parcel ID from revenue records")
    area_sqm: float = Field(..., gt=0, description="Property area in square meters")
    owner_name: Optional[str] = Field(None, description="Owner name (anonymized)")
    registration_date: Optional[date] = Field(None, description="Original registration date")
    last_transaction_date: Optional[date] = Field(None, description="Most recent transaction date")
    encumbrance_status: EncumbranceStatus = Field(..., description="Legal encumbrance status")
    property_type: PropertyType = Field(..., description="Type of property")
    market_value_estimate: Optional[float] = Field(None, ge=0, description="Estimated market value in INR")
    data_source: DataSource = Field(..., description="Source of this data")
    last_verified: date = Field(..., description="Date when data was last verified")

    @validator('last_transaction_date')
    def transaction_date_not_before_registration(cls, v, values):
        """Ensure transaction date is not before registration date"""
        if v and 'registration_date' in values and values['registration_date']:
            if v < values['registration_date']:
                raise ValueError('Last transaction date cannot be before registration date')
        return v

    class Config:
        use_enum_values = True


class PropertyCreate(PropertyBase):
    """Model for creating a new property"""
    pass


class PropertyUpdate(BaseModel):
    """Model for updating property (all fields optional)"""
    plot_number: Optional[str] = None
    locality: Optional[LocalityEnum] = None
    khasra_number: Optional[str] = None
    area_sqm: Optional[float] = Field(None, gt=0)
    owner_name: Optional[str] = None
    registration_date: Optional[date] = None
    last_transaction_date: Optional[date] = None
    encumbrance_status: Optional[EncumbranceStatus] = None
    property_type: Optional[PropertyType] = None
    market_value_estimate: Optional[float] = Field(None, ge=0)
    data_source: Optional[DataSource] = None
    last_verified: Optional[date] = None

    class Config:
        use_enum_values = True


class Property(PropertyBase):
    """Full property model with database ID"""
    id: int = Field(..., description="Unique property ID")
    created_at: datetime = Field(..., description="Record creation timestamp")

    class Config:
        from_attributes = True
        use_enum_values = True


class PropertyDetail(Property):
    """Extended property details including additional information"""
    additional_details: Optional[Dict[str, Any]] = Field(None, description="Additional property details")
    verification_level: VerificationLevel = Field(VerificationLevel.UNVERIFIED, description="Verification confidence")

    class Config:
        from_attributes = True
        use_enum_values = True


# Search and filter models
class PropertySearchFilters(BaseModel):
    """Filters for property search"""
    locality: Optional[LocalityEnum] = None
    plot_number: Optional[str] = None
    khasra_number: Optional[str] = None
    min_area: Optional[float] = Field(None, ge=0)
    max_area: Optional[float] = Field(None, ge=0)
    min_price: Optional[float] = Field(None, ge=0)
    max_price: Optional[float] = Field(None, ge=0)
    encumbrance_status: Optional[EncumbranceStatus] = None
    property_type: Optional[PropertyType] = None
    verified_after: Optional[date] = None

    @validator('max_area')
    def max_area_greater_than_min(cls, v, values):
        """Ensure max_area > min_area"""
        if v and 'min_area' in values and values['min_area']:
            if v < values['min_area']:
                raise ValueError('max_area must be greater than min_area')
        return v

    @validator('max_price')
    def max_price_greater_than_min(cls, v, values):
        """Ensure max_price > min_price"""
        if v and 'min_price' in values and values['min_price']:
            if v < values['min_price']:
                raise ValueError('max_price must be greater than min_price')
        return v

    class Config:
        use_enum_values = True


class PropertySearchResponse(BaseModel):
    """Response for property search"""
    total: int = Field(..., description="Total number of matching properties")
    page: int = Field(..., ge=1, description="Current page number")
    page_size: int = Field(..., ge=1, le=100, description="Number of results per page")
    properties: List[Property] = Field(..., description="List of properties")


# Comparison models
class PropertyComparisonRequest(BaseModel):
    """Request to compare multiple properties"""
    property_ids: List[int] = Field(..., min_items=2, max_items=4, description="Property IDs to compare (2-4)")


class PropertyComparison(BaseModel):
    """Comparison result for multiple properties"""
    properties: List[Property] = Field(..., description="Properties being compared")
    comparison_matrix: Dict[str, List[Any]] = Field(..., description="Side-by-side comparison")
    insights: List[str] = Field(..., description="Key insights from comparison")


# Statistics models
class LocalityStatistics(BaseModel):
    """Aggregate statistics for a locality"""
    locality: LocalityEnum
    total_properties: int = Field(..., ge=0)
    avg_area_sqm: Optional[float] = Field(None, ge=0)
    avg_price_per_sqm: Optional[float] = Field(None, ge=0)
    median_price: Optional[float] = Field(None, ge=0)
    encumbrance_distribution: Dict[str, int] = Field(..., description="Count by encumbrance status")
    property_type_distribution: Dict[str, int] = Field(..., description="Count by property type")
    recent_transactions_count: int = Field(..., ge=0, description="Transactions in last 6 months")
    last_updated: datetime

    class Config:
        use_enum_values = True


# Export models
class ExportFormat(str, Enum):
    """Supported export formats"""
    JSON = "json"
    CSV = "csv"
    PDF = "pdf"


class PropertyExportRequest(BaseModel):
    """Request to export property data"""
    property_id: int
    format: ExportFormat = ExportFormat.JSON
    include_additional_details: bool = True


class ComparisonExportRequest(BaseModel):
    """Request to export property comparison"""
    property_ids: List[int] = Field(..., min_items=2, max_items=4)
    format: ExportFormat = ExportFormat.PDF


# Health check and metadata models
class HealthCheckResponse(BaseModel):
    """Health check response"""
    status: str = Field(..., description="Service health status")
    records_count: int = Field(..., ge=0, description="Total records in database")
    timestamp: datetime


class MetadataResponse(BaseModel):
    """API metadata response"""
    localities: List[str] = Field(..., description="Supported localities")
    total_records: int = Field(..., ge=0, description="Total properties in database")
    last_updated: Optional[datetime] = Field(None, description="Last database update")
    data_sources: List[str] = Field(..., description="Available data sources")
    encumbrance_statuses: List[str] = Field(..., description="Possible encumbrance statuses")
    property_types: List[str] = Field(..., description="Supported property types")


# Error response model
class ErrorResponse(BaseModel):
    """Standard error response"""
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    timestamp: datetime = Field(default_factory=datetime.now)


# Validation result model
class ValidationResult(BaseModel):
    """Result of data validation"""
    is_valid: bool
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
