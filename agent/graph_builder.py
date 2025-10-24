"""
Graph builder for the Murder Mystery game.

This module constructs the LangGraph workflows:
1. Conversation Sub-Graph: Manages character conversations
2. Game Loop Graph: Orchestrates the overall game flow
"""

from langchain_openai import ChatOpenAI
from langgraph.graph import START, END, StateGraph

from .schemas import ConversationState, GenerateGameState
from .game_logic import (
    # Import all node functions
    create_characters,
    create_story,
    narrator,
    sherlock,
    character_introduction,
    ask_question,
    answer_question,
    where_to_go,
    conversation,
    guesser,
    # Import initialization functions
    initialize_llm,
    set_conversation_graph
)


def build_conversation_graph():
    """
    Builds the conversation sub-graph for character interviews.
    
    This graph handles the flow of conversations between Sherlock/player
    and individual characters in the game.
    
    Returns:
        Compiled StateGraph for conversation management
    """
    # Create the conversation graph
    conversation_builder = StateGraph(ConversationState)

    # Add nodes
    conversation_builder.add_node("character_introduction", character_introduction)
    conversation_builder.add_node("ask_question", ask_question)
    conversation_builder.add_node("answer_question", answer_question)

    # Add edges
    conversation_builder.add_edge(START, "character_introduction")
    conversation_builder.add_edge("character_introduction", "ask_question")
    conversation_builder.add_conditional_edges(
        "ask_question",
        where_to_go,
        {"continue": "answer_question", "end": END}
    )
    conversation_builder.add_edge("answer_question", "ask_question")

    # Compile and return
    return conversation_builder.compile()


def build_game_loop_graph():
    """
    Builds the main game loop graph.
    
    This graph orchestrates the entire game flow including:
    - Character creation
    - Story generation
    - Character selection
    - Conversations (via conversation sub-graph)
    - Killer guessing
    
    Returns:
        Compiled StateGraph for game loop management
    """
    # Create the game loop graph
    builder = StateGraph(GenerateGameState)

    # Add nodes
    builder.add_node("create_characters", create_characters)
    builder.add_node("create_story", create_story)
    builder.add_node("narrator", narrator)
    builder.add_node("sherlock", sherlock)
    builder.add_node("guesser", guesser)
    builder.add_node("conversation", conversation)

    # Add edges
    builder.add_edge(START, "create_characters")
    builder.add_edge("create_characters", "create_story")
    builder.add_edge("create_story", "narrator")
    builder.add_edge("narrator", "sherlock")

    builder.add_conditional_edges(
        "sherlock",
        lambda state: "next_talk" if state.get('selected_character_id') is not None else "end_talks",
        {
            "next_talk": "conversation",
            "end_talks": "guesser"
        }
    )

    builder.add_edge("conversation", "sherlock")
    builder.add_conditional_edges(
        "guesser",
        lambda state: state.get('result'),
        {"sherlock": "sherlock", "end": END}
    )

    # Compile and return
    return builder.compile()


def build_murder_mystery_game(model_name="gpt-4o", temperature=0):
    """
    Main function to build and configure the complete Murder Mystery game.
    
    This function:
    1. Initializes the LLM
    2. Builds the conversation sub-graph
    3. Builds the game loop graph
    4. Wires them together
    
    Args:
        model_name (str): Name of the OpenAI model to use (default: "gpt-4o")
        temperature (float): Temperature for LLM responses (default: 0 for deterministic)
    
    Returns:
        Compiled game loop graph ready to be invoked
    """
    # Initialize the LLM
    llm = ChatOpenAI(model=model_name, temperature=temperature)
    initialize_llm(llm)
    
    # Build the conversation graph first (needed by game loop)
    conversation_graph = build_conversation_graph()
    
    # Set the conversation graph in the game logic module
    set_conversation_graph(conversation_graph)
    
    # Build and return the game loop graph
    game_graph = build_game_loop_graph()
    
    return game_graph, conversation_graph


def visualize_graphs(game_graph, conversation_graph, save_path=None):
    """
    Generate visualizations of the game graphs.
    
    Args:
        game_graph: The compiled game loop graph
        conversation_graph: The compiled conversation graph
        save_path (str, optional): Path to save the visualization images
    
    Returns:
        tuple: (game_graph_image, conversation_graph_image) as PNG bytes
    """
    try:
        game_graph_img = game_graph.get_graph(xray=1).draw_mermaid_png()
        conversation_graph_img = conversation_graph.get_graph(xray=1).draw_mermaid_png()
        
        if save_path:
            import os
            os.makedirs(save_path, exist_ok=True)
            
            with open(os.path.join(save_path, "game_graph.png"), "wb") as f:
                f.write(game_graph_img)
            
            with open(os.path.join(save_path, "conversation_graph.png"), "wb") as f:
                f.write(conversation_graph_img)
        
        return game_graph_img, conversation_graph_img
    except Exception as e:
        print(f"Warning: Could not generate graph visualizations: {e}")
        return None, None

