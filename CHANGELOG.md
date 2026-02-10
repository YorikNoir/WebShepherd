# Changelog

All notable changes to WebShepherd will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-02-10

### Added
- Initial release of WebShepherd
- FastAPI backend with async SQLAlchemy
- 11 WCAG 2.1 Level AA accessibility rules
  - Perceivable: Image alt text, HTML lang, Page title
  - Operable: Form labels, Button names, Link text
  - Understandable: Heading hierarchy, H1 existence, Page title
  - Robust: Duplicate IDs, ARIA roles
- RESTful API with automatic OpenAPI documentation
- Static HTML/CSS/JS frontend
- Rate limiting (10 scans per hour per IP)
- SQLite database for scan storage
- Mac Mini deployment automation scripts
- Comprehensive README with installation and testing guides
- MIT License
- Contributing guidelines

### Features
- Async URL fetching with configurable timeout
- HTML parsing with BeautifulSoup4
- Accessibility score calculation (0-100)
- Detailed findings with remediation guidance
- WCAG principle categorization
- Scan history and statistics API

### Security
- Rate limiting to prevent abuse
- Request size limits (5MB max)
- Input validation with Pydantic
- CORS configuration for secure deployment

[1.0.0]: https://github.com/YorikNoir/WebShepherd/releases/tag/v1.0.0
