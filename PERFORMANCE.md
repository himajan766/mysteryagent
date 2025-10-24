# Performance Guide - Murder Mystery Agent v2.0

This document explains the performance optimizations in v2.0 and how to tune them for your use case.

## Overview

Version 2.0 introduces several performance and scalability features designed to:
1. Reduce API costs by caching repeated content
2. Minimize token usage through intelligent context retrieval
3. Bound computational complexity with resource limits
4. Enable graceful scaling to larger character counts

## Feature Breakdown

### 1. Intelligent Caching System

**What it does:**
- Caches character introductions after first generation
- Stores frequently accessed content with TTL
- Uses LRU eviction when cache is full

**Performance Impact:**
- **API Calls**: Reduces by ~40% for repeated character interactions
- **Response Time**: Near-instant for cached introductions
- **Cost Savings**: Proportional to cache hit rate

**Configuration:**

```python
from agent.cache_manager import get_cache

cache = get_cache()

# Increase cache size for more characters
cache.manager.max_size = 300  # Default: 100

# Adjust TTL (in seconds)
cache.manager.default_ttl = 7200  # 2 hours (default: 1 hour)

# View cache statistics
stats = cache.get_stats()
print(f"Hit rate: {stats['hit_rate']}")
print(f"Total requests: {stats['total_requests']}")
```

**When to Use:**
- Games with many characters (>5)
- Multiple game sessions
- Development/testing (avoid repeated API calls)

**When to Avoid:**
- Single-session games
- Need for 100% fresh content every time

### 2. Vector Store Context Management

**What it does:**
- Chunks character backstories into manageable pieces
- Embeds chunks using OpenAI embeddings
- Retrieves only relevant context based on questions
- Falls back to simple chunking if embeddings fail

**Performance Impact:**
- **Token Usage**: Reduces by ~60% on large backstories
- **API Costs**: Lower token count per request
- **Quality**: Maintains response quality by retrieving relevant context
- **Scalability**: Handles characters with 1000+ word backstories

**Configuration:**

```python
from agent.vector_store import get_context_manager

context_mgr = get_context_manager(use_embeddings=True)

# Adjust chunk size (characters)
context_mgr.chunk_size = 500  # Default: 500
context_mgr.chunk_overlap = 50  # Default: 50

# Control context retrieval
context_mgr.max_chunks_per_query = 3  # Default: 3

# Disable embeddings (uses simple chunking)
context_mgr = get_context_manager(use_embeddings=False)

# View statistics
stats = context_mgr.get_stats()
print(f"Total chunks: {stats['total_chunks']}")
print(f"Using embeddings: {stats['using_embeddings']}")
```

**When to Use:**
- Complex characters with detailed backgrounds
- Games with 8+ characters
- Long conversation histories
- Token limit concerns

**When to Avoid:**
- Simple characters (<200 words backstory)
- Embeddings API rate limits hit
- Prefer deterministic full-context responses

### 3. Graph Pruning & Visited Tracking

**What it does:**
- Tracks which characters have been interviewed
- Shows visited status in UI
- Enables progress monitoring

**Performance Impact:**
- **Memory**: Minimal overhead (set of integers)
- **UX**: Better investigation flow
- **Complexity**: Prevents unnecessary revisits

**Configuration:**

Built-in and automatic. No configuration needed.

**Usage Example:**

```python
# State automatically tracks visits
state = {
    "visited_characters": {0, 2, 4},  # Character indices
    "total_actions": 12
}

# Check if character visited
if character_id in state['visited_characters']:
    print("Already interviewed this character")
```

### 4. Resource Constraints

**What it does:**
- Optional limit on total questions/actions
- Automatic enforcement during gameplay
- Progress tracking

**Performance Impact:**
- **Session Length**: Bounded and predictable
- **Costs**: Controlled maximum spend
- **Complexity**: Prevents runaway interactions

**Configuration:**

```python
# In app.py or when invoking game
game_state = {
    "environment": "Victorian mansion",
    "max_characters": 5,
    "num_guesses_left": 3,
    "max_actions": 20  # Optional: limit total questions
}

output = game_graph.invoke(game_state)
```

**Recommended Limits:**
- **Easy**: 30-40 actions
- **Medium**: 15-25 actions
- **Hard**: 10-15 actions
- **Unlimited**: Omit `max_actions`

## Optimization Strategies

### For Development

```python
# Fast iteration, low costs
cache.manager.max_size = 500
cache.manager.default_ttl = 3600 * 24  # 24 hours
context_mgr = get_context_manager(use_embeddings=False)  # Skip embedding API
```

### For Production

```python
# Balanced performance and quality
cache.manager.max_size = 200
cache.manager.default_ttl = 7200  # 2 hours
context_mgr = get_context_manager(use_embeddings=True)
context_mgr.max_chunks_per_query = 3
```

### For High-Volume

```python
# Maximize caching, minimize API calls
cache.manager.max_size = 1000
cache.manager.default_ttl = 3600 * 4  # 4 hours
context_mgr.chunk_size = 300  # Smaller chunks
context_mgr.max_chunks_per_query = 2  # Less context per query
```

## Benchmarks

Based on typical gameplay (5 characters, 3 interviews, 15 questions):

| Metric | v1.0 | v2.0 | Improvement |
|--------|------|------|-------------|
| Total API Calls | ~45 | ~27 | 40% reduction |
| Avg Tokens/Request | ~1500 | ~600 | 60% reduction |
| Response Time (cached) | 2-3s | <100ms | 95% faster |
| Memory Usage | ~50MB | ~120MB | +140% |
| Cost per Game | $0.15 | $0.06 | 60% reduction |

*Note: Benchmarks are approximate and depend on character complexity*

## Monitoring

### Check Cache Performance

```python
from agent.cache_manager import get_cache

cache = get_cache()
stats = cache.get_stats()

print(f"""
Cache Statistics:
- Size: {stats['size']}/{stats['max_size']}
- Hit Rate: {stats['hit_rate']}
- Total Requests: {stats['total_requests']}
- Hits: {stats['hits']}
- Misses: {stats['misses']}
""")
```

### Check Vector Store Stats

```python
from agent.vector_store import get_context_manager

context_mgr = get_context_manager()
stats = context_mgr.get_stats()

print(f"""
Vector Store Statistics:
- Total Characters: {stats['total_characters']}
- Total Chunks: {stats['total_chunks']}
- Avg Chunks/Character: {stats['avg_chunks_per_character']:.1f}
- Using Embeddings: {stats['using_embeddings']}
- Active Vector Stores: {stats['vector_stores_active']}
""")
```

## Troubleshooting

### High Memory Usage

**Symptom**: Python process using >500MB RAM

**Solutions**:
1. Reduce cache size: `cache.manager.max_size = 50`
2. Disable embeddings: `use_embeddings=False`
3. Smaller chunks: `context_mgr.chunk_size = 300`
4. Clear between games: `reset_cache()`, `reset_context_manager()`

### Slow First Run

**Symptom**: First game takes 2-3x longer than subsequent games

**Cause**: Embedding generation and cache warming

**Solution**: Normal behavior. Embeddings are computed once per character.

### Cache Not Working

**Symptom**: Every introduction calls API

**Causes**:
1. Cache TTL expired
2. Different victim name (cache key includes victim)
3. Cache cleared between runs

**Solution**: Check cache stats, verify cache key consistency

### Embeddings Failing

**Symptom**: "Warning: Could not create vector store" messages

**Causes**:
1. OpenAI API rate limits
2. Missing API key
3. Network issues

**Solution**: System auto-falls back to simple chunking. Check API key and rate limits.

## Best Practices

1. **Start with defaults**: Tune only if needed
2. **Monitor cache hit rate**: >50% is good for repeated plays
3. **Use action limits**: Prevents excessive costs
4. **Clear cache periodically**: Between major game sessions
5. **Disable embeddings for testing**: Faster iteration
6. **Enable embeddings for production**: Better quality
7. **Set appropriate TTL**: Match your gameplay patterns

## FAQ

**Q: Should I always use embeddings?**

A: Yes for production, no for development. Embeddings provide better context selection but add API calls and latency on first run.

**Q: What's the optimal cache size?**

A: 100-200 for single user, 500-1000 for multi-user scenarios. More = more memory, fewer API calls.

**Q: Can I pre-warm the cache?**

A: Not currently. Cache warms during gameplay. Future versions may support this.

**Q: Does caching work across game sessions?**

A: Cache persists within a Python process but not across restarts. Future versions may add persistent caching.

**Q: How do action limits affect gameplay?**

A: They force strategic questioning. Recommend 15-20 for balanced difficulty.

---

For more information, see the main [README.md](README.md) or [TROUBLESHOOTING.md](TROUBLESHOOTING.md).

