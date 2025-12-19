# 📊 Contraídos Visual Analyzer

> Professional visual tool for analyzing contraídos and accounting documents with extensible architecture for future features.

## 🌟 Features

### Current Features (v1.0.0)
- ✅ **Visual File Upload** - Drag & drop Excel files (.xlsx, .xls)
- ✅ **Automatic Analysis** - Instant validation and processing
- ✅ **Interactive Dashboard** - Visual charts and KPI metrics
- ✅ **Business Rules Validation** - Automated compliance checking
- ✅ **Multiple Export Formats** - Excel and JSON exports
- ✅ **Real-time Feedback** - Progress indicators and error handling

### Extensible Architecture
- 🔌 **Plugin-Ready** - Easy to add new file formats (PDF, CSV, etc.)
- 🎯 **Multi-Analysis** - Prepared for balance sheets, invoices, expenses
- 📈 **Scalable** - Factory pattern for parsers and analyzers
- 🏗️ **Clean Architecture** - Separation of concerns, SOLID principles

---

## 🏗️ Architecture Overview

```
contraidos-processor/
├── backend/                  # FastAPI Backend
│   ├── app/
│   │   ├── core/            # Core business logic
│   │   │   ├── parsers/     # File parsers (extensible)
│   │   │   │   ├── base.py             # Base parser interface
│   │   │   │   ├── factory.py          # Parser factory
│   │   │   │   └── contraidos_parser.py # Excel parser
│   │   │   ├── analyzers/   # Data analyzers (extensible)
│   │   │   │   ├── base.py              # Base analyzer interface
│   │   │   │   ├── factory.py           # Analyzer factory
│   │   │   │   └── contraidos_analyzer.py # Contraídos analyzer
│   │   │   └── models.py    # Data models
│   │   ├── api/             # API routes
│   │   │   └── routes/
│   │   │       ├── upload.py
│   │   │       ├── analysis.py
│   │   │       └── export.py
│   │   ├── services/        # Business services
│   │   │   ├── file_service.py
│   │   │   ├── analysis_service.py
│   │   │   └── export_service.py
│   │   ├── db/              # Database schemas
│   │   ├── config.py        # Configuration
│   │   └── main.py          # FastAPI app
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/                # React Frontend
│   ├── src/
│   │   ├── components/      # React components
│   │   │   ├── upload/      # File upload components
│   │   │   ├── dashboard/   # Dashboard components
│   │   │   └── common/      # Shared components
│   │   ├── services/        # API client
│   │   ├── types/           # TypeScript types
│   │   ├── utils/           # Utilities
│   │   ├── App.tsx          # Main app
│   │   └── main.tsx         # Entry point
│   ├── package.json
│   └── Dockerfile
└── docker-compose.yml       # Docker orchestration
```

---

## 🚀 Quick Start

### Option 1: Docker (Recommended)

```bash
# Clone repository
cd contraidos-processor

# Start services
docker-compose up -d

# Access application
# Frontend: http://localhost
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/api/docs
```

### Option 2: Local Development

#### Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file (optional)
cp .env.example .env

# Run development server
uvicorn app.main:app --reload

# Backend runs at: http://localhost:8000
# API Documentation: http://localhost:8000/api/docs
```

#### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev

# Frontend runs at: http://localhost:5173
```

---

## 📖 Usage Guide

### 1. Upload File

1. Open the application in your browser
2. Drag and drop an Excel file or click to select
3. Supported formats: `.xlsx`, `.xls`
4. Maximum size: 50MB

### 2. View Analysis

The dashboard displays:
- **Summary Cards**: Total operations, AINP count, balance, issues
- **Charts**: Distribution by phase, balance summary
- **Validation**: Detected issues and warnings
- **Details**: Grouped data by contraído

### 3. Export Results

Click export buttons to download:
- **Excel**: Multi-sheet workbook with summary and details
- **JSON**: Complete analysis in JSON format

---

## 🔌 Extending the System

### Adding a New File Format (Example: PDF)

#### 1. Create PDF Parser

```python
# backend/app/core/parsers/pdf_parser.py

from .base import BaseFileParser, ParserResult
import pdfplumber

class PDFParser(BaseFileParser):
    supported_extensions = {".pdf"}

    def can_handle(self, file_path: Path) -> bool:
        return file_path.suffix.lower() == '.pdf'

    def parse(self, file_path: Path) -> ParserResult:
        # Implement PDF parsing logic
        with pdfplumber.open(file_path) as pdf:
            # Extract tables, process data
            ...
        return ParserResult(success=True, dataframe=df, ...)

    def validate_structure(self, df: DataFrame) -> tuple[bool, list[str]]:
        # Validate PDF structure
        ...
```

#### 2. Register Parser

```python
# backend/app/core/__init__.py

from .parsers.pdf_parser import PDFParser

def register_plugins():
    parser_factory = get_parser_factory()
    parser_factory.register_parser(PDFParser())
    # ... existing registrations
```

That's it! The system will automatically:
- Accept PDF uploads
- Use PDF parser for `.pdf` files
- Process and analyze the data

### Adding a New Analysis Type (Example: Balance Sheet)

#### 1. Create Balance Analyzer

```python
# backend/app/core/analyzers/balance_analyzer.py

from .base import BaseAnalyzer, AnalysisResult

class BalanceSheetAnalyzer(BaseAnalyzer):
    def get_analysis_type(self) -> str:
        return "balance_sheet"

    @staticmethod
    def can_analyze(df: DataFrame, metadata: dict = None) -> bool:
        # Detect balance sheet columns
        required_cols = {"Activo", "Pasivo", "Patrimonio"}
        return required_cols.issubset(set(df.columns))

    def analyze(self) -> AnalysisResult:
        # Implement balance sheet analysis
        return AnalysisResult(
            success=True,
            analysis_type="balance_sheet",
            summary=self._analyze_summary(),
            ...
        )

    def validate_business_rules(self) -> dict:
        # Rule: Assets = Liabilities + Equity
        ...

    def get_chart_data(self) -> dict:
        # Return balance sheet charts
        ...
```

#### 2. Register Analyzer

```python
# backend/app/core/__init__.py

from .analyzers.balance_analyzer import BalanceSheetAnalyzer

def register_plugins():
    analyzer_factory = get_analyzer_factory()
    analyzer_factory.register_analyzer("balance_sheet", BalanceSheetAnalyzer)
    # ... existing registrations
```

#### 3. Create Frontend Dashboard (Optional)

```tsx
// frontend/src/components/dashboards/BalanceDashboard.tsx

export const BalanceDashboard: React.FC<{data: any}> = ({ data }) => {
  return (
    <div>
      {/* Custom charts and visualizations for balance sheets */}
      <SummaryCard title="Total Assets" value={data.summary.total_assets} />
      <AssetsPieChart data={data.chart_data.assets_distribution} />
    </div>
  );
};
```

---

## 🎯 API Reference

### Upload File
```http
POST /api/v1/upload
Content-Type: multipart/form-data

Response:
{
  "upload_id": "uuid",
  "filename": "contraidos.xlsx",
  "status": "uploaded"
}
```

### Analyze File
```http
POST /api/v1/analysis/{upload_id}
Content-Type: application/json

Body (optional):
{
  "analysis_type": "contraidos"  // or auto-detect
}

Response:
{
  "analysis_id": "uuid",
  "analysis_type": "contraidos",
  "summary": {...},
  "details": {...},
  "validation": {...},
  "chart_data": {...}
}
```

### Export Analysis
```http
POST /api/v1/export/{analysis_id}
Content-Type: application/json

Body:
{
  "format": "excel"  // or "json"
}

Response:
{
  "export_id": "uuid",
  "download_url": "/api/v1/export/download/uuid"
}
```

Full API documentation: `http://localhost:8000/api/docs`

---

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm test
```

---

## 📦 Deployment

### Production Docker Deployment

```bash
# Build production images
docker-compose -f docker-compose.yml build

# Start services
docker-compose up -d

# Check logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Environment Variables

Create `.env` file in backend directory:

```env
APP_NAME="Contraídos Visual Analyzer"
DEBUG=false
API_PREFIX="/api/v1"
CORS_ORIGINS=["https://yourdomain.com"]
MAX_UPLOAD_SIZE=52428800
```

---

## 🔒 Security Considerations

- ✅ File type validation (only Excel files)
- ✅ File size limits (50MB default)
- ✅ CORS configuration
- ✅ Input sanitization
- ⚠️ **TODO**: Add authentication for multi-user
- ⚠️ **TODO**: Add rate limiting
- ⚠️ **TODO**: Encrypt sensitive data

---

## 🗺️ Roadmap

### Phase 1: MVP ✅ (Current)
- [x] Excel file upload
- [x] Contraídos analysis
- [x] Visual dashboard
- [x] Export functionality

### Phase 2: Enhanced Features (Next)
- [ ] PDF report parsing
- [ ] Advanced filtering and search
- [ ] Custom business rules editor
- [ ] Batch file processing

### Phase 3: Multi-Analysis Support
- [ ] Balance sheet analyzer
- [ ] Invoice analyzer
- [ ] Expense report analyzer
- [ ] Cross-document analysis

### Phase 4: Enterprise Features
- [ ] User authentication
- [ ] Database persistence
- [ ] API versioning
- [ ] Scheduled analysis
- [ ] Email notifications

---

## 🐛 Troubleshooting

### Backend won't start
```bash
# Check Python version
python --version  # Should be 3.11+

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Check port availability
lsof -i :8000
```

### Frontend won't build
```bash
# Clear node modules
rm -rf node_modules package-lock.json
npm install

# Check Node version
node --version  # Should be 18+
```

### Docker issues
```bash
# Rebuild containers
docker-compose down
docker-compose build --no-cache
docker-compose up

# Check logs
docker-compose logs backend
docker-compose logs frontend
```

---

## 📝 License

This project is proprietary software. All rights reserved.

---

## 👥 Contributing

### Adding New Features

1. **Backend**: Create parser/analyzer in `backend/app/core/`
2. **Frontend**: Add components in `frontend/src/components/`
3. **Test**: Add tests for new functionality
4. **Document**: Update README with new features

### Code Style

- **Python**: Follow PEP 8, use Black formatter
- **TypeScript**: Follow ESLint rules
- **Commits**: Use conventional commits format

---

## 📞 Support

For issues or questions:
1. Check API documentation: `/api/docs`
2. Review architecture diagrams in this README
3. Check troubleshooting section

---

## 🎉 Success!

You now have a production-ready, extensible visual tool for analyzing contraídos with the ability to easily add:
- New file formats (PDF, CSV, etc.)
- New analysis types (balances, invoices, etc.)
- New visualizations
- New export formats

**Ready to scale!** 🚀
