"""
Murder Mystery Agent - A LangGraph-powered detective game

This package contains the core components for the Murder Mystery investigation game
where players act as Sherlock Holmes to solve procedurally generated murder cases.

Features:
- Procedural story generation with unique mysteries each session
- Intelligent caching for faster response times
- Vector store-based context management for token efficiency
- Graph pruning with visited character tracking
- Configurable action and guess limits
"""

from .schemas import Character, NPC, StoryDetails, ConversationState, GenerateGameState
from .graph_builder import build_murder_mystery_game, visualize_graphs
from .cache_manager import get_cache, reset_cache
from .vector_store import get_context_manager, reset_context_manager

__all__ = [
    'Character',
    'NPC',
    'StoryDetails',
    'ConversationState',
    'GenerateGameState',
    'build_murder_mystery_game',
    'visualize_graphs',
    'get_cache',
    'reset_cache',
    'get_context_manager',
    'reset_context_manager',
]

__version__ = '2.0.0'

