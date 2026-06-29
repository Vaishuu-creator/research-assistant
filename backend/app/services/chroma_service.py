import chromadb
from chromadb.config import Settings as ChromaSettings
from app.config import settings
import logging
import uuid

logger = logging.getLogger(__name__)


class ChromaService:
    """
    Manages the ChromaDB vector store.
    
    Phase 1: store + retrieve text chunks by metadata.
    Phase 2: we'll add embeddings for semantic search.
    """

    def __init__(self):
        # PersistentClient saves to disk — data survives restarts
        self.client = chromadb.PersistentClient(
            path=settings.chroma_persist_dir,
            settings=ChromaSettings(anonymized_telemetry=False),
        )
        # get_or_create is idempotent — safe to call on every startup
        self.collection = self.client.get_or_create_collection(
            name=settings.chroma_collection_name,
            metadata={"hnsw:space": "cosine"},  # cosine similarity for embeddings
        )
        logger.info(
            f"ChromaDB ready — collection '{settings.chroma_collection_name}' "
            f"has {self.collection.count()} documents"
        )

    def add_documents(self, documents: list[dict]) -> list[str]:
        """
        Store search result chunks.
        
        Each document must have: content (str), metadata (dict)
        Returns list of generated IDs.
        """
        if not documents:
            return []

        ids = [str(uuid.uuid4()) for _ in documents]
        texts = [doc["content"] for doc in documents]
        metadatas = [doc.get("metadata", {}) for doc in documents]

        self.collection.add(
            ids=ids,
            documents=texts,
            metadatas=metadatas,
        )
        logger.info(f"Stored {len(documents)} chunks in ChromaDB")
        return ids

    def query(self, query_text: str, n_results: int = 5) -> list[dict]:
        """
        Retrieve most relevant chunks for a query.
        Returns list of dicts with content + metadata.
        """
        results = self.collection.query(
            query_texts=[query_text],
            n_results=min(n_results, self.collection.count() or 1),
        )
        # Flatten the nested list structure ChromaDB returns
        chunks = []
        for i, doc in enumerate(results["documents"][0]):
            chunks.append({
                "content": doc,
                "metadata": results["metadatas"][0][i],
                "distance": results["distances"][0][i],
            })
        return chunks

    def get_count(self) -> int:
        return self.collection.count()

    def reset_collection(self) -> None:
        """Delete all documents. Useful for testing."""
        self.client.delete_collection(settings.chroma_collection_name)
        self.collection = self.client.get_or_create_collection(
            name=settings.chroma_collection_name,
            metadata={"hnsw:space": "cosine"},
        )
        logger.warning("ChromaDB collection reset")