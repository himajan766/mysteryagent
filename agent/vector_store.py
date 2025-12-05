"""
Vector store for scalable dialogue context management.

This module provides:
1. Character background chunking
2. Embedding-based retrieval of relevant context
3. Token limit management
4. Efficient memory usage for large character backgrounds
"""

from typing import List, Dict, Optional, Tuple
import hashlib
from dataclasses import dataclass

try:
    from langchain_openai import OpenAIEmbeddings
    from langchain_community.vectorstores import FAISS
    from langchain_core.documents import Document
    VECTOR_STORE_AVAILABLE = True
except ImportError:
    VECTOR_STORE_AVAILABLE = False


@dataclass
class TextChunk:
    """
    Represents a chunk of text with metadata.
    
    Attributes:
        content: The text content
        chunk_id: Unique identifier for this chunk
        source: Source identifier (e.g., character_id)
        metadata: Additional metadata
    """
    content: str
    chunk_id: str
    source: str
    metadata: Dict


class CharacterContextManager:
    """
    Manages character context using chunking and vector similarity search.
    
    This class helps manage large character backgrounds by:
    - Splitting them into manageable chunks
    - Storing chunks in a vector database
    - Retrieving only relevant chunks based on query
    - Staying within token limits
    """
    
    def __init__(self, 
                 chunk_size: int = 500,
                 chunk_overlap: int = 50,
                 max_chunks_per_query: int = 3,
                 use_embeddings: bool = True):
        """
        Initialize the context manager.
        
        Args:
            chunk_size: Maximum size of each text chunk in characters
            chunk_overlap: Overlap between chunks to maintain context
            max_chunks_per_query: Maximum chunks to retrieve per query
            use_embeddings: Whether to use embeddings (requires OpenAI API)
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.max_chunks_per_query = max_chunks_per_query
        self.use_embeddings = use_embeddings and VECTOR_STORE_AVAILABLE
        
        # Storage
        self.chunks: Dict[str, List[TextChunk]] = {}
        self.vector_stores: Dict[str, any] = {}
        
        # Initialize embeddings if available
        if self.use_embeddings:
            try:
                self.embeddings = OpenAIEmbeddings()
            except Exception as e:
                print(f"Warning: Could not initialize embeddings: {e}")
                self.use_embeddings = False
    
    def _chunk_text(self, text: str, source: str) -> List[TextChunk]:
        """
        Split text into overlapping chunks.
        
        Args:
            text: Text to chunk
            source: Source identifier
        
        Returns:
            List of TextChunk objects
        """
        chunks = []
        start = 0
        text_length = len(text)
        
        while start < text_length:
            end = start + self.chunk_size
            
            # If not at the end, try to break at a sentence or word boundary
            if end < text_length:
                # Look for sentence end
                sentence_end = text.rfind('. ', start, end)
                if sentence_end > start:
                    end = sentence_end + 1
                else:
                    # Look for word boundary
                    word_end = text.rfind(' ', start, end)
                    if word_end > start:
                        end = word_end
            
            chunk_content = text[start:end].strip()
            if chunk_content:
                chunk_id = hashlib.md5(
                    f"{source}_{start}_{chunk_content[:50]}".encode()
                ).hexdigest()
                
                chunks.append(TextChunk(
                    content=chunk_content,
                    chunk_id=chunk_id,
                    source=source,
                    metadata={
                        'start': start,
                        'end': end,
                        'chunk_index': len(chunks)
                    }
                ))
            
            # Move to next chunk with overlap
            start = end - self.chunk_overlap
            if start <= 0:
                start = end
        
        return chunks
    
    def add_character_context(self, character_id: str, 
                            backstory: str,
                            additional_context: Optional[Dict[str, str]] = None):
        """
        Add character context to the store.
        
        Args:
            character_id: Unique character identifier
            backstory: Character's backstory text
            additional_context: Optional additional context fields
        """
        # Combine all text
        full_text = backstory
        if additional_context:
            for key, value in additional_context.items():
                full_text += f"\n\n{key}: {value}"
        
        # Chunk the text
        chunks = self._chunk_text(full_text, character_id)
        self.chunks[character_id] = chunks
        
        # Create vector store if using embeddings
        if self.use_embeddings and chunks:
            try:
                documents = [
                    Document(
                        page_content=chunk.content,
                        metadata={
                            'character_id': character_id,
                            'chunk_id': chunk.chunk_id,
                            **chunk.metadata
                        }
                    )
                    for chunk in chunks
                ]
                
                self.vector_stores[character_id] = FAISS.from_documents(
                    documents,
                    self.embeddings
                )
            except Exception as e:
                print(f"Warning: Could not create vector store for {character_id}: {e}")
    
    def get_relevant_context(self, character_id: str, 
                           query: str,
                           max_tokens: int = 1000) -> str:
        """
        Retrieve relevant context for a character based on a query.
        
        Args:
            character_id: Character identifier
            query: Query string to find relevant context for
            max_tokens: Maximum tokens in returned context (approximate)
        
        Returns:
            Relevant context string
        """
        if character_id not in self.chunks:
            return ""
        
        # If using vector store, do similarity search
        if self.use_embeddings and character_id in self.vector_stores:
            try:
                docs = self.vector_stores[character_id].similarity_search(
                    query,
                    k=self.max_chunks_per_query
                )
                relevant_chunks = [doc.page_content for doc in docs]
            except Exception as e:
                print(f"Warning: Vector search failed, using fallback: {e}")
                relevant_chunks = [chunk.content for chunk in self.chunks[character_id][:self.max_chunks_per_query]]
        else:
            # Fallback: return first few chunks
            relevant_chunks = [
                chunk.content 
                for chunk in self.chunks[character_id][:self.max_chunks_per_query]
            ]
        
        # Combine chunks and truncate to max_tokens (rough estimate: 1 token ≈ 4 chars)
        max_chars = max_tokens * 4
        combined = "\n\n".join(relevant_chunks)
        
        if len(combined) > max_chars:
            combined = combined[:max_chars] + "..."
        
        return combined
    
    def get_full_context(self, character_id: str) -> str:
        """
        Get the full context for a character (all chunks combined).
        
        Args:
            character_id: Character identifier
        
        Returns:
            Full context string
        """
        if character_id not in self.chunks:
            return ""
        
        return "\n".join([chunk.content for chunk in self.chunks[character_id]])
    
    def remove_character(self, character_id: str):
        """
        Remove a character's context from storage.
        
        Args:
            character_id: Character identifier
        """
        if character_id in self.chunks:
            del self.chunks[character_id]
        if character_id in self.vector_stores:
            del self.vector_stores[character_id]
    
    def clear(self):
        """Clear all stored contexts."""
        self.chunks.clear()
        self.vector_stores.clear()
    
    def get_stats(self) -> Dict[str, any]:
        """
        Get statistics about stored contexts.
        
        Returns:
            Dictionary with statistics
        """
        total_chunks = sum(len(chunks) for chunks in self.chunks.values())
        
        return {
            'total_characters': len(self.chunks),
            'total_chunks': total_chunks,
            'avg_chunks_per_character': total_chunks / len(self.chunks) if self.chunks else 0,
            'using_embeddings': self.use_embeddings,
            'vector_stores_active': len(self.vector_stores)
        }


class SimpleContextManager:
    """
    Simplified context manager without embeddings.
    
    Falls back to basic text truncation and chunking.
    Useful when embeddings are not available or desired.
    """
    
    def __init__(self, max_context_length: int = 2000):
        """
        Initialize simple context manager.
        
        Args:
            max_context_length: Maximum characters to return for context
        """
        self.max_context_length = max_context_length
        self.contexts: Dict[str, str] = {}
    
    def add_character_context(self, character_id: str, context: str):
        """
        Add character context.
        
        Args:
            character_id: Character identifier
            context: Context text
        """
        self.contexts[character_id] = context
    
    def get_relevant_context(self, character_id: str, 
                           query: Optional[str] = None,
                           max_tokens: int = 1000) -> str:
        """
        Get context for a character, truncated if needed.
        
        Args:
            character_id: Character identifier
            query: Unused in simple manager
            max_tokens: Maximum tokens (approximate)
        
        Returns:
            Context string
        """
        if character_id not in self.contexts:
            return ""
        
        context = self.contexts[character_id]
        max_chars = min(max_tokens * 4, self.max_context_length)
        
        if len(context) > max_chars:
            return context[:max_chars] + "..."
        
        return context
    
    def clear(self):
        """Clear all contexts."""
        self.contexts.clear()


# Global context manager instance
_global_context_manager: Optional[CharacterContextManager] = None


def get_context_manager(use_embeddings: bool = True) -> CharacterContextManager:
    """
    Get or create the global context manager.
    
    Args:
        use_embeddings: Whether to use embeddings (requires OpenAI API)
    
    Returns:
        Global CharacterContextManager instance
    """
    global _global_context_manager
    if _global_context_manager is None:
        _global_context_manager = CharacterContextManager(
            chunk_size=500,
            chunk_overlap=50,
            max_chunks_per_query=3,
            use_embeddings=use_embeddings
        )
    return _global_context_manager


def reset_context_manager():
    """Reset the global context manager."""
    global _global_context_manager
    if _global_context_manager is not None:
        _global_context_manager.clear()
    _global_context_manager = None

