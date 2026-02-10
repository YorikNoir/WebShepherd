# Contributing to WebShepherd

Thank you for your interest in contributing to WebShepherd! This document provides guidelines for contributing to the project.

## 🐛 Reporting Bugs

If you find a bug, please create an issue with:
- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Your environment (OS, Python version, etc.)

## 💡 Suggesting Enhancements

Feature requests are welcome! Please include:
- Clear use case
- Expected behavior
- Why this would be valuable for accessibility checking

## 🔧 Development Setup

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/YorikNoir/WebShepherd.git
   cd WebShepherd
   ```

2. **Set up Python environment**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Run tests**
   ```bash
   pytest tests/ -v
   ```

4. **Start development server**
   ```bash
   uvicorn main:app --reload
   ```

## 📝 Code Style

- **Python**: Follow PEP 8, use `black` for formatting, `isort` for imports
- **JavaScript**: Use ES6+ features, maintain accessibility standards
- **Comments**: Write clear, concise comments explaining "why", not "what"

## ✅ Pull Request Process

1. Create a feature branch (`git checkout -b feature/AmazingFeature`)
2. Make your changes and commit (`git commit -m 'Add AmazingFeature'`)
3. Run tests and linters
4. Push to your fork (`git push origin feature/AmazingFeature`)
5. Open a Pull Request with a clear description

## 🧪 Testing

All new features should include:
- Unit tests for backend logic
- Integration tests for API endpoints
- Manual testing checklist for UI changes

## 🌐 Adding New WCAG Rules

When adding new accessibility checks:

1. Create a new rule class in `backend/scanner/rules/`
2. Inherit from `WCAGRule` base class
3. Implement required methods:
   - `check()`: Main validation logic
   - Set `wcag_reference`, `level`, `principle`, `guideline`
4. Add rule to `ALL_RULES` in `backend/scanner/rules/__init__.py`
5. Include test cases with sample HTML
6. Update README.md with the new check

Example:
```python
class NewAccessibilityRule(WCAGRule):
    name = "Descriptive Rule Name"
    wcag_reference = "X.X.X"
    level = "AA"
    principle = "Perceivable"
    guideline = "X.X Description"

    async def check(self, soup: BeautifulSoup, url: str) -> List[Finding]:
        findings = []
        # Your validation logic here
        return findings
```

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

## ❓ Questions?

Feel free to open an issue for questions about contributing!
