# Delhi Land Records System - Portal Analysis and Documentation

**Date:** January 27, 2026
**Status:** Research Phase - MVP Development

---

## Executive Summary

This document provides a comprehensive analysis of Delhi's land records and property registration systems, including technical capabilities, data structures, legal considerations, and access restrictions. The analysis covers two primary portal systems:

1. **Delhi Land Revenue Corporation (DLRC) Portal** - Land records system
2. **Delhi Property Registration System** - Property registration and document search

---

## 1. Delhi Land Revenue Corporation (DLRC) Portal

**URL:** https://dlrc.delhi.gov.in/
**Alternative URL:** https://dlrc.delhigovt.nic.in/
**System Owner:** Department of Revenue, Government of NCT of Delhi
**Developed/Hosted by:** National Informatics Centre (NIC)

### 1.1 Available Services and Information

The DLRC portal provides access to two primary land record systems:

#### 1.1.1 Khasra Khatauni Details (under DLR Act)
- **Purpose:** Agricultural land records
- **Access Level:** Public, no authentication required
- **Data Type:** Online display only (informational purposes)
- **Geographic Coverage:** District-wise, subdivision-wise, village-wise

#### 1.1.2 Jamabandi Details (under PLR Act)
- **Purpose:** Property records and record of rights
- **Access Level:** Public, no authentication required
- **Update Frequency:** Amended every 5 years
- **Fields:** 12 columns containing land details, owner information, crop data, tenants, and rent holders

#### 1.1.3 GIS Mapping
- **Feature:** Geographic Information System functionality
- **Purpose:** Geographic visualization of land parcels
- **Integration:** Linked with land record database

### 1.2 Search Capabilities

#### Search Methods Available:
1. **By Khata Number** (Account Number)
2. **By Khasra Number** (Plot/Survey Number)
3. **By Name** (Owner's Name)

#### Search Process Flow:
```
1. Select District
2. Select Subdivision
3. Select Village
4. Choose Search Method (Khata/Khasra/Name)
5. Enter Search Parameters
6. Click "View Khata Details"
```

### 1.3 Required Search Fields

| Search Type | Required Fields |
|-------------|----------------|
| **Initial Selection** | District, Subdivision, Village, Khata Type |
| **By Khata Number** | Khata Number (Account Number) |
| **By Khasra Number** | Khasra Number (Plot/Survey Number) |
| **By Name** | Owner's Name (Full or Partial) |

### 1.4 Data Format and Structure

#### 1.4.1 Khasra (Plot Record)
**Definition:** Unique number assigned to a piece of land (similar to plot/survey number)

**Fields:**
- Khasra Number (Unique Plot ID)
- Plot Area (in standard units)
- Land Classification
- Geographic Boundaries

#### 1.4.2 Girdawari (Harvest Inspection Register)
**Definition:** Khasra-wise annual harvest record register maintained by Patwari

**Structure:** 7 columns
**Update Frequency:** Bi-annually (April and October)

**Fields:**
- Owner/Holder/Tenant Name
- Land Khasra Number
- Area
- Land Type (Cultivated/Non-cultivated)
- Irrigation Method
- Crop Name
- Crop Condition

#### 1.4.3 Jamabandi (Record of Rights)
**Definition:** Khewat-wise comprehensive record-of-rights

**Structure:** 12 columns
**Update Frequency:** Every 5 years

**Fields:**
- Owner Details (Name, Father's Name, Aadhar, Registered Address)
- Khata Number
- Khasra Number
- Land Area
- Land Classification (Agricultural, Residential, Commercial, Government)
- Cultivation Details
- Revenue Assessment
- Rent and Cess Payable
- Tenancy Information
- Mutation Records
- Encumbrance Status
- Pending Disputes/Liabilities

### 1.5 Access Restrictions

#### Public Access:
- ✅ View-only access to land records
- ✅ No login/authentication required for viewing
- ✅ Free of charge for basic searches
- ❌ No bulk download functionality
- ❌ No API access documented
- ❌ No automated data extraction tools provided

#### Authentication Requirements:
- **None for viewing records**
- Authentication may be required for:
  - Obtaining certified copies
  - Filing mutation requests
  - Official document downloads

#### Disclaimers:
> "This website has been designed and hosted by NIC and belongs to Department of Revenue, Government of NCT of Delhi, India. NIC will not be responsible for any inaccuracy in the data on this website."

> "Information is displayed for informational purposes only. Contact local revenue offices for additional details."

### 1.6 Technical Limitations

- ❌ No documented public API
- ❌ No programmatic data access
- ❌ Data displayed in HTML format only
- ❌ No structured data export (CSV, JSON, XML)
- ⚠️ Session-based web interface
- ⚠️ Data accuracy not guaranteed by NIC

---

## 2. Delhi Property Registration System

### 2.1 System Overview

**Important Note:** The domain `registrationdelhigovt.nic.in` returned a 403 error during research, suggesting access restrictions or deprecated status. The active systems are:

1. **NGDRS (Next Generation Document Registration System)** - Current system
2. **e-Search Portal** - Document search and verification
3. **Deed Doc Portal** - Scanned document retrieval
4. **DORIS** - Legacy system (being phased out)

### 2.2 NGDRS - Next Generation Document Registration System

**URL:** https://ngdrs.delhi.gov.in/
**National Portal:** https://www.ngdrs.gov.in/
**Implementation Date:** Mandated by January 2025
**Status:** Active across all Sub-Registrar offices in Delhi

#### Features:
- Online deed entry
- Online payment processing
- Online appointment scheduling
- Document admission
- Document search
- Certified copy generation
- API integration with national portal

#### Integration:
- Delhi shares registration data with the national NGDRS portal through API/User Interface
- Part of Digital India Land Records Modernization Programme (DILRMP)

### 2.3 e-Search Portal

**URL:** https://esearch.delhigovt.nic.in/
**Alternative:** https://edoris.delhigovt.nic.in/Complete_search.aspx
**NGDRS e-Search:** https://ngdrs.delhi.gov.in/NGDRS_DL/DLSearch/citizenloginesearch

#### Purpose:
- Search details of all registered properties in Sub-Registrar/e-Sub-Registrar offices
- Find property owner information
- Verify registration numbers and dates

#### Search Capabilities:
- Search by property owner name
- Search by registration number
- Search by registration date
- Search by property locality

### 2.4 Deed Doc Portal

**URL:** https://scan.delhigovt.nic.in/

#### Purpose:
- Access scanned deed documents
- Retrieve historical property records

#### Required Search Fields:

| Field Name | Description | Required |
|------------|-------------|----------|
| Property Locality | Area/location name | Yes |
| Subregistrar Office (SRO) | Specific sub-registrar office | Yes |
| Registration Number | Unique registration number | Yes |
| Registration Year | Year of registration | Yes |
| Book Number | Book number where deed is recorded | Yes |

### 2.5 Data Format and Structure

#### Registration Document Fields:
```json
{
  "registration_number": "string",
  "registration_date": "date",
  "registration_year": "integer",
  "book_number": "string",
  "subregistrar_office": "string",
  "property_locality": "string",
  "owner_details": {
    "name": "string",
    "father_name": "string",
    "address": "string"
  },
  "property_details": {
    "type": "string",
    "area": "number",
    "boundaries": "object"
  },
  "transaction_type": "string",
  "consideration_amount": "number",
  "stamp_duty": "number",
  "registration_fee": "number"
}
```

### 2.6 Access Restrictions

#### Public Access:
- ✅ Search property registration details
- ✅ Verify ownership information
- ✅ Check registration status
- ⚠️ Login may be required for detailed document access
- ❌ No bulk data export
- ❌ No API access for third parties

#### Authentication:
- Basic searches: May not require login
- Detailed document access: Login required
- Certified copies: Login + payment required
- NGDRS services: Citizen login required

---

## 3. Legal Considerations

### 3.1 Indian Legal Framework for Data Scraping

#### 3.1.1 Digital Personal Data Protection Act (DPDPA) 2023

**Status:** Brought into force in 2025; core provisions effective May 13, 2027
**Key Date:** Registration for consent managers opens November 13, 2026

#### Key Provisions:

**Consent Requirements:**
- Must be "free, specific, informed, unconditional and unambiguous"
- Affirmative act required (no pre-checked boxes)
- Applies to private sector data processing

**Government Data Exception - Legitimate Uses (Section 7):**
> The State and its instrumentalities may process personal data to provide or issue subsidies, benefits, services, certificates, licenses or permits where:
> - (i) The individual has previously consented, OR
> - (ii) Such personal data is available in databases maintained by the State that are notified by the Central Government

**Publicly Available Data Exemption (Section 3(c)(ii)):**
> The DPDPA does not apply to personal data that is made or caused to be made publicly available by:
> - (A) The Data Principal (individual) to whom such personal data relates, OR
> - (B) Any other person who is under an obligation under any law to make such personal data publicly available

**Contradiction in Framework:**
⚠️ While Section 3(c)(ii) exempts publicly available data, the government has indicated that organizations scraping or processing publicly available data may still need to comply with consent and other obligations.

#### 3.1.2 Information Technology Act, 2000

**Section 43 - Civil Liability:**
- Sanctions for damage to computer systems
- Covers unauthorized access to computer systems or servers
- Includes accessing systems remotely without permission

**Section 66 - Criminal Penalties:**
- Imprisonment up to 3 years
- Fine up to INR 5 Lakhs
- Applies to acts mentioned under Section 43

**Relevant Scenario:**
Aggressive scraping that damages or disrupts government servers could fall under these provisions.

#### 3.1.3 Copyright Act, 1957

**Applicability to Data:**
- Compilations are considered "literary works"
- Copyright vests in "original" literary work
- Database compilations may be protected

**Precedent:**
- Delhi High Court granted OLX a permanent restraining order preventing data scraping from its website
- Establishes that websites can claim copyright over their data compilations

### 3.2 What Can Be Legally Accessed

#### ✅ **Permitted Activities:**

1. **Manual Searches:**
   - Using the portal interface as designed
   - Individual property searches
   - Verification of specific records
   - Educational/research purposes (fair use)

2. **Public Information:**
   - Information explicitly made public by government portals
   - Data displayed without authentication
   - Information provided for "informational purposes"

3. **Licensed Access:**
   - Using official APIs when available
   - Accessing data through authorized partnerships
   - Obtaining bulk data through official channels

4. **Personal Use:**
   - Checking your own property records
   - Verifying information for legitimate transactions
   - Research and analysis for non-commercial purposes

### 3.3 What Cannot Be Scraped

#### ❌ **Prohibited Activities:**

1. **Automated Scraping:**
   - Large-scale automated data extraction
   - Bot-based scraping without permission
   - Bypassing CAPTCHA or security measures
   - Session hijacking or credential stuffing

2. **Data Compilation for Commercial Use:**
   - Creating competing databases
   - Reselling scraped government data
   - Building commercial products on scraped data
   - Mass data extraction for profit

3. **Server Disruption:**
   - High-frequency requests causing load
   - DDoS-like behavior
   - Interfering with normal portal operations

4. **Privacy Violations:**
   - Extracting and republishing personal data
   - Creating profiles without consent
   - Bulk collection of PII (Personally Identifiable Information)

### 3.4 Public vs Private Data

#### Public Data (Lower Risk):
- Property ownership records (already public)
- Registration numbers and dates
- Land classification information
- Geographic boundaries
- Revenue assessment data

#### Private/Sensitive Data (Higher Risk):
- Aadhar numbers
- Complete residential addresses
- Phone numbers and email addresses
- Bank account details
- Detailed personal information beyond what's necessary

### 3.5 Terms of Service Analysis

#### DLRC Portal Disclaimer:
> "This website has been designed and hosted by NIC and belongs to Department of Revenue, Government of NCT of Delhi, India. NIC will not be responsible for any inaccuracy in the data on this website."

**Implications:**
- Data provided "as is"
- No guarantees of accuracy
- Informational purposes only
- Official verification required from revenue offices

#### Delhi Property Registration Terms:
- All SR offices migrated to NGDRS
- DORIS being phased out
- Login required for detailed access
- Citizen authentication for certified copies

### 3.6 Risk Assessment Matrix

| Activity | Legal Risk | Technical Risk | Recommendation |
|----------|-----------|----------------|----------------|
| Manual individual searches | Low | Low | ✅ Permitted |
| Accessing public search interface | Low | Low | ✅ Permitted |
| Building on official APIs (if available) | Low | Low | ✅ Permitted |
| Moderate automated scraping | Medium | Medium | ⚠️ Requires legal review |
| Large-scale automated extraction | High | Medium | ❌ Not recommended |
| Commercial data reselling | High | Low | ❌ Prohibited |
| Bypassing security measures | Very High | High | ❌ Illegal |

### 3.7 Best Practices for Legal Compliance

#### ✅ **Recommended Approach:**

1. **Seek Official Channels:**
   - Request official API access from Delhi government
   - Apply for data sharing partnerships
   - Use DILRMP national portal for authorized access

2. **Respect Rate Limits:**
   - Implement reasonable delays between requests
   - Avoid overwhelming servers
   - Monitor and respect robots.txt if present

3. **Data Minimization:**
   - Only collect data necessary for your purpose
   - Avoid collecting PII when not needed
   - Implement privacy-by-design principles

4. **Transparency:**
   - Be transparent about data collection methods
   - Provide clear privacy policies
   - Offer opt-out mechanisms

5. **Legal Consultation:**
   - Consult with legal experts in IT law
   - Review DPDPA compliance requirements
   - Stay updated on evolving regulations

6. **Technical Safeguards:**
   - Implement proper data security
   - Encrypt stored data
   - Limit data retention periods

---

## 4. Sample Data Structures

### 4.1 Land Record (Khasra Khatauni) Data Structure

```json
{
  "record_type": "khasra_khatauni",
  "record_id": "DL-SW-001-KH-12345",
  "last_updated": "2026-01-15T10:30:00Z",
  "jurisdiction": {
    "district": "South West Delhi",
    "subdivision": "Najafgarh",
    "village": "Dwarka",
    "tehsil": "Najafgarh"
  },
  "khasra_details": {
    "khasra_number": "123/1",
    "area": {
      "value": 500,
      "unit": "square_meters"
    },
    "land_type": "agricultural",
    "boundaries": {
      "north": "Road",
      "south": "Khasra 123/2",
      "east": "Canal",
      "west": "Khasra 122"
    }
  },
  "khata_details": {
    "khata_number": "KH-456",
    "khata_type": "pattedari"
  },
  "ownership": {
    "owners": [
      {
        "name": "Rajesh Kumar",
        "father_name": "Ram Kumar",
        "share": "50%",
        "owner_type": "individual"
      },
      {
        "name": "Suresh Kumar",
        "father_name": "Ram Kumar",
        "share": "50%",
        "owner_type": "individual"
      }
    ],
    "total_owners": 2
  },
  "cultivation": {
    "cultivator_name": "Rajesh Kumar",
    "cultivator_type": "owner",
    "current_crop": "wheat",
    "irrigation_method": "canal",
    "cultivation_status": "cultivated"
  },
  "revenue": {
    "annual_revenue": 5000,
    "cess_payable": 500,
    "currency": "INR",
    "payment_status": "paid"
  },
  "mutations": [
    {
      "mutation_id": "MUT-2024-001",
      "mutation_date": "2024-03-15",
      "mutation_type": "inheritance",
      "previous_owner": "Ram Kumar",
      "new_owners": ["Rajesh Kumar", "Suresh Kumar"],
      "status": "completed"
    }
  ],
  "encumbrances": {
    "has_encumbrance": false,
    "pending_disputes": false,
    "mortgage_status": "clear"
  },
  "source": {
    "portal": "DLRC",
    "url": "https://dlrc.delhi.gov.in/",
    "disclaimer": "For informational purposes only. Verify with revenue office."
  }
}
```

### 4.2 Girdawari (Harvest Inspection) Data Structure

```json
{
  "record_type": "girdawari",
  "inspection_id": "GW-2025-10-123",
  "inspection_date": "2025-10-15",
  "inspection_season": "kharif",
  "inspector": {
    "name": "Patwari Name",
    "designation": "Patwari",
    "circle": "Circle 3"
  },
  "land_details": {
    "khasra_number": "123/1",
    "area": {
      "value": 500,
      "unit": "square_meters"
    }
  },
  "cultivation_details": {
    "land_holder": "Rajesh Kumar",
    "holder_type": "owner",
    "land_status": "cultivated",
    "crop_name": "rice",
    "crop_condition": "good",
    "irrigation_source": "canal",
    "expected_yield": "moderate"
  },
  "previous_inspection": {
    "date": "2025-04-15",
    "season": "rabi",
    "crop": "wheat"
  }
}
```

### 4.3 Jamabandi (Record of Rights) Data Structure

```json
{
  "record_type": "jamabandi",
  "jamabandi_year": "2025-2030",
  "issue_date": "2025-01-01",
  "valid_until": "2030-12-31",
  "record_id": "JB-DL-SW-001-456",
  "jurisdiction": {
    "district": "South West Delhi",
    "subdivision": "Najafgarh",
    "village": "Dwarka",
    "halka": "Halka 5"
  },
  "khewat": {
    "khewat_number": "KW-789",
    "owners": [
      {
        "owner_id": "OWN-001",
        "name": "Rajesh Kumar",
        "father_name": "Ram Kumar",
        "address": "Village Dwarka, Delhi",
        "aadhar_linked": true,
        "ownership_type": "joint",
        "share_percentage": 50
      },
      {
        "owner_id": "OWN-002",
        "name": "Suresh Kumar",
        "father_name": "Ram Kumar",
        "address": "Village Dwarka, Delhi",
        "aadhar_linked": true,
        "ownership_type": "joint",
        "share_percentage": 50
      }
    ]
  },
  "khatuni": {
    "khatuni_number": "KHU-456",
    "total_holdings": [
      {
        "khasra_number": "123/1",
        "area": {
          "value": 500,
          "unit": "square_meters"
        },
        "land_class": "agricultural",
        "soil_type": "loamy",
        "irrigation_facility": "canal"
      },
      {
        "khasra_number": "123/2",
        "area": {
          "value": 300,
          "unit": "square_meters"
        },
        "land_class": "agricultural",
        "soil_type": "loamy",
        "irrigation_facility": "canal"
      }
    ],
    "total_area": {
      "value": 800,
      "unit": "square_meters"
    }
  },
  "revenue_details": {
    "annual_revenue": 8000,
    "land_revenue": 7000,
    "water_cess": 500,
    "other_cess": 500,
    "currency": "INR",
    "payment_cycle": "annual"
  },
  "tenancy": {
    "has_tenants": false,
    "tenant_details": []
  },
  "rights_and_restrictions": {
    "ownership_rights": "full",
    "restrictions": [],
    "easements": [],
    "government_acquisitions": "none"
  },
  "mutations_history": [
    {
      "serial_number": 1,
      "mutation_date": "2024-03-15",
      "mutation_type": "inheritance",
      "details": "Transfer from Ram Kumar to Rajesh Kumar and Suresh Kumar"
    }
  ],
  "verification": {
    "verified_by": "Patwari Name",
    "verification_date": "2025-01-15",
    "attestation": "Revenue Inspector Name",
    "seal": "official_seal_reference"
  }
}
```

### 4.4 Property Registration Document Structure

```json
{
  "record_type": "property_registration",
  "document_id": "REG-DL-2025-12345",
  "registration_details": {
    "registration_number": "12345",
    "book_number": "Book-1",
    "volume_number": "Vol-25",
    "page_number": "Page-101",
    "registration_date": "2025-01-20",
    "registration_year": 2025,
    "subregistrar_office": {
      "sro_name": "SRO Dwarka",
      "sro_code": "DL-SW-03",
      "district": "South West Delhi"
    }
  },
  "document_type": "sale_deed",
  "parties": {
    "sellers": [
      {
        "party_id": "SELLER-001",
        "name": "Amit Sharma",
        "father_name": "Vijay Sharma",
        "address": "123, Sector 10, Dwarka, New Delhi - 110075",
        "pan": "ABCDE1234F",
        "aadhar": "XXXX-XXXX-5678"
      }
    ],
    "buyers": [
      {
        "party_id": "BUYER-001",
        "name": "Priya Gupta",
        "father_name": "Rakesh Gupta",
        "address": "456, Sector 12, Dwarka, New Delhi - 110078",
        "pan": "FGHIJ5678K",
        "aadhar": "XXXX-XXXX-9012"
      }
    ],
    "witnesses": [
      {
        "name": "Witness 1",
        "address": "Address 1"
      },
      {
        "name": "Witness 2",
        "address": "Address 2"
      }
    ]
  },
  "property_details": {
    "property_id": "PROP-DL-001",
    "locality": "Dwarka Sector 10",
    "address": "Plot No. 123, Sector 10, Dwarka, New Delhi - 110075",
    "property_type": "residential",
    "sub_type": "independent_floor",
    "area": {
      "plot_area": {
        "value": 200,
        "unit": "square_meters"
      },
      "built_up_area": {
        "value": 150,
        "unit": "square_meters"
      }
    },
    "boundaries": {
      "north": "Plot 122",
      "south": "Plot 124",
      "east": "Road",
      "west": "Plot 123A"
    },
    "khasra_number": "567/2",
    "khata_number": "KH-789"
  },
  "financial_details": {
    "consideration_amount": 5000000,
    "stamp_duty": 300000,
    "registration_fee": 30000,
    "total_amount": 5330000,
    "currency": "INR",
    "payment_mode": "bank_transfer",
    "payment_reference": "UTR123456789"
  },
  "previous_documents": [
    {
      "document_type": "sale_deed",
      "registration_number": "10001",
      "registration_date": "2015-05-10",
      "previous_owner": "Vijay Sharma"
    }
  ],
  "verification": {
    "verified_by": "Sub Registrar Name",
    "verification_date": "2025-01-20",
    "seal_number": "SEAL-2025-001",
    "signature": "digital_signature_reference"
  },
  "encumbrances": {
    "checked": true,
    "encumbrance_certificate_number": "EC-2025-001",
    "encumbrance_status": "clear",
    "checked_from": "2015-05-10",
    "checked_to": "2025-01-20"
  },
  "digital_details": {
    "document_url": "https://scan.delhigovt.nic.in/docs/...",
    "digital_signature": "SHA256:...",
    "qr_code": "QR_DATA",
    "ngdrs_id": "NGDRS-DL-2025-12345"
  }
}
```

### 4.5 Search Query Structure

```json
{
  "query_type": "land_record_search",
  "portal": "DLRC",
  "search_parameters": {
    "district": "South West Delhi",
    "subdivision": "Najafgarh",
    "village": "Dwarka",
    "search_by": "khasra_number",
    "search_value": "123/1"
  },
  "alternate_searches": {
    "by_khata": {
      "khata_number": "KH-456"
    },
    "by_name": {
      "owner_name": "Rajesh Kumar",
      "fuzzy_match": true
    }
  }
}
```

```json
{
  "query_type": "registration_search",
  "portal": "e-Search",
  "search_parameters": {
    "property_locality": "Dwarka Sector 10",
    "subregistrar_office": "SRO Dwarka",
    "registration_number": "12345",
    "registration_year": 2025,
    "book_number": "Book-1"
  },
  "optional_parameters": {
    "owner_name": "Priya Gupta",
    "date_from": "2025-01-01",
    "date_to": "2025-01-31"
  }
}
```

---

## 5. Technical Integration Considerations

### 5.1 Current State

**Official APIs:** Not publicly documented
**NGDRS Integration:** Available for government agencies through API
**Data Format:** HTML-based web interface
**Bulk Access:** Not available to public

### 5.2 Alternative Approaches

#### Option 1: Official Data Partnership
- Apply to Delhi Revenue Department for data access
- Partner with DILRMP for authorized integration
- Use NGDRS API (if access granted)

#### Option 2: Manual Verification Service
- Build interface for users to input their own data
- Users search on official portal
- Users input results into your system
- Your system helps organize and analyze

#### Option 3: Hybrid Approach
- Provide direct links to official portals
- Guide users through search process
- Store minimal data (references only, not full records)
- Focus on value-added services (alerts, analysis, comparisons)

### 5.3 Recommended MVP Approach

For legal and practical reasons, the recommended MVP approach is:

```
┌─────────────────────────────────────────┐
│         Your Application (MVP)          │
│                                         │
│  ┌───────────────────────────────────┐ │
│  │   User Input Interface            │ │
│  │   - Guide users to official       │ │
│  │     portals                       │ │
│  │   - Provide search instructions   │ │
│  └───────────────────────────────────┘ │
│                                         │
│  ┌───────────────────────────────────┐ │
│  │   Manual Data Entry               │ │
│  │   - Users enter their property    │ │
│  │     details from official source  │ │
│  └───────────────────────────────────┘ │
│                                         │
│  ┌───────────────────────────────────┐ │
│  │   Value-Added Services            │ │
│  │   - Data validation               │ │
│  │   - Alerts on changes             │ │
│  │   - Document organization         │ │
│  │   - Analysis and insights         │ │
│  └───────────────────────────────────┘ │
│                                         │
│  ┌───────────────────────────────────┐ │
│  │   Reference Storage               │ │
│  │   - Store only references         │ │
│  │   - Link to official sources      │ │
│  │   - User's personal notes         │ │
│  └───────────────────────────────────┘ │
└─────────────────────────────────────────┘
           │                 │
           │                 │
           ▼                 ▼
    User verifies     Official portal
    on official       verification link
    portal
```

---

## 6. Key Findings Summary

### 6.1 Portal Capabilities

| Feature | DLRC Portal | NGDRS/e-Search |
|---------|-------------|----------------|
| Public Access | ✅ Yes | ⚠️ Limited |
| Authentication Required | ❌ No | ⚠️ For details |
| Search by Owner Name | ✅ Yes | ✅ Yes |
| Search by Property ID | ✅ Yes | ✅ Yes |
| Download Records | ❌ No | ⚠️ Paid |
| API Access | ❌ No | ⚠️ Government only |
| GIS Mapping | ✅ Yes | ❌ No |
| Historical Records | ✅ Yes | ✅ Yes |

### 6.2 Legal Constraints

| Activity | Risk Level | Recommendation |
|----------|-----------|----------------|
| Manual searches | 🟢 Low | Proceed |
| User-directed searches | 🟢 Low | Proceed |
| Light automation | 🟡 Medium | Legal review |
| Heavy scraping | 🔴 High | Avoid |
| Bulk extraction | 🔴 High | Avoid |
| Commercial resale | 🔴 Very High | Illegal |

### 6.3 Data Availability

**Publicly Available:**
- Land ownership records
- Property boundaries
- Revenue assessment
- Mutation history
- Registration details

**Restricted/Sensitive:**
- Complete Aadhar numbers
- Detailed financial information
- Certified copies (paid)
- Bulk datasets

---

## 7. Recommendations for MVP Development

### 7.1 Phase 1: Foundation (Legal & Safe)

1. **Educational Portal:**
   - Guide users on how to search official portals
   - Provide explanatory content about land records
   - Link to official sources
   - No data scraping

2. **User Data Entry:**
   - Allow users to manually enter their property details
   - Store only user-provided data
   - Provide validation tools
   - Clear privacy policy

3. **Reference Management:**
   - Store references to official records (not the records themselves)
   - Save search parameters for repeat searches
   - Organize user's personal property portfolio

### 7.2 Phase 2: Value Addition

1. **Alert System:**
   - Notify users when they should check for updates
   - Remind about verification deadlines
   - Alert on common issues

2. **Analytics:**
   - Analyze user's property data
   - Identify potential issues
   - Suggest actions

3. **Document Management:**
   - Help users organize their property documents
   - Track document expiry dates
   - Generate checklists

### 7.3 Phase 3: Scale (With Proper Authorization)

1. **Official Partnership:**
   - Apply for official data access
   - Partner with Delhi Revenue Department
   - Obtain API access to NGDRS

2. **Authorized Integration:**
   - Build on official APIs
   - Implement real-time verification
   - Provide certified reports

3. **Enterprise Services:**
   - Offer bulk verification for banks
   - Property due diligence for developers
   - Compliance tools for legal firms

---

## 8. Legal Checklist for Development

### Pre-Launch:
- [ ] Consult with IT law attorney
- [ ] Review DPDPA compliance requirements
- [ ] Draft comprehensive Terms of Service
- [ ] Create clear Privacy Policy
- [ ] Implement data minimization
- [ ] Set up data security measures
- [ ] Document all data sources
- [ ] Avoid any automated scraping
- [ ] Implement user consent mechanisms
- [ ] Plan data retention policies

### During Development:
- [ ] Use only official APIs (when available)
- [ ] Implement proper authentication
- [ ] Add rate limiting
- [ ] Log all data access
- [ ] Encrypt sensitive data
- [ ] Follow security best practices
- [ ] Test with legal team
- [ ] Document compliance measures

### Post-Launch:
- [ ] Monitor for legal updates
- [ ] Stay informed on DPDPA developments
- [ ] Maintain audit trails
- [ ] Respond to takedown requests
- [ ] Provide data deletion mechanisms
- [ ] Regular compliance reviews
- [ ] User privacy rights implementation

---

## 9. References and Sources

### Official Portals:
- Delhi Land Revenue Corporation: https://dlrc.delhi.gov.in/
- NGDRS Delhi: https://ngdrs.delhi.gov.in/
- e-Search Portal: https://esearch.delhigovt.nic.in/
- Deed Doc Portal: https://scan.delhigovt.nic.in/
- Department of Revenue, Delhi: https://revenue.delhi.gov.in/

### Legal References:
- Digital Personal Data Protection Act (DPDPA), 2023
- Information Technology Act, 2000
- Copyright Act, 1957
- Digital India Land Records Modernization Programme (DILRMP)

### Research Sources:
- [Bhulekh Delhi Land Records Online | Check Property & Khasra Info](https://www.squareyards.com/blog/bhulekh-delhi-land-records-lrid)
- [Land Records | Department of Revenue](https://revenue.delhi.gov.in/revenue/land-records)
- [Delhi Land Records: How to Check Ownership Details Online](https://www.basichomeloan.com/blog/home-loans/delhi-land-record)
- [Scraping public data in India: Innovation enabler or privacy threat? | IAPP](https://iapp.org/news/a/scraping-public-data-in-india-innovation-enabler-or-privacy-threat-)
- [Data scraping consent and India's DPDPA exemption | India | Law.asia](https://law.asia/india-data-scraping-regulation/)
- [Legality of Data Scraping Under Indian Law: Key Considerations](https://spiceroutelegal.com/publications/legality-of-data-scraping-under-indian-law/)
- [National Generic Document Registration System (NGDRS)](https://dolr.gov.in/national-generic-document-registration-system/)
- [Land Records Terminology in India | AssetYogi](https://assetyogi.com/guides/land-records/land-records-terminology-in-india/)
- [India's new privacy law is here: What you need to know](https://www.mwe.com/insights/what-to-know-about-indias-new-privacy-law/)
- [Publicly Available Data Exemption in the DPDPA | India | Law.asia](https://law.asia/publicly-available-data-dpdpa/)

---

## 10. Glossary

**Aadhar:** Unique 12-digit identification number issued by UIDAI to Indian residents

**DILRMP:** Digital India Land Records Modernization Programme

**DORIS:** Delhi Online Registration Information System (legacy system)

**DPDPA:** Digital Personal Data Protection Act, 2023

**Girdawari:** Harvest inspection register maintained by Patwari

**Jamabandi:** Record of rights document (updated every 5 years)

**Khata:** Account number representing ownership

**Khasra:** Plot/survey number for land parcels

**Khatauni:** Register containing details of holdings

**Khewat:** Register of owners

**Mutation:** Transfer of ownership rights

**NGDRS:** Next Generation Document Registration System

**NIC:** National Informatics Centre

**Patwari:** Village-level revenue official

**SRO:** Sub-Registrar Office

**Tehsil:** Administrative division (sub-district)

---

**Document Version:** 1.0
**Last Updated:** January 27, 2026
**Next Review:** Before starting Phase 2 development or upon legal framework changes

---

## DISCLAIMER

This document is for research and informational purposes only and does not constitute legal advice. The legal landscape around data scraping and privacy in India is evolving, particularly with the DPDPA coming into full force in 2027. Always consult with qualified legal counsel before implementing any data collection or processing activities. The information in this document may become outdated as laws, regulations, and portal capabilities change.
