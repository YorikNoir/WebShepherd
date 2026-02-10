# WebShepherd 🐑

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688?logo=fastapi&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)
![WCAG](https://img.shields.io/badge/WCAG-2.1%20AA-purple)

**Guiding your website to WCAG 2.1 AA compliance**

A lightweight, fast accessibility checker that analyzes public URLs for WCAG 2.1 Level AA compliance, helping ensure conformance with Germany's **Barrierefreie-Informationstechnik-Verordnung (BITV 2.0)**.

Built with **FastAPI** + **Vanilla JS** as a portfolio project demonstrating full-stack web development and accessibility expertise.

---

## 🎯 Features

- **Automated WCAG 2.1 AA Checks** - Detects common accessibility issues
- **Real-time Scanning** - Async URL analysis with live progress
- **Educational Results** - Clear explanations and remediation tips
- **RESTful API** - Well-documented endpoints with Swagger UI
- **Lightweight** - No headless browser needed, pure HTML parsing
- **Rate Limited** - Safe for public deployment

---

## 🔍 What WebShepherd Checks

### Perceivable
- ✅ Missing `alt` attributes on images
- ✅ Missing `lang` attribute on HTML
- ✅ Basic color contrast issues

### Operable
- ✅ Form inputs without labels
- ✅ Buttons without accessible names
- ✅ Keyboard accessibility hints

### Understandable
- ✅ Empty or vague link text
- ✅ Skipped heading levels (h1→h3)

### Robust
- ✅ Invalid ARIA roles
- ✅ Duplicate IDs

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 16+ (for frontend)
- pip and npm

### Installation

```bash
# Clone the repository
git clone https://github.com/YorikNoir/WebShepherd.git
cd WebShepherd

# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Frontend setup
cd ../frontend
npm install

# Run the application
# Terminal 1 - Backend
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2 - Frontend
cd frontend
npm start
```

Visit **http://localhost:3000** to use WebShepherd!

API documentation available at **http://localhost:8000/docs**

---

## 📁 Project Structure

```
WebShepherd/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── models.py            # Pydantic models
│   ├── scanner/
│   │   ├── __init__.py
│   │   ├── fetcher.py       # URL fetching logic
│   │   ├── parser.py        # HTML parsing
│   │   └── rules/           # WCAG check implementations
│   ├── database.py          # SQLite/PostgreSQL setup
│   ├── config.py            # Configuration
│   └── requirements.txt
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ScanForm.jsx
│   │   │   ├── Results.jsx
│   │   │   └── FindingCard.jsx
│   │   ├── App.jsx
│   │   └── index.js
│   └── package.json
├── deployment/
│   ├── docker-compose.yml
│   ├── nginx.conf
│   └── systemd/
├── docs/
│   ├── DESIGN.md
│   └── API.md
└── README.md
```

---

## 🎓 Educational Focus

This tool is designed to:
- Catch **80% of common accessibility issues** automatically
- Provide **learning opportunities** with detailed explanations
- Encourage **manual testing** for issues that can't be automated
- Demonstrate **best practices** in API and UI design

**Note:** Automated tools can only catch ~30-40% of WCAG issues. Always combine with manual testing!

---

## 🔒 Security & Performance

- **URL Validation** - Blocks private IPs and invalid protocols
- **Rate Limiting** - Prevents abuse (10 scans/hour per IP)
- **Size Limits** - Max 5MB HTML documents
- **Timeout Protection** - 10-second request timeout
- **No JavaScript Execution** - Safe static analysis only

---

## 🛠️ Technology Stack

**Backend:**
- FastAPI (async Python web framework)
- BeautifulSoup4 (HTML parsing)
- httpx (async HTTP client)
- SQLite/PostgreSQL (scan storage)
- Pydantic (data validation)

**Frontend:**
- React 18
- Axios (HTTP client)
- CSS3 with responsive design
- Bootstrap 5

**Deployment:**
- Gunicorn (WSGI server)
- Nginx (reverse proxy)
- systemd (process management)

---

## 📊 API Documentation

### POST /api/scan/
Submit a URL for accessibility scanning

**Request:**
```json
{
  "url": "https://example.com"
}
```

**Response:**
```json
{
  "scan_id": "abc123",
  "status": "pending",
  "created_at": "2026-02-10T14:30:00Z"
}
```

### GET /api/scan/{scan_id}
Retrieve scan results

**Response:**
```json
{
  "scan_id": "abc123",
  "url": "https://example.com",
  "status": "complete",
  "score": 78.5,
  "findings": [
    {
      "rule_code": "IMG_ALT_MISSING",
      "severity": "fail",
      "message": "Image missing alt text",
      "element": "<img src=\"logo.png\">",
      "wcag_reference": "1.1.1",
      "remediation": "Add descriptive alt text to all images"
    }
  ],
  "completed_at": "2026-02-10T14:30:05Z"
}
```

Full API documentation: **[http://localhost:8000/docs](http://localhost:8000/docs)**

---

## 🌐 Deployment

### Production Deployment

See **[deployment/README.md](deployment/README.md)** for full deployment instructions including:
- Docker setup
- Nginx configuration
- systemd service files
- SSL/TLS setup
- Environment variables

### Environment Variables

```bash
# .env file
DATABASE_URL=sqlite:///./webshepherd.db
ALLOWED_ORIGINS=https://yorik.space
RATE_LIMIT_PER_HOUR=10
MAX_HTML_SIZE_MB=5
REQUEST_TIMEOUT=10
```

---

## 🧪 Development

### Running Tests
```bash
cd backend
pytest tests/ -v
```

### Manual Testing Checklist

**Positive Test Cases:**
- [ ] Submit valid URL (e.g., `https://example.com`)
- [ ] Verify scan completes successfully
- [ ] Check score calculation (0-100 range)
- [ ] Verify findings are categorized correctly
- [ ] Test with accessible website (high score expected)
- [ ] Test with inaccessible website (low score expected)

**Negative Test Cases:**
- [ ] Submit invalid URL (missing protocol)
- [ ] Submit unreachable URL (should fail gracefully)
- [ ] Submit URL with timeout (check error handling)
- [ ] Exceed rate limit (10 scans/hour per IP)
- [ ] Submit extremely large page (>5MB)

**API Testing:**
```bash
# Submit scan
curl -X POST http://localhost:8000/api/scan/ \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'

# Get scan results
curl http://localhost:8000/api/scan/{scan_id}

# Get statistics
curl http://localhost:8000/api/stats
```

**WCAG Rule Testing:**

Test each rule individually with purpose-built test pages:
- **Image Alt Text** (`1.1.1`): Page with `<img>` without alt attribute
- **HTML Lang** (`3.1.1`): Page missing `<html lang="...">` attribute
- **Page Title** (`2.4.2`): Page without `<title>` tag
- **Form Labels** (`3.3.2`): Form `<input>` without associated `<label>`
- **Button Names** (`4.1.2`): `<button>` without text content or aria-label
- **Link Text** (`2.4.4`): Links with generic text like "click here"
- **Heading Hierarchy** (`1.3.1`): Headings that skip levels (h1 → h3)
- **H1 Exists** (`2.4.6`): Page without any `<h1>` element
- **Duplicate IDs** (`4.1.1`): Multiple elements with same `id` attribute
- **ARIA Roles** (`4.1.2`): Invalid ARIA role values

### Code Quality
```bash
# Format code
black .
isort .

# Lint
flake8
mypy .
```

---

## 📝 License

MIT License - see LICENSE file for details

---

## 👤 Author

**Yorik Schwarz**
- Portfolio: [https://yorik.space](https://yorik.space)
- GitHub: [@YorikNoir](https://github.com/YorikNoir)
- LinkedIn: [Yorik Schwarz](https://linkedin.com/in/yorik-schwarz)

---

## 🤝 Contributing

This is a portfolio project, but suggestions and feedback are welcome! Please open an issue to discuss proposed changes.

---

## 🙏 Acknowledgments

- WCAG 2.1 Guidelines - W3C
- BITV 2.0 - German accessibility standards
- Inspired by axe-core and Lighthouse accessibility audits

---

## 📚 Resources

- [WCAG 2.1 Quick Reference](https://www.w3.org/WAI/WCAG21/quickref/)
- [WebAIM Resources](https://webaim.org/resources/)
- [BITV 2.0 (German)](https://www.bitvtest.de/bitv_test/das_testverfahren_im_detail/bitv_2_0.html)
- [ARIA Authoring Practices](https://www.w3.org/WAI/ARIA/apg/)

---

**Live Demo:** [https://yorik.space/webshepherd](https://yorik.space/webshepherd)
