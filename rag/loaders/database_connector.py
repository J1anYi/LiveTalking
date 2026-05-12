"""Database connectors for RAG knowledge base.

Provides base class and implementations for connecting to various databases
and converting query results to document format.
"""

from abc import ABC, abstractmethod
import re
from typing import Any


class BaseDatabaseConnector(ABC):
    """Abstract base class for database connectors.

    Implements DocumentLoader Protocol with load() method.
    Subclasses must implement connect(), disconnect(), and execute_query().
    """

    def __init__(
        self,
        connection_string: str,
        query: str,
        query_params: dict | None = None,
        content_columns: list[str] | None = None,
        metadata_columns: list[str] | None = None,
        db_type: str = "unknown",
    ) -> None:
        """Initialize database connector.

        Args:
            connection_string: Database connection string (DSN)
            query: SQL query to execute
            query_params: Optional parameters for parameterized query
            content_columns: Column names to include in document content
            metadata_columns: Column names to include in metadata (optional)
            db_type: Database type identifier (sqlite, mysql, postgresql, etc.)
        """
        self._connection_string = connection_string
        self._query = query
        self._query_params = query_params or {}
        self._content_columns = content_columns or []
        self._metadata_columns = metadata_columns or []
        self._db_type = db_type
        self._connection: Any = None

    @abstractmethod
    def connect(self) -> None:
        """Establish database connection.

        Raises:
            ConnectionError: If connection cannot be established
        """
        ...

    @abstractmethod
    def disconnect(self) -> None:
        """Close database connection."""
        ...

    @abstractmethod
    def execute_query(self, query: str, params: dict | None = None) -> list[dict]:
        """Execute SQL query and return results as list of dicts.

        Args:
            query: SQL query string
            params: Query parameters for parameterized query

        Returns:
            List of row dictionaries (column_name -> value)

        Raises:
            RuntimeError: If not connected
            Exception: For query execution errors
        """
        ...

    def load(self) -> list[tuple[str, dict]]:
        """Load documents from database query results.

        Implements DocumentLoader Protocol.

        Returns:
            List of (content, metadata) tuples

        Raises:
            RuntimeError: If not connected
        """
        if self._connection is None:
            self.connect()

        rows = self.execute_query(self._query, self._query_params)
        documents = []

        for idx, row in enumerate(rows):
            content, metadata = self._row_to_document(row, idx)
            documents.append((content, metadata))

        return documents

    def _execute_and_format(self) -> list[tuple[str, dict]]:
        """Execute query and format results as documents.

        Returns:
            List of (content, metadata) tuples
        """
        rows = self.execute_query(self._query, self._query_params)
        documents = []

        for idx, row in enumerate(rows):
            content, metadata = self._row_to_document(row, idx)
            documents.append((content, metadata))

        return documents

    def _row_to_document(self, row: dict, row_idx: int) -> tuple[str, dict]:
        """Convert a database row to document format.

        Args:
            row: Row data as dictionary
            row_idx: Row index for identification

        Returns:
            Tuple of (content, metadata)
        """
        # Build content from content_columns
        content_parts = []
        if self._content_columns:
            for col in self._content_columns:
                if col in row and row[col] is not None:
                    content_parts.append(f"{col}: {row[col]}")
        else:
            # If no content_columns specified, use all columns
            for col, val in row.items():
                if val is not None:
                    content_parts.append(f"{col}: {val}")

        content = "\n".join(content_parts)

        # Build metadata
        metadata: dict[str, Any] = {
            "source": self._safe_connection_string(),
            "type": self._db_type,
            "table": self._extract_table_name(),
            "row_id": row_idx,
        }

        # Add metadata columns if specified
        if self._metadata_columns:
            for col in self._metadata_columns:
                if col in row:
                    metadata[col] = row[col]

        return content, metadata

    def _safe_connection_string(self) -> str:
        """Return connection string with password hidden.

        Returns:
            Connection string with password replaced by '***'
        """
        # Hide password in connection string
        # Patterns: password=xxx, pwd=xxx, :password@, :pwd@
        safe_str = self._connection_string
        safe_str = re.sub(r"password=([^;@]+)", "password=***", safe_str, flags=re.IGNORECASE)
        safe_str = re.sub(r"pwd=([^;@]+)", "pwd=***", safe_str, flags=re.IGNORECASE)
        safe_str = re.sub(r":([^@]+)@", ":***@", safe_str)
        return safe_str

    def _extract_table_name(self) -> str | None:
        """Extract table name from SQL query.

        Returns:
            Table name if found, None otherwise
        """
        # Simple pattern matching for FROM clause
        match = re.search(r"\bFROM\s+([a-zA-Z_][a-zA-Z0-9_]*)", self._query, re.IGNORECASE)
        if match:
            return match.group(1)
        return None


class SQLiteConnector(BaseDatabaseConnector):
    """SQLite database connector.

    Uses Python's standard library sqlite3 module.
    """

    def __init__(
        self,
        connection_string: str,
        query: str,
        query_params: dict | None = None,
        content_columns: list[str] | None = None,
        metadata_columns: list[str] | None = None,
    ) -> None:
        """Initialize SQLite connector.

        Args:
            connection_string: Path to SQLite database file
            query: SQL query to execute
            query_params: Optional parameters for parameterized query
            content_columns: Column names to include in document content
            metadata_columns: Column names to include in metadata
        """
        super().__init__(
            connection_string=connection_string,
            query=query,
            query_params=query_params,
            content_columns=content_columns,
            metadata_columns=metadata_columns,
            db_type="sqlite",
        )

    def connect(self) -> None:
        """Establish SQLite database connection.

        Raises:
            ConnectionError: If database file cannot be opened
        """
        import sqlite3

        try:
            self._connection = sqlite3.connect(self._connection_string)
            # Enable dictionary access to rows
            self._connection.row_factory = sqlite3.Row
        except Exception as e:
            raise ConnectionError(f"Failed to connect to SQLite database: {e}")

    def disconnect(self) -> None:
        """Close SQLite database connection."""
        if self._connection is not None:
            self._connection.close()
            self._connection = None

    def execute_query(self, query: str, params: dict | None = None) -> list[dict]:
        """Execute SQL query and return results as list of dicts.

        Args:
            query: SQL query string
            params: Query parameters for parameterized query

        Returns:
            List of row dictionaries

        Raises:
            RuntimeError: If not connected
            Exception: For query execution errors
        """
        if self._connection is None:
            raise RuntimeError("Not connected to database. Call connect() first.")

        cursor = self._connection.cursor()

        # Execute query with or without parameters
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)

        # Convert sqlite3.Row objects to dicts
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
