"""
Core game logic and node functions for the Murder Mystery game.

This module contains all the LangGraph node functions that implement
the game mechanics, including character creation, story generation,
conversations, and killer guessing.
"""

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.graph import END

from .schemas import (
    Character, 
    NPC, 
    StoryDetails, 
    ConversationState, 
    GenerateGameState
)
from .prompts import (
    CHARACTER_INSTRUCTIONS,
    STORY_INSTRUCTIONS,
    NARRATOR_INSTRUCTIONS,
    CHARACTER_INTRODUCTION_INSTRUCTIONS,
    SHERLOCK_ASK_PROMPT,
    ANSWER_INSTRUCTIONS
)
from .display import (
    print_game_header,
    print_narration,
    print_introduction,
    get_player_input,
    print_character_answer,
    print_characters_list,
    get_character_selection,
    get_player_yesno_answer,
    print_suspect_list,
    print_guesses_remaining,
    print_result,
    print_incorrect_guess,
    print_sherlock_question
)
from .cache_manager import get_cache
from .vector_store import get_context_manager

from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel


# Constants
KILLER_ROLE = "Killer"
VICTIM_ROLE = "Victim"

# Global LLM instance - will be initialized by the graph builder
llm = None

# Global conversation graph - will be set by the graph builder
conversation_graph = None

# Global cache and context manager instances
cache = None
context_manager = None


def initialize_llm(language_model):
    """
    Initialize the global LLM instance.
    
    Args:
        language_model: The ChatOpenAI instance to use for all LLM operations
    """
    global llm, cache, context_manager
    llm = language_model
    cache = get_cache()
    context_manager = get_context_manager(use_embeddings=True)


def set_conversation_graph(graph):
    """
    Set the global conversation graph instance.
    
    Args:
        graph: The compiled conversation graph
    """
    global conversation_graph
    conversation_graph = graph


# ==================== CHARACTER & STORY CREATION NODES ====================

def create_characters(state: GenerateGameState):
    """
    Part of the Game Loop Graph.

    Creates a cast of characters for the murder mystery game based on the environment and max_characters.
    Uses procedural generation to ensure each game is unique.

    Args:
        state (GenerateGameState): The LangGraph State object containing:
            - environment: Description of the game's setting
            - max_characters: Maximum number of characters to create

    Returns:
        dict: Contains the generated character list. Adds to the State object.
            - characters: List of NPC objects with defined roles, including:
                - One killer
                - One victim
                - Supporting characters
    """
    import random
    
    environment = state['environment']
    max_characters = state['max_characters']

    # Add randomness seed to environment to ensure unique generation
    random_seed = random.randint(1000, 9999)
    environment_with_seed = f"{environment} (Mystery #{random_seed})"

    # Enforce structured output
    structured_llm = llm.with_structured_output(NPC)

    # System message
    system_message = CHARACTER_INSTRUCTIONS.replace("{{environment}}", environment_with_seed)
    system_message = system_message.replace("{{max_characters}}", str(max_characters))

    # Generate characters
    result = structured_llm.invoke([
        SystemMessage(content=system_message),
        HumanMessage(content="Generate the set of characters")
    ])

    # Add character contexts to vector store for efficient retrieval
    for idx, character in enumerate(result.characters):
        context_manager.add_character_context(
            character_id=str(idx),
            backstory=character.backstory,
            additional_context={
                'name': character.name,
                'role': character.role
            }
        )

    # Initialize visited tracking
    return {
        "characters": result.characters,
        "visited_characters": set(),
        "total_actions": 0,
        "conversation_cache": {}
    }


def create_story(state: GenerateGameState):
    """
    Part of the Game Loop Graph.

    Generates the complete murder mystery scenario and storyline based on the provided environment and characters.

    Args:
        state (GenerateGameState): The LangGraph State object containing:
            - environment: Description of the game's setting
            - characters: List of character objects generated in create_character step

    Returns:
        dict: Contains the complete story details. Adds to the State Object.
            - story_details: StoryDetails object including:
                - Crime scene information
                - Evidence and clues
                - Character relationships
                - Environmental factors
    """
    environment = state['environment']
    characters = state['characters']

    # Format character list for the prompt
    character_list = "\n".join([char.persona for char in characters])

    # Enforce structured output
    structured_llm = llm.with_structured_output(StoryDetails)

    # System message
    system_message = STORY_INSTRUCTIONS.replace("{{environment}}", environment)
    system_message = system_message.replace("{{characters}}", character_list)

    # Generate story details
    result = structured_llm.invoke([
        SystemMessage(content=system_message),
        HumanMessage(content="Generate the murder mystery scenario")
    ])

    # Return the story details
    return {"story_details": result}


def narrator(state: GenerateGameState):
    """
    Part of the Game Loop Graph.

    Generates Dr. Watson's narration of the crime scene for Sherlock Holmes.

    Args:
        state (GenerateGameState): The LangGraph State object containing:
            - story_details: Complete information about the crime

    Returns:
        dict: Contains the narration message. Adds to the State Object.
            - messages: Dr. Watson's narrative description
    """
    story = state['story_details']

    # Format the message with the story details
    system_message = NARRATOR_INSTRUCTIONS.format(
        victim=story.victim_name,
        time=story.time_of_death,
        location=story.location_found,
        weapon=story.murder_weapon,
        cause=story.cause_of_death,
        scene=story.crime_scene_details
    )
    
    # Generate narration
    narration = llm.invoke([
        SystemMessage(content=system_message),
        HumanMessage(content="Create an atmospheric narration of the crime scene")
    ])

    print_game_header()
    print_narration(narration)

    return {"messages": [narration]}


# ==================== CHARACTER SELECTION NODE ====================

def sherlock(state: GenerateGameState):
    """
    Part of the Game Loop Graph.

    Handles the character selection phase of the investigation.
    Shows visited status and enforces action limits if configured.

    Args:
        state (GenerateGameState): The LangGraph State object containing:
            - characters: List of all character objects
            - visited_characters: Set of visited character IDs
            - total_actions: Total actions taken so far
            - max_actions: Maximum allowed actions (optional)

    Returns:
        dict: Result of get_character_selection containing. Adds to the State Object.
            - selected_character_id: Index of selected character or None for guessing phase
    """
    console = Console()
    characters = state['characters']
    visited_characters = state.get('visited_characters', set())
    total_actions = state.get('total_actions', 0)
    max_actions = state.get('max_actions')
    
    # Check if action limit reached
    if max_actions and total_actions >= max_actions:
        console.print(Panel(
            f"[bold red]Maximum action limit reached ({max_actions} actions)[/bold red]\n"
            f"You must now make your final guess!",
            border_style="red",
            title="⚠️ Action Limit",
            title_align="left"
        ))
        return {"selected_character_id": None}
    
    # Display action stats
    if max_actions:
        console.print(Panel(
            f"[bold]Actions taken: {total_actions}/{max_actions}[/bold]\n"
            f"[dim]Characters visited: {len(visited_characters)}/{len([c for c in characters if c.role != VICTIM_ROLE])}[/dim]",
            border_style="cyan",
            title="📊 Investigation Progress",
            title_align="left"
        ))
    
    # Display characters with visited indicators
    display_to_original = print_characters_list(characters)
    
    # Show which characters have been visited
    if visited_characters:
        visited_names = [characters[i].name for i in visited_characters if i < len(characters)]
        console.print(f"\n[dim]Already interviewed: {', '.join(visited_names)}[/dim]\n")

    # Get user selection
    return get_character_selection(characters, display_to_original)


# ==================== CONVERSATION NODES ====================

def character_introduction(state: ConversationState):
    """
    Part of the Conversation Sub-Graph.

    Generates and displays a character's introduction to Sherlock Holmes.
    Uses caching to speed up repeated introductions.

    Args:
        state (ConversationState): The LangGraph State object containing:
            - messages: List of previous conversation messages
            - character: Character object with persona and character details
            - story_details: Object containing crime details
            - cached_intro: Pre-cached introduction if available

    Returns:
        dict: Adds the introduction messages to the conversation history
            - messages: Introduction messages to be added
            - turn_count: Initialized to 0
    """
    character = state['character']
    story = state['story_details']
    
    # Check cache first
    cache_key = f"{character.name}_{story.victim_name}"
    cached_intro = cache.get_character_intro(cache_key, character.name)
    
    if cached_intro:
        # Use cached introduction
        narration = AIMessage(content=cached_intro)
        console = Console()
        console.print(Panel(
            "[dim italic]Using cached introduction for faster response[/dim italic]",
            border_style="dim"
        ))
    else:
        # Generate new introduction
        system_message = CHARACTER_INTRODUCTION_INSTRUCTIONS.format(
            subject_persona=character.persona,
            victim=story.victim_name,
            time=story.time_of_death,
            location=story.location_found,
        )
        
        narration = llm.invoke([
            SystemMessage(content=system_message),
            HumanMessage(content="Introduce yourself to Sherlock Holmes")
        ])
        
        # Cache for future use
        cache.cache_character_intro(cache_key, character.name, narration.content)
    
    print_introduction(character, narration)

    return {"messages": [narration], "turn_count": 0}


def get_question(state: ConversationState):
    """
    Part of the Conversation Sub-Graph.

    Generates an investigative question from Sherlock Holmes to ask a character.

    Args:
        state (ConversationState): The LangGraph State object containing:
            - messages: List of previous conversation messages
            - character: Character object with persona and character details
            - story_details: Object containing crime details

    Returns:
        str: Generated question content from Sherlock AI assistance.
    """
    messages = state["messages"]
    character = state["character"]
    story = state["story_details"]
    
    system_message = SHERLOCK_ASK_PROMPT.format(
        character_name=character.name,
        victim_name=story.victim_name,
        time_of_death=story.time_of_death,
        location_found=story.location_found,
        murder_weapon=story.murder_weapon,
        cause_of_death=story.cause_of_death,
        crime_scene_details=story.crime_scene_details,
        initial_clues=story.initial_clues,
        conversation_history="\n".join([f"{msg.type}: {msg.content}" for msg in messages])
    )

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_message),
            MessagesPlaceholder(variable_name="messages"),
        ]
    )
    chain = prompt | llm
    question = chain.invoke(messages)

    print_sherlock_question(question.content)

    return question.content


def ask_question(state: ConversationState):
    """
    Part of the Conversation Sub-Graph.

    Handles the question-asking process, allowing either AI-generated Sherlock questions
    or direct player input. Tracks turn count.

    Args:
        state (ConversationState): The LangGraph State object containing:
            - messages: List of previous conversation messages
            - character: Character object with persona and character details
            - story_details: Object containing crime details
            - turn_count: Current turn count in this conversation

    Returns:
        dict: Adds question asked to the conversation history
            - messages: Question to be added
            - turn_count: Incremented turn count
    """
    character = state['character']
    turn_count = state.get('turn_count', 0)
    
    # Get user input
    while True:
        try:
            use_ai_sherlock = get_player_yesno_answer("Do you want SherlockAI to ask a question?")
            if use_ai_sherlock.lower()[0] == 'y':
                question = get_question(state)
            else:
                question = get_player_input(character.name)
            return {"messages": [HumanMessage(content=question)], "turn_count": turn_count + 1}
        except ValueError:
            print("Invalid input. Please enter a valid question")


def answer_question(state: ConversationState):
    """
    Part of the Conversation Sub-Graph.

    Generates a character's response to a question during the investigation.
    Uses vector store to retrieve only relevant context, reducing token usage.

    Args:
        state (ConversationState): The LangGraph State object containing:
            - messages: List of previous conversation messages
            - character: Character object with persona and character details
            - story_details: Object containing crime details

    Returns:
        dict: Adds response from the character to the conversation history
            - messages: Response to be added
    """
    messages = state['messages']
    character = state['character']
    last_message = messages[-1]
    story = state['story_details']
    
    # Get character ID (we'll use the character name as a simple identifier)
    character_id = character.name
    
    # Use vector store to get relevant context based on the question
    # This reduces token usage by only including relevant parts of the backstory
    relevant_backstory = context_manager.get_relevant_context(
        character_id=character_id,
        query=last_message.content,
        max_tokens=300  # Limit context to avoid token overflow
    )
    
    # If we couldn't get relevant context, fall back to full backstory
    if not relevant_backstory:
        relevant_backstory = character.backstory
    
    # Use the relevant context instead of full persona
    focused_persona = f"Name: {character.name}\nRole: {character.role}\nRelevant Background: {relevant_backstory}\n"
    
    system_message = ANSWER_INSTRUCTIONS.format(
        subject_persona=focused_persona,
        victim=story.victim_name,
        time=story.time_of_death,
        location=story.location_found,
        weapon=story.murder_weapon,
        cause=story.cause_of_death,
        scene=story.crime_scene_details,
        npc_brief=story.npc_brief,
        question=last_message.content
    )

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_message),
            MessagesPlaceholder(variable_name="messages"),
        ]
    )
    chain = prompt | llm
    answer = chain.invoke(messages)

    print_character_answer(character, answer.content)

    return {"messages": [answer]}


def where_to_go(state: ConversationState):
    """
    Part of the Conversation Sub-Graph.

    Determines the next conversation state based on the last message.

    Args:
        state (ConversationState): The LangGraph State object containing:
            - messages: List of previous conversation messages

    Returns:
        str: Either "end" to terminate conversation or "continue" to proceed
    """
    messages = state['messages']
    last_message = messages[-1]
    if "EXIT" in last_message.content:
        return "end"
    else:
        return "continue"


# ==================== CONVERSATION WRAPPER NODE ====================

def conversation(state: GenerateGameState):
    """
    Part of the Game Loop Graph.

    Manages the main conversation loop between Sherlock/player and characters.
    Tracks visited characters and increments action count.

    Args:
        state (GenerateGameState): The LangGraph State object containing:
            - selected_character_id: ID of the character to converse with
            - characters: List of all character objects
            - story_details: Complete story information
            - visited_characters: Set of visited character IDs
            - total_actions: Current action count

    Returns:
        dict: Contains either:
            - messages: List of conversation messages if character selected
            - visited_characters: Updated set with this character marked as visited
            - total_actions: Incremented action count
            - END constant if no character selected (moving to guessing phase)
    """
    selected_character_id = state['selected_character_id']
    if selected_character_id is not None:
        characters = state['characters']
        character = characters[selected_character_id]
        visited_characters = state.get('visited_characters', set()).copy()
        total_actions = state.get('total_actions', 0)
        
        # Mark character as visited
        visited_characters.add(selected_character_id)
        
        inputs = {
            "character": character,
            "story_details": state['story_details'],
            "turn_count": 0,
            "cached_intro": None
        }
        response = conversation_graph.invoke(inputs, {"recursion_limit": 50})
        
        # Count the number of turns (questions asked) in this conversation
        turn_count = response.get('turn_count', 1)
        total_actions += turn_count

        # Return the response as a message with updated tracking
        return {
            "messages": [response['messages']],
            "visited_characters": visited_characters,
            "total_actions": total_actions
        }
    else:
        return END


# ==================== KILLER GUESSING NODE ====================

def guesser(state: GenerateGameState):
    """
    Part of the Game Loop Graph.

    Manages the final phase where the player attempts to identify the killer.

    Args:
        state (GenerateGameState): The LangGraph State object containing:
            - num_guesses_left: Number of remaining guess attempts
            - characters: List of all character objects

    Returns:
        dict: Contains:
            - result: "end" if game is over, "sherlock" to continue investigation
            - num_guesses_left: Updated number of remaining guesses
    """
    console = Console()
    num_guesses_left = state['num_guesses_left']
    all_characters = state['characters']
    non_victims = [char for char in all_characters if char.role != VICTIM_ROLE]
    killer_character = next(char for char in all_characters if char.role == KILLER_ROLE)
    characters = list(sorted(non_victims, key=lambda x: x.name))

    # Print initial state
    console.rule("[bold red]🔍 Final Deduction[/bold red]")
    print_guesses_remaining(num_guesses_left)
    print_suspect_list(characters)

    is_win, is_lose = False, False

    while True:
        try:
            # Get user input
            choice = Prompt.ask(
                "\n[bold red]Who is the killer?[/bold red] (Enter suspect number)",
                default="",
                show_default=False
            )

            choice = int(choice)
            if 0 < choice <= len(characters):
                selected_character_id = choice - 1
                selected_character = characters[selected_character_id]

                if selected_character.role == KILLER_ROLE:
                    is_win = True
                    break
                else:
                    print_incorrect_guess()
                    num_guesses_left -= 1
                    if num_guesses_left > 0:
                        print_guesses_remaining(num_guesses_left)

                if num_guesses_left == 0:
                    is_lose = True
                    break

            else:
                console.print("[red]Invalid input. Please enter a valid suspect number.[/red]")
        except ValueError:
            console.print("[red]Invalid input. Please enter a number.[/red]")

    # Print final result
    print_result(is_win, is_lose, killer_character.name)

    is_end = is_win or is_lose
    return {"result": "end", "num_guesses_left": num_guesses_left} if is_end else {"result": "sherlock", "num_guesses_left": num_guesses_left}

