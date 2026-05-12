"""Document processor for RAG knowledge base.

Handles text chunking with Chinese-optimized separators.

Verification results:
    - chunk_size: 800
    - chunk_overlap: 100
"""

from langchain_text_splitters import RecursiveCharacterTextSplitter

CHINESE_SEPARATORS = ["\n\n", "\n", "。", "！", "？", "；", "，", " "]


class DocumentProcessor:
    """Document processor for loading and chunking text.

    Verification results:
        - chunk_size: 800
        - chunk_overlap: 100
    """

    def __init__(
        self,
        chunk_size: int = 800,
        chunk_overlap: int = 100,
        separators: list[str] | None = None,
    ) -> None:
        """Initialize document processor.

        Args:
            chunk_size: Maximum chunk size in characters
            chunk_overlap: Overlap between chunks in characters
            separators: List of separators, defaults to Chinese-optimized separators
        """
        self._chunk_size = chunk_size
        self._chunk_overlap = chunk_overlap
        self._separators = separators or CHINESE_SEPARATORS

        self._splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=self._separators,
        )

    def process_text(
        self,
        text: str,
        metadata: dict | None = None,
    ) -> list[dict]:
        """Split text into chunks.

        Args:
            text: Input text to split
            metadata: Optional metadata to attach to each chunk

        Returns:
            List of chunks, each containing: {"text": str, "metadata": dict}
        """
        chunks = self._splitter.split_text(text)
        return [{"text": chunk, "metadata": metadata or {}} for chunk in chunks]

    def process_file(self, file_path: str) -> list[dict]:
        """Load and split a file.

        Args:
            file_path: Path to the file

        Returns:
            List of chunks with metadata

        Raises:
            FileNotFoundError: If file does not exist
            ValueError: If file type is not supported
        """
        from pathlib import Path

        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        ext = path.suffix.lower()

        if ext == ".pdf":
            text = self._load_pdf(file_path)
        elif ext in (".txt", ".md"):
            text = self._load_text(file_path)
        else:
            raise ValueError(f"Unsupported file type: {ext}")

        metadata = {
            "source": str(path),
            "type": ext[1:],
        }

        return self.process_text(text, metadata)

    def _load_text(self, file_path: str) -> str:
        """Load text file."""
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()

    def _load_pdf(self, file_path: str) -> str:
        """Load PDF file."""
        try:
            from pypdf import PdfReader
        except ImportError:
            raise ImportError(
                "pypdf is required for PDF support. "
                "Install with: pip install pypdf"
            )

        reader = PdfReader(file_path)
        pages = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                pages.append(text)
        return "\n\n".join(pages)

    def process_directory(
        self,
        dir_path: str,
        recursive: bool = True,
    ) -> list[dict]:
        """Process all supported files in a directory.

        Args:
            dir_path: Directory path
            recursive: Whether to search recursively

        Returns:
            List of all chunks from all files
        """
        from pathlib import Path

        results = []
        path = Path(dir_path)

        if not path.exists():
            raise FileNotFoundError(f"Directory not found: {dir_path}")

        supported_extensions = {".txt", ".md", ".pdf"}

        if recursive:
            pattern = "**/*"
        else:
            pattern = "*"

        for file_path in path.glob(pattern):
            if file_path.is_file() and file_path.suffix.lower() in supported_extensions:
                try:
                    chunks = self.process_file(str(file_path))
                    results.extend(chunks)
                except Exception:
                    continue

        return results

    @property
    def chunk_size(self) -> int:
        """Return chunk size."""
        return self._chunk_size

    @property
    def chunk_overlap(self) -> int:
        """Return chunk overlap."""
        return self._chunk_overlap

    @property
    def separators(self) -> list[str]:
        """Return separators."""
        return self._separators
