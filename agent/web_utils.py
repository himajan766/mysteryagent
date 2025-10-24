"""
Web utility functions for integrating the game logic with Streamlit UI.

This module provides helper functions to bridge the gap between
the LangGraph-based game logic and the Streamlit web interface.
"""

from typing import Dict, Any, List, Optional, Tuple
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from .schemas import Character, ConversationState, GenerateGameState
from .game_logic import (
    create_characters,
    create_story,
    narrator,
    character_introduction,
    ask_question,
    answer_question,
    where_to_go
)


def initialize_game(game_graph, game_state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Initialize a new game by creating characters and story.
    
    Args:
        game_graph: The compiled game loop graph
        game_state: Initial game configuration
    
    Returns:
        Updated game state with characters, story, and narration
    """
    # Create characters
    char_result = create_characters(game_state)
    game_state.update(char_result)
    
    # Create story
    story_result = create_story(game_state)
    game_state.update(story_result)
    
    # Generate narration
    narr_result = narrator(game_state)
    game_state.update(narr_result)
    
    return game_state


def start_conversation_with_character(
    conversation_graph,
    character: Character,
    story_details,
) -> Tuple[str, List]:
    """
    Start a conversation with a character and get their introduction.
    
    Args:
        conversation_graph: The compiled conversation graph
        character: Character to interview
        story_details: Story details for context
    
    Returns:
        Tuple of (introduction_text, messages_list)
    """
    # Create conversation state
    conv_state = {
        "character": character,
        "story_details": story_details,
        "messages": [],
        "turn_count": 0,
        "cached_intro": None
    }
    
    # Get character introduction
    intro_result = character_introduction(conv_state)
    messages = intro_result['messages']
    
    intro_text = messages[0].content if messages else ""
    
    return intro_text, messages


def ask_character_question(
    character: Character,
    story_details,
    messages: List,
    question_text: str,
    use_sherlock_ai: bool = False
) -> Tuple[str, List]:
    """
    Ask a character a question and get their response.
    
    Args:
        character: Character being interviewed
        story_details: Story context
        messages: Previous conversation messages
        question_text: Question to ask (ignored if use_sherlock_ai=True)
        use_sherlock_ai: Whether to use AI-generated question
    
    Returns:
        Tuple of (response_text, updated_messages)
    """
    from .game_logic import get_question
    
    # Create conversation state
    conv_state = {
        "character": character,
        "story_details": story_details,
        "messages": messages,
        "turn_count": len([m for m in messages if isinstance(m, HumanMessage)])
    }
    
    # Generate or use provided question
    if use_sherlock_ai:
        question = get_question(conv_state)
    else:
        question = question_text
    
    # Add question to messages
    conv_state['messages'].append(HumanMessage(content=question))
    
    # Get answer
    answer_result = answer_question(conv_state)
    updated_messages = conv_state['messages'] + answer_result['messages']
    
    response_text = answer_result['messages'][0].content if answer_result['messages'] else ""
    
    return response_text, updated_messages


def get_killer_character(characters: List[Character]) -> Optional[Character]:
    """
    Find and return the killer character.
    
    Args:
        characters: List of all characters
    
    Returns:
        The killer character or None
    """
    for char in characters:
        if char.role == 'Killer':
            return char
    return None


def check_guess(characters: List[Character], guessed_name: str) -> Tuple[bool, str]:
    """
    Check if the guessed character is the killer.
    
    Args:
        characters: List of all characters
        guessed_name: Name of the accused character
    
    Returns:
        Tuple of (is_correct, killer_name)
    """
    killer = get_killer_character(characters)
    killer_name = killer.name if killer else "Unknown"
    is_correct = killer_name == guessed_name
    
    return is_correct, killer_name


def format_character_for_display(character: Character, is_visited: bool = False) -> Dict[str, Any]:
    """
    Format character data for display in the UI.
    
    Args:
        character: Character to format
        is_visited: Whether this character has been interviewed
    
    Returns:
        Dictionary with formatted character data
    """
    return {
        'name': character.name,
        'role': character.role,
        'backstory': character.backstory,
        'is_victim': character.role == 'Victim',
        'is_visited': is_visited,
        'can_interview': character.role != 'Victim' and not is_visited
    }


def get_investigation_progress(game_state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculate and return investigation progress metrics.
    
    Args:
        game_state: Current game state
    
    Returns:
        Dictionary with progress metrics
    """
    characters = game_state.get('characters', [])
    visited = game_state.get('visited_characters', set())
    total_actions = game_state.get('total_actions', 0)
    max_actions = game_state.get('max_actions')
    num_guesses = game_state.get('num_guesses_left', 0)
    
    interviewable = [c for c in characters if c.role != 'Victim']
    interviewed_count = len(visited)
    total_interviewable = len(interviewable)
    
    progress = {
        'guesses_left': num_guesses,
        'interviewed': interviewed_count,
        'total_characters': total_interviewable,
        'actions_taken': total_actions,
        'max_actions': max_actions,
        'actions_remaining': (max_actions - total_actions) if max_actions else None,
        'progress_percentage': (interviewed_count / total_interviewable * 100) if total_interviewable > 0 else 0
    }
    
    return progress


def mark_character_visited(game_state: Dict[str, Any], character_index: int, turns_taken: int = 1) -> Dict[str, Any]:
    """
    Mark a character as visited and update action count.
    
    Args:
        game_state: Current game state
        character_index: Index of the character visited
        turns_taken: Number of turns/questions in the conversation
    
    Returns:
        Updated game state
    """
    visited = game_state.get('visited_characters', set()).copy()
    visited.add(character_index)
    
    total_actions = game_state.get('total_actions', 0)
    total_actions += turns_taken
    
    game_state['visited_characters'] = visited
    game_state['total_actions'] = total_actions
    
    return game_state


def is_action_limit_reached(game_state: Dict[str, Any]) -> bool:
    """
    Check if the action limit has been reached.
    
    Args:
        game_state: Current game state
    
    Returns:
        True if limit reached, False otherwise
    """
    max_actions = game_state.get('max_actions')
    if not max_actions:
        return False
    
    total_actions = game_state.get('total_actions', 0)
    return total_actions >= max_actions


def decrement_guesses(game_state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Decrement the number of guesses remaining.
    
    Args:
        game_state: Current game state
    
    Returns:
        Updated game state
    """
    game_state['num_guesses_left'] = max(0, game_state.get('num_guesses_left', 0) - 1)
    return game_state


def get_suspects_list(characters: List[Character]) -> List[Character]:
    """
    Get list of characters that can be accused (non-victims).
    
    Args:
        characters: List of all characters
    
    Returns:
        List of suspect characters
    """
    return [c for c in characters if c.role != 'Victim']


def get_unvisited_characters(game_state: Dict[str, Any]) -> List[Tuple[int, Character]]:
    """
    Get list of characters that haven't been interviewed yet.
    
    Args:
        game_state: Current game state
    
    Returns:
        List of tuples (index, character) for unvisited characters
    """
    characters = game_state.get('characters', [])
    visited = game_state.get('visited_characters', set())
    
    unvisited = []
    for idx, char in enumerate(characters):
        if char.role != 'Victim' and idx not in visited:
            unvisited.append((idx, char))
    
    return unvisited


def export_investigation_log(game_state: Dict[str, Any], investigation_log: List[Dict]) -> str:
    """
    Export investigation log as formatted text.
    
    Args:
        game_state: Current game state
        investigation_log: List of investigation events
    
    Returns:
        Formatted investigation log
    """
    lines = ["=== INVESTIGATION LOG ===\n"]
    
    # Game info
    lines.append(f"Environment: {game_state.get('environment', 'Unknown')}")
    lines.append(f"Total Characters: {len(game_state.get('characters', []))}")
    lines.append(f"Total Actions: {game_state.get('total_actions', 0)}\n")
    
    # Interview log
    lines.append("=== INTERVIEWS ===")
    for idx, event in enumerate(investigation_log, 1):
        lines.append(f"\n{idx}. Interview with {event.get('character', 'Unknown')}")
        lines.append(f"   Q: {event.get('question', 'N/A')}")
        if 'response' in event:
            lines.append(f"   A: {event.get('response', 'N/A')}")
    
    return "\n".join(lines)

