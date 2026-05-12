"""Local file loader for RAG knowledge base.

Supports multiple document formats: .txt, .md, .pdf
"""

import os
from pathlib import Path

DEFAULT_EXTENSIONS = [".txt", ".md", ".pdf", ".docx"]


class FileLoader:
    """Local file loader.

    Supports loading documents from various file formats.
    """

    def __init__(
        self,
        supported_extensions: list[str] | None = None,
        encoding: str = "utf-8",
    ) -> None:
        """Initialize file loader.

        Args:
            supported_extensions: List of supported file extensions, default: .txt, .md, .pdf
            encoding: Default file encoding for text files
        """
        self._extensions = supported_extensions or DEFAULT_EXTENSIONS
        self._encoding = encoding

    def load(self, file_path: str) -> tuple[str, dict]:
        """Load a single file.

        Args:
            file_path: Path to the file

        Returns:
            Tuple of (content, metadata)
            metadata contains: source, type, size

        Raises:
            ValueError: If file extension is not supported
            FileNotFoundError: If file does not exist
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        ext = path.suffix.lower()
        if ext not in self._extensions:
            raise ValueError(f"Unsupported file extension: {ext}")

        if ext == ".pdf":
            content = self._load_pdf(file_path)
        elif ext == ".docx":
            content = self._load_docx(file_path)
        else:
            content = self._load_text(file_path)

        metadata = {
            "source": str(path),
            "type": ext[1:],  # Remove leading dot
            "size": len(content),
        }

        return content, metadata

    def _load_text(self, file_path: str) -> str:
        """Load text file with specified encoding."""
        with open(file_path, "r", encoding=self._encoding) as f:
            return f.read()

    def _load_pdf(self, file_path: str) -> str:
        """Load PDF file using pypdf."""
        try:
            from pypdf import PdfReader
        except ImportError:
            raise ImportError(
                "pypdf is required for PDF support. "
                "Install it with: pip install pypdf"
            )

        reader = PdfReader(file_path)
        pages = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                pages.append(text)
        return "\n\n".join(pages)

    def _load_docx(self, file_path: str) -> str:
        """Load DOCX file using python-docx.

        Extracts text from paragraphs, preserving document structure.

        Args:
            file_path: Path to the DOCX file

        Returns:
            Extracted text content joined by newlines

        Raises:
            ImportError: If python-docx is not installed
        """
        try:
            from docx import Document
        except ImportError:
            raise ImportError(
                "python-docx is required for DOCX support. "
                "Install it with: pip install python-docx"
            )

        doc = Document(file_path)
        paragraphs = []
        for para in doc.paragraphs:
            if para.text.strip():
                paragraphs.append(para.text)
        return "\n\n".join(paragraphs)

    def load_directory(
        self,
        dir_path: str,
        recursive: bool = True,
    ) -> list[tuple[str, dict]]:
        """Load all supported files from a directory.

        Args:
            dir_path: Directory path
            recursive: Whether to search recursively

        Returns:
            List of (content, metadata) tuples
        """
        results = []
        path = Path(dir_path)

        if not path.exists():
            raise FileNotFoundError(f"Directory not found: {dir_path}")

        if recursive:
            pattern = "**/*"
        else:
            pattern = "*"

        for file_path in path.glob(pattern):
            if file_path.is_file() and file_path.suffix.lower() in self._extensions:
                try:
                    content, metadata = self.load(str(file_path))
                    results.append((content, metadata))
                except Exception:
                    continue  # Skip files that fail to load

        return results

    @property
    def supported_extensions(self) -> list[str]:
        """Return supported extensions."""
        return self._extensions
