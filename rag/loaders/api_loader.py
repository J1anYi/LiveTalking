"""REST API loader for RAG knowledge base.

Supports GET/POST requests with authentication and JSONPath data extraction.
"""

import json
from datetime import datetime
from typing import Any
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError


class APILoader:
    """REST API data loader.

    Fetches data from REST API endpoints and converts to document format.
    Supports GET/POST methods with Bearer Token and API Key authentication.
    """

    def __init__(
        self,
        url: str,
        method: str = "GET",
        headers: dict[str, str] | None = None,
        body: dict[str, Any] | None = None,
        data_path: str | None = None,
        auth: dict[str, str] | None = None,
        timeout: int = 30,
    ) -> None:
        """Initialize API loader.

        Args:
            url: API endpoint URL
            method: HTTP method (GET or POST), default: GET
            headers: Optional HTTP headers
            body: Optional request body for POST requests
            data_path: Optional JSONPath expression to extract data from response
            auth: Optional authentication config:
                - {"type": "bearer", "token": "xxx"} for Bearer Token
                - {"type": "api_key", "key": "xxx", "header": "X-API-Key"} for API Key
            timeout: Request timeout in seconds, default: 30
        """
        self._url = url
        self._method = method.upper()
        self._headers = headers or {}
        self._body = body
        self._data_path = data_path
        self._auth = auth or {}
        self._timeout = timeout

        # Validate method
        if self._method not in ("GET", "POST"):
            raise ValueError(f"Unsupported HTTP method: {self._method}. Use GET or POST.")

    def load(self) -> list[tuple[str, dict]]:
        """Load documents from API response.

        Returns:
            List of (content, metadata) tuples

        Raises:
            RuntimeError: If API request fails
            ValueError: If response is not valid JSON
        """
        # Prepare headers with authentication
        headers = dict(self._headers)
        self._apply_auth(headers)

        # Prepare request
        data = None
        if self._method == "POST" and self._body:
            data = json.dumps(self._body).encode("utf-8")
            if "Content-Type" not in headers:
                headers["Content-Type"] = "application/json"

        request = Request(
            self._url,
            data=data,
            headers=headers,
            method=self._method,
        )

        # Execute request
        try:
            response = urlopen(request, timeout=self._timeout)
            response_data = response.read().decode("utf-8")
            response_headers = dict(response.headers)
        except HTTPError as e:
            raise RuntimeError(f"API request failed with HTTP {e.code}: {e.reason}")
        except URLError as e:
            raise RuntimeError(f"API request failed: {e.reason}")
        except Exception as e:
            raise RuntimeError(f"API request failed: {e}")

        # Parse JSON response
        try:
            json_data = json.loads(response_data)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON response: {e}")

        # Extract data using JSONPath if specified
        extracted_data = self._extract_data(json_data)

        # Convert to documents
        documents = self._to_documents(extracted_data, response_headers)

        return documents

    def _apply_auth(self, headers: dict[str, str]) -> None:
        """Apply authentication to headers.

        Args:
            headers: Headers dict to modify in place
        """
        if not self._auth:
            return

        auth_type = self._auth.get("type", "").lower()

        if auth_type == "bearer":
            token = self._auth.get("token", "")
            headers["Authorization"] = f"Bearer {token}"
        elif auth_type == "api_key":
            key = self._auth.get("key", "")
            header_name = self._auth.get("header", "X-API-Key")
            headers[header_name] = key

    def _extract_data(self, json_data: Any) -> Any:
        """Extract data from JSON using JSONPath.

        Args:
            json_data: Parsed JSON data

        Returns:
            Extracted data (original data if no data_path)
        """
        if not self._data_path:
            return json_data

        # Simple JSONPath implementation for basic paths
        # Supports: $.field, $.field.nested, $.field[0], $.field[*]
        result = json_data
        path = self._data_path

        # Normalize path
        if path.startswith("$."):
            path = path[2:]
        elif path.startswith("$"):
            path = path[1:]

        # Split path into parts
        parts = self._parse_jsonpath(path)

        for part in parts:
            if result is None:
                break

            if isinstance(part, int):
                # Array index
                if isinstance(result, list) and 0 <= part < len(result):
                    result = result[part]
                else:
                    result = None
            elif part == "*":
                # Wildcard: return all items
                if isinstance(result, list):
                    # Continue processing for each item
                    pass
                elif isinstance(result, dict):
                    result = list(result.values())
            else:
                # Object key
                if isinstance(result, dict) and part in result:
                    result = result[part]
                else:
                    result = None

        return result

    def _parse_jsonpath(self, path: str) -> list[str | int]:
        """Parse JSONPath into parts.

        Args:
            path: JSONPath string (without $. prefix)

        Returns:
            List of field names and array indices
        """
        parts: list[str | int] = []
        current = ""
        in_bracket = False

        for char in path:
            if char == "." and not in_bracket:
                if current:
                    parts.append(self._try_int(current))
                    current = ""
            elif char == "[":
                if current:
                    parts.append(self._try_int(current))
                    current = ""
                in_bracket = True
            elif char == "]":
                if current:
                    parts.append(self._try_int(current))
                    current = ""
                in_bracket = False
            else:
                current += char

        if current:
            parts.append(self._try_int(current))

        return parts

    def _try_int(self, value: str) -> str | int:
        """Try to convert string to int if possible.

        Args:
            value: String value

        Returns:
            Integer if parseable, original string otherwise
        """
        try:
            return int(value)
        except ValueError:
            return value

    def _to_documents(
        self,
        data: Any,
        response_headers: dict[str, str],
    ) -> list[tuple[str, dict]]:
        """Convert extracted data to documents.

        Args:
            data: Extracted data from API
            response_headers: HTTP response headers

        Returns:
            List of (content, metadata) tuples
        """
        # Get current timestamp
        retrieved_at = datetime.utcnow().isoformat()

        # Base metadata
        base_metadata: dict[str, Any] = {
            "source": self._url,
            "type": "api",
            "method": self._method,
            "retrieved_at": retrieved_at,
        }

        # Add content type if available
        content_type = response_headers.get("Content-Type", "")
        if content_type:
            base_metadata["content_type"] = content_type.split(";")[0]

        # Convert data to documents
        documents: list[tuple[str, dict]] = []

        if isinstance(data, list):
            # Multiple items
            for idx, item in enumerate(data):
                content, item_metadata = self._item_to_document(
                    item, idx, base_metadata.copy()
                )
                documents.append((content, item_metadata))
        else:
            # Single item
            content, metadata = self._item_to_document(data, 0, base_metadata.copy())
            documents.append((content, metadata))

        return documents

    def _item_to_document(
        self,
        item: Any,
        index: int,
        metadata: dict[str, Any],
    ) -> tuple[str, dict]:
        """Convert a single item to document format.

        Args:
            item: Data item
            index: Item index
            metadata: Base metadata dict

        Returns:
            Tuple of (content, metadata)
        """
        if isinstance(item, dict):
            # Convert dict to formatted string
            content = json.dumps(item, ensure_ascii=False, indent=2)
            metadata["item_index"] = index
            metadata["size"] = len(content)
        elif isinstance(item, str):
            content = item
            metadata["item_index"] = index
            metadata["size"] = len(content)
        else:
            content = str(item)
            metadata["item_index"] = index
            metadata["size"] = len(content)

        return content, metadata