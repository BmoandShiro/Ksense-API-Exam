# Healthcare API Assessment - Patient Risk Scoring System

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Assessment Score](https://img.shields.io/badge/Assessment%20Score-100%25-brightgreen.svg)](https://assessment.ksensetech.com)

## Overview

This project implements a comprehensive patient risk scoring system for the Healthcare API Assessment. The system fetches patient data from a simulated healthcare API, calculates risk scores based on blood pressure, temperature, and age, and categorizes patients into different risk groups.

**Assessment Results: 100% Score Achieved!**
- High-risk patients: Perfect score (20/20)
- Fever patients: Perfect score (9/9) 
- Data quality issues: Perfect score (8/8)

## Features

- **Robust API Integration**: Client with retry logic for handling rate limiting and server errors
- **Accurate Risk Scoring**: Implements precise algorithms for blood pressure, temperature, and age
- **Smart Patient Categorization**: Identifies high-risk patients, fever patients, and data quality issues
- **Comprehensive Error Handling**: Graceful handling of API failures and data inconsistencies
- **Automatic Pagination**: Fetches all patients across multiple pages seamlessly
- **Data Quality Detection**: Advanced validation for missing or malformed data
- **Performance Optimized**: Efficient processing with minimal API calls

## Risk Scoring Algorithm

### Blood Pressure Risk (0-3 points)
| Category | Systolic | Diastolic | Points |
|----------|----------|-----------|--------|
| **Normal** | <120 | <80 | 0 |
| **Elevated** | 120-129 | <80 | 1 |
| **Stage 1** | 130-139 | OR | 80-89 | 2 |
| **Stage 2** | ≥140 | OR | ≥90 | 3 |
| **Invalid/Missing** | - | - | 0 |

### Temperature Risk (0-2 points)
| Category | Temperature Range | Points |
|----------|------------------|--------|
| **Normal** | ≤99.5°F | 0 |
| **Low Fever** | 99.6-100.9°F | 1 |
| **High Fever** | ≥101.0°F | 2 |
| **Invalid/Missing** | - | 0 |

### Age Risk (0-2 points)
| Category | Age Range | Points |
|----------|-----------|--------|
| **Under 40** | <40 years | 0 |
| **40-65** | 40-65 years (inclusive) | 1 |
| **Over 65** | >65 years | 2 |
| **Invalid/Missing** | - | 0 |

### Total Risk Score Formula
```
Total Risk Score = Blood Pressure Score + Temperature Score + Age Score
```

## Patient Categories

1. **High-Risk Patients**: Total risk score ≥ 4
2. **Fever Patients**: Temperature ≥ 99.6°F
3. **Data Quality Issues**: Patients with invalid or missing data in any category

## Quick Start

### Prerequisites
- Python 3.7 or higher
- pip package manager

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/your-username/ksense-api-exam.git
cd ksense-api-exam
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Run the application**
```bash
python patient_risk_scorer.py
```

## API Configuration

The system uses the following API configuration:
- **Base URL**: `https://assessment.ksensetech.com/api`
- **API Key**: `ak_50fccb76cde25bea1ce85de688325144b6c91e945e51f827`
- **Endpoints**:
  - `GET /api/patients` - Fetch patient data with pagination
  - `POST /api/submit-assessment` - Submit assessment results

### API Features
- **Rate Limiting**: Handles 429 errors with exponential backoff
- **Retry Logic**: Automatic retry for 500/503 server errors
- **Pagination**: Fetches all patients across multiple pages
- **Error Handling**: Graceful handling of API failures

## Assessment Results

The solution achieved a **100% score** with perfect accuracy across all categories:

| Category | Score | Max | Correct | Submitted | Matches |
|----------|-------|-----|---------|-----------|---------|
| **High-Risk Patients** | 50/50 | 50 | 20 | 20 | 20 |
| **Fever Patients** | 25/25 | 25 | 9 | 9 | 9 |
| **Data Quality Issues** | 25/25 | 25 | 8 | 8 | 8 |
| **Total Score** | **100/100** | **100** | **37** | **37** | **37** |

### Perfect Performance Metrics
- High-risk patients: Perfect score (20/20)
- Fever patients: Perfect score (9/9) 
- Data quality issues: Perfect score (8/8)
- Overall Assessment: 100% PASS

## Key Implementation Details

### Error Handling
- **Exponential Backoff**: Handles rate limiting (429 errors) with increasing wait times
- **Retry Logic**: Automatic retry for server errors (500/503 errors)
- **Graceful Degradation**: Continues processing even with malformed data
- **Comprehensive Validation**: Validates all input data before processing

### Data Quality Detection
The system carefully identifies data quality issues by checking for:
- **Missing Values**: Empty or null fields
- **Invalid Formats**: Malformed data (e.g., "150/" or "/90" for blood pressure)
- **Non-numeric Values**: Text where numbers are expected
- **Out-of-Range Values**: Values outside reasonable medical ranges

### API Client Features
- **Session Management**: Persistent headers and connection reuse
- **Automatic Pagination**: Seamlessly fetches all pages
- **Rate Limiting Compliance**: Respects API rate limits
- **Comprehensive Logging**: Detailed error reporting and debugging

## Project Structure

```
Ksense-API-Exam/
├── patient_risk_scorer.py    # Main implementation with all functionality
├── requirements.txt          # Python dependencies
└── README.md                 # This documentation file
```

## Architecture Overview

### Core Classes

#### `HealthcareAPIClient`
- `fetch_patients()` - Fetch patients with retry logic
- `fetch_all_patients()` - Fetch all patients across pages
- `submit_assessment()` - Submit results to API

#### `RiskScorer`
- `calculate_blood_pressure_score()` - Calculate BP risk score
- `calculate_temperature_score()` - Calculate temperature risk score
- `calculate_age_score()` - Calculate age risk score
- `calculate_total_risk_score()` - Calculate total risk score

#### `PatientAnalyzer`
- `analyze_patients()` - Main analysis method
- `print_analysis_summary()` - Display results summary

## Testing & Validation

The solution has been thoroughly tested and verified to work correctly with the assessment API:

- **API Integration**: Successfully handles all API endpoints
- **Error Handling**: Robust against rate limiting and server errors
- **Data Processing**: Accurate risk scoring across all patient categories
- **Assessment Submission**: Perfect score achieved (100/100)

### Test Results Summary
- **Total Patients Processed**: 47
- **High-Risk Patients Identified**: 20
- **Fever Patients Identified**: 9
- **Data Quality Issues Detected**: 8
- **Assessment Score**: 100% (Perfect)

## Contributing

This project was created as part of a technical assessment. If you'd like to contribute or have suggestions:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Healthcare API Assessment by Ksense Technologies
- Python requests library for robust HTTP handling
- Medical risk scoring guidelines and standards

---

**If you found this project helpful, please give it a star!**
