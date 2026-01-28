# Delhi Land Records MVP

A unified land records search interface for Greater Kailash (I, II, III) and Chitranjan Park areas in Delhi.

## Project Goal

This MVP validates whether a unified land records search interface adds value for property buyers in Delhi. It provides:

- Property search with advanced filters
- Encumbrance status checking
- Property comparison (up to 4 properties)
- Locality-wise statistics and analytics

## Features

- **Search**: Search properties by plot number, locality, area, price, and status
- **Compare**: Side-by-side comparison of up to 4 properties with insights
- **Statistics**: Locality-wise analytics including average prices and encumbrance rates
- **User-friendly**: Clean, responsive interface built with modern web technologies

## Tech Stack

### Backend
- **FastAPI**: Modern Python web framework
- **SQLite**: Lightweight database
- **Pydantic**: Data validation
- **Uvicorn**: ASGI server

### Frontend
- **HTML/CSS/JavaScript**: Pure vanilla JS (no framework overhead)
- **TailwindCSS**: Utility-first CSS framework
- **Responsive Design**: Mobile-friendly interface

## Project Structure

```
land-records-mvp/
├── api/                    # Backend API
│   ├── __init__.py
│   ├── main.py            # FastAPI application
│   ├── models.py          # Pydantic data models
│   └── database.py        # Database operations
├── database/              # Database files
│   ├── schema.sql         # Database schema
│   ├── seed_data.sql      # Sample data
│   └── land_records.db    # SQLite database
├── frontend/              # Frontend files
│   ├── index.html         # Home page
│   ├── search.html        # Search page
│   ├── about.html         # About page
│   └── static/
│       ├── css/           # Stylesheets
│       └── js/            # JavaScript
├── scripts/               # Utility scripts
│   ├── init_database.py   # Database initialization
│   ├── manual_data_entry.py  # Manual data entry tool
│   ├── import_csv.py      # CSV import tool
│   └── verify_records.py # Data verification tool
├── tests/                 # Unit tests
│   ├── __init__.py
│   └── test_api.py        # API tests
├── research/              # Research documentation
│   ├── delhi_portal_analysis.md
│   ├── sample_records.json
│   └── legal_considerations.md
├── docs/                  # Documentation
│   ├── API.md            # API documentation
│   └── USER_GUIDE.md     # User guide
├── requirements.txt       # Python dependencies
├── Procfile              # Deployment configuration
└── README.md             # This file
```

## Installation

### Prerequisites
- Python 3.11+
- pip

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd land-records-mvp
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize database**
   ```bash
   python scripts/init_database.py
   ```

5. **Run the application**
   ```bash
   uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
   ```

6. **Access the application**
   - Frontend: http://localhost:8000
   - API Documentation: http://localhost:8000/api/docs
   - API Alternative Docs: http://localhost:8000/api/redoc

## Usage

### Search Properties

Navigate to http://localhost:8000/search or use the search bar on the home page.

**Available Filters:**
- Locality (GK I/II/III, CR Park)
- Plot number (partial match)
- Area range (in sqm)
- Price range (in ₹)
- Encumbrance status (Clear/Mortgaged/Disputed/Unknown)
- Property type (Residential/Commercial/Mixed-use)

### Compare Properties

1. Search for properties
2. Select up to 4 properties using checkboxes
3. Click "Compare Selected"
4. View side-by-side comparison with insights

### View Statistics

Navigate to specific locality stats or view summary on the home page.

## Data Management

### Manual Data Entry

```bash
python scripts/manual_data_entry.py
```

Interactive CLI tool for entering property records one at a time.

### CSV Import

1. **Create CSV template**
   ```bash
   python scripts/import_csv.py --create-template
   ```

2. **Import data**
   ```bash
   python scripts/import_csv.py data/your_file.csv
   ```

3. **Dry run (validation only)**
   ```bash
   python scripts/import_csv.py data/your_file.csv --dry-run
   ```

### Data Verification

```bash
python scripts/verify_records.py
```

Checks for:
- Missing required fields
- Outdated records (>3 months)
- Data anomalies
- Consistency issues

## API Documentation

See [docs/API.md](docs/API.md) for detailed API documentation.

### Quick API Examples

**Search properties:**
```bash
curl "http://localhost:8000/api/properties/search?locality=Greater%20Kailash%20I"
```

**Get property details:**
```bash
curl "http://localhost:8000/api/properties/1"
```

**Compare properties:**
```bash
curl -X POST "http://localhost:8000/api/properties/compare" \
  -H "Content-Type: application/json" \
  -d '{"property_ids": [1, 2, 3]}'
```

**Get locality statistics:**
```bash
curl "http://localhost:8000/api/statistics/locality/Greater%20Kailash%20I"
```

## Testing

Run tests using pytest:

```bash
pytest tests/ -v
```

Run specific test file:
```bash
pytest tests/test_api.py -v
```

## Deployment

### Option 1: Railway.app / Render (Recommended for MVP)

1. Connect GitHub repository
2. Set environment variables (if needed)
3. Deploy automatically

Files included:
- `Procfile` - Deployment command
- `runtime.txt` - Python version
- `requirements.txt` - Dependencies

### Option 2: Docker (Future)

```dockerfile
# Dockerfile (to be created)
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Option 3: Traditional Server

```bash
# Using gunicorn for production
gunicorn api.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## Legal & Compliance

### Data Sources

This MVP uses data from:
- Manual entry from verified documents
- Public real estate listings
- User contributions (crowdsourced)
- Individual queries to official portals

### Important Disclaimers

- **NOT OFFICIAL**: This is not an official government service
- **VERIFY DATA**: Always verify property information through official portals
- **INFORMATIONAL ONLY**: Data is for research and informational purposes
- **NO WARRANTIES**: No warranties about data accuracy or completeness

### Official Portals

- [Delhi Land Revenue Corporation (DLRC)](https://dlrc.delhi.gov.in/)
- [NGDRS - Property Registration](https://ngdrs.delhi.gov.in/)

### Privacy

- All owner names are anonymized
- No personal data is collected without consent
- User contributions are voluntary
- See [research/legal_considerations.md](research/legal_considerations.md) for details

## Contributing

### Data Contributions

If you're a property owner in GK/CRP and want to contribute your property data:

1. Use the manual data entry tool
2. Provide only information you're comfortable sharing
3. Owner names are automatically anonymized

### Code Contributions

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Write/update tests
5. Submit a pull request

## Roadmap

### Phase 1 (MVP - Current)
- [x] Basic search functionality
- [x] Property comparison
- [x] Locality statistics
- [x] Manual data entry tools
- [x] CSV import

### Phase 2 (Post-MVP Validation)
- [ ] User authentication
- [ ] Property alerts
- [ ] Historical price trends
- [ ] Mobile app (React Native)
- [ ] Email notifications

### Phase 3 (Scale)
- [ ] Expand to more Delhi localities
- [ ] Automated data updates (with authorization)
- [ ] Premium features (subscription model)
- [ ] API access for developers
- [ ] Integration with official government APIs

### Phase 4 (Multi-State)
- [ ] Bangalore (Bhoomi portal)
- [ ] Telangana (Dharani portal)
- [ ] Unified pan-India search

## Success Metrics

MVP is successful if:
- ✅ 10+ people use it voluntarily
- ✅ 3+ people say "I would pay for this"
- ✅ Zero legal complaints
- ✅ <2 hours/week maintenance
- ✅ Clear path to expand

## Troubleshooting

### Database Issues

**Database not found:**
```bash
python scripts/init_database.py
```

**Corrupted database:**
```bash
rm database/land_records.db
python scripts/init_database.py
```

### API Issues

**Port already in use:**
```bash
uvicorn api.main:app --port 8001  # Use different port
```

**Import errors:**
```bash
pip install -r requirements.txt --upgrade
```

### Data Import Issues

**CSV format errors:**
```bash
python scripts/import_csv.py --create-template
# Use the template as reference
```

**Validation errors:**
```bash
python scripts/import_csv.py your_file.csv --dry-run
# Check errors before importing
```

## Support & Contact

For issues, questions, or feedback:
- Open an issue on GitHub
- Check documentation in `/docs`
- Review legal considerations in `/research`

## License

This project is for educational and research purposes. See [research/legal_considerations.md](research/legal_considerations.md) for legal framework.

## Acknowledgments

- Built with Claude Code
- Inspired by property search platforms like Zillow, Zoopla
- Data structure based on Delhi Land Revenue Corporation portal
- Legal framework references India's DPDPA 2023 and IT Act 2000

---

**Version:** 1.0.0
**Last Updated:** January 27, 2026
**Status:** MVP - Ready for validation
