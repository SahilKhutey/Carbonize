"""
Validate all links in documentation
"""
import re
from pathlib import Path
from typing import List, Tuple
import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LinkValidator:
    """Validate internal links in Markdown files."""
    
    def __init__(self, docs_dir: str = 'docs'):
        self.docs_dir = Path(docs_dir)
        self.broken_links: List[Tuple[Path, str, str, int]] = []
        self.checked = 0
    
    def validate_all(self) -> bool:
        """Validate all Markdown files."""
        logger.info(f"Validating links in {self.docs_dir}")
        if not self.docs_dir.exists():
            logger.info("Docs directory empty or not created yet.")
            return True
            
        for md_file in self.docs_dir.rglob('*.md'):
            self._validate_file(md_file)
        
        if self.broken_links:
            logger.error(f"\n✗ Found {len(self.broken_links)} broken links:")
            for file, link, line_content, line_num in self.broken_links:
                logger.error(f"  {file}:{line_num} -> {link}")
            return False
        
        logger.info(f"✓ All {self.checked} links are valid")
        return True
    
    def _validate_file(self, file_path: Path):
        with open(file_path, encoding='utf-8') as f:
            content = f.read()
        
        pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        matches = re.finditer(pattern, content)
        for match in matches:
            link_text, link_url = match.groups()
            line_num = content[:match.start()].count('\n') + 1
            if link_url.startswith('#') or link_url.startswith('mailto:') or link_url.startswith(('http://', 'https://')):
                continue
            self.checked += 1
            if not self._validate_internal_link(file_path, link_url):
                self.broken_links.append((file_path, link_url, match.group(0), line_num))
    
    def _validate_internal_link(self, source_file: Path, link: str) -> bool:
        if '#' in link:
            link = link.split('#')[0]
        if not link:
            return True
        target = (source_file.parent / link).resolve()
        return target.exists()


if __name__ == '__main__':
    validator = LinkValidator()
    success = validator.validate_all()
    sys.exit(0 if success else 1)
