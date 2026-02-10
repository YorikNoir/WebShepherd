# Screenshots

## 📸 Adding Screenshots to This Repository

To make this project more visually appealing for recruiters and contributors, consider adding screenshots in this directory:

### Recommended Screenshots

1. **`frontend-home.png`** - Main scan form interface
2. **`results-overview.png`** - Scan results with score circle
3. **`findings-detail.png`** - Detailed accessibility findings
4. **`api-docs.png`** - FastAPI Swagger UI documentation

### How to Add

```bash
# Take screenshots of the running application
# Save them to this directory
# Update README.md with image references

# Example README.md syntax:
# ![WebShepherd Interface](screenshots/frontend-home.png)
```

### Screenshot Guidelines

- **Resolution**: 1920x1080 or similar standard resolution
- **Format**: PNG for UI screenshots, JPEG for photos
- **Content**: Show the application in use with example data
- **Privacy**: Don't include real personal URLs or sensitive data

### Quick Screenshot Guide

1. Start the application: `uvicorn main:app --reload`
2. Open `frontend/index.html` in browser
3. Scan a public test URL (e.g., https://example.com)
4. Capture screenshots of each view
5. Save to this directory
6. Update README.md with `![Description](screenshots/filename.png)`

---

**Note**: Screenshots are not included in the initial commit to keep the repository size small. Add them when preparing for portfolio presentation.
