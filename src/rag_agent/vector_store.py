"""
Vector database integration for RAG Agent Platform.
"""

import os
from typing import List, Optional, Dict, Any
from llama_index import VectorStoreIndex, Document, StorageContext
from llama_index.vector_stores import VectorStore

# Try to import Chroma (lightweight local option)
try:
    import chromadb
    from chromadb.config import Settings
    from llama_index.vector_stores import ChromaVectorStore
    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False
    ChromaVectorStore = None

# Try to import Qdrant (production option)
try:
    from qdrant_client import QdrantClient
    from llama_index.vector_stores import QdrantVectorStore
    QDRANT_AVAILABLE = True
except ImportError:
    QDRANT_AVAILABLE = False
    QdrantClient = None
    QdrantVectorStore = None

# Try to import Pinecone (cloud option)
try:
    import pinecone
    from llama_index.vector_stores import PineconeVectorStore
    PINECONE_AVAILABLE = True
except ImportError:
    PINECONE_AVAILABLE = False
    pinecone = None
    PineconeVectorStore = None


class VectorStoreManager:
    """Manager for vector database operations."""
    
    def __init__(self, vector_store_type: str = "chroma", **kwargs):
        """Initialize vector store manager.
        
        Args:
            vector_store_type: Type of vector store ("chroma", "qdrant", "pinecone", or "in_memory")
            **kwargs: Additional configuration for vector store
        """
        self.vector_store_type = vector_store_type.lower()
        self.vector_store: Optional[VectorStore] = None
        self.storage_context: Optional[StorageContext] = None
        self.index: Optional[VectorStoreIndex] = None
        
        if self.vector_store_type == "chroma":
            self._init_chroma(**kwargs)
        elif self.vector_store_type == "qdrant":
            self._init_qdrant(**kwargs)
        elif self.vector_store_type == "pinecone":
            self._init_pinecone(**kwargs)
        else:
            # Default to in-memory
            self._init_in_memory(**kwargs)
    
    def _init_chroma(self, **kwargs):
        """Initialize Chroma vector store."""
        if not CHROMA_AVAILABLE:
            raise ImportError(
                "Chroma not available. Install with: pip install chromadb"
            )
        
        persist_dir = kwargs.get("persist_dir", os.getenv("CHROMA_PERSIST_DIR", "./data/chroma"))
        collection_name = kwargs.get("collection_name", os.getenv("CHROMA_COLLECTION", "rag_documents"))
        
        # Create directory if it doesn't exist
        os.makedirs(persist_dir, exist_ok=True)
        
        # Initialize Chroma client
        chroma_client = chromadb.PersistentClient(
            path=persist_dir,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Get or create collection
        chroma_collection = chroma_client.get_or_create_collection(
            name=collection_name
        )
        
        # Create vector store
        self.vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
        self.storage_context = StorageContext.from_defaults(
            vector_store=self.vector_store
        )
    
    def _init_qdrant(self, **kwargs):
        """Initialize Qdrant vector store."""
        if not QDRANT_AVAILABLE:
            raise ImportError(
                "Qdrant not available. Install with: pip install qdrant-client"
            )
        
        url = kwargs.get("url", os.getenv("QDRANT_URL", "http://localhost:6333"))
        collection_name = kwargs.get("collection_name", os.getenv("QDRANT_COLLECTION", "rag_documents"))
        api_key = kwargs.get("api_key", os.getenv("QDRANT_API_KEY"))
        
        # Create Qdrant client
        qdrant_client = QdrantClient(url=url, api_key=api_key)
        
        # Create vector store
        self.vector_store = QdrantVectorStore(
            client=qdrant_client,
            collection_name=collection_name
        )
        self.storage_context = StorageContext.from_defaults(
            vector_store=self.vector_store
        )
    
    def _init_pinecone(self, **kwargs):
        """Initialize Pinecone vector store."""
        if not PINECONE_AVAILABLE:
            raise ImportError(
                "Pinecone not available. Install with: pip install pinecone-client"
            )
        
        api_key = kwargs.get("api_key", os.getenv("PINECONE_API_KEY"))
        environment = kwargs.get("environment", os.getenv("PINECONE_ENVIRONMENT"))
        index_name = kwargs.get("index_name", os.getenv("PINECONE_INDEX_NAME", "rag-documents"))
        
        if not api_key:
            raise ValueError("Pinecone API key is required")
        
        # Initialize Pinecone
        pinecone.init(api_key=api_key, environment=environment)
        
        # Create vector store
        self.vector_store = PineconeVectorStore(
            index_name=index_name
        )
        self.storage_context = StorageContext.from_defaults(
            vector_store=self.vector_store
        )
    
    def _init_in_memory(self, **kwargs):
        """Initialize in-memory vector store (default)."""
        self.storage_context = None  # Will use default in-memory storage
        self.vector_store = None
    
    def create_index(self, documents: List[Document]) -> VectorStoreIndex:
        """Create vector index from documents."""
        if self.storage_context:
            self.index = VectorStoreIndex.from_documents(
                documents,
                storage_context=self.storage_context
            )
        else:
            # Fallback to in-memory
            self.index = VectorStoreIndex.from_documents(documents)
        
        return self.index
    
    def load_index(self) -> Optional[VectorStoreIndex]:
        """Load existing vector index."""
        if self.storage_context:
            try:
                self.index = VectorStoreIndex.from_vector_store(
                    vector_store=self.vector_store,
                    storage_context=self.storage_context
                )
            except Exception:
                # Index doesn't exist yet
                self.index = None
        else:
            self.index = None
        
        return self.index
    
    def get_index(self) -> Optional[VectorStoreIndex]:
        """Get current vector index."""
        return self.index
    
    def persist(self):
        """Persist vector store."""
        if self.vector_store_type == "chroma":
            # Chroma persists automatically
            pass
        elif self.vector_store_type in ["qdrant", "pinecone"]:
            # These persist automatically
            pass
        # In-memory doesn't persist


def get_vector_store_manager(**kwargs) -> VectorStoreManager:
    """Get vector store manager instance.
    
    Args:
        **kwargs: Configuration for vector store
        
    Returns:
        VectorStoreManager instance
    """
    vector_store_type = kwargs.get(
        "vector_store_type",
        os.getenv("VECTOR_STORE_TYPE", "chroma")
    )
    
    return VectorStoreManager(vector_store_type=vector_store_type, **kwargs)

