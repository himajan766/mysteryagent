"""
Cache manager for pre-generated content in the Murder Mystery game.

This module provides caching functionality to:
1. Pre-generate character introductions in batch
2. Cache narrative transitions
3. Reduce API calls and improve response time
4. Manage memory efficiently with TTL and size limits
"""

import hashlib
import json
from typing import Dict, Optional, List, Any
from datetime import datetime, timedelta
from collections import OrderedDict


class CacheEntry:
    """
    Represents a single cache entry with metadata.
    
    Attributes:
        content: The cached content
        timestamp: When the entry was created
        access_count: Number of times accessed
        ttl_seconds: Time to live in seconds
    """
    def __init__(self, content: Any, ttl_seconds: int = 3600):
        self.content = content
        self.timestamp = datetime.now()
        self.access_count = 0
        self.ttl_seconds = ttl_seconds
    
    def is_expired(self) -> bool:
        """Check if this cache entry has expired."""
        return datetime.now() > self.timestamp + timedelta(seconds=self.ttl_seconds)
    
    def access(self) -> Any:
        """Access the cached content and increment counter."""
        self.access_count += 1
        return self.content


class CacheManager:
    """
    Manages caching for game content with LRU eviction and TTL.
    
    Features:
    - LRU (Least Recently Used) eviction when size limit reached
    - TTL (Time To Live) for automatic expiration
    - Key-based storage for quick lookups
    - Statistics tracking
    """
    
    def __init__(self, max_size: int = 100, default_ttl: int = 3600):
        """
        Initialize the cache manager.
        
        Args:
            max_size: Maximum number of entries to cache
            default_ttl: Default time-to-live in seconds (default: 1 hour)
        """
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self.hits = 0
        self.misses = 0
    
    def _generate_key(self, *args, **kwargs) -> str:
        """
        Generate a unique cache key from arguments.
        
        Args:
            *args: Positional arguments to include in key
            **kwargs: Keyword arguments to include in key
        
        Returns:
            SHA256 hash of the serialized arguments
        """
        key_data = {
            'args': args,
            'kwargs': kwargs
        }
        key_string = json.dumps(key_data, sort_keys=True)
        return hashlib.sha256(key_string.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        """
        Retrieve an item from cache.
        
        Args:
            key: Cache key
        
        Returns:
            Cached content if found and not expired, None otherwise
        """
        if key in self.cache:
            entry = self.cache[key]
            
            # Check if expired
            if entry.is_expired():
                del self.cache[key]
                self.misses += 1
                return None
            
            # Move to end (most recently used)
            self.cache.move_to_end(key)
            self.hits += 1
            return entry.access()
        
        self.misses += 1
        return None
    
    def set(self, key: str, content: Any, ttl: Optional[int] = None):
        """
        Store an item in cache.
        
        Args:
            key: Cache key
            content: Content to cache
            ttl: Time-to-live in seconds (uses default if not specified)
        """
        # Remove if already exists
        if key in self.cache:
            del self.cache[key]
        
        # Evict oldest if at capacity
        elif len(self.cache) >= self.max_size:
            self.cache.popitem(last=False)  # Remove oldest (FIFO)
        
        # Add new entry
        ttl = ttl if ttl is not None else self.default_ttl
        self.cache[key] = CacheEntry(content, ttl)
    
    def get_or_compute(self, key: str, compute_fn, ttl: Optional[int] = None) -> Any:
        """
        Get from cache or compute and cache if not found.
        
        Args:
            key: Cache key
            compute_fn: Function to call if cache miss
            ttl: Time-to-live in seconds
        
        Returns:
            Cached or newly computed content
        """
        cached = self.get(key)
        if cached is not None:
            return cached
        
        # Compute and cache
        result = compute_fn()
        self.set(key, result, ttl)
        return result
    
    def invalidate(self, key: str):
        """Remove a specific key from cache."""
        if key in self.cache:
            del self.cache[key]
    
    def clear(self):
        """Clear all cache entries."""
        self.cache.clear()
        self.hits = 0
        self.misses = 0
    
    def cleanup_expired(self):
        """Remove all expired entries from cache."""
        expired_keys = [
            key for key, entry in self.cache.items()
            if entry.is_expired()
        ]
        for key in expired_keys:
            del self.cache[key]
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        total_requests = self.hits + self.misses
        hit_rate = (self.hits / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'size': len(self.cache),
            'max_size': self.max_size,
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': f"{hit_rate:.2f}%",
            'total_requests': total_requests
        }


class GameContentCache:
    """
    Specialized cache for Murder Mystery game content.
    
    Provides convenient methods for caching specific game elements:
    - Character introductions
    - Story narrations
    - Character responses
    """
    
    def __init__(self, max_size: int = 100):
        self.manager = CacheManager(max_size=max_size, default_ttl=7200)  # 2 hours
    
    def cache_character_intro(self, character_id: str, character_name: str, 
                             intro_text: str):
        """
        Cache a character introduction.
        
        Args:
            character_id: Unique character identifier
            character_name: Character name
            intro_text: Introduction text to cache
        """
        key = f"intro_{character_id}_{character_name}"
        self.manager.set(key, intro_text)
    
    def get_character_intro(self, character_id: str, character_name: str) -> Optional[str]:
        """
        Retrieve cached character introduction.
        
        Args:
            character_id: Unique character identifier
            character_name: Character name
        
        Returns:
            Cached introduction text or None
        """
        key = f"intro_{character_id}_{character_name}"
        return self.manager.get(key)
    
    def batch_cache_intros(self, intros: Dict[str, str]):
        """
        Cache multiple character introductions at once.
        
        Args:
            intros: Dictionary mapping character_id to intro text
        """
        for char_id, intro_text in intros.items():
            self.manager.set(f"intro_{char_id}", intro_text)
    
    def cache_narration(self, narration_key: str, narration_text: str):
        """
        Cache a story narration.
        
        Args:
            narration_key: Unique key for this narration
            narration_text: Narration text to cache
        """
        key = f"narration_{narration_key}"
        self.manager.set(key, narration_text)
    
    def get_narration(self, narration_key: str) -> Optional[str]:
        """
        Retrieve cached narration.
        
        Args:
            narration_key: Unique key for the narration
        
        Returns:
            Cached narration text or None
        """
        key = f"narration_{narration_key}"
        return self.manager.get(key)
    
    def cache_response(self, character_id: str, question_hash: str, 
                      response_text: str, ttl: int = 1800):
        """
        Cache a character's response to a question.
        
        Args:
            character_id: Character identifier
            question_hash: Hash of the question
            response_text: Response to cache
            ttl: Time-to-live (default: 30 minutes)
        """
        key = f"response_{character_id}_{question_hash}"
        self.manager.set(key, response_text, ttl)
    
    def get_response(self, character_id: str, question_hash: str) -> Optional[str]:
        """
        Retrieve cached response.
        
        Args:
            character_id: Character identifier
            question_hash: Hash of the question
        
        Returns:
            Cached response or None
        """
        key = f"response_{character_id}_{question_hash}"
        return self.manager.get(key)
    
    def clear_character_cache(self, character_id: str):
        """
        Clear all cached content for a specific character.
        
        Args:
            character_id: Character identifier
        """
        keys_to_remove = [
            key for key in self.manager.cache.keys()
            if character_id in key
        ]
        for key in keys_to_remove:
            self.manager.invalidate(key)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return self.manager.get_stats()


# Global cache instance
_global_cache: Optional[GameContentCache] = None


def get_cache() -> GameContentCache:
    """
    Get or create the global game content cache.
    
    Returns:
        Global GameContentCache instance
    """
    global _global_cache
    if _global_cache is None:
        _global_cache = GameContentCache(max_size=200)
    return _global_cache


def reset_cache():
    """Reset the global cache (useful for testing or new game sessions)."""
    global _global_cache
    if _global_cache is not None:
        _global_cache.manager.clear()

