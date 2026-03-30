import chromadb
from chromadb.config import Settings
from langchain_openai import OpenAIEmbeddings
from app.utils.config import config
from app.utils.logger import get_logger

logger = get_logger(__name__)

class VectorStore:
    def __init__(self):
        self.client = chromadb.PersistentClient(
            path=config.CHROMA_PERSIST_DIR
        )
        self.embeddings = OpenAIEmbeddings(
            model=config.EMBEDDING_MODEL,
            api_key=config.OPENAI_API_KEY
        )
        self.policy_collection = self.client.get_or_create_collection(
            name=config.CHROMA_COLLECTION_POLICY,
            metadata={"hnsw:space": "cosine"}
        )
        self.clinical_collection = self.client.get_or_create_collection(
            name=config.CHROMA_COLLECTION_CLINICAL,
            metadata={"hnsw:space": "cosine"}
        )
        logger.info("VectorStore initialized")

    def add_policy_document(self, parsed_doc: dict) -> dict:
        """Store insurance policy chunks in ChromaDB."""
        return self._add_to_collection(
            collection=self.policy_collection,
            parsed_doc=parsed_doc,
            doc_type="policy"
        )

    def add_clinical_note(self, parsed_doc: dict) -> dict:
        """Store clinical note chunks in ChromaDB."""
        return self._add_to_collection(
            collection=self.clinical_collection,
            parsed_doc=parsed_doc,
            doc_type="clinical"
        )

    def _add_to_collection(
        self,
        collection,
        parsed_doc: dict,
        doc_type: str
    ) -> dict:
        """Generic method to add document chunks to a collection."""
        chunks = parsed_doc.get("chunks", [])
        if not chunks:
            logger.warning("No chunks to store")
            return {"stored": 0}

        texts = [c["text"] for c in chunks]
        ids = [
            f"{doc_type}_{parsed_doc['file_name']}_{c['chunk_index']}"
            for c in chunks
        ]
        metadatas = [
            {
                "file_name": parsed_doc["file_name"],
                "chunk_index": c["chunk_index"],
                "word_count": c["word_count"],
                "doc_type": doc_type
            }
            for c in chunks
        ]

        logger.info(f"Embedding {len(texts)} chunks...")

        # Generate embeddings
        embeddings = self.embeddings.embed_documents(texts)

        # Store in ChromaDB
        collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas
        )

        logger.info(
            f"Stored {len(texts)} chunks in {doc_type} collection"
        )
        return {"stored": len(texts)}

    def query_policies(self, query: str, n_results: int = None) -> list:
        """Query insurance policy collection."""
        return self._query_collection(
            collection=self.policy_collection,
            query=query,
            n_results=n_results or config.TOP_K_RESULTS
        )

    def query_clinical(self, query: str, n_results: int = None) -> list:
        """Query clinical notes collection."""
        return self._query_collection(
            collection=self.clinical_collection,
            query=query,
            n_results=n_results or config.TOP_K_RESULTS
        )

    def _query_collection(
        self,
        collection,
        query: str,
        n_results: int
    ) -> list:
        """Generic query method."""
        query_embedding = self.embeddings.embed_query(query)

        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=min(n_results, collection.count() or 1)
        )

        formatted = []
        for i, doc in enumerate(results["documents"][0]):
            formatted.append({
                "text": doc,
                "metadata": results["metadatas"][0][i],
                "distance": results["distances"][0][i]
            })

        return formatted

    def get_collection_stats(self) -> dict:
        """Get stats on what's stored."""
        return {
            "policy_chunks": self.policy_collection.count(),
            "clinical_chunks": self.clinical_collection.count()
        }