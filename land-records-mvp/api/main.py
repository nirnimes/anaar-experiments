"""
FastAPI application for Delhi Land Records MVP
REST API for property search, comparison, and statistics
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from typing import List, Optional
from datetime import datetime
import os

from .models import (
    Property,
    PropertyCreate,
    PropertySearchFilters,
    PropertySearchResponse,
    PropertyComparisonRequest,
    PropertyComparison,
    LocalityStatistics,
    HealthCheckResponse,
    MetadataResponse,
    ErrorResponse,
    LocalityEnum,
    EncumbranceStatus,
    PropertyType,
    DataSource,
)
from .database import get_database


# Initialize FastAPI app
app = FastAPI(
    title="Delhi Land Records MVP",
    description="API for searching and comparing property records in Greater Kailash and Chitranjan Park",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get database instance
db = get_database()


# Error handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="InternalServerError",
            message=str(exc),
            timestamp=datetime.now()
        ).model_dump()
    )


# Health check and metadata endpoints
@app.get("/api/health", response_model=HealthCheckResponse, tags=["System"])
async def health_check():
    """
    Health check endpoint
    Returns system status and record count
    """
    try:
        records_count = db.get_total_count()
        return HealthCheckResponse(
            status="healthy",
            records_count=records_count,
            timestamp=datetime.now()
        )
    except Exception as e:
        return HealthCheckResponse(
            status=f"unhealthy: {str(e)}",
            records_count=0,
            timestamp=datetime.now()
        )


@app.get("/api/metadata", response_model=MetadataResponse, tags=["System"])
async def get_metadata():
    """
    Get API metadata
    Returns supported localities, statuses, types, and database info
    """
    return MetadataResponse(
        localities=[e.value for e in LocalityEnum],
        total_records=db.get_total_count(),
        last_updated=db.get_last_update_time(),
        data_sources=[e.value for e in DataSource],
        encumbrance_statuses=[e.value for e in EncumbranceStatus],
        property_types=[e.value for e in PropertyType]
    )


# Property CRUD endpoints
@app.post("/api/properties", response_model=Property, status_code=201, tags=["Properties"])
async def create_property(property_data: PropertyCreate):
    """
    Create a new property record
    Requires all mandatory fields
    """
    try:
        property_obj = db.create_property(property_data)
        return property_obj
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/properties/{property_id}", response_model=Property, tags=["Properties"])
async def get_property(property_id: int):
    """
    Get detailed property information by ID
    Returns full property record including all fields
    """
    property_obj = db.get_property_by_id(property_id)
    if not property_obj:
        raise HTTPException(status_code=404, detail=f"Property {property_id} not found")
    return property_obj


# Search endpoint
@app.get("/api/properties/search", response_model=PropertySearchResponse, tags=["Search"])
async def search_properties(
    locality: Optional[str] = Query(None, description="Filter by locality"),
    plot_number: Optional[str] = Query(None, description="Search by plot number (partial match)"),
    khasra_number: Optional[str] = Query(None, description="Search by khasra number (partial match)"),
    min_area: Optional[float] = Query(None, ge=0, description="Minimum area in sqm"),
    max_area: Optional[float] = Query(None, ge=0, description="Maximum area in sqm"),
    min_price: Optional[float] = Query(None, ge=0, description="Minimum market value"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum market value"),
    encumbrance_status: Optional[str] = Query(None, description="Filter by encumbrance status"),
    property_type: Optional[str] = Query(None, description="Filter by property type"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Results per page")
):
    """
    Search properties with filters

    All filters are optional. Results are paginated.
    Returns matching properties sorted by last verified date.
    """
    try:
        filters = PropertySearchFilters(
            locality=locality,
            plot_number=plot_number,
            khasra_number=khasra_number,
            min_area=min_area,
            max_area=max_area,
            min_price=min_price,
            max_price=max_price,
            encumbrance_status=encumbrance_status,
            property_type=property_type
        )

        properties, total = db.search_properties(filters, page, page_size)

        return PropertySearchResponse(
            total=total,
            page=page,
            page_size=page_size,
            properties=properties
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# Full-text search
@app.get("/api/properties/search/fulltext", response_model=List[Property], tags=["Search"])
async def fulltext_search(
    q: str = Query(..., min_length=2, description="Search query"),
    limit: int = Query(20, ge=1, le=100, description="Maximum results")
):
    """
    Full-text search across all property fields
    Searches plot numbers, localities, khasra numbers, and owner names
    """
    try:
        properties = db.full_text_search(q, limit)
        return properties
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Comparison endpoint
@app.post("/api/properties/compare", response_model=PropertyComparison, tags=["Comparison"])
async def compare_properties(request: PropertyComparisonRequest):
    """
    Compare 2-4 properties side by side
    Returns structured comparison with insights
    """
    if len(request.property_ids) < 2 or len(request.property_ids) > 4:
        raise HTTPException(
            status_code=400,
            detail="Please provide between 2 and 4 property IDs for comparison"
        )

    properties = db.get_properties_by_ids(request.property_ids)

    if len(properties) != len(request.property_ids):
        found_ids = {p.id for p in properties}
        missing_ids = set(request.property_ids) - found_ids
        raise HTTPException(
            status_code=404,
            detail=f"Properties not found: {missing_ids}"
        )

    # Build comparison matrix
    comparison_matrix = {
        "plot_number": [p.plot_number for p in properties],
        "locality": [p.locality for p in properties],
        "area_sqm": [p.area_sqm for p in properties],
        "encumbrance_status": [p.encumbrance_status for p in properties],
        "property_type": [p.property_type for p in properties],
        "market_value_estimate": [p.market_value_estimate for p in properties],
        "price_per_sqm": [
            p.market_value_estimate / p.area_sqm if p.market_value_estimate else None
            for p in properties
        ],
        "registration_date": [p.registration_date for p in properties],
        "last_transaction_date": [p.last_transaction_date for p in properties],
        "last_verified": [p.last_verified for p in properties],
    }

    # Generate insights
    insights = []

    # Area comparison
    areas = [p.area_sqm for p in properties]
    max_area_idx = areas.index(max(areas))
    min_area_idx = areas.index(min(areas))
    if max_area_idx != min_area_idx:
        insights.append(
            f"{properties[max_area_idx].plot_number} is the largest "
            f"({properties[max_area_idx].area_sqm:.1f} sqm), "
            f"{properties[min_area_idx].plot_number} is the smallest "
            f"({properties[min_area_idx].area_sqm:.1f} sqm)"
        )

    # Price comparison
    prices = [p.market_value_estimate for p in properties if p.market_value_estimate]
    if len(prices) >= 2:
        max_price = max(prices)
        min_price = min(prices)
        insights.append(
            f"Price range: ₹{min_price:,.0f} to ₹{max_price:,.0f} "
            f"(difference: ₹{max_price - min_price:,.0f})"
        )

    # Encumbrance status
    clear_count = sum(1 for p in properties if p.encumbrance_status == "Clear")
    if clear_count > 0:
        insights.append(f"{clear_count} out of {len(properties)} properties have clear title")

    # Price per sqm comparison
    price_per_sqm = [
        (p.market_value_estimate / p.area_sqm, p.plot_number)
        for p in properties if p.market_value_estimate
    ]
    if len(price_per_sqm) >= 2:
        price_per_sqm.sort()
        insights.append(
            f"Best value: {price_per_sqm[0][1]} at ₹{price_per_sqm[0][0]:,.0f}/sqm, "
            f"Most expensive: {price_per_sqm[-1][1]} at ₹{price_per_sqm[-1][0]:,.0f}/sqm"
        )

    return PropertyComparison(
        properties=properties,
        comparison_matrix=comparison_matrix,
        insights=insights
    )


# Statistics endpoint
@app.get("/api/statistics/locality/{locality}", response_model=LocalityStatistics, tags=["Statistics"])
async def get_locality_statistics(locality: str):
    """
    Get aggregate statistics for a locality

    Returns:
    - Average property size
    - Average and median price per sqm
    - Encumbrance distribution
    - Property type distribution
    - Recent transaction count
    """
    try:
        # Validate locality
        try:
            locality_enum = LocalityEnum(locality)
        except ValueError:
            valid_localities = [e.value for e in LocalityEnum]
            raise HTTPException(
                status_code=400,
                detail=f"Invalid locality. Must be one of: {', '.join(valid_localities)}"
            )

        stats = db.get_locality_statistics(locality_enum)
        return LocalityStatistics(**stats)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Summary statistics endpoint
@app.get("/api/statistics/summary", tags=["Statistics"])
async def get_summary_statistics():
    """
    Get summary statistics across all localities
    """
    try:
        summary = {}
        for locality in LocalityEnum:
            stats = db.get_locality_statistics(locality)
            summary[locality.value] = {
                "total_properties": stats["total_properties"],
                "avg_price_per_sqm": stats["avg_price_per_sqm"],
                "clear_title_percentage": (
                    100 * stats["encumbrance_distribution"].get("Clear", 0) / stats["total_properties"]
                    if stats["total_properties"] > 0 else 0
                )
            }
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Serve frontend static files
# Check if frontend directory exists
frontend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
if os.path.exists(frontend_dir):
    app.mount("/static", StaticFiles(directory=os.path.join(frontend_dir, "static")), name="static")

    @app.get("/", tags=["Frontend"])
    async def serve_index():
        """Serve the main frontend page"""
        index_path = os.path.join(frontend_dir, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
        return {"message": "Frontend not yet built"}

    @app.get("/search", tags=["Frontend"])
    async def serve_search():
        """Serve search page"""
        search_path = os.path.join(frontend_dir, "search.html")
        if os.path.exists(search_path):
            return FileResponse(search_path)
        return {"message": "Search page not yet built"}

    @app.get("/property/{property_id}", tags=["Frontend"])
    async def serve_property_detail(property_id: int):
        """Serve property detail page"""
        detail_path = os.path.join(frontend_dir, "property.html")
        if os.path.exists(detail_path):
            return FileResponse(detail_path)
        return {"message": "Property detail page not yet built"}

    @app.get("/compare", tags=["Frontend"])
    async def serve_compare():
        """Serve comparison page"""
        compare_path = os.path.join(frontend_dir, "compare.html")
        if os.path.exists(compare_path):
            return FileResponse(compare_path)
        return {"message": "Compare page not yet built"}

    @app.get("/about", tags=["Frontend"])
    async def serve_about():
        """Serve about page"""
        about_path = os.path.join(frontend_dir, "about.html")
        if os.path.exists(about_path):
            return FileResponse(about_path)
        return {"message": "About page not yet built"}


# Root API endpoint
@app.get("/api", tags=["System"])
async def api_root():
    """API root endpoint with links to documentation"""
    return {
        "message": "Delhi Land Records MVP API",
        "version": "1.0.0",
        "documentation": "/api/docs",
        "health": "/api/health",
        "metadata": "/api/metadata"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
