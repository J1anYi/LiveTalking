"""Unit tests for database connector module."""

import pytest
import tempfile
import os
import sqlite3


class TestSQLiteConnector:
    """Tests for SQLiteConnector class."""

    def test_connect_creates_connection(self):
        """Test connect() establishes connection."""
        from rag.loaders.database_connector import SQLiteConnector

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test.db")
            connector = SQLiteConnector(
                connection_string=db_path,
                query="SELECT 1",
            )

            connector.connect()

            assert connector._connection is not None
            connector.disconnect()

    def test_disconnect_closes_connection(self):
        """Test disconnect() closes connection."""
        from rag.loaders.database_connector import SQLiteConnector

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test.db")
            connector = SQLiteConnector(
                connection_string=db_path,
                query="SELECT 1",
            )

            connector.connect()
            assert connector._connection is not None

            connector.disconnect()
            assert connector._connection is None

    def test_execute_query_returns_results(self):
        """Test execute_query returns query results."""
        from rag.loaders.database_connector import SQLiteConnector

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test.db")
            connector = SQLiteConnector(
                connection_string=db_path,
                query="SELECT * FROM test",
            )

            connector.connect()

            # Create test table and insert data
            connector._connection.execute("CREATE TABLE test (id INTEGER, name TEXT)")
            connector._connection.execute("INSERT INTO test VALUES (1, 'alice')")
            connector._connection.execute("INSERT INTO test VALUES (2, 'bob')")
            connector._connection.commit()

            # Execute query
            results = connector.execute_query("SELECT * FROM test")

            assert len(results) == 2
            assert results[0]["name"] == "alice"
            assert results[1]["name"] == "bob"

            connector.disconnect()

    def test_execute_query_with_params(self):
        """Test parameterized query."""
        from rag.loaders.database_connector import SQLiteConnector

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test.db")
            connector = SQLiteConnector(
                connection_string=db_path,
                query="SELECT * FROM test WHERE id = :id",
            )

            connector.connect()

            # Create test table
            connector._connection.execute("CREATE TABLE test (id INTEGER, name TEXT)")
            connector._connection.execute("INSERT INTO test VALUES (1, 'alice')")
            connector._connection.execute("INSERT INTO test VALUES (2, 'bob')")
            connector._connection.commit()

            # Execute with params
            results = connector.execute_query(
                "SELECT * FROM test WHERE id = :id",
                params={"id": 1}
            )

            assert len(results) == 1
            assert results[0]["name"] == "alice"

            connector.disconnect()

    def test_execute_query_raises_when_not_connected(self):
        """Test execute_query raises RuntimeError when not connected."""
        from rag.loaders.database_connector import SQLiteConnector

        connector = SQLiteConnector(
            connection_string=":memory:",
            query="SELECT 1",
        )

        with pytest.raises(RuntimeError, match="Not connected"):
            connector.execute_query("SELECT 1")

    def test_load_returns_documents(self):
        """Test load() returns document list."""
        from rag.loaders.database_connector import SQLiteConnector

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test.db")
            connector = SQLiteConnector(
                connection_string=db_path,
                query="SELECT id, name FROM users",
                content_columns=["name"],
            )

            connector.connect()

            # Create test data
            connector._connection.execute("CREATE TABLE users (id INTEGER, name TEXT)")
            connector._connection.execute("INSERT INTO users VALUES (1, 'Alice')")
            connector._connection.execute("INSERT INTO users VALUES (2, 'Bob')")
            connector._connection.commit()

            # Load documents
            documents = connector.load()

            assert len(documents) == 2
            assert "Alice" in documents[0][0]  # Content
            assert documents[0][1]["type"] == "sqlite"  # Metadata

            connector.disconnect()

    def test_load_with_content_columns(self):
        """Test content_columns filters content."""
        from rag.loaders.database_connector import SQLiteConnector

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test.db")
            connector = SQLiteConnector(
                connection_string=db_path,
                query="SELECT id, title, description FROM articles",
                content_columns=["title", "description"],
            )

            connector.connect()

            # Create test data
            connector._connection.execute(
                "CREATE TABLE articles (id INTEGER, title TEXT, description TEXT)"
            )
            connector._connection.execute(
                "INSERT INTO articles VALUES (1, 'Test Title', 'Test Description')"
            )
            connector._connection.commit()

            documents = connector.load()

            assert len(documents) == 1
            content = documents[0][0]
            assert "title: Test Title" in content
            assert "description: Test Description" in content

            connector.disconnect()

    def test_load_with_metadata_columns(self):
        """Test metadata_columns adds to metadata."""
        from rag.loaders.database_connector import SQLiteConnector

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test.db")
            connector = SQLiteConnector(
                connection_string=db_path,
                query="SELECT id, name, category FROM items",
                content_columns=["name"],
                metadata_columns=["category"],
            )

            connector.connect()

            # Create test data
            connector._connection.execute(
                "CREATE TABLE items (id INTEGER, name TEXT, category TEXT)"
            )
            connector._connection.execute(
                "INSERT INTO items VALUES (1, 'Item1', 'electronics')"
            )
            connector._connection.commit()

            documents = connector.load()

            assert len(documents) == 1
            metadata = documents[0][1]
            assert metadata["category"] == "electronics"

            connector.disconnect()


class TestBaseDatabaseConnectorHelperMethods:
    """Tests for BaseDatabaseConnector helper methods."""

    def test_safe_connection_string_hides_password(self):
        """Test password=xxx is hidden."""
        from rag.loaders.database_connector import SQLiteConnector

        connector = SQLiteConnector(
            connection_string="sqlite:///db.db?password=secret123",
            query="SELECT 1",
        )

        safe = connector._safe_connection_string()

        assert "secret123" not in safe
        assert "***" in safe

    def test_safe_connection_string_hides_pwd(self):
        """Test pwd=xxx is hidden."""
        from rag.loaders.database_connector import SQLiteConnector

        connector = SQLiteConnector(
            connection_string="sqlite:///db.db?pwd=mysecret",
            query="SELECT 1",
        )

        safe = connector._safe_connection_string()

        assert "mysecret" not in safe
        assert "***" in safe

    def test_extract_table_name_from_query(self):
        """Test table name extraction from SQL."""
        from rag.loaders.database_connector import SQLiteConnector

        connector = SQLiteConnector(
            connection_string=":memory:",
            query="SELECT * FROM users WHERE id = 1",
        )

        table_name = connector._extract_table_name()

        assert table_name == "users"

    def test_extract_table_name_returns_none_for_invalid_query(self):
        """Test invalid query returns None."""
        from rag.loaders.database_connector import SQLiteConnector

        connector = SQLiteConnector(
            connection_string=":memory:",
            query="INVALID SQL",
        )

        table_name = connector._extract_table_name()

        assert table_name is None
