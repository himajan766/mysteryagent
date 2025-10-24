"""
Data models and state classes for the Murder Mystery game.

This module defines:
- Character and NPC models for game characters
- StoryDetails for the murder mystery scenario
- ConversationState for managing character conversations
- GenerateGameState for overall game state management
"""

from typing import List, Optional, Annotated, Sequence
from typing_extensions import TypedDict
import operator

from pydantic import BaseModel, Field
from langchain_core.messages import BaseMessage


class Character(BaseModel):
    """
    Represents a character in the murder mystery game.
    
    Attributes:
        role: Primary role of the character in the story (e.g., Killer, Victim, Suspect)
        name: Name of the character
        backstory: Detailed backstory including concerns, motives, and background
    """
    role: str = Field(
        description="Primary role of the character in the story",
    )
    name: str = Field(
        description="Name of the character."
    )
    backstory: str = Field(
        description="Backstory of the character focus, concerns, and motives.",
    )
    
    @property
    def persona(self) -> str:
        """Returns a formatted string of the character's complete persona."""
        return f"Name: {self.name}\nRole: {self.role}\nBackstory: {self.backstory}\n"


class NPC(BaseModel):
    """
    Container for all non-player characters in the game.
    
    Attributes:
        characters: List of all Character objects in the game
    """
    characters: List[Character] = Field(
        description="Comprehensive list of characters with their roles and backstories.",
        default_factory=list
    )


class StoryDetails(BaseModel):
    """
    Contains all details about the murder mystery scenario.
    
    Attributes:
        victim_name: Name of the murder victim
        time_of_death: Approximate time when the murder occurred
        location_found: Where the body was discovered
        murder_weapon: The weapon or method used in the murder
        cause_of_death: Specific medical cause of death
        crime_scene_details: Description of the crime scene and any relevant evidence found
        witnesses: Information about potential witnesses or last known sightings
        initial_clues: Initial clues or evidence found at the scene
        npc_brief: Brief description of the characters and their relationships
    """
    victim_name: str = Field(
        description="Name of the murder victim"
    )
    time_of_death: str = Field(
        description="Approximate time when the murder occurred"
    )
    location_found: str = Field(
        description="Where the body was discovered"
    )
    murder_weapon: str = Field(
        description="The weapon or method used in the murder"
    )
    cause_of_death: str = Field(
        description="Specific medical cause of death"
    )
    crime_scene_details: str = Field(
        description="Description of the crime scene and any relevant evidence found"
    )
    witnesses: str = Field(
        description="Information about potential witnesses or last known sightings"
    )
    initial_clues: str = Field(
        description="Initial clues or evidence found at the scene"
    )
    npc_brief: str = Field(
        description="Brief description of the characters and their relationships"
    )


class ConversationState(TypedDict):
    """
    State management for character conversations.
    
    Attributes:
        messages: Sequence of conversation messages
        character: Character being interviewed
        story_details: Details about the murder mystery
        turn_count: Number of turns in this conversation
        cached_intro: Cached character introduction (if available)
    """
    messages: Annotated[Sequence[BaseMessage], operator.add]
    character: Character
    story_details: Optional[StoryDetails]
    turn_count: int
    cached_intro: Optional[str]


class GenerateGameState(TypedDict):
    """
    Overall game state management.
    
    Attributes:
        messages: Sequence of all game messages
        environment: Story environment/setting
        max_characters: Number of characters in the game
        characters: List of all Character objects
        story_details: Details about the murder mystery
        selected_character_id: Index of the currently selected character
        num_guesses_left: Number of guesses remaining for the player
        result: Store the guesser result and evaluate Correct/Incorrect
        visited_characters: Set of character IDs that have been interviewed
        total_actions: Total number of actions taken (questions asked, characters visited)
        max_actions: Maximum number of actions allowed (optional limit)
        conversation_cache: Dictionary storing cached content by character_id
    """
    messages: Annotated[Sequence[BaseMessage], operator.add]
    environment: str
    max_characters: int
    characters: List[Character]
    story_details: Optional[StoryDetails]
    selected_character_id: Optional[int]
    num_guesses_left: int
    result: str
    visited_characters: set
    total_actions: int
    max_actions: Optional[int]
    conversation_cache: dict

