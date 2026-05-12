"""RAG Retriever - end-to-end retrieval service.

Coordinates embedding generation and vector store queries.
"""

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .embeddings import DashScopeEmbedding
    from .vector_store import VectorStore

logger = logging.getLogger(__name__)


class RAGRetriever:
    """RAG retrieval service.

    Coordinates embedding generation and vector store queries
    for end-to-end retrieval.
    """

    def __init__(
        self,
        vector_store: "VectorStore",
        embedding_client: "DashScopeEmbedding",
        top_k: int = 3,
        timeout_ms: int = 300,
        min_similarity: float = 0.0,
    ) -> None:
        """Initialize RAG retriever.

        Args:
            vector_store: Vector store instance
            embedding_client: Embedding client instance
            top_k: Default number of results to retrieve
            timeout_ms: Timeout for retrieval in milliseconds
            min_similarity: Minimum similarity threshold (0.0 = disabled)
        """
        self._vector_store = vector_store
        self._embedding_client = embedding_client
        self._top_k = top_k
        self._timeout_ms = timeout_ms
        self._min_similarity = min_similarity

    def retrieve(
        self,
        query: str,
        top_k: int | None = None,
        filter_metadata: dict | None = None,
    ) -> list[dict] | None:
        """Retrieve relevant documents for a query.

        Args:
            query: Query text
            top_k: Number of results (uses default if None)
            filter_metadata: Metadata filter conditions

        Returns:
            List of retrieved documents, or None if error/timeout
        """
        if not query:
            return None

        try:
            # Generate query embedding
            query_embedding = self._embedding_client.embed_query(query)

            # Query vector store
            k = top_k or self._top_k
            results = self._vector_store.query(
                query_embedding=query_embedding,
                top_k=k,
                filter_metadata=filter_metadata,
            )

            # Filter by similarity if threshold set
            if self._min_similarity > 0:
                # Convert distance to similarity (cosine distance: 0 = same, 2 = opposite)
                # For cosine: similarity = 1 - distance
                results = [
                    r for r in results
                    if (1 - r.get("distance", 1)) >= self._min_similarity
                ]

            return results if results else None

        except Exception as e:
            logger.warning(f"Retrieval failed: {e}")
            return None

    def ingest(
        self,
        documents: list[dict],
        batch_size: int = 20,
    ) -> int:
        """Ingest documents into the knowledge base.

        Args:
            documents: List of documents, each with "text" and optional "metadata"
            batch_size: Batch size for embedding (max 20 for DashScope)

        Returns:
            Number of documents added
        """
        if not documents:
            return 0

        total_added = 0

        # Process in batches
        for i in range(0, len(documents), batch_size):
            batch = documents[i:i + batch_size]

            try:
                # Extract texts
                texts = [doc["text"] for doc in batch]

                # Generate embeddings
                embeddings = self._embedding_client.embed(texts)

                # Extract metadatas
                metadatas = [doc.get("metadata", {}) for doc in batch]

                # Add to vector store
                self._vector_store.add(
                    chunks=texts,
                    embeddings=embeddings,
                    metadatas=metadatas,
                )

                total_added += len(batch)

            except Exception as e:
                logger.error(f"Failed to ingest batch {i // batch_size}: {e}")
                continue

        return total_added

    def clear(self) -> None:
        """Clear all documents from the knowledge base."""
        self._vector_store.clear()

    def count(self) -> int:
        """Return total document count."""
        return self._vector_store.count()

    @property
    def top_k(self) -> int:
        """Return default top_k."""
        return self._top_k
