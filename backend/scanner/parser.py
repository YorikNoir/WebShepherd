"""
HTML Parser - Parses HTML and provides convenient access to elements
"""
from bs4 import BeautifulSoup
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


class ParsedHTML:
    """Wrapper for parsed HTML with convenience methods"""

    def __init__(self, soup: BeautifulSoup, raw_html: str):
        self.soup = soup
        self.raw_html = raw_html

    def find_all(self, tag: str, **kwargs) -> List:
        """Find all elements matching tag and attributes"""
        return self.soup.find_all(tag, **kwargs)

    def find(self, tag: str, **kwargs) -> Optional:
        """Find first element matching tag and attributes"""
        return self.soup.find(tag, **kwargs)

    def get_text(self) -> str:
        """Get all text content"""
        return self.soup.get_text()

    @property
    def html_tag(self):
        """Get <html> tag"""
        return self.soup.find('html')

    @property
    def title(self) -> Optional[str]:
        """Get page title"""
        title_tag = self.soup.find('title')
        return title_tag.get_text().strip() if title_tag else None

    @property
    def images(self) -> List:
        """Get all <img> tags"""
        return self.soup.find_all('img')

    @property
    def links(self) -> List:
        """Get all <a> tags"""
        return self.soup.find_all('a')

    @property
    def forms(self) -> List:
        """Get all <form> tags"""
        return self.soup.find_all('form')

    @property
    def inputs(self) -> List:
        """Get all input elements"""
        return self.soup.find_all(['input', 'textarea', 'select'])

    @property
    def headings(self) -> List:
        """Get all heading tags (h1-h6)"""
        return self.soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])

    @property
    def buttons(self) -> List:
        """Get all buttons"""
        return self.soup.find_all(['button']) + self.soup.find_all('input', type='button')

    def get_elements_with_role(self, role: str) -> List:
        """Get all elements with specific ARIA role"""
        return self.soup.find_all(attrs={"role": role})

    def get_elements_with_aria_attribute(self, attr: str) -> List:
        """Get all elements with specific ARIA attribute"""
        return self.soup.find_all(attrs={attr: True})

    def get_all_ids(self) -> List[str]:
        """Get all ID attributes"""
        return [elem.get('id') for elem in self.soup.find_all(id=True)]


class HTMLParser:
    """HTML parser using BeautifulSoup"""

    def parse(self, html: str) -> ParsedHTML:
        """
        Parse HTML string into ParsedHTML object

        Args:
            html: HTML content string

        Returns:
            ParsedHTML object with convenience methods
        """
        try:
            soup = BeautifulSoup(html, 'lxml')
            logger.info(f"Successfully parsed HTML ({len(html)} chars)")
            return ParsedHTML(soup, html)
        except Exception as e:
            logger.error(f"Failed to parse HTML: {str(e)}")
            # Fallback to html.parser
            soup = BeautifulSoup(html, 'html.parser')
            logger.info("Parsed with fallback html.parser")
            return ParsedHTML(soup, html)
